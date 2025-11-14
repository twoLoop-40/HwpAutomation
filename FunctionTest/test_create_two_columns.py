"""
2단 레이아웃 설정 함수

목적: 한글 스크립트의 단2나누기 기능을 Python으로 구현
원본: OnScriptMacro_단2나누기()
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


def mili_to_hwp_unit(mili: float) -> int:
    """
    밀리미터를 HWP 단위로 변환

    HWP 단위 = 1/7200 inch = 1/283.465 mm
    """
    # 1mm = 283.465 HWPUNIT (approximately)
    return int(mili * 283.465)


def create_two_column_layout(hwp) -> bool:
    """
    2단 레이아웃 설정

    원본 스크립트:
    - Count = 2 (2단)
    - SameGap = MiliToHwpUnit(8.0) (단 간격 8mm)

    Args:
        hwp: HWP Automation 객체

    Returns:
        bool: 성공 여부
    """
    try:
        print('\n[다단 레이아웃 설정]')

        # MultiColumn Action
        print('  MultiColumn 설정')
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 2                           # 2단
        col_def.SameGap = mili_to_hwp_unit(8.0)     # 단 간격 8mm
        col_def.HSet.SetItem("ApplyClass", 832)     # 적용 클래스
        col_def.HSet.SetItem("ApplyTo", 6)          # 적용 범위

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        print(f'     MultiColumn 실행: {result}')
        time.sleep(0.1)

        print('  ✅ 2단 레이아웃 설정 완료')
        return True

    except Exception as e:
        print(f'  ❌ 2단 레이아웃 설정 실패: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_create_two_columns():
    """2단 레이아웃 설정 테스트"""

    print('=' * 70)
    print('2단 레이아웃 설정 테스트')
    print('=' * 70)

    # 출력 파일
    output_path = Path(__file__).parent / "결과_2단레이아웃.hwp"

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
        # 새 문서 생성
        print('\n[1/4] 새 문서 생성')
        # Action으로 새 문서 생성
        hwp.HAction.Run("FileNew")
        time.sleep(0.5)
        print('✅ 문서 생성 완료')

        # 초기 위치 확인
        initial_pos = hwp.GetPos()
        print(f'초기 위치: {initial_pos}')

        # 2단 레이아웃 설정
        print('\n[2/4] 2단 레이아웃 설정')
        success = create_two_column_layout(hwp)

        if not success:
            return False

        # 설정 후 위치 확인
        after_pos = hwp.GetPos()
        print(f'\n설정 후 위치: {after_pos}')

        # 테스트 텍스트 삽입
        print('\n[3/4] 테스트 텍스트 삽입')

        test_text = """첫 번째 단에 들어갈 텍스트입니다.
여러 줄의 텍스트를 입력하여
2단 레이아웃이 제대로 작동하는지
확인해봅니다.

이 텍스트는 첫 번째 단을 채우기 위한
긴 내용입니다. 충분히 길게 작성하여
두 번째 단으로 넘어가는지 확인합니다.

더 많은 텍스트를 추가합니다.
"""

        hwp.HAction.GetDefault('InsertText', hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = test_text
        hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        final_pos = hwp.GetPos()
        print(f'텍스트 삽입 후 위치: {final_pos}')
        print('✅ 테스트 텍스트 삽입 완료')

        # 결과 저장
        print(f'\n[4/4] 결과 저장: {output_path.name}')
        hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes')
        else:
            print(f'⚠️  저장 실패')

        # 결과 요약
        print('\n' + '=' * 70)
        print('테스트 결과')
        print('=' * 70)
        print('설정:')
        print('  - 2단 레이아웃')
        print('  - 단 간격: 8mm')
        print('  - 신문형 배치 (Newspaper)')
        print('  - 같은 너비 (SameSize)')
        print('  - 왼쪽부터 배치 (Left)')
        print('  - 구분선 없음 (None)')
        print()
        print('확인 사항:')
        print('  - 파일을 열어서 2단 레이아웃 적용되었는지 확인')
        print('  - 텍스트가 첫 번째 단 → 두 번째 단으로 흐르는지 확인')
        print('=' * 70)

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
    success = test_create_two_columns()
    sys.exit(0 if success else 1)
