"""
AppV1 Merger 테스트 (5개 파일)

40문항 성공 로직 + 뒤에서부터 빈 Para 제거 방식
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

from AppV1.types import ProblemFile, MergeConfig
from AppV1.merger import ProblemMerger

# 테스트 파일 5개
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:5]

print('선택된 파일 5개:')
for i, f in enumerate(test_files, 1):
    print(f'  [{i}] {f.name}')

# 양식 파일
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
output_file = Path("Tests/AppV1/결과_Merger_5문항.hwp")

# ProblemFile 객체 생성
problem_files = [
    ProblemFile(path=f, name=f.name, index=i)
    for i, f in enumerate(test_files, 1)
]

# MergeConfig 생성
config = MergeConfig(
    template_path=template_file,
    problem_files=problem_files,
    output_path=output_file,
    use_template=True
)

# Merger 실행
merger = ProblemMerger()
success, page_count = merger.merge_files(config)

if success:
    print(f'\n✅ 성공: {len(problem_files)}개 합병, {page_count} 페이지')
    print(f'출력: {output_file}')
else:
    print(f'\n❌ 실패')
