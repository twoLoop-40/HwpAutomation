"""
병렬 파일 전처리 모듈

각 문항 파일을 독립적으로 처리:
1. 1단 변환
2. 빈 Para 제거
3. 임시 파일 저장
"""
import time
from pathlib import Path
from typing import List
from multiprocessing import Pool, cpu_count
from tempfile import mkdtemp

from core.automation_client import AutomationClient
from .types import ProblemFile
from .column import convert_to_single_column
from .para_scanner import scan_paras, remove_empty_paras


def preprocess_single_file(args):
    """
    단일 파일 전처리 (병렬 실행용)

    Returns: (success, problem, processed_path, error_msg)
    """
    problem, temp_dir = args

    try:
        # 각 프로세스마다 독립적인 HWP 클라이언트
        client = AutomationClient()
        hwp = client.hwp

        # 보안 모듈
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 창 숨기기
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # 1. 파일 열기
        result = client.open_document(str(problem.path))
        if not result.success:
            client.cleanup()
            return (False, problem, None, f"열기 실패: {result.error}")

        # 2. 1단 변환
        convert_to_single_column(hwp)

        # 3. Para 스캔 및 빈 Para 제거
        paras = scan_paras(hwp)
        removed = remove_empty_paras(hwp, paras)

        # 4. 임시 파일로 저장
        processed_path = Path(temp_dir) / f"processed_{problem.index:03d}.hwp"
        hwp.SaveAs(str(processed_path.absolute()))
        time.sleep(0.1)

        # 정리
        client.close_document()
        client.cleanup()

        return (True, problem, processed_path, f"Para:{len(paras)} 빈:{removed}")

    except Exception as e:
        return (False, problem, None, str(e)[:50])


def preprocess_files_parallel(problem_files: List[ProblemFile], num_workers: int = None) -> tuple:
    """
    병렬로 파일 전처리

    Returns: (processed_files, temp_dir, failed_files)
        processed_files: [(problem, processed_path), ...]
        temp_dir: 임시 디렉토리 경로
        failed_files: [(problem, error_msg), ...]
    """
    if num_workers is None:
        num_workers = min(cpu_count(), len(problem_files))

    print(f'[병렬 전처리] {len(problem_files)}개 파일, {num_workers}개 워커')

    # 임시 디렉토리 생성
    temp_dir = mkdtemp(prefix="hwp_preprocessed_")
    print(f'임시 디렉토리: {temp_dir}')

    # 병렬 처리 인자 준비
    args_list = [(problem, temp_dir) for problem in problem_files]

    start_time = time.time()
    processed_files = []
    failed_files = []

    # 병렬 실행
    with Pool(processes=num_workers) as pool:
        results = pool.map(preprocess_single_file, args_list)

    # 결과 정리
    for success, problem, processed_path, msg in results:
        if success:
            processed_files.append((problem, processed_path))
            print(f'  [{problem.index:2d}] ✅ {problem.name[:40]} - {msg}')
        else:
            failed_files.append((problem, msg))
            print(f'  [{problem.index:2d}] ❌ {problem.name[:40]} - {msg}')

    elapsed = time.time() - start_time

    print(f'병렬 전처리 완료: {len(processed_files)}개 성공, {len(failed_files)}개 실패')
    print(f'소요 시간: {elapsed:.1f}초 (파일당 평균: {elapsed/len(problem_files):.2f}초)')

    return (processed_files, temp_dir, failed_files)
