"""
math-collector의 실제 메서드 테스트
"""
import sys
from pathlib import Path

# math-collector 경로 추가
sys.path.insert(0, r'c:\Users\joonho.lee\Projects\math-collector\src')

from tools.handle_hwp import iter_note_blocks, select_and_save, open_hwp

# 테스트 파일
test_file = r"c:\Users\joonho.lee\Projects\math-collector\src\core\merger\테스트_2개문항.hwp"
output_dir = Path("Tests/seperation/output_mathcollector")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"파일: {Path(test_file).name}\n")

with open_hwp(test_file) as hwp:
    # 블록 개수 확인
    blocks = list(iter_note_blocks(hwp))
    print(f"총 {len(blocks)}개 블록\n")

    # 처음 2개 블록만 저장
    for i, (start, end) in enumerate(blocks[:2], 1):
        print(f"블록 {i}: {start} → {end}")

        try:
            # select_and_save 사용
            saver = select_and_save(hwp, idx=i-1, origin_num=i, csv_filename="test.csv")
            is_ok, target_path = saver(f"문제{i}")

            if is_ok:
                print(f"  ✓ 저장 성공: {target_path}\n")
            else:
                print(f"  ✗ 저장 실패\n")

        except Exception as e:
            print(f"  에러: {e}\n")

print("완료!")
