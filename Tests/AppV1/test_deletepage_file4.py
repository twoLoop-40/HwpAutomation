"""
File #4 DeletePage 테스트

문제: 첫 페이지에서 BreakPage 후 엔터 2번 → 무조건 페이지 넘어감
해결: DeletePage 액션으로 페이지 제거 가능한지 확인

HwpIdris/Actions/Text.idr:
- DeletePage: "쪽 지우기"
- ParameterSet: Range, RangeCustom
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

# 문제 파일 #4
problem_file = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905/2025 커팅 S_공수2_기말_4회차_2_3_15.hwp")
problem_file = problem_file.absolute()

print('=' * 70)
print('File #4 DeletePage 테스트')
print('=' * 70)
print(f'파일: {problem_file.name}')
print(f'문제: 첫 페이지 BreakPage + 엔터 2번 → 페이지 넘어감')
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
    print(f'경로: {problem_file}')
    print(f'파일 존재: {problem_file.exists()}')

    # HWP COM API 직접 사용 (경로 문제 우회)
    hwp.Open(str(problem_file), "HWP", "")
    time.sleep(0.2)

    initial_pages = hwp.PageCount
    print(f'✅ 열기 완료 - 초기 페이지: {initial_pages}')

    # 기본 정보 확인
    print(f'   PageCount: {hwp.PageCount}')

    # 텍스트 전체 선택 및 확인
    hwp.Run("MoveDocBegin")
    hwp.Run("SelectAll")
    time.sleep(0.1)
    text = hwp.GetText()
    print(f'   전체 텍스트 길이: {len(text)} 자')
    print(f'   첫 50자: {text[:50] if text else "(빈 문서)"}')

    # 2. 문서 구조 파악
    print('\n[2] 문서 구조 분석...')
    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    para_count = 0
    page_breaks = []

    while True:
        current_pos = hwp.GetPos()
        current_page = current_pos[0]  # list, page, pos

        # Para 끝으로 이동
        hwp.Run("MoveParaEnd")
        time.sleep(0.02)
        end_pos = hwp.GetPos()

        # Para 내용 확인 (빈 Para?)
        is_empty = (end_pos[2] == 0)

        # 페이지 나누기 확인 (다음 Para로 이동 시 페이지 변경?)
        before_page = hwp.GetPos()[0]
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)
        after_pos = hwp.GetPos()
        after_page = after_pos[0]

        # 페이지가 바뀌면 BreakPage
        if after_page != before_page:
            page_breaks.append((para_count, before_page, after_page))

        # 위치가 변하지 않으면 마지막 Para
        if after_pos == end_pos:
            break

        para_count += 1

        if para_count > 100:  # 안전 장치
            break

    print(f'✅ Para 수: {para_count}')
    print(f'✅ BreakPage 발견: {len(page_breaks)}개')
    for i, (para_num, before_page, after_page) in enumerate(page_breaks):
        print(f'   [{i+1}] Para {para_num} → 페이지 {before_page} → {after_page}')

    # 3. DeletePage 시도
    print('\n[3] DeletePage 시도...')

    if len(page_breaks) == 0:
        print('⚠️  BreakPage가 없습니다. 테스트 불가.')
    else:
        # 첫 번째 BreakPage 위치로 이동
        first_break_para = page_breaks[0][0]
        print(f'첫 번째 BreakPage 위치: Para {first_break_para}')

        # 해당 Para로 이동
        hwp.Run("MoveDocBegin")
        time.sleep(0.05)

        for _ in range(first_break_para):
            hwp.Run("MoveNextParaBegin")
            time.sleep(0.02)

        current_pos = hwp.GetPos()
        print(f'현재 위치: List={current_pos[0]}, Page={current_pos[1]}, Pos={current_pos[2]}')

        # DeletePage 액션 시도
        print('\n[시도 1] DeletePage 액션 (파라미터 없음)...')
        try:
            hwp.Run("DeletePage")
            time.sleep(0.2)
            after_pages = hwp.PageCount
            print(f'✅ DeletePage 실행 완료')
            print(f'   초기 페이지: {initial_pages} → 현재 페이지: {after_pages}')

            if after_pages < initial_pages:
                print(f'✅✅ 성공! 페이지가 {initial_pages - after_pages}개 줄었습니다!')
            else:
                print(f'⚠️  페이지 수가 변하지 않았습니다.')
        except Exception as e:
            print(f'❌ DeletePage 실패: {e}')

        # ParameterSet 사용 시도
        print('\n[시도 2] DeletePage with ParameterSet (Range=0)...')
        try:
            act = hwp.CreateAction("DeletePage")
            if act:
                pset = act.CreateSet()
                if pset:
                    act.GetDefault(pset)
                    pset.SetItem("Range", 0)  # 범위 설정 (0: 현재 페이지?)
                    result = act.Execute(pset)
                    time.sleep(0.2)

                    after_pages2 = hwp.PageCount
                    print(f'✅ DeletePage (Range=0) 실행 완료')
                    print(f'   이전 페이지: {after_pages} → 현재 페이지: {after_pages2}')

                    if after_pages2 < after_pages:
                        print(f'✅✅ 성공! 페이지가 {after_pages - after_pages2}개 더 줄었습니다!')
                    else:
                        print(f'⚠️  페이지 수가 변하지 않았습니다.')
                else:
                    print('❌ ParameterSet 생성 실패')
            else:
                print('❌ CreateAction 실패')
        except Exception as e:
            print(f'❌ DeletePage with ParameterSet 실패: {e}')

    print('\n' + '=' * 70)
    print('테스트 완료')
    print('=' * 70)
    print(f'초기 페이지: {initial_pages}')
    print(f'최종 페이지: {hwp.PageCount}')
    print(f'페이지 차이: {initial_pages - hwp.PageCount}')
    print('=' * 70)

    # 파일 닫기 (저장하지 않음)
    client.close_document()

except Exception as e:
    print(f'\n💥 오류 발생: {e}')
    import traceback
    traceback.print_exc()

finally:
    # 정리
    client.cleanup()
    time.sleep(0.5)
