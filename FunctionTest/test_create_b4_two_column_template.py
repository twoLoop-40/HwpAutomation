"""
B4 + 2단 레이아웃 템플릿 생성

목적: 한글 스크립트의 b4만들기 + 단2나누기를 Python으로 구현
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
    """밀리미터를 HWP 단위로 변환"""
    return int(mili * 283.465)


def setup_b4_page(hwp) -> bool:
    """
    B4 페이지 설정

    원본 스크립트: OnScriptMacro_b4만들기()
    - 용지: B4 (257mm x 364mm)
    - 여백: 좌우 30mm, 상 20mm, 하 15mm
    - 머리글/꼬리글: 15mm
    """
    try:
        print('\n[B4 페이지 설정]')
        hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)

        sec_def = hwp.HParameterSet.HSecDef
        sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)     # 257mm
        sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)    # 364mm
        sec_def.PageDef.LeftMargin = mili_to_hwp_unit(30.0)      # 좌측 30mm
        sec_def.PageDef.RightMargin = mili_to_hwp_unit(30.0)     # 우측 30mm
        sec_def.PageDef.TopMargin = mili_to_hwp_unit(20.0)       # 상단 20mm
        sec_def.PageDef.BottomMargin = mili_to_hwp_unit(15.0)    # 하단 15mm
        sec_def.PageDef.HeaderLen = mili_to_hwp_unit(15.0)       # 머리글 15mm
        sec_def.PageDef.FooterLen = mili_to_hwp_unit(15.0)       # 꼬리글 15mm
        sec_def.HSet.SetItem("ApplyClass", 24)                   # 적용 클래스
        sec_def.HSet.SetItem("ApplyTo", 3)                       # 적용 범위

        result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
        print(f'     PageSetup 실행: {result}')
        time.sleep(0.1)

        print('  ✅ B4 페이지 설정 완료')
        return True

    except Exception as e:
        print(f'  ❌ B4 페이지 설정 실패: {e}')
        import traceback
        traceback.print_exc()
        return False


def create_two_column_layout(hwp) -> bool:
    """
    2단 레이아웃 설정

    원본 스크립트: OnScriptMacro_단2나누기()
    - Count: 2 (2단)
    - SameGap: 8mm (단 간격)
    """
    try:
        print('\n[2단 레이아웃 설정]')
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


def test_create_b4_two_column_template():
    """B4 + 2단 레이아웃 템플릿 생성 테스트"""

    print('=' * 70)
    print('B4 + 2단 레이아웃 템플릿 생성 테스트')
    print('=' * 70)

    # 출력 파일
    output_path = Path(__file__).parent / "결과_B4_2단템플릿.hwp"

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
        hwp.HAction.Run("FileNew")
        time.sleep(0.5)
        print('✅ 문서 생성 완료')

        initial_pos = hwp.GetPos()
        print(f'초기 위치: {initial_pos}')

        # B4 페이지 설정
        print('\n[2/4] B4 페이지 설정')
        if not setup_b4_page(hwp):
            return False

        # 2단 레이아웃 설정
        print('\n[3/4] 2단 레이아웃 설정')
        if not create_two_column_layout(hwp):
            return False

        # 설정 후 위치 확인
        after_setup_pos = hwp.GetPos()
        print(f'\n설정 완료 후 위치: {after_setup_pos}')

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
        print('템플릿 설정')
        print('=' * 70)
        print('페이지:')
        print('  - 용지: B4 (257mm x 364mm)')
        print('  - 여백: 좌우 30mm, 상 20mm, 하 15mm')
        print('  - 머리글/꼬리글: 15mm')
        print()
        print('레이아웃:')
        print('  - 2단')
        print('  - 단 간격: 8mm')
        print()
        print('확인 사항:')
        print('  - 파일을 열어서 B4 크기 확인')
        print('  - 2단 레이아웃 적용 확인')
        print('  - 페이지 여백 확인')
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
    success = test_create_b4_two_column_template()
    sys.exit(0 if success else 1)
