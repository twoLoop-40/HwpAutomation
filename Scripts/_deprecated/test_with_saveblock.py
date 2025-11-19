"""
saveblock argument 옵션 테스트
"""
import sys
import codecs
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from typing import Generator

Block = tuple[tuple[int, int, int], tuple[int, int, int]]


@contextmanager
def open_hwp(file_path: str):
    """HWP 파일 열기"""
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
            end = (pset.Item("List"), pset.Item("Para"), pset.Item("Pos"))
            yield start, end
            start = end
        ctrl = ctrl.Next

    hwp.Run("MoveDocEnd")
    yield start, hwp.GetPos()


def save_block_with_argument(hwp, filepath: str, fmt: str = "HWP") -> bool:
    """saveblock argument를 사용한 블록 저장"""
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1
    hwp.HParameterSet.HFileOpenSave.Argument = "saveblock"  # ✨ 추가!

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result


# 테스트
test_file = r"C:\db\mad-label\2022 내신기출_공통수학2\2022 내신기출_공통수학2_집합_3.hwp"
output_dir = Path("Tests/seperation/output_saveblock")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== saveblock argument 테스트 ===\n")
print(f"파일: {Path(test_file).name}\n")

with open_hwp(test_file) as hwp:
    blocks = list(iter_note_blocks(hwp))
    print(f"총 {len(blocks)}개 블록\n")

    # 블록 6 추출 (idx=6)
    idx = 6
    if idx < 1 or idx > len(blocks):
        print(f"idx={idx} 범위 초과")
    else:
        start, end = blocks[idx - 1]
        print(f"블록 {idx}: {start} → {end}")

        if start == end:
            print(f"  ⊘ 빈 블록")
        else:
            # 블록 선택
            hwp.SetPos(*start)
            hwp.Run("Select")
            hwp.SetPos(*end)

            # saveblock argument로 저장
            output_path = output_dir / f"문제_{idx:03d}.hwp"
            success = save_block_with_argument(hwp, str(output_path))

            if success:
                if output_path.exists():
                    file_size = output_path.stat().st_size
                    print(f"  ✓ 저장 성공: {file_size:,} bytes")
                else:
                    print(f"  ⚠️  save_block returned True but file not found")
            else:
                print(f"  ✗ 저장 실패")

print("\n완료!")
