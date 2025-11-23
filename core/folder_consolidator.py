"""
Folder Consolidator - 병렬 파일 통합

Idris2 명세: Specs/Consolidator/Types.idr, Workflow.idr

주요 기능:
- 여러 폴더의 파일을 하나의 폴더로 통합
- 병렬 처리 (ProcessPoolExecutor, max_workers=5)
- 복사 또는 이동 모드
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional
import shutil
import os


def worker_copy_file(
    source_path: str,
    target_dir: str,
    verbose: bool = False
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    워커 함수: 파일 복사

    Idris2 명세: Workflow.ProcessFiles (CopyMode)

    Args:
        source_path: 원본 파일 경로
        target_dir: 대상 디렉토리
        verbose: 상세 로그

    Returns:
        (success, dest_path, error)
    """
    try:
        source = Path(source_path)
        if not source.exists():
            return False, None, f"파일 없음: {source_path}"

        # 대상 경로
        dest = Path(target_dir) / source.name

        # 파일 복사
        shutil.copy2(source, dest)

        if verbose:
            size_kb = dest.stat().st_size / 1024
            print(f"[복사 완료] {source.name} ({size_kb:.1f} KB)")

        return True, str(dest), None

    except Exception as e:
        return False, None, f"복사 실패: {str(e)}"


def worker_move_file(
    source_path: str,
    target_dir: str,
    verbose: bool = False
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    워커 함수: 파일 이동 (복사 + 삭제)

    Idris2 명세: Workflow.ProcessFiles (MoveMode)

    Args:
        source_path: 원본 파일 경로
        target_dir: 대상 디렉토리
        verbose: 상세 로그

    Returns:
        (success, dest_path, error)
    """
    try:
        source = Path(source_path)
        if not source.exists():
            return False, None, f"파일 없음: {source_path}"

        # 대상 경로
        dest = Path(target_dir) / source.name

        # 파일 이동
        shutil.move(str(source), str(dest))

        if verbose:
            size_kb = dest.stat().st_size / 1024
            print(f"[이동 완료] {source.name} ({size_kb:.1f} KB)")

        return True, str(dest), None

    except Exception as e:
        return False, None, f"이동 실패: {str(e)}"


def scan_folders(
    folders: List[str],
    verbose: bool = False
) -> List[str]:
    """
    1단계: 소스 폴더 스캔

    Idris2 명세: Workflow.ScanSources

    Args:
        folders: 소스 폴더 목록
        verbose: 상세 로그

    Returns:
        모든 파일 경로 목록
    """
    all_files = []

    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists() or not folder_path.is_dir():
            if verbose:
                print(f"[경고] 폴더 없음: {folder}")
            continue

        # 폴더 내 모든 파일 수집
        files = [str(f) for f in folder_path.iterdir() if f.is_file()]
        all_files.extend(files)

        if verbose:
            print(f"[스캔] {folder_path.name}: {len(files)}개 파일")

    if verbose:
        print(f"\n[스캔 완료] 총 {len(all_files)}개 파일")

    return all_files


def create_target_folder(
    parent_path: str,
    folder_name: str,
    verbose: bool = False
) -> Optional[str]:
    """
    2단계: 대상 폴더 생성

    Idris2 명세: Workflow.CreateTarget

    Args:
        parent_path: 부모 디렉토리
        folder_name: 새 폴더 이름
        verbose: 상세 로그

    Returns:
        생성된 폴더 경로 (실패 시 None)
    """
    try:
        target = Path(parent_path) / folder_name
        target.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"[대상 폴더 생성] {target}")

        return str(target)

    except Exception as e:
        if verbose:
            print(f"[에러] 폴더 생성 실패: {e}")
        return None


def consolidate_parallel(
    source_folders: List[str],
    target_parent: str,
    target_name: str,
    mode: str = "copy",
    max_workers: int = 5,
    verbose: bool = False
) -> Tuple[int, int, int]:
    """
    병렬 파일 통합

    Idris2 명세:
    - Workflow.copyWorkflow (mode="copy")
    - Workflow.moveWorkflow (mode="move")

    Args:
        source_folders: 소스 폴더 목록
        target_parent: 대상 부모 경로
        target_name: 대상 폴더 이름
        mode: "copy" 또는 "move"
        max_workers: 최대 병렬 워커 수
        verbose: 상세 로그

    Returns:
        (total, success, failed) - OperationStats
    """
    if verbose:
        print(f"[시작] 모드: {mode}, 워커: {max_workers}")

    # 1. ScanSources
    files = scan_folders(source_folders, verbose)
    if not files:
        if verbose:
            print("[에러] 파일 없음")
        return 0, 0, 0

    # 2. CreateTarget
    target_dir = create_target_folder(target_parent, target_name, verbose)
    if not target_dir:
        return len(files), 0, len(files)

    # 3. ProcessFiles (병렬)
    if verbose:
        print(f"\n[병렬 처리 시작] {len(files)}개 파일...")

    worker_fn = worker_move_file if mode == "move" else worker_copy_file
    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(worker_fn, file_path, target_dir, verbose): file_path
            for file_path in files
        }

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                success, dest, error = future.result()
                results.append((success, dest, error))

                if not success and verbose:
                    print(f"[실패] {Path(file_path).name}: {error}")

            except Exception as e:
                results.append((False, None, f"워커 예외: {str(e)}"))
                if verbose:
                    print(f"[실패] {Path(file_path).name}: 워커 예외 {e}")

    # 4. Cleanup (MoveMode만)
    if mode == "move":
        if verbose:
            print(f"\n[정리] 빈 폴더 삭제...")
        for folder in source_folders:
            folder_path = Path(folder)
            if folder_path.exists() and folder_path.is_dir():
                try:
                    if not list(folder_path.iterdir()):  # 빈 폴더
                        folder_path.rmdir()
                        if verbose:
                            print(f"[삭제] {folder_path.name}")
                except Exception as e:
                    if verbose:
                        print(f"[경고] 폴더 삭제 실패: {e}")

    # 5. CollectStats
    total = len(files)
    success = sum(1 for s, _, _ in results if s)
    failed = total - success

    if verbose:
        print(f"\n[완료] 전체: {total}, 성공: {success}, 실패: {failed}")

    return total, success, failed
