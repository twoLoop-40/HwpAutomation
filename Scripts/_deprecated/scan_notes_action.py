"""
NoteToNext 액션을 사용한 주석 순회

HwpIdris Actions/Misc.idr의 NoteToNext 사용
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


def scan_notes(file_path: str):
    """NoteToNext를 사용한 주석 스캔"""
    print(f"파일: {file_path}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 파일 열기 성공\n")

        print("=== NoteToNext로 주석 순회 ===")

        # 문서 처음으로
        hwp.Run("MoveDocBegin")

        note_count = 0
        all_text = []

        for i in range(1000):  # 최대 1000개
            # 다음 주석으로 이동
            result = hwp.Run("NoteToNext")

            if not result:
                print(f"더 이상 주석 없음 (총 {note_count}개)\n")
                break

            note_count += 1

            # 현재 주석의 텍스트 읽기
            hwp.Run("SelectAll")  # 주석 내 전체 선택
            text_result = hwp.GetText()
            text = text_result[1] if isinstance(text_result, tuple) else text_result
            text = str(text).strip() if text else ""

            all_text.append(text)

            if note_count <= 10:  # 처음 10개만 출력
                print(f"[{note_count}] {text[:100]}")

        if note_count > 10:
            print(f"... 외 {note_count - 10}개")

        print(f"\n총 {note_count}개 주석 발견")

        # 전체 텍스트 합쳐서 출력
        if all_text:
            full_text = '\n'.join(all_text)
            print(f"\n전체 텍스트 길이: {len(full_text)} 문자")
            print(f"첫 500자:\n{full_text[:500]}\n")

            # 문제 패턴 찾기
            import re
            patterns = [
                (r'\n\s*(\d+)\.\s+', '숫자.'),
                (r'\n\s*(\d+)\)\s+', '숫자)'),
            ]

            for pattern, name in patterns:
                matches = list(re.finditer(pattern, full_text))
                if matches:
                    print(f"{name} 패턴: {len(matches)}개 발견")
                    if matches:
                        numbers = [int(m.group(1)) for m in matches[:20]]
                        print(f"  처음 20개 번호: {numbers}")

        hwp.Clear(1)
        print("\n✓ 분석 완료")

        return note_count

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()
        return 0

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"
    scan_notes(test_file)
