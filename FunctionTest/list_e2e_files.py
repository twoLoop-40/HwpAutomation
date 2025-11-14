from pathlib import Path

problem_dir = Path('Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905')
problem_files = sorted(problem_dir.glob('*.hwp'))[:5]

for i, pf in enumerate(problem_files, 1):
    print(f'{i}. {pf.name}')
    print(f'   Full path: {pf}')
    print(f'   Exists: {pf.exists()}')
    print()
