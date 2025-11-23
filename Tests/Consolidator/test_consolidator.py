"""
Folder Consolidator 테스트

Idris2 명세: Specs/Consolidator/
"""
# -*- coding: utf-8 -*-
import sys
import io
from pathlib import Path
import tempfile
import shutil

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.folder_consolidator import (
    scan_folders,
    create_target_folder,
    consolidate_parallel
)


def test_scan_folders():
    """1단계: 폴더 스캔 테스트"""
    print("=== 폴더 스캔 테스트 ===\n")

    # 임시 테스트 폴더 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 3개 폴더 생성
        folder1 = temp_path / "folder1"
        folder2 = temp_path / "folder2"
        folder3 = temp_path / "folder3"

        folder1.mkdir()
        folder2.mkdir()
        folder3.mkdir()

        # 각 폴더에 파일 생성
        (folder1 / "file1.txt").write_text("test1")
        (folder1 / "file2.txt").write_text("test2")
        (folder2 / "file3.txt").write_text("test3")
        (folder3 / "file4.txt").write_text("test4")
        (folder3 / "file5.txt").write_text("test5")

        # 스캔
        files = scan_folders([str(folder1), str(folder2), str(folder3)], verbose=True)

        print(f"\n발견된 파일: {len(files)}개")
        assert len(files) == 5, f"예상: 5개, 실제: {len(files)}개"
        print("✅ 스캔 테스트 통과!\n")


def test_create_target():
    """2단계: 대상 폴더 생성 테스트"""
    print("=== 대상 폴더 생성 테스트 ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        target_path = create_target_folder(temp_dir, "test_target", verbose=True)

        assert target_path is not None, "폴더 생성 실패"
        assert Path(target_path).exists(), "폴더가 존재하지 않음"
        print("✅ 대상 폴더 생성 테스트 통과!\n")


def test_consolidate_copy():
    """3단계: 복사 모드 통합 테스트"""
    print("=== 복사 모드 통합 테스트 ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 소스 폴더 생성
        source1 = temp_path / "source1"
        source2 = temp_path / "source2"
        source1.mkdir()
        source2.mkdir()

        # 파일 생성
        (source1 / "file1.txt").write_text("content1")
        (source1 / "file2.txt").write_text("content2")
        (source2 / "file3.txt").write_text("content3")

        # 복사 모드로 통합
        total, success, failed = consolidate_parallel(
            source_folders=[str(source1), str(source2)],
            target_parent=str(temp_path),
            target_name="merged",
            mode="copy",
            max_workers=2,
            verbose=True
        )

        print(f"\n통계: 전체={total}, 성공={success}, 실패={failed}")

        # 검증
        target = temp_path / "merged"
        assert target.exists(), "대상 폴더가 생성되지 않음"
        assert (target / "file1.txt").exists(), "file1.txt가 복사되지 않음"
        assert (target / "file2.txt").exists(), "file2.txt가 복사되지 않음"
        assert (target / "file3.txt").exists(), "file3.txt가 복사되지 않음"

        # 원본 확인 (복사 모드이므로 유지되어야 함)
        assert (source1 / "file1.txt").exists(), "원본 파일이 삭제됨 (복사 모드)"
        assert source1.exists(), "원본 폴더가 삭제됨 (복사 모드)"

        assert success == 3, f"예상 성공: 3, 실제: {success}"
        assert failed == 0, f"예상 실패: 0, 실제: {failed}"

        print("✅ 복사 모드 테스트 통과!\n")


def test_consolidate_move():
    """4단계: 이동 모드 통합 테스트"""
    print("=== 이동 모드 통합 테스트 ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 소스 폴더 생성
        source1 = temp_path / "source1"
        source2 = temp_path / "source2"
        source1.mkdir()
        source2.mkdir()

        # 파일 생성
        (source1 / "file1.txt").write_text("content1")
        (source2 / "file2.txt").write_text("content2")

        # 이동 모드로 통합
        total, success, failed = consolidate_parallel(
            source_folders=[str(source1), str(source2)],
            target_parent=str(temp_path),
            target_name="moved",
            mode="move",
            max_workers=2,
            verbose=True
        )

        print(f"\n통계: 전체={total}, 성공={success}, 실패={failed}")

        # 검증
        target = temp_path / "moved"
        assert target.exists(), "대상 폴더가 생성되지 않음"
        assert (target / "file1.txt").exists(), "file1.txt가 이동되지 않음"
        assert (target / "file2.txt").exists(), "file2.txt가 이동되지 않음"

        # 원본 확인 (이동 모드이므로 삭제되어야 함)
        assert not (source1 / "file1.txt").exists(), "원본 파일이 남아있음 (이동 모드)"
        assert not source1.exists(), "원본 폴더가 남아있음 (이동 모드)"

        assert success == 2, f"예상 성공: 2, 실제: {success}"
        assert failed == 0, f"예상 실패: 0, 실제: {failed}"

        print("✅ 이동 모드 테스트 통과!\n")


def test_parallel_performance():
    """5단계: 병렬 처리 성능 테스트"""
    print("=== 병렬 처리 성능 테스트 ===\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 3개 폴더에 각각 10개 파일 생성
        sources = []
        for i in range(3):
            folder = temp_path / f"source{i}"
            folder.mkdir()
            sources.append(str(folder))

            for j in range(10):
                (folder / f"file{i}_{j}.txt").write_text(f"content {i}-{j}")

        # 병렬 복사
        import time
        start = time.time()

        total, success, failed = consolidate_parallel(
            source_folders=sources,
            target_parent=str(temp_path),
            target_name="parallel_test",
            mode="copy",
            max_workers=5,
            verbose=True
        )

        elapsed = time.time() - start

        print(f"\n소요 시간: {elapsed:.2f}초")
        print(f"통계: 전체={total}, 성공={success}, 실패={failed}")

        assert success == 30, f"예상 성공: 30, 실제: {success}"
        print("✅ 병렬 처리 테스트 통과!\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consolidator 테스트")
    parser.add_argument(
        '--test',
        choices=['scan', 'create', 'copy', 'move', 'parallel', 'all'],
        default='all',
        help='실행할 테스트'
    )
    args = parser.parse_args()

    try:
        if args.test == 'scan' or args.test == 'all':
            test_scan_folders()

        if args.test == 'create' or args.test == 'all':
            test_create_target()

        if args.test == 'copy' or args.test == 'all':
            test_consolidate_copy()

        if args.test == 'move' or args.test == 'all':
            test_consolidate_move()

        if args.test == 'parallel' or args.test == 'all':
            test_parallel_performance()

        print("="*50)
        print("✅ 모든 테스트 통과!")
        print("="*50)

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
