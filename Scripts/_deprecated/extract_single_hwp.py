"""
단일 HWP 파일을 문제별로 분리

파일명으로 출력 폴더 자동 생성
"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# 프로젝트 루트를 path에 추가
sys.path.insert(0, r'c:\Users\joonho.lee\Projects\AutoHwp')

from core.hwp_extractor import open_hwp, get_block_count, extract_problem

# 입력 파일
input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\6. 명제_2023.hwp"
input_path = Path(input_file)

# 출력 폴더: 파일명으로 자동 생성 (확장자 제외)
output_dir = input_path.parent / input_path.stem
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== HWP 파일 분리 ===\n")
print(f"입력: {input_path.name}")
print(f"출력: {output_dir}\n")

# 블록 수 확인
with open_hwp(input_file) as hwp:
    total_blocks = get_block_count(hwp)

print(f"총 {total_blocks}개 블록 발견\n")

success_count = 0
total_size = 0

# math-collector 방식: iter_note_blocks를 yield하면서 처리
from core.hwp_extractor import open_hwp, iter_note_blocks, make_hwp_path, save_block

with open_hwp(input_file) as hwp:
    # 제너레이터로 블록을 하나씩 처리
    for idx, block in enumerate(iter_note_blocks(hwp), 1):
        src = f"문제_{idx:03d}"
        print(f"{idx}/{total_blocks}: {src}")

        start, end = block

        # 블록 선택
        hwp.SetPos(*start)
        hwp.Run("Select")
        hwp.SetPos(*end)

        # 저장 경로 생성
        target_path = make_hwp_path(src, idx, out_dir=str(output_dir))

        # 저장
        result = save_block(hwp, filepath=target_path)

        if result and target_path.exists():
            file_size = target_path.stat().st_size
            total_size += file_size
            success_count += 1
            print(f"  ✓ 저장: {target_path.name} ({file_size:,} bytes)")
        else:
            print(f"  ✗ 실패")

print(f"\n=== 결과 ===")
print(f"성공: {success_count}/{total_blocks}")
print(f"총 크기: {total_size:,} bytes")
print(f"평균 크기: {total_size // success_count:,} bytes" if success_count > 0 else "")
print(f"출력 폴더: {output_dir}")
