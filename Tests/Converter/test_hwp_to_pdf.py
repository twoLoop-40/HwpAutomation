"""
HWP to PDF Converter 테스트

Idris2 명세: Specs/Converter/Types.idr

테스트 데이터: Tests/hwp2pdf/*.hwp (15개 파일)
"""
import sys
from pathlib import Path
from glob import glob

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.hwp_to_pdf import convert_single_hwp_to_pdf, convert_hwp_to_pdf_parallel


def test_single_conversion():
    """단일 파일 변환 테스트"""
    print("=== 단일 파일 변환 테스트 ===\n")

    # 첫 번째 파일로 테스트
    test_dir = project_root / "Tests" / "hwp2pdf"
    hwp_files = sorted(test_dir.glob("*.hwp"))

    if not hwp_files:
        print(f"❌ 테스트 파일 없음: {test_dir}")
        return

    test_file = str(hwp_files[0])
    print(f"테스트 파일: {Path(test_file).name}")

    success, output_path, error = convert_single_hwp_to_pdf(test_file, verbose=True)

    if success:
        print(f"\n✅ 변환 성공!")
        print(f"   출력: {output_path}")

        # 파일 크기 확인
        pdf_size = Path(output_path).stat().st_size / 1024
        print(f"   크기: {pdf_size:.1f} KB")
    else:
        print(f"\n❌ 변환 실패: {error}")


def test_parallel_conversion():
    """병렬 변환 테스트 - 15개 파일"""
    print("\n=== 병렬 변환 테스트 (15개 파일) ===\n")

    # Tests/hwp2pdf 디렉토리의 모든 HWP 파일
    test_dir = project_root / "Tests" / "hwp2pdf"
    hwp_files = sorted(test_dir.glob("*.hwp"))

    if not hwp_files:
        print(f"❌ 테스트 파일 없음: {test_dir}")
        return

    print(f"발견된 파일: {len(hwp_files)}개")
    for i, f in enumerate(hwp_files[:3], 1):
        print(f"  {i}. {f.name}")
    if len(hwp_files) > 3:
        print(f"  ... 외 {len(hwp_files)-3}개")

    print(f"\n병렬 변환 시작 (max_workers=5)...\n")

    results = convert_hwp_to_pdf_parallel(
        hwp_files=[str(f) for f in hwp_files],
        max_workers=5,
        verbose=True
    )

    # 결과 분석
    success_count = sum(1 for s, _, _ in results if s)
    fail_count = len(results) - success_count

    print(f"\n{'='*50}")
    print(f"통계: 성공 {success_count}, 실패 {fail_count}")

    if fail_count > 0:
        print(f"\n실패한 파일:")
        for i, (success, output, error) in enumerate(results):
            if not success:
                print(f"  - {hwp_files[i].name}: {error}")

    # 생성된 PDF 파일 확인
    pdf_files = sorted(test_dir.glob("*.pdf"))
    if pdf_files:
        total_size = sum(f.stat().st_size for f in pdf_files) / 1024
        print(f"\n생성된 PDF: {len(pdf_files)}개 (총 {total_size:.1f} KB)")


def test_parallel_small():
    """소규모 병렬 테스트 - 5개 파일"""
    print("\n=== 소규모 병렬 테스트 (5개 파일) ===\n")

    # 처음 5개 파일만 선택
    test_dir = project_root / "Tests" / "hwp2pdf"
    hwp_files = sorted(test_dir.glob("*.hwp"))[:5]

    if not hwp_files:
        print(f"❌ 테스트 파일 없음: {test_dir}")
        return

    print(f"테스트 파일:")
    for i, f in enumerate(hwp_files, 1):
        print(f"  {i}. {f.name}")

    print(f"\n병렬 변환 시작 (max_workers=5)...\n")

    results = convert_hwp_to_pdf_parallel(
        hwp_files=[str(f) for f in hwp_files],
        max_workers=5,
        verbose=True
    )

    # 결과 분석
    success_count = sum(1 for s, _, _ in results if s)
    fail_count = len(results) - success_count

    print(f"\n{'='*50}")
    print(f"통계: 성공 {success_count}, 실패 {fail_count}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HWP to PDF 변환 테스트")
    parser.add_argument(
        '--mode',
        choices=['single', 'small', 'all'],
        default='small',
        help='테스트 모드: single(1개), small(5개), all(15개)'
    )
    args = parser.parse_args()

    if args.mode == 'single':
        test_single_conversion()
    elif args.mode == 'small':
        test_parallel_small()
    elif args.mode == 'all':
        test_parallel_conversion()
