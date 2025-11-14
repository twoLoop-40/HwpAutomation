"""
빈 칼럼 감지 테스트

목적: 생성된 문서에서 빈 칼럼이 있는지 파악
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


def get_clipboard_text():
    """클립보드 텍스트 가져오기"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return text
        finally:
            win32clipboard.CloseClipboard()
    except:
        return ""


def check_para_content(hwp, para_num: int) -> dict:
    """
    Para 내용 확인

    Returns:
        dict: {
            'para': para 번호,
            'pos': 실제 위치,
            'has_content': 내용 존재 여부,
            'text_length': 텍스트 길이,
            'preview': 텍스트 미리보기 (처음 50자)
        }
    """
    try:
        # Para 시작으로 이동
        set_result = hwp.SetPos(0, para_num, 0)

        if not set_result:
            return {
                'para': para_num,
                'pos': None,
                'has_content': False,
                'text_length': 0,
                'preview': '',
                'error': 'SetPos 실패',
            }

        start_pos = hwp.GetPos()

        # Para 끝까지 선택
        hwp.Run("Select")
        hwp.Run("MoveParagraphEnd")

        end_pos = hwp.GetPos()

        # 복사
        hwp.Run("Copy")
        time.sleep(0.05)

        # 클립보드에서 텍스트 가져오기
        text = get_clipboard_text()

        # 선택 취소
        hwp.Run("Cancel")

        # 길이 계산
        text_length = len(text.strip()) if text else 0
        has_content = text_length > 0

        return {
            'para': para_num,
            'pos': start_pos,
            'has_content': has_content,
            'text_length': text_length,
            'preview': text[:50] if text else '',
        }

    except Exception as e:
        return {
            'para': para_num,
            'pos': None,
            'has_content': False,
            'text_length': 0,
            'preview': '',
            'error': str(e),
        }


def analyze_column_distribution(hwp, max_paras: int = 100):
    """
    칼럼별 내용 분포 분석

    2단 레이아웃 가정:
    - 홀수 Para (1, 3, 5, ...) = 왼쪽 칼럼
    - 짝수 Para (2, 4, 6, ...) = 오른쪽 칼럼
    """
    print('\n[칼럼별 내용 분포 분석]')
    print('-' * 70)

    left_column_paras = []   # 왼쪽 칼럼 (홀수)
    right_column_paras = []  # 오른쪽 칼럼 (짝수)

    # 모든 Para 검사
    for para_num in range(max_paras):
        info = check_para_content(hwp, para_num)

        if 'error' in info and info['error'] == 'SetPos 실패':
            print(f'\nPara {para_num}부터 존재하지 않음')
            break

        # 홀수/짝수 분류 (Para 0 제외)
        if para_num > 0:
            if para_num % 2 == 1:  # 홀수
                left_column_paras.append(info)
            else:  # 짝수
                right_column_paras.append(info)

        # 내용 있는 Para만 출력
        if info['has_content']:
            column_marker = "L" if para_num % 2 == 1 else "R"
            print(f'Para {para_num:2d} [{column_marker}]: {info["text_length"]:4d}자 | {info["preview"]}...')

    # 통계
    print('\n' + '=' * 70)
    print('통계')
    print('=' * 70)

    # 왼쪽 칼럼
    left_with_content = [p for p in left_column_paras if p['has_content']]
    left_empty = [p for p in left_column_paras if not p['has_content']]

    print(f'\n왼쪽 칼럼 (홀수 Para):')
    print(f'  총 Para 수: {len(left_column_paras)}')
    print(f'  내용 있음: {len(left_with_content)}')
    print(f'  빈 Para: {len(left_empty)}')

    if left_empty:
        print(f'  빈 Para 번호: {[p["para"] for p in left_empty]}')

    # 오른쪽 칼럼
    right_with_content = [p for p in right_column_paras if p['has_content']]
    right_empty = [p for p in right_column_paras if not p['has_content']]

    print(f'\n오른쪽 칼럼 (짝수 Para):')
    print(f'  총 Para 수: {len(right_column_paras)}')
    print(f'  내용 있음: {len(right_with_content)}')
    print(f'  빈 Para: {len(right_empty)}')

    if right_empty:
        print(f'  빈 Para 번호: {[p["para"] for p in right_empty]}')

    # 빈 칼럼 경고
    total_empty = len(left_empty) + len(right_empty)
    if total_empty > 0:
        print(f'\n⚠️  빈 Para 발견: {total_empty}개')
        print(f'   왼쪽 칼럼: {len(left_empty)}개')
        print(f'   오른쪽 칼럼: {len(right_empty)}개')
    else:
        print(f'\n✅ 빈 Para 없음 - 모든 칼럼에 내용이 있습니다')

    print('=' * 70)


def test_detect_empty_columns():
    """빈 칼럼 감지 테스트"""

    print('=' * 70)
    print('빈 칼럼 감지 테스트')
    print('=' * 70)

    # 테스트할 파일들
    test_files = [
        Path("FunctionTest/결과_E2E_B4_2단_합병.hwp"),
        Path("FunctionTest/결과_칼럼추적기.hwp"),
    ]

    for test_file in test_files:
        if not test_file.exists():
            print(f'\n⚠️  파일 없음: {test_file}')
            continue

        print(f'\n\n{"=" * 70}')
        print(f'파일: {test_file.name}')
        print('=' * 70)

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
            # 파일 열기
            result = client.open_document(str(test_file), options="readonly:true")

            if not result.success:
                print(f'❌ 파일 열기 실패: {result.error}')
                continue

            time.sleep(0.3)

            # 문서 정보
            page_count = hwp.PageCount
            print(f'\n문서 정보: {page_count}페이지')

            # 칼럼 분포 분석
            analyze_column_distribution(hwp, max_paras=100)

        except Exception as e:
            print(f'\n💥 오류 발생: {e}')
            import traceback
            traceback.print_exc()

        finally:
            # 정리
            client.close_document()
            client.cleanup()
            time.sleep(0.2)

    print('\n\n✅ 모든 파일 분석 완료')
    return True


if __name__ == "__main__":
    success = test_detect_empty_columns()
    sys.exit(0 if success else 1)
