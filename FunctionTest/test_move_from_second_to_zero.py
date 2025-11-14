"""
두 번째 칼럼에서 (0, 0, 0)으로 이동 테스트

목적: 두 번째 칼럼에 커서가 있을 때 SetPos(0, 0, 0)으로 이동하면 어디로 가는지 확인

시나리오:
1. 첫 번째 칼럼에 텍스트 삽입
2. BreakColumn으로 두 번째 칼럼 생성
3. 두 번째 칼럼에 텍스트 삽입 (현재 위치 확인)
4. SetPos(0, 0, 0) 호출
5. 해당 위치에 텍스트 삽입하여 어디인지 확인
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


def test_move_from_second_to_zero():
    """두 번째 칼럼에서 (0, 0, 0)으로 이동"""

    print('=' * 70)
    print('두 번째 칼럼 → (0, 0, 0) 이동 테스트')
    print('=' * 70)

    # 파일 경로
    template_path = Path(__file__).parent / "[양식]mad모의고사.hwp"
    output_path = Path(__file__).parent / "결과_두번째칼럼에서_000이동.hwp"

    if not template_path.exists():
        print(f'❌ 템플릿 파일이 없습니다: {template_path}')
        return False

    client = AutomationClient()
    hwp = client.hwp

    # 보안 모듈 등록
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    # 창 숨기기
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 1. 템플릿 열기
        print(f'\n[1/8] 템플릿 열기: {template_path.name}')
        result = client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 템플릿 로드 완료')

        # 2. 첫 번째 칼럼에 텍스트 삽입
        print('\n[2/8] 첫 번째 칼럼에 텍스트 삽입')
        hwp.SetPos(0, 1, 0)
        time.sleep(0.1)

        pos1 = hwp.GetPos()
        print(f'첫 번째 칼럼 위치: {pos1}')

        hwp.HAction.GetDefault('InsertText', hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = '[첫 번째 칼럼 텍스트]\n' * 2
        hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('✅ 첫 번째 칼럼 텍스트 삽입 완료')

        # 3. BreakColumn으로 두 번째 칼럼 생성
        print('\n[3/8] BreakColumn으로 두 번째 칼럼 생성')
        hwp.Run('BreakColumn')
        time.sleep(0.1)

        pos_after_break = hwp.GetPos()
        print(f'BreakColumn 후 위치: {pos_after_break}')

        # 4. 두 번째 칼럼에 텍스트 삽입
        print('\n[4/8] 두 번째 칼럼에 텍스트 삽입')
        hwp.HParameterSet.HInsertText.Text = '[두 번째 칼럼 텍스트]\n' * 2
        hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        pos2 = hwp.GetPos()
        print(f'두 번째 칼럼 텍스트 삽입 후 위치: {pos2}')
        print('✅ 두 번째 칼럼 텍스트 삽입 완료')
        print('   → 현재 커서는 두 번째 칼럼에 있습니다')

        # 5. SetPos(0, 0, 0)으로 이동
        print('\n[5/8] SetPos(0, 0, 0) 호출')
        set_result = hwp.SetPos(0, 0, 0)
        print(f'SetPos 반환값: {set_result}')
        time.sleep(0.1)

        # 6. 이동 후 위치 확인
        print('\n[6/8] 이동 후 위치 확인')
        pos_after_move = hwp.GetPos()
        print(f'SetPos(0, 0, 0) 후 실제 위치: {pos_after_move}')

        if pos_after_move == (0, 0, 0):
            print('✅ 정확히 (0, 0, 0)으로 이동')
        else:
            print(f'⚠️  예상과 다른 위치: {pos_after_move}')

        # 7. (0, 0, 0) 위치에 마커 텍스트 삽입
        print('\n[7/8] (0, 0, 0) 위치에 마커 텍스트 삽입')
        marker_text = '\n\n<<< (0, 0, 0) 위치 >>>\n이 텍스트가 (0, 0, 0)에 삽입되었습니다.\n'

        hwp.HParameterSet.HInsertText.Text = marker_text
        hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        print('✅ 마커 텍스트 삽입 완료')

        # 8. 결과 저장
        print(f'\n[8/8] 결과 저장: {output_path.name}')
        save_result = client.save_document_as(str(output_path))

        if save_result.success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes')
        else:
            print(f'⚠️  저장 실패')

        # 최종 결과 요약
        print('\n' + '=' * 70)
        print('테스트 결과 요약')
        print('=' * 70)
        print(f'1. 첫 번째 칼럼 시작: {pos1}')
        print(f'2. BreakColumn 후: {pos_after_break}')
        print(f'3. 두 번째 칼럼 텍스트 후: {pos2}')
        print(f'4. SetPos(0, 0, 0) 호출: {set_result}')
        print(f'5. 실제 이동 위치: {pos_after_move}')
        print()
        print('결론:')
        if pos_after_move == (0, 0, 0):
            print('  ✅ 두 번째 칼럼에서 (0, 0, 0)으로 정확히 이동 가능')
        else:
            print(f'  ⚠️  (0, 0, 0)이 아닌 {pos_after_move}로 이동됨')
        print()
        print('저장된 파일을 열어서 "(0, 0, 0) 위치" 텍스트가')
        print('어느 칼럼의 어느 위치에 있는지 확인하세요.')
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
        client.close_document()
        client.cleanup()
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_move_from_second_to_zero()
    sys.exit(0 if success else 1)
