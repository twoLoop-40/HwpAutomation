"""
Preprocessed 파일 테스트

정상적인 파일로 텍스트 읽기 테스트
"""

import sys
import codecs
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# 프로젝트 루트
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.automation_client import AutomationClient


def test_file(file_path: str):
    """파일 테스트"""
    print(f"파일: {Path(file_path).name}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 파일 열기 성공")

        # 페이지 수
        print(f"페이지 수: {hwp.PageCount}")

        # SelectAll + GetText
        hwp.Run("SelectAll")
        text_result = hwp.GetText()
        text = text_result[1] if isinstance(text_result, tuple) else text_result
        text = str(text) if text else ""

        print(f"텍스트 길이: {len(text)} 문자")
        print(f"첫 200자:\n{text[:200]}\n")

        # 문제 패턴 찾기
        import re
        pattern = r'\n\s*(\d+)\.\s+'
        matches = list(re.finditer(pattern, text))
        print(f"'숫자.' 패턴: {len(matches)}개 발견")

        if matches:
            numbers = [int(m.group(1)) for m in matches[:20]]
            print(f"처음 20개 번호: {numbers}")

        hwp.Clear(1)
        print("\n✓ 테스트 완료")

        return len(text) > 0

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.quit()


if __name__ == "__main__":
    # Tests/AppV1/Preprocessed 파일 중 하나
    test_path = Path("Tests/AppV1/Preprocessed")

    # 첫 번째 hwp 파일 찾기
    hwp_files = list(test_path.glob("*.hwp"))
    if not hwp_files:
        print("HWP 파일을 찾을 수 없습니다.")
        sys.exit(1)

    test_file_path = str(hwp_files[0])
    print(f"테스트 파일: {test_file_path}\n")

    success = test_file(test_file_path)
    print(f"\n{'성공!' if success else '실패'}")
