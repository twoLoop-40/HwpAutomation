"""
EBS 파일로 테스트 - math-collector 로직 직접 복사
"""
import sys
import codecs
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# math-collector 코드 복사
import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from typing import Generator

Block = tuple[tuple[int, int, int], tuple[int, int, int]]


@contextmanager
def open_hwp(file_path: str):
    """HWP 파일 열기 (context manager)"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        yield hwp

        hwp.Quit()
    finally:
        pythoncom.CoUninitialize()


def iter_note_blocks(hwp) -> Generator[Block, None, None]:
    """EndNote 앵커 기반 블록 나누기"""
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl

    while ctrl:
        if ctrl.CtrlID == 'en':
            pset = ctrl.GetAnchorPos(0)
            lst = pset.Item("List")
            para = pset.Item("Para")
            pos = pset.Item("Pos")

            end = (lst, para, pos)
            yield start, end
            start = end

        ctrl = ctrl.Next

    hwp.Run("MoveDocEnd")
    yield start, hwp.GetPos()


def save_block(hwp, filepath: str, fmt: str = "HWP") -> bool:
    """선택된 블록 저장"""
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result


# 테스트 - EBS 파일 중 하나
test_file = r"Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"
output_dir = Path("Tests/seperation/output_ebs")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"파일: {Path(test_file).name}\n")

with open_hwp(test_file) as hwp:
    # EndNote 개수 확인
    ctrl = hwp.HeadCtrl
    en_count = 0
    while ctrl:
        if ctrl.CtrlID == 'en':
            en_count += 1
        ctrl = ctrl.Next

    print(f"EndNote 앵커: {en_count}개\n")

    # 블록 리스트
    blocks = list(iter_note_blocks(hwp))
    print(f"총 {len(blocks)}개 블록\n")

    # 각 블록 정보 출력 (처음 5개만)
    for i, (start, end) in enumerate(blocks[:5], 1):
        print(f"블록 {i}: {start} → {end}")

        # 빈 블록인지 확인
        if start == end:
            print(f"  ⊘ 빈 블록\n")
        else:
            # 블록 선택
            hwp.SetPos(*start)
            hwp.Run("Select")
            hwp.SetPos(*end)

            # 텍스트 미리보기
            try:
                text_result = hwp.GetText()
                text = text_result[1] if isinstance(text_result, tuple) else text_result
                text = str(text) if text else ""
                preview = text[:100].replace('\r', ' ').replace('\n', ' ')
                print(f"  내용: {preview}...\n")
            except:
                print(f"  내용: (읽기 실패)\n")

print(f"완료! 총 {len(blocks)}개 블록 발견")
print(f"EndNote 앵커: {en_count}개")
