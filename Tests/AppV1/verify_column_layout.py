"""
칼럼 레이아웃 검증 스크립트

InsertFile 결과물의 칼럼 구조와 내용 분포를 확인
"""
import sys
import codecs
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 검증할 파일
result_file = Path("Tests/AppV1/결과_InsertFile_5문항.hwp")

if not result_file.exists():
    print(f'❌ 파일이 없습니다: {result_file}')
    sys.exit(1)

print('=' * 70)
print('InsertFile 결과물 칼럼 레이아웃 검증')
print('=' * 70)
print(f'파일: {result_file}')

# 클라이언트 생성
client = AutomationClient()
hwp = client.hwp
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 파일 열기
result = client.open_document(str(result_file))
if not result.success:
    print(f'❌ 열기 실패: {result.error}')
    sys.exit(1)

print(f'\n파일 열림 성공')
print(f'전체 페이지: {hwp.PageCount}')

# 문서 처음으로 이동
hwp.Run("MoveDocBegin")

# 각 페이지 순회하며 칼럼 확인
print('\n' + '=' * 70)
print('페이지별 칼럼 내용 확인')
print('=' * 70)

for page in range(1, hwp.PageCount + 1):
    print(f'\n[페이지 {page}]')

    # 페이지 이동
    hwp.SetPos(page - 1, 0, 0)

    # 현재 위치 확인
    pos = hwp.GetPos()
    print(f'  위치: List={pos[0]}, Para={pos[1]}, Pos={pos[2]}')

    # 텍스트 읽기 시도
    try:
        # 페이지 전체 선택
        hwp.Run("MovePageBegin")
        hwp.Run("Select")
        hwp.Run("MovePageEnd")

        text = hwp.GetText()
        if text:
            text_preview = str(text).replace('\r', '').replace('\n', ' ')[:100]
            print(f'  텍스트: {text_preview}...')
            print(f'  길이: {len(str(text))} 자')
        else:
            print(f'  텍스트: (비어있음)')

        # 선택 해제
        hwp.Run("Cancel")
    except Exception as e:
        print(f'  ❌ 텍스트 읽기 실패: {e}')

# 칼럼 정보 확인
print('\n' + '=' * 70)
print('칼럼 구조 분석')
print('=' * 70)

# 문서 처음으로
hwp.Run("MoveDocBegin")

# Para 단위로 순회
para_count = 0
empty_paras = 0
column_breaks = 0

try:
    while True:
        # 현재 Para 위치
        pos_before = hwp.GetPos()

        # Para 텍스트
        hwp.Run("Select")
        hwp.Run("MoveParaEnd")
        text = hwp.GetText()
        hwp.Run("Cancel")

        para_count += 1

        if not text or len(str(text).strip()) == 0:
            empty_paras += 1

        # 칼럼 구분 확인 (BreakColumn은 특수 문자로 나타남)
        if text and '\x0d' in str(text):  # 칼럼 구분자
            column_breaks += 1

        # 다음 Para로
        hwp.Run("MoveParaEnd")
        hwp.Run("MoveRight")

        # 위치 변화 확인 (문서 끝 감지)
        pos_after = hwp.GetPos()
        if pos_before == pos_after:
            break

except Exception as e:
    print(f'순회 중 오류: {e}')

print(f'총 Para 수: {para_count}')
print(f'빈 Para 수: {empty_paras}')
print(f'칼럼 구분: {column_breaks}개')

# 정리
client.close_document()
client.cleanup()

print('\n' + '=' * 70)
print('검증 완료')
print('=' * 70)
