"""
KeepSection 파라미터 실험

HwpIdris/ParameterSet_extracted.txt:
  KeepSection PIT_UI1 - 끼워 넣을 문서를 구역으로 나누어 쪽 모양을 유지할지 여부

가설: KeepSection=1로 설정하면 2단 구성을 유지하여 BreakColumn이 작동할 것
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
from src.common.sync import wait_for_hwp_ready

# 테스트 파일 2개만
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:2]

print('=' * 70)
print('KeepSection 파라미터 실험')
print('=' * 70)
print(f'테스트 파일: {len(test_files)}개')
for i, f in enumerate(test_files, 1):
    print(f'  [{i}] {f.name}')

# 양식 파일
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")

# 실험 1: KeepSection=0 (기존 방식)
print('\n' + '=' * 70)
print('[실험 1] KeepSection=0 (구역 정보 무시)')
print('=' * 70)

client1 = AutomationClient()
hwp1 = client1.hwp
hwp1.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

result = client1.open_document(str(template_file))
print(f'양식 열림: {result.success}')
print(f'초기 페이지: {hwp1.PageCount}')

hwp1.Run("MoveDocBegin")
wait_for_hwp_ready(hwp1)

for i, test_file in enumerate(test_files, 1):
    print(f'\n[{i}/{len(test_files)}] {test_file.name[:50]}')

    # InsertFile (KeepSection=0)
    hwp1.HAction.GetDefault("InsertFile", hwp1.HParameterSet.HInsertFile.HSet)
    insert_params = hwp1.HParameterSet.HInsertFile
    insert_params.HSet.SetItem("FileName", str(test_file.absolute()))
    insert_params.HSet.SetItem("FileFormat", "HWP")
    insert_params.HSet.SetItem("KeepSection", 0)  # 구역 무시

    result = hwp1.HAction.Execute("InsertFile", insert_params.HSet)
    wait_for_hwp_ready(hwp1, timeout=5.0)

    pos = hwp1.GetPos()
    print(f'  InsertFile 후: List={pos[0]}, Para={pos[1]}, PageCount={hwp1.PageCount}')

    # MoveDocEnd
    hwp1.Run("MoveDocEnd")
    wait_for_hwp_ready(hwp1)

    # BreakColumn (마지막 제외)
    if i < len(test_files):
        hwp1.Run("BreakColumn")
        wait_for_hwp_ready(hwp1, timeout=3.0)
        print(f'  BreakColumn 실행')

output1 = Path("Tests/AppV1/결과_KeepSection_0.hwp")
output1.parent.mkdir(parents=True, exist_ok=True)
hwp1.SaveAs(str(output1.absolute()))
wait_for_hwp_ready(hwp1, timeout=10.0)

print(f'\n최종 상태:')
print(f'  페이지: {hwp1.PageCount}')
print(f'  출력: {output1}')

client1.close_document()
client1.cleanup()

# 실험 2: KeepSection=1 (구역 정보 유지)
print('\n' + '=' * 70)
print('[실험 2] KeepSection=1 (구역 정보 유지)')
print('=' * 70)

client2 = AutomationClient()
hwp2 = client2.hwp
hwp2.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

result = client2.open_document(str(template_file))
print(f'양식 열림: {result.success}')
print(f'초기 페이지: {hwp2.PageCount}')

hwp2.Run("MoveDocBegin")
wait_for_hwp_ready(hwp2)

for i, test_file in enumerate(test_files, 1):
    print(f'\n[{i}/{len(test_files)}] {test_file.name[:50]}')

    # InsertFile (KeepSection=1)
    hwp2.HAction.GetDefault("InsertFile", hwp2.HParameterSet.HInsertFile.HSet)
    insert_params = hwp2.HParameterSet.HInsertFile
    insert_params.HSet.SetItem("FileName", str(test_file.absolute()))
    insert_params.HSet.SetItem("FileFormat", "HWP")
    insert_params.HSet.SetItem("KeepSection", 1)  # 구역 유지 ⭐

    result = hwp2.HAction.Execute("InsertFile", insert_params.HSet)
    wait_for_hwp_ready(hwp2, timeout=5.0)

    pos = hwp2.GetPos()
    print(f'  InsertFile 후: List={pos[0]}, Para={pos[1]}, PageCount={hwp2.PageCount}')

    # MoveDocEnd
    hwp2.Run("MoveDocEnd")
    wait_for_hwp_ready(hwp2)

    # BreakColumn (마지막 제외)
    if i < len(test_files):
        hwp2.Run("BreakColumn")
        wait_for_hwp_ready(hwp2, timeout=3.0)
        print(f'  BreakColumn 실행')

output2 = Path("Tests/AppV1/결과_KeepSection_1.hwp")
output2.parent.mkdir(parents=True, exist_ok=True)
hwp2.SaveAs(str(output2.absolute()))
wait_for_hwp_ready(hwp2, timeout=10.0)

print(f'\n최종 상태:')
print(f'  페이지: {hwp2.PageCount}')
print(f'  출력: {output2}')

client2.close_document()
client2.cleanup()

# 비교
print('\n' + '=' * 70)
print('결과 비교')
print('=' * 70)
print(f'KeepSection=0: {output1.stat().st_size:,} bytes')
print(f'KeepSection=1: {output2.stat().st_size:,} bytes')
print()
print('파일을 직접 열어서 칼럼 구조를 확인하세요!')
print('=' * 70)
