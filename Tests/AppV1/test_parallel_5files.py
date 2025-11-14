"""
병렬 전처리 테스트 (5개 파일)

HwpIdris/AppV1/ParallelPreprocessor.idr 명세 검증
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

from AppV1.parallel_preprocessor import (
    ParallelPreprocessor,
    PreprocessConfig,
    predict_performance
)

# 테스트 파일 5개
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')][:5]

print('=' * 70)
print('병렬 전처리 테스트 (5개 파일)')
print('=' * 70)
print(f'선택된 파일:')
for i, f in enumerate(test_files, 1):
    print(f'  [{i}] {f.name}')
print()

# 성능 예측 (순차 처리 기준: 9.8s/file)
seq_time, par_time, improvement = predict_performance(5, 9.8, 5)
print(f'성능 예측:')
print(f'  순차 처리: {seq_time:.1f}초 (~{seq_time/60:.1f}분)')
print(f'  병렬 처리: {par_time:.1f}초 (5 workers)')
print(f'  예상 개선: {improvement:.1f}%')
print()

if __name__ == '__main__':
    # 설정
    config = PreprocessConfig(
        max_workers=5,  # 5개 파일이므로 5 workers
        output_dir="Tests/AppV1/Preprocessed_5files",
        keep_original=True,
        timeout=30.0
    )

    # 병렬 전처리 실행
    preprocessor = ParallelPreprocessor(config)

    file_paths = [str(f.absolute()) for f in test_files]
    success_results, failure_results = preprocessor.preprocess_parallel(file_paths)

    # 결과 집계
    summary = preprocessor.summarize(success_results, failure_results)

    print('\n' + '=' * 70)
    print('결과 요약')
    print('=' * 70)
    print(f'전체 파일: {summary["total_files"]}개')
    print(f'성공: {summary["success_count"]}개')
    print(f'실패: {summary["failure_count"]}개')
    print(f'전체 Para: {summary["total_paras"]}개')
    print(f'제거된 Para: {summary["total_removed"]}개')
    print(f'총 처리 시간: {summary["total_time"]:.1f}초')
    print(f'파일당 평균: {summary["avg_time_per_file"]:.2f}초')
    print('=' * 70)

    # 성공률 확인
    if summary['success_count'] == len(test_files):
        print('✅ 모든 파일 전처리 성공!')
    else:
        print(f'⚠️  {summary["failure_count"]}개 파일 실패')
        for result in failure_results:
            print(f'   - {Path(result.original_path).name}: {result.error_message}')

    print('=' * 70)
