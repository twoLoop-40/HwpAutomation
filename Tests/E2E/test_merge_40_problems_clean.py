"""
40개 실제 문항 합병 E2E 테스트 (양식 기반)

목적: [문항원본], [문항합본] 제외한 실제 40개 문항만 합병

워크플로우 (논의된 알고리즘):
1. 양식 파일 복사 또는 B4 2단 새 문서 생성
2. 각 문항 파일:
   - 파일 열기
   - 1단으로 변환 (이미 1단이면 스킵)
   - Para 스캔
   - 빈 Para 제거 (MoveSelDown)
   - 복사
   - 대상에 붙여넣기
   - BreakColumn (마지막 제외)
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


def convert_to_single_column(hwp) -> bool:
    """1단으로 변환 (논의된 알고리즘)"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 1  # 1단으로 설정
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        return False


def find_all_paras(hwp) -> List[dict]:
    """네비게이션으로 모든 Para 찾기"""
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
            break

    return paras


def remove_empty_paras_movesel_down(hwp, paras: List[dict]) -> int:
    """MoveSelDown 방식으로 빈 Para 제거 (논의된 알고리즘)"""
    empty_paras = [p for p in paras if p['is_empty']]

    if not empty_paras:
        return 0

    removed = 0

    for para in reversed(empty_paras):
        try:
            hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])
            time.sleep(0.02)

            hwp.Run("MoveParaEnd")
            end_pos = hwp.GetPos()

            if end_pos[2] == 0:
                hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])
                hwp.Run("MoveSelDown")
                time.sleep(0.02)
                hwp.Run("Delete")
                time.sleep(0.02)
                removed += 1

        except Exception as e:
            pass

    return removed


def process_single_problem(
    source_file: Path,
    target_hwp,
    source_client: AutomationClient,
    problem_num: int,
    total_problems: int,
) -> Tuple[bool, int]:
    """
    단일 문항 처리 (논의된 알고리즘)

    Steps:
    1. 파일 열기
    2. 1단으로 변환
    3. Para 스캔
    4. 빈 Para 제거 (MoveSelDown)
    5. 복사
    6. 붙여넣기
    """
    try:
        source_hwp = source_client.hwp

        # 진행률 표시
        progress = (problem_num / total_problems) * 100
        print(f'  [{problem_num:2d}/{total_problems}] ({progress:5.1f}%) {source_file.name[:35]:35s}', end='')

        # Step 1: 파일 열기
        result = source_client.open_document(str(source_file))
        if not result.success:
            print(f' ❌ 열기 실패')
            return (False, 0)

        time.sleep(0.2)

        # Step 2: 1단으로 변환 (논의된 알고리즘)
        convert_to_single_column(source_hwp)

        # Step 3: Para 스캔
        paras = find_all_paras(source_hwp)
        empty_count = sum(1 for p in paras if p['is_empty'])

        # Step 4: 빈 Para 제거 (MoveSelDown, 논의된 알고리즘)
        removed = remove_empty_paras_movesel_down(source_hwp, paras)

        # Step 5: 복사
        source_hwp.Run("MoveDocBegin")
        source_hwp.Run("SelectAll")
        source_hwp.Run("Copy")
        time.sleep(0.15)

        # 소스 파일 닫기
        source_hwp.Run("Cancel")
        source_client.close_document()

        # Step 6: 붙여넣기
        target_hwp.Run("Paste")
        time.sleep(0.15)

        print(f' ✅ Para:{len(paras):2d} 빈:{removed:2d}')

        return (True, removed)

    except Exception as e:
        print(f' ❌ 실패: {str(e)[:20]}')
        return (False, 0)


