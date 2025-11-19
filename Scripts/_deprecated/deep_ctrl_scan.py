"""
깊이 우선 Ctrl 탐색

모든 컨트롤을 재귀적으로 탐색하여 en(미주), fn(각주) 찾기
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


def explore_ctrl(ctrl, depth=0, max_depth=5):
    """재귀적으로 Ctrl 탐색"""
    results = []
    indent = "  " * depth

    if ctrl is None or depth > max_depth:
        return results

    try:
        ctrl_id = ctrl.CtrlID
        info = f"{indent}[{depth}] CtrlID: {ctrl_id}"

        # 추가 속성 확인
        try:
            if hasattr(ctrl, 'UserDesc'):
                info += f" | UserDesc: {ctrl.UserDesc}"
            if hasattr(ctrl, 'Text'):
                text = str(ctrl.Text)[:50]
                info += f" | Text: {text}"
        except:
            pass

        results.append((ctrl_id, depth, info))
        print(info)

        # en(미주)나 fn(각주)인 경우 내용 읽기 시도
        if ctrl_id in ["en", "fn"]:
            print(f"{indent}  → 주석 발견! 내용 읽기 시도...")
            try:
                # Child로 들어가기
                if hasattr(ctrl, 'GetTextFile'):
                    text = ctrl.GetTextFile(0, -1)
                    print(f"{indent}  → GetTextFile: {text[:100]}")
            except Exception as e:
                print(f"{indent}  → 읽기 실패: {e}")

        # Child 탐색
        if hasattr(ctrl, 'Child'):
            child = ctrl.Child
            if child:
                print(f"{indent}  ↓ Child 탐색:")
                child_results = explore_ctrl(child, depth + 1, max_depth)
                results.extend(child_results)

        # Next 탐색 (같은 레벨)
        if hasattr(ctrl, 'Next'):
            next_ctrl = ctrl.Next
            if next_ctrl:
                next_results = explore_ctrl(next_ctrl, depth, max_depth)
                results.extend(next_results)

    except Exception as e:
        print(f"{indent}에러: {e}")

    return results


def deep_scan(file_path: str):
    """깊이 우선 탐색"""
    print(f"파일: {file_path}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 파일 열기 성공\n")

        print("=== 깊이 우선 Ctrl 탐색 ===\n")

        head = hwp.HeadCtrl
        if head:
            results = explore_ctrl(head, depth=0, max_depth=10)

            print(f"\n{'='*60}")
            print(f"총 {len(results)}개 컨트롤 발견")

            # en, fn 통계
            en_count = sum(1 for ctrl_id, _, _ in results if ctrl_id == "en")
            fn_count = sum(1 for ctrl_id, _, _ in results if ctrl_id == "fn")

            print(f"미주(en): {en_count}개")
            print(f"각주(fn): {fn_count}개")
            print(f"{'='*60}")

            return results
        else:
            print("HeadCtrl이 None입니다.")
            return []

        hwp.Clear(1)

    except Exception as e:
        print(f"에러: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"
    deep_scan(test_file)
