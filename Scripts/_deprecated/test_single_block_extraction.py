"""
단일 블록 추출 테스트 - 블록 7,8,9 (인덱스 6,7,8)
"""
import sys
from pathlib import Path
sys.path.insert(0, r'c:\\Users\\joonho.lee\\Projects\\AutoHwp')

from core.hwp_extractor import open_hwp, iter_note_blocks
from core.hwp_extractor_copypaste import extract_block_copypaste

input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"

print("블록 위치 수집...")
with open_hwp(input_file) as hwp:
    all_blocks = list(iter_note_blocks(hwp))

# 블록 0 제외
all_blocks = all_blocks[1:]

# 블록 6,7,8 (7,8,9번째 문항)
block_indices = [6, 7, 8]
merged_block = (all_blocks[block_indices[0]][0], all_blocks[block_indices[-1]][1])

print(f"블록 [7,8,9] 병합: {merged_block}")

# 추출
output_path = Path(r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\test_block_789.hwp")

with open_hwp(input_file) as hwp:
    success = extract_block_copypaste(hwp, merged_block, output_path, verbose=True)

if output_path.exists():
    size = output_path.stat().st_size
    print(f"\n✓ 성공: {size:,} bytes")
else:
    print(f"\n✗ 실패")
