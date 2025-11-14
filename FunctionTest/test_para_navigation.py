"""
Para 네비게이션 명령으로 빈 문단 감지

아이디어:
- MovePrevParaEnd, MoveNextParaBegin 등으로 실제 Para 이동
- 이동 전후 GetPos() 비교로 빈 문단 감지
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


def scan_paras_with_navigation(hwp, max_iterations: int = 100):
    """
    네비게이션 명령으로 Para 스캔

    전략:
    1. 문서 시작으로 이동
    2. MoveNextParaBegin 반복
    3. 이동 전후 위치 비교
    4. 위치가 변경되면 새 Para 발견
    """
    print('\n[Para 네비게이션 스캔]')
    print('-' * 70)

    paras = []

    # 문서 시작
    hwp.Run("MoveDocBegin")
    time.sleep(0.1)

    prev_pos = hwp.GetPos()
    print(f'시작 위치: {prev_pos}')

    paras.append({
        'index': 0,
        'pos': prev_pos,
    })

    # MoveNextParaBegin 반복
    for i in range(max_iterations):
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.05)

        curr_pos = hwp.GetPos()

        # 위치가 변경되지 않으면 종료 (더 이상 Para 없음)
        if curr_pos == prev_pos:
            print(f'\n더 이상 Para 없음 (위치 변경 없음)')
            break

        paras.append({
            'index': i + 1,
            'pos': curr_pos,
        })

        print(f'Para {i + 1:2d}: {curr_pos}')

        prev_pos = curr_pos

    return paras


def scan_para_ends(hwp, max_iterations: int = 100):
    """
    MovePrevParaEnd / MoveParaEnd 방식으로 스캔
    """
    print('\n[Para 끝 위치 스캔]')
    print('-' * 70)

    para_ends = []

    # 문서 시작
    hwp.Run("MoveDocBegin")
    time.sleep(0.1)

    for i in range(max_iterations):
        # 현재 Para 끝으로 이동
        hwp.Run("MoveParaEnd")
        time.sleep(0.05)

        end_pos = hwp.GetPos()

        para_ends.append({
            'index': i,
            'end_pos': end_pos,
        })

        print(f'Para {i:2d} 끝: {end_pos}')

        # 다음 Para 시작으로 이동
        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.05)

        after_pos = hwp.GetPos()

        # 위치가 변경되지 않으면 종료
        if after_pos == before_pos:
            print(f'\n더 이상 Para 없음')
            break

    return para_ends


def test_para_navigation():
    """Para 네비게이션 명령 테스트"""

    print('=' * 70)
    print('Para 네비게이션 명령 테스트')
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

        # 방법 1: MoveNextParaBegin
        paras = scan_paras_with_navigation(hwp, max_iterations=20)

        print(f'\n총 {len(paras)}개 Para 발견 (MoveNextParaBegin)')

        # 방법 2: MoveParaEnd + MoveNextParaBegin
        para_ends = scan_para_ends(hwp, max_iterations=20)

        print(f'\n총 {len(para_ends)}개 Para 발견 (MoveParaEnd)')

        # 분석
        print('\n' + '=' * 70)
        print('분석')
        print('=' * 70)

        if len(paras) > 0:
            print(f'✅ Para 네비게이션으로 {len(paras)}개 Para 감지 성공!')
            print(f'\n발견된 Para 위치:')
            for p in paras[:10]:  # 처음 10개만
                print(f'  Para {p["index"]:2d}: {p["pos"]}')

            if len(paras) > 10:
                print(f'  ... 외 {len(paras) - 10}개')

        else:
            print(f'⚠️  Para를 찾을 수 없습니다')

        # ColumnTracker 예상과 비교
        print('\n[ColumnTracker 예상 결과와 비교]')
        print('-' * 70)
        print('ColumnTracker는 10개 문항을 삽입했습니다.')
        print('예상: Para 위치가 문항별로 구분되어야 함')

        if len(paras) >= 10:
            print(f'\n✅ {len(paras)}개 Para 발견 - 10개 문항과 대략 일치!')
        else:
            print(f'\n⚠️  {len(paras)}개 Para만 발견 - 10개 문항보다 적음')

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
    success = test_para_navigation()
    sys.exit(0 if success else 1)
