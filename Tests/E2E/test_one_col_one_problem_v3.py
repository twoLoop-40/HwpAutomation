"""
OneColOneProblem 워크플로우 v3 (최종 - DeleteBack 제거)

핵심 개선:
1. DeleteBack 제거 (시간 소요 문제)
2. 단순 워크플로우: 칼럼 체크 → 1단 변환 → 복사/붙여넣기
3. 40개 파일 전체 테스트

워크플로우:
1. 칼럼 체크 → 1단 변환
2. 복사 → 붙여넣기 → BreakColumn
"""

import sys
import time
import csv
from pathlib import Path
from typing import Optional, List

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


def get_column_count(hwp) -> int:
    """칼럼 개수 확인"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)
        col_def = hwp.HParameterSet.HColDef
        return col_def.Count
    except:
        return 1


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


# Para 스캔 및 제거 기능 제거 (시간 소요 문제로 DeleteBack 사용 안 함)


def process_problem_file(
    source_client: AutomationClient,
    file_path: Path
) -> Optional[dict]:
    """
    문제 파일 처리 (v3 - 단순화)

    Returns:
        처리 정보 또는 None (실패 시)
    """
    hwp = source_client.hwp

    print(f'\n파일 처리: {file_path.name}')

    # 1. 파일 열기
    result = source_client.open_document(str(file_path.absolute()))
    if not result.success:
        print(f'  ❌ 열기 실패: {result.error}')
        return None

    time.sleep(0.2)

    # 2. 칼럼 수 확인
    column_count = get_column_count(hwp)
    print(f'  칼럼 수: {column_count}')

    # 3. 2단 이상이면 1단으로 변환
    if column_count > 1:
        print(f'  1단으로 변환 중...')
        if not convert_to_single_column(hwp):
            print(f'  ❌ 1단 변환 실패')
            source_client.close_document()
            return None
        print(f'  ✅ 1단 변환 완료')

    # 4. 페이지 수 확인
    page_count = hwp.PageCount
    print(f'  최종 페이지: {page_count}')

    return {
        'file': file_path.name,
        'columns': column_count,
        'pages': page_count
    }


def copy_template(template_path: Path, output_path: Path) -> bool:
    """양식 파일 복사"""
    try:
        import shutil
        import time

        # 파일이 존재하면 삭제 시도 (여러 번)
        if output_path.exists():
            for attempt in range(5):
                try:
                    output_path.unlink()
                    break
                except PermissionError:
                    if attempt < 4:
                        time.sleep(1)
                    else:
                        raise

        shutil.copy2(template_path, output_path)
        return True
    except Exception as e:
        print(f'❌ 양식 복사 실패: {e}')
        return False


def load_problem_files_from_csv(csv_path: Path, problem_dir: Path) -> List[Path]:
    """CSV에서 문제 파일 목록 로드 (origin_num 순서)"""

    if not csv_path.exists():
        print(f'⚠️  CSV 파일 없음, 디렉토리 전체 파일 사용')
        all_files = sorted(problem_dir.glob("*.hwp"))
        return [
            f for f in all_files
            if '문항원본' not in f.name and '문항합본' not in f.name and not f.name.startswith('~')
        ]

    # CSV 읽기
    files_ordered = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_name = row['file_name']
            file_path = problem_dir / file_name
            if file_path.exists():
                files_ordered.append(file_path)

    return files_ordered


def run_workflow_v3(
    template_path: Path,
    problem_files: List[Path],
    output_path: Path
) -> bool:
    """OneColOneProblem 워크플로우 v3 실행 (40개 파일)"""

    print('=' * 70)
    print('OneColOneProblem 워크플로우 v3 (40개 파일)')
    print('=' * 70)
    print(f'템플릿: {template_path.name}')
    print(f'문제 파일: {len(problem_files)}개')
    print(f'출력: {output_path.name}')

    # 1. 양식 복사
    print(f'\n[1/3] 양식 복사...')
    if not copy_template(template_path, output_path):
        return False
    print(f'  ✅ 복사 완료')

    # 2. 각 문제 파일 처리
    print(f'\n[2/3] 문제 파일 처리 (총 {len(problem_files)}개)...')

    source_client = AutomationClient()
    target_client = AutomationClient()

    source_hwp = source_client.hwp
    target_hwp = target_client.hwp

    try:
        # 보안 모듈
        source_hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        target_hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

        # 창 숨기기
        try:
            source_hwp.XHwpWindows.Item(0).Visible = False
            target_hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # 대상 문서 열기
        result = target_client.open_document(str(output_path.absolute()))
        if not result.success:
            print(f'  ❌ 대상 문서 열기 실패: {result.error}')
            return False

        time.sleep(0.2)

        # 양식 파일은 이미 레이아웃이 설정되어 있으므로 건드리지 않음
        # (양식 파일이 A3 등 다른 크기일 수 있음)
        print(f'\n  양식 파일 사용 (기존 레이아웃 유지)...')

        # 본문 시작 위치로 이동 (헤더 건너뛰기)
        print(f'  본문 영역으로 이동...')
        target_hwp.Run("MoveDocBegin")  # 문서 시작으로 이동
        time.sleep(0.05)
        target_hwp.Run("MoveParaBegin")  # 첫 번째 Para 시작으로
        time.sleep(0.05)

        # 각 문제 파일 처리
        processed_count = 0

        for idx, problem_file in enumerate(problem_files):
            print(f'\n--- {idx+1}/{len(problem_files)} ---')

            # 소스 파일 처리
            info = process_problem_file(source_client, problem_file)

            if info is None:
                print(f'  ⚠️  건너뜀: {problem_file.name}')
                continue

            # 전체 선택 및 복사
            source_hwp.Run("SelectAll")
            time.sleep(0.1)
            source_hwp.Run("Copy")
            time.sleep(0.1)
            source_hwp.Run("Cancel")

            # 소스 닫기
            source_client.close_document()

            # 대상에 붙여넣기
            target_hwp.Run("Paste")
            time.sleep(0.2)

            # 마지막 파일이 아니면 BreakColumn
            if idx < len(problem_files) - 1:
                target_hwp.HAction.Run("BreakColumn")
                time.sleep(0.2)
                print(f'  ✅ 삽입 완료 (BreakColumn)')
            else:
                print(f'  ✅ 삽입 완료 (마지막)')

            processed_count += 1

        # 3. 결과 저장
        print(f'\n[3/3] 결과 저장...')
        final_pages = target_hwp.PageCount
        print(f'  최종 페이지 수: {final_pages}')

        target_hwp.Save()
        time.sleep(0.3)

        print(f'✅ 저장 완료')

        # 정리
        target_client.close_document()

        # 결과 요약
        print(f'\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'처리된 문제: {processed_count}/{len(problem_files)}개')
        print(f'최종 페이지: {final_pages}')
        print(f'출력 파일: {output_path}')

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'파일 크기: {file_size:,} bytes')

        print('=' * 70)

        return True

    except Exception as e:
        print(f'❌ 에러 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        source_client.close_document()
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()


if __name__ == "__main__":
    # 테스트 설정
    template_path = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    csv_path = problem_dir / "problem_files.csv"
    output_path = Path("Tests/E2E/결과_OneColOneProblem_v3_40개.hwp")

    # CSV에서 파일 목록 로드 (또는 전체 파일)
    problem_files = load_problem_files_from_csv(csv_path, problem_dir)

    print(f'\n로드된 파일: {len(problem_files)}개')

    if len(problem_files) == 0:
        print('❌ 문제 파일이 없습니다')
    else:
        # 워크플로우 실행
        success = run_workflow_v3(template_path, problem_files, output_path)

        if success:
            print('\n✅ 워크플로우 완료!')
        else:
            print('\n❌ 워크플로우 실패')
