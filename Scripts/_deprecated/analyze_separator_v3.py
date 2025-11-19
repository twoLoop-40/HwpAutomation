"""
문서 분리 분석 스크립트 V3

표 내부 포함한 전체 텍스트 추출 및 분석
"""

import sys
import codecs
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.automation_client import AutomationClient


def analyze_full_content(file_path: str):
    """전체 텍스트를 추출하여 문제 패턴 찾기"""
    print(f"\n{'='*60}")
    print(f"문서 분석 V3: {Path(file_path).name}")
    print(f"{'='*60}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        # FilePathChecker DLL 등록
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 문서 열기
        print(f"문서 열기: {file_path}")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 문서 열기 성공\n")

        # 기본 정보
        print("=== 기본 정보 ===")
        page_count = hwp.PageCount
        print(f"페이지 수: {page_count}")

        # 전체 텍스트 선택 및 추출
        print("\n=== 전체 텍스트 추출 ===")
        hwp.Run("SelectAll")
        text_result = hwp.GetText()

        # GetText()가 tuple을 반환하면 두 번째 요소 사용
        full_text = text_result[1] if isinstance(text_result, tuple) else text_result
        full_text = str(full_text) if full_text else ""

        print(f"추출된 텍스트 길이: {len(full_text)} 문자")
        print(f"첫 500자:\n{full_text[:500]}\n")

        # 문제 번호 패턴 찾기
        print("=== 문제 패턴 분석 ===")
        import re

        # 다양한 문제 번호 패턴
        patterns = [
            (r'\n\s*(\d+)\.\s+', '숫자.'),  # "1. " 형식
            (r'\n\s*(\d+)\)\s+', '숫자)'),   # "1) " 형식
            (r'\n\s*\[(\d+)\]\s+', '[숫자]'), # "[1] " 형식
            (r'\n\s*문제\s*(\d+)', '문제 숫자'),  # "문제 1" 형식
            (r'\n\s*제(\d+)문', '제N문'),     # "제1문" 형식
        ]

        problem_numbers = []
        for pattern, name in patterns:
            matches = re.finditer(pattern, full_text)
            count = 0
            positions = []
            for match in matches:
                count += 1
                num = match.group(1)
                pos = match.start()
                positions.append((int(num), pos))
                if count <= 5:  # 처음 5개만 출력
                    context = full_text[max(0, pos-20):min(len(full_text), pos+50)]
                    print(f"  {name} - 번호 {num}, 위치 {pos}: ...{context}...")

            if count > 0:
                print(f"  → 총 {count}개 발견 ({name})\n")
                problem_numbers.extend(positions)

        # 번호 정렬
        problem_numbers.sort(key=lambda x: x[1])  # 위치 기준 정렬
        unique_numbers = sorted(list(set([n[0] for n in problem_numbers])))

        print(f"=== 발견된 문제 번호 ===")
        print(f"총 문제 수: {len(problem_numbers)}")
        print(f"고유 번호: {len(unique_numbers)}개")
        if unique_numbers:
            print(f"번호 범위: {min(unique_numbers)} ~ {max(unique_numbers)}")
            print(f"처음 20개: {unique_numbers[:20]}")
            if len(unique_numbers) > 20:
                print(f"... 외 {len(unique_numbers) - 20}개")

        # 문서 닫기
        hwp.Clear(1)
        print("\n✓ 분석 완료")

        return {
            "page_count": page_count,
            "text_length": len(full_text),
            "problem_count": len(problem_numbers),
            "unique_numbers": unique_numbers
        }

    except Exception as e:
        print(f"\n✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"

    if not Path(test_file).exists():
        print(f"파일이 존재하지 않습니다: {test_file}")
        sys.exit(1)

    result = analyze_full_content(test_file)

    if result:
        print(f"\n{'='*60}")
        print("분석 결과 요약:")
        print(f"  - 페이지: {result['page_count']}")
        print(f"  - 텍스트: {result['text_length']} 문자")
        print(f"  - 문제: {result['problem_count']}개")
        print(f"  - 고유 번호: {len(result['unique_numbers'])}개")
        print(f"{'='*60}")
