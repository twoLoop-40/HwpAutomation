"""
HWPX에서 문제 추출

144개 문제를 [정답] 패턴 기준으로 분리하여
개별 텍스트로 추출
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
import re
from typing import List, Tuple
from dataclasses import dataclass

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


@dataclass
class Problem:
    """문제 데이터"""
    number: int
    text: str
    start_pos: int
    end_pos: int
    char_count: int


def extract_full_text(hwpx_path: str) -> str:
    """HWPX에서 전체 텍스트 추출"""
    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        section_files = [
            f for f in zf.namelist()
            if 'section' in f.lower() and f.startswith('Contents/')
        ]

        if not section_files:
            raise ValueError("Section 파일을 찾을 수 없습니다.")

        xml_content = zf.read(sorted(section_files)[0])
        root = ET.fromstring(xml_content)

        namespaces = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
        text_elements = root.findall('.//hh:t', namespaces)

        # 공백으로 연결
        full_text = ' '.join(t.text for t in text_elements if t.text)

        return full_text


def find_answer_positions(text: str) -> List[Tuple[int, int]]:
    """[정답] 위치 찾기

    Returns:
        List of (start, end) positions
    """
    pattern = r'\[정답\]\s*[➀-➄]'
    matches = list(re.finditer(pattern, text))

    return [(m.start(), m.end()) for m in matches]


def split_problems(text: str, answer_positions: List[Tuple[int, int]]) -> List[Problem]:
    """[정답] 기준으로 문제 분리

    전략:
    - 첫 번째 [정답] 이전은 문제 설명 또는 첫 문제 일부로 간주
    - 각 [정답] ~ 다음 [정답] 사이가 하나의 문제
    - 마지막 [정답] 이후는 마지막 문제

    Returns:
        List of Problem objects
    """
    if not answer_positions:
        return []

    problems = []

    # 첫 번째 [정답]이 매우 앞쪽에 있다면 문제 1의 정답부터 시작
    # 그렇지 않으면 처음~첫 정답이 문제 1
    first_answer_start = answer_positions[0][0]

    if first_answer_start > 100:  # 첫 정답 앞에 충분한 내용이 있음
        # 처음 ~ 첫 정답 = 문제 1
        problem_text = text[:answer_positions[0][1]].strip()
        problems.append(Problem(
            number=1,
            text=problem_text,
            start_pos=0,
            end_pos=answer_positions[0][1],
            char_count=len(problem_text)
        ))

        # 나머지 문제들
        for i in range(len(answer_positions) - 1):
            start = answer_positions[i][1]
            end = answer_positions[i + 1][1]
            problem_text = text[start:end].strip()

            problems.append(Problem(
                number=i + 2,
                text=problem_text,
                start_pos=start,
                end_pos=end,
                char_count=len(problem_text)
            ))

        # 마지막 문제
        last_start = answer_positions[-1][1]
        last_text = text[last_start:].strip()
        problems.append(Problem(
            number=len(answer_positions) + 1,
            text=last_text,
            start_pos=last_start,
            end_pos=len(text),
            char_count=len(last_text)
        ))

    else:
        # 첫 정답부터가 문제 1
        for i in range(len(answer_positions) - 1):
            start = answer_positions[i][0]  # [정답]부터 포함
            end = answer_positions[i + 1][0]  # 다음 [정답] 직전까지
            problem_text = text[start:end].strip()

            problems.append(Problem(
                number=i + 1,
                text=problem_text,
                start_pos=start,
                end_pos=end,
                char_count=len(problem_text)
            ))

        # 마지막 문제
        last_start = answer_positions[-1][0]
        last_text = text[last_start:].strip()
        problems.append(Problem(
            number=len(answer_positions),
            text=last_text,
            start_pos=last_start,
            end_pos=len(text),
            char_count=len(last_text)
        ))

    return problems


def extract_problems(hwpx_path: str) -> List[Problem]:
    """HWPX에서 문제 추출 (메인 함수)"""
    print(f"파일: {Path(hwpx_path).name}\n")

    # 1. 전체 텍스트 추출
    print("1. 텍스트 추출 중...")
    full_text = extract_full_text(hwpx_path)
    print(f"   → {len(full_text):,} 문자 추출\n")

    # 2. [정답] 위치 찾기
    print("2. [정답] 패턴 찾기...")
    answer_positions = find_answer_positions(full_text)
    print(f"   → {len(answer_positions)}개 발견\n")

    # 3. 문제 분리
    print("3. 문제 분리 중...")
    problems = split_problems(full_text, answer_positions)
    print(f"   → {len(problems)}개 문제 추출\n")

    return problems


def save_problems_as_text(problems: List[Problem], output_dir: Path):
    """문제들을 텍스트 파일로 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"4. 텍스트 파일 저장 중: {output_dir}\n")

    for problem in problems:
        filename = f"문제_{problem.number:03d}.txt"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(problem.text)

        print(f"   [{problem.number:3d}] {filename:20s} ({problem.char_count:5d} 문자)")

    print(f"\n✓ 총 {len(problems)}개 파일 저장 완료")


def print_problem_stats(problems: List[Problem]):
    """문제 통계 출력"""
    print("\n=== 문제 통계 ===\n")

    char_counts = [p.char_count for p in problems]
    avg_chars = sum(char_counts) / len(char_counts) if char_counts else 0

    print(f"총 문제 수: {len(problems)}개")
    print(f"평균 길이: {avg_chars:.0f} 문자")
    print(f"최소 길이: {min(char_counts)} 문자 (문제 {char_counts.index(min(char_counts)) + 1})")
    print(f"최대 길이: {max(char_counts)} 문자 (문제 {char_counts.index(max(char_counts)) + 1})")

    # 길이 분포
    short = sum(1 for c in char_counts if c < 300)
    medium = sum(1 for c in char_counts if 300 <= c < 1000)
    long_prob = sum(1 for c in char_counts if c >= 1000)

    print(f"\n길이 분포:")
    print(f"  짧음 (<300자):    {short:3d}개")
    print(f"  보통 (300-1000자): {medium:3d}개")
    print(f"  긺 (>1000자):     {long_prob:3d}개")

    # 처음 5개 미리보기
    print(f"\n=== 처음 5개 문제 미리보기 ===\n")
    for p in problems[:5]:
        preview = p.text[:100].replace('\n', ' ')
        print(f"[문제 {p.number:3d}] {preview}...")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"
    output_directory = Path("Tests/seperation/extracted")

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    # 문제 추출
    problems = extract_problems(hwpx_file)

    # 통계 출력
    print_problem_stats(problems)

    # 텍스트 파일로 저장
    save_problems_as_text(problems, output_directory)
