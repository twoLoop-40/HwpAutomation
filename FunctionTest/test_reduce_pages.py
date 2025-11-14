"""
2페이지를 1페이지로 줄이는 테스트

방법 시도:
1. 여백 줄이기 (Top/Bottom/Left/Right Margin)
2. 페이지 크기 늘리기 (Paper Size)
3. 줄 간격 줄이기 (LineSpacing)
4. 글꼴 크기 줄이기 (FontSize)
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


def hwp_to_mm(hwp_unit: int) -> float:
    """HWP 단위를 밀리미터로 변환"""
    return hwp_unit / 283.465


def test_reduce_pages():
    """2페이지를 1페이지로 줄이는 테스트"""

    print('=' * 70)
    print('2페이지 → 1페이지 축소 테스트')
    print('=' * 70)

    # 파일 경로
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    all_files = sorted(problem_dir.glob("*.hwp"))
    test_file = all_files[3]  # 2025 커팅 S_공수2_기말_4회차_2_3_15.hwp

    output_path = Path("FunctionTest/결과_페이지축소.hwp")

    print(f'\n[1/6] 원본 파일 열기: {test_file.name}')

    client = AutomationClient()
    hwp = client.hwp

    # 보안 모듈
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

    # 창 숨기기
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    result = client.open_document(str(test_file))
    if not result.success:
        print(f'❌ 파일 열기 실패: {result.error}')
        return

    time.sleep(0.3)

    # 원본 페이지 수
    original_pages = hwp.PageCount
    print(f'✅ 원본 페이지 수: {original_pages}')

    try:
        # [2/6] 원본 페이지 설정 확인
        print(f'\n[2/6] 원본 페이지 설정...')
        hwp.HAction.GetDefault('PageSetup', hwp.HParameterSet.HSecDef.HSet)
        sec_def = hwp.HParameterSet.HSecDef

        original_width = sec_def.PageDef.PaperWidth
        original_height = sec_def.PageDef.PaperHeight
        original_left = sec_def.PageDef.LeftMargin
        original_right = sec_def.PageDef.RightMargin
        original_top = sec_def.PageDef.TopMargin
        original_bottom = sec_def.PageDef.BottomMargin

        print(f'  용지: {hwp_to_mm(original_width):.1f}mm x {hwp_to_mm(original_height):.1f}mm')
        print(f'  여백: L{hwp_to_mm(original_left):.1f} R{hwp_to_mm(original_right):.1f} T{hwp_to_mm(original_top):.1f} B{hwp_to_mm(original_bottom):.1f}')

        # [3/6] 전략 1: 여백 줄이기
        print(f'\n[3/6] 전략 1: 여백 줄이기 (10mm로)')
        hwp.HAction.GetDefault('PageSetup', hwp.HParameterSet.HSecDef.HSet)
        sec_def = hwp.HParameterSet.HSecDef

        sec_def.PageDef.LeftMargin = mili_to_hwp_unit(10.0)
        sec_def.PageDef.RightMargin = mili_to_hwp_unit(10.0)
        sec_def.PageDef.TopMargin = mili_to_hwp_unit(10.0)
        sec_def.PageDef.BottomMargin = mili_to_hwp_unit(10.0)
        sec_def.HSet.SetItem("ApplyClass", 24)
        sec_def.HSet.SetItem("ApplyTo", 3)

        result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
        time.sleep(0.2)

        pages_after_margin = hwp.PageCount
        print(f'  여백 축소 후 페이지: {pages_after_margin}')

        if pages_after_margin == 1:
            print(f'  ✅ 성공! 1페이지로 축소')
        else:
            print(f'  ⚠️  아직 {pages_after_margin}페이지')

            # [4/6] 전략 2: 페이지 크기 늘리기 (A4 → B4)
            print(f'\n[4/6] 전략 2: 페이지 크기 늘리기 (B4)')
            hwp.HAction.GetDefault('PageSetup', hwp.HParameterSet.HSecDef.HSet)
            sec_def = hwp.HParameterSet.HSecDef

            # B4 크기
            sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)
            sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)
            sec_def.PageDef.LeftMargin = mili_to_hwp_unit(10.0)
            sec_def.PageDef.RightMargin = mili_to_hwp_unit(10.0)
            sec_def.PageDef.TopMargin = mili_to_hwp_unit(10.0)
            sec_def.PageDef.BottomMargin = mili_to_hwp_unit(10.0)
            sec_def.HSet.SetItem("ApplyClass", 24)
            sec_def.HSet.SetItem("ApplyTo", 3)

            result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
            time.sleep(0.2)

            pages_after_size = hwp.PageCount
            print(f'  B4 크기 적용 후 페이지: {pages_after_size}')

            if pages_after_size == 1:
                print(f'  ✅ 성공! 1페이지로 축소')
            else:
                print(f'  ⚠️  아직 {pages_after_size}페이지')

        # [5/6] 최종 페이지 수 확인
        final_pages = hwp.PageCount
        print(f'\n[5/6] 최종 페이지 수: {final_pages}')

        # [6/6] 결과 저장
        print(f'\n[6/6] 결과 저장: {output_path.name}')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료 ({file_size:,} bytes)')
        else:
            print(f'⚠️  저장 실패')

        # 결과 요약
        print(f'\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'원본 파일: {test_file.name}')
        print(f'원본 페이지: {original_pages}')
        print(f'최종 페이지: {final_pages}')
        print(f'축소 성공: {"✅ Yes" if final_pages == 1 else "⚠️  No"}')
        print(f'출력 파일: {output_path}')
        print('=' * 70)

    finally:
        # 정리
        client.close_document()
        client.cleanup()


if __name__ == "__main__":
    test_reduce_pages()
