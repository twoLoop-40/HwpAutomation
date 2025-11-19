"""
core/hwp_extractor.py 모듈 전체 테스트 (5개 문제)
"""
import sys
import codecs
import csv
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# 프로젝트 루트를 path에 추가
sys.path.insert(0, r'c:\Users\joonho.lee\Projects\AutoHwp')

from core.hwp_extractor import extract_problem

csv_path = r"C:\Users\joonho.lee\Downloads\[맞춤형]사준호_7_내신대비_집합_20251115_1756.csv"
db_root = Path(r"C:\db\mad-label")

print(f"=== core/hwp_extractor.py 전체 테스트 ===\n")

# CSV 파싱
problems = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        problems.append({
            'id': row['id'],
            'origin_num': int(row['origin_num']),
            'src': row['src'],
            'mongo_id': row['mongo_id']
        })

print(f"총 {len(problems)}개 문제 발견\n")

success_count = 0
total_size = 0

for i, problem in enumerate(problems, 1):
    src = problem['src']
    origin_num = problem['origin_num']

    # src에서 파일명과 idx 추출
    parts = src.rsplit('_', 1)
    base_name = parts[0]
    idx = int(parts[1])

    # 파일 찾기
    possible_file = f"{base_name}.hwp"
    found_files = list(db_root.rglob(possible_file))

    if not found_files:
        print(f"{i}. {src}")
        print(f"  ✗ 파일 없음: {possible_file}\n")
        continue

    problem_path = str(found_files[0])

    print(f"{i}. {src}")
    print(f"  파일: {Path(problem_path).name}")
    print(f"  idx: {idx}, origin_num: {origin_num}")

    # extract_problem 사용 (filepath는 str로 전달)
    is_ok, target_path = extract_problem(
        hwp_file_path=problem_path,
        idx=idx,
        src=src,
        origin_num=origin_num,
        csv_filename=Path(csv_path).name
    )

    if is_ok and target_path and target_path.exists():
        file_size = target_path.stat().st_size
        total_size += file_size
        success_count += 1
        print(f"  ✓ 성공: {file_size:,} bytes")
    else:
        print(f"  ✗ 실패")

    print()

print(f"\n=== 결과 ===")
print(f"성공: {success_count}/{len(problems)}")
print(f"총 크기: {total_size:,} bytes")
print(f"평균 크기: {total_size // success_count:,} bytes" if success_count > 0 else "")
