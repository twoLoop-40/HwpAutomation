"""
모든 HWP 파일의 EndNote 개수 확인
"""
import win32com.client as win32
import pythoncom
from pathlib import Path


def count_endnotes(file_path: str) -> int:
    """EndNote 앵커 개수 세기"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        ctrl = hwp.HeadCtrl
        count = 0

        while ctrl:
            if ctrl.CtrlID == 'en':
                count += 1
            ctrl = ctrl.Next

        hwp.Quit()
        return count

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    test_dir = Path("Tests/seperation")
    hwp_files = list(test_dir.glob("*.hwp"))

    print("=== HWP 파일별 EndNote 개수 ===\n")

    for hwp_file in hwp_files:
        try:
            count = count_endnotes(str(hwp_file))
            print(f"{hwp_file.name:50s} : {count:4d}개")
        except Exception as e:
            print(f"{hwp_file.name:50s} : 에러 - {e}")

    print(f"\n총 {len(hwp_files)}개 파일 확인")
