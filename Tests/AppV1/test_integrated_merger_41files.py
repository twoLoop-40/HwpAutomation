"""
통합 Merger 테스트 (41개 파일)

2단계 워크플로우:
1. 병렬 전처리 (20 workers): 원본 → 전처리 파일
2. 순차 합병: 전처리 파일 → 최종 문서

예상 성능:
- Step 1: ~100초 (병렬)
- Step 2: ~50초 (순차, 전처리된 파일이라 빠름)
- 총: ~150초 (기존 403초 대비 63% 개선)
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
from AppV1.integrated_merger import IntegratedMerger

# 실제 문항 파일 스캔
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files_paths = [f for f in all_files if not f.name.startswith('[문항')]

print('=' * 70)
print('통합 Merger 테스트 (41개 파일)')
print('=' * 70)
print(f'실제 문항 수: {len(problem_files_paths)}개')
print()

# 양식 파일
template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
output_file = Path("Tests/AppV1/결과_IntegratedMerger_41문항.hwp")

# ProblemFile 객체 생성
problem_files = [
    ProblemFile(path=f, name=f.name, index=i)
    for i, f in enumerate(problem_files_paths, 1)
]

# MergeConfig 생성
config = MergeConfig(
    template_path=template_file,
    problem_files=problem_files,
    output_path=output_file,
    use_template=True
)

if __name__ == '__main__':
    # Integrated Merger 실행
    merger = IntegratedMerger()
    success, page_count = merger.merge_with_parallel_preprocessing(
        config,
        max_workers=20
    )

    if success:
        print(f'\n✅ 성공: {len(problem_files)}개 합병, {page_count} 페이지')
        print(f'출력: {output_file}')
    else:
        print(f'\n❌ 실패')
