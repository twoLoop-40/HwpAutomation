"""
문항 파일 합병 메인 로직

Idris2 명세 (HwpIdris/AppV1/MergeProblemFiles.idr) 구현
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from core.automation_client import AutomationClient

from .types import ProblemFile, ProcessResult, MergeConfig, expected_page_count, validate_page_count
from .column import convert_to_single_column, break_column
from .para_scanner import scan_paras, remove_empty_paras


class ProblemMerger:
    """
    문항 파일 합병 클래스

    Idris2 MergeWorkflowSpec 인터페이스 구현
    """

    def __init__(self):
        self.source_client: Optional[AutomationClient] = None
        self.target_client: Optional[AutomationClient] = None

    def initialize(self) -> bool:
        """클라이언트 초기화"""
        try:
            self.source_client = AutomationClient()
            self.target_client = AutomationClient()

            source_hwp = self.source_client.hwp
            target_hwp = self.target_client.hwp

            # 보안 모듈
            source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

            # 창 숨기기
            try:
                source_hwp.XHwpWindows.Item(0).Visible = False
                target_hwp.XHwpWindows.Item(0).Visible = False
            except:
                pass

            return True

        except Exception as e:
            print(f'❌ 초기화 실패: {e}')
            return False

    def process_single_problem(
        self,
        problem: ProblemFile,
        total_problems: int,
        target_hwp
    ) -> Tuple[bool, ProcessResult]:
        """
        단일 문항 처리

        Idris2 processSingleProblem 구현:
        1. 파일 열기
        2. 1단으로 변환
        3. Para 스캔
        4. 빈 Para 제거 (MoveSelDown 방식)
        5. 복사
        6. 붙여넣기 (test_merge_40_problems_clean.py 패턴)
        """
        try:
            source_hwp = self.source_client.hwp

            # 진행률 표시
            progress = (problem.index / total_problems) * 100
            print(f'  [{problem.index:2d}/{total_problems}] ({progress:5.1f}%) {problem.name[:35]:35s}', end='')

            # Step 1: 파일 열기
            result = self.source_client.open_document(str(problem.path))
            if not result.success:
                print(f' ❌ 열기 실패: {result.error}')
                return (False, ProcessResult(False, 0, 0, 0))

            time.sleep(0.2)

            # 파일이 실제로 열렸는지 확인 (PageCount > 0)
            if source_hwp.PageCount < 1:
                print(f' ❌ 빈 문서')
                self.source_client.close_document()
                return (False, ProcessResult(False, 0, 0, 0))

            # Step 2: 1단으로 변환
            convert_to_single_column(source_hwp)

            # Step 3: Para 스캔
            paras = scan_paras(source_hwp)
            empty_count = sum(1 for p in paras if p.is_empty)

            # Step 4: 빈 Para 제거 (MoveSelDown)
            removed = remove_empty_paras(source_hwp, paras)

            # Step 5: 복사
            source_hwp.Run("MoveDocBegin")
            source_hwp.Run("SelectAll")
            source_hwp.Run("Copy")
            time.sleep(0.15)

            # 소스 파일 닫기 (CRITICAL: 붙여넣기 전에 닫기!)
            source_hwp.Run("Cancel")
            self.source_client.close_document()

            # Step 6: 붙여넣기 (test_merge_40_problems_clean.py 패턴)
            target_hwp.Run("Paste")
            time.sleep(0.15)

            print(f' ✅ Para:{len(paras):2d} 빈:{removed:2d}')

            return (True, ProcessResult(
                success=True,
                para_count=len(paras),
                empty_para_count=empty_count,
                removed_count=removed
            ))

        except Exception as e:
            print(f' ❌ 실패: {str(e)[:20]}')
            return (False, ProcessResult(False, 0, 0, 0))

    def merge_files(self, config: MergeConfig) -> Tuple[bool, int]:
        """
        파일 합병 실행

        Idris2 mergeProblemFiles 구현

        Returns:
            (성공 여부, 최종 페이지 수)
        """
        print('=' * 70)
        print('AppV1: 문항 파일 합병')
        print('=' * 70)
        print(f'양식: {config.template_path.name if config.use_template else "새 문서"}')
        print(f'문항 수: {len(config.problem_files)}개')
        print(f'출력: {config.output_path}')
        print(f'예상 페이지: {expected_page_count(len(config.problem_files))}페이지')

        if not self.initialize():
            return (False, 0)

        try:
            target_hwp = self.target_client.hwp

            # 1. 양식 또는 새 문서 준비
            if config.use_template:
                print(f'\n[양식 열기] {config.template_path}')
                result = self.target_client.open_document(str(config.template_path))
                if not result.success:
                    print(f'❌ 양식 열기 실패: {result.error}')
                    return (False, 0)

                # v3에서 학습: 양식 파일은 레이아웃 유지 (A3 등)
                print('✅ 양식 준비 완료 (기존 레이아웃 유지)')
            else:
                # 새 문서 생성 (TODO: 구현 필요)
                print('❌ 새 문서 생성은 아직 미구현')
                return (False, 0)

            # 본문 시작 위치로 이동 (v3에서 학습)
            target_hwp.Run("MoveDocBegin")
            time.sleep(0.05)
            target_hwp.Run("MoveParaBegin")
            time.sleep(0.05)

            # 2. 각 문항 파일 처리
            print(f'\n[문항 삽입] 시작...')
            print('-' * 70)

            start_time = time.time()
            inserted = 0
            total_removed = 0
            failed = []

            for i, problem in enumerate(config.problem_files, 1):
                success, process_result = self.process_single_problem(
                    problem,
                    len(config.problem_files),
                    target_hwp  # test_merge_40_problems_clean.py 패턴
                )

                if success:
                    inserted += 1
                    total_removed += process_result.removed_count

                    # 7. BreakColumn (마지막 문항 제외)
                    if i < len(config.problem_files):
                        break_column(target_hwp)
                else:
                    failed.append((i, problem.name))

                # 10개마다 진행 상황
                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = avg_time * (len(config.problem_files) - i)
                    print(f'  --- 진행: {i}/{len(config.problem_files)} ({elapsed:.1f}초 경과, 예상 남은 시간: {remaining:.1f}초)')

            elapsed_total = time.time() - start_time

            print('-' * 70)
            print(f'✅ 문항 삽입 완료 (총 {elapsed_total:.1f}초)')

            # 3. 결과 저장
            print(f'\n[저장] 결과 저장 중...')
            config.output_path.parent.mkdir(parents=True, exist_ok=True)
            target_hwp.SaveAs(str(config.output_path.absolute()))
            time.sleep(0.5)

            if config.output_path.exists():
                file_size = config.output_path.stat().st_size
                print(f'✅ 저장 완료')
                print(f'   파일: {config.output_path}')
                print(f'   크기: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)')
            else:
                print(f'⚠️  저장 실패')
                return (False, 0)

            # 4. 최종 페이지 수
            page_count = target_hwp.PageCount

            # 결과 요약
            print('\n' + '=' * 70)
            print('결과 요약')
            print('=' * 70)
            print(f'문항 수: {len(config.problem_files)}개')
            print(f'삽입 성공: {inserted}개')
            print(f'삽입 실패: {len(failed)}개')
            print(f'제거된 빈 Para: {total_removed}개')
            print(f'최종 페이지: {page_count}개')
            print(f'소요 시간: {elapsed_total:.1f}초')
            print(f'문항당 평균: {elapsed_total / len(config.problem_files):.2f}초')
            print('=' * 70)

            # 검증
            expected = expected_page_count(len(config.problem_files))
            print(f'\n[검증]')
            print(f'예상 페이지: {expected}개')
            print(f'실제 페이지: {page_count}개')

            if validate_page_count(expected, page_count):
                print(f'✅ 페이지 수 검증 통과!')
            else:
                diff = abs(expected - page_count)
                print(f'⚠️  페이지 수 차이: {diff}페이지')

            if inserted == len(config.problem_files):
                print(f'✅ 모든 문항 삽입 성공!')
            else:
                print(f'⚠️  {len(config.problem_files) - inserted}개 문항 실패')

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
            if self.target_client:
                self.target_client.close_document()
            if self.source_client:
                self.source_client.cleanup()
            if self.target_client:
                self.target_client.cleanup()
            time.sleep(0.5)
            print('✅ 정리 완료')
