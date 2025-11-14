"""
AppV1 데이터 타입 정의

Idris2 명세 (HwpIdris/AppV1/MergeProblemFiles.idr) 기반
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional


@dataclass
class ProblemFile:
    """문항 파일 정보"""
    path: Path
    name: str
    index: int


@dataclass
class ParaInfo:
    """Para 정보"""
    para_num: int
    start_pos: Tuple[int, int, int]  # (list, para, pos)
    end_pos: Tuple[int, int, int]
    is_empty: bool


@dataclass
class ProcessResult:
    """문항 처리 결과"""
    success: bool
    para_count: int
    empty_para_count: int
    removed_count: int


@dataclass
class MergeConfig:
    """합병 설정"""
    template_path: Optional[Path]
    problem_files: List[ProblemFile]
    output_path: Path
    use_template: bool  # True: 양식 사용, False: 새 문서 생성


def expected_page_count(problem_count: int) -> int:
    """
    예상 페이지 수 계산

    2단 레이아웃: 2개 문항당 1페이지
    올림 계산
    """
    if problem_count == 0:
        return 0
    # 올림: (n + 1) // 2
    return (problem_count + 1) // 2


def validate_page_count(expected: int, actual: int) -> bool:
    """
    페이지 수 검증

    ±2 페이지 이내면 성공으로 간주
    """
    diff = abs(expected - actual)
    return diff <= 2
