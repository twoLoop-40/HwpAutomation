"""파일 인덱스 #4 찾기"""
import sys
import codecs
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files_paths = [f for f in all_files if not f.name.startswith('[문항')]

for i, f in enumerate(problem_files_paths, 1):
    marker = " << FILE #4" if i == 4 else ""
    print(f'[{i:2d}] {f.name}{marker}')
