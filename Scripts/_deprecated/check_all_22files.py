"""
22개정으로 시작하는 모든 파일의 EndNote 확인
"""
import sys
import codecs
from pathlib import Path
import win32com.client as win32
import pythoncom

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


def check_file(file_path: str):
    """파일의 EndNote 앵커 개수 확인"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        # EndNote 개수 확인
        ctrl = hwp.HeadCtrl
        en_count = 0
        while ctrl:
            if ctrl.CtrlID == 'en':
                en_count += 1
            ctrl = ctrl.Next

        # 파일 정보
        page_count = hwp.PageCount

        # 텍스트 샘플
        hwp.Run("MoveDocBegin")
        hwp.MovePos(201, 0, 1)  # 100자 선택
        try:
            text_result = hwp.GetText()
            text = text_result[1] if isinstance(text_result, tuple) else text_result
            text = str(text) if text else ""
            sample = text[:150].replace('\r', ' ').replace('\n', ' ')
        except:
            sample = "(읽기 실패)"

        hwp.Quit()

        return {
            'en_count': en_count,
            'page_count': page_count,
            'sample': sample
        }

    finally:
        pythoncom.CoUninitialize()


# 22개정 파일들 확인
test_dir = Path(r"Tests\seperation")
files = list(test_dir.glob("22개정*.hwp"))

print(f"22개정 파일 {len(files)}개 확인\n")
print("=" * 80)

for file_path in files:
    print(f"\n파일: {file_path.name}")
    try:
        info = check_file(str(file_path))
        print(f"  페이지: {info['page_count']}")
        print(f"  EndNote: {info['en_count']}개")
        print(f"  샘플: {info['sample']}")
    except Exception as e:
        print(f"  에러: {e}")

print("\n" + "=" * 80)
