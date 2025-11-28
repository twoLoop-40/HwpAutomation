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
    Specs/HwpIdris/AppV1/EnhancedPreprocessor.idr 확장
    """
    success: bool
    original_path: str
    preprocessed_path: Optional[str]
    para_count: int
    removed_count: int
    processing_time: float
    error_message: Optional[str] = None
    # Enhanced fields (EnhancedPreprocessor.idr)
    initial_page_count: int = 0
    final_page_count: int = 0
    page_deleted: bool = False


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
    Specs/HwpIdris/AppV1/EnhancedPreprocessor.idr 구현

    순서 (Enhanced):
    1. 파일 열기
    2. PageCount 확인
    3. PageCount >= 2이면 마지막 페이지 삭제 (DeletePage)
    4. 1단으로 변환
    5. Para 스캔
    6. 빈 Para 제거 (뒤에서부터)
    7. 임시 파일로 저장
    8. 파일 닫기

    Args:
        file_path: 원본 파일 경로
        output_dir: 출력 디렉토리
        file_index: 파일 인덱스 (로깅용)

    Returns:
        PreprocessResult (with page deletion info)
    """
    start_time = time.time()
    client = None

    try:
        # 1. 클라이언트 초기화
        try:
            client = AutomationClient()
            hwp = client.hwp
        except Exception as e:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Client init failed: {e}"
            )

        # 보안 모듈
        try:
            hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        except Exception as e:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Register module failed: {e}"
            )

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

        # 2. PageCount 확인 (EnhancedPreprocessor.idr: Step 1)
        initial_page_count = hwp.PageCount
        page_deleted = False

        # 3. 조건부 페이지 삭제 (DISABLED - 너무 공격적)
        # 문제: 내용이 있는 페이지도 삭제해버림
        # 해결: Para 제거 로직만 사용
        #
        # if initial_page_count >= 2:
        #     try:
        #         hwp.Run("MoveDocEnd")
        #         time.sleep(0.05)
        #         hwp.HAction.GetDefault("DeletePage", hwp.HParameterSet.HDeletePage.HSet)
        #         hwp.HAction.Execute("DeletePage", hwp.HParameterSet.HDeletePage.HSet)
        #         time.sleep(0.1)
        #         page_deleted = True
        #     except Exception as e:
        #         pass

        # 4. 1단으로 변환
        try:
            convert_to_single_column(hwp)
        except Exception as e:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Convert to single column failed: {str(e)}"
            )

        # 5. Para 스캔
        try:
            paras = scan_paras(hwp)
        except Exception as e:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=0,
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Para scan failed: {str(e)}"
            )

        # 6. 빈 Para 제거
        try:
            removed = remove_empty_paras(hwp, paras)
        except Exception as e:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=len(paras),
                removed_count=0,
                processing_time=time.time() - start_time,
                error_message=f"Remove empty paras failed: {str(e)}"
            )

        # 6. 임시 파일로 저장
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 파일명에서 _N.hwp 패턴 제거 (원본이 xxx_1.hwp 형식인 경우)
        original_name = file_path_obj.stem  # 확장자 제거
        if original_name.endswith('_1'):
            # _1 제거
            base_name = original_name[:-2]
        else:
            base_name = original_name

        output_file = output_path / f"preprocessed_{file_index:03d}_{base_name}.hwp"

        # 기존 파일 삭제 (덮어쓰기 방지)
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception:
                pass

        # AutomationClient의 save_document_as 사용
        result = client.save_document_as(str(output_file.absolute()))
        if not result.success:
            return PreprocessResult(
                success=False,
                original_path=file_path,
                preprocessed_path=None,
                para_count=len(paras),
                removed_count=removed,
                processing_time=time.time() - start_time,
                error_message=f"Save failed: {result.error}"
            )
        time.sleep(0.2)

        # 8. 최종 페이지 수 확인
        final_page_count = hwp.PageCount

        # 9. 파일 닫기
        client.close_document()

        processing_time = time.time() - start_time

        return PreprocessResult(
            success=True,
            original_path=file_path,
            preprocessed_path=str(output_file),
            para_count=len(paras),
            removed_count=removed,
            processing_time=processing_time,
            error_message=None,
            # Enhanced fields
            initial_page_count=initial_page_count,
            final_page_count=final_page_count,
            page_deleted=page_deleted
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

        submit_start = time.time()
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

            submit_time = time.time() - submit_start
            print(f'✓ {total}개 작업을 병렬로 제출 완료 ({submit_time:.2f}초)')
            print(f'  → 최대 {self.config.max_workers}개 파일이 동시에 처리됩니다')
            print('-' * 70)

            # 완료된 작업부터 수집
            completed = 0
            for future in as_completed(future_to_index.keys()):
                index, file_path = future_to_index[future]

                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)

                    completed += 1
                    progress = (completed / total) * 100

                    # 진행률 출력 (EnhancedPreprocessor.idr: 페이지 삭제 정보 포함)
                    status = '✅' if result.success else '❌'
                    file_name = Path(file_path).name[:40]

                    # 페이지 정보 표시
                    page_info = ''
                    if result.page_deleted:
                        page_info = f'Pg:{result.initial_page_count}→{result.final_page_count} '

                    # 오류 메시지 표시 (실패 시)
                    error_msg = ''
                    if not result.success and result.error_message:
                        error_msg = f' | {result.error_message[:50]}'

                    print(f'[{completed:2d}/{total}] ({progress:5.1f}%) {status} {file_name:40s} '
                          f'{page_info}'
                          f'Para:{result.para_count:3d} Rm:{result.removed_count:2d} '
                          f'{result.processing_time:.2f}s{error_msg}')

                    # UI 진행률 콜백 호출
                    if progress_callback:
                        try:
                             # 4 args format
                            progress_callback(
                                'preprocess',
                                completed,
                                total,
                                f"{status} {file_name[:30]}"
                            )
                        except TypeError:
                            # 2 args format fallback
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

        # 병렬 처리 성능 요약
        total_wall_time = time.time() - submit_start
        total_cpu_time = sum(r.processing_time for r in results)
        if total_wall_time > 0:
            speedup = total_cpu_time / total_wall_time
            efficiency = (speedup / self.config.max_workers) * 100
            print(f'\n병렬 처리 성능:')
            print(f'  실제 소요 시간 (wall time): {total_wall_time:.2f}초')
            print(f'  총 CPU 시간 (sum of all): {total_cpu_time:.2f}초')
            print(f'  속도 향상 (speedup): {speedup:.1f}x')
            print(f'  병렬 효율 (efficiency): {efficiency:.1f}%')
            print(f'  → 순차 처리 대비 약 {total_cpu_time - total_wall_time:.1f}초 절약')
            print('-' * 70)

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
