"""
Separator - 메인 워크플로우

Idris2 명세: Specs/Separator/Separator/Workflow.idr
"""

from pathlib import Path
from .types import SeparatorConfig, BatchWriteResult, InputFormat, OutputFormat
from .xml_parser import HwpxParser
from .hwp_parser import HwpParser
from .problem_extractor import ProblemExtractor
from .grouper import ProblemGrouper
from .file_writer import FileWriter
from .hwp_hwp_extractor import HwpHwpExtractor


class Separator:
    """HWP/HWPX 문제 분리기

    Idris2 WorkflowStage 구현:
    - Input: 입력 파일 처리
    - Parse: HWP/HWPX 파싱
    - Extract: 문제 추출
    - Write: 파일 저장
    - Complete: 완료
    """

    def __init__(self, config: SeparatorConfig):
        self.config = config
        self.verbose = config.verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[Separator] {message}")

    def run(self) -> BatchWriteResult:
        """전체 워크플로우 실행

        Returns:
            BatchWriteResult
        """
        self.log("=" * 60)
        self.log("Separator 시작")
        self.log("=" * 60)

        file_ext = Path(self.config.input_path).suffix.lower()

        # HWP → HWP 특수 경로 (병렬/순차 추출)
        if file_ext == '.hwp' and self.config.output_format == OutputFormat.HWPX:
            # HWPX 출력이지만 실제로는 HWP로 저장됨 (naming_rule 확인)
            # TODO: OutputFormat.HWP 추가 필요
            self.log("HWP → HWP 블록 추출 모드")
            extractor = HwpHwpExtractor(self.config)
            return extractor.extract()

        # 기존 워크플로우: TEXT 추출
        # 1. Input + Parse: 파일 형식에 따라 파서 선택
        self.log(f"\n[1/4] 파싱 중: {self.config.input_path}")

        if file_ext == '.hwp':
            self.log("HWP 파일 감지 - COM API 사용")
            parser = HwpParser(self.config.input_path, self.verbose)
        elif file_ext == '.hwpx':
            self.log("HWPX 파일 감지 - XML 파싱 사용")
            parser = HwpxParser(self.config.input_path, self.verbose)
        else:
            self.log(f"ERROR: 지원하지 않는 파일 형식: {file_ext}")
            return BatchWriteResult(0, 0, 0, 0, [])

        endnotes = parser.parse()

        if not endnotes:
            self.log("ERROR: EndNote를 찾을 수 없습니다")
            return BatchWriteResult(0, 0, 0, 0, [])

        total_elements = parser.get_total_elements()

        # 2. Extract: 문제 추출
        self.log(f"\n[2/4] 문제 추출 중...")
        extractor = ProblemExtractor(self.verbose)
        problems = extractor.extract(endnotes, total_elements)

        # 3. Extract: 그룹화
        self.log(f"\n[3/4] 그룹화 중: {self.config.grouping_strategy}")
        grouper = ProblemGrouper(self.verbose)
        groups = grouper.group(self.config.grouping_strategy, problems)

        # 4. Write: 파일 저장
        self.log(f"\n[4/4] 파일 저장 중: {self.config.output_dir}")
        writer = FileWriter(self.config.output_dir, self.verbose)
        result = writer.write_groups(
            groups,
            problems,
            parser,
            self.config.naming_rule,
            self.config.output_format,
            self.config.include_endnote
        )

        # Complete
        self.log("\n" + "=" * 60)
        if result.is_success():
            self.log(f"[SUCCESS] 완료: {result.success_count}개 파일 생성")
        else:
            self.log(f"[WARNING] 완료: {result.success_count}개 성공, {result.failed_count}개 실패")
        self.log("=" * 60)

        return result


def separate_problems(config: SeparatorConfig) -> BatchWriteResult:
    """단일 함수 인터페이스"""
    separator = Separator(config)
    return separator.run()
