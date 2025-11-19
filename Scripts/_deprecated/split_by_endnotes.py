"""
미주 기준으로 문제 분리

미주 N ~ 미주 N+1 사이 = 문제 N
마지막 미주 ~ 파일 끝 = 마지막 문제
"""

import sys
import codecs
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())


@dataclass
class ProblemSection:
    """문제 섹션 정보"""
    number: int
    endnote_element: ET.Element
    endnote_text: str
    body_paras: List[ET.Element]  # 본문 문단들
    char_count: int


def split_by_endnotes(hwpx_path: str) -> List[ProblemSection]:
    """미주 기준으로 문제 분리"""
    print(f"파일: {Path(hwpx_path).name}\n")

    with zipfile.ZipFile(hwpx_path, 'r') as zf:
        xml_content = zf.read('Contents/section0.xml')
        root = ET.fromstring(xml_content)

        namespaces = {
            'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
        }

        print("=== 미주 기준 문제 분리 ===\n")

        # 1. 모든 endNote 찾기
        endnotes = root.findall('.//hh:endNote', namespaces)
        if not endnotes:
            endnotes = root.findall('.//endNote')

        print(f"총 미주(endNote): {len(endnotes)}개\n")

        # 2. 전체 요소 순서대로 순회하면서 미주 위치 파악
        # XML 트리를 순회하면서 각 요소의 위치(인덱스) 저장
        all_elements = list(root.iter())

        # 미주의 위치(인덱스) 저장
        endnote_positions = []
        for en in endnotes:
            try:
                pos = all_elements.index(en)
                endnote_positions.append((pos, en))
            except ValueError:
                continue

        # 위치 순서대로 정렬
        endnote_positions.sort(key=lambda x: x[0])

        print(f"미주 위치 확인: {len(endnote_positions)}개\n")

        # 3. 각 미주 사이의 문단들 추출
        problems = []

        for i, (pos, endnote) in enumerate(endnote_positions):
            problem_num = i + 1

            # 미주 내용
            en_texts = endnote.findall('.//hh:t', namespaces)
            if not en_texts:
                en_texts = endnote.findall('.//t')
            endnote_text = ''.join(t.text for t in en_texts if t.text)

            # 현재 미주부터 다음 미주 전까지의 요소들
            if i < len(endnote_positions) - 1:
                next_pos = endnote_positions[i + 1][0]
            else:
                next_pos = len(all_elements)  # 마지막 문제는 파일 끝까지

            # 이 구간의 문단들 (<p> 태그)
            section_paras = []
            for elem_idx in range(pos, next_pos):
                elem = all_elements[elem_idx]
                tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

                if tag_name == 'p':
                    # 미주 내부 문단은 제외
                    # (endnote의 자손인지 확인)
                    is_inside_endnote = False
                    for ancestor_idx in range(elem_idx, -1, -1):
                        ancestor = all_elements[ancestor_idx]
                        if ancestor == elem:
                            continue
                        ancestor_tag = ancestor.tag.split('}')[-1] if '}' in ancestor.tag else ancestor.tag
                        if ancestor_tag == 'endNote':
                            is_inside_endnote = True
                            break
                        # 범위를 벗어나면 중단
                        if ancestor_idx < pos:
                            break

                    if not is_inside_endnote:
                        section_paras.append(elem)

            # 본문 텍스트 추출
            body_text_parts = []
            for para in section_paras:
                texts = para.findall('.//hh:t', namespaces)
                if not texts:
                    texts = para.findall('.//t')
                para_text = ''.join(t.text for t in texts if t.text)
                body_text_parts.append(para_text)

            total_body_text = ' '.join(body_text_parts)
            total_chars = len(endnote_text) + len(total_body_text)

            problem = ProblemSection(
                number=problem_num,
                endnote_element=endnote,
                endnote_text=endnote_text,
                body_paras=section_paras,
                char_count=total_chars
            )

            problems.append(problem)

            # 진행 상황 출력 (처음 20개만)
            if i < 20:
                print(f"[문제 {problem_num:3d}] 미주: {len(endnote_text):4d}자, 본문: {len(total_body_text):5d}자 | {endnote_text[:60]}")

        if len(problems) > 20:
            print(f"... 외 {len(problems) - 20}개\n")

        print(f"\n✓ 총 {len(problems)}개 문제 분리 완료\n")

        return problems


def print_statistics(problems: List[ProblemSection]):
    """통계 출력"""
    print("=== 통계 ===\n")

    total = len(problems)
    char_counts = [p.char_count for p in problems]
    avg_chars = sum(char_counts) / total if total > 0 else 0

    print(f"총 문제 수: {total}개")
    print(f"평균 길이: {avg_chars:.0f} 문자")
    print(f"최소 길이: {min(char_counts)} 문자 (문제 {char_counts.index(min(char_counts)) + 1})")
    print(f"최대 길이: {max(char_counts)} 문자 (문제 {char_counts.index(max(char_counts)) + 1})")

    # [정답] 포함 개수
    with_answer = sum(1 for p in problems if '[정답]' in p.endnote_text)
    print(f"\n[정답] 포함: {with_answer}개 ({with_answer/total*100:.1f}%)")


def save_problems_as_text(problems: List[ProblemSection], output_dir: Path):
    """문제들을 텍스트 파일로 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== 파일 저장 ===\n")
    print(f"출력 디렉토리: {output_dir}\n")

    for problem in problems:
        filename = f"문제_{problem.number:03d}.txt"
        filepath = output_dir / filename

        # 미주 + 본문 텍스트
        full_text = problem.endnote_text + "\n\n"

        # 본문 문단들
        for para in problem.body_paras:
            # 네임스페이스 처리
            texts = para.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}t')
            if not texts:
                texts = para.findall('.//t')
            para_text = ''.join(t.text for t in texts if t.text)
            if para_text.strip():
                full_text += para_text + "\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_text)

        if problem.number <= 10:
            print(f"   [{problem.number:3d}] {filename:20s} ({problem.char_count:5d} 문자)")

    if len(problems) > 10:
        print(f"   ... 외 {len(problems) - 10}개")

    print(f"\n✓ 총 {len(problems)}개 파일 저장 완료")


if __name__ == "__main__":
    hwpx_file = r"Tests\seperation\6. 명제_2023.hwpx"
    output_directory = Path("Tests/seperation/problems_by_endnote")

    if not Path(hwpx_file).exists():
        print(f"파일이 존재하지 않습니다: {hwpx_file}")
        sys.exit(1)

    # 문제 분리
    problems = split_by_endnotes(hwpx_file)

    # 통계
    print_statistics(problems)

    # 파일 저장
    save_problems_as_text(problems, output_directory)
