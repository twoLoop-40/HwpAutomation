"""
2페이지 파일의 구조 분석

목적:
1. PageBreak 또는 SectionBreak가 있는지 확인
2. Para별 내용 확인
3. 페이지 나누기를 제거할 수 있는지 테스트
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


def analyze_2page_structure():
    """2페이지 파일 구조 분석"""

    print('=' * 70)
    print('2페이지 파일 구조 분석')
    print('=' * 70)

    # 파일 경로
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    all_files = sorted(problem_dir.glob("*.hwp"))
    test_file = all_files[3]  # 2025 커팅 S_공수2_기말_4회차_2_3_15.hwp

    print(f'\n[1/3] 파일 열기: {test_file.name}')

    client = AutomationClient()
    hwp = client.hwp

    # 보안 모듈
    hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

    # 창 숨기기
    try:
        hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    result = client.open_document(str(test_file))
    if not result.success:
        print(f'❌ 파일 열기 실패: {result.error}')
        return

    time.sleep(0.3)

    page_count = hwp.PageCount
    print(f'✅ 페이지 수: {page_count}')

    try:
        # [2/3] Para 스캔
        print(f'\n[2/3] Para 구조 분석...')

        hwp.Run('MoveDocBegin')
        time.sleep(0.05)

        para_num = 0
        paras = []

        while True:
            start_pos = hwp.GetPos()

            # Para 끝으로 이동
            hwp.Run('MoveParaEnd')
            time.sleep(0.02)

            end_pos = hwp.GetPos()

            # Para 내용 가져오기 시도
            try:
                hwp.SetPos(start_pos[0], start_pos[1], start_pos[2])
                hwp.Run('MoveParaEnd')
                hwp.Run('MoveSelParaBegin')
                time.sleep(0.02)

                para_text = hwp.GetSelectedText()

                # 첫 30글자만
                preview = para_text[:30] if para_text else ""
            except:
                preview = "(내용 없음)"

            para_info = {
                'num': para_num,
                'start': start_pos,
                'end': end_pos,
                'is_empty': (end_pos[2] == 0),
                'preview': preview
            }

            paras.append(para_info)

            print(f'  Para {para_num:2d}: pos={start_pos} → {end_pos}, empty={para_info["is_empty"]}, preview="{preview}"')

            # 다음 Para로
            hwp.Run('Cancel')
            before_pos = hwp.GetPos()
            hwp.Run('MoveNextParaBegin')
            time.sleep(0.02)

            after_pos = hwp.GetPos()

            if after_pos == before_pos:
                break

            para_num += 1

            if para_num > 20:
                print('  (20개 Para 제한)')
                break

        print(f'\n총 {len(paras)}개 Para')
        print(f'빈 Para: {sum(1 for p in paras if p["is_empty"])}개')

        # [3/3] 구조 분석 - Para 위치 기반
        print(f'\n[3/3] 구조 분석...')

        # Para들의 list 번호 분석
        list_numbers = [p['start'][0] for p in paras]
        unique_lists = set(list_numbers)

        print(f'  사용된 list 번호: {sorted(unique_lists)}')
        print(f'  list 개수: {len(unique_lists)}개')

        # 2페이지가 되는 이유 추정
        print(f'\n  분석:')
        if len(paras) > 5:
            print(f'    - Para가 많아서 2페이지가 된 것으로 추정')
        if sum(1 for p in paras if p['is_empty']) > 0:
            print(f'    - 빈 Para {sum(1 for p in paras if p["is_empty"])}개 존재')

        print(f'\n  해결 방법:')
        print(f'    1. 빈 Para 제거 (MoveSelDown)')
        print(f'    2. 여백/용지 크기 조정')
        print(f'    3. 현재 상태 그대로 사용 (2페이지 유지)')

        # 결과 요약
        print(f'\n' + '=' * 70)
        print('분석 결과')
        print('=' * 70)
        print(f'파일: {test_file.name}')
        print(f'페이지 수: {page_count}')
        print(f'Para 수: {len(paras)}')
        print(f'빈 Para: {sum(1 for p in paras if p["is_empty"])}개')
        print('=' * 70)

    finally:
        # 정리
        client.close_document()
        client.cleanup()


if __name__ == "__main__":
    analyze_2page_structure()
