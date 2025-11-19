"""
3문항씩 묶어서 추출 테스트

Idris2 명세: Specs/Extractor/SequentialExtraction.idr (Solution3_CopyPaste)

전략:
1. 전체 블록 위치를 먼저 수집 (list(iter_note_blocks))
2. 3개씩 묶어서 그룹화: [1,2,3], [4,5,6], [7,8,9], ...
3. 각 그룹마다:
   - 첫 번째 블록 시작 ~ 마지막 블록 끝
   - Copy/Paste로 추출
"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

sys.path.insert(0, r'c:\Users\joonho.lee\Projects\AutoHwp')

from core.hwp_extractor import open_hwp, iter_note_blocks
from core.hwp_extractor_copypaste import extract_block_copypaste

# 입력 파일
input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"
input_path = Path(input_file)

# 출력 폴더: 파일명_merged3
output_dir = input_path.parent / f"{input_path.stem}_merged3"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== 3문항씩 묶어서 추출 ===\n")
print(f"입력: {input_path.name}")
print(f"출력: {output_dir}\n")

# 1단계: 전체 블록 위치 수집
print("1단계: 블록 위치 수집 중...")
with open_hwp(input_file) as hwp:
    all_blocks = list(iter_note_blocks(hwp))

total_blocks = len(all_blocks)
print(f"총 {total_blocks}개 블록 발견")

# 블록 0은 첫 번째 문항 이전 부분이므로 제외
# 블록 1부터가 실제 문항
all_blocks = all_blocks[1:]  # 블록 0 제거
actual_problems = len(all_blocks)
print(f"블록 0 제외, 실제 문항: {actual_problems}개\n")

# 2단계: 3개씩 그룹화 (블록 1,2,3 / 4,5,6 / ...)
groups_per_file = 3
groups = []
for i in range(0, actual_problems, groups_per_file):
    group = list(range(i, min(i + groups_per_file, actual_problems)))
    groups.append(group)

print(f"2단계: {len(groups)}개 그룹으로 분할")
for idx, group in enumerate(groups, 1):
    print(f"  그룹 {idx}: 블록 {[g+1 for g in group]}")  # 1-based 표시

# 3단계: 각 그룹별로 추출
print(f"\n3단계: Copy/Paste 추출 시작\n")

results = []
with open_hwp(input_file) as hwp:
    for group_idx, group in enumerate(groups, 1):
        # 그룹의 첫 블록 시작 ~ 마지막 블록 끝
        first_block = all_blocks[group[0]]
        last_block = all_blocks[group[-1]]

        merged_block = (first_block[0], last_block[1])

        # 저장 경로
        filename = f"문제_{group[0]+1:03d}_to_{group[-1]+1:03d}.hwp"
        filepath = output_dir / filename

        print(f"그룹 {group_idx}: 블록 {[g+1 for g in group]} → {filename}")

        # Copy/Paste 추출 (verbose=True)
        success = extract_block_copypaste(hwp, merged_block, filepath, verbose=True)

        # 파일 존재 여부가 더 신뢰할 수 있음 (result=False여도 저장될 수 있음)
        if filepath.exists():
            file_size = filepath.stat().st_size
            results.append((True, filepath, file_size))
            print(f"  ✓ 성공: {file_size:,} bytes (API result={success})\n")
        else:
            results.append((False, None, 0))
            print(f"  ✗ 실패: 파일 생성 안됨\n")

# 결과 분석
success_count = sum(1 for ok, _, _ in results if ok)
total_count = len(results)
total_size = sum(size for _, _, size in results)

print(f"=== 요약 ===")
print(f"성공: {success_count}/{total_count} 그룹")
print(f"총 크기: {total_size:,} bytes")
if success_count > 0:
    print(f"평균 크기: {total_size // success_count:,} bytes")
print(f"출력 폴더: {output_dir}")
