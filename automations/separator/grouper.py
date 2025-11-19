"""
Grouper - 문제 그룹화

Idris2 명세: Specs/Separator/Separator/Extractor.idr - groupProblems
"""

from typing import List, Tuple
from .types import (
    ProblemInfo, GroupInfo, GroupingStrategy,
    OnePerFile, GroupByCount, GroupByRange
)


class ProblemGrouper:
    """문제 그룹화"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[ProblemGrouper] {message}")

    def group(
        self,
        strategy: GroupingStrategy,
        problems: List[ProblemInfo]
    ) -> List[GroupInfo]:
        """그룹화 전략에 따라 문제 그룹화

        Args:
            strategy: 그룹화 전략
            problems: 전체 문제 리스트

        Returns:
            GroupInfo 리스트
        """
        self.log(f"그룹화 시작: {strategy}")

        if isinstance(strategy, OnePerFile):
            return self._one_per_file(problems)
        elif isinstance(strategy, GroupByCount):
            return self._by_count(strategy.count, problems)
        elif isinstance(strategy, GroupByRange):
            return self._by_range(strategy.ranges, problems)
        else:
            raise ValueError(f"알 수 없는 그룹화 전략: {strategy}")

    def _one_per_file(self, problems: List[ProblemInfo]) -> List[GroupInfo]:
        """1문제 = 1파일 (Idris2: OnePerFile)"""
        groups = []
        for i, prob in enumerate(problems, 1):
            group = GroupInfo(
                group_num=i,
                start_problem=prob.number,
                end_problem=prob.number,
                problem_count=1
            )
            groups.append(group)

        self.log(f"1문제 = 1파일: {len(groups)}개 그룹")
        return groups

    def _by_count(self, count: int, problems: List[ProblemInfo]) -> List[GroupInfo]:
        """N개씩 묶기 (Idris2: GroupByCount)

        예: count=30, 408문제
        → 14그룹 (13×30 + 1×18)
        """
        groups = []
        group_num = 1

        for i in range(0, len(problems), count):
            chunk = problems[i:i + count]
            if not chunk:
                break

            group = GroupInfo(
                group_num=group_num,
                start_problem=chunk[0].number,
                end_problem=chunk[-1].number,
                problem_count=len(chunk)
            )
            groups.append(group)
            group_num += 1

        self.log(f"{count}개씩 묶기: {len(groups)}개 그룹 생성")
        return groups

    def _by_range(
        self,
        ranges: List[Tuple[int, int]],
        problems: List[ProblemInfo]
    ) -> List[GroupInfo]:
        """범위 지정 (Idris2: GroupByRange)

        예: [(1,30), (31,60), ...]
        """
        groups = []
        group_num = 1

        for start, end in ranges:
            filtered = [
                p for p in problems
                if start <= p.number.value <= end
            ]

            if not filtered:
                continue

            group = GroupInfo(
                group_num=group_num,
                start_problem=filtered[0].number,
                end_problem=filtered[-1].number,
                problem_count=len(filtered)
            )
            groups.append(group)
            group_num += 1

        self.log(f"범위 지정: {len(groups)}개 그룹 생성")
        return groups
