"""
병렬 전처리 + InsertFile 통합 테스트 (2파일만)
"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from AppV1.types import ProblemFile
from AppV1.preprocessor import preprocess_files_parallel
from src.automation.client import AutomationClient
import time

# 테스트 파일 2개만
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:2]

problem_files = [
    ProblemFile(path=f, name=f.name, index=i+1)
    for i, f in enumerate(test_files)
]

print('=' * 70)
print('병렬 전처리 + InsertFile 테스트')
print('=' * 70)

# 1. 병렬 전처리
print('\n[1단계] 병렬 전처리 시작...')
processed_files, temp_dir, failed = preprocess_files_parallel(problem_files, num_workers=2)

if failed:
    print(f'⚠️  {len(failed)}개 파일 전처리 실패')
    for problem, error in failed:
        print(f'  - {problem.name}: {error}')

# 2. InsertFile로 합병
print(f'\n[2단계] InsertFile로 합병...')
target_client = AutomationClient()
target_hwp = target_client.hwp
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 양식 열기
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
result = target_client.open_document(str(template_file))
print(f'양식 열림: {result.success}')

# 본문 시작으로
target_hwp.Run("MoveDocBegin")
target_hwp.Run("MoveParaBegin")
time.sleep(0.05)

start_time = time.time()

# 전처리된 파일들 삽입
for i, (problem, processed_path) in enumerate(processed_files, 1):
    print(f'  [{i}/{len(processed_files)}] {problem.name[:40]}')

    # InsertFile
    target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
    insert_params = target_hwp.HParameterSet.HInsertFile
    insert_params.HSet.SetItem("FileName", str(processed_path.absolute()))
    insert_params.HSet.SetItem("FileFormat", "HWP")
    insert_params.HSet.SetItem("KeepSection", 0)
    target_hwp.HAction.Execute("InsertFile", insert_params.HSet)

    # BreakColumn (마지막 제외)
    if i < len(processed_files):
        target_hwp.Run("BreakColumn")
        time.sleep(0.02)

    print(f'     페이지: {target_hwp.PageCount}')

merge_time = time.time() - start_time

# 저장
output = Path("test_parallel_insertfile_result.hwp")
target_hwp.SaveAs(str(output.absolute()))
time.sleep(0.5)

print(f'\n결과:')
print(f'최종 페이지: {target_hwp.PageCount}')
print(f'파일 크기: {output.stat().st_size:,} bytes')
print(f'합병 소요 시간: {merge_time:.2f}초')

# 정리
target_client.close_document()
target_client.cleanup()

# 임시 파일 정리
import shutil
shutil.rmtree(temp_dir)
print(f'임시 디렉토리 삭제: {temp_dir}')

print('=' * 70)
