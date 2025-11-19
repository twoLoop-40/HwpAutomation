"""
math-collector의 _process_single 정확히 복사해서 실행
"""
import sys
import codecs
import csv
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# math-collector 경로 추가
sys.path.insert(0, r'c:\Users\joonho.lee\Projects\math-collector')

from src.tools.handle_hwp import open_hwp, select_and_save

def _process_single(problem_path: str, idx: int, csv_path: str | Path, origin_num: int, src: str, csv_filename: str = None):
    """
    math-collector의 _process_single 그대로 복사
    """
    with open_hwp(problem_path) as hwp:
        filename = csv_filename if csv_filename else Path(csv_path).name
        saver = select_and_save(hwp, idx=idx, origin_num=origin_num, csv_filename=filename)
        return saver(src)


# CSV 파일 읽기
csv_path = r"C:\Users\joonho.lee\Downloads\[맞춤형]사준호_7_내신대비_집합_20251115_1756.csv"
db_root = Path(r"C:\db\mad-label")

print(f"=== math-collector 정확한 복사 테스트 ===\n")

# CSV 읽기
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

print(f"총 {len(problems)}개 문제\n")

# 처음 3개 문제만 처리
success_count = 0
fail_count = 0

for i, problem in enumerate(problems[:3], 1):
    src = problem['src']
    origin_num = problem['origin_num']

    print(f"\n{'='*80}")
    print(f"문제 {i}")
    print(f"src: {src}")

    # 파일 찾기
    parts = src.rsplit('_', 1)
    if len(parts) != 2:
        print(f"  ✗ src 패턴 오류")
        fail_count += 1
        continue

    base_name = parts[0]
    idx = int(parts[1])

    possible_file = f"{base_name}.hwp"
    found_files = list(db_root.rglob(possible_file))

    if not found_files:
        print(f"  ✗ 파일 못찾음")
        fail_count += 1
        continue

    problem_path = str(found_files[0])
    print(f"  ✓ 파일: {found_files[0].name}")
    print(f"  ✓ idx: {idx}")

    # math-collector의 _process_single 실행
    try:
        is_ok, target_path = _process_single(
            problem_path=problem_path,
            idx=idx,
            csv_path=csv_path,
            origin_num=origin_num,
            src=src,
            csv_filename=Path(csv_path).name
        )

        if is_ok:
            file_size = Path(target_path).stat().st_size if Path(target_path).exists() else 0
            print(f"  ✓ 성공: {file_size:,} bytes")
            print(f"  ✓ 경로: {target_path}")
            success_count += 1
        else:
            print(f"  ✗ 저장 실패")
            fail_count += 1

    except Exception as e:
        print(f"  ✗ 에러: {e}")
        import traceback
        traceback.print_exc()
        fail_count += 1

print(f"\n{'='*80}")
print(f"\n결과: 성공 {success_count}/3, 실패 {fail_count}/3")
