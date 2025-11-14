"""
OneColOneProblem 워크플로우 v2

매크로 기반 개선:
1. 칼럼 체크 → 2개 이상이면 1개로 변환
2. DeleteBack으로 페이지가 1이 될 때까지 반복
"""

import sys
import time
from pathlib import Path
from typing import Optional, Tuple

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


def get_column_count(hwp) -> int:
    """칼럼 개수 확인"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)
        col_def = hwp.HParameterSet.HColDef
        return col_def.Count
    except:
        return 1


def convert_to_single_column(hwp) -> bool:
    """1단으로 변환 (MultiColumnPreset0 사용)"""
    try:
        hwp.HAction.GetDefault("MultiColumnPreset0", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 1
        col_def.SameGap = mili_to_hwp_unit(0.0)
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumnPreset0", col_def.HSet)
        time.sleep(0.1)
        return result
    except Exception as e:
        print(f'  ❌ 1단 변환 실패: {e}')
        return False


def reduce_to_one_page_by_deleteback(hwp, max_attempts: int = 100) -> Tuple[int, int]:
    """
    DeleteBack으로 페이지가 1이 될 때까지 반복

    Returns:
        (DeleteBack 실행 횟수, 최종 페이지 수)
    """
    delete_count = 0

    print(f'  초기 페이지: {hwp.PageCount}')

    for i in range(max_attempts):
        # 페이지가 1이면 중단
        if hwp.PageCount <= 1:
            print(f'  ✅ 1페이지 달성!')
            break

        # 문서 끝으로
        hwp.Run('MoveDocEnd')
        time.sleep(0.02)

        # DeleteBack 실행
        hwp.Run('DeleteBack')
        time.sleep(0.02)
        delete_count += 1

        # 10번마다 진행상황 출력
        if delete_count % 10 == 0:
            print(f'  DeleteBack {delete_count}회 → {hwp.PageCount}페이지')

    final_pages = hwp.PageCount
    return delete_count, final_pages


def process_problem_file(
    source_client: AutomationClient,
    file_path: Path
) -> Optional[Tuple[int, int]]:
    """
    문제 파일 처리 (v2)

    Returns:
        (DeleteBack 횟수, 최종 페이지) 또는 None (실패 시)
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

    # 4. DeleteBack으로 1페이지로 축소
    print(f'  DeleteBack으로 페이지 축소 시작...')
    delete_count, final_pages = reduce_to_one_page_by_deleteback(hwp, max_attempts=100)
    print(f'  DeleteBack {delete_count}회 실행')
    print(f'  최종 페이지: {final_pages}')

    return delete_count, final_pages


def copy_template(template_path: Path, output_path: Path) -> bool:
    """양식 파일 복사"""
    try:
        import shutil
        shutil.copy2(template_path, output_path)
        return True
    except Exception as e:
        print(f'❌ 양식 복사 실패: {e}')
        return False


def run_workflow_v2(
    template_path: Path,
    problem_files: list[Path],
    output_path: Path
) -> bool:
    """OneColOneProblem 워크플로우 v2 실행"""

    print('=' * 70)
    print('OneColOneProblem 워크플로우 v2')
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
    print(f'\n[2/3] 문제 파일 처리...')

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

        # 각 문제 파일 처리
        for idx, problem_file in enumerate(problem_files):
            # 소스 파일 처리 (1단 변환 + 페이지 축소)
            process_result = process_problem_file(source_client, problem_file)

            if process_result is None:
                print(f'  ⚠️  건너뜀: {problem_file.name}')
                continue

            delete_count, final_pages = process_result

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
                print(f'  ✅ 문제 {idx+1} 삽입 완료 (BreakColumn)')
            else:
                print(f'  ✅ 문제 {idx+1} 삽입 완료 (마지막)')

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
        print(f'처리된 문제: {len(problem_files)}개')
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
    output_path = Path("Tests/E2E/결과_OneColOneProblem_v2.hwp")

    # 문제 파일 찾기
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = [
        f for f in all_files
        if '문항원본' not in f.name and '문항합본' not in f.name and not f.name.startswith('~')
    ]

    if len(problem_files) < 2:
        print(f'❌ 문제 파일이 충분하지 않습니다: {len(problem_files)}개')
    else:
        # 첫 2개 문제로 테스트
        test_files = problem_files[:2]

        # 워크플로우 실행
        success = run_workflow_v2(template_path, test_files, output_path)

        if success:
            print('\n✅ 워크플로우 완료!')
        else:
            print('\n❌ 워크플로우 실패')
