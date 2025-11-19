"""
CSV src로 실제 파일 찾기 테스트
"""
import sys
import codecs
import csv
from pathlib import Path
import re

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# CSV 파일 읽기
csv_path = r"C:\Users\joonho.lee\Downloads\[맞춤형]사준호_7_내신대비_집합_20251115_1756.csv"
db_root = Path(r"C:\db\mad-label")

print(f"=== 파일 찾기 테스트 ===\n")

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

# 각 문제에 대해 파일 찾기
for i, problem in enumerate(problems, 1):
    src = problem['src']
    print(f"\n{'='*80}")
    print(f"문제 {i}")
    print(f"src: {src}")

    # src 패턴 분석
    # 예: "2022년 개정교육과정 EBS 올림포스 공통수학II 2. 집합과 명제 112제_2_10"
    # → 폴더: "2022년 개정교육과정 EBS 올림포스 공통수학II"
    # → 파일: "2022년 개정교육과정 EBS 올림포스 공통수학II 2. 집합과 명제 112제_2.hwp"

    # 마지막 언더스코어 뒤의 숫자 제거
    # "..._2_10" → "..._2"
    parts = src.rsplit('_', 1)
    if len(parts) == 2:
        base_name = parts[0]  # "2022년 개정교육과정 EBS 올림포스 공통수학II 2. 집합과 명제 112제_2"
        idx = parts[1]  # "10"

        print(f"  base_name: {base_name}")
        print(f"  idx: {idx}")

        # 폴더명 추출 (첫 번째 숫자나 언더스코어 전까지)
        # "2022년 개정교육과정 EBS 올림포스 공통수학II 2. 집합과 명제 112제_2"
        # → "2022년 개정교육과정 EBS 올림포스 공통수학II"

        # 간단한 패턴: 첫 번째 "제" 앞까지 또는 특정 패턴
        # 일단 파일명에서 폴더명을 직접 찾아보자

        # 가능한 파일명 패턴
        possible_file = f"{base_name}.hwp"
        print(f"  possible_file: {possible_file}")

        # DB에서 파일 검색
        found_files = list(db_root.rglob(f"{base_name}.hwp"))

        if found_files:
            print(f"  ✓ 찾음: {found_files[0]}")
            print(f"    idx={idx} 사용 예정")
        else:
            print(f"  ✗ 못찾음")

            # 패턴 변경 시도: 마지막 두 언더스코어 제거
            # "..._2_10" → "..._2" 이미 했으니, 다른 패턴 시도
            parts2 = src.rsplit('_', 2)
            if len(parts2) == 3:
                base_name2 = parts2[0]
                possible_file2 = f"{base_name2}*.hwp"
                print(f"  대안 검색: {possible_file2}")

                found_files2 = list(db_root.rglob(possible_file2))
                if found_files2:
                    print(f"    ✓ 찾음: {len(found_files2)}개 파일")
                    for f in found_files2[:3]:
                        print(f"      - {f.name}")

print(f"\n{'='*80}\n완료!")
