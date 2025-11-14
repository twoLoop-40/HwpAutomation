"""
세 위치에 문제 삽입 + BreakColumn 테스트

목적: 각 문제 삽입 후 BreakColumn을 호출하여 다음 칼럼으로 이동
      글자 겹침 방지

시나리오:
1. 첫 번째 문제 → SetPos(0, 0, 0) 후 삽입 → BreakColumn
2. 두 번째 문제 → SetPos(0, 1, 0) 후 삽입 → BreakColumn
3. 세 번째 문제 → SetPos(0, 2, 0) 후 삽입
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


def test_insert_three_problems_with_break():
    """세 위치에 문제 삽입 + BreakColumn"""

    print('=' * 70)
    print('세 위치에 문제 삽입 + BreakColumn 테스트')
    print('=' * 70)

    # 파일 경로
    template_path = Path(__file__).parent / "[양식]mad모의고사.hwp"
    output_path = Path(__file__).parent / "결과_세위치_문제삽입_BreakColumn.hwp"

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
        # 템플릿 열기
        print(f'\n[1/4] 템플릿 열기: {template_path.name}')
        result = client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 템플릿 로드 완료')

        # 문제 텍스트 정의
        problems = [
            {
                'num': 1,
                'pos': (0, 0, 0),
                'text': '''[문제 1]

다음 중 함수 f(x) = x² + 2x + 1의 최솟값은?

① -2
② -1
③ 0
④ 1
⑤ 2

'''
            },
            {
                'num': 2,
                'pos': (0, 1, 0),
                'text': '''[문제 2]

다음 등식이 성립할 때, 상수 a의 값은?
lim(x→0) (sin 3x) / (ax) = 1

① 1/3
② 1
③ 3
④ 6
⑤ 9

'''
            },
            {
                'num': 3,
                'pos': (0, 2, 0),
                'text': '''[문제 3]

함수 f(x) = x³ - 3x² + 2의 극댓값은?

① -2
② 0
③ 2
④ 4
⑤ 6

'''
            }
        ]

        # 각 문제 삽입
        print(f'\n[2/4] 문제 삽입 (BreakColumn 포함)')

        for i, problem in enumerate(problems):
            num = problem['num']
            pos = problem['pos']
            text = problem['text']

            print(f'\n--- 문제 {num} ---')
            print(f'목표 위치: {pos}')

            # 위치 이동
            list_num, para, char_pos = pos
            set_result = hwp.SetPos(list_num, para, char_pos)
            print(f'SetPos{pos} 반환값: {set_result}')
            time.sleep(0.1)

            # 실제 위치 확인
            actual_pos = hwp.GetPos()
            print(f'실제 위치: {actual_pos}')

            if actual_pos == pos:
                print(f'✅ 위치 일치')
            else:
                print(f'⚠️  위치 불일치 (목표: {pos}, 실제: {actual_pos})')

            # 문제 텍스트 삽입
            hwp.HAction.GetDefault('InsertText', hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = text
            hwp.HAction.Execute('InsertText', hwp.HParameterSet.HInsertText.HSet)
            time.sleep(0.1)

            # 삽입 후 위치
            after_insert_pos = hwp.GetPos()
            print(f'삽입 후 위치: {after_insert_pos}')
            print(f'✅ 문제 {num} 삽입 완료')

            # 마지막 문제가 아니면 BreakColumn 호출
            if i < len(problems) - 1:
                print(f'hwp.Run("BreakColumn") 호출...')
                hwp.Run("BreakColumn")
                time.sleep(0.1)

                after_break_pos = hwp.GetPos()
                print(f'BreakColumn 후 위치: {after_break_pos}')
                print(f'✅ 다음 칼럼으로 이동')

        # 최종 상태 확인
        print(f'\n[3/4] 최종 문서 상태')
        page_count = hwp.PageCount
        final_pos = hwp.GetPos()
        print(f'페이지 수: {page_count}')
        print(f'최종 커서 위치: {final_pos}')

        # 결과 저장
        print(f'\n[4/4] 결과 저장: {output_path.name}')
        save_result = client.save_document_as(str(output_path))

        if save_result.success and output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes')
        else:
            print(f'⚠️  저장 실패')

        # 결과 요약
        print('\n' + '=' * 70)
        print('테스트 결과 요약')
        print('=' * 70)
        print('삽입 순서:')
        print('  1. 문제 1 → SetPos(0, 0, 0) → 삽입 → BreakColumn')
        print('  2. 문제 2 → SetPos(0, 1, 0) → 삽입 → BreakColumn')
        print('  3. 문제 3 → SetPos(0, 2, 0) → 삽입')
        print()
        print('기대 효과:')
        print('  - 각 문제가 별도 칼럼에 배치')
        print('  - 글자 겹침 없음')
        print('  - BreakColumn이 칼럼 분리 역할')
        print()
        print('저장된 파일을 열어서 확인하세요:')
        print('  - 각 문제가 개별 칼럼에 있는지')
        print('  - 글자 겹침이 해결되었는지')
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
    success = test_insert_three_problems_with_break()
    sys.exit(0 if success else 1)
