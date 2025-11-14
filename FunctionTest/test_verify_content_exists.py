"""
문서 내용 존재 여부 확인

목적: Para가 아닌 전체 문서 차원에서 내용 확인
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


def test_verify_content():
    """문서 내용 존재 여부 확인"""

    print('=' * 70)
    print('문서 내용 존재 여부 확인')
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

        # 방법 1: SelectAll로 전체 선택
        print('\n[방법 1: SelectAll로 전체 내용 확인]')
        print('-' * 70)

        hwp.Run("MoveDocBegin")
        time.sleep(0.1)

        hwp.Run("SelectAll")
        time.sleep(0.2)

        hwp.Run("Copy")
        time.sleep(0.3)

        all_text = get_clipboard_text()

        hwp.Run("Cancel")

        if all_text:
            text_length = len(all_text)
            lines = all_text.split('\n')
            print(f'✅ 문서에 내용이 있습니다!')
            print(f'   총 길이: {text_length:,}자')
            print(f'   총 줄 수: {len(lines):,}줄')
            print(f'\n   처음 500자:')
            print(f'   {all_text[:500]}...')
        else:
            print(f'⚠️  SelectAll로 내용을 찾을 수 없습니다')

        # 방법 2: 페이지별 순회
        print('\n\n[방법 2: 페이지별 내용 확인]')
        print('-' * 70)

        for page in range(1, min(page_count + 1, 6)):  # 최대 5페이지까지
            print(f'\n--- Page {page} ---')

            # 페이지 시작으로 이동
            hwp.Run("MoveDocBegin")
            time.sleep(0.1)

            # N페이지로 이동 (PageDown 반복)
            for _ in range(page - 1):
                hwp.Run("MovePageDown")
                time.sleep(0.1)

            pos = hwp.GetPos()
            print(f'  위치: {pos}')

            # 현재 페이지 선택 (임의로 500자)
            hwp.Run("Select")
            for _ in range(10):  # 10줄 선택
                hwp.Run("MoveLineDown")
            time.sleep(0.1)

            hwp.Run("Copy")
            time.sleep(0.1)

            page_text = get_clipboard_text()

            hwp.Run("Cancel")

            if page_text:
                print(f'  내용 길이: {len(page_text)}자')
                print(f'  미리보기: {page_text[:100]}...')
            else:
                print(f'  ⚠️  내용 없음')

        # 결론
        print('\n\n' + '=' * 70)
        print('결론')
        print('=' * 70)

        if all_text:
            print('✅ 문서에 내용이 정상적으로 삽입되었습니다')
            print(f'   총 {text_length:,}자의 텍스트가 있습니다')
            print()
            print('💡 Para 구조로는 내용을 읽을 수 없지만,')
            print('   SelectAll이나 페이지 이동으로는 내용을 확인할 수 있습니다.')
            print()
            print('   이는 내용이 표(Table)나 개체(Object) 안에 저장되어 있기 때문입니다.')
            print('   Para는 구조적 메타데이터일 뿐입니다.')
        else:
            print('⚠️  문서에 내용이 없거나 접근할 수 없습니다')

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
    success = test_verify_content()
    sys.exit(0 if success else 1)
