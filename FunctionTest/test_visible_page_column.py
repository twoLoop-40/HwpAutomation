"""
창을 표시하고 페이지/칼럼 정보 감지

목적: 창을 Visible=True로 설정하고 HKeyIndicator 재테스트
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


def get_key_indicator_info(hwp):
    """HKeyIndicator 정보 가져오기"""
    try:
        hwp.HAction.GetDefault("KeyIndicator", hwp.HParameterSet.HKeyIndicator.HSet)
        indicator = hwp.HParameterSet.HKeyIndicator

        return {
            'CurrentColumn': indicator.CurrentColumn,
            'CurrentLineNo': indicator.CurrentLineNo,
            'PrintPageNo': indicator.PrintPageNo,
        }
    except Exception as e:
        return {'error': str(e)}


def test_visible_page_column():
    """창을 표시하고 페이지/칼럼 정보 테스트"""

    print('=' * 70)
    print('창 표시 + 페이지/칼럼 정보 테스트')
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

    # 창 표시 (Visible=True)
    print('\n창을 표시합니다...')
    try:
        hwp.XHwpWindows.Item(0).Visible = True
        print('✅ 창 표시 완료')
    except Exception as e:
        print(f'⚠️  창 표시 실패: {e}')

    try:
        # 파일 열기
        print(f'\n파일 열기: {test_file.name}')
        result = client.open_document(str(test_file), options="readonly:true")

        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(1.0)  # 화면 렌더링 대기
        print('✅ 파일 열기 완료')

        # 문서 정보
        page_count = hwp.PageCount
        print(f'\n문서 정보: PageCount = {page_count}')

        # 여러 위치에서 테스트
        print('\n[위치별 페이지/칼럼 정보 - 창 표시 모드]')
        print('-' * 70)

        test_positions = [
            (0, 0, 0),   # 첫 번째 칼럼 시작
            (0, 1, 0),   # Para 1
            (0, 9, 0),   # 두 번째 문항 시작
            (0, 10, 0),  # Para 10
            (0, 18, 0),  # 세 번째 문항 시작
            (0, 19, 0),  # Para 19
            (0, 27, 0),  # 네 번째 문항 시작
            (0, 28, 0),  # Para 28
        ]

        for i, (list_num, para, pos) in enumerate(test_positions, 1):
            print(f'\n--- 위치 {i}: SetPos({list_num}, {para}, {pos}) ---')

            # 이동
            hwp.SetPos(list_num, para, pos)
            time.sleep(0.2)  # 화면 업데이트 대기

            # GetPos로 실제 위치 확인
            actual_pos = hwp.GetPos()
            print(f'  GetPos() = {actual_pos}')

            # HKeyIndicator 정보
            indicator_info = get_key_indicator_info(hwp)
            print(f'  Page={indicator_info.get("PrintPageNo", "?")}, Column={indicator_info.get("CurrentColumn", "?")}, Line={indicator_info.get("CurrentLineNo", "?")}')

        print('\n\n테스트 완료!')
        print('창을 5초 후 닫습니다...')
        time.sleep(5.0)

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
    success = test_visible_page_column()
    sys.exit(0 if success else 1)
