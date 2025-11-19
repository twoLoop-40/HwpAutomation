"""
실제 문제 파일 구조 분석
"""
import win32com.client as win32
import pythoncom
from pathlib import Path


def analyze_file(file_path: str):
    """파일 구조 분석"""
    print(f"파일: {Path(file_path).name}\n")

    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        print("=== 기본 정보 ===")
        print(f"페이지 수: {hwp.PageCount}")

        # EndNote 확인
        ctrl = hwp.HeadCtrl
        en_count = 0
        while ctrl:
            if ctrl.CtrlID == 'en':
                en_count += 1
            ctrl = ctrl.Next

        print(f"EndNote 앵커: {en_count}개\n")

        # 텍스트 추출
        hwp.Run("SelectAll")
        text_result = hwp.GetText()
        text = text_result[1] if isinstance(text_result, tuple) else text_result
        text = str(text) if text else ""

        print(f"=== 텍스트 정보 ===")
        print(f"전체 길이: {len(text):,} 문자\n")

        # 첫 500자 출력
        print("=== 첫 500자 ===")
        print(text[:500])

        hwp.Quit()

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    # EBS 파일 중 하나
    test_file = r"Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"

    analyze_file(test_file)
