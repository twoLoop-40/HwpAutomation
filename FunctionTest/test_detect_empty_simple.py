"""
빈 칼럼 간단 감지

목적: 칼럼 추적기 결과 파일에서 빈 칼럼 확인
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


def test_detect_empty_simple():
    """간단한 빈 칼럼 감지"""

    print('=' * 70)
    print('빈 칼럼 간단 감지 테스트')
    print('=' * 70)

    test_file = Path("FunctionTest/결과_칼럼추적기.hwp")

    if not test_file.exists():
        print(f'❌ 파일 없음: {test_file}')
        return False

    print(f'\n파일: {test_file.name}')

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
            return False

        time.sleep(0.5)

        # 문서 정보
        page_count = hwp.PageCount
        print(f'\n문서 정보: {page_count}페이지')

        # Para별 내용 확인
        print('\n[Para별 내용 확인]')
        print('-' * 70)

        paras_with_content = []
        paras_empty = []

        for para_num in range(70):  # 최대 70개 Para
            # Para 시작으로 이동
            set_result = hwp.SetPos(0, para_num, 0)

            if not set_result:
                print(f'\nPara {para_num}부터 존재하지 않음')
                break

            start_pos = hwp.GetPos()

            # Para 끝까지 선택
            hwp.Run("Select")
            hwp.Run("MoveParagraphEnd")

            # 복사
            hwp.Run("Copy")
            time.sleep(0.05)

            # 클립보드에서 텍스트 가져오기
            text = get_clipboard_text()

            # 선택 취소
            hwp.Run("Cancel")

            # 내용 확인
            text_length = len(text.strip()) if text else 0

            if text_length > 0:
                paras_with_content.append(para_num)
                preview = text[:30] if text else ''
                print(f'Para {para_num:2d}: {text_length:4d}자 | {preview}...')
            else:
                paras_empty.append(para_num)

        # 통계
        print('\n' + '=' * 70)
        print('통계')
        print('=' * 70)
        print(f'총 Para 수: {len(paras_with_content) + len(paras_empty)}')
        print(f'내용 있음: {len(paras_with_content)}개 - Para {paras_with_content}')
        print(f'빈 Para: {len(paras_empty)}개 - Para {paras_empty}')

        # ColumnTracker 결과와 비교
        print('\n[ColumnTracker 예상 결과와 비교]')
        print('-' * 70)
        print('ColumnTracker는 10개 문항을 삽입했습니다:')
        print('  문항  1: Page 1, Column 1 | Para 0 → 9')
        print('  문항  2: Page 1, Column 2 | Para 9 → 18')
        print('  문항  3: Page 2, Column 1 | Para 18 → 21')
        print('  문항  4: Page 2, Column 2 | Para 21 → 27')
        print('  문항  5: Page 3, Column 1 | Para 27 → 32')
        print('  문항  6: Page 3, Column 2 | Para 32 → 33')
        print('  문항  7: Page 4, Column 1 | Para 33 → 41')
        print('  문항  8: Page 4, Column 2 | Para 41 → 47')
        print('  문항  9: Page 5, Column 1 | Para 47 → 51')
        print('  문항 10: Page 5, Column 2 | Para 51 → 56')

        expected_para_ranges = [
            (0, 9), (9, 18), (18, 21), (21, 27), (27, 32),
            (32, 33), (33, 41), (41, 47), (47, 51), (51, 56)
        ]

        print('\n예상되는 내용 있는 Para:')
        expected_paras = set()
        for start, end in expected_para_ranges:
            for p in range(start, end + 1):
                expected_paras.add(p)

        print(f'  {sorted(expected_paras)}')

        # 실제 vs 예상 비교
        actual_paras = set(paras_with_content)
        missing = expected_paras - actual_paras
        extra = actual_paras - expected_paras

        if missing:
            print(f'\n⚠️  예상했지만 빈 Para: {sorted(missing)}')
        if extra:
            print(f'\n⚠️  예상 밖의 내용 있는 Para: {sorted(extra)}')

        if not missing and not extra:
            print(f'\n✅ 완벽하게 일치! 빈 칼럼 없음')

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
    success = test_detect_empty_simple()
    sys.exit(0 if success else 1)
