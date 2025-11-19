"""
HWPX에서 미주(Endnote) 찾기

XML 구조에서 미주 영역을 찾아 개수 확인
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import re

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


def find_endnotes_in_hwpx(hwpx_path: str):
    """HWPX에서 미주 찾기"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        # 모든 파일 목록
        all_files = zf.namelist()
        print(f"=== HWPX 파일 구조 ===")
        print(f"총 파일 수: {len(all_files)}\n")

        # Contents 디렉토리 파일들
        content_files = [f for f in all_files if f.startswith('Contents/')]
        print(f"Contents 파일들:")
        for f in sorted(content_files):
            print(f"  - {f}")

        print(f"\n=== Section 파일 분석 ===\n")

        # section0.xml 파싱
        section_file = 'Contents/section0.xml'
        if section_file not in all_files:
            print("section0.xml을 찾을 수 없습니다.")
            return

        xml_content = zf.read(section_file)
        root = ET.fromstring(xml_content)

        # 네임스페이스
        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
            'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        # 미주 관련 요소 찾기
        print("1. 미주 관련 XML 태그 검색:\n")

        # 가능한 미주 태그들
        endnote_tags = [
            './/hh:endnote',
            './/hp:endnote',
            './/endnote',
            './/hh:en',
            './/hp:en',
            './/en',
        ]

        found_endnotes = []
        for tag in endnote_tags:
            try:
                elements = root.findall(tag, namespaces)
                if elements:
                    print(f"   {tag}: {len(elements)}개 발견!")
                    found_endnotes.extend(elements)
            except:
                pass

        if not found_endnotes:
            print("   미주 태그를 찾을 수 없습니다.\n")

        # 모든 태그 이름 수집
        print("\n2. XML의 모든 고유 태그 이름:\n")
        all_tags = set()

        def collect_tags(elem):
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            all_tags.add(tag_name)
            for child in elem:
                collect_tags(child)

        collect_tags(root)

        # note, foot, end 관련 태그 필터
        note_related = [t for t in sorted(all_tags) if 'note' in t.lower() or 'foot' in t.lower() or 'end' in t.lower()]
        if note_related:
            print(f"   주석/미주 관련 태그: {note_related}")
        else:
            print("   주석/미주 관련 태그 없음")

        # 전체 태그 통계
        print(f"\n   총 고유 태그 수: {len(all_tags)}개")
        if len(all_tags) < 50:
            print(f"   전체 태그: {sorted(all_tags)}")

        # 본문과 미주 영역 구분
        print("\n\n3. 본문 영역 분석:\n")

        # 섹션 내 서브섹션 찾기
        sections = root.findall('.//hh:section', namespaces)
        if not sections:
            sections = root.findall('.//section', namespaces)

        print(f"   Section 요소: {len(sections)}개")

        # 문단 분석
        paras = root.findall('.//hh:p', namespaces)
        print(f"   총 문단(<p>): {len(paras)}개\n")

        # 각 섹션별 텍스트 추출
        if sections:
            for i, section in enumerate(sections[:5]):  # 처음 5개만
                texts = section.findall('.//hh:t', namespaces)
                text_content = ''.join(t.text for t in texts if t.text)
                print(f"   Section {i}: {len(text_content)} 문자, 첫 100자: {text_content[:100]}")

        # 미주 번호 패턴 찾기 (텍스트 기반)
        print("\n\n4. 텍스트에서 미주 패턴 찾기:\n")

        text_elements = root.findall('.//hh:t', namespaces)
        full_text = ' '.join(t.text for t in text_elements if t.text)

        # 미주 번호는 보통 "1. 2. 3." 형태
        # 상위첨자로 표시될 수도 있음

        # 방법 1: 연속된 "숫자." 패턴 찾기
        # 문제 본문에는 선택지(➀➁➂➃➄)가 있고
        # 미주 영역에는 "1. 2. 3. ..." 형태

        # [정답] 이후의 패턴 분석
        answer_pattern = r'\[정답\]\s*[➀-➄]'
        answer_matches = list(re.finditer(answer_pattern, full_text))

        print(f"   [정답] 패턴: {len(answer_matches)}개")

        # 마지막 [정답] 이후 영역이 미주일 가능성
        if answer_matches:
            last_answer_pos = answer_matches[-1].end()
            after_last_answer = full_text[last_answer_pos:]

            print(f"   마지막 [정답] 이후 텍스트 길이: {len(after_last_answer)} 문자")
            print(f"   마지막 [정답] 이후 샘플:\n   {after_last_answer[:300]}\n")

            # 이 영역에서 "숫자." 패턴 찾기
            number_pattern = r'(\d{1,3})\.\s+'
            numbers_in_endnote = list(re.finditer(number_pattern, after_last_answer))

            if numbers_in_endnote:
                nums = [int(m.group(1)) for m in numbers_in_endnote[:20]]
                print(f"   미주 영역 추정 번호 패턴: {nums}")
                print(f"   총 개수: {len(numbers_in_endnote)}개")

        # 전체 텍스트에서 선택지 vs 일반 숫자 비율
        choice_count = len(re.findall(r'[➀-➄]', full_text))
        print(f"\n   선택지 기호(➀-➄): {choice_count}개")
        print(f"   추정 문제 수: {choice_count // 5}개")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    find_endnotes_in_hwpx(hwpx_file)
