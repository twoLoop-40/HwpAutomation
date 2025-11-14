"""
파일 페이지 정보 분석 테스트

목적:
1. PageCount로 페이지 수 확인
2. 페이지 설정 정보 조회
3. 칼럼 설정 정보 조회
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


def hwp_to_mm(hwp_unit: int) -> float:
    """HWP 단위를 밀리미터로 변환"""
    return hwp_unit / 283.465


def analyze_page_info(file_path: Path):
    """파일의 페이지 정보 분석"""

    print('=' * 70)
    print('파일 페이지 정보 분석')
    print('=' * 70)

    if not file_path.exists():
        print(f'❌ 파일이 없습니다: {file_path}')
        return

    print(f'\n[1/4] 파일 열기: {file_path.name}')

    client = AutomationClient()
    hwp = client.hwp

    # 보안 모듈
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

    # 창 숨기기
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    result = client.open_document(str(file_path))
    if not result.success:
        print(f'❌ 파일 열기 실패: {result.error}')
        return

    time.sleep(0.3)
    print('✅ 파일 열기 완료')

    try:
        # 1. PageCount 속성
        print(f'\n[2/4] 페이지 정보 수집...')
        page_count = hwp.PageCount
        print(f'PageCount: {page_count} 페이지')

        # 2. Para 수 계산
        hwp.Run('MoveDocBegin')
        time.sleep(0.05)

        para_count = 0
        while True:
            before_pos = hwp.GetPos()
            hwp.Run('MoveNextParaBegin')
            time.sleep(0.02)
            after_pos = hwp.GetPos()

            if after_pos == before_pos:
                break

            para_count += 1
            if para_count > 100:
                print('  (100개 Para 제한)')
                break

        print(f'Para 수: {para_count}개')

        # 3. 페이지 설정 정보
        print(f'\n[3/4] 페이지 설정 정보...')
        try:
            hwp.HAction.GetDefault('PageSetup', hwp.HParameterSet.HSecDef.HSet)
            sec_def = hwp.HParameterSet.HSecDef

            paper_width = sec_def.PageDef.PaperWidth
            paper_height = sec_def.PageDef.PaperHeight
            left_margin = sec_def.PageDef.LeftMargin
            right_margin = sec_def.PageDef.RightMargin
            top_margin = sec_def.PageDef.TopMargin
            bottom_margin = sec_def.PageDef.BottomMargin

            print(f'  용지 크기: {hwp_to_mm(paper_width):.1f}mm x {hwp_to_mm(paper_height):.1f}mm')
            print(f'  왼쪽 여백: {hwp_to_mm(left_margin):.1f}mm')
            print(f'  오른쪽 여백: {hwp_to_mm(right_margin):.1f}mm')
            print(f'  위쪽 여백: {hwp_to_mm(top_margin):.1f}mm')
            print(f'  아래쪽 여백: {hwp_to_mm(bottom_margin):.1f}mm')

        except Exception as e:
            print(f'  ❌ PageSetup 정보 조회 실패: {e}')

        # 4. 칼럼 설정 정보
        print(f'\n[4/4] 칼럼 설정 정보...')
        try:
            hwp.HAction.GetDefault('MultiColumn', hwp.HParameterSet.HColDef.HSet)
            col_def = hwp.HParameterSet.HColDef

            col_count = col_def.Count
            same_gap = col_def.SameGap

            print(f'  칼럼 수: {col_count}개')
            print(f'  칼럼 간격: {hwp_to_mm(same_gap):.1f}mm')

        except Exception as e:
            print(f'  ❌ MultiColumn 정보 조회 실패: {e}')

        # 요약
        print(f'\n' + '=' * 70)
        print('분석 결과 요약')
        print('=' * 70)
        print(f'파일명: {file_path.name}')
        print(f'페이지 수: {page_count}')
        print(f'Para 수: {para_count}')
        print('=' * 70)

    finally:
        # 정리
        client.close_document()
        client.cleanup()


if __name__ == "__main__":
    # 파일 직접 지정 (리스트 4번째 파일)
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    all_files = sorted(problem_dir.glob("*.hwp"))

    # 리스트에서 4번째 파일 사용 (인덱스 3)
    # 2025 커팅 S_공수2_기말_4회차_2_3_15.hwp
    test_file = all_files[3]

    print(f'선택한 파일: {test_file.name}\n')
    analyze_page_info(test_file)
