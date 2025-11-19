"""
File Writer - 파일 저장

Idris2 명세: Specs/Separator/Separator/FileWriter.idr
"""

from pathlib import Path
from typing import List, TYPE_CHECKING, Union
from .types import (
    GroupInfo, NamingRule, OutputFormat,
    WriteResult, BatchWriteResult, ProblemInfo
)

if TYPE_CHECKING:
    from .xml_parser import HwpxParser
    from .hwp_parser import HwpParser


class FileWriter:
    """파일 작성기"""

    def __init__(self, output_dir: str, verbose: bool = False):
        self.output_dir = Path(output_dir)
        self.verbose = verbose

    def log(self, message: str):
        if self.verbose:
            print(f"[FileWriter] {message}")

    def write_groups(
        self,
        groups: List[GroupInfo],
        problems: List[ProblemInfo],
        parser: Union['HwpxParser', 'HwpParser'],
        naming_rule: NamingRule,
        output_format: OutputFormat,
        include_endnote: bool = True
    ) -> BatchWriteResult:
        """그룹별 파일 저장

        Args:
            groups: 그룹 리스트
            parser: HWP 또는 HWPX 파서
            naming_rule: 파일명 규칙
            output_format: 출력 형식

        Returns:
            BatchWriteResult
        """
        self.log(f"파일 저장 시작: {len(groups)}개 그룹")

        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)

        output_files = []
        success_count = 0
        failed_count = 0

        # 문제 번호로 인덱싱
        problem_dict = {p.number.value: p for p in problems}

        for group in groups:
            filename = naming_rule.generate_group_filename(group)
            filepath = self.output_dir / filename

            # 그룹에 해당하는 문제들 찾기
            group_problems = [
                problem_dict[i]
                for i in range(group.start_problem.value, group.end_problem.value + 1)
                if i in problem_dict
            ]

            result = self._write_single_file(
                filepath, group, group_problems, parser, output_format, include_endnote
            )

            if result.success:
                success_count += 1
                output_files.append(str(filepath))
                self.log(f"[OK] {filename}")
            else:
                failed_count += 1
                self.log(f"[FAIL] {filename}: {result.error}")

        self.log(f"저장 완료: {success_count}개 성공, {failed_count}개 실패")

        return BatchWriteResult(
            total_problems=len(groups),
            success_count=success_count,
            failed_count=failed_count,
            skipped_count=0,
            output_files=output_files
        )

    def _write_single_file(
        self,
        filepath: Path,
        group: GroupInfo,
        group_problems: List[ProblemInfo],
        parser: 'HwpxParser',
        output_format: OutputFormat,
        include_endnote: bool
    ) -> WriteResult:
        """단일 파일 저장"""
        try:
            # 실제 문제 본문 추출
            content = self._generate_content(
                group, group_problems, parser, output_format, include_endnote
            )

            filepath.write_text(content, encoding='utf-8')

            return WriteResult(
                success=True,
                filepath=str(filepath),
                bytes_written=len(content.encode('utf-8'))
            )

        except Exception as e:
            return WriteResult(
                success=False,
                filepath=str(filepath),
                bytes_written=0,
                error=str(e)
            )

    def _generate_content(
        self,
        group: GroupInfo,
        group_problems: List[ProblemInfo],
        parser: 'HwpxParser',
        output_format: OutputFormat,
        include_endnote: bool
    ) -> str:
        """파일 내용 생성 (iter_note_blocks 패턴)

        문제 본문 추출:
        - startPosition ~ endPosition = 본문 범위
        - startPosition: 이전 EndNote 앵커 (첫 문제는 0)
        - endPosition: 현재 EndNote 앵커
        """
        texts = []

        for prob in group_problems:
            # 문제 헤더
            texts.append(f"\n{'='*60}\n")
            texts.append(f"문제 {prob.number.value}\n")
            texts.append(f"{'='*60}\n\n")

            # 본문 텍스트 추출 (startPosition ~ endPosition)
            problem_text = parser.get_text_between(
                prob.start_position.index,  # 본문 시작 (이전 EndNote 앵커 or 0)
                prob.end_position.index,    # 본문 끝 (현재 EndNote 앵커)
                include_endnote=False       # EndNote 태그는 제외 (본문만)
            )

            texts.append(problem_text)
            texts.append("\n\n")

        return ''.join(texts)
