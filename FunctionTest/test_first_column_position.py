"""
첫 번째 칼럼 상단 포인팅 테스트

참조: Specs/TemplateMerge.idr - firstColumnStart : DocPosition
목적: B4 2단 템플릿에서 첫 번째 칼럼 시작 위치를 정확히 포인팅하는지 검증

예상 결과:
- SetPos(0, 1, 0) 호출 후 GetPos() 반환값이 (0, 1, 0)이어야 함
- 해당 위치에 텍스트 삽입 시 첫 번째 칼럼 상단에 표시되어야 함
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


def test_first_column_position():
    """
    첫 번째 칼럼 상단 포인팅 테스트

    테스트 단계:
    1. 템플릿 열기
    2. 초기 위치 확인
    3. SetPos(0, 1, 0) 호출
    4. GetPos()로 위치 확인
    5. 테스트 텍스트 삽입
    6. 결과 저장
    """
    print('=' * 70)
    print('첫 번째 칼럼 상단 포인팅 테스트')
    print('=' * 70)

    # 파일 경로
    template_path = Path(__file__).parent / "[양식]mad모의고사.hwp"
    output_path = Path(__file__).parent / "결과_첫번째칼럼.hwp"

    if not template_path.exists():
        print(f'❌ 템플릿 파일이 없습니다: {template_path}')
        return False

    # MCP 클라이언트 생성
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
        print(f'\n[1/6] 템플릿 열기: {template_path.name}')
        result = client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 템플릿 로드 완료')

        # 2. 초기 위치 확인
        print('\n[2/6] 초기 위치 확인')
        initial_pos = hwp.GetPos()
        print(f'초기 위치: {initial_pos}')

        # 3. 첫 번째 칼럼 시작 위치로 이동
        print('\n[3/6] 첫 번째 칼럼 시작 위치로 이동')
        print('SetPos(0, 1, 0) 호출...')

        set_result = hwp.SetPos(0, 1, 0)
        print(f'SetPos 반환값: {set_result}')
        time.sleep(0.1)

        # 4. 위치 확인
        print('\n[4/6] 위치 확인')
        current_pos = hwp.GetPos()
        print(f'현재 위치: {current_pos}')

        # 위치 검증
        expected_pos = (0, 1, 0)
        if current_pos == expected_pos:
            print(f'✅ 위치 일치: {current_pos}')
            position_correct = True
        else:
            print(f'⚠️  위치 불일치!')
            print(f'   예상: {expected_pos}')
            print(f'   실제: {current_pos}')
            position_correct = False

        # 5. 테스트 텍스트 삽입
        print('\n[5/6] 테스트 텍스트 삽입')
        test_text = '<<< 첫 번째 칼럼 상단 >>>\n\n이 텍스트가 첫 번째 칼럼 맨 위에 있어야 합니다.'

        hwp.HAction.GetDefault('InsertText', hwp.HParameterSet.HInsertText.HSet)
        hwp.HParameterSet.HInsertText.Text = test_text
        hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
        time.sleep(0.1)

        after_insert_pos = hwp.GetPos()
        print(f'텍스트 삽입 후 위치: {after_insert_pos}')
        print('✅ 텍스트 삽입 완료')

        # 6. 결과 저장
        print(f'\n[6/6] 결과 저장: {output_path.name}')
        save_result = client.save_document_as(str(output_path))

        if save_result.success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes')
        else:
            print(f'⚠️  저장 실패: {save_result.error if not save_result.success else "알 수 없음"}')

        # 최종 결과
        print('\n' + '=' * 70)
        print('테스트 결과')
        print('=' * 70)
        print(f'SetPos 성공: {set_result}')
        print(f'위치 정확성: {"✅ 정확" if position_correct else "❌ 부정확"}')
        print(f'예상 위치: {expected_pos}')
        print(f'실제 위치: {current_pos}')
        print(f'텍스트 삽입: ✅ 완료')
        print(f'파일 저장: {"✅ 완료" if output_path.exists() else "❌ 실패"}')
        print('=' * 70)

        return position_correct

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
    success = test_first_column_position()
    sys.exit(0 if success else 1)
