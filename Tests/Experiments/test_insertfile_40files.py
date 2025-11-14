"""
InsertFile 방식으로 40문항 테스트

Copy/Paste 없이 InsertFile로 직접 삽입
- 빠름: 파일당 0.2초 × 40 = 8초
- 안정: Clipboard 문제 회피
"""
import sys
import codecs
from pathlib import Path
import time
import csv

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 파일 목록 로드 (디렉토리 스캔)
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files = [f for f in all_files if not f.name.startswith('[문항')]

print('=' * 70)
print(f'InsertFile 방식 40문항 테스트')
print('=' * 70)
print(f'문항 수: {len(problem_files)}개')

# 클라이언트 생성
target_client = AutomationClient()
target_hwp = target_client.hwp
target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 양식 열기
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
result = target_client.open_document(str(template_file))
print(f'양식 열림: {result.success}')
print(f'초기 페이지: {target_hwp.PageCount}')

# 본문 시작으로
target_hwp.Run("MoveDocBegin")
target_hwp.Run("MoveParaBegin")
time.sleep(0.05)

print(f'\n문항 삽입 시작...')
print('-' * 70)

start_time = time.time()
inserted = 0

for i, problem_file in enumerate(problem_files, 1):
    try:
        progress = (i / len(problem_files)) * 100
        print(f'  [{i:2d}/{len(problem_files)}] ({progress:5.1f}%) {problem_file.name[:40]}', end='')

        # InsertFile 액션
        target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
        insert_params = target_hwp.HParameterSet.HInsertFile

        abs_path = str(problem_file.absolute())
        insert_params.HSet.SetItem("FileName", abs_path)
        insert_params.HSet.SetItem("FileFormat", "HWP")
        insert_params.HSet.SetItem("KeepSection", 0)

        result = target_hwp.HAction.Execute("InsertFile", insert_params.HSet)

        if result:
            inserted += 1
            print(f' ✅')
        else:
            print(f' ❌')

        # BreakColumn (마지막 제외)
        if i < len(problem_files):
            target_hwp.Run("BreakColumn")
            time.sleep(0.15)  # 칼럼 구분 완료 대기

        # 진행 표시 (10개마다)
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg = elapsed / i
            remaining = avg * (len(problem_files) - i)
            print(f'  --- 진행: {i}/{len(problem_files)} ({elapsed:.1f}초, 예상 남은 시간: {remaining:.1f}초)')

    except Exception as e:
        print(f' ❌ {str(e)[:30]}')

total_time = time.time() - start_time

print('-' * 70)
print(f'✅ 삽입 완료 (총 {total_time:.1f}초)')

# 저장
output = Path("AppV1/결과_InsertFile_40문항.hwp")
output.parent.mkdir(parents=True, exist_ok=True)
target_hwp.SaveAs(str(output.absolute()))
time.sleep(0.5)

print(f'\n결과:')
print(f'삽입 성공: {inserted}/{len(problem_files)}')
print(f'최종 페이지: {target_hwp.PageCount}')
print(f'소요 시간: {total_time:.1f}초')
print(f'파일당 평균: {total_time/len(problem_files):.2f}초')
print(f'파일 크기: {output.stat().st_size:,} bytes ({output.stat().st_size/1024/1024:.2f} MB)')
print(f'출력 파일: {output}')

# 정리
target_client.close_document()
target_client.cleanup()

print('=' * 70)
