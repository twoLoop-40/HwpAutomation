"""
LangGraph Send 병렬 처리 테스트 (3개 파일)

Idris2 명세: HwpIdris/AppV1/ParallelMerge.idr
"""
import sys
import codecs
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from AppV1.types import ProblemFile
from AppV1.parallel_workflow import run_parallel_merge

# 테스트 파일 3개
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:3]

problem_files = [
    ProblemFile(path=f, name=f.name, index=i+1)
    for i, f in enumerate(test_files)
]

# 양식 및 출력 경로
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
output_file = Path("AppV1/결과_LangGraph_3문항.hwp")

# LangGraph 워크플로우 실행
success, page_count, inserted_count = run_parallel_merge(
    template_path=template_file,
    problem_files=problem_files,
    output_path=output_file
)

if success:
    print(f'\n✅ 성공: {inserted_count}개 삽입, {page_count} 페이지')
else:
    print(f'\n❌ 실패')
