"""
InsertFile 방식 테스트: Copy/Paste 대신 InsertFile 액션 사용

장점:
1. 파일을 열 필요 없음 - InsertFile이 직접 삽입
2. Clipboard 사용 안함 - COM clipboard 문제 회피
3. 훨씬 빠른 속도 예상
"""
import sys
import codecs
from pathlib import Path
import time

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 클라이언트 생성
target_client = AutomationClient()
target_hwp = target_client.hwp

# 보안 모듈
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 양식 열기
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
print(f'양식 열기: {template_file}')
result = target_client.open_document(str(template_file))
print(f'양식 열림: {result.success}')
print(f'초기 페이지: {target_hwp.PageCount}')

# 본문 시작으로 이동
target_hwp.Run("MoveDocBegin")
target_hwp.Run("MoveParaBegin")
time.sleep(0.05)

# 테스트: 첫 2개 파일만 InsertFile
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:2]

print(f'\n테스트 파일 {len(test_files)}개:')
for f in test_files:
    print(f'  - {f.name}')

start_time = time.time()

for i, problem_file in enumerate(test_files, 1):
    print(f'\n[{i}/{len(test_files)}] {problem_file.name[:40]}')

    # InsertFile 액션 사용
    # 파라미터: FileName, FileFormat, FileArg, KeepSection
    target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
    insert_params = target_hwp.HParameterSet.HInsertFile

    # 절대 경로 사용
    abs_path = str(problem_file.absolute())
    print(f'  파일 경로: {abs_path}')

    insert_params.HSet.SetItem("FileName", abs_path)
    insert_params.HSet.SetItem("FileFormat", "HWP")
    insert_params.HSet.SetItem("KeepSection", 0)  # 구역 유지 안함

    # 실행
    result = target_hwp.HAction.Execute("InsertFile", insert_params.HSet)
    print(f'  InsertFile 결과: {result}')
    print(f'  현재 페이지: {target_hwp.PageCount}')

    # 마지막 파일이 아니면 BreakColumn
    if i < len(test_files):
        target_hwp.Run("BreakColumn")
        time.sleep(0.02)

elapsed = time.time() - start_time

print(f'\n결과:')
print(f'최종 페이지: {target_hwp.PageCount}')
print(f'소요 시간: {elapsed:.2f}초')
print(f'파일당 평균: {elapsed/len(test_files):.2f}초')

# 저장
output = Path("test_insertfile_result.hwp")
target_hwp.SaveAs(str(output.absolute()))
print(f'저장: {output} ({output.stat().st_size:,} bytes)')

# 정리
target_client.close_document()
target_client.cleanup()
