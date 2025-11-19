"""
HWPX 파일 분석

HWPX는 ZIP + XML 형식이므로 직접 파싱 가능
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


def analyze_hwpx(file_path: str):
    """HWPX 파일 분석"""
    print(f"파일: {Path(file_path).name}\n")

    try:
        # HWPX는 ZIP 파일
        with zipfile.ZipFile(file_path, 'r') as zf:
            print("=== HWPX 구조 ===")
            file_list = zf.namelist()
            print(f"총 {len(file_list)}개 파일")

            # Contents 폴더의 XML 파일들
            content_files = [f for f in file_list if f.startswith('Contents/')]
            print(f"Contents 파일: {len(content_files)}개")

            # 섹션 파일들 (section*.xml)
            section_files = [f for f in content_files if 'section' in f.lower()]
            print(f"Section 파일: {len(section_files)}개\n")

            # 모든 텍스트 추출
            all_text = []

            for section_file in sorted(section_files):
                print(f"읽기: {section_file}")

                try:
                    xml_content = zf.read(section_file)
                    root = ET.fromstring(xml_content)

                    # 모든 텍스트 노드 찾기
                    # HWPX에서 텍스트는 <hh:t> 태그에 있음
                    namespace = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

                    text_elements = root.findall('.//hh:t', namespace)
                    section_text = []

                    for elem in text_elements:
                        if elem.text:
                            section_text.append(elem.text)

                    text = ''.join(section_text)
                    all_text.append(text)

                    print(f"  → {len(text)} 문자")

                except Exception as e:
                    print(f"  → 에러: {e}")

            # 전체 텍스트 합치기
            full_text = '\n'.join(all_text)
            print(f"\n=== 전체 텍스트 ===")
            print(f"총 {len(full_text)} 문자")
            print(f"첫 500자:\n{full_text[:500]}\n")

            # 문제 패턴 찾기
            print("=== 문제 패턴 분석 ===")

            # 더 유연한 패턴: 공백 또는 줄바꿈 후 숫자.
            patterns = [
                (r'(?:^|\s)(\d+)\.\s+[가-힣]', '공백+숫자.+한글'),  # " 1. 가" 형태
                (r'(?:^|\s)(\d{1,3})\.\s', '숫자.'),  # 1~3자리 숫자
                (r'\[(\d+)점\]', '[숫자점]'),  # [3점] 형태
            ]

            for pattern, name in patterns:
                matches = list(re.finditer(pattern, full_text, re.MULTILINE))
                if matches:
                    print(f"\n{name} 패턴: {len(matches)}개 발견")
                    numbers = [int(m.group(1)) for m in matches[:20]]
                    print(f"  처음 20개 번호: {numbers}")

                    # 연속성 확인
                    if len(matches) >= 10:
                        first_10 = [int(m.group(1)) for m in matches[:10]]
                        is_sequential = all(first_10[i] == i+1 for i in range(len(first_10)))
                        print(f"  연속성: {'✓ 1부터 순차적' if is_sequential else '✗ 비연속적'}")

            # 샘플 텍스트 출력 (문제 구조 파악)
            print(f"\n=== 샘플 텍스트 (1000~2000자) ===")
            print(full_text[1000:2000])

            return full_text

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(test_file).exists():
        print(f"파일이 존재하지 않습니다: {test_file}")
        sys.exit(1)

    text = analyze_hwpx(test_file)

    if text:
        print(f"\n✓ 분석 성공! ({len(text)} 문자)")
    else:
        print(f"\n✗ 분석 실패")
