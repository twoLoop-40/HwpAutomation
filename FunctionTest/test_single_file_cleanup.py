"""
단일 파일 빈 Para 분석 및 제거 테스트

목적: 특정 파일의 빈 Para 개수 확인 및 제거 테스트
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


def find_all_paras(hwp) -> list:
    """
    네비게이션으로 모든 Para 찾기
    """
    paras = []

    # 문서 시작
    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    para_num = 0

    while True:
        # 현재 Para 시작 위치
        start_pos = hwp.GetPos()

        # Para 끝으로 이동
        hwp.Run("MoveParaEnd")
        time.sleep(0.02)

        end_pos = hwp.GetPos()

        # 빈 Para 확인 (pos 값이 0)
        is_empty = (end_pos[2] == 0)

        paras.append({
            'para_num': para_num,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'is_empty': is_empty,
            'length': end_pos[2] - start_pos[2] if not is_empty else 0,
        })

        # 다음 Para로 이동
        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)

        after_pos = hwp.GetPos()

        # 위치 변경 없으면 종료
        if after_pos == before_pos:
            break

        para_num += 1

        # 안전장치
        if para_num > 500:
            print(f'⚠️  500개 Para 제한 도달')
            break

    return paras


def remove_empty_paras(hwp, paras: list) -> int:
    """
    빈 Para 삭제 (역순)
    """
    empty_paras = [p for p in paras if p['is_empty']]

    if not empty_paras:
        return 0

    removed = 0

    # 역순으로 삭제
    for para in reversed(empty_paras):
        para_num = para['para_num']

        try:
            # Para 위치로 이동
            hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])
            time.sleep(0.02)

            # Para 전체 선택
            hwp.Run("Select")
            hwp.Run("MoveParaEnd")
            time.sleep(0.02)

            # 삭제
            hwp.Run("Delete")
            time.sleep(0.02)

            removed += 1
            print(f'  Para {para_num:2d} 삭제')

        except Exception as e:
            print(f'  ⚠️  Para {para_num} 삭제 실패: {e}')

    return removed


def test_single_file_cleanup():
    """단일 파일 빈 Para 분석 및 제거"""

    print('=' * 70)
    print('단일 파일 빈 Para 분석 및 제거 테스트')
    print('=' * 70)

    # 파일 찾기
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    target_filename = "2025 커팅 S_공수2_기말_2회차_4_4_13.hwp"

    files = list(problem_dir.glob(f"*{target_filename}*"))

    if not files:
        # 전체 파일 검색
        files = sorted(problem_dir.glob("*.hwp"))
        if len(files) >= 3:
            test_file = files[2]  # 3번째 파일 사용
            print(f'⚠️  지정 파일을 찾을 수 없어 3번째 파일 사용: {test_file.name}')
        else:
            print(f'❌ 파일을 찾을 수 없습니다')
            return False
    else:
        test_file = files[0]

    print(f'\n파일: {test_file.name}')
    print(f'경로: {test_file}')

    # 클라이언트 2개 생성 (원본, 작업용)
    original_client = AutomationClient()
    work_client = AutomationClient()

    original_hwp = original_client.hwp
    work_hwp = work_client.hwp

    # 보안 모듈 등록
    original_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    work_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    # 창 숨기기
    try:
        original_hwp.XHwpWindows.Item(0).Visible = False
        work_hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # ========================================
        # 1단계: 원본 파일 분석
        # ========================================
        print('\n' + '=' * 70)
        print('[1단계] 원본 파일 분석')
        print('=' * 70)

        result = original_client.open_document(str(test_file), options="readonly:true")
        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.5)

        # Para 스캔
        print('\nPara 스캔 중...')
        original_paras = find_all_paras(original_hwp)

        print(f'\n총 Para 수: {len(original_paras)}개')

        # 통계
        empty_paras = [p for p in original_paras if p['is_empty']]
        content_paras = [p for p in original_paras if not p['is_empty']]

        print(f'빈 Para: {len(empty_paras)}개')
        print(f'내용 있는 Para: {len(content_paras)}개')

        # 상세 출력
        print('\n[Para 상세 정보]')
        print('-' * 70)
        print(f'{"Para":>4} | {"시작":>15} | {"끝":>15} | {"길이":>6} | {"상태"}')
        print('-' * 70)

        for p in original_paras:
            status = "빈 문단" if p['is_empty'] else "내용 있음"
            print(f'{p["para_num"]:4d} | {str(p["start_pos"]):>15} | {str(p["end_pos"]):>15} | {p["length"]:6d} | {status}')

        if empty_paras:
            print(f'\n빈 Para 목록: {[p["para_num"] for p in empty_paras]}')

        # 원본 파일 닫기
        original_client.close_document()

        # ========================================
        # 2단계: 빈 Para 제거 테스트
        # ========================================
        print('\n' + '=' * 70)
        print('[2단계] 빈 Para 제거 테스트')
        print('=' * 70)

        # 작업용으로 파일 다시 열기 (쓰기 모드)
        result = work_client.open_document(str(test_file))
        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.5)

        # Para 재스캔
        print('\nPara 재스캔 중...')
        work_paras = find_all_paras(work_hwp)

        print(f'총 Para 수: {len(work_paras)}개')

        # 빈 Para 삭제
        print(f'\n빈 Para 삭제 중...')
        removed = remove_empty_paras(work_hwp, work_paras)

        print(f'✅ {removed}개 빈 Para 삭제 완료')

        # 삭제 후 재스캔
        print(f'\n삭제 후 재스캔...')
        final_paras = find_all_paras(work_hwp)

        print(f'최종 Para 수: {len(final_paras)}개')

        final_empty = [p for p in final_paras if p['is_empty']]
        final_content = [p for p in final_paras if not p['is_empty']]

        print(f'최종 빈 Para: {len(final_empty)}개')
        print(f'최종 내용 있는 Para: {len(final_content)}개')

        # 결과 저장
        output_path = Path("FunctionTest/결과_단일파일_빈문단제거.hwp")
        print(f'\n결과 저장: {output_path.name}')
        work_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            original_size = test_file.stat().st_size
            final_size = output_path.stat().st_size

            print(f'✅ 저장 완료')
            print(f'   원본 파일: {test_file}')
            print(f'   원본 크기: {original_size:,} bytes')
            print(f'   결과 파일: {output_path}')
            print(f'   결과 크기: {final_size:,} bytes')
            print(f'   크기 차이: {original_size - final_size:,} bytes')
        else:
            print(f'⚠️  저장 실패')

        # 작업용 파일 닫기
        work_client.close_document()

        # ========================================
        # 3단계: 요약
        # ========================================
        print('\n' + '=' * 70)
        print('요약')
        print('=' * 70)
        print(f'원본 Para 수: {len(original_paras)}개')
        print(f'  - 빈 Para: {len(empty_paras)}개')
        print(f'  - 내용 있는 Para: {len(content_paras)}개')
        print()
        print(f'삭제된 빈 Para: {removed}개')
        print()
        print(f'최종 Para 수: {len(final_paras)}개')
        print(f'  - 빈 Para: {len(final_empty)}개')
        print(f'  - 내용 있는 Para: {len(final_content)}개')
        print()

        if removed > 0:
            print(f'✅ 빈 Para 제거 성공!')
            print(f'   {removed}개 삭제됨')
        else:
            print(f'⚠️  제거할 빈 Para가 없었습니다')

        if len(final_empty) > 0:
            print(f'\n⚠️  주의: 삭제 후에도 {len(final_empty)}개 빈 Para가 남아있습니다')
            print(f'   이것은 HWP 내부 구조상 정상일 수 있습니다')

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
        original_client.cleanup()
        work_client.cleanup()
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_single_file_cleanup()
    sys.exit(0 if success else 1)
