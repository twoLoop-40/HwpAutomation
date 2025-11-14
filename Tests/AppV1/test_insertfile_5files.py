"""
InsertFile 방식 5개 파일 테스트

file_inserter.py 사용: 전처리 + InsertFile 통합
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

from AppV1.types import ProblemFile
from AppV1.file_inserter import merge_with_insertfile

# 테스트 파일 5개
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:5]

problem_files = [
    ProblemFile(path=f, name=f.name, index=i+1)
    for i, f in enumerate(test_files)
]

print('선택된 파일 {}개:'.format(len(problem_files)))
for p in problem_files:
    print(f'  [{p.index}] {p.name}')
print()

# 양식 및 출력 경로
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
output_file = Path("Tests/AppV1/결과_InsertFile_5문항.hwp")

# InsertFile 방식 합병 실행
success, page_count, inserted_count = merge_with_insertfile(
    template_path=template_file,
    problem_files=problem_files,
    output_path=output_file
)

if success:
    print(f'\n✅ 성공: {inserted_count}개 삽입, {page_count} 페이지')
    print(f'출력: {output_file}')
else:
    print(f'\n❌ 실패')
