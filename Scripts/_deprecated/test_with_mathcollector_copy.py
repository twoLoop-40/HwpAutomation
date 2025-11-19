"""
math-collector 코드 직접 복사해서 사용
"""
import sys
import codecs
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# math-collector 코드 복사 (handle_hwp.py에서)
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


# 테스트
test_file = r"c:\Users\joonho.lee\Projects\math-collector\src\core\merger\테스트_2개문항.hwp"
output_dir = Path("Tests/seperation/output_mathcollector_copy")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"파일: {Path(test_file).name}\n")

with open_hwp(test_file) as hwp:
    blocks = list(iter_note_blocks(hwp))
    print(f"총 {len(blocks)}개 블록\n")

    for i, (start, end) in enumerate(blocks, 1):
        print(f"블록 {i}: {start} → {end}")

        # 빈 블록 건너뛰기 (시작 == 끝)
        if start == end:
            print(f"  ⊘ 빈 블록 건너뜀\n")
            continue

        # 블록 선택
        hwp.SetPos(*start)
        hwp.Run("Select")
        hwp.SetPos(*end)

        # 저장
        output_path = output_dir / f"문제_{i:03d}.hwp"
        success = save_block(hwp, str(output_path))

        if success:
            file_size = output_path.stat().st_size if output_path.exists() else 0
            print(f"  ✓ 저장: {file_size:,} bytes\n")
        else:
            print(f"  ✗ 실패\n")

print("완료!")
