"""
File #4 단독 전처리 테스트

merger.py의 process_single_problem 로직을 그대로 실행해서
실제로 어떤 상태가 되는지 확인
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
from AppV1.para_scanner import scan_paras, remove_empty_paras
from AppV1.column import convert_to_single_column

# File #4
problem_file = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905/2025 커팅 S_공수2_기말_4회차_2_3_15.hwp")
problem_file = problem_file.absolute()

print('=' * 70)
print('File #4 전처리 테스트')
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
    # 1. 파일 열기
    print('[1] 파일 열기...')
    hwp.Open(str(problem_file), "HWP", "")
    time.sleep(0.2)

    if hwp.PageCount < 1:
        print(f'❌ 빈 문서')
        sys.exit(1)

    initial_pages = hwp.PageCount
    print(f'✅ 열기 완료 - 초기 페이지: {initial_pages}')

    # 텍스트 확인
    hwp.Run("MoveDocBegin")
    hwp.Run("SelectAll")
    time.sleep(0.1)
    text = hwp.GetText()
    print(f'   전체 텍스트 길이: {len(text)} 자')
    if len(text) > 100:
        print(f'   첫 100자: {str(text)[:100]}...')
    else:
        print(f'   전체 텍스트: {text}')

    # 2. 1단으로 변환
    print('\n[2] 1단으로 변환...')
    convert_to_single_column(hwp)
    print(f'✅ 변환 완료 - 페이지: {hwp.PageCount}')

    # 3. Para 스캔
    print('\n[3] Para 스캔...')
    paras = scan_paras(hwp)
    empty_count = sum(1 for p in paras if p.is_empty)
    print(f'✅ Para 수: {len(paras)}')
    print(f'   빈 Para: {empty_count}개')

    # Para 상세 정보 (처음 10개 + 마지막 10개)
    print('\n   [처음 10개 Para]')
    for i, p in enumerate(paras[:10]):
        empty_mark = ' (빈)' if p.is_empty else ''
        print(f'     [{i:2d}] {p}{empty_mark}')

    if len(paras) > 20:
        print('   ...')
        print('\n   [마지막 10개 Para]')
        for i, p in enumerate(paras[-10:], len(paras) - 10):
            empty_mark = ' (빈)' if p.is_empty else ''
            print(f'     [{i:2d}] {p}{empty_mark}')

    # 4. 빈 Para 제거
    print('\n[4] 빈 Para 제거 (뒤에서부터)...')
    removed = remove_empty_paras(hwp, paras)
    print(f'✅ 제거 완료: {removed}개')
    print(f'   최종 페이지: {hwp.PageCount}')

    # 5. 최종 상태 확인
    print('\n[5] 최종 상태 확인...')
    final_paras = scan_paras(hwp)
    print(f'✅ 최종 Para 수: {len(final_paras)}')
    print(f'   빈 Para: {sum(1 for p in final_paras if p.is_empty)}개')

    print('\n' + '=' * 70)
    print('처리 완료')
    print('=' * 70)
    print(f'초기 페이지: {initial_pages} → 최종 페이지: {hwp.PageCount}')
    print(f'초기 Para: {len(paras)} → 최종 Para: {len(final_paras)}')
    print(f'제거된 빈 Para: {removed}개')
    print('=' * 70)

    # 파일 닫기 (저장하지 않음)

except Exception as e:
    print(f'\n💥 오류 발생: {e}')
    import traceback
    traceback.print_exc()

finally:
    # 정리
    client.close_document()
    client.cleanup()
    time.sleep(0.5)
