"""
HWP → HWP Extractor - HWP 파일로 블록 추출

Idris2 명세: Specs/Extractor/ParallelExtraction.idr

핵심:
- HWP 파일에서 블록 추출 → HWP 파일로 저장
- 순차/병렬 처리 지원
- iter_note_blocks + Copy/Paste 방식
"""

from pathlib import Path
from typing import List, Tuple, Optional
from .types import (
    SeparatorConfig, BatchWriteResult, GroupingStrategy,
    GroupByCount, OnePerFile, GroupByRange
)
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.hwp_extractor import open_hwp, iter_note_blocks
from core.hwp_extractor_copypaste import extract_block_copypaste
from core.hwp_extractor_parallel import extract_blocks_parallel


class HwpHwpExtractor:
    """HWP → HWP 블록 추출기

    iter_note_blocks 패턴:
    - block 0: 첫 문항 이전 부분 (제외)
    - block 1+: 실제 문항들
    """

    def __init__(self, config: SeparatorConfig):
        self.config = config
        self.verbose = config.verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[HwpHwpExtractor] {message}")

    def extract(self) -> BatchWriteResult:
        """메인 워크플로우: HWP → HWP 블록 추출

        Returns:
            BatchWriteResult
        """
        self.log("=" * 60)
        self.log("HWP → HWP 블록 추출 시작")
        self.log("=" * 60)

        # 그룹화 전략 확인
        strategy = self.config.grouping_strategy

        if isinstance(strategy, OnePerFile):
            # 1문제 = 1파일 (blocks_per_group = 1)
            blocks_per_group = 1
        elif isinstance(strategy, GroupByCount):
            # N개씩 묶기
            blocks_per_group = strategy.count
        else:
            # GroupByRange는 병렬 처리 불가 (복잡한 로직 필요)
            self.log("ERROR: GroupByRange는 현재 지원하지 않습니다")
            return BatchWriteResult(0, 0, 0, 0, [])

        self.log(f"그룹화: {blocks_per_group}개씩 묶기")

        # 병렬/순차 선택
        if self.config.use_parallel and blocks_per_group > 0:
            self.log(f"병렬 처리 (최대 {self.config.max_workers}개 워커)")
            return self._extract_parallel(blocks_per_group)
        else:
            self.log("순차 처리")
            return self._extract_sequential(blocks_per_group)

    def _extract_parallel(self, blocks_per_group: int) -> BatchWriteResult:
        """병렬 추출 (core/hwp_extractor_parallel.py 사용)"""

        results = extract_blocks_parallel(
            hwp_file_path=self.config.input_path,
            output_dir=self.config.output_dir,
            blocks_per_group=blocks_per_group,
            max_workers=self.config.max_workers,
            verbose=self.verbose,
            naming_rule=self.config.naming_rule  # NamingRule 전달
        )

        # 결과 변환
        success_count = sum(1 for ok, _ in results if ok)
        failed_count = len(results) - success_count
        output_files = [str(p) for ok, p in results if ok and p]

        return BatchWriteResult(
            total_problems=len(results),
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=0,
            output_files=output_files
        )

    def _extract_sequential(self, blocks_per_group: int) -> BatchWriteResult:
        """순차 추출 (한 번에 한 그룹씩)"""

        self.log("1단계: 블록 위치 수집 중...")
        self.log(f"  파일: {Path(self.config.input_path).name}")
        self.log(f"  파일 열기 시도...")

        try:
            with open_hwp(self.config.input_path) as hwp:
                self.log(f"  파일 열기 성공!")
                self.log(f"  EndNote 블록 탐색 중 (시간이 걸릴 수 있습니다)...")
                all_blocks = list(iter_note_blocks(hwp))
                self.log(f"  블록 탐색 완료!")
        except Exception as e:
            self.log(f"  [ERROR] 파일 열기 실패: {e}")
            raise

        total_blocks = len(all_blocks)
        self.log(f"총 {total_blocks}개 블록 발견")

        # 블록 0 제외
        all_blocks = all_blocks[1:]
        actual_problems = len(all_blocks)
        self.log(f"블록 0 제외, 실제 문항: {actual_problems}개\n")

        # 그룹 분할
        groups = []
        for i in range(0, actual_problems, blocks_per_group):
            group = list(range(i, min(i + blocks_per_group, actual_problems)))
            groups.append(group)

        self.log(f"2단계: {len(groups)}개 그룹으로 분할")

        # 출력 디렉토리 생성
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 순차 추출
        self.log("\n3단계: 순차 추출 시작\n")

        results = []

        with open_hwp(self.config.input_path) as hwp:
            for group_idx, group in enumerate(groups, 1):
                # 그룹의 첫 블록 ~ 마지막 블록 병합
                try:
                    first_block = all_blocks[group[0]]
                    last_block = all_blocks[group[-1]]

                    if not first_block or not last_block:
                        self.log(f"[ERROR] 그룹 {group_idx}: 블록 정보 없음")
                        results.append((False, None))
                        continue

                    merged_block = (first_block[0], last_block[1])
                except IndexError as e:
                    self.log(f"[ERROR] 그룹 {group_idx}: 인덱스 오류 - {e}")
                    results.append((False, None))
                    continue
                except Exception as e:
                    self.log(f"[ERROR] 그룹 {group_idx}: 블록 병합 실패 - {e}")
                    results.append((False, None))
                    continue

                # 출력 파일명 (NamingRule 사용)
                from .types import GroupInfo, ProblemNumber
                group_info = GroupInfo(
                    group_num=group_idx + 1,
                    start_problem=ProblemNumber(group[0] + 1),
                    end_problem=ProblemNumber(group[-1] + 1),
                    problem_count=len(group)
                )
                filename = self.config.naming_rule.generate_group_filename(group_info)
                output_file = output_path / filename

                # Copy/Paste 추출
                success = extract_block_copypaste(
                    hwp, merged_block, str(output_file), self.verbose
                )

                if success and output_file.exists():
                    file_size = output_file.stat().st_size
                    self.log(f"[OK] 그룹 {group_idx}: {file_size:,} bytes")
                    results.append((True, output_file))
                else:
                    self.log(f"[FAIL] 그룹 {group_idx}: 실패")
                    results.append((False, None))

        # 결과 변환
        success_count = sum(1 for ok, _ in results if ok)
        failed_count = len(results) - success_count
        output_files = [str(p) for ok, p in results if ok and p]

        self.log("\n" + "=" * 60)
        self.log(f"완료: {success_count}/{len(results)} 그룹 성공")
        self.log("=" * 60)

        return BatchWriteResult(
            total_problems=len(results),
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=0,
            output_files=output_files
        )
