import sys
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

problem_dir = Path('Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905')

print(f'Directory exists: {problem_dir.exists()}')
print(f'Directory path: {problem_dir.absolute()}')

if problem_dir.exists():
    all_files = sorted(problem_dir.glob('*.hwp'))
    print(f'\nAll HWP files: {len(all_files)}')

    # List first 10
    print('\nFirst 10 files:')
    for f in all_files[:10]:
        print(f'  {f.name}')

    # Find files with "4회차"
    target_files = [f for f in all_files if '4회차' in f.name]
    print(f'\nFiles with "4회차": {len(target_files)}')

    for f in target_files:
        print(f'  Full name: {f.name}')
        print(f'  Full path: {f.absolute()}')
else:
    print('Directory does not exist!')
