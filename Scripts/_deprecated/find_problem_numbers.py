"""
문제 번호 패턴 정확히 찾기

선택지 기호(➀➁➂➃➄)를 기준으로 문제 구간을 나누고,
각 문제의 시작점을 찾는다.
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


def find_problems(file_path: str):
    """문제 번호 찾기"""
    print(f"파일: {Path(file_path).name}\n")

    with zipfile.ZipFile(file_path, 'r') as zf:
        section_files = [f for f in zf.namelist() if 'section' in f.lower() and f.startswith('Contents/')]
        xml_content = zf.read(sorted(section_files)[0])
        root = ET.fromstring(xml_content)

        namespaces = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
        text_elements = root.findall('.//hh:t', namespaces)

        # 전체 텍스트 추출
        full_text = ' '.join(t.text for t in text_elements if t.text)

        print(f"전체 텍스트 길이: {len(full_text):,} 문자\n")

        # 방법 1: 선택지 기호로 문제 위치 추정
        choice_pattern = r'➀|➁|➂|➃|➄'
        choice_matches = list(re.finditer(choice_pattern, full_text))

        print(f"=== 선택지 기호 분석 ===")
        print(f"총 선택지 기호: {len(choice_matches)}개\n")

        # 5개 단위로 그룹화 (문제당 5개 선택지)
        problem_count = len(choice_matches) // 5
        print(f"추정 문제 수: {problem_count}개 (선택지 5개 기준)\n")

        # 각 문제 시작 부분 출력
        print("=== 문제 시작 부분 샘플 (처음 20개) ===\n")

        for i in range(min(20, problem_count)):
            choice_pos = choice_matches[i * 5].start()  # i번째 문제의 첫 선택지 위치

            # 선택지 이전 200자를 가져와서 문제 텍스트 추정
            start = max(0, choice_pos - 200)
            end = choice_pos + 100
            context = full_text[start:end]

            # 줄바꿈 정리
            context = context.replace('\n', ' ').strip()

            print(f"[문제 {i+1:3d}] ...{context[-150:]}")

        # 방법 2: [정답] 패턴 찾기
        print("\n\n=== [정답] 패턴 분석 ===\n")
        answer_pattern = r'\[정답\]\s*[➀-➄]'
        answer_matches = list(re.finditer(answer_pattern, full_text))

        print(f"총 [정답] 발견: {len(answer_matches)}개\n")

        if len(answer_matches) >= 10:
            print("처음 10개 [정답] 위치:\n")
            for i, match in enumerate(answer_matches[:10]):
                pos = match.start()
                context = full_text[max(0, pos-50):pos+80]
                context = context.replace('\n', ' ')
                print(f"[{i+1:3d}] ...{context}")

        # 방법 3: [정답] 간격으로 문제 나누기
        print(f"\n\n=== 문제 구간 분석 (정답 기준) ===\n")

        if len(answer_matches) >= 2:
            # 각 정답 사이 간격 계산
            gaps = []
            for i in range(len(answer_matches) - 1):
                gap = answer_matches[i+1].start() - answer_matches[i].start()
                gaps.append(gap)

            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            print(f"평균 문제 길이: {avg_gap:.0f} 문자")
            print(f"최소: {min(gaps)} 문자")
            print(f"최대: {max(gaps)} 문자\n")

            # 각 정답 이후 텍스트가 다음 문제인지 확인
            print("각 정답 직후 텍스트 (다음 문제 시작):\n")
            for i in range(min(10, len(answer_matches) - 1)):
                after_answer = answer_matches[i].end()
                next_answer = answer_matches[i+1].start()

                # 정답 직후 150자
                next_problem_text = full_text[after_answer:after_answer+150]
                next_problem_text = next_problem_text.strip().replace('\n', ' ')

                print(f"[문제 {i+2:3d}] {next_problem_text}")

        # 방법 4: 숫자로 시작하는 패턴 찾기 (단, 수식 제외)
        print("\n\n=== 문제 번호 후보 찾기 ===\n")

        # "[정답] ➄" 다음에 나오는 숫자 찾기
        problem_num_pattern = r'\[정답\]\s*[➀-➄]\s*(.{0,50}?)(\d+)\.'

        num_matches = list(re.finditer(problem_num_pattern, full_text))
        if num_matches:
            print(f"정답 후 숫자 패턴: {len(num_matches)}개\n")
            for i, match in enumerate(num_matches[:20]):
                print(f"[{i+1:3d}] 번호={match.group(2)} | 컨텍스트: {match.group(1)}{match.group(2)}.")


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwpx"

    if not Path(test_file).exists():
        print(f"파일이 존재하지 않습니다: {test_file}")
        sys.exit(1)

    find_problems(test_file)
