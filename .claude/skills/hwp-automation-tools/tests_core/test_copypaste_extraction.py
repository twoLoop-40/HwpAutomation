"""
Copy/Paste 방식 추출 테스트

Idris2 명세: Specs/Extractor/SequentialExtraction.idr (Solution3_CopyPaste)
"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

sys.path.insert(0, r'c:\Users\joonho.lee\Projects\AutoHwp')

from core.hwp_extractor_copypaste import extract_all_sequential_copypaste

# 입력 파일
input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\6. 명제_2023.hwp"
input_path = Path(input_file)

# 출력 폴더: 파일명_copypaste
output_dir = input_path.parent / f"{input_path.stem}_copypaste"

print(f"=== Copy/Paste 방식 HWP 블록 추출 ===\n")
print(f"입력: {input_path.name}")
print(f"출력: {output_dir}\n")
print(f"명세: Specs/Extractor/SequentialExtraction.idr\n")

# 추출 실행
results = extract_all_sequential_copypaste(input_file, output_dir)

# 결과 분석
success_count = sum(1 for ok, _ in results if ok)
total_count = len(results)
total_size = 0

print(f"\n=== 추출 결과 ===\n")

for idx, (success, filepath) in enumerate(results, 1):
    if success and filepath:
        file_size = filepath.stat().st_size
        total_size += file_size
        print(f"{idx}. ✓ 성공: {filepath.name} ({file_size:,} bytes)")
    else:
        print(f"{idx}. ✗ 실패")

print(f"\n=== 요약 ===")
print(f"성공: {success_count}/{total_count}")
print(f"총 크기: {total_size:,} bytes")
if success_count > 0:
    print(f"평균 크기: {total_size // success_count:,} bytes")
print(f"출력 폴더: {output_dir}")
