"""
2페이지 이상의 파일을 1페이지로 병합

전략:
1. 폰트 크기 축소 (CharShape)
2. 줄 간격 축소 (ParaShape)
3. 여백 축소 (PageDef)
4. 빈 Para 제거
"""

import sys
import codecs
from pathlib import Path

# UTF-8 설정 (Windows)
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.action_table.client import ActionTableClient


def mili_to_hwp_unit(mm: float) -> int:
    """밀리미터를 HWPUNIT으로 변환 (1mm = 283.465 HWPUNIT)"""
    return int(mm * 283.465)


def hwp_unit_to_mili(hwp_unit: int) -> float:
    """HWPUNIT을 밀리미터로 변환"""
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
            # Para 선택 후 삭제
            hwp.MovePos(4)  # MoveDocBegin
            for _ in range(i):
                hwp.MovePos(13)  # MoveParaEnd
                hwp.MovePos(14)  # MoveNextPara

            # Para 전체 선택
            hwp.Run("SelectAll")
            hwp.Run("Delete")

            removed_count += 1

    return removed_count


def reduce_font_size(hwp, reduction_percent: float = 0.85):
    """
    모든 텍스트의 폰트 크기 축소

    Args:
        reduction_percent: 축소 비율 (0.85 = 85%)
    """
    # 전체 선택
    hwp.Run("SelectAll")

    # CharShape 가져오기
    h_action = hwp.CreateAction("CharShape")
    h_set = h_action.CreateSet()
    h_action.GetDefault(h_set)

    # 현재 폰트 크기 가져오기
    current_size = h_set.Item("Height")
    new_size = int(current_size * reduction_percent)

    # 새 폰트 크기 설정
    h_set.SetItem("Height", new_size)
    h_action.Execute(h_set)

    # 선택 해제
    hwp.Run("Cancel")

    print(f'  폰트 크기: {current_size} → {new_size} (약 {reduction_percent*100:.0f}%)')

    return current_size, new_size


def reduce_line_spacing(hwp, reduction_percent: float = 0.9):
    """
    줄 간격 축소

    Args:
        reduction_percent: 축소 비율 (0.9 = 90%)
    """
    # 전체 선택
    hwp.Run("SelectAll")

    # ParaShape 가져오기
    h_action = hwp.CreateAction("ParaShape")
    h_set = h_action.CreateSet()
    h_action.GetDefault(h_set)

    # 현재 줄 간격
    current_spacing = h_set.Item("LineSpacing")
    new_spacing = int(current_spacing * reduction_percent)

    # 새 줄 간격 설정
    h_set.SetItem("LineSpacing", new_spacing)
    h_action.Execute(h_set)

    # 선택 해제
    hwp.Run("Cancel")

    print(f'  줄 간격: {current_spacing} → {new_spacing} (약 {reduction_percent*100:.0f}%)')

    return current_spacing, new_spacing


def reduce_margins(hwp, margin_mm: float = 8.0):
    """
    여백 축소

    Args:
        margin_mm: 여백 크기 (밀리미터)
    """
    # SecDef 액션
    h_action = hwp.CreateAction("PageSetup")
    h_set = h_action.CreateSet()
    h_action.GetDefault(h_set)

    # PageDef 가져오기
    page_def = h_set.Item("PageDef")

    # 현재 여백
    current_left = page_def.Item("LeftMargin")
    current_right = page_def.Item("RightMargin")
    current_top = page_def.Item("TopMargin")
    current_bottom = page_def.Item("BottomMargin")

    # 새 여백 설정
    new_margin = mili_to_hwp_unit(margin_mm)
    page_def.SetItem("LeftMargin", new_margin)
    page_def.SetItem("RightMargin", new_margin)
    page_def.SetItem("TopMargin", new_margin)
    page_def.SetItem("BottomMargin", new_margin)

    # 적용
    h_set.SetItem("ApplyTo", 1)  # 현재 섹션
    h_action.Execute(h_set)

    print(f'  여백: {hwp_unit_to_mili(current_left):.1f}mm → {margin_mm}mm')

    return current_left, new_margin


def merge_to_single_page(file_path: Path, output_path: Path = None):
    """
    2페이지 이상의 파일을 1페이지로 병합

    Args:
        file_path: 원본 파일 경로
        output_path: 저장 경로 (None이면 '_1page' 접미사 추가)

    Returns:
        성공 여부, 원래 페이지 수, 최종 페이지 수
    """
    client = ActionTableClient()

    try:
        # 절대 경로로 변환
        abs_path = file_path.resolve()

        # 문서 열기
        print(f'\n파일 열기: {file_path.name}')
        print(f'  경로: {abs_path}')
        result = client.open_document(str(abs_path))
        if result.success is False:
            print(f'  ❌ 열기 실패: {result.error}')
            return False, 0, 0

        hwp = client.hwp

        # 초기 페이지 수
        initial_pages = hwp.PageCount
        print(f'  초기 페이지 수: {initial_pages}')

        if initial_pages <= 1:
            print(f'  ✅ 이미 1페이지입니다')
            client.close_document()
            return True, initial_pages, initial_pages

        # 전략 1: 빈 Para 제거
        print(f'\n[1/4] 빈 Para 제거...')
        removed = remove_empty_paras(hwp)
        print(f'  제거된 빈 Para: {removed}개')
        print(f'  페이지 수: {hwp.PageCount}')

        # 전략 2: 여백 축소
        print(f'\n[2/4] 여백 축소...')
        reduce_margins(hwp, margin_mm=8.0)
        print(f'  페이지 수: {hwp.PageCount}')

        # 전략 3: 줄 간격 축소
        if hwp.PageCount > 1:
            print(f'\n[3/4] 줄 간격 축소...')
            reduce_line_spacing(hwp, reduction_percent=0.85)
            print(f'  페이지 수: {hwp.PageCount}')

        # 전략 4: 폰트 크기 축소
        if hwp.PageCount > 1:
            print(f'\n[4/4] 폰트 크기 축소...')
            reduce_font_size(hwp, reduction_percent=0.8)
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
        client.save_document(str(output_path))

        # 닫기
        client.close_document()

        return True, initial_pages, final_pages

    except Exception as e:
        print(f'❌ 에러: {e}')
        import traceback
        traceback.print_exc()
        client.close_document()
        return False, 0, 0


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
