"""
HKeyIndicator를 사용한 페이지/칼럼 정보 감지

목적: HKeyIndicator.CurrentColumn, CurrentLineNo, PrintPageNo 테스트
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

        info = {}

        # 모든 속성 확인
        for attr in dir(indicator):
            if not attr.startswith('_'):
                try:
                    value = getattr(indicator, attr)
                    if not callable(value):
                        info[attr] = value
                except:
                    pass

        return info
    except Exception as e:
        print(f'  ❌ HKeyIndicator 실패: {e}')
        return None


def test_key_indicator():
    """HKeyIndicator 테스트"""

    print('=' * 70)
    print('HKeyIndicator 페이지/칼럼 정보 테스트')
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
        print(f'\n문서 정보: PageCount = {page_count}')

        # 여러 위치에서 테스트
        print('\n[위치별 페이지/칼럼 정보]')
        print('-' * 70)

        test_positions = [
            (0, 0, 0),   # 첫 번째 칼럼 시작
            (0, 9, 0),   # 두 번째 문항 시작
            (0, 18, 0),  # 세 번째 문항 시작
            (0, 27, 0),  # 네 번째 문항 시작
            (0, 36, 0),  # 다섯 번째 문항 시작 (존재하지 않을 수 있음)
        ]

        for i, (list_num, para, pos) in enumerate(test_positions, 1):
            print(f'\n--- 위치 {i}: ({list_num}, {para}, {pos}) ---')

            # 이동
            hwp.SetPos(list_num, para, pos)
            time.sleep(0.05)

            # GetPos로 실제 위치 확인
            actual_pos = hwp.GetPos()
            print(f'  GetPos() = {actual_pos}')

            # HKeyIndicator 정보
            indicator_info = get_key_indicator_info(hwp)

            if indicator_info:
                print(f'  HKeyIndicator:')

                # 주요 정보만 출력
                key_attrs = ['CurrentColumn', 'CurrentLineNo', 'PrintPageNo']
                for attr in key_attrs:
                    if attr in indicator_info:
                        print(f'    {attr} = {indicator_info[attr]}')

                # 기타 관련 정보
                print(f'  \n  기타 정보:')
                for attr, value in indicator_info.items():
                    if attr not in key_attrs and 'page' in attr.lower() or 'column' in attr.lower() or 'line' in attr.lower():
                        print(f'    {attr} = {value}')

        # 문서 전체 순회하며 칼럼/페이지 변화 추적
        print('\n\n[전체 문서 순회]')
        print('-' * 70)

        # 문서 처음으로
        hwp.Run("MoveDocBegin")
        time.sleep(0.1)

        prev_page = None
        prev_column = None
        para_count = 0

        for para_num in range(50):  # 최대 50개 para 검사
            set_result = hwp.SetPos(0, para_num, 0)

            if not set_result:
                print(f'\nPara {para_num}부터 존재하지 않음')
                break

            actual_pos = hwp.GetPos()

            # KeyIndicator 확인
            indicator_info = get_key_indicator_info(hwp)

            if indicator_info:
                page = indicator_info.get('PrintPageNo', '?')
                column = indicator_info.get('CurrentColumn', '?')
                line = indicator_info.get('CurrentLineNo', '?')

                # 페이지나 칼럼이 변경되면 출력
                if page != prev_page or column != prev_column:
                    print(f'Para {para_num:2d}: Page={page}, Column={column}, Line={line}, Pos={actual_pos}')
                    prev_page = page
                    prev_column = column

            para_count += 1

        print(f'\n총 {para_count}개 Para 확인')

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
    success = test_key_indicator()
    sys.exit(0 if success else 1)
