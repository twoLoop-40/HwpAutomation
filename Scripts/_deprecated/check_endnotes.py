"""HWP 파일의 EndNote 구조 진단 스크립트"""
import sys
import contextlib
import pythoncom
import win32com.client as win32
from pathlib import Path

@contextlib.contextmanager
def open_hwp(file_path: str):
    """HWP 파일 열기 (handle_hwp.py 패턴)"""
    pythoncom.CoInitialize()
    hwp = None
    try:
        hwp = win32.DispatchEx("HwpFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        arg = "lock:false;forceopen:true;readonly:true"
        hwp.Open(file_path, "HWP", arg)
        hwp.XHwpWindows.Item(0).Visible = False
        yield hwp
    finally:
        if hwp:
            try:
                hwp.XHwpDocuments.Active_XHwpDocument.Close(False)
                hwp.Quit()
            finally:
                pythoncom.CoUninitialize()


def diagnose_hwp_structure(file_path: str):
    """HWP 파일 구조 진단"""
    print(f"파일: {Path(file_path).name}\n")
    print("=" * 60)

    with open_hwp(file_path) as hwp:
        # 1. 문서 기본 정보
        print("[1] 문서 기본 정보")
        print("-" * 60)
        hwp.Run("MoveDocBegin")
        hwp.Run("MoveDocEnd")
        doc_end_pos = hwp.GetPos()
        print(f"문서 끝 위치: List={doc_end_pos[0]}, Para={doc_end_pos[1]}, Pos={doc_end_pos[2]}\n")

        # 2. HeadCtrl 전체 순회
        print("[2] HeadCtrl 전체 순회")
        print("-" * 60)
        hwp.Run("MoveDocBegin")
        ctrl = hwp.HeadCtrl

        ctrl_count = 0
        ctrl_types = {}
        endnote_count = 0

        while ctrl:
            ctrl_id = ctrl.CtrlID
            ctrl_types[ctrl_id] = ctrl_types.get(ctrl_id, 0) + 1
            ctrl_count += 1

            # EndNote 상세 정보
            if ctrl_id == 'en':
                endnote_count += 1
                print(f"\n[EndNote #{endnote_count}]")
                try:
                    pset = ctrl.GetAnchorPos(0)
                    lst = pset.Item("List")
                    para = pset.Item("Para")
                    pos = pset.Item("Pos")
                    print(f"  Anchor Position: List={lst}, Para={para}, Pos={pos}")

                    # EndNote 내용 확인 (가능하면)
                    try:
                        # EndNote 영역으로 이동
                        hwp.SetPos(lst, para, pos)
                        hwp.Run("MoveRight")  # EndNote 내부로 진입
                        sample_text = hwp.GetTextFile("TEXT", "saveblock")[:100]
                        print(f"  내용 샘플: {sample_text}")
                    except Exception as e:
                        print(f"  내용 읽기 실패: {e}")

                except Exception as e:
                    print(f"  GetAnchorPos 실패: {e}")

            ctrl = ctrl.Next

        print(f"\n총 Control 개수: {ctrl_count}")
        print(f"Control 타입별 개수:")
        for ctrl_id, count in sorted(ctrl_types.items()):
            print(f"  {ctrl_id}: {count}개")

        # 3. 미주 번호 검색 (텍스트 기반)
        print("\n[3] 텍스트에서 미주 참조 검색")
        print("-" * 60)
        import re

        # GetText() 반환 타입 확인
        hwp.Run("MoveDocBegin")
        hwp.Run("SelectAll")
        full_text = hwp.GetText()
        print(f"GetText() 반환 타입: {type(full_text)}")

        if isinstance(full_text, tuple):
            print(f"튜플 길이: {len(full_text)}")
            if full_text:
                full_text = str(full_text[0]) if full_text[0] else ""

        # [정답] 패턴 찾기
        if isinstance(full_text, str):
            answer_pattern = r'\[정답\]'
            answers = list(re.finditer(answer_pattern, full_text))
            print(f"[정답] 개수: {len(answers)}")

            # 문서 끝 부분 확인 (미주 영역 추정)
            print(f"\n전체 텍스트 길이: {len(full_text)} 문자")
            print(f"마지막 1000자:")
            print("-" * 60)
            print(full_text[-1000:])
        else:
            print("텍스트 추출 실패")


if __name__ == "__main__":
    import sys

    # 두 파일 모두 테스트
    print("=" * 80)
    print("HWP 파일 테스트")
    print("=" * 80)
    hwp_file = r"Tests\seperation\6. 명제_2023.hwp"
    if Path(hwp_file).exists():
        diagnose_hwp_structure(hwp_file)

    print("\n\n")
    print("=" * 80)
    print("HWPX 파일에서 EndNote 찾기")
    print("=" * 80)

    # HWPX는 XML 파싱으로 확인
    import zipfile
    import xml.etree.ElementTree as ET

    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"
    if not Path(hwpx_file).exists():
        print("HWPX 파일이 없습니다")
        sys.exit(1)

    with zipfile.ZipFile(hwpx_file, 'r') as zf:
        section_file = 'Contents/section0.xml'
        xml_content = zf.read(section_file)
        root = ET.fromstring(xml_content)

        ns = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

        # EndNote 태그 찾기
        endnotes = root.findall('.//hh:endnote', ns)
        print(f"<endnote> 태그: {len(endnotes)}개")

        # 모든 태그 확인
        all_tags = set()
        def collect(elem):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            all_tags.add(tag)
            for child in elem:
                collect(child)
        collect(root)

        note_tags = [t for t in sorted(all_tags) if 'note' in t.lower() or 'en' in t.lower()]
        print(f"Note 관련 태그: {note_tags}")
