"""
math-collector의 HWP 파일 EndNote 확인
"""
import win32com.client as win32
import pythoncom


def check_endnotes(file_path: str):
    """EndNote 앵커 확인"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        ctrl = hwp.HeadCtrl
        count = 0
        positions = []

        while ctrl:
            if ctrl.CtrlID == 'en':
                count += 1
                pset = ctrl.GetAnchorPos(0)
                lst = pset.Item("List")
                para = pset.Item("Para")
                pos = pset.Item("Pos")
                positions.append((lst, para, pos))

            ctrl = ctrl.Next

        hwp.Quit()
        return count, positions

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    test_file = r"c:\Users\joonho.lee\Projects\math-collector\src\core\merger\테스트_2개문항.hwp"

    print(f"파일: {test_file}\n")

    count, positions = check_endnotes(test_file)

    print(f"EndNote 앵커: {count}개\n")

    if count > 0:
        print("위치:")
        for i, pos in enumerate(positions, 1):
            print(f"  {i}. {pos}")
    else:
        print("EndNote 앵커가 없습니다")
