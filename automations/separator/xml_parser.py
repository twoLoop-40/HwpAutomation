"""
XML Parser - HWPX 파일 파싱

Idris2 명세: Specs/Separator/Separator/XmlParser.idr
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple
from .types import (
    EndNoteInfo, EndNoteNumber, ElementPosition,
    InputFormat, ParaType
)


class HwpxParser:
    """HWPX 파서

    Idris2 ParseStep 구현:
    - OpenZip: ZIP 파일 열기
    - ReadSection: section0.xml 읽기
    - ParseXml: XML 파싱
    - FindEndNotes: EndNote 요소 찾기
    - SortByPosition: 위치순 정렬
    """

    def __init__(self, hwpx_path: str, verbose: bool = False):
        self.hwpx_path = Path(hwpx_path)
        self.verbose = verbose
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.endnotes: List[EndNoteInfo] = []

    def log(self, message: str):
        """로그 출력"""
        if self.verbose:
            print(f"[XmlParser] {message}")

    def parse(self) -> List[EndNoteInfo]:
        """전체 파싱 파이프라인

        Returns:
            정렬된 EndNote 리스트
        """
        self.log(f"파싱 시작: {self.hwpx_path}")

        # 1. OpenZip
        self.log("ZIP 파일 열기...")
        if not self._open_zip():
            raise FileNotFoundError(f"HWPX 파일을 찾을 수 없습니다: {self.hwpx_path}")

        # 2. ReadSection
        self.log("section0.xml 읽기...")
        xml_content = self._read_section()
        if not xml_content:
            raise ValueError("section0.xml을 읽을 수 없습니다")

        # 3. ParseXml
        self.log("XML 파싱...")
        self._parse_xml(xml_content)

        # 4. FindEndNotes
        self.log("EndNote 찾기...")
        self.endnotes = self._find_endnotes()

        # 5. SortByPosition
        self.log("위치순 정렬...")
        self.endnotes.sort(key=lambda e: e.position.index)

        self.log(f"파싱 완료: {len(self.endnotes)}개 EndNote 발견")
        return self.endnotes

    def _open_zip(self) -> bool:
        """ZIP 파일 열기 (Idris2: OpenZip)"""
        return self.hwpx_path.exists() and zipfile.is_zipfile(self.hwpx_path)

    def _read_section(self) -> Optional[str]:
        """section0.xml 읽기 (Idris2: ReadSection)"""
        try:
            with zipfile.ZipFile(self.hwpx_path, 'r') as zf:
                # Contents/section0.xml 읽기
                with zf.open('Contents/section0.xml') as f:
                    return f.read().decode('utf-8')
        except Exception as e:
            self.log(f"섹션 읽기 실패: {e}")
            return None

    def _parse_xml(self, xml_content: str):
        """XML 파싱 (Idris2: ParseXml)"""
        self.tree = ET.ElementTree(ET.fromstring(xml_content))
        self.root = self.tree.getroot()

    def _find_endnotes(self) -> List[EndNoteInfo]:
        """EndNote 요소 찾기 (Idris2: FindEndNotes)

        실제 HWPX 구조:
        <sec xmlns="http://www.hancom.co.kr/hwpml/2011/section">
          <p>...</p>
          <ctrl>
            <endNote number="1" suffixChar="46" instId="298702148">
              <p>[정답] ...</p>
            </endNote>
          </ctrl>
        </sec>
        """
        if not self.root:
            return []

        endnotes = []
        all_elements = list(self.root.iter())  # 모든 요소를 순회

        for idx, elem in enumerate(all_elements):
            # 네임스페이스 포함 태그 처리
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

            if tag_name == 'endNote':
                # EndNote 정보 추출
                number = int(elem.get('number', '0'))
                suffix_char_code = elem.get('suffixChar', '46')  # 46 = '.'
                suffix_char = chr(int(suffix_char_code)) if suffix_char_code.isdigit() else '.'
                inst_id = elem.get('instId', '')

                # EndNote 내부 문단 수 계산 (네임스페이스 처리)
                paras = [e for e in elem.iter() if e.tag.split('}')[-1] == 'p']
                para_count = len(paras)

                # 글자 수 및 [정답] 포함 여부 계산
                text_content = ''.join(elem.itertext())
                char_count = len(text_content.strip())
                has_answer = '[정답]' in text_content

                endnote_info = EndNoteInfo(
                    number=EndNoteNumber(number),
                    position=ElementPosition(idx, self._get_xpath(elem)),
                    suffix_char=suffix_char,
                    inst_id=inst_id,
                    para_count=para_count,
                    char_count=char_count
                )
                endnotes.append(endnote_info)

        return endnotes

    def _count_chars(self, elem: ET.Element) -> int:
        """요소 내 글자 수 계산"""
        text = ''.join(elem.itertext())
        return len(text.strip())

    def _get_xpath(self, elem: ET.Element) -> str:
        """요소의 XPath 생성 (간단 버전)"""
        return elem.tag

    def get_all_paragraphs(self) -> List[Tuple[int, ParaType]]:
        """모든 문단 정보 가져오기

        Returns:
            [(인덱스, 타입), ...] 리스트
        """
        if not self.root:
            return []

        paragraphs = []
        all_elements = list(self.root.iter())

        for idx, elem in enumerate(all_elements):
            if elem.tag == 'P':
                # 부모 확인: ENDNOTE 내부인지 아닌지
                parent = self._find_parent(elem, all_elements)
                if parent and parent.tag == 'ENDNOTE':
                    para_type = ParaType.ENDNOTE
                else:
                    para_type = ParaType.BODY

                paragraphs.append((idx, para_type))

        return paragraphs

    def _find_parent(self, elem: ET.Element, all_elems: List[ET.Element]) -> Optional[ET.Element]:
        """부모 요소 찾기 (간단 버전)"""
        # ElementTree는 부모 참조가 없으므로 순회로 찾음
        for parent in all_elems:
            if elem in list(parent):
                return parent
        return None

    def get_text_between(self, start_idx: int, end_idx: int, include_endnote: bool = True) -> str:
        """지정 범위의 텍스트 추출

        Args:
            start_idx: 시작 인덱스
            end_idx: 끝 인덱스
            include_endnote: EndNote 내용 포함 여부

        Returns:
            추출된 텍스트
        """
        if not self.root:
            return ""

        all_elements = list(self.root.iter())
        texts = []

        for idx in range(start_idx, min(end_idx, len(all_elements))):
            elem = all_elements[idx]
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

            # EndNote 스킵 여부 확인
            if not include_endnote and tag_name == 'endNote':
                continue

            # 't' 태그(텍스트 런)에서만 텍스트 추출
            if tag_name == 't' and elem.text:
                texts.append(elem.text)

        return ''.join(texts)

    def get_total_elements(self) -> int:
        """전체 요소 개수"""
        if not self.root:
            return 0
        return len(list(self.root.iter()))


def detect_format(file_path: str) -> InputFormat:
    """파일 형식 감지 (Idris2: detectFormat)

    Args:
        file_path: 파일 경로

    Returns:
        InputFormat.HWP 또는 InputFormat.HWPX
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == '.hwpx':
        return InputFormat.HWPX
    elif suffix == '.hwp':
        return InputFormat.HWP
    else:
        # 기본값: HWPX
        return InputFormat.HWPX
