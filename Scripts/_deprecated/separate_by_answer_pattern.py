"""
[정답] 패턴 기반 문제 분리 (HWPX)

HWPX 파일에서 [정답] 패턴을 찾아서 문제를 분리합니다.
EndNote가 없는 파일에 적합합니다.
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


def extract_text_with_positions(file_path: str):
    """텍스트와 위치 정보 추출"""
    with zipfile.ZipFile(file_path, 'r') as zf:
        section_files = [f for f in zf.namelist()
                        if 'section' in f.lower() and f.startswith('Contents/')]
        xml_content = zf.read(sorted(section_files)[0])
        root = ET.fromstring(xml_content)

        namespaces = {'hh': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}

        # 모든 paragraph 추출 (구조 유지)
        paragraphs = root.findall('.//hh:p', namespaces)

        text_parts = []
        for para in paragraphs:
            text_elements = para.findall('.//hh:t', namespaces)
            para_text = ''.join(t.text for t in text_elements if t.text)
            if para_text.strip():
                text_parts.append(para_text)

        return text_parts, root, namespaces


def find_answer_positions(text_parts):
    """[정답] 패턴 찾기"""
    answer_pattern = r'\[정답\]\s*[➀-➄①-⑤]'

    positions = []
    cumulative_len = 0

    for para_idx, text in enumerate(text_parts):
        for match in re.finditer(answer_pattern, text):
            positions.append({
                'para_idx': para_idx,
                'match_start': match.start(),
                'match_end': match.end(),
                'cumulative_pos': cumulative_len + match.end(),  # [정답] 끝 = 문제 끝
                'text': text[max(0, match.start()-50):match.end()+50]
            })
        cumulative_len += len(text) + 1  # +1 for paragraph break

    return positions


def split_problems(text_parts, answer_positions):
    """[정답] 기준으로 문제 분리"""
    problems = []

    # 첫 문제 시작은 0번째 para
    start_para = 0
    start_offset = 0

    for i, ans_pos in enumerate(answer_positions):
        end_para = ans_pos['para_idx']
        end_offset = ans_pos['match_end']

        # 문제 텍스트 추출
        problem_text_parts = []

        # 시작 para
        if start_para == end_para:
            problem_text_parts.append(text_parts[start_para][start_offset:end_offset])
        else:
            problem_text_parts.append(text_parts[start_para][start_offset:])

            # 중간 paras
            for para_idx in range(start_para + 1, end_para):
                problem_text_parts.append(text_parts[para_idx])

            # 끝 para
            if end_para < len(text_parts):
                problem_text_parts.append(text_parts[end_para][:end_offset])

        problem_text = '\n'.join(problem_text_parts).strip()

        if problem_text:
            problems.append({
                'number': i + 1,
                'text': problem_text,
                'start_para': start_para,
                'end_para': end_para,
                'char_count': len(problem_text)
            })

        # 다음 문제 시작 위치
        start_para = end_para
        start_offset = end_offset

    return problems


def save_problems(problems, output_dir: Path, group_size: int = 1):
    """문제 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)

    if group_size == 1:
        # 1문제 = 1파일
        for prob in problems:
            output_path = output_dir / f"문제_{prob['number']:03d}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"{'='*60}\n")
                f.write(f"문제 {prob['number']}\n")
                f.write(f"{'='*60}\n\n")
                f.write(prob['text'])
            print(f"✓ {output_path.name} ({prob['char_count']:,} 문자)")
    else:
        # N개씩 그룹
        for group_idx in range(0, len(problems), group_size):
            group = problems[group_idx:group_idx + group_size]
            start_num = group[0]['number']
            end_num = group[-1]['number']

            output_path = output_dir / f"문제_{start_num:03d}-{end_num:03d}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                for prob in group:
                    f.write(f"{'='*60}\n")
                    f.write(f"문제 {prob['number']}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(prob['text'])
                    f.write("\n\n\n")

            total_chars = sum(p['char_count'] for p in group)
            print(f"✓ {output_path.name} ({len(group)}문제, {total_chars:,} 문자)")


def main():
    # 테스트 파일
    test_file = r"Tests\seperation\6. 명제_2023.hwpx"
    output_dir = Path("Tests/seperation/output_text_based")

    print(f"파일: {Path(test_file).name}\n")

    # 텍스트 추출
    print("1. 텍스트 추출 중...")
    text_parts, root, ns = extract_text_with_positions(test_file)
    print(f"   총 {len(text_parts)}개 문단, {sum(len(t) for t in text_parts):,} 문자\n")

    # [정답] 찾기
    print("2. [정답] 패턴 찾기...")
    answer_positions = find_answer_positions(text_parts)
    print(f"   총 {len(answer_positions)}개 발견\n")

    # 문제 분리
    print("3. 문제 분리 중...")
    problems = split_problems(text_parts, answer_positions)
    print(f"   총 {len(problems)}개 문제\n")

    # 통계
    print("=== 통계 ===")
    print(f"문제 수: {len(problems)}개")
    char_counts = [p['char_count'] for p in problems]
    print(f"평균 길이: {sum(char_counts) / len(char_counts):.0f} 문자")
    print(f"최소 길이: {min(char_counts)} 문자")
    print(f"최대 길이: {max(char_counts)} 문자\n")

    # 처음 3개 샘플 출력
    print("=== 처음 3개 문제 샘플 ===\n")
    for prob in problems[:3]:
        preview = prob['text'][:200].replace('\n', ' ')
        print(f"문제 {prob['number']:3d}: {preview}...\n")

    # 저장
    print("\n=== 파일 저장 ===\n")
    save_problems(problems[:10], output_dir, group_size=1)  # 처음 10개만 테스트

    print(f"\n완료! 출력 디렉토리: {output_dir}")


if __name__ == "__main__":
    main()
