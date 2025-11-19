"""
문서 분리 분석 스크립트

6. 명제_2023.hwp 파일의 구조를 분석하여:
1. 전체 문단 수
2. 문제 구분 패턴 찾기
3. 각 문제의 시작/끝 위치
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


def analyze_document_structure(file_path: str):
    """문서 구조 분석"""
    print(f"\n{'='*60}")
    print(f"문서 분석: {Path(file_path).name}")
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

        # 전체 선택하여 문단 수 확인
        hwp.Run("SelectAll")
        hwp.Run("MoveDocBegin")

        # 문단 스캔
        print("\n=== 문단 스캔 ===")
        para_count = 0
        problems = []  # (para_index, text_preview)
        current_text = ""

        hwp.Run("MoveDocBegin")

        for i in range(10000):  # 최대 10000 문단
            # 현재 문단 텍스트 가져오기
            hwp.Run("SelectParaBegin")
            hwp.Run("SelectParaEnd")
            text_result = hwp.GetText()

            # GetText()가 tuple을 반환하면 첫 번째 요소 사용
            text = text_result[1] if isinstance(text_result, tuple) else text_result

            # 문제 번호 패턴 찾기 (예: "1.", "1)", "[1]", "문제 1" 등)
            text_stripped = str(text).strip() if text else ""
            if text_stripped:
                # 숫자로 시작하는 패턴
                if (text_stripped[0].isdigit() and
                    len(text_stripped) > 1 and
                    text_stripped[1] in ['.', ')', ']']):
                    problems.append((i, text_stripped[:50]))
                    print(f"문단 {i}: {text_stripped[:50]}")

            para_count += 1

            # 다음 문단으로
            hwp.Run("MoveParaEnd")
            prev_pos = hwp.GetPos()
            hwp.Run("MoveDown")
            new_pos = hwp.GetPos()

            # 위치가 변하지 않으면 문서 끝
            if prev_pos == new_pos:
                break

        print(f"\n총 문단 수: {para_count}")
        print(f"발견된 문제 수: {len(problems)}")

        if problems:
            print("\n=== 문제 목록 ===")
            for idx, (para_idx, preview) in enumerate(problems[:20], 1):
                print(f"{idx}. 문단 {para_idx}: {preview}")

            if len(problems) > 20:
                print(f"... 외 {len(problems) - 20}개")

        # 문서 닫기
        hwp.Clear(1)
        print("\n✓ 분석 완료")

        return {
            "page_count": page_count,
            "para_count": para_count,
            "problems": problems
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

    result = analyze_document_structure(test_file)

    if result:
        print(f"\n{'='*60}")
        print("분석 결과 요약:")
        print(f"  - 페이지: {result['page_count']}")
        print(f"  - 문단: {result['para_count']}")
        print(f"  - 문제: {len(result['problems'])}")
        print(f"{'='*60}")
