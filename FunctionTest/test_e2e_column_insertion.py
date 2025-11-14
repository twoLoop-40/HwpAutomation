"""
E2E 테스트: 실제 문항 파일을 칼럼별로 삽입

목적: 양식 파일에 실제 문항 HWP 파일들을 복사-붙여넣기로 삽입
      각 문항마다 BreakColumn으로 칼럼 생성

전략:
1. 양식 파일 열기
2. 각 문항 파일에 대해:
   - 문항 파일 열기
   - 전체 선택 & 복사
   - 양식 파일로 돌아와서 붙여넣기
   - BreakColumn으로 다음 칼럼 생성
3. 결과 저장
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


def copy_paste_problem(source_file: Path, target_client: AutomationClient, source_client: AutomationClient) -> bool:
    """
    문항 파일의 내용을 복사-붙여넣기로 가져오기
    """
    try:
        source_hwp = source_client.hwp
        target_hwp = target_client.hwp

        # 원본 파일 열기
        print(f'      원본 열기: {source_file.name[:30]}...')
        result = source_client.open_document(str(source_file), options="readonly:true")
        if not result.success:
            print(f'      ❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.2)

        # 원본 전체 선택
        source_hwp.Run("MoveDocBegin")
        source_hwp.Run("Select")
        source_hwp.Run("MoveDocEnd")

        # 복사
        source_hwp.Run("Copy")
        time.sleep(0.2)

        # 원본 파일 닫기
        source_hwp.Run("Cancel")
        source_client.close_document()
        time.sleep(0.1)

        # 대상 문서에 붙여넣기
        target_hwp.Run("Paste")
        time.sleep(0.2)

        print(f'      ✅ 복사-붙여넣기 완료')
        return True

    except Exception as e:
        print(f'      ❌ 복사-붙여넣기 실패: {e}')
        return False


def test_e2e_column_insertion():
    """E2E 칼럼별 문항 삽입 테스트"""

    print('=' * 70)
    print('E2E 테스트: 실제 문항 파일 칼럼별 삽입')
    print('=' * 70)

    # 파일 경로
    template_path = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    output_path = Path("FunctionTest/결과_E2E_칼럼삽입.hwp")

    if not template_path.exists():
        print(f'❌ 템플릿 파일이 없습니다: {template_path}')
        return False

    if not problem_dir.exists():
        print(f'❌ 문항 디렉토리가 없습니다: {problem_dir}')
        return False

    # 문항 파일 목록 (처음 5개만 테스트)
    problem_files = sorted(problem_dir.glob("*.hwp"))[:5]

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다: {problem_dir}')
        return False

    print(f'\n테스트할 문항 수: {len(problem_files)}개')
    for i, pf in enumerate(problem_files, 1):
        print(f'  {i}. {pf.name[:50]}...')

    # MCP 클라이언트 2개 생성 (target, source)
    print('\n[1/4] MCP 클라이언트 초기화...')
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
        # 템플릿 열기
        print(f'\n[2/4] 템플릿 열기: {template_path.name}')
        result = target_client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 템플릿 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 템플릿 로드 완료')

        # 첫 번째 칼럼 시작 위치로 이동
        print('\n초기 위치 설정: SetPos(0, 1, 0)')
        target_hwp.SetPos(0, 1, 0)
        time.sleep(0.1)
        initial_pos = target_hwp.GetPos()
        print(f'초기 위치: {initial_pos}')

        # 각 문항 삽입
        print(f'\n[3/4] 문항 삽입 (총 {len(problem_files)}개)')
        inserted = 0

        for i, problem_file in enumerate(problem_files, 1):
            print(f'\n--- 문항 {i}/{len(problem_files)} ---')
            print(f'   파일: {problem_file.name[:40]}...')

            # 현재 위치 확인
            before_pos = target_hwp.GetPos()
            print(f'   삽입 전 위치: {before_pos}')

            # 복사-붙여넣기
            if copy_paste_problem(problem_file, target_client, source_client):
                inserted += 1

                # 삽입 후 위치
                after_pos = target_hwp.GetPos()
                print(f'   삽입 후 위치: {after_pos}')

                # 마지막 문항이 아니면 BreakColumn
                if i < len(problem_files):
                    print(f'   hwp.Run("BreakColumn") 호출...')
                    target_hwp.Run("BreakColumn")
                    time.sleep(0.1)

                    break_pos = target_hwp.GetPos()
                    print(f'   BreakColumn 후 위치: {break_pos}')
                    print(f'   ✅ 다음 칼럼 준비 완료')
            else:
                print(f'   ⚠️  문항 {i} 삽입 실패')

        # 최종 상태
        print(f'\n[4/4] 최종 문서 상태')
        page_count = target_hwp.PageCount
        final_pos = target_hwp.GetPos()
        print(f'페이지 수: {page_count}')
        print(f'최종 커서 위치: {final_pos}')
        print(f'삽입된 문항: {inserted}/{len(problem_files)}개')

        # 결과 저장
        print(f'\n결과 저장: {output_path.name}')
        save_result = target_client.save_document_as(str(output_path))

        if save_result.success and output_path.exists():
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
        print(f'템플릿: {template_path.name}')
        print(f'삽입 문항 수: {inserted}개')
        print(f'최종 페이지: {page_count}개')
        print(f'출력 파일: {output_path}')
        print()
        print('검증 사항:')
        print('  - 각 문항이 개별 칼럼에 배치되었는지')
        print('  - 문항 순서가 올바른지')
        print('  - 글자 겹침이 없는지')
        print('  - B4 2단 레이아웃이 유지되는지')
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
    success = test_e2e_column_insertion()
    sys.exit(0 if success else 1)
