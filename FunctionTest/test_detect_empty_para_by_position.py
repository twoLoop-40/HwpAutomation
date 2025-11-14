"""
위치 비교로 빈 문단 감지

아이디어:
1. 각 문단의 시작 위치와 끝 위치를 GetPos()로 가져옴
2. 시작 == 끝 → 빈 문단
3. 시작 != 끝 → 내용 있는 문단
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


def check_para_by_position(hwp, para_num: int) -> dict:
    """
    위치 비교로 문단 내용 확인

    Returns:
        dict: {
            'para': para 번호,
            'start_pos': 시작 위치,
            'end_pos': 끝 위치,
            'is_empty': 빈 문단 여부,
        }
    """
    try:
        # Para 시작으로 이동
        set_result = hwp.SetPos(0, para_num, 0)

        if not set_result:
            return {
                'para': para_num,
                'start_pos': None,
                'end_pos': None,
                'is_empty': None,
                'error': 'SetPos 실패',
            }

        # 시작 위치
        start_pos = hwp.GetPos()

        # Para 끝으로 이동
        hwp.Run("MoveParagraphEnd")
        time.sleep(0.05)

        # 끝 위치
        end_pos = hwp.GetPos()

        # 비교
        is_empty = (start_pos == end_pos)

        return {
            'para': para_num,
            'start_pos': start_pos,
            'end_pos': end_pos,
            'is_empty': is_empty,
        }

    except Exception as e:
        return {
            'para': para_num,
            'start_pos': None,
            'end_pos': None,
            'is_empty': None,
            'error': str(e),
        }


def test_detect_empty_para_by_position():
    """위치 비교로 빈 문단 감지"""

    print('=' * 70)
    print('위치 비교로 빈 문단 감지')
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

        # Para별 위치 확인
        print('\n[Para별 위치 확인]')
        print('-' * 70)

        paras_with_content = []
        paras_empty = []

        for para_num in range(70):  # 최대 70개 Para
            info = check_para_by_position(hwp, para_num)

            if 'error' in info:
                print(f'\nPara {para_num}부터 존재하지 않음')
                break

            if info['is_empty']:
                paras_empty.append(para_num)
            else:
                paras_with_content.append(para_num)
                start = info['start_pos']
                end = info['end_pos']
                print(f'Para {para_num:2d}: {start} → {end} (내용 있음)')

        # 통계
        print('\n' + '=' * 70)
        print('통계')
        print('=' * 70)
        print(f'총 Para 수: {len(paras_with_content) + len(paras_empty)}')
        print(f'내용 있는 Para: {len(paras_with_content)}개')
        print(f'  {paras_with_content}')
        print(f'빈 Para: {len(paras_empty)}개')
        print(f'  {paras_empty}')

        # ColumnTracker 예상 결과와 비교
        print('\n[ColumnTracker 예상 결과와 비교]')
        print('-' * 70)
        print('ColumnTracker 삽입 범위:')
        expected_para_ranges = [
            (0, 9), (9, 18), (18, 21), (21, 27), (27, 32),
            (32, 33), (33, 41), (41, 47), (47, 51), (51, 56)
        ]

        for i, (start, end) in enumerate(expected_para_ranges, 1):
            print(f'  문항 {i:2d}: Para {start} → {end}')

        # 예상되는 내용 있는 Para
        expected_paras = set()
        for start, end in expected_para_ranges:
            for p in range(start, end + 1):
                expected_paras.add(p)

        print(f'\n예상 내용 있는 Para: {sorted(expected_paras)}')

        # 실제 vs 예상 비교
        actual_paras = set(paras_with_content)
        missing = expected_paras - actual_paras
        extra = actual_paras - expected_paras

        print('\n비교 결과:')
        if missing:
            print(f'  ⚠️  예상했지만 빈 Para: {sorted(missing)}')
        if extra:
            print(f'  ⚠️  예상 밖의 내용 있는 Para: {sorted(extra)}')

        if not missing and not extra:
            print(f'  ✅ 완벽하게 일치! 빈 칼럼 감지 성공')

        # 칼럼별 분류
        print('\n[칼럼별 분류 (2단 가정)]')
        print('-' * 70)

        # ColumnTracker 정보 기반 칼럼 분류
        column_map = {}
        for i, (start_para, end_para) in enumerate(expected_para_ranges, 1):
            page = ((i - 1) // 2) + 1
            column = ((i - 1) % 2) + 1

            column_key = (page, column)
            if column_key not in column_map:
                column_map[column_key] = []

            column_map[column_key].append({
                'problem': i,
                'para_range': (start_para, end_para),
                'has_content': any(p in paras_with_content for p in range(start_para, end_para + 1))
            })

        # 칼럼별 출력
        for (page, column), items in sorted(column_map.items()):
            has_content = all(item['has_content'] for item in items)
            status = "✅ 내용 있음" if has_content else "❌ 빈 칼럼"

            print(f'\nPage {page}, Column {column}: {status}')
            for item in items:
                start, end = item['para_range']
                content_status = "✅" if item['has_content'] else "❌"
                print(f'  문항 {item["problem"]:2d} {content_status}: Para {start} → {end}')

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
    success = test_detect_empty_para_by_position()
    sys.exit(0 if success else 1)
