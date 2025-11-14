"""
MoveSel 명령 연구 테스트

목적: MoveSelLeft, MoveSelRight, MoveSelDown의 동작 차이 파악

테스트 항목:
1. MoveSelLeft vs MoveSelRight - 방향 차이
2. MoveSelDown - 줄 단위 선택
3. 빈 Para 삭제에 최적인 명령 파악
"""

import sys
import time
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


def test_movesel_left():
    """MoveSelLeft 테스트 - 왼쪽으로 선택 확장"""
    print('\n[1/4] MoveSelLeft 테스트')
    print('-' * 70)

    client = AutomationClient()
    hwp = client.hwp

    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 새 문서 생성
        hwp.HAction.Run("FileNew")
        time.sleep(0.3)

        # 테스트 텍스트 삽입
        hwp.Run("MoveDocBegin")
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = "ABCDEFGH"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('삽입된 텍스트: "ABCDEFGH"')

        # 문서 끝으로 이동 (H 뒤)
        hwp.Run("MoveDocEnd")
        start_pos = hwp.GetPos()
        print(f'시작 위치 (H 뒤): {start_pos}')

        # MoveSelLeft 3번
        print('\nMoveSelLeft 3번 실행...')
        for i in range(3):
            hwp.Run("MoveSelLeft")
            time.sleep(0.05)
            curr_pos = hwp.GetPos()
            print(f'  {i+1}회: pos={curr_pos}')

        # 선택된 텍스트 확인
        hwp.Run("Copy")
        time.sleep(0.1)

        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            selected = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f'\n선택된 텍스트: "{selected}"')
            print(f'예상: "FGH" (오른쪽 3글자)')
        except:
            print('클립보드 읽기 실패')

        hwp.Run("Cancel")

        return True

    except Exception as e:
        print(f'오류: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.close_document()
        client.cleanup()


def test_movesel_right():
    """MoveSelRight 테스트 - 오른쪽으로 선택 확장"""
    print('\n[2/4] MoveSelRight 테스트')
    print('-' * 70)

    client = AutomationClient()
    hwp = client.hwp

    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 새 문서 생성
        hwp.HAction.Run("FileNew")
        time.sleep(0.3)

        # 테스트 텍스트 삽입
        hwp.Run("MoveDocBegin")
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = "ABCDEFGH"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('삽입된 텍스트: "ABCDEFGH"')

        # 문서 시작으로 이동 (A 앞)
        hwp.Run("MoveDocBegin")
        start_pos = hwp.GetPos()
        print(f'시작 위치 (A 앞): {start_pos}')

        # MoveSelRight 3번
        print('\nMoveSelRight 3번 실행...')
        for i in range(3):
            hwp.Run("MoveSelRight")
            time.sleep(0.05)
            curr_pos = hwp.GetPos()
            print(f'  {i+1}회: pos={curr_pos}')

        # 선택된 텍스트 확인
        hwp.Run("Copy")
        time.sleep(0.1)

        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            selected = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f'\n선택된 텍스트: "{selected}"')
            print(f'예상: "ABC" (왼쪽 3글자)')
        except:
            print('클립보드 읽기 실패')

        hwp.Run("Cancel")

        return True

    except Exception as e:
        print(f'오류: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.close_document()
        client.cleanup()


def test_movesel_down():
    """MoveSelDown 테스트 - 아래로 선택 확장"""
    print('\n[3/4] MoveSelDown 테스트')
    print('-' * 70)

    client = AutomationClient()
    hwp = client.hwp

    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 새 문서 생성
        hwp.HAction.Run("FileNew")
        time.sleep(0.3)

        # 여러 줄 텍스트 삽입
        hwp.Run("MoveDocBegin")
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = "Line1"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.Run("BreakPara")

        hwp.HParameterSet.HInsertText.Text = "Line2"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.Run("BreakPara")

        hwp.HParameterSet.HInsertText.Text = "Line3"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('삽입된 텍스트:')
        print('  Line1')
        print('  Line2')
        print('  Line3')

        # 문서 시작으로 이동
        hwp.Run("MoveDocBegin")
        start_pos = hwp.GetPos()
        print(f'\n시작 위치: {start_pos}')

        # MoveSelDown 2번
        print('\nMoveSelDown 2번 실행...')
        for i in range(2):
            hwp.Run("MoveSelDown")
            time.sleep(0.05)
            curr_pos = hwp.GetPos()
            print(f'  {i+1}회: pos={curr_pos}')

        # 선택된 텍스트 확인
        hwp.Run("Copy")
        time.sleep(0.1)

        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            selected = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f'\n선택된 텍스트:\n"{selected}"')
            print(f'예상: "Line1\\nLine2" (2줄)')
        except:
            print('클립보드 읽기 실패')

        hwp.Run("Cancel")

        return True

    except Exception as e:
        print(f'오류: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.close_document()
        client.cleanup()


def test_empty_para_with_movesel():
    """빈 Para에 대한 MoveSel 동작 테스트"""
    print('\n[4/4] 빈 Para에 대한 MoveSel 테스트')
    print('-' * 70)

    client = AutomationClient()
    hwp = client.hwp

    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 새 문서 생성
        hwp.HAction.Run("FileNew")
        time.sleep(0.3)

        # 텍스트 + 빈 Para + 텍스트 구조
        hwp.Run("MoveDocBegin")
        hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = "Before"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        hwp.Run("BreakPara")
        hwp.Run("BreakPara")  # 빈 Para
        hwp.HParameterSet.HInsertText.Text = "After"
        hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('구조:')
        print('  Para 0: "Before"')
        print('  Para 1: (빈 문단)')
        print('  Para 2: "After"')

        # Para 1 (빈 문단) 시작으로 이동
        hwp.Run("MoveDocBegin")
        hwp.Run("MoveNextParaBegin")
        empty_para_pos = hwp.GetPos()
        print(f'\n빈 Para 시작 위치: {empty_para_pos}')

        # 끝 위치 확인
        hwp.Run("MoveParaEnd")
        end_pos = hwp.GetPos()
        print(f'빈 Para 끝 위치: {end_pos}')
        print(f'빈 Para 확인: {end_pos[2] == 0}')

        # 방법 1: MoveSelRight (from start)
        print('\n[방법 1] 빈 Para 시작에서 MoveSelRight x2')
        hwp.SetPos(empty_para_pos[0], empty_para_pos[1], empty_para_pos[2])
        hwp.Run("MoveSelRight")
        hwp.Run("MoveSelRight")
        time.sleep(0.05)

        # 선택 확인
        hwp.Run("Copy")
        time.sleep(0.1)
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            selected = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f'선택된 텍스트: "{selected}"')
        except:
            print('선택 없음 또는 클립보드 읽기 실패')

        hwp.Run("Cancel")

        # 방법 2: MoveSelDown (from start)
        print('\n[방법 2] 빈 Para 시작에서 MoveSelDown x1')
        hwp.SetPos(empty_para_pos[0], empty_para_pos[1], empty_para_pos[2])
        hwp.Run("MoveSelDown")
        time.sleep(0.05)

        # 선택 확인
        hwp.Run("Copy")
        time.sleep(0.1)
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            selected = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            print(f'선택된 텍스트: "{selected}"')
        except:
            print('선택 없음 또는 클립보드 읽기 실패')

        hwp.Run("Cancel")

        return True

    except Exception as e:
        print(f'오류: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.close_document()
        client.cleanup()


def main():
    print('=' * 70)
    print('MoveSel 명령 연구 테스트')
    print('=' * 70)

    results = []

    results.append(('MoveSelLeft', test_movesel_left()))
    time.sleep(0.5)

    results.append(('MoveSelRight', test_movesel_right()))
    time.sleep(0.5)

    results.append(('MoveSelDown', test_movesel_down()))
    time.sleep(0.5)

    results.append(('Empty Para MoveSel', test_empty_para_with_movesel()))
    time.sleep(0.5)

    # 결과 요약
    print('\n' + '=' * 70)
    print('테스트 결과 요약')
    print('=' * 70)

    for name, success in results:
        status = '✅' if success else '❌'
        print(f'{status} {name}')

    print('\n' + '=' * 70)
    print('결론 및 권장사항')
    print('=' * 70)
    print('1. MoveSelLeft: 현재 위치에서 왼쪽(이전)으로 선택 확장')
    print('2. MoveSelRight: 현재 위치에서 오른쪽(다음)으로 선택 확장')
    print('3. MoveSelDown: 현재 위치에서 아래(다음 줄)로 선택 확장')
    print('\n빈 Para 삭제 최적 방법:')
    print('  - Para 시작에서: MoveSelRight 또는 MoveSelDown')
    print('  - Para 끝에서: MoveSelLeft')
    print('=' * 70)

    return all(success for _, success in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
