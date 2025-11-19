"""
Types - Idris2 Types.idr 기반 Python 타입 정의

Idris2 명세: Specs/Separator/Separator/Types.idr
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple


# ============================================================================
# 기본 타입
# ============================================================================

@dataclass
class ProblemNumber:
    """문제 번호 (1부터 시작)"""
    value: int

    def __repr__(self):
        return f"Problem {self.value}"


@dataclass
class EndNoteNumber:
    """미주 번호 (1부터 시작)"""
    value: int

    def __repr__(self):
        return f"EndNote {self.value}"


@dataclass
class ElementPosition:
    """요소 위치 (인덱스)"""
    index: int
    xpath: Optional[str] = None

    def __repr__(self):
        return f"Pos({self.index})"


# ============================================================================
# 입력/출력 포맷
# ============================================================================

class InputFormat(Enum):
    """입력 파일 형식"""
    HWP = "hwp"
    HWPX = "hwpx"


class OutputFormat(Enum):
    """출력 파일 형식

    HWP가 기본값 (Idris2 증명: defaultOutputFormat = HwpFile)
    """
    MARKDOWN = "md"   # 텍스트 기반, 디버깅/검토용
    HWP = "hwp"       # Windows COM API (기본)
    HWPX = "hwpx"     # XML 기반


class ParaType(Enum):
    """문단 타입"""
    BODY = "body"
    ENDNOTE = "endNote"


# ============================================================================
# EndNote 정보
# ============================================================================

@dataclass
class EndNoteInfo:
    """미주 정보

    Idris2: record EndNoteInfo
    """
    number: EndNoteNumber
    position: ElementPosition
    suffix_char: str  # 미주 번호 뒤 문자 (보통 ".")
    inst_id: str  # HWPX instId
    para_count: int  # 미주 내 문단 수
    char_count: int  # 미주 내 글자 수

    def __repr__(self):
        return f"EndNote({self.number.value}, pos={self.position.index}, chars={self.char_count})"


# ============================================================================
# 문제 정보
# ============================================================================

@dataclass
class ProblemInfo:
    """문제 정보 (iter_note_blocks 패턴)

    Idris2: record ProblemInfo

    핵심 로직:
    - EndNote는 본문에 앵커를 가짐
    - 문제 i번 = EndNote[i-1] 앵커 ~ EndNote[i] 앵커
    - 첫 문제 = 문서 시작(0) ~ EndNote[0] 앵커

    Args:
        number: 문제 번호 (1부터 시작)
        start_position: 본문 시작 (이전 EndNote 앵커 or 문서 시작)
        end_position: 본문 끝 (현재 EndNote 앵커)
        endnote: 해당 해설 정보 (EndNote[i])
        body_para_count: 본문 문단 수
        total_char_count: 본문 글자 수
    """
    number: ProblemNumber
    start_position: ElementPosition  # 본문 시작 (이전 EndNote 앵커 or 0)
    end_position: ElementPosition    # 본문 끝 (현재 EndNote 앵커)
    endnote: EndNoteInfo             # 해당 해설 (EndNote[i])
    body_para_count: int             # 본문 문단 수
    total_char_count: int            # 본문 글자 수

    def __repr__(self):
        return f"Problem({self.number.value}, {self.start_position.index}~{self.end_position.index})"


# ============================================================================
# 그룹화
# ============================================================================

class GroupingStrategy:
    """그룹화 전략 기본 클래스"""
    pass


class OnePerFile(GroupingStrategy):
    """1문제 = 1파일"""
    def __repr__(self):
        return "OnePerFile"


@dataclass
class GroupByCount(GroupingStrategy):
    """N개씩 묶기"""
    count: int

    def __repr__(self):
        return f"GroupByCount({self.count})"


@dataclass
class GroupByRange(GroupingStrategy):
    """범위 지정 [(1,30), (31,60), ...]"""
    ranges: List[Tuple[int, int]]

    def __repr__(self):
        return f"GroupByRange({len(self.ranges)} ranges)"


@dataclass
class GroupInfo:
    """그룹 정보

    Idris2: record GroupInfo
    """
    group_num: int  # 그룹 번호 (1부터)
    start_problem: ProblemNumber
    end_problem: ProblemNumber
    problem_count: int

    def __repr__(self):
        return f"Group{self.group_num}({self.start_problem.value}-{self.end_problem.value}, {self.problem_count}문제)"


# ============================================================================
# 파일명 규칙
# ============================================================================

class NamingStrategy(Enum):
    """파일명 생성 전략

    Idris2: data NamingStrategy
    """
    DEFAULT = "default"  # "문제_001-030.hwp"
    CUSTOM = "custom"    # "커스텀접두사_1.hwp"


@dataclass
class NamingRule:
    """파일명 규칙

    Idris2: record NamingRule
    HWP First 원칙: 기본 확장자는 .hwp (Idris2 증명: defaultRuleUsesHwp)
    """
    name_prefix: str  # 기본 접두사: "문제"
    digit_count: int  # 제로 패딩 자릿수 (예: 3 → "001")
    file_extension: str  # 확장자 (기본: ".hwp")
    strategy: NamingStrategy = NamingStrategy.DEFAULT  # 파일명 전략
    custom_prefix: Optional[str] = None  # 커스텀 접두사 (strategy=CUSTOM일 때)

    def generate_filename(self, num: int) -> str:
        """단일 파일명 생성"""
        padded = str(num).zfill(self.digit_count)
        return f"{self.name_prefix}_{padded}{self.file_extension}"

    def generate_group_filename(self, group: GroupInfo) -> str:
        """그룹 파일명 생성

        Idris2: generateGroupFilename
        """
        start = group.start_problem.value
        end = group.end_problem.value

        if self.strategy == NamingStrategy.CUSTOM and self.custom_prefix:
            # 커스텀 전략: "2025 커팅_수학2_함수의극한_1.hwp"
            return f"{self.custom_prefix}_{group.group_num}{self.file_extension}"
        else:
            # 기본 전략: "문제_001-030.hwp"
            if start == end:
                # 1문제만: "문제_001.hwp"
                return self.generate_filename(start)
            else:
                # 여러 문제: "문제_001-030.hwp"
                start_padded = str(start).zfill(self.digit_count)
                end_padded = str(end).zfill(self.digit_count)
                return f"{self.name_prefix}_{start_padded}-{end_padded}{self.file_extension}"


# ============================================================================
# HWP ↔ HWPX 변환 설정
# ============================================================================

@dataclass
class ConversionConfig:
    """HWP → HWPX 변환 설정

    Idris2: record ConversionConfig
    """
    keep_original: bool  # 원본 HWP 파일 유지
    temp_dir: str  # 임시 디렉토리
    timeout: int  # 타임아웃 (초)


# ============================================================================
# Separator 설정
# ============================================================================

@dataclass
class SeparatorConfig:
    """Separator 전체 설정

    Idris2: record SeparatorConfig
    """
    input_path: str
    input_format: InputFormat
    output_dir: str
    naming_rule: NamingRule
    output_format: OutputFormat
    include_endnote: bool  # 미주 포함 여부
    grouping_strategy: GroupingStrategy
    conversion_config: Optional[ConversionConfig]
    verbose: bool
    # HWP 병렬 추출 설정 (HWP → HWP 전용)
    use_parallel: bool = False  # 병렬 처리 활성화
    max_workers: int = 5        # 최대 병렬 워커 수 (기본: 5)

    @staticmethod
    def default() -> 'SeparatorConfig':
        """기본 설정 (1문제 = 1파일)

        HWP First: 기본 출력은 .hwp
        """
        return SeparatorConfig(
            input_path="input.hwpx",
            input_format=InputFormat.HWPX,
            output_dir="output",
            naming_rule=NamingRule("문제", 3, ".hwp"),  # HWP First
            output_format=OutputFormat.HWP,  # HWP First
            include_endnote=True,
            grouping_strategy=OnePerFile(),
            conversion_config=None,
            verbose=False
        )

    @staticmethod
    def for_hwpx(input_path: str, output_dir: str) -> 'SeparatorConfig':
        """HWPX 입력용 설정

        HWP First: 기본 출력은 .hwp
        """
        return SeparatorConfig(
            input_path=input_path,
            input_format=InputFormat.HWPX,
            output_dir=output_dir,
            naming_rule=NamingRule("문제", 3, ".hwp"),  # HWP First
            output_format=OutputFormat.HWP,  # HWP First
            include_endnote=True,
            grouping_strategy=OnePerFile(),
            conversion_config=None,
            verbose=True
        )

    @staticmethod
    def grouped(input_path: str, output_dir: str, group_size: int) -> 'SeparatorConfig':
        """N개씩 묶는 설정

        HWP First: 기본 출력은 .hwp
        """
        return SeparatorConfig(
            input_path=input_path,
            input_format=InputFormat.HWPX,
            output_dir=output_dir,
            naming_rule=NamingRule("문제", 3, ".hwp"),  # HWP First
            output_format=OutputFormat.HWP,  # HWP First
            include_endnote=True,
            grouping_strategy=GroupByCount(group_size),
            conversion_config=None,
            verbose=True
        )


# ============================================================================
# 결과 타입
# ============================================================================

@dataclass
class WriteResult:
    """파일 쓰기 결과"""
    success: bool
    filepath: Optional[str]
    bytes_written: int
    error: Optional[str] = None


@dataclass
class BatchWriteResult:
    """일괄 저장 결과

    Idris2: record BatchWriteResult
    """
    total_problems: int
    success_count: int
    failed_count: int
    skipped_count: int
    output_files: List[str]

    def is_success(self) -> bool:
        return self.failed_count == 0 and self.success_count == self.total_problems
