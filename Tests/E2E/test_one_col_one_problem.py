"""
OneColOneProblem 워크플로우 구현
Schema/OneColOneProblemLogic.md + HwpIdris/OneColOneProblem.idr 기반

워크플로우:
1. 양식 파일 복사
2. 소스 파일 열기
3. 단 개수 확인 (2 이상이면 1단으로 변환)
4. Para 스캔
5. 빈 Para 제거
6. 페이지 수 확인 (2 이상이면 빈 Para 제거하여 1페이지로 만들기)
7. 대상에 복사
8. 다음 파일이 있으면 BreakColumn 후 반복
9. 저장 및 종료
"""

import sys
import time
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


@dataclass
class ParaInfo:
    """Para 정보 (Idris2 spec 기반)"""
    index: int
    is_empty: bool
    start_pos: Tuple[int, int, int]  # List, Para, Pos
    end_pos: Tuple[int, int, int]


@dataclass
class ProblemFileInfo:
    """문제 파일 정보"""
    path: str
    column_count: int
    page_count: int
    paras: List[ParaInfo]
    empty_para_count: int


def mili_to_hwp_unit(mili: float) -> int:
    """밀리미터를 HWP 단위로 변환"""
    return int(mili * 283.465)


def copy_template(template_path: Path, output_path: Path) -> bool:
    """양식 파일 복사"""
    try:
        shutil.copy2(template_path, output_path)
        return True
    except Exception as e:
        print(f'  ❌ 양식 복사 실패: {e}')
        return False


def get_column_count(hwp) -> int:
    """현재 문서의 칼럼 수 확인"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)
        col_def = hwp.HParameterSet.HColDef
        return col_def.Count
    except:
        return 1  # 기본 1단


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


def scan_paras(hwp) -> List[ParaInfo]:
    """Para 스캔 (Idris2 spec 기반)"""
    paras = []

    hwp.Run('MoveDocBegin')
    time.sleep(0.05)

    para_idx = 0

    while para_idx < 1000:  # 안전 장치
        start_pos = hwp.GetPos()

        # Para 끝으로 이동
        hwp.Run('MoveParaEnd')
        time.sleep(0.02)

        end_pos = hwp.GetPos()

        # Para가 비어있는지 확인: start_pos[2] == end_pos[2]
        is_empty = (end_pos[2] == 0)

        para_info = ParaInfo(
            index=para_idx,
            is_empty=is_empty,
            start_pos=start_pos,
            end_pos=end_pos
        )

        paras.append(para_info)

        # 다음 Para로 이동 시도
        old_pos = hwp.GetPos()
        hwp.Run('MoveNextPara')
        new_pos = hwp.GetPos()

        # 위치가 변하지 않았으면 마지막 Para
        if old_pos == new_pos:
            break

        para_idx += 1

    return paras


def remove_empty_paras(hwp, paras: List[ParaInfo]) -> int:
    """
    빈 Para 제거 (MoveSelLeft 활용)
    주의: 비어있지 않은 Para는 건드리지 않음

    전략: 뒤에서부터 제거하여 인덱스 변화 방지
    """
    removed_count = 0

    # 빈 Para 목록 (역순)
    empty_paras = [p for p in paras if p.is_empty]
    empty_paras.reverse()

    for para in empty_paras:
        try:
            # Para로 이동
            hwp.SetPos(*para.start_pos)
            time.sleep(0.02)

            # Para 전체 선택 (MoveSelLeft 사용)
            hwp.Run('MoveParaEnd')
            hwp.Run('MoveSelParaBegin')
            time.sleep(0.02)

            # 선택된 내용 확인 (안전 검사)
            selected = hwp.GetSelectedText()

            if not selected or selected.strip() == '':
                # 빈 Para 확인됨, 삭제
                hwp.Run('Delete')
                time.sleep(0.02)
                removed_count += 1
            else:
                # 비어있지 않음, 스킵
                hwp.Run('Cancel')

        except Exception as e:
            print(f'  ⚠️  Para {para.index} 제거 실패: {e}')
            continue

    return removed_count


def remove_empty_paras_until_one_page(hwp) -> Tuple[int, int]:
    """
    페이지가 1이 될 때까지 빈 Para 제거

    Returns:
        (제거된 Para 수, 최종 페이지 수)
    """
    removed_total = 0
    max_attempts = 50  # 최대 50개까지만 제거 시도

    while hwp.PageCount > 1 and removed_total < max_attempts:
        # Para 재스캔
        paras = scan_paras(hwp)
        empty_paras = [p for p in paras if p.is_empty]

        if not empty_paras:
            # 빈 Para가 없으면 중단
            print(f'  ⚠️  빈 Para가 없지만 아직 {hwp.PageCount}페이지입니다')
            break

        # 마지막 빈 Para 1개 제거
        removed = remove_empty_paras(hwp, [empty_paras[-1]])
        removed_total += removed

        if removed == 0:
            # 제거 실패하면 중단
            break

    final_pages = hwp.PageCount

    return removed_total, final_pages


def process_problem_file(
    source_client: AutomationClient,
    file_path: Path
) -> Optional[ProblemFileInfo]:
    """
    문제 파일 처리

    Returns:
        ProblemFileInfo 또는 None (실패 시)
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

    # 4. Para 스캔
    print(f'  Para 스캔 중...')
    paras = scan_paras(hwp)
    empty_count = sum(1 for p in paras if p.is_empty)
    print(f'  총 Para: {len(paras)}개 (빈 Para: {empty_count}개)')

    # 5. 빈 Para 제거
    if empty_count > 0:
        print(f'  빈 Para 제거 중...')
        removed = remove_empty_paras(hwp, paras)
        print(f'  제거된 빈 Para: {removed}개')

    # 6. 페이지 수 확인
    page_count = hwp.PageCount
    print(f'  페이지 수: {page_count}')

    # 7. 2페이지 이상이면 1페이지로 만들기
    if page_count > 1:
        print(f'  1페이지로 축소 중...')
        removed, final_pages = remove_empty_paras_until_one_page(hwp)
        print(f'  추가 제거된 빈 Para: {removed}개')
        print(f'  최종 페이지: {final_pages}')
        page_count = final_pages

    # Para 재스캔
    final_paras = scan_paras(hwp)

    info = ProblemFileInfo(
        path=str(file_path),
        column_count=column_count,
        page_count=page_count,
        paras=final_paras,
        empty_para_count=sum(1 for p in final_paras if p.is_empty)
    )

    return info


