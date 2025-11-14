"""
InsertFile 디버깅: 커서 위치 및 삽입 위치 확인

InsertFile 후 커서가 어디에 있는지, 내용이 어디에 삽입되는지 확인
"""
import sys
import codecs
from pathlib import Path
import time

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 테스트 파일 2개만
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:2]

print('=' * 70)
print('InsertFile 디버깅: 커서 위치 추적')
print('=' * 70)
print(f'테스트 파일: {len(test_files)}개')
for i, f in enumerate(test_files, 1):
    print(f'  [{i}] {f.name}')

# 클라이언트 생성
client = AutomationClient()
hwp = client.hwp
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 양식 열기
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
result = client.open_document(str(template_file))
print(f'\n양식 열림: {result.success}')
print(f'초기 페이지: {hwp.PageCount}')

# 문서 정보 (생략)

# 본문 시작으로
print(f'\n본문 시작으로 이동...')
hwp.Run("MoveDocBegin")
time.sleep(0.05)
hwp.Run("MoveParaBegin")
time.sleep(0.05)

pos = hwp.GetPos()
print(f'  초기 위치: List={pos[0]}, Para={pos[1]}, Pos={pos[2]}')

# 각 파일 InsertFile
for i, test_file in enumerate(test_files, 1):
    print(f'\n[{i}/{len(test_files)}] {test_file.name[:50]}')

    # InsertFile 전 위치
    pos_before = hwp.GetPos()
    print(f'  InsertFile 전:')
    print(f'    위치: List={pos_before[0]}, Para={pos_before[1]}, Pos={pos_before[2]}')

    # InsertFile
    hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
    insert_params = hwp.HParameterSet.HInsertFile
    insert_params.HSet.SetItem("FileName", str(test_file.absolute()))
    insert_params.HSet.SetItem("FileFormat", "HWP")
    insert_params.HSet.SetItem("KeepSection", 0)

    result = hwp.HAction.Execute("InsertFile", insert_params.HSet)
    time.sleep(0.1)

    # InsertFile 후 위치
    pos_after = hwp.GetPos()
    print(f'  InsertFile 후:')
    print(f'    결과: {result}')
    print(f'    위치: List={pos_after[0]}, Para={pos_after[1]}, Pos={pos_after[2]}')
    print(f'    전체 페이지: {hwp.PageCount}')

    # BreakColumn (마지막 제외)
    if i < len(test_files):
        print(f'  BreakColumn 실행...')
        pos_before_break = hwp.GetPos()

        hwp.Run("BreakColumn")
        time.sleep(0.15)

        pos_after_break = hwp.GetPos()
        print(f'    BreakColumn 전 위치: List={pos_before_break[0]}, Para={pos_before_break[1]}')
        print(f'    BreakColumn 후 위치: List={pos_after_break[0]}, Para={pos_after_break[1]}')

# 최종 상태
print(f'\n최종 상태:')
print(f'  전체 페이지: {hwp.PageCount}')

# 저장
output = Path("Tests/AppV1/결과_InsertFile_디버그.hwp")
output.parent.mkdir(parents=True, exist_ok=True)
hwp.SaveAs(str(output.absolute()))
time.sleep(0.5)

print(f'\n출력 파일: {output}')

# 정리
client.close_document()
client.cleanup()

print('=' * 70)
