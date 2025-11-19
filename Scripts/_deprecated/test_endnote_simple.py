"""간단한 EndNote 테스트 (iter_note_blocks 로직)"""
import win32com.client as win32
import pythoncom
from pathlib import Path

# 테스트 파일
test_file = r'Tests\AppV1\결과_Merger_40문항.hwp'

print(f"파일: {Path(test_file).name}\n")

pythoncom.CoInitialize()
try:
    hwp = win32.DispatchEx('HwpFrame.HwpObject')
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
    hwp.Open(test_file, 'HWP', 'lock:false;forceopen:true')
    hwp.XHwpWindows.Item(0).Visible = False

    # iter_note_blocks 로직 그대로
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl
    block_num = 0
    en_count = 0

    print("EndNote 찾기 중...")
    print("="*60)

    while ctrl:
        if ctrl.CtrlID == 'en':
            en_count += 1
            pset = ctrl.GetAnchorPos(0)
            lst = pset.Item("List")
            para = pset.Item("Para")
            pos = pset.Item("Pos")

            end = (lst, para, pos)
            block_num += 1
            print(f"블록 {block_num}: {start} → {end}")
            start = end

        ctrl = ctrl.Next

    # 마지막 블록
    hwp.Run("MoveDocEnd")
    end = hwp.GetPos()
    block_num += 1
    print(f"블록 {block_num}: {start} → {end}")

    print("="*60)
    print(f"\nEndNote 개수: {en_count}개")
    print(f"총 블록 수: {block_num}개")

    hwp.Quit()
finally:
    pythoncom.CoUninitialize()

print("\n완료!")
