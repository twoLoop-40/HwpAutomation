"""
3문항씩 묶어서 병렬 추출 테스트

Idris2 명세: Specs/Extractor/ParallelExtraction.idr

전략:
1. 전체 블록 위치를 먼저 수집 (list(iter_note_blocks))
2. 블록 0 제외
3. 3개씩 묶어서 그룹화: [1,2,3], [4,5,6], [7,8,9], ...
4. 그룹들을 배치로 분할 (최대 5개 병렬)
5. 각 배치 순차 처리:
   - 원본 파일을 N개 복사 (N = 배치당 그룹 수)
   - ProcessPoolExecutor로 병렬 처리
   - 각 워커: 복사본 열기 → 그룹 추출 → 닫기
   - 복사본 삭제
6. 다음 배치 진행
"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

sys.path.insert(0, r'c:\\Users\\joonho.lee\\Projects\\AutoHwp')

from core.hwp_extractor_parallel import extract_blocks_parallel


def main():
    # 입력 파일
    input_file = r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\seperation\22개정 EBS 올림포스 기출문제집 공통수학2_7.도형의 방정식2_3.hwp"
    input_path = Path(input_file)

    # 출력 폴더: 파일명_parallel2 (디버깅)
    output_dir = input_path.parent / f"{input_path.stem}_parallel2"

    print(f"=== 3문항씩 묶어서 병렬 추출 ===\n")
    print(f"입력: {input_path.name}")
    print(f"출력: {output_dir}\n")
    print(f"명세: Specs/Extractor/ParallelExtraction.idr\n")
    print(f"설정: 3문항/그룹, 최대 5개 병렬\n")

    # 병렬 추출 실행
    results = extract_blocks_parallel(
        input_file,
        output_dir,
        blocks_per_group=3,
        max_workers=5,
        verbose=True  # 워커별 상세 로그 활성화 (디버깅)
    )

    # 결과 분석
    success_count = sum(1 for ok, _ in results if ok)
    total_count = len(results)
    total_size = sum(p.stat().st_size for ok, p in results if ok and p)

    print(f"\n=== 최종 요약 ===")
    print(f"성공: {success_count}/{total_count} 그룹")
    print(f"총 크기: {total_size:,} bytes")
    if success_count > 0:
        print(f"평균 크기: {total_size // success_count:,} bytes")
    print(f"출력 폴더: {output_dir}")


if __name__ == "__main__":
    main()
