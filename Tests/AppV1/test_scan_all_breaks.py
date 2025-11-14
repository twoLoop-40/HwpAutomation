"""
원본 파일들의 모든 Break 조사

Break 종류:
- BreakColDef: 단 정의 삽입
- BreakColumn: 단 나누기
- BreakLine: line break
- BreakPage: 쪽 나누기
- BreakPara: 문단 나누기
- BreakSection: 구역 나누기

방법: GetText()로 특수 문자 코드 확인 또는 Para 순회하며 페이지/구역 변경 감지
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

# 모든 문항 파일
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files_paths = [f for f in all_files if not f.name.startswith('[문항')]

print('=' * 80)
print('원본 파일 Break 종합 조사')
print('=' * 80)
print(f'총 파일: {len(problem_files_paths)}개')
print()

# 클라이언트 초기화
client = AutomationClient()
hwp = client.hwp

# 보안 모듈
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 창 숨기기
try:
    hwp.XHwpWindows.Item(0).Visible = False
except:
    pass

# 결과 저장
results = []

try:
    for i, file_path in enumerate(problem_files_paths, 1):
        try:
            # 기존 문서 모두 닫기
            while hwp.XHwpDocuments.Count > 0:
                hwp.Clear(1)
                time.sleep(0.05)

            # 파일 열기
            open_result = hwp.Open(str(file_path.absolute()), "HWP", "")
            time.sleep(0.15)

            if not open_result and hwp.PageCount < 1:
                print(f'[{i:2d}] ❌ 열기 실패: {file_path.name[:40]}')
                continue

            pages = hwp.PageCount

            # Break 감지: Para 순회하며 페이지/구역 변경 확인
            hwp.Run("MoveDocBegin")
            time.sleep(0.02)

            page_breaks = 0
            section_breaks = 0
            para_count = 0
            max_paras = 300

            prev_page = 0
            prev_list = 0

            while para_count < max_paras:
                # 현재 위치
                pos = hwp.GetPos()
                curr_list = pos[0]
                curr_page = pos[1]

                # 페이지가 바뀌면 BreakPage
                if para_count > 0 and curr_page != prev_page:
                    page_breaks += 1

                # List가 바뀌면 BreakSection (구역)
                if para_count > 0 and curr_list != prev_list:
                    section_breaks += 1

                prev_page = curr_page
                prev_list = curr_list

                # Para 끝으로 이동
                hwp.Run("MoveParaEnd")
                time.sleep(0.01)

                # 다음 Para로 이동
                before_pos = hwp.GetPos()
                hwp.Run("MoveNextParaBegin")
                time.sleep(0.01)
                after_pos = hwp.GetPos()

                # 위치가 변하지 않으면 마지막
                if after_pos == before_pos:
                    break

                para_count += 1

            # 결과 저장
            result = {
                'index': i,
                'name': file_path.name,
                'pages': pages,
                'paras': para_count + 1,
                'page_breaks': page_breaks,
                'section_breaks': section_breaks,
            }
            results.append(result)

            # 출력
            marker = ' << 주의!' if (page_breaks > 0 or section_breaks > 0) else ''
            print(f'[{i:2d}] P:{pages:2d} Para:{para_count+1:3d} PgBr:{page_breaks} SecBr:{section_breaks}{marker}')

            # 파일 닫기
            hwp.Clear(1)
            time.sleep(0.05)

        except Exception as e:
            print(f'[{i:2d}] ❌ 오류: {str(e)[:40]}')
            try:
                hwp.Clear(1)
            except:
                pass

    print('\n' + '=' * 80)
    print('조사 완료')
    print('=' * 80)
    print(f'총 파일: {len(results)}개')

    # BreakPage가 있는 파일들
    page_break_files = [r for r in results if r['page_breaks'] > 0]
    print(f'\nBreakPage 포함 파일: {len(page_break_files)}개')
    for r in page_break_files:
        print(f'  [{r["index"]:2d}] {r["name"][:50]:50s} (PgBr:{r["page_breaks"]})')

    # BreakSection이 있는 파일들
    section_break_files = [r for r in results if r['section_breaks'] > 0]
    print(f'\nBreakSection 포함 파일: {len(section_break_files)}개')
    for r in section_break_files:
        print(f'  [{r["index"]:2d}] {r["name"][:50]:50s} (SecBr:{r["section_breaks"]})')

    print('=' * 80)

except Exception as e:
    print(f'\n💥 오류 발생: {e}')
    import traceback
    traceback.print_exc()

finally:
    # 정리
    try:
        while hwp.XHwpDocuments.Count > 0:
            hwp.Clear(1)
            time.sleep(0.05)
    except:
        pass
    client.cleanup()
    time.sleep(0.5)
