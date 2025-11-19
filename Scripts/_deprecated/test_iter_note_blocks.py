"""iter_note_blocks 패턴 테스트"""
import sys
from pathlib import Path

# math-collector의 handle_hwp.py 사용
sys.path.insert(0, r'c:\Users\joonho.lee\Projects\math-collector\src')
from tools.handle_hwp import get_block_count, iter_note_blocks
import win32com.client as win32
import pythoncom

# 테스트 파일
test_file = r'c:\Users\joonho.lee\Projects\AutoHwp\Tests\AppV1\결과_Merger_40문항.hwp'

print(f"파일: {Path(test_file).name}\n")

pythoncom.CoInitialize()
try:
    hwp = win32.DispatchEx('HwpFrame.HwpObject')
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
    hwp.Open(test_file, 'HWP', 'lock:false;forceopen:true')
    hwp.XHwpWindows.Item(0).Visible = False

    # iter_note_blocks로 블록 개수 확인
    block_count = get_block_count(hwp)
    print(f"총 블록 수 (iter_note_blocks): {block_count}개\n")

    # 각 블록 정보 출력
    print("블록 정보:")
    print("="*60)
    for i, (start, end) in enumerate(iter_note_blocks(hwp), 1):
        print(f"블록 {i}: {start} → {end}")
        if i >= 10:
            print(f"... (총 {block_count}개)")
            break

    hwp.Quit()
finally:
    pythoncom.CoUninitialize()

print("\n완료!")
