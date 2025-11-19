"""
Block Selection and Save 테스트 (math-collector 방식)

Math-collector가 사용하는 정확한 방법:
1. iter_note_blocks로 블록 경계 찾기
2. SetPos + Select + SetPos로 블록 선택
3. FileSaveAs_S로 선택된 블록만 저장
"""
import sys
from pathlib import Path
import win32com.client as win32
import pythoncom

# Math-collector의 iter_note_blocks 로직
def iter_note_blocks(hwp):
    """EndNote 기반으로 블록 나누기"""
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl
    blocks = []

    while ctrl:
        if ctrl.CtrlID == 'en':  # EndNote 발견
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
    """선택된 블록을 파일로 저장"""
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result


# 테스트 파일
test_file = r'Tests\AppV1\결과_Merger_40문항.hwp'
output_dir = Path('Tests/seperation/output_blocks')
output_dir.mkdir(parents=True, exist_ok=True)

print(f"파일: {Path(test_file).name}\n")

pythoncom.CoInitialize()
try:
    hwp = win32.DispatchEx('HwpFrame.HwpObject')
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
    hwp.Open(test_file, 'HWP', 'lock:false;forceopen:true')
    hwp.XHwpWindows.Item(0).Visible = False

    # 블록 찾기
    blocks = iter_note_blocks(hwp)
    print(f"총 {len(blocks)}개 블록 발견\n")

    # 처음 3개 블록만 저장 테스트
    for i, (start, end) in enumerate(blocks[:3], 1):
        print(f"\n블록 {i}: {start} → {end}")

        # 블록 선택
        hwp.SetPos(*start)
        hwp.Run("Select")
        hwp.SetPos(*end)

        # 저장
        output_path = output_dir / f"문제_{i:03d}.hwp"
        success = save_block(hwp, str(output_path))

        if success:
            file_size = output_path.stat().st_size
            print(f"  ✓ 저장 완료: {output_path.name} ({file_size:,} bytes)")
        else:
            print(f"  ✗ 저장 실패")

        # 파일 다시 열기 (다음 블록 처리를 위해)
        hwp.Open(test_file, 'HWP', 'lock:false;forceopen:true')

    hwp.Quit()

finally:
    pythoncom.CoUninitialize()

print("\n\n=== 결과 검증 ===")
for i in range(1, 4):
    output_path = output_dir / f"문제_{i:03d}.hwp"
    if output_path.exists():
        size = output_path.stat().st_size
        print(f"문제 {i}: {size:,} bytes")

print("\n완료!")