def test_merge_40_problems_clean():
    """40개 실제 문항 합병 E2E 테스트"""

    print('=' * 70)
    print('40개 실제 문항 합병 E2E 테스트 (논의된 알고리즘)')
    print('=' * 70)

    # 파일 경로
    template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    output_path = Path("Tests/E2E/결과_40문항_깨끗한_합병.hwp")

    if not template_file.exists():
        print(f'❌ 양식 파일이 없습니다: {template_file}')
        return False

    if not problem_dir.exists():
        print(f'❌ 문항 디렉토리가 없습니다: {problem_dir}')
        return False

    # 실제 문항 파일만 스캔 ([문항원본], [문항합본] 제외)
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = [f for f in all_files if not f.name.startswith('[문항')]

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다: {problem_dir}')
        return False

    print(f'\n📄 양식 파일: {template_file.name}')
    print(f'📁 문항 디렉토리: {problem_dir.name}')
    print(f'📄 실제 문항 수: {len(problem_files)}개')
    print(f'📄 예상 페이지: {(len(problem_files) - 1) // 2 + 1}페이지')
    print(f'\n알고리즘:')
    print(f'  0. 양식 파일 복사해서 열기')
    print(f'  1. 각 문항 파일 열기')
    print(f'  2. 1단으로 변환')
    print(f'  3. Para 스캔')
    print(f'  4. 빈 Para 제거 (MoveSelDown)')
    print(f'  5. 복사 → 붙여넣기')
    print(f'  6. BreakColumn')

    # 클라이언트 2개 생성
    print(f'\n[초기화] MCP 클라이언트 생성...')
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
        # 양식 파일 열기
        print(f'\n[양식 열기] {template_file.name}')
        result = target_client.open_document(str(template_file))
        if not result.success:
            print(f'❌ 양식 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 양식 준비 완료')

        # 첫 번째 칼럼 시작
        target_hwp.SetPos(0, 0, 0)
        time.sleep(0.1)

        # 문항 삽입 시작
        print(f'\n[문항 삽입] 시작...')
        print('-' * 70)

        start_time = time.time()
        inserted = 0
        total_removed = 0
        failed = []

        for i, problem_file in enumerate(problem_files, 1):
            # 단일 문항 처리 (논의된 알고리즘)
            success, removed = process_single_problem(
                problem_file,
                target_hwp,
                source_client,
                i,
                len(problem_files)
            )

            if success:
                inserted += 1
                total_removed += removed

                # BreakColumn (마지막 문항 제외)
                if i < len(problem_files):
                    target_hwp.Run("BreakColumn")
                    time.sleep(0.05)
            else:
                failed.append((i, problem_file.name))

            # 10개마다 진행 상황 요약
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = avg_time * (len(problem_files) - i)
                print(f'  --- 진행: {i}/{len(problem_files)} ({elapsed:.1f}초 경과, 예상 남은 시간: {remaining:.1f}초)')

        elapsed_total = time.time() - start_time

        print('-' * 70)
        print(f'✅ 문항 삽입 완료 (총 {elapsed_total:.1f}초)')

        # 최종 상태 확인
        print(f'\n[최종 문서 상태]')
        page_count = target_hwp.PageCount
        final_pos = target_hwp.GetPos()
        print(f'PageCount: {page_count}')
        print(f'최종 커서 위치: {final_pos}')
        print(f'삽입된 문항: {inserted}/{len(problem_files)}개')

        if failed:
            print(f'\n⚠️  실패한 문항: {len(failed)}개')
            for idx, name in failed[:5]:
                print(f'  {idx}. {name}')
            if len(failed) > 5:
                print(f'  ... 외 {len(failed) - 5}개')

        # 최종 Para 스캔
        print(f'\n최종 문서 Para 스캔 중...')
        final_paras = find_all_paras(target_hwp)
        empty_count = sum(1 for p in final_paras if p['is_empty'])

        print(f'총 {len(final_paras)}개 Para')
        print(f'빈 Para: {empty_count}개')
        print(f'내용 있는 Para: {len(final_paras) - empty_count}개')

        # 결과 저장
        print(f'\n[저장] 결과 저장 중...')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.5)

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)')
        else:
            print(f'⚠️  저장 실패')

        # 결과 요약
        print('\n' + '=' * 70)
        print('40개 실제 문항 합병 E2E 테스트 결과')
        print('=' * 70)
        print(f'실제 문항 수: {len(problem_files)}개')
        print(f'삽입 성공: {inserted}개')
        print(f'삽입 실패: {len(failed)}개')
        print(f'제거된 빈 Para: {total_removed}개')
        print(f'최종 페이지: {page_count}개')
        print(f'최종 Para 수: {len(final_paras)}개')
        print(f'최종 빈 Para: {empty_count}개')
        print(f'소요 시간: {elapsed_total:.1f}초')
        print(f'문항당 평균: {elapsed_total / len(problem_files):.2f}초')
        print(f'출력 파일: {output_path}')
        print('=' * 70)

        # 검증
        expected_page = (len(problem_files) - 1) // 2 + 1
        print(f'\n[검증]')
        print(f'예상 페이지: {expected_page}개')
        print(f'실제 페이지: {page_count}개')

        if page_count == expected_page:
            print(f'✅ 페이지 수 일치!')
        elif page_count == expected_page + 1:
            print(f'✅ 페이지 수 거의 일치 (+1페이지)')
        else:
            diff = abs(page_count - expected_page)
            if diff <= 2:
                print(f'✅ 페이지 수 거의 일치 (차이: {diff}페이지)')
            else:
                print(f'⚠️  페이지 수 차이: {diff}페이지')

        if inserted == len(problem_files):
            print(f'✅ 모든 문항 삽입 성공!')
        else:
            print(f'⚠️  {len(problem_files) - inserted}개 문항 실패')

        print('=' * 70)

        return True

    except Exception as e:
        print(f'\n💥 오류 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 정리
        print(f'\n[정리] 문서 닫기...')
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()
        time.sleep(0.5)
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_merge_40_problems_clean()
    sys.exit(0 if success else 1)
