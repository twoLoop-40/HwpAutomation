"""
각 Para의 실제 텍스트 내용 읽기

목적: Para별로 텍스트를 선택하고 클립보드로 복사하여 실제 내용 확인
"""

import sys
import time
from pathlib import Path
import win32clipboard

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


def get_clipboard_text() -> str:
    """클립보드에서 텍스트 가져오기"""
    try:
        win32clipboard.OpenClipboard()
        try:
            text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            return text
        except:
            return ""
        finally:
            win32clipboard.CloseClipboard()
    except Exception as e:
        print(f'클립보드 읽기 실패: {e}')
        return ""


def read_para_content(file_path: Path):
    """각 Para의 실제 텍스트 내용 읽기"""

    print('=' * 70)
    print(f'Para 내용 읽기: {file_path.name[:50]}...')
    print('=' * 70)

    if not file_path.exists():
        print(f'❌ 파일이 없습니다: {file_path}')
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
        # 파일 열기
        print(f'\n[1] 파일 열기: {file_path.name[:50]}...')
        result = client.open_document(str(file_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 파일 로드 완료')

        # 문서 끝 위치 확인
        hwp.Run("MoveDocEnd")
        doc_end_pos = hwp.GetPos()
        max_para = doc_end_pos[1]
        print(f'\n문서 끝: {doc_end_pos}, 최대 para: {max_para}')

        # 각 Para 내용 읽기
        print('\n' + '=' * 70)
        print(f'Para 0 ~ {max_para} 내용 읽기')
        print('=' * 70)

        for para in range(max_para + 1):
            print(f'\n--- Para {para} ---')

            # Para 시작 위치로 이동
            set_result = hwp.SetPos(0, para, 0)
            actual_pos = hwp.GetPos()
            print(f'SetPos(0, {para}, 0) → {actual_pos}')

            if actual_pos[1] != para:
                print(f'⚠️  접근 불가 (자동 이동됨)')
                continue

            # Para 전체 선택
            hwp.Run("Select")
            hwp.Run("MoveParagraphEnd")
            time.sleep(0.1)

            end_pos = hwp.GetPos()
            para_length = end_pos[2]
            print(f'Para 끝: {end_pos}, 길이: {para_length}자')

            # 클립보드로 복사
            hwp.Run("Copy")
            time.sleep(0.2)

            # 클립보드에서 텍스트 읽기
            text = get_clipboard_text()

            # 선택 취소
            hwp.Run("Cancel")
            time.sleep(0.1)

            # 내용 출력
            if text.strip():
                # 첫 100자만 출력
                preview = text[:100].replace('\r', '').replace('\n', '↵')
                print(f'내용: "{preview}"...')
                print(f'전체 길이: {len(text)}자')
            else:
                print('내용: (빈 문단)')

        # 결과 요약
        print('\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'파일: {file_path.name}')
        print(f'최대 para: {max_para}')
        print()
        print('Para별 내용:')

        # 다시 한번 순회하며 요약
        content_paras = []
        empty_paras = []

        for para in range(max_para + 1):
            hwp.SetPos(0, para, 0)
            actual_pos = hwp.GetPos()

            if actual_pos[1] != para:
                continue

            hwp.Run("Select")
            hwp.Run("MoveParagraphEnd")
            time.sleep(0.1)

            end_pos = hwp.GetPos()
            hwp.Run("Copy")
            time.sleep(0.2)

            text = get_clipboard_text()
            hwp.Run("Cancel")

            if text.strip():
                content_paras.append(para)
            else:
                empty_paras.append(para)

        if content_paras:
            print(f'  내용 있음: Para {content_paras}')
        if empty_paras:
            print(f'  빈 문단: Para {empty_paras}')

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
    # 테스트할 파일 선택
    import sys

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # 기본값: 양식 파일
        file_path = Path(__file__).parent / "[양식]mad모의고사.hwp"

    success = read_para_content(file_path)
    sys.exit(0 if success else 1)
