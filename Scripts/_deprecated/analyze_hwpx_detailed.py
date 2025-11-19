"""
HWPX XML 구조 상세 분석

실제 XML 요소를 확인하여 텍스트 추출 방식을 개선
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


def analyze_xml_structure(file_path: str):
    """XML 구조 상세 분석"""
    print(f"파일: {Path(file_path).name}\n")

    with zipfile.ZipFile(file_path, 'r') as zf:
        section_files = [f for f in zf.namelist() if 'section' in f.lower() and f.startswith('Contents/')]

        if not section_files:
            print("Section 파일을 찾을 수 없습니다.")
            return

        section_file = sorted(section_files)[0]
        print(f"분석 파일: {section_file}\n")

        xml_content = zf.read(section_file)
        root = ET.fromstring(xml_content)

        # 네임스페이스 정의
        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
            'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        print("=== XML 구조 샘플 (처음 10개 텍스트 요소) ===\n")

        # 모든 텍스트 요소 찾기
        text_elements = root.findall('.//hh:t', namespaces)
        print(f"총 <hh:t> 요소 수: {len(text_elements)}\n")

        # 처음 50개 요소 출력
        for i, elem in enumerate(text_elements[:50]):
            text = elem.text or ""
            parent = elem.getparent() if hasattr(elem, 'getparent') else None

            # 부모 태그 정보
            parent_info = ""
            if parent is not None:
                parent_tag = parent.tag.split('}')[-1] if '}' in parent.tag else parent.tag
                parent_info = f"[부모: {parent_tag}]"

            print(f"[{i+1:3d}] {parent_info:20s} {text[:100]}")

        print("\n=== 전체 텍스트 추출 및 문제 번호 찾기 ===\n")

        # 방법 1: 공백 포함하여 연결
        all_text_spaced = []
        for elem in text_elements:
            if elem.text:
                all_text_spaced.append(elem.text)

        full_text = ' '.join(all_text_spaced)
        print(f"전체 텍스트 길이: {len(full_text)} 문자")
        print(f"첫 1000자:\n{full_text[:1000]}\n")

        # 방법 2: Para 단위로 그룹화 (더 정확함)
        paras = root.findall('.//hh:p', namespaces)
        print(f"\n총 <hh:p> (문단) 수: {len(paras)}\n")

        para_texts = []
        for i, para in enumerate(paras[:20]):  # 처음 20개 문단
            texts = para.findall('.//hh:t', namespaces)
            para_text = ''.join(t.text for t in texts if t.text)
            para_texts.append(para_text)

            if para_text.strip():
                print(f"[Para {i+1:3d}] {para_text[:150]}")

        # 문제 번호 패턴 찾기
        print("\n=== 문제 번호 패턴 분석 ===\n")

        # 여러 패턴 시도
        patterns = [
            (r'\s(\d{1,3})\.\s+[가-힣①-➉]', '숫자. + (한글|선택지)'),
            (r'^\s*(\d{1,3})\.\s', '줄시작 숫자.'),
            (r'\s(\d{1,3})\)\s', '숫자)'),
            (r'\[(\d+)점\]', '[숫자점]'),
            (r'➀|➁|➂|➃|➄', '선택지 기호'),
        ]

        for pattern, name in patterns:
            if name == '선택지 기호':
                matches = re.findall(pattern, full_text)
                print(f"{name}: {len(matches)}개")
            else:
                matches = list(re.finditer(pattern, full_text, re.MULTILINE))
                if matches:
                    print(f"\n{name}: {len(matches)}개")
                    if matches and '점' not in name:
                        numbers = [int(m.group(1)) for m in matches[:30]]
                        print(f"  처음 30개: {numbers}")

                        # 연속성 체크
                        if len(numbers) >= 10:
                            gaps = [numbers[i+1] - numbers[i] for i in range(min(20, len(numbers)-1))]
                            print(f"  간격: {gaps[:20]}")


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(test_file).exists():
        print(f"파일이 존재하지 않습니다: {test_file}")
        sys.exit(1)

    analyze_xml_structure(test_file)
