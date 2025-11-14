"""
합병 결과 파일에서 BreakPage 확인

사용자가 말한 "4번 파일 BreakPage 문제"는
합병된 결과 파일의 4번째 문항 위치를 의미하는 것 같음
"""
import sys
import codecs
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 합병 결과 파일
result_file = Path("Tests/AppV1/결과_Merger_40문항.hwp")

if not result_file.exists():
    print(f'❌ 결과 파일이 없습니다: {result_file}')
    sys.exit(1)

print('=' * 70)
print('합병 결과 파일 BreakPage 분석')
print('=' * 70)
print(f'파일: {result_file.name}')
print()

# 클라이언트 초기화
client = AutomationClient()
hwp = client.hwp

# 보안 모듈
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 창 보이기 (디버깅용)
try:
    hwp.XHwpWindows.Item(0).Visible = True
except:
    pass

try:
    # 1. 파일 열기
    print('[1] 파일 열기...')
    hwp.Open(str(result_file.absolute()), "HWP", "")
    time.sleep(0.3)

    total_pages = hwp.PageCount
    print(f'✅ 열기 완료 - 총 페이지: {total_pages}')

    # 2. BreakPage 찾기
    print('\n[2] BreakPage 위치 찾기...')
    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    page_breaks = []
    para_num = 0
    max_paras = 500

    while para_num < max_paras:
        # 현재 위치
        start_pos = hwp.GetPos()
        start_page = start_pos[0]

        # Para 끝으로 이동
        hwp.Run("MoveParaEnd")
        time.sleep(0.01)
        end_pos = hwp.GetPos()

        # 다음 Para로 이동
        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.01)
        after_pos = hwp.GetPos()

        # 위치가 변하지 않으면 마지막
        if after_pos == before_pos:
            break

        # 페이지가 바뀌면 BreakPage
        after_page = after_pos[0]
        if after_page != start_page:
            page_breaks.append({
                'para_num': para_num,
                'from_page': start_page,
                'to_page': after_page,
            })

        para_num += 1

    print(f'✅ Para 스캔 완료: {para_num}개')
    print(f'✅ BreakPage 발견: {len(page_breaks)}개')

    # 3. BreakPage 상세 정보
    if page_breaks:
        print('\n[3] BreakPage 위치:')
        for i, bp in enumerate(page_breaks[:20], 1):  # 처음 20개만
            print(f'   [{i:2d}] Para {bp["para_num"]:3d}: 페이지 {bp["from_page"]:2d} → {bp["to_page"]:2d}')

        if len(page_breaks) > 20:
            print(f'   ... ({len(page_breaks) - 20}개 더 있음)')

    # 4. 문항 4번 근처 BreakPage 확인 (BreakColumn은 약 40개, 문항 4번은 3번째 BreakPage 근처)
    print('\n[4] 문항 4번 근처 BreakPage (3~5번째 BreakPage):')
    if len(page_breaks) >= 5:
        for i in range(2, 5):  # 3, 4, 5번째
            bp = page_breaks[i]
            print(f'   [{i+1}번째 BreakPage] Para {bp["para_num"]}: {bp["from_page"]} → {bp["to_page"]}')

    print('\n' + '=' * 70)
    print('분석 완료')
    print('=' * 70)
    print(f'총 페이지: {total_pages}')
    print(f'총 Para: {para_num}')
    print(f'총 BreakPage: {len(page_breaks)}개')
    print('=' * 70)

except Exception as e:
    print(f'\n💥 오류 발생: {e}')
    import traceback
    traceback.print_exc()

finally:
    # 정리
    try:
        client.close_document()
    except:
        pass
    client.cleanup()
    time.sleep(0.5)
