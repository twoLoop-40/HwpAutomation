"""
페이지와 칼럼 정보 감지 테스트

목적: (list, para, pos) → (page, col, line) 매핑 방법 찾기
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


def test_page_column_detection():
    """페이지와 칼럼 정보 감지"""

    print('=' * 70)
    print('페이지와 칼럼 정보 감지 테스트')
    print('=' * 70)

    # E2E 결과 파일 열기
    test_file = Path("FunctionTest/결과_E2E_B4_2단_합병.hwp")

    if not test_file.exists():
        print(f'❌ 테스트 파일이 없습니다: {test_file}')
        return False

    client = AutomationClient()
    hwp = client.hwp

    # 보안 모듈 등록
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    # 창 숨기기
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 파일 열기
        print(f'\n파일 열기: {test_file.name}')
        result = client.open_document(str(test_file), options="readonly:true")

        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.3)
        print('✅ 파일 열기 완료')

        # 문서 정보
        page_count = hwp.PageCount
        print(f'\n문서 정보:')
        print(f'  PageCount: {page_count}')

        # 여러 위치에서 페이지/칼럼 정보 확인
        print('\n[위치별 정보 확인]')
        print('-' * 70)

        test_positions = [
            (0, 0, 0),   # 첫 번째 칼럼 시작
            (0, 9, 0),   # 두 번째 문항 시작
            (0, 18, 0),  # 세 번째 문항 시작
            (0, 27, 0),  # 네 번째 문항 시작
            (0, 36, 0),  # 다섯 번째 문항 시작
        ]

        for i, (list_num, para, pos) in enumerate(test_positions, 1):
            print(f'\n--- 위치 {i} ---')
            print(f'SetPos({list_num}, {para}, {pos})')

            # 이동
            hwp.SetPos(list_num, para, pos)
            time.sleep(0.05)

            # GetPos로 실제 위치 확인
            actual_pos = hwp.GetPos()
            print(f'  GetPos() = {actual_pos}')

            # 사용 가능한 속성들 확인
            try:
                # PosToLinePos - 라인 정보 변환
                line_pos = hwp.PosToLinePos(actual_pos)
                print(f'  PosToLinePos() = {line_pos}')
            except Exception as e:
                print(f'  PosToLinePos() 실패: {e}')

            try:
                # GetCursorPos - 커서 위치 정보
                cursor_info = hwp.GetCursorPos()
                print(f'  GetCursorPos() = {cursor_info}')
            except Exception as e:
                print(f'  GetCursorPos() 실패: {e}')

            try:
                # GetPosBySet - ParameterSet 정보
                hwp.HAction.GetDefault("MoveToPage", hwp.HParameterSet.HMoveToPage.HSet)
                move_page = hwp.HParameterSet.HMoveToPage
                print(f'  MoveToPage.Page = {move_page.Page if hasattr(move_page, "Page") else "N/A"}')
            except Exception as e:
                print(f'  MoveToPage 실패: {e}')

            # 가능한 모든 속성 출력
            print('\n  hwp 객체의 관련 속성들:')
            for attr in dir(hwp):
                if any(keyword in attr.lower() for keyword in ['page', 'column', 'col', 'line', 'cursor', 'pos']):
                    try:
                        value = getattr(hwp, attr)
                        if not callable(value):
                            print(f'    {attr} = {value}')
                    except:
                        pass

        # ParameterSet 탐색
        print('\n[ParameterSet 탐색]')
        print('-' * 70)

        try:
            param_set = hwp.HParameterSet
            print('HParameterSet 속성들:')
            for attr in dir(param_set):
                if not attr.startswith('_'):
                    try:
                        obj = getattr(param_set, attr)
                        print(f'  {attr}: {type(obj).__name__}')

                        # 하위 속성도 확인
                        if hasattr(obj, 'HSet'):
                            for sub_attr in dir(obj):
                                if any(keyword in sub_attr.lower() for keyword in ['page', 'column', 'col', 'line']):
                                    print(f'    └─ {sub_attr}')
                    except:
                        pass
        except Exception as e:
            print(f'ParameterSet 탐색 실패: {e}')

        return True

    except Exception as e:
        print(f'\n💥 오류 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 정리
        print('\n[정리] 문서 닫기...')
        client.close_document()
        client.cleanup()
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_page_column_detection()
    sys.exit(0 if success else 1)