def run_one_col_one_problem_workflow(
    template_path: Path,
    problem_files: List[Path],
    output_path: Path
) -> bool:
    """
    OneColOneProblem 워크플로우 실행

    Args:
        template_path: 양식 파일 경로
        problem_files: 문제 파일 목록
        output_path: 출력 파일 경로

    Returns:
        성공 여부
    """
    print('=' * 70)
    print('OneColOneProblem 워크플로우')
    print('=' * 70)
    print(f'양식: {template_path.name}')
    print(f'문제 파일: {len(problem_files)}개')
    print(f'출력: {output_path.name}')

    # 1. 양식 복사
    print(f'\n[1/4] 양식 파일 복사...')
    if not copy_template(template_path, output_path):
        return False

    # 클라이언트 2개
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

        # 대상 파일 열기 (양식)
        result = target_client.open_document(str(output_path.absolute()))
        if not result.success:
            print(f'  ❌ 대상 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.2)

        # 2. 각 문제 파일 처리
        print(f'\n[2/4] 문제 파일 처리...')

        for idx, problem_file in enumerate(problem_files, 1):
            print(f'\n--- 문제 {idx}/{len(problem_files)} ---')

            # 파일 처리
            info = process_problem_file(source_client, problem_file)

            if info is None:
                print(f'  ❌ 파일 처리 실패, 스킵')
                continue

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

            print(f'  ✅ 복사 완료')

            # 마지막 파일이 아니면 BreakColumn
            if idx < len(problem_files):
                target_hwp.HAction.Run("BreakColumn")
                time.sleep(0.2)
                print(f'  ✅ 칼럼 나눔')

        # 3. 결과 확인
        print(f'\n[3/4] 결과 확인...')
        final_pages = target_hwp.PageCount
        print(f'  최종 페이지 수: {final_pages}')

        # 4. 저장
        print(f'\n[4/4] 저장...')
        target_hwp.Save()
        time.sleep(0.3)

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료 ({file_size:,} bytes)')
        else:
            print(f'⚠️  저장 실패')
            return False

        # 결과 요약
        print(f'\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'처리된 문제: {len(problem_files)}개')
        print(f'최종 페이지: {final_pages}')
        print(f'출력 파일: {output_path}')
        print('=' * 70)

        return True

    finally:
        # 정리
        source_client.close_document()
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()


def test_one_col_one_problem():
    """OneColOneProblem 워크플로우 테스트"""

    # 양식 파일
    template_path = Path("Tests/E2ETest/[양식]mad모의고사.hwp")

    if not template_path.exists():
        print(f'❌ 양식 파일이 없습니다: {template_path}')
        return

    # 문제 파일 디렉토리
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")

    if not problem_dir.exists():
        print(f'❌ 문제 디렉토리가 없습니다: {problem_dir}')
        return

    # 실제 문제 파일만
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = [
        f for f in all_files
        if '문항원본' not in f.name and '문항합본' not in f.name and not f.name.startswith('~')
    ]

    if len(problem_files) < 2:
        print(f'❌ 문제 파일이 충분하지 않습니다: {len(problem_files)}개')
        return

    # 첫 2개 파일만 테스트
    test_files = problem_files[:2]

    # 출력 파일
    output_path = Path("Tests/E2E/결과_OneColOneProblem.hwp")

    # 워크플로우 실행
    success = run_one_col_one_problem_workflow(
        template_path=template_path,
        problem_files=test_files,
        output_path=output_path
    )

    if success:
        print('\n✅ 테스트 성공!')
    else:
        print('\n❌ 테스트 실패')


if __name__ == "__main__":
    test_one_col_one_problem()
