"""
칼럼당 1개 문제 E2E 테스트

목적: 각 칼럼에 1개씩만 문제를 넣는 단순 테스트

워크플로우:
1. B4 2단 새 문서 생성
2. 첫 번째 문항 파일:
   - 파일 열기
   - 1단으로 변환
   - 복사
   - 대상에 붙여넣기
   - BreakColumn
3. 두 번째 문항 파일:
   - 파일 열기
   - 1단으로 변환
   - 복사
   - 대상에 붙여넣기
4. 결과 저장

기반: test_merge_40_problems_clean.py 단순화
"""

import sys
import time
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


def mili_to_hwp_unit(mili: float) -> int:
    """밀리미터를 HWP 단위로 변환"""
    return int(mili * 283.465)


def setup_b4_page(hwp) -> bool:
    """B4 페이지 설정"""
    try:
        hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)

        sec_def = hwp.HParameterSet.HSecDef
        sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)
        sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)
        sec_def.PageDef.LeftMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.RightMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.TopMargin = mili_to_hwp_unit(20.0)
        sec_def.PageDef.BottomMargin = mili_to_hwp_unit(15.0)
        sec_def.PageDef.HeaderLen = mili_to_hwp_unit(15.0)
        sec_def.PageDef.FooterLen = mili_to_hwp_unit(15.0)
        sec_def.HSet.SetItem("ApplyClass", 24)
        sec_def.HSet.SetItem("ApplyTo", 3)

        result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f'  ❌ B4 페이지 설정 실패: {e}')
        return False


def create_two_column_layout(hwp) -> bool:
    """2단 레이아웃 설정"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 2
        col_def.SameGap = mili_to_hwp_unit(8.0)
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f'  ❌ 2단 레이아웃 설정 실패: {e}')
        return False


def convert_to_single_column(hwp) -> bool:
    """1단으로 변환"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 1
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f'  ❌ 1단 변환 실패: {e}')
        return False


def merge_1_problem_per_column():
    """칼럼당 1개 문제 E2E 테스트"""

    print('=' * 70)
    print('칼럼당 1개 문제 E2E 테스트')
    print('=' * 70)

    # 테스트 문제 디렉토리
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")

    if not problem_dir.exists():
        print(f'❌ 디렉토리가 없습니다: {problem_dir}')
        return

    # 출력 파일
    output_path = Path("Tests/E2E/결과_칼럼당_1개.hwp")

    # 실제 문제 파일만 (문항원본/문항합본 제외)
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = [
        f for f in all_files
        if '문항원본' not in f.name and '문항합본' not in f.name and not f.name.startswith('~')
    ]

    if len(problem_files) < 2:
        print(f'❌ 문제 파일이 충분하지 않습니다: {len(problem_files)}개')
        return

    # 첫 2개 문제만 사용
    test_files = problem_files[:2]

    print(f'\n사용할 문제 파일:')
    for i, f in enumerate(test_files, 1):
        print(f'  {i}. {f.name}')

    # 클라이언트 2개 (원본용, 대상용)
    source_client = AutomationClient()
    target_client = AutomationClient()

    source_hwp = source_client.hwp
    target_hwp = target_client.hwp

    try:
        # 보안 모듈 등록
        source_hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        target_hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

        # 창 숨기기
        try:
            source_hwp.XHwpWindows.Item(0).Visible = False
            target_hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # [1/5] 대상 문서 준비
        print(f'\n[1/5] 대상 문서 준비 (B4 2단)...')
        target_hwp.HAction.Run("FileNew")
        time.sleep(0.2)

        if not setup_b4_page(target_hwp):
            print(f'  ❌ B4 페이지 설정 실패')
            return

        if not create_two_column_layout(target_hwp):
            print(f'  ❌ 2단 레이아웃 설정 실패')
            return

        print(f'  ✅ 대상 문서 준비 완료')

        # [2/5] 첫 번째 문제 삽입
        problem_file = test_files[0]
        print(f'\n[2/5] 첫 번째 문제 삽입: {problem_file.name}')

        # 원본 파일 열기
        result = source_client.open_document(str(problem_file.absolute()))
        if not result.success:
            print(f'  ❌ 파일 열기 실패: {result.error}')
            return

        time.sleep(0.2)

        # 1단으로 변환
        print(f'  1단으로 변환...')
        convert_to_single_column(source_hwp)

        # 전체 선택 및 복사
        source_hwp.Run("SelectAll")
        time.sleep(0.1)
        source_hwp.Run("Copy")
        time.sleep(0.1)
        source_hwp.Run("Cancel")

        # 원본 닫기
        source_client.close_document()

        # 대상에 붙여넣기
        target_hwp.Run("Paste")
        time.sleep(0.2)

        # Break Column (다음 칼럼으로)
        target_hwp.HAction.Run("BreakColumn")
        time.sleep(0.2)

        print(f'  ✅ 첫 번째 문제 삽입 완료')

        # [3/5] 두 번째 문제 삽입
        problem_file = test_files[1]
        print(f'\n[3/5] 두 번째 문제 삽입: {problem_file.name}')

        # 원본 파일 열기
        result = source_client.open_document(str(problem_file.absolute()))
        if not result.success:
            print(f'  ❌ 파일 열기 실패: {result.error}')
            return

        time.sleep(0.2)

        # 1단으로 변환
        print(f'  1단으로 변환...')
        convert_to_single_column(source_hwp)

        # 전체 선택 및 복사
        source_hwp.Run("SelectAll")
        time.sleep(0.1)
        source_hwp.Run("Copy")
        time.sleep(0.1)
        source_hwp.Run("Cancel")

        # 원본 닫기
        source_client.close_document()

        # 대상에 붙여넣기 (마지막 문제이므로 BreakColumn 없음)
        target_hwp.Run("Paste")
        time.sleep(0.2)

        print(f'  ✅ 두 번째 문제 삽입 완료')

        # [4/5] 결과 확인
        print(f'\n[4/5] 결과 확인...')
        final_pages = target_hwp.PageCount
        print(f'  최종 페이지 수: {final_pages}')

        # [5/5] 저장
        print(f'\n[5/5] 결과 저장: {output_path.name}')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))
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
        print(f'총 문제 수: 2개 (칼럼당 1개)')
        print(f'최종 페이지: {final_pages}')
        print(f'출력 파일: {output_path}')
        print('=' * 70)

    finally:
        # 정리
        source_client.close_document()
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()


if __name__ == "__main__":
    merge_1_problem_per_column()
