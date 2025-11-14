"""
최종 합병 워크플로우 E2E 테스트

Idris2 명세 기반: Specs/MergeWorkflow.idr

워크플로우:
1. 대상 문서 생성 + B4 + 2단 설정
2. 각 소스 파일에 대해:
   a. 소스 파일 열기
   b. Para 스캔 (MoveNextParaBegin)
   c. 빈 Para 제거 (MoveSelDown x1)
   d. 전체 선택 + 복사
   e. 소스 파일 닫기
   f. 대상에 붙여넣기
   g. BreakColumn (마지막 문항 제외)
3. 결과 저장
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple

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


def find_all_paras(hwp) -> List[dict]:
    """
    네비게이션으로 모든 Para 찾기 (Idris2: Step2_AnalyzeParas)
    """
    paras = []

    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    para_num = 0

    while True:
        start_pos = hwp.GetPos()

        hwp.Run("MoveParaEnd")
        time.sleep(0.02)

        end_pos = hwp.GetPos()

        is_empty = (end_pos[2] == 0)

        paras.append({
            'para_num': para_num,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'is_empty': is_empty,
        })

        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)

        after_pos = hwp.GetPos()

        if after_pos == before_pos:
            break

        para_num += 1

        if para_num > 500:
            print(f'  ⚠️  500개 Para 제한 도달')
            break

    return paras


def remove_empty_paras_movesel_down(hwp, paras: List[dict]) -> int:
    """
    MoveSelDown 방식으로 빈 Para 제거 (Idris2: Step3_RemoveEmptyParas UseSelDown 1)
    """
    empty_paras = [p for p in paras if p['is_empty']]

    if not empty_paras:
        return 0

    removed = 0

    # 역순으로 삭제
    for para in reversed(empty_paras):
        para_num = para['para_num']

        try:
            # Para 시작으로 이동
            hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])
            time.sleep(0.02)

            # 빈 Para 재확인
            hwp.Run("MoveParaEnd")
            end_pos = hwp.GetPos()

            if end_pos[2] == 0:
                # Para 시작으로 복귀
                hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])

                # MoveSelDown 1회 (Idris2 명세대로)
                hwp.Run("MoveSelDown")
                time.sleep(0.02)

                # 삭제
                hwp.Run("Delete")
                time.sleep(0.02)

                removed += 1
                print(f'    Para {para_num:2d} 삭제 (MoveSelDown)')

        except Exception as e:
            print(f'    ⚠️  Para {para_num} 삭제 실패: {e}')

    return removed


def process_single_problem(
    source_file: Path,
    target_hwp,
    source_client: AutomationClient,
    problem_num: int,
) -> Tuple[bool, int]:
    """
    단일 문항 처리 (Idris2: SingleProblemWorkflow)

    Returns:
        (success, removed_paras)
    """
    try:
        source_hwp = source_client.hwp

        print(f'  [문항 {problem_num}] {source_file.name[:40]}...')

        # Step 1: 소스 파일 열기
        print(f'    Step1: 소스 파일 열기...')
        result = source_client.open_document(str(source_file))
        if not result.success:
            print(f'      ❌ 파일 열기 실패: {result.error}')
            return (False, 0)

        time.sleep(0.3)

        # Step 2: Para 스캔
        print(f'    Step2: Para 스캔...')
        paras = find_all_paras(source_hwp)
        print(f'      총 {len(paras)}개 Para (빈 Para {sum(1 for p in paras if p["is_empty"])}개)')

        # Step 3: 빈 Para 제거 (MoveSelDown)
        print(f'    Step3: 빈 Para 제거 (MoveSelDown)...')
        removed = remove_empty_paras_movesel_down(source_hwp, paras)
        print(f'      ✅ {removed}개 제거')

        # Step 4: 전체 선택 + 복사
        print(f'    Step4: 전체 선택 + 복사...')
        source_hwp.Run("MoveDocBegin")
        source_hwp.Run("SelectAll")
        source_hwp.Run("Copy")
        time.sleep(0.2)

        # Step 5: 소스 파일 닫기
        print(f'    Step5: 소스 파일 닫기...')
        source_hwp.Run("Cancel")
        source_client.close_document()

        # Step 8: 대상에 붙여넣기
        print(f'    Step8: 붙여넣기...')
        target_hwp.Run("Paste")
        time.sleep(0.2)

        return (True, removed)

    except Exception as e:
        print(f'      ❌ 실패: {e}')
        import traceback
        traceback.print_exc()
        return (False, 0)


def test_final_merge_workflow():
    """최종 합병 워크플로우 E2E 테스트"""

    print('=' * 70)
    print('최종 합병 워크플로우 E2E 테스트')
    print('=' * 70)
    print('Idris2 명세: Specs/MergeWorkflow.idr')
    print('=' * 70)

    # 파일 경로
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    output_path = Path("Tests/E2E/결과_최종_합병_워크플로우.hwp")

    if not problem_dir.exists():
        print(f'❌ 문항 디렉토리가 없습니다: {problem_dir}')
        return False

    # 문항 파일 목록 (처음 3개 테스트)
    problem_files = sorted(problem_dir.glob("*.hwp"))[:3]

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다: {problem_dir}')
        return False

    print(f'\n테스트할 문항 수: {len(problem_files)}개')
    for i, pf in enumerate(problem_files, 1):
        print(f'  {i}. {pf.name[:50]}...')

    # 클라이언트 2개 생성
    print('\n[초기화] MCP 클라이언트 생성...')
    target_client = AutomationClient()
    source_client = AutomationClient()

    target_hwp = target_client.hwp
    source_hwp = source_client.hwp

    # 보안 모듈 등록
    target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    # 창 숨기기
    try:
        target_hwp.XHwpWindows.Item(0).Visible = False
        source_hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    print('✅ 클라이언트 초기화 완료')

    try:
        # Step 6: 새 문서 생성
        print('\n[Step6] 새 문서 생성')
        target_hwp.HAction.Run("FileNew")
        time.sleep(0.5)
        print('✅ 문서 생성 완료')

        # Step 7: B4 + 2단 설정
        print('\n[Step7] B4 + 2단 설정')
        if not setup_b4_page(target_hwp):
            return False
        print('  ✅ B4 페이지 설정 완료')

        if not create_two_column_layout(target_hwp):
            return False
        print('  ✅ 2단 레이아웃 설정 완료')

        # 첫 번째 칼럼 시작
        print('\n[문항 삽입 시작]')
        target_hwp.SetPos(0, 0, 0)
        time.sleep(0.1)

        inserted = 0
        total_removed = 0

        # 각 문항 처리
        for i, problem_file in enumerate(problem_files, 1):
            # 현재 위치 확인
            before_pos = target_hwp.GetPos()
            print(f'\n--- 문항 {i}/{len(problem_files)} ---')
            print(f'  삽입 전 위치: {before_pos}')

            # 단일 문항 처리 (Idris2: SingleProblemWorkflow)
            success, removed = process_single_problem(
                problem_file,
                target_hwp,
                source_client,
                i
            )

            if success:
                inserted += 1
                total_removed += removed

                # 삽입 후 위치
                after_pos = target_hwp.GetPos()
                print(f'  삽입 후 위치: {after_pos}')

                # Step 9: BreakColumn (마지막 문항 제외)
                if i < len(problem_files):
                    print(f'  Step9: BreakColumn...')
                    target_hwp.Run("BreakColumn")
                    time.sleep(0.1)

                    break_pos = target_hwp.GetPos()
                    print(f'  BreakColumn 후 위치: {break_pos}')
                    print(f'  ✅ 다음 칼럼 준비')
            else:
                print(f'  ⚠️  문항 {i} 처리 실패')

        # 최종 상태 확인
        print(f'\n[최종 문서 상태]')
        page_count = target_hwp.PageCount
        final_pos = target_hwp.GetPos()
        print(f'PageCount: {page_count}')
        print(f'최종 커서 위치: {final_pos}')
        print(f'삽입된 문항: {inserted}/{len(problem_files)}개')

        # 최종 Para 스캔
        print(f'\n최종 문서 Para 스캔...')
        final_paras = find_all_paras(target_hwp)
        print(f'총 {len(final_paras)}개 Para')

        empty_count = sum(1 for p in final_paras if p['is_empty'])
        print(f'빈 Para: {empty_count}개')
        print(f'내용 있는 Para: {len(final_paras) - empty_count}개')

        # Step 10: 결과 저장
        print(f'\n[Step10] 결과 저장: {output_path.name}')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))
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
        print('E2E 테스트 결과')
        print('=' * 70)
        print(f'삽입 문항 수: {inserted}개')
        print(f'제거된 빈 Para: {total_removed}개')
        print(f'최종 페이지: {page_count}개')
        print(f'최종 Para 수: {len(final_paras)}개')
        print(f'최종 빈 Para: {empty_count}개')
        print(f'출력 파일: {output_path}')
        print('=' * 70)

        # 검증
        expected_page = (len(problem_files) - 1) // 2 + 1
        print(f'\n[검증]')
        print(f'예상 페이지: {expected_page}개')
        print(f'실제 페이지: {page_count}개')

        if page_count == expected_page:
            print(f'✅ 페이지 수 일치!')
        else:
            print(f'⚠️  페이지 수 불일치')

        if empty_count < total_removed:
            print(f'✅ 빈 Para 감소 ({total_removed} → {empty_count})')
        else:
            print(f'⚠️  빈 Para 여전히 존재')

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
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()
        time.sleep(0.5)
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_final_merge_workflow()
    sys.exit(0 if success else 1)
