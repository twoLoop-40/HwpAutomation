"""생성된 출력 파일 검증 - HWP COM으로 열어서 텍스트 확인"""
import win32com.client as win32
import pythoncom
from pathlib import Path

# 첫 번째 출력 파일 (HWPX를 HWP COM으로 열기)
output_file = r"Tests\seperation\output_test_new\문제_001-010.hwpx"

if not Path(output_file).exists():
    print(f"파일이 없습니다: {output_file}")
    exit(1)

print(f"파일: {Path(output_file).name}")
print(f"크기: {Path(output_file).stat().st_size} bytes\n")

pythoncom.CoInitialize()
try:
    hwp = win32.DispatchEx('HwpFrame.HwpObject')
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

    try:
        # HWPX 파일 열기
        hwp.Open(output_file, 'HWPX', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        # 전체 텍스트 추출
        hwp.Run("MoveDocBegin")
        hwp.Run("SelectAll")
        text_result = hwp.GetText()

        # GetText 결과 처리
        if isinstance(text_result, tuple):
            full_text = str(text_result[0]) if text_result else ""
        else:
            full_text = str(text_result)

        print("="*60)
        print("파일 내용 (처음 2000자):")
        print("="*60)
        print(full_text[:2000])
        print("="*60)
        print(f"\n전체 길이: {len(full_text)} 문자")

        # [정답] 개수 확인
        answer_count = full_text.count('[정답]')
        print(f"[정답] 개수: {answer_count}")

        hwp.Quit()

    except Exception as e:
        print(f"파일 열기 실패: {e}")
        hwp.Quit()

finally:
    pythoncom.CoUninitialize()

print("\n완료!")
