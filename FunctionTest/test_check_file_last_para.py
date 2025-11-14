"""
특정 문항 파일의 마지막 para 확인

목적: 문항 파일을 열어서 마지막 para 위치를 확인
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


def check_file_last_para(file_path: Path):
    """파일의 마지막 para 확인"""

    print('=' * 70)
    print(f'파일 마지막 Para 확인: {file_path.name[:50]}...')
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

        # 문서 시작 위치
        print('\n[2] 문서 시작 위치')
        hwp.Run("MoveDocBegin")
        doc_begin_pos = hwp.GetPos()
        print(f'MoveDocBegin() → {doc_begin_pos}')

        # 문서 끝 위치
        print('\n[3] 문서 끝 위치')
        hwp.Run("MoveDocEnd")
        doc_end_pos = hwp.GetPos()
        print(f'MoveDocEnd() → {doc_end_pos}')
        print(f'마지막 para: {doc_end_pos[1]}')

        # 페이지 수
        page_count = hwp.PageCount
        print(f'\n페이지 수: {page_count}')

        # Para별 매핑 (끝 위치 para까지)
        print(f'\n[4] Para 0 ~ {doc_end_pos[1]} 매핑')
        for para in range(doc_end_pos[1] + 1):
            # 시작 위치
            hwp.SetPos(0, para, 0)
            start_pos = hwp.GetPos()

            # 끝 위치 찾기
            if start_pos[1] == para:  # SetPos 성공한 경우만
                hwp.Run("MoveParagraphEnd")
                end_pos = hwp.GetPos()
                print(f'Para {para:2d}: SetPos(0, {para}, 0) → {start_pos}, 끝 → {end_pos}, 길이: {end_pos[2]}자')
            else:
                print(f'Para {para:2d}: 접근 불가 (자동 이동 → {start_pos})')

        # 결과 요약
        print('\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'파일: {file_path.name}')
        print(f'문서 시작: {doc_begin_pos}')
        print(f'문서 끝: {doc_end_pos}')
        print(f'마지막 para: {doc_end_pos[1]}')
        print(f'페이지 수: {page_count}')
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
    # 파일 경로
    file_path = Path(r"C:\Users\joonho.lee\Projects\AutoHwp\Tests\E2ETest\[내신대비]휘문고_2_기말_1회_20251112_0905\RPM 공통수학Ⅱ 07. 명제 134제_13_14문항_6_18.hwp")

    success = check_file_last_para(file_path)
    sys.exit(0 if success else 1)
