"""
Problem Extractor - 문제 정보 추출 (iter_note_blocks 패턴)

Idris2 명세: Specs/Separator/Separator/Extractor.idr - extractProblemBlocks

핵심 로직:
- EndNote는 본문에 앵커를 가짐
- 문제 i번 = EndNote[i-1] 앵커 ~ EndNote[i] 앵커
- 첫 문제 = 문서 시작(0) ~ EndNote[0] 앵커
"""

from typing import List
from .types import EndNoteInfo, ProblemInfo, ProblemNumber, ElementPosition


class ProblemExtractor:
    """문제 정보 추출기 (iter_note_blocks 패턴)"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[ProblemExtractor] {message}")

    def extract(
        self,
        endnotes: List[EndNoteInfo],
        total_elements: int
    ) -> List[ProblemInfo]:
        """EndNote 목록에서 ProblemInfo 추출 (iter_note_blocks 패턴)

        알고리즘:
        1. 첫 문제: (문서 시작=0) ~ EndNote[0] 앵커
        2. 문제 i (i >= 2): EndNote[i-2] 앵커 ~ EndNote[i-1] 앵커

        Args:
            endnotes: 정렬된 EndNote 리스트 (408개)
            total_elements: 전체 XML 요소 개수 (사용 안 함)

        Returns:
            ProblemInfo 리스트 (408개)
        """
        self.log(f"문제 블록 추출 시작: {len(endnotes)}개 EndNote")

        if not endnotes:
            return []

        problems = []

        # 첫 문제: 문서 시작(0) ~ EndNote[0] 앵커
        first_problem = self._create_first_problem(endnotes[0])
        problems.append(first_problem)
        self.log(f"[1] 문서 시작(0) ~ EndNote[0].pos({endnotes[0].position.index})")

        # 나머지 문제들: EndNote[i-1] ~ EndNote[i]
        for i in range(1, len(endnotes)):
            prev_endnote = endnotes[i - 1]
            curr_endnote = endnotes[i]
            problem = self._create_problem(i + 1, prev_endnote, curr_endnote)
            problems.append(problem)
            self.log(f"[{i+1}] EndNote[{i-1}].pos({prev_endnote.position.index}) ~ EndNote[{i}].pos({curr_endnote.position.index})")

        self.log(f"문제 블록 추출 완료: {len(problems)}개")
        return problems

    def _create_first_problem(self, first_endnote: EndNoteInfo) -> ProblemInfo:
        """첫 번째 문제 생성

        범위: 문서 시작(0) ~ EndNote[0] 앵커
        """
        start_pos = ElementPosition(0, None)  # 문서 시작
        end_pos = first_endnote.position      # EndNote[0] 앵커

        element_count = end_pos.index - start_pos.index
        body_para_count = max(1, element_count // 10)

        return ProblemInfo(
            number=ProblemNumber(1),
            start_position=start_pos,
            end_position=end_pos,
            endnote=first_endnote,
            body_para_count=body_para_count,
            total_char_count=0  # TODO: 실제 텍스트에서 계산
        )

    def _create_problem(
        self,
        problem_num: int,
        prev_endnote: EndNoteInfo,
        curr_endnote: EndNoteInfo
    ) -> ProblemInfo:
        """일반 문제 생성

        범위: EndNote[i-1] 앵커 ~ EndNote[i] 앵커
        """
        start_pos = prev_endnote.position  # 이전 EndNote 앵커
        end_pos = curr_endnote.position    # 현재 EndNote 앵커

        element_count = end_pos.index - start_pos.index
        body_para_count = max(1, element_count // 10)

        return ProblemInfo(
            number=ProblemNumber(problem_num),
            start_position=start_pos,
            end_position=end_pos,
            endnote=curr_endnote,
            body_para_count=body_para_count,
            total_char_count=0  # TODO: 실제 텍스트에서 계산
        )
