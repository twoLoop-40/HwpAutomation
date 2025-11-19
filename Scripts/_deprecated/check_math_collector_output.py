"""
math-collector 실제 출력 확인
"""
import sys
import codecs
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

import win32com.client as win32
import pythoncom

output_dir = Path(r"C:\Users\joonho.lee\Downloads\[맞춤형]사준호_7_내신대비_집합_20251115_1756")

print("=== math-collector 실제 출력 파일 ===\n")

hwp_files = [f for f in output_dir.glob("*.hwp") if f.name != "combined_problems.hwp"]

print(f"발견된 파일: {len(hwp_files)}개\n")

for file_path in hwp_files:
    print(f"파일: {file_path.name}")
    print(f"  크기: {file_path.stat().st_size:,} bytes")

    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(str(file_path), 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        # SelectAll로 모든 텍스트 가져오기
        hwp.Run('SelectAll')
        text_result = hwp.GetText()
        text = text_result[1] if isinstance(text_result, tuple) else text_result
        text_str = str(text) if text else ""

        print(f"  텍스트: {len(text_str)} 문자")

        if len(text_str) > 0:
            preview = text_str[:150].replace('\r', ' ').replace('\n', ' ')
            print(f"  내용: {preview}...")
        else:
            print(f"  내용: (비어있음)")

        hwp.Quit()
    except Exception as e:
        print(f"  에러: {e}")
    finally:
        pythoncom.CoUninitialize()

    print()

print("완료!")
