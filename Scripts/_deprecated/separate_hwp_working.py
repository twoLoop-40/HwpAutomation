"""
HWP 파일 문제 분리 (math-collector 방식)

iter_note_blocks로 EndNote 앵커 찾고
SetPos + Select + SaveBlockAction으로 저장
"""
import sys
import codecs
from pathlib import Path
import win32com.client as win32
import pythoncom

# UTF-8 출력 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


def iter_note_blocks(hwp):
    """EndNote 앵커 기반 블록 나누기"""
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl
    blocks = []

    while ctrl:
        if ctrl.CtrlID == 'en':  # EndNote 앵커 발견
            pset = ctrl.GetAnchorPos(0)
            lst = pset.Item("List")
            para = pset.Item("Para")
            pos = pset.Item("Pos")

            end = (lst, para, pos)
            blocks.append((start, end))
            start = end

        ctrl = ctrl.Next

    # 마지막 블록
    hwp.Run("MoveDocEnd")
    end = hwp.GetPos()
    blocks.append((start, end))

    return blocks


def save_block(hwp, filepath: str, fmt: str = "HWP") -> bool:
    """선택된 블록을 파일로 저장 (math-collector 방식 그대로)"""
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result


def separate_problems(input_path: str, output_dir: Path, group_size: int = 1, max_problems: int = None):
    """문제 분리"""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"파일: {Path(input_path).name}")
    print(f"출력: {output_dir}\n")

    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(input_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        # 블록 찾기
        print("EndNote 앵커 찾는 중...")
        blocks = iter_note_blocks(hwp)
        total_blocks = len(blocks)
        print(f"총 {total_blocks}개 블록 발견\n")

        if max_problems:
            blocks = blocks[:max_problems]
            print(f"처음 {max_problems}개만 처리\n")

        # 그룹화 처리
        if group_size == 1:
            # 1문제 = 1파일
            for i, (start, end) in enumerate(blocks, 1):
                # 블록 선택
                hwp.SetPos(*start)
                hwp.Run("Select")
                hwp.SetPos(*end)

                # 저장
                output_path = output_dir / f"문제_{i:03d}.hwp"
                success = save_block(hwp, str(output_path))

                if success:
                    file_size = output_path.stat().st_size
                    print(f"✓ {output_path.name} ({file_size:,} bytes)")
                else:
                    print(f"✗ {output_path.name} 저장 실패")

                # 파일 다시 열기 (다음 블록 처리 위해)
                hwp.Open(input_path, 'HWP', 'lock:false;forceopen:true')

        else:
            # N개씩 그룹
            for group_idx in range(0, len(blocks), group_size):
                group_blocks = blocks[group_idx:group_idx + group_size]
                start_num = group_idx + 1
                end_num = min(group_idx + group_size, len(blocks))

                # 그룹 전체 선택 (첫 블록 시작 ~ 마지막 블록 끝)
                first_start = group_blocks[0][0]
                last_end = group_blocks[-1][1]

                hwp.SetPos(*first_start)
                hwp.Run("Select")
                hwp.SetPos(*last_end)

                # 저장
                output_path = output_dir / f"문제_{start_num:03d}-{end_num:03d}.hwp"
                success = save_block(hwp, str(output_path))

                if success:
                    file_size = output_path.stat().st_size
                    print(f"✓ {output_path.name} ({len(group_blocks)}문제, {file_size:,} bytes)")
                else:
                    print(f"✗ {output_path.name} 저장 실패")

                # 파일 다시 열기
                hwp.Open(input_path, 'HWP', 'lock:false;forceopen:true')

        hwp.Quit()
        print(f"\n완료! {len(blocks)}개 처리됨")

    finally:
        pythoncom.CoUninitialize()


def convert_hwpx_to_hwp(hwpx_path: str, hwp_path: str) -> bool:
    """HWPX를 HWP로 변환"""
    print(f"HWPX → HWP 변환 중...")

    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(hwpx_path, 'HWPX', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        # HWP로 저장
        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = hwp_path
        hwp.HParameterSet.HFileOpenSave.Format = "HWP"
        hwp.HParameterSet.HFileOpenSave.Attributes = 1

        result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.Quit()

        if result:
            print(f"✓ 변환 완료: {Path(hwp_path).name}\n")
        return result

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    # 테스트 파일 (EndNote 앵커가 있는 파일)
    input_file = r"c:\Users\joonho.lee\Projects\math-collector\src\core\merger\테스트_2개문항.hwp"
    output_dir = Path("Tests/seperation/output_hwp_working")

    # 문제 분리 (전체)
    separate_problems(
        input_path=input_file,
        output_dir=output_dir,
        group_size=1,
        max_problems=None  # 전체 처리
    )
