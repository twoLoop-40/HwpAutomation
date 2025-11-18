"""
통합 Merger (병렬 전처리 + 순차 합병)

2단계 워크플로우:
1. 병렬 전처리: 원본 파일들 → 전처리된 파일들 (20 workers)
2. 순차 합병: 전처리된 파일들 → 최종 문서 (Copy/Paste)

모듈화: 각 단계를 독립적으로 실행 가능
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

# UTF-8 설정 (모듈 import 시에는 하지 않음 - 메인 스크립트에서만)

from core.automation_client import AutomationClient

from .types import ProblemFile, MergeConfig
from .parallel_preprocessor import (
    ParallelPreprocessor,
    PreprocessConfig,
    PreprocessResult
)
from .column import break_column


class IntegratedMerger:
    """
    통합 Merger

    병렬 전처리 + 순차 합병을 분리하여 실행
    """

    def __init__(self):
        self.target_client: Optional[AutomationClient] = None

    def step1_parallel_preprocess(
        self,
        problem_files: List[ProblemFile],
        max_workers: int = 20,
        output_dir: str = "Tests/AppV1/Preprocessed"
    ) -> Tuple[List[PreprocessResult], List[PreprocessResult]]:
        """
        Step 1: 병렬 전처리

        원본 파일들을 병렬로 전처리 (1단 변환 + Para 스캔 + 빈 Para 제거)

        Args:
            problem_files: 전처리할 문항 파일 리스트
            max_workers: 최대 워커 수 (기본: 20)
            output_dir: 출력 디렉토리

        Returns:
            (성공 결과 리스트, 실패 결과 리스트)
        """
        print('=' * 70)
        print('[Step 1] 병렬 전처리')
        print('=' * 70)

        # 설정
        config = PreprocessConfig(
            max_workers=max_workers,
            output_dir=output_dir,
            keep_original=True,
            timeout=60.0
        )

        # 병렬 전처리 실행
        preprocessor = ParallelPreprocessor(config)

        file_paths = [str(f.path.absolute()) for f in problem_files]

        start_time = time.time()
        success_results, failure_results = preprocessor.preprocess_parallel(file_paths)
        elapsed = time.time() - start_time

        # 결과 집계
        summary = preprocessor.summarize(success_results, failure_results)

        print('\n' + '=' * 70)
        print('[Step 1 완료] 병렬 전처리 결과')
        print('=' * 70)
        print(f'전체 파일: {summary["total_files"]}개')
        print(f'성공: {summary["success_count"]}개')
        print(f'실패: {summary["failure_count"]}개')
        print(f'전체 Para: {summary["total_paras"]}개')
        print(f'제거된 빈 Para: {summary["total_removed"]}개')
        print(f'총 처리 시간: {elapsed:.1f}초 (~{elapsed/60:.1f}분)')
        print('=' * 70)

        return success_results, failure_results

    def step2_sequential_merge(
        self,
        preprocessed_results: List[PreprocessResult],
        template_path: Path,
        output_path: Path
    ) -> Tuple[bool, int]:
        """
        Step 2: 순차 합병

        전처리된 파일들을 순차적으로 Copy/Paste하여 최종 문서 생성

        Args:
            preprocessed_results: 전처리 성공 결과 리스트
            template_path: 양식 파일 경로
            output_path: 출력 파일 경로

        Returns:
            (성공 여부, 최종 페이지 수)
        """
        print('\n' + '=' * 70)
        print('[Step 2] 순차 합병')
        print('=' * 70)
        print(f'전처리된 파일 수: {len(preprocessed_results)}개')
        print(f'양식: {template_path.name}')
        print(f'출력: {output_path}')
        print()

        # 클라이언트 초기화
        source_client = AutomationClient()
        target_client = AutomationClient()

        try:
            source_hwp = source_client.hwp
            target_hwp = target_client.hwp

            # 보안 모듈
            source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

            # 창 숨기기
            try:
                source_hwp.XHwpWindows.Item(0).Visible = False
                target_hwp.XHwpWindows.Item(0).Visible = False
            except:
                pass

            # 1. 양식 파일 열기
            print('[양식 열기]')
            result = target_client.open_document(str(template_path))
            if not result.success:
                print(f'❌ 양식 열기 실패: {result.error}')
                return (False, 0)

            print('✅ 양식 준비 완료')

            # 본문 시작 위치로 이동
            target_hwp.Run("MoveDocBegin")
            time.sleep(0.05)
            target_hwp.Run("MoveParaBegin")
            time.sleep(0.05)

            # 2. 전처리된 파일들을 순차적으로 Copy/Paste
            print(f'\n[문항 삽입] 시작...')
            print('-' * 70)

            start_time = time.time()
            inserted = 0

            for i, result in enumerate(preprocessed_results, 1):
                if not result.preprocessed_path:
                    print(f'[{i:2d}/{len(preprocessed_results)}] ❌ 스킵 (전처리 실패)')
                    continue

                preprocessed_file = Path(result.preprocessed_path)
                progress = (i / len(preprocessed_results)) * 100

                print(f'[{i:2d}/{len(preprocessed_results)}] ({progress:5.1f}%) {preprocessed_file.name[:50]:50s}', end='')

                try:
                    # 전처리된 파일 열기
                    open_result = source_client.open_document(str(preprocessed_file.absolute()))
                    if not open_result.success:
                        print(f' ❌ 열기 실패')
                        continue

                    time.sleep(0.1)

                    # Copy
                    source_hwp.Run("MoveDocBegin")
                    source_hwp.Run("SelectAll")
                    source_hwp.Run("Copy")
                    time.sleep(0.1)

                    # 소스 닫기 (CRITICAL: 붙여넣기 전에 닫기)
                    source_hwp.Run("Cancel")
                    source_client.close_document()

                    # Paste
                    target_hwp.Run("Paste")
                    time.sleep(0.1)

                    inserted += 1
                    print(f' ✅')

                    # BreakColumn (마지막 문항 제외)
                    if i < len(preprocessed_results):
                        break_column(target_hwp)

                except Exception as e:
                    print(f' ❌ {str(e)[:30]}')

                # 10개마다 진행 상황
                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = avg_time * (len(preprocessed_results) - i)
                    print(f'  --- 진행: {i}/{len(preprocessed_results)} ({elapsed:.1f}초 경과, 예상 남은 시간: {remaining:.1f}초)')

            elapsed_total = time.time() - start_time

            print('-' * 70)
            print(f'✅ 문항 삽입 완료 (총 {elapsed_total:.1f}초)')

            # 3. 결과 저장
            print(f'\n[저장] 결과 저장 중...')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            target_hwp.SaveAs(str(output_path.absolute()))
            time.sleep(0.5)

            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f'✅ 저장 완료')
                print(f'   파일: {output_path}')
                print(f'   크기: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)')
            else:
                print(f'⚠️  저장 실패')
                return (False, 0)

            # 4. 최종 페이지 수
            page_count = target_hwp.PageCount

            print('\n' + '=' * 70)
            print('[Step 2 완료] 순차 합병 결과')
            print('=' * 70)
            print(f'삽입 성공: {inserted}개')
            print(f'최종 페이지: {page_count}개')
            print(f'소요 시간: {elapsed_total:.1f}초')
            print(f'파일당 평균: {elapsed_total / len(preprocessed_results):.2f}초')
            print('=' * 70)

            return (True, page_count)

        except Exception as e:
            print(f'\n💥 오류 발생: {e}')
            import traceback
            traceback.print_exc()
            return (False, 0)

        finally:
            # 정리
            print(f'\n[정리] 문서 닫기...')
            if target_client:
                target_client.close_document()
            if source_client:
                source_client.cleanup()
            if target_client:
                target_client.cleanup()
            time.sleep(0.5)
            print('✅ 정리 완료')

    def merge_with_parallel_preprocessing(
        self,
        config: MergeConfig,
        max_workers: int = 20
    ) -> Tuple[bool, int]:
        """
        전체 워크플로우 실행

        Step 1: 병렬 전처리 → Step 2: 순차 합병

        Args:
            config: 합병 설정
            max_workers: 병렬 처리 워커 수

        Returns:
            (성공 여부, 최종 페이지 수)
        """
        overall_start = time.time()

        print('=' * 70)
        print('AppV1: 통합 Merger (병렬 전처리 + 순차 합병)')
        print('=' * 70)
        print(f'문항 수: {len(config.problem_files)}개')
        print(f'병렬 워커: {max_workers}개')
        print(f'출력: {config.output_path}')
        print('=' * 70)

        # Step 1: 병렬 전처리
        success_results, failure_results = self.step1_parallel_preprocess(
            config.problem_files,
            max_workers=max_workers,
            output_dir="Tests/AppV1/Preprocessed"
        )

        if len(success_results) == 0:
            print('\n❌ 전처리된 파일이 없습니다.')
            return (False, 0)

        # Step 2: 순차 합병
        success, page_count = self.step2_sequential_merge(
            success_results,
            config.template_path,
            config.output_path
        )

        overall_elapsed = time.time() - overall_start

        # 최종 요약
        print('\n' + '=' * 70)
        print('최종 요약')
        print('=' * 70)
        print(f'전체 소요 시간: {overall_elapsed:.1f}초 (~{overall_elapsed/60:.1f}분)')
        print(f'Step 1 (병렬 전처리): ~{overall_elapsed * 0.7:.1f}초')
        print(f'Step 2 (순차 합병): ~{overall_elapsed * 0.3:.1f}초')
        print(f'최종 페이지: {page_count}개')
        print(f'성공 여부: {"✅" if success else "❌"}')
        print('=' * 70)

        return (success, page_count)
