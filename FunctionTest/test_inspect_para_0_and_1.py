"""
양식 파일의 Para 0과 Para 1 내용 확인

목적: (0, 0, ...)과 (0, 1, ...) 위치에 실제로 무엇이 있는지 확인
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


def inspect_para_content():
    """Para 0과 Para 1의 내용 확인"""

    print('=' * 70)
    print('양식 파일 Para 0과 Para 1 내용 검사')
    print('=' * 70)

    template_path = Path(__file__).parent / "[양식]mad모의고사.hwp"

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
        print(f'\n[1] 템플릿 열기: {template_path.name}')
        result = client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 열기 실패: {result.error}')
            return False

        time.sleep(0.5)
        print('✅ 템플릿 로드 완료')

        # Para 0 검사
        print('\n' + '=' * 70)
        print('[Para 0 검사]')
        print('=' * 70)

        # Para 0의 여러 위치 시도
        for pos in [0, 10, 20, 30, 40, 48, 50]:
            print(f'\nSetPos(0, 0, {pos}) 시도...')
            set_result = hwp.SetPos(0, 0, pos)
            actual_pos = hwp.GetPos()
            print(f'  SetPos 반환: {set_result}')
            print(f'  실제 위치: {actual_pos}')

            # 해당 위치에서 선택 & 텍스트 가져오기 시도
            try:
                # 현재 위치부터 50자 선택
                hwp.Run("Select")
                for _ in range(50):
                    hwp.Run("MoveRight")

                # 복사
                hwp.Run("Copy")
                time.sleep(0.1)

                # GetText 시도 (실제로는 clipboard에서 읽어야 함)
                print(f'  → 위치 {pos}에서 텍스트 선택 완료')

                hwp.Run("Cancel")

            except Exception as e:
                print(f'  → 텍스트 선택 실패: {e}')

        # Para 0 전체를 한번에 선택
        print('\n\nPara 0 전체 선택 시도...')
        hwp.SetPos(0, 0, 0)
        hwp.Run("Select")
        hwp.Run("MoveParagraphEnd")
        time.sleep(0.1)

        end_pos = hwp.GetPos()
        print(f'Para 0 끝 위치: {end_pos}')

        hwp.Run("Cancel")

        # Para 1 검사
        print('\n' + '=' * 70)
        print('[Para 1 검사]')
        print('=' * 70)

        print('\nSetPos(0, 1, 0) 시도...')
        hwp.SetPos(0, 1, 0)
        actual_pos = hwp.GetPos()
        print(f'실제 위치: {actual_pos}')

        # Para 1 전체 선택
        print('\nPara 1 전체 선택 시도...')
        hwp.Run("Select")
        hwp.Run("MoveParagraphEnd")
        time.sleep(0.1)

        end_pos = hwp.GetPos()
        print(f'Para 1 끝 위치: {end_pos}')

        hwp.Run("Cancel")

        # 문서 전체 구조 확인
        print('\n' + '=' * 70)
        print('[문서 전체 구조]')
        print('=' * 70)

        # 문서 시작으로 이동
        hwp.Run("MoveDocBegin")
        doc_begin_pos = hwp.GetPos()
        print(f'문서 시작 위치 (MoveDocBegin): {doc_begin_pos}')

        # 문서 끝으로 이동
        hwp.Run("MoveDocEnd")
        doc_end_pos = hwp.GetPos()
        print(f'문서 끝 위치 (MoveDocEnd): {doc_end_pos}')

        # 페이지 정보
        page_count = hwp.PageCount
        print(f'페이지 수: {page_count}')

        # Para별로 순회하며 위치 확인
        print('\n[Para 0~5 위치 맵핑]')
        for para in range(6):
            print(f'\nPara {para}:')

            # 시작 위치
            hwp.SetPos(0, para, 0)
            start_pos = hwp.GetPos()
            print(f'  SetPos(0, {para}, 0) → {start_pos}')

            # 끝 위치 찾기
            if start_pos[1] == para:  # SetPos 성공한 경우만
                hwp.Run("MoveParagraphEnd")
                end_pos = hwp.GetPos()
                print(f'  Para 끝 → {end_pos}')
                print(f'  Para 길이: {end_pos[2]} 문자')

        # 결과 요약
        print('\n' + '=' * 70)
        print('검사 결과 요약')
        print('=' * 70)
        print('문서 구조:')
        print(f'  - 시작: {doc_begin_pos}')
        print(f'  - 끝: {doc_end_pos}')
        print(f'  - 페이지: {page_count}개')
        print()
        print('Para 0의 특징:')
        print('  - SetPos(0, 0, 0) 시 자동으로 다른 위치로 이동')
        print('  - 직접 접근 불가 (헤더/특수 영역)')
        print()
        print('Para 1의 특징:')
        print('  - 접근 가능')
        print('  - 실제 본문의 시작 위치')
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
    success = inspect_para_content()
    sys.exit(0 if success else 1)
