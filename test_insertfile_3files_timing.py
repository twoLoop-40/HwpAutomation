"""
InsertFile 방식 BreakColumn 타이밍 테스트 (3개 파일)

BreakColumn이 완료될 때까지 대기 시간 테스트
"""
import sys
import codecs
from pathlib import Path
import time

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 테스트 파일 3개만
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files = [f for f in all_files if not f.name.startswith('[문항')][:3]

print('=' * 70)
print('InsertFile + BreakColumn 타이밍 테스트 (3개 파일)')
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
        print(f'[{i}/{len(problem_files)}] {problem_file.name[:50]}')

        # InsertFile 액션
        target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
        insert_params = target_hwp.HParameterSet.HInsertFile

        abs_path = str(problem_file.absolute())
        insert_params.HSet.SetItem("FileName", abs_path)
        insert_params.HSet.SetItem("FileFormat", "HWP")
        insert_params.HSet.SetItem("KeepSection", 0)

        insert_start = time.time()
        result = target_hwp.HAction.Execute("InsertFile", insert_params.HSet)
        insert_time = time.time() - insert_start

        if result:
            inserted += 1
            print(f'  ✅ InsertFile 완료 ({insert_time:.3f}초)')
        else:
            print(f'  ❌ InsertFile 실패')

        # BreakColumn (마지막 제외) - 타이밍 증가
        if i < len(problem_files):
            break_start = time.time()
            target_hwp.Run("BreakColumn")
            # 타이밍 테스트: 0.05초 → 0.1초 → 0.15초
            time.sleep(0.15)
            break_time = time.time() - break_start
            print(f'  🔹 BreakColumn 완료 ({break_time:.3f}초)')

        print(f'  현재 페이지: {target_hwp.PageCount}')
        print()

    except Exception as e:
        print(f'  ❌ 오류: {str(e)[:50]}')

total_time = time.time() - start_time

print('-' * 70)
print(f'✅ 삽입 완료 (총 {total_time:.2f}초)')

# 저장
output = Path("AppV1/결과_InsertFile_3문항_타이밍테스트.hwp")
output.parent.mkdir(parents=True, exist_ok=True)
target_hwp.SaveAs(str(output.absolute()))
time.sleep(0.5)

print(f'\n결과:')
print(f'삽입 성공: {inserted}/{len(problem_files)}')
print(f'최종 페이지: {target_hwp.PageCount}')
print(f'소요 시간: {total_time:.2f}초')
print(f'파일당 평균: {total_time/len(problem_files):.2f}초')
print(f'파일 크기: {output.stat().st_size:,} bytes ({output.stat().st_size/1024/1024:.2f} MB)')
print(f'\n출력 파일: {output}')
print('\n⚠️  파일을 열어서 칼럼이 제대로 나뉘어져 있는지 확인하세요!')

# 정리
target_client.close_document()
target_client.cleanup()

print('=' * 70)
