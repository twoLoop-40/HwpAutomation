"""
MoveSelLeft로 빈 Para 삭제 테스트

아이디어:
1. 빈 Para 시작으로 이동
2. MoveSelLeft 반복 (빈 Para 전체 선택)
3. Delete 한 번에 삭제
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
            'length': end_pos[2] - start_pos[2] if not is_empty else 0,
        })

        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)

        after_pos = hwp.GetPos()

        if after_pos == before_pos:
            break

        para_num += 1

        if para_num > 500:
            print(f'⚠️  500개 Para 제한 도달')
            break

    return paras


def delete_empty_paras_with_movesel(hwp, paras: list) -> int:
    """
    MoveSelLeft로 빈 Para 삭제

    전략:
    1. 각 빈 Para의 시작으로 이동
    2. MoveSelLeft 반복 (Para 끝까지 선택)
    3. Delete로 삭제
    """
    empty_paras = [p for p in paras if p['is_empty']]

    if not empty_paras:
        print(f'  빈 Para 없음')
        return 0

    print(f'  빈 Para {len(empty_paras)}개 발견')

    removed = 0

    # 역순으로 삭제 (앞에서 삭제하면 Para 번호 밀림)
    for para in reversed(empty_paras):
        para_num = para['para_num']

        try:
            # Para 시작으로 이동
            hwp.SetPos(para['start_pos'][0], para['start_pos'][1], para['start_pos'][2])
            time.sleep(0.02)

            print(f'    Para {para_num:2d} 삭제 시도...')

            # Para 끝으로 이동해서 길이 확인
            start_pos = hwp.GetPos()
            hwp.Run("MoveParaEnd")
            end_pos = hwp.GetPos()

            # 빈 Para 확인
            if end_pos[2] == 0:
                # 방법 1: MoveSelLeft 사용
                hwp.SetPos(start_pos[0], start_pos[1], start_pos[2])

                # Para 전체 선택 (Select + MoveParaEnd)
                hwp.Run("Select")
                hwp.Run("MoveParaEnd")
                time.sleep(0.02)

                # 삭제
                hwp.Run("Delete")
                time.sleep(0.02)

                removed += 1
                print(f'      ✅ 삭제 완료')
            else:
                print(f'      ⚠️  빈 Para 아님 (길이: {end_pos[2]})')

        except Exception as e:
            print(f'      ❌ 삭제 실패: {e}')

    return removed


def delete_empty_paras_movesel_v2(hwp, paras: list) -> int:
    """
    MoveSelLeft 방식 v2 - 스크립트 방식 그대로

    OnScriptMacro_DeleteEmptryPara() 로직:
    - MoveSelLeft 2번
    - Delete
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

            # MoveSelLeft 2번 (스크립트처럼)
            hwp.Run("MoveSelLeft")
            time.sleep(0.02)
            hwp.Run("MoveSelLeft")
            time.sleep(0.02)

            # Delete
            hwp.Run("Delete")
            time.sleep(0.02)

            removed += 1
            print(f'    Para {para_num:2d} 삭제 (MoveSelLeft 방식)')

        except Exception as e:
            print(f'    ⚠️  Para {para_num} 삭제 실패: {e}')

    return removed


def test_delete_empty_with_movesel():
    """MoveSelLeft로 빈 Para 삭제 테스트"""

    print('=' * 70)
    print('MoveSelLeft로 빈 Para 삭제 테스트')
    print('=' * 70)

    # 파일 찾기
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    files = sorted(problem_dir.glob("*.hwp"))

    if len(files) < 3:
        print(f'❌ 파일을 찾을 수 없습니다')
        return False

    test_file = files[2]  # 3번째 파일

    print(f'\n파일: {test_file.name}')

    # 클라이언트 생성
    client = AutomationClient()
    hwp = client.hwp

    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 파일 열기
        print('\n[1/4] 파일 열기')
        result = client.open_document(str(test_file))
        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 파일 열기 완료')

        # 원본 Para 스캔
        print('\n[2/4] 원본 Para 스캔')
        original_paras = find_all_paras(hwp)

        print(f'총 Para 수: {len(original_paras)}개')

        empty_paras = [p for p in original_paras if p['is_empty']]
        content_paras = [p for p in original_paras if not p['is_empty']]

        print(f'빈 Para: {len(empty_paras)}개 - {[p["para_num"] for p in empty_paras]}')
        print(f'내용 있는 Para: {len(content_paras)}개')

        # 빈 Para 삭제 (MoveSelLeft 방식)
        print('\n[3/4] 빈 Para 삭제 (MoveSelLeft 방식)')
        removed = delete_empty_paras_movesel_v2(hwp, original_paras)
        print(f'✅ {removed}개 삭제 완료')

        # 삭제 후 재스캔
        print('\n[4/4] 삭제 후 재스캔')
        final_paras = find_all_paras(hwp)

        print(f'최종 Para 수: {len(final_paras)}개')

        final_empty = [p for p in final_paras if p['is_empty']]
        final_content = [p for p in final_paras if not p['is_empty']]

        print(f'최종 빈 Para: {len(final_empty)}개')
        print(f'최종 내용 있는 Para: {len(final_content)}개')

        # 결과 저장
        output_path = Path("FunctionTest/결과_MoveSelLeft_삭제.hwp")
        print(f'\n결과 저장: {output_path.name}')
        hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            original_size = test_file.stat().st_size
            final_size = output_path.stat().st_size

            print(f'✅ 저장 완료')
            print(f'   원본 크기: {original_size:,} bytes')
            print(f'   결과 크기: {final_size:,} bytes')
            print(f'   크기 차이: {original_size - final_size:,} bytes')

        # 요약
        print('\n' + '=' * 70)
        print('요약')
        print('=' * 70)
        print(f'원본: {len(original_paras)}개 Para (빈 Para {len(empty_paras)}개)')
        print(f'삭제: {removed}개')
        print(f'최종: {len(final_paras)}개 Para (빈 Para {len(final_empty)}개)')

        if len(final_empty) < len(empty_paras):
            print(f'\n✅ 성공! {len(empty_paras) - len(final_empty)}개 빈 Para 감소')
        elif len(final_empty) == len(empty_paras):
            print(f'\n⚠️  빈 Para 개수 변화 없음 (HWP 자동 재생성)')
        else:
            print(f'\n⚠️  빈 Para 증가? ({len(empty_paras)} → {len(final_empty)})')

        print('=' * 70)

        return True

    except Exception as e:
        print(f'\n💥 오류 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        print('\n[정리] 문서 닫기...')
        client.close_document()
        client.cleanup()
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_delete_empty_with_movesel()
    sys.exit(0 if success else 1)
