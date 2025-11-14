"""
파일 #4 상세 구조 분석

2페이지, 6개 Para - 구조를 상세히 확인
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

# File #4
problem_file = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905/2025 커팅 S_공수2_기말_4회차_2_3_15.hwp")

print('=' * 70)
print('File #4 상세 구조 분석')
print('=' * 70)
print(f'파일: {problem_file.name}')
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
    # 모든 문서 닫기
    print('[0] 기존 문서 정리...')
    try:
        while hwp.XHwpDocuments.Count > 0:
            hwp.Clear(1)
            time.sleep(0.1)
        print(f'✅ 정리 완료')
    except:
        pass

    # 파일 열기
    print('\n[1] 파일 열기...')
    print(f'   경로: {problem_file}')
    print(f'   존재: {problem_file.exists()}')
    result = hwp.Open(str(problem_file.absolute()), "HWP", "")
    print(f'   Open() 반환값: {result}')
    time.sleep(0.5)  # 대기 시간 증가

    pages = hwp.PageCount
    print(f'✅ 열기 완료 - 페이지: {pages}')

    # 문서가 실제로 열렸는지 확인
    try:
        doc_count = hwp.XHwpDocuments.Count
        print(f'   열린 문서 수: {doc_count}')
        if doc_count > 0:
            active_doc = hwp.XHwpDocuments.Active_XHwpDocument
            print(f'   활성 문서: {active_doc}')
    except Exception as e:
        print(f'   문서 확인 실패: {e}')

    # Para별 상세 정보
    print('\n[2] Para별 상세 정보:')
    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    para_num = 0
    max_paras = 50

    print(f'{"Para":<6} {"위치(List,Page,Pos)":<25} {"길이":<6} {"내용 (첫 50자)"}')
    print('-' * 100)

    while para_num < max_paras:
        # Para 시작 위치
        start_pos = hwp.GetPos()

        # Para 선택
        hwp.Run("MoveParaEnd")
        hwp.Run("MoveSelParaBegin")
        time.sleep(0.02)

        # Para 텍스트 가져오기
        try:
            text = hwp.GetText()
            if isinstance(text, tuple):
                text = text[1] if len(text) > 1 else ""
            text_len = len(text)
            text_preview = text[:50].replace('\n', '\\n').replace('\r', '\\r') if text else "(빈)"
        except:
            text_len = 0
            text_preview = "(에러)"

        # Para 끝 위치
        hwp.Run("Cancel")
        hwp.Run("MoveParaEnd")
        end_pos = hwp.GetPos()

        # 출력
        pos_str = f"({start_pos[0]},{start_pos[1]},{start_pos[2]})"
        print(f'{para_num:<6} {pos_str:<25} {text_len:<6} {text_preview}')

        # 다음 Para로 이동
        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)
        after_pos = hwp.GetPos()

        # 위치가 변하지 않으면 마지막
        if after_pos == before_pos:
            break

        # 페이지가 바뀌었는지 확인
        if after_pos[0] != before_pos[0]:
            print(f'       ↓ 페이지 전환: {before_pos[0]} → {after_pos[0]}')

        para_num += 1

    print('-' * 100)
    print(f'총 Para: {para_num + 1}개')

    # 전체 텍스트 길이
    print('\n[3] 전체 텍스트:')
    hwp.Run("MoveDocBegin")
    hwp.Run("SelectAll")
    time.sleep(0.1)
    all_text = hwp.GetText()
    if isinstance(all_text, tuple):
        all_text = all_text[1] if len(all_text) > 1 else ""
    print(f'   전체 길이: {len(all_text)}자')
    print(f'   첫 200자:\n{all_text[:200]}')

    print('\n' + '=' * 70)
    print('분석 완료')
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
