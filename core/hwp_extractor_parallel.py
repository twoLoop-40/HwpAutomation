"""
HWP 병렬 블록 추출 - 파일 복사 기반

Idris2 명세: Specs/Extractor/ParallelExtraction.idr

검증됨:
- Copy/Paste 방식 사용 (Solution3)
- 최대 5개 병렬 워커 (일반 PC 고려)
- 순차 배치 처리 (메모리 관리)
- 파일 복사로 COM 객체 충돌 방지

방식:
1. 원본 파일을 N개 복사 (N = 배치당 워커 수, 최대 5)
2. ProcessPoolExecutor로 병렬 처리
3. 각 프로세스가 별도 파일 열기
4. 배치 완료 후 복사본 삭제
5. 다음 배치 진행
"""
import win32com.client as win32
import pythoncom
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, Optional, List
import shutil
import os
import time

from .hwp_extractor import open_hwp, iter_note_blocks, Block
from .hwp_extractor_copypaste import extract_block_copypaste


def worker_extract_group(
    file_copy_path: str,
    all_blocks: List[Block],
    group_indices: List[int],  # 0-based
    output_path: str,
    verbose: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    워커 함수: 별도 프로세스에서 실행

    Idris2 명세:
    WorkerFunction =
      (fileCopy : FileCopy)
      -> (blocks : List Block)
      -> (groupIndices : List Nat)
      -> (outputPath : String)
      -> IO (Bool, Maybe String)

    Args:
        file_copy_path: 복사된 HWP 파일 경로
        all_blocks: 전체 블록 리스트 (block 0 제외됨)
        group_indices: 병합할 블록 인덱스 (0-based)
        output_path: 저장 경로
        verbose: 상세 로그 출력 여부

    Returns:
        (성공 여부, 저장 경로 또는 None)
    """
    # ProcessPoolExecutor에서는 각 프로세스가 COM 초기화 필요
    pythoncom.CoInitialize()

    try:
        if verbose:
            print(f"[워커] 파일 열기: {file_copy_path}")
            print(f"[워커] 그룹 인덱스: {group_indices}")

        with open_hwp(file_copy_path) as hwp:
            # 그룹의 첫 블록 시작 ~ 마지막 블록 끝
            try:
                first_block = all_blocks[group_indices[0]]
                last_block = all_blocks[group_indices[-1]]

                if not first_block or not last_block:
                    print(f"[워커] ERROR: 블록 정보 없음")
                    return (False, None)

                merged_block = (first_block[0], last_block[1])
            except IndexError as e:
                print(f"[워커] ERROR: 인덱스 오류 - {e}")
                return (False, None)

            if verbose:
                print(f"[워커] 병합 블록: {merged_block}")

            # Copy/Paste 추출
            success = extract_block_copypaste(hwp, merged_block, output_path, verbose)

            # 파일 존재 여부가 더 신뢰할 수 있음
            output_file = Path(output_path)
            if output_file.exists():
                file_size = output_file.stat().st_size
                if verbose:
                    print(f"[워커] 성공: {file_size:,} bytes")
                return (True, output_path)
            else:
                if verbose:
                    print(f"[워커] 실패: 파일 생성 안됨")
                return (False, None)

    except Exception as e:
        print(f"[워커] 오류: {e}")
        import traceback
        traceback.print_exc()
        return (False, None)

    finally:
        pythoncom.CoUninitialize()


def extract_blocks_parallel(
    hwp_file_path: str,
    output_dir: str | Path,
    blocks_per_group: int = 3,
    max_workers: int = 5,
    verbose: bool = False
) -> List[Tuple[bool, Optional[Path]]]:
    """
    병렬 블록 추출

    Idris2 명세:
    ParallelExtractAll =
      (hwpFilePath : String)
      -> (outputDir : String)
      -> (grouping : GroupingStrategy)
      -> (memory : MemoryConstraint)
      -> IO (List (Bool, Maybe String))

    Args:
        hwp_file_path: 원본 HWP 파일
        output_dir: 출력 디렉토리
        blocks_per_group: 그룹당 블록 수 (기본: 3)
        max_workers: 최대 병렬 워커 수 (기본: 5)
        verbose: 상세 로그 출력 여부

    Returns:
        [(성공 여부, 저장 경로), ...] 리스트
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1단계: 블록 위치 수집
    print(f"1단계: 블록 위치 수집 중...")
    print(f"  파일: {Path(hwp_file_path).name}")
    print(f"  파일 열기 시도...")

    try:
        with open_hwp(hwp_file_path) as hwp:
            print(f"  파일 열기 성공!")
            print(f"  EndNote 블록 탐색 중 (시간이 걸릴 수 있습니다)...")
            all_blocks = list(iter_note_blocks(hwp))
            print(f"  블록 탐색 완료!")
    except Exception as e:
        print(f"  [ERROR] 파일 열기 실패: {e}")
        raise

    total_blocks = len(all_blocks)
    print(f"총 {total_blocks}개 블록 발견")

    # 블록 0 제외 (첫 번째 문항 이전 부분)
    all_blocks = all_blocks[1:]
    actual_problems = len(all_blocks)
    print(f"블록 0 제외, 실제 문항: {actual_problems}개\n")

    # 2단계: 그룹 분할 ([1,2,3], [4,5,6], ...)
    groups = []
    for i in range(0, actual_problems, blocks_per_group):
        group = list(range(i, min(i + blocks_per_group, actual_problems)))
        groups.append(group)

    print(f"2단계: {len(groups)}개 그룹으로 분할")
    for idx, group in enumerate(groups, 1):
        print(f"  그룹 {idx}: 블록 {[g+1 for g in group]}")  # 1-based 표시

    # 3단계: 배치 분할 (최대 max_workers개씩)
    batches = []
    for i in range(0, len(groups), max_workers):
        batch = groups[i:i+max_workers]
        batches.append(batch)

    print(f"\n3단계: {len(batches)}개 배치로 분할 (배치당 최대 {max_workers}개 그룹)")
    for batch_idx, batch in enumerate(batches, 1):
        print(f"  배치 {batch_idx}: {len(batch)}개 그룹")

    # 4단계: 각 배치 순차 처리
    print(f"\n4단계: 병렬 추출 시작\n")

    all_results = []

    for batch_idx, batch in enumerate(batches, 1):
        print(f"=== 배치 {batch_idx}/{len(batches)} 처리 중 ({len(batch)}개 그룹) ===\n")

        # 4-1. 파일 복사 생성 및 검증
        file_copies = []
        original_path = Path(hwp_file_path)
        original_size = original_path.stat().st_size
        temp_dir = output_path / "_temp"
        temp_dir.mkdir(exist_ok=True)

        for worker_id in range(len(batch)):
            copy_name = f"{original_path.stem}_temp_{batch_idx}_{worker_id}{original_path.suffix}"
            copy_path = temp_dir / copy_name

            # 파일 복사
            shutil.copy(hwp_file_path, copy_path)

            # 복사 완료 검증 (크기 확인)
            max_retries = 5
            for _ in range(max_retries):
                copy_size = copy_path.stat().st_size
                if copy_size == original_size:
                    break
                # 복사 중일 수 있음 - 짧은 대기 후 재확인
                time.sleep(0.1)
            else:
                # 최대 재시도 후에도 크기 불일치
                print(f"경고: 복사본 크기 불일치 - 원본: {original_size:,}, 복사: {copy_size:,}")

            file_copies.append(copy_path)
            if verbose:
                print(f"파일 복사: {copy_path.name} ({copy_size:,} bytes)")

        # 4-2. 병렬 처리
        batch_results = []

        with ProcessPoolExecutor(max_workers=len(batch)) as executor:
            futures = {}

            for worker_id, group in enumerate(batch):
                # 출력 파일명
                filename = f"문제_{group[0]+1:03d}_to_{group[-1]+1:03d}.hwp"
                output_file = output_path / filename

                # 워커 제출
                future = executor.submit(
                    worker_extract_group,
                    str(file_copies[worker_id]),
                    all_blocks,
                    group,
                    str(output_file),
                    verbose
                )
                futures[future] = (group, output_file)

            # 결과 대기
            for future in as_completed(futures):
                group, output_file = futures[future]
                try:
                    success, result_path = future.result()

                    if success and output_file.exists():
                        file_size = output_file.stat().st_size
                        print(f"[OK] 그룹 {[g+1 for g in group]}: {file_size:,} bytes")
                        batch_results.append((True, output_file))
                    else:
                        print(f"[FAIL] 그룹 {[g+1 for g in group]}: 실패")
                        batch_results.append((False, None))

                except Exception as e:
                    print(f"[ERROR] 그룹 {[g+1 for g in group]}: 오류 - {e}")
                    batch_results.append((False, None))

        # 4-3. 복사본 삭제
        if verbose:
            print(f"\n복사본 파일 삭제 중...")

        for copy_path in file_copies:
            try:
                copy_path.unlink()
            except Exception as e:
                print(f"경고: 복사본 삭제 실패 - {copy_path.name}: {e}")

        # 임시 디렉토리 삭제 시도
        try:
            if temp_dir.exists() and not list(temp_dir.iterdir()):
                temp_dir.rmdir()
        except:
            pass

        all_results.extend(batch_results)

        print(f"\n배치 {batch_idx} 완료: {sum(1 for ok, _ in batch_results if ok)}/{len(batch_results)} 성공\n")

        # 다음 배치 전 짧은 대기 (메모리 정리)
        if batch_idx < len(batches):
            time.sleep(1.0)

    return all_results


if __name__ == "__main__":
    # 테스트
    import sys

    if len(sys.argv) < 2:
        print("사용법: python hwp_extractor_parallel.py <hwp_file>")
        sys.exit(1)

    hwp_file = sys.argv[1]
    output_dir = Path(hwp_file).parent / f"{Path(hwp_file).stem}_parallel"

    print(f"=== HWP 병렬 블록 추출 ===\n")
    print(f"입력: {Path(hwp_file).name}")
    print(f"출력: {output_dir}\n")
    print(f"명세: Specs/Extractor/ParallelExtraction.idr\n")

    results = extract_blocks_parallel(hwp_file, output_dir, verbose=True)

    # 결과 요약
    success_count = sum(1 for ok, _ in results if ok)
    total_count = len(results)
    total_size = sum(p.stat().st_size for ok, p in results if ok and p)

    print(f"\n=== 요약 ===")
    print(f"성공: {success_count}/{total_count} 그룹")
    print(f"총 크기: {total_size:,} bytes")
    if success_count > 0:
        print(f"평균 크기: {total_size // success_count:,} bytes")
    print(f"출력 폴더: {output_dir}")
