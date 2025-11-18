"""
GetText() 반환값 디버깅
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


def debug_gettext(file_path: str):
    """GetText() 디버깅"""
    print(f"파일: {file_path}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 파일 열기 성공\n")

        # SelectAll
        print("SelectAll 실행...")
        hwp.Run("SelectAll")

        # GetText() 원시 반환값
        print("\nGetText() 원시 반환값:")
        result = hwp.GetText()
        print(f"타입: {type(result)}")
        print(f"내용: {repr(result)}")

        if isinstance(result, tuple):
            print(f"\n튜플 길이: {len(result)}")
            for i, item in enumerate(result):
                print(f"  [{i}]: {type(item)} = {repr(item)[:100]}")

        # 다른 방법들 시도
        print("\n\n=== 대안 방법들 ===")

        # 1. MoveDocBegin
        hwp.Run("MoveDocBegin")
        hwp.Run("Select")
        result2 = hwp.GetText()
        print(f"1. MoveDocBegin + Select: {type(result2)} = {repr(result2)[:100]}")

        # 2. 문단별로 읽기
        hwp.Run("MoveDocBegin")
        hwp.Run("SelectParaBegin")
        hwp.Run("SelectParaEnd")
        result3 = hwp.GetText()
        print(f"2. SelectParaBegin/End: {type(result3)} = {repr(result3)[:100]}")

        # 3. TextFile로 저장 후 읽기
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            hwp.SaveAs(tmp_path, "TEXT")
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
            print(f"3. TEXT 파일 저장: {len(text_content)} 문자")
            print(f"   첫 200자: {text_content[:200]}")
        except Exception as e:
            print(f"3. TEXT 파일 저장 실패: {e}")

        hwp.Clear(1)

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"
    debug_gettext(test_file)
