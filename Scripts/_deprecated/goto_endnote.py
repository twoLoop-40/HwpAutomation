"""
Goto 액션으로 미주 영역 이동 시도

HwpIdris Actions/Navigation.idr의 Goto 사용
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


def goto_endnote_area(file_path: str):
    """Goto로 미주 영역 이동"""
    print(f"파일: {file_path}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 파일 열기 성공\n")

        print("=== 미주 영역으로 이동 시도 ===\n")

        # 방법 1: Ctrl+End로 문서 끝으로
        print("1. 문서 끝으로 이동 (Ctrl+End)")
        hwp.Run("MoveDocEnd")

        # 현재 위치에서 텍스트 읽기
        hwp.Run("SelectParaBegin")
        hwp.Run("SelectParaEnd")
        text_result = hwp.GetText()
        text = text_result[1] if isinstance(text_result, tuple) else text_result
        text = str(text).strip() if text else ""
        print(f"   현재 문단: {text[:100]}")

        # 방법 2: 위로 올라가면서 스캔
        print("\n2. 역순 스캔 (문서 끝에서 위로)")
        problems_found = []

        for i in range(500):  # 최대 500문단
            hwp.Run("SelectParaBegin")
            hwp.Run("SelectParaEnd")
            text_result = hwp.GetText()
            text = text_result[1] if isinstance(text_result, tuple) else text_result
            text = str(text).strip() if text else ""

            # "숫자." 패턴 찾기
            if text and len(text) > 1:
                if text[0].isdigit() and text[1] == '.':
                    problems_found.append((i, text[:80]))
                    if len(problems_found) <= 10:
                        print(f"   [{len(problems_found)}] {text[:80]}")

            # 이전 문단으로
            result = hwp.Run("MovePrevParaBegin")
            if not result:
                break

        if len(problems_found) > 10:
            print(f"   ... 외 {len(problems_found) - 10}개")

        print(f"\n총 {len(problems_found)}개 문제 발견!")

        # 방법 3: 첫 번째 미주 찾기
        print("\n3. 미주 번호로 찾기")
        hwp.Run("MoveDocBegin")

        # Find & Replace로 "1." 검색
        pset = hwp.HParameterSet.HFindReplace
        hwp.HAction.GetDefault("RepeatFind", pset.HSet)
        pset.FindString = "1."
        pset.FindType = 1  # 정확히 일치

        result = hwp.HAction.Execute("RepeatFind", pset.HSet)
        if result:
            print(f"   '1.' 찾기 성공!")

            # 현재 위치 텍스트
            hwp.Run("SelectParaBegin")
            hwp.Run("SelectParaEnd")
            text_result = hwp.GetText()
            text = text_result[1] if isinstance(text_result, tuple) else text_result
            print(f"   찾은 위치: {str(text)[:100]}")
        else:
            print(f"   '1.' 찾기 실패")

        hwp.Clear(1)
        print("\n✓ 분석 완료")

        return problems_found

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"
    goto_endnote_area(test_file)
