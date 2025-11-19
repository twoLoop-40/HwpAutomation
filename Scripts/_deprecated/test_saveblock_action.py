"""
SaveBlockAction 사용 테스트
"""
import sys
import codecs

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from pathlib import Path

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


def save_block_action(hwp, filepath: str) -> bool:
    """SaveBlockAction 사용"""
    try:
        # FileSaveBlock ParameterSet 사용
        hwp.HAction.GetDefault("SaveBlockAction", hwp.HParameterSet.HFileSaveBlock.HSet)
        hwp.HParameterSet.HFileSaveBlock.FileName = filepath
        hwp.HParameterSet.HFileSaveBlock.Format = "HWP"

        result = hwp.HAction.Execute("SaveBlockAction", hwp.HParameterSet.HFileSaveBlock.HSet)
        return result
    except Exception as e:
        print(f"  SaveBlockAction 에러: {e}")
        return False


# 테스트
test_file = r"C:\db\mad-label\2022 내신기출_공통수학2\2022 내신기출_공통수학2_집합_3.hwp"
output_dir = Path("Tests/seperation/output_saveblock_action")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== SaveBlockAction 테스트 ===\n")
print(f"파일: {Path(test_file).name}\n")

with open_hwp(test_file) as hwp:
    # EndNote 찾기
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()
    ctrl = hwp.HeadCtrl

    blocks = []
    while ctrl:
        if ctrl.CtrlID == 'en':
            pset = ctrl.GetAnchorPos(0)
            end = (pset.Item("List"), pset.Item("Para"), pset.Item("Pos"))
            blocks.append((start, end))
            start = end
        ctrl = ctrl.Next

    hwp.Run("MoveDocEnd")
    blocks.append((start, hwp.GetPos()))

    print(f"총 {len(blocks)}개 블록\n")

    # 블록 6 추출
    idx = 6
    start, end = blocks[idx - 1]
    print(f"블록 {idx}: {start} → {end}\n")

    # 블록 선택
    hwp.SetPos(*start)
    hwp.Run("Select")
    hwp.SetPos(*end)

    # SaveBlockAction으로 저장
    output_path = output_dir / f"문제_{idx:03d}.hwp"
    success = save_block_action(hwp, str(output_path))

    if success:
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"  ✓ 저장 성공: {file_size:,} bytes")
        else:
            print(f"  ⚠️  반환값 True이지만 파일 없음")
    else:
        print(f"  ✗ 저장 실패")

print("\n완료!")
