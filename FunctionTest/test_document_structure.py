"""
문서 구조 분석: 표, 개체, List 정보

목적: Para 외에 실제 내용이 저장된 구조 파악
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


def analyze_document_structure(file_path: Path):
    """문서의 표, 개체, List 구조 분석"""

    print('=' * 70)
    print(f'문서 구조 분석: {file_path.name[:50]}...')
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

        # 기본 정보
        print('\n[2] 기본 문서 정보')
        hwp.Run("MoveDocBegin")
        doc_begin = hwp.GetPos()
        hwp.Run("MoveDocEnd")
        doc_end = hwp.GetPos()
        page_count = hwp.PageCount

        print(f'문서 시작: {doc_begin}')
        print(f'문서 끝: {doc_end}')
        print(f'페이지 수: {page_count}')
        print(f'Para 범위: 0 ~ {doc_end[1]}')

        # 표(Table) 정보
        print('\n[3] 표(Table) 구조')
        try:
            # 문서 시작으로 이동
            hwp.Run("MoveDocBegin")

            # 표 검색
            table_count = 0
            max_searches = 100  # 무한 루프 방지

            for i in range(max_searches):
                # 다음 표 찾기
                result = hwp.HAction.GetDefault("TableCellBlock", hwp.HParameterSet.HCellBlockExtend.HSet)

                if result:
                    table_count += 1
                    current_pos = hwp.GetPos()
                    print(f'  표 {table_count}: 위치 {current_pos}')

                    # 표 다음으로 이동
                    hwp.Run("MoveRight")
                else:
                    break

            if table_count == 0:
                print('  표 없음')
            else:
                print(f'\n  총 표 개수: {table_count}개')

        except Exception as e:
            print(f'  표 검색 실패: {e}')

        # 개체(FieldList) 정보
        print('\n[4] 개체(Object) 구조')
        try:
            # FieldList - 그림, 표, 하이퍼링크 등의 개체 목록
            hwp.Run("MoveDocBegin")

            # GetFieldList로 개체 목록 가져오기 시도
            # 주의: 이 API는 문서화가 부족하여 동작하지 않을 수 있음

            print('  개체 정보 조회 API 제한으로 생략')

        except Exception as e:
            print(f'  개체 검색 실패: {e}')

        # List 정보 (다른 텍스트 영역)
        print('\n[5] List 구조 (텍스트 영역)')

        # 현재 list=0만 확인했는데, 다른 list가 있는지 확인
        print('  List 0 (본문):')
        print(f'    Para 범위: 0 ~ {doc_end[1]}')

        # List 1, 2, ... 접근 시도
        other_lists = []
        for list_num in range(1, 10):
            try:
                set_result = hwp.SetPos(list_num, 0, 0)
                if set_result:
                    actual_pos = hwp.GetPos()
                    if actual_pos[0] == list_num:
                        other_lists.append(list_num)
                        print(f'  List {list_num}: 존재 (위치: {actual_pos})')
            except:
                pass

        if not other_lists:
            print('  다른 List 없음 (List 0만 존재)')

        # 문서 내용 타입 추정
        print('\n[6] 내용 저장 구조 추정')

        # Para가 모두 빈 문단인지 확인
        hwp.Run("MoveDocBegin")
        hwp.Run("SelectAll")
        hwp.Run("Copy")
        time.sleep(0.2)

        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            try:
                text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                text_length = len(text.strip()) if text else 0
            except:
                text_length = 0
            finally:
                win32clipboard.CloseClipboard()
        except:
            text_length = 0

        hwp.Run("Cancel")

        print(f'전체 선택 후 복사한 텍스트 길이: {text_length}자')

        if text_length > 0:
            print('✅ 문서에 실제 텍스트 내용 있음')
            print('   → Para가 빈 문단이어도 다른 구조(표, 개체 등)에 내용 저장')
        else:
            print('⚠️  텍스트 없음 (순수 구조만)')

        # 결과 요약
        print('\n' + '=' * 70)
        print('구조 분석 결과')
        print('=' * 70)
        print(f'파일: {file_path.name}')
        print(f'페이지: {page_count}')
        print(f'Para 범위: 0 ~ {doc_end[1]}')
        print(f'표 개수: {table_count if "table_count" in locals() else "확인 불가"}')
        print(f'List 개수: {1 + len(other_lists)}')
        print(f'텍스트 길이: {text_length}자')
        print()
        print('핵심 발견:')
        if text_length > 0 and doc_end[1] > 0:
            print('  - Para는 모두 빈 문단이지만 실제 내용은 존재')
            print('  - 내용은 표, 개체, 또는 특수 구조에 저장')
            print('  - Copy-Paste는 이런 복잡한 구조를 통째로 복사')
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

    success = analyze_document_structure(file_path)
    sys.exit(0 if success else 1)
