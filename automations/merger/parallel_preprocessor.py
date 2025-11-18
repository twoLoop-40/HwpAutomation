"""
병렬 전처리 모듈

HwpIdris/AppV1/ParallelPreprocessor.idr 명세 구현

multiprocessing.ProcessPoolExecutor 기반
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, as_completed

# UTF-8 설정 (모듈 import 시에는 하지 않음 - 메인 스크립트에서만)

from core.automation_client import AutomationClient
from .column import convert_to_single_column
from .para_scanner import scan_paras, remove_empty_paras


@dataclass
class PreprocessResult:
    """
    전처리 작업 결과

    HwpIdris PreprocessResult 구현
    """
    success: bool
    original_path: str
    preprocessed_path: Optional[str]
    para_count: int
    removed_count: int
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class PreprocessConfig:
    """
    전처리 설정

    HwpIdris PreprocessConfig 구현
    """
    max_workers: int = 20
    output_dir: str = "Tests/AppV1/Preprocessed"
    keep_original: bool = True
    timeout: Optional[float] = 30.0


def preprocess_single_file(
    file_path: str,
    output_dir: str,
    file_index: int
) -> PreprocessResult:
    """
    단일 파일 전처리 (별도 프로세스에서 실행)

    HwpIdris preprocessSingleFile 구현

    순서:
    1. 파일 열기
    2. 1단으로 변환
    3. Para 스캔
    4. 빈 Para 제거 (뒤에서부터)
    5. 임시 파일로 저장
    6. 파일 닫기

    Args:
        file_path: 원본 파일 경로
        output_dir: 출력 디렉토리
        file_index: 파일 인덱스 (로깅용)

    Returns:
        PreprocessResult
    """
    start_time = time.time()
    client = None

    try:
        # 1. 클라이언트 초기화
        client = AutomationClient()
        hwp = client.hwp

        # 보안 모듈
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 2. 파일 열기
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"File not found: {file_path}"
            )

        result = client.open_document(str(file_path_obj.absolute()))
        if not result.success:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Failed to open: {result.error}"
            )

        time.sleep(0.1)

        # 파일 확인
        if hwp.PageCount < 1:
            client.close_document()
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message="Empty document"
            )

        # 3. 1단으로 변환
        convert_to_single_column(hwp)

        # 4. Para 스캔
        paras = scan_paras(hwp)

        # 5. 빈 Para 제거
        removed = remove_empty_paras(hwp, paras)

        # 6. 임시 파일로 저장
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        output_file = output_path / f"preprocessed_{file_index:03d}_{file_path_obj.name}"
        hwp.SaveAs(str(output_file.absolute()))
        time.sleep(0.2)

        # 7. 파일 닫기
        client.close_document()

        processing_time = time.time() - start_time

        return PreprocessResult(
            success=True,
            original_path=file_path,
            preprocessed_path=str(output_file),
            para_count=len(paras),
            removed_count=removed,
            processing_time=processing_time,
            error_message=None
        )

    except Exception as e:
        return PreprocessResult(
            success=False,
            original_path=file_path,
            preprocessed_path=None,
            para_count=0,
            removed_count=0,
            processing_time=time.time() - start_time,
            error_message=str(e)
        )

    finally:
        # 정리
        if client:
            try:
                client.cleanup()
            except:
                pass


class ParallelPreprocessor:
    """
    병렬 전처리기

    HwpIdris ParallelPreprocessor 구현
    """

    def __init__(self, config: Optional[PreprocessConfig] = None):
        """
        초기화

        Args:
            config: 전처리 설정 (None이면 기본값 사용)
        """
        self.config = config or PreprocessConfig()

    def preprocess_parallel(
        self,
        file_paths: List[str],
        progress_callback: Optional[callable] = None
    ) -> Tuple[List[PreprocessResult], List[PreprocessResult]]:
        """
        병렬 전처리 실행

        HwpIdris preprocessParallel 구현

        Args:
            file_paths: 전처리할 파일 경로 리스트
            progress_callback: 진행률 콜백 함수 (completed, total)

        Returns:
            (성공 결과 리스트, 실패 결과 리스트)
        """
        total = len(file_paths)
        results = []

        print(f'\n병렬 전처리 시작 (워커: {self.config.max_workers}개)')
        print(f'파일 수: {total}개')
        print('-' * 70)

        # ProcessPoolExecutor 사용
        with ProcessPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 모든 작업 submit
            future_to_index = {}
            for i, file_path in enumerate(file_paths, 1):
                future = executor.submit(
                    preprocess_single_file,
                    file_path,
                    self.config.output_dir,
                    i
                )
                future_to_index[future] = (i, file_path)

            # 완료된 작업부터 수집
            completed = 0
            for future in as_completed(future_to_index.keys()):
                index, file_path = future_to_index[future]

                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)

                    completed += 1
                    progress = (completed / total) * 100

                    # 진행률 출력
                    status = '✅' if result.success else '❌'
                    file_name = Path(file_path).name[:40]
                    print(f'[{completed:2d}/{total}] ({progress:5.1f}%) {status} {file_name:40s} '
                          f'Para:{result.para_count:3d} Rm:{result.removed_count:2d} '
                          f'{result.processing_time:.2f}s')

                    # 콜백 호출
                    if progress_callback:
                        progress_callback(completed, total)

                except Exception as e:
                    # 타임아웃 또는 에러
                    result = PreprocessResult(
                        success=False,
                        original_path=file_path,
                        preprocessed_path=None,
                        para_count=0,
                        removed_count=0,
                        processing_time=0.0,
                        error_message=f"Future error: {e}"
                    )
                    results.append(result)
                    completed += 1

        print('-' * 70)

        # 성공/실패 분리
        success_results = [r for r in results if r.success]
        failure_results = [r for r in results if not r.success]

        return success_results, failure_results

    def summarize(
        self,
        success_results: List[PreprocessResult],
        failure_results: List[PreprocessResult]
    ) -> dict:
        """
        결과 집계

        HwpIdris summarizeResults 구현

        Returns:
            집계 딕셔너리
        """
        all_results = success_results + failure_results

        total_files = len(all_results)
        success_count = len(success_results)
        failure_count = len(failure_results)
        total_paras = sum(r.para_count for r in all_results)
        total_removed = sum(r.removed_count for r in all_results)
        total_time = sum(r.processing_time for r in all_results)
        avg_time = total_time / total_files if total_files > 0 else 0.0

        return {
            'total_files': total_files,
            'success_count': success_count,
            'failure_count': failure_count,
            'total_paras': total_paras,
            'total_removed': total_removed,
            'total_time': total_time,
            'avg_time_per_file': avg_time,
        }


def predict_performance(
    file_count: int,
    avg_time_per_file: float,
    max_workers: int
) -> Tuple[float, float, float]:
    """
    병렬 처리 성능 예측

    HwpIdris predictPerformance 구현

    Returns:
        (순차 처리 시간, 병렬 처리 시간, 개선율 %)
    """
    sequential_time = file_count * avg_time_per_file
    parallel_time = (file_count / max_workers) * avg_time_per_file
    improvement = ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0.0

    return sequential_time, parallel_time, improvement
