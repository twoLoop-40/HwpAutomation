"""
2페이지 이상의 파일을 1페이지로 병합

전략 (순서대로 시도):
1. 빈 Para 제거
2. 여백 축소 (8mm)
3. 줄 간격 축소 (85%)
4. 폰트 크기 축소 (80%)

기반: test_reduce_pages.py + test_analyze_2page_structure.py
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


def find_all_paras(hwp):
    """문서의 모든 Para 찾기"""
    paras = []

    hwp.InitScan(Range=0x0077)  # Body only

    while True:
        state = hwp.GetText()
        if state == 0 or state == 1:  # 끝
            break

        text = hwp.GetTextFile("TEXT")
        paras.append({
            'index': len(paras),
            'text': text,
            'is_empty': (text.strip() == '')
        })

    hwp.ReleaseScan()

    return paras


def remove_empty_paras(hwp):
    """빈 Para 제거"""
    removed_count = 0

    # 뒤에서부터 제거 (인덱스 변화 방지)
    paras = find_all_paras(hwp)

    for i in range(len(paras) - 1, -1, -1):
        if paras[i]['is_empty']:
            # Para로 이동
            hwp.MovePos(4)  # MoveDocBegin

            for _ in range(i):
                hwp.MovePos(14)  # MoveNextPara

            # Para 선택 및 삭제
            hwp.Run("Select")
            hwp.HAction.Run("Delete")

            removed_count += 1

    return removed_count


def reduce_margins(hwp, margin_mm: float = 8.0):
    """여백 축소"""
    hwp.HAction.GetDefault('PageSetup', hwp.HParameterSet.HSecDef.HSet)
    sec_def = hwp.HParameterSet.HSecDef

    # 현재 여백
    current_left = sec_def.PageDef.LeftMargin
    current_top = sec_def.PageDef.TopMargin

    # 새 여백 설정
    new_margin = mili_to_hwp_unit(margin_mm)
    sec_def.PageDef.LeftMargin = new_margin
    sec_def.PageDef.RightMargin = new_margin
    sec_def.PageDef.TopMargin = new_margin
    sec_def.PageDef.BottomMargin = new_margin
    sec_def.HSet.SetItem("ApplyClass", 24)
    sec_def.HSet.SetItem("ApplyTo", 3)

    hwp.HAction.Execute("PageSetup", sec_def.HSet)
    time.sleep(0.2)

    print(f'  여백: {hwp_to_mm(current_left):.1f}mm → {margin_mm}mm')

    return current_left, new_margin


def reduce_line_spacing(hwp, reduction_percent: float = 0.85):
    """줄 간격 축소 (전체 문서)"""
    # 전체 선택
    hwp.Run("SelectAll")

    # ParaShape 가져오기
    hwp.HAction.GetDefault('ParaShape', hwp.HParameterSet.HParaShape.HSet)
    para_shape = hwp.HParameterSet.HParaShape

    # 현재 줄 간격
    current_spacing = para_shape.LineSpacing
    new_spacing = int(current_spacing * reduction_percent)

    # 새 줄 간격 설정
    para_shape.LineSpacing = new_spacing

    result = hwp.HAction.Execute('ParaShape', para_shape.HSet)
    time.sleep(0.2)

    # 선택 해제
    hwp.Run("Cancel")

    print(f'  줄 간격: {current_spacing} → {new_spacing} (약 {reduction_percent*100:.0f}%)')

    return current_spacing, new_spacing


def reduce_font_size(hwp, reduction_percent: float = 0.80):
    """폰트 크기 축소 (전체 문서)"""
    # 전체 선택
    hwp.Run("SelectAll")

    # CharShape 가져오기
    hwp.HAction.GetDefault('CharShape', hwp.HParameterSet.HCharShape.HSet)
    char_shape = hwp.HParameterSet.HCharShape

    # 현재 폰트 크기
    current_size = char_shape.Height
    new_size = int(current_size * reduction_percent)

    # 새 폰트 크기 설정
    char_shape.Height = new_size

    result = hwp.HAction.Execute('CharShape', char_shape.HSet)
    time.sleep(0.2)

    # 선택 해제
    hwp.Run("Cancel")

    print(f'  폰트 크기: {current_size} → {new_size} (약 {reduction_percent*100:.0f}%)')

    return current_size, new_size


def merge_to_single_page(file_path: Path, output_path: Path = None):
    """
    2페이지 이상의 파일을 1페이지로 병합

    Args:
        file_path: 원본 파일 경로
        output_path: 저장 경로 (None이면 '_1page' 접미사 추가)

    Returns:
        성공 여부, 원래 페이지 수, 최종 페이지 수
    """
    client = AutomationClient()
    hwp = client.hwp

    try:
        # 보안 모듈
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

        # 창 숨기기
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # 절대 경로로 변환
        abs_path = file_path.resolve()

        # 문서 열기
        print(f'\n파일 열기: {file_path.name}')
        result = client.open_document(str(abs_path))
        if result.success is False:
            print(f'  ❌ 열기 실패: {result.error}')
            return False, 0, 0

        time.sleep(0.3)

        # 초기 페이지 수
        initial_pages = hwp.PageCount
        print(f'  초기 페이지 수: {initial_pages}')

        if initial_pages <= 1:
            print(f'  ✅ 이미 1페이지입니다')
            client.close_document()
            return True, initial_pages, initial_pages

        # 전략 1: 여백 축소
        print(f'\n[1/3] 여백 축소...')
        reduce_margins(hwp, margin_mm=8.0)
        print(f'  페이지 수: {hwp.PageCount}')

        # 전략 2: 줄 간격 축소
        if hwp.PageCount > 1:
            print(f'\n[2/3] 줄 간격 축소...')
            reduce_line_spacing(hwp, reduction_percent=0.85)
            print(f'  페이지 수: {hwp.PageCount}')

        # 전략 3: 폰트 크기 축소
        if hwp.PageCount > 1:
            print(f'\n[3/3] 폰트 크기 축소...')
            reduce_font_size(hwp, reduction_percent=0.80)
            print(f'  페이지 수: {hwp.PageCount}')

        final_pages = hwp.PageCount

        # 결과 출력
        print(f'\n{"="*50}')
        print(f'결과: {initial_pages} 페이지 → {final_pages} 페이지')

        if final_pages == 1:
            print(f'✅ 성공: 1페이지로 병합 완료')
        else:
            print(f'⚠️  여전히 {final_pages} 페이지입니다')

        # 저장
        if output_path is None:
            output_path = file_path.parent / f'{file_path.stem}_1page.hwp'

        print(f'\n저장: {output_path.name}')
        hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        # 닫기
        client.close_document()

        return True, initial_pages, final_pages

    except Exception as e:
        print(f'❌ 에러: {e}')
        import traceback
        traceback.print_exc()
        client.close_document()
        return False, 0, 0

    finally:
        client.cleanup()


def test_sample_file():
    """샘플 파일로 테스트"""

    # 테스트 파일 찾기
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")

    if not problem_dir.exists():
        print(f'❌ 디렉토리가 없습니다: {problem_dir}')
        return

    all_files = sorted(problem_dir.glob("*.hwp"))

    if len(all_files) < 4:
        print(f'❌ 파일이 충분하지 않습니다: {len(all_files)}개')
        return

    # 4번째 파일 (이전에 2페이지로 확인된 파일)
    test_file = all_files[3]

    print('=' * 70)
    print('2페이지 → 1페이지 병합 테스트')
    print('=' * 70)

    success, initial, final = merge_to_single_page(test_file)

    if success:
        print('\n' + '=' * 70)
        print('테스트 완료!')
        print('=' * 70)
    else:
        print('\n❌ 테스트 실패')


if __name__ == "__main__":
    test_sample_file()
