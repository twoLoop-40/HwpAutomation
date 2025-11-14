"""
AppV1 간단 테스트: 2개 파일만 양식에 붙이기
"""
from pathlib import Path
from AppV1.types import ProblemFile, MergeConfig
from AppV1.merger import ProblemMerger

# 파일 경로 설정
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
output_path = Path("AppV1/테스트_2개문항.hwp")

# 문항 파일 2개만 선택
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files_list = [f for f in all_files if not f.name.startswith('[문항')][:2]  # 처음 2개만

problem_files = [
    ProblemFile(path=f, name=f.name, index=i+1)
    for i, f in enumerate(problem_files_list)
]

print(f'선택된 파일:')
for pf in problem_files:
    print(f'  {pf.index}. {pf.name}')

# 설정 생성
config = MergeConfig(
    template_path=template_file,
    problem_files=problem_files,
    output_path=output_path,
    use_template=True
)

# 합병 실행
merger = ProblemMerger()
success, page_count = merger.merge_files(config)

if success:
    print(f'\n✅ 테스트 완료!')
    print(f'출력 파일: {output_path}')
    print(f'파일 크기: {output_path.stat().st_size:,} bytes')
    print(f'페이지 수: {page_count}')
else:
    print(f'\n❌ 테스트 실패')
