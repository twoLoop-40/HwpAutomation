"""
모든 List 탐색 및 내용 확인

목적: List 0~9의 내용과 구조 파악
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
            return text if text else ""
        except:
            return ""
        finally:
            win32clipboard.CloseClipboard()
    except Exception as e:
        return ""


def explore_all_lists(file_path: Path):
    """모든 List의 내용 탐색"""

    print('=' * 70)
    print(f'List 탐색: {file_path.name[:50]}...')
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
        print(f'\n[1] 파일 열기')
        result = client.open_document(str(file_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 파일 로드 완료')

        # 각 List 탐색
        print('\n[2] List 0~9 탐색')
        print('=' * 70)

        list_info = []

        for list_num in range(10):
            print(f'\n--- List {list_num} ---')

            try:
                # List로 이동 시도
                set_result = hwp.SetPos(list_num, 0, 0)

                if not set_result:
                    print(f'  접근 불가 (SetPos 실패)')
                    continue

                actual_pos = hwp.GetPos()
                print(f'  SetPos({list_num}, 0, 0) → {actual_pos}')

                if actual_pos[0] != list_num:
                    print(f'  ⚠️  다른 List로 이동됨')
                    continue

                # List 끝 위치 찾기
                # 방법 1: Para 0부터 순회
                max_para = 0
                for para in range(100):  # 최대 100 para 검색
                    try:
                        hwp.SetPos(list_num, para, 0)
                        pos = hwp.GetPos()
                        if pos[0] == list_num and pos[1] == para:
                            max_para = para
                        else:
                            break
                    except:
                        break

                print(f'  Para 범위: 0 ~ {max_para}')

                # List 전체 선택 시도
                hwp.SetPos(list_num, 0, 0)
                hwp.Run("Select")

                # Para 끝까지 선택
                for _ in range(1000):  # 충분히 큰 숫자
                    current_pos = hwp.GetPos()
                    if current_pos[1] >= max_para:
                        break
                    hwp.Run("MoveDown")

                hwp.Run("MoveParagraphEnd")
                time.sleep(0.1)

                end_pos = hwp.GetPos()
                print(f'  선택 끝 위치: {end_pos}')

                # 복사
                hwp.Run("Copy")
                time.sleep(0.2)

                # 클립보드에서 텍스트 읽기
                text = get_clipboard_text()

                # 선택 취소
                hwp.Run("Cancel")
                time.sleep(0.1)

                # 내용 분석
                if text.strip():
                    text_preview = text.strip()[:100].replace('\r', '').replace('\n', '↵')
                    print(f'  내용: "{text_preview}"...')
                    print(f'  텍스트 길이: {len(text)}자')

                    list_info.append({
                        'list': list_num,
                        'max_para': max_para,
                        'text_length': len(text),
                        'preview': text_preview
                    })
                else:
                    print(f'  내용: (빈 List)')
                    list_info.append({
                        'list': list_num,
                        'max_para': max_para,
                        'text_length': 0,
                        'preview': ''
                    })

            except Exception as e:
                print(f'  오류: {e}')

        # 결과 요약
        print('\n' + '=' * 70)
        print('List 탐색 결과')
        print('=' * 70)

        print(f'\n접근 가능한 List:')
        for info in list_info:
            list_num = info['list']
            max_para = info['max_para']
            text_length = info['text_length']

            if text_length > 0:
                print(f'  List {list_num}: Para 0~{max_para}, {text_length}자')
                print(f'    → "{info["preview"][:50]}..."')
            else:
                print(f'  List {list_num}: Para 0~{max_para}, 빈 List')

        # 본문(List 0)으로 돌아가기
        print(f'\n본문(List 0)으로 복귀...')
        hwp.SetPos(0, 1, 0)  # List 0, Para 1, Pos 0
        final_pos = hwp.GetPos()
        print(f'최종 위치: {final_pos}')

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
    import sys

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # 기본값: 양식 파일
        file_path = Path(__file__).parent / "[양식]mad모의고사.hwp"

    success = explore_all_lists(file_path)
    sys.exit(0 if success else 1)
