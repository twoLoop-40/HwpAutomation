"""
병렬 전처리 테스트 (41개 파일)

HwpIdris/AppV1/ParallelPreprocessor.idr 명세 검증

목표:
- 순차 처리: 403초 (41 files × 9.8s/file)
- 병렬 처리: 40-50초 (20 workers)
- 개선율: 87-90%
"""
import sys
import codecs
import time
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

# 모든 문항 파일 (41개)
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
test_files = [f for f in all_files if not f.name.startswith('[문항')]

print('=' * 70)
print('병렬 전처리 테스트 (41개 파일)')
print('=' * 70)
print(f'전체 파일 수: {len(test_files)}개')
print()

# 성능 예측 (순차 처리 기준: 9.8s/file)
seq_time, par_time, improvement = predict_performance(len(test_files), 9.8, 20)
print(f'성능 예측:')
print(f'  순차 처리: {seq_time:.1f}초 (~{seq_time/60:.1f}분)')
print(f'  병렬 처리: {par_time:.1f}초 (20 workers)')
print(f'  예상 개선: {improvement:.1f}%')
print(f'  실제 예상 (오버헤드 포함): 40-50초')
print()

if __name__ == '__main__':
    # 설정
    config = PreprocessConfig(
        max_workers=20,  # HwpIdris 명세 권장값
        output_dir="Tests/AppV1/Preprocessed_41files",
        keep_original=True,
        timeout=60.0  # 타임아웃 증가
    )

    # 병렬 전처리 실행
    preprocessor = ParallelPreprocessor(config)

    file_paths = [str(f.absolute()) for f in test_files]

    start_time = time.time()
    success_results, failure_results = preprocessor.preprocess_parallel(file_paths)
    elapsed_total = time.time() - start_time

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
    print(f'총 처리 시간 (실제 경과): {elapsed_total:.1f}초 (~{elapsed_total/60:.1f}분)')
    print(f'파일당 평균: {elapsed_total / len(test_files):.2f}초')
    print('=' * 70)

    # 성능 분석
    print('\n[성능 분석]')
    print(f'순차 처리 예상: {seq_time:.1f}초')
    print(f'병렬 처리 실제: {elapsed_total:.1f}초')
    actual_improvement = ((seq_time - elapsed_total) / seq_time * 100) if seq_time > 0 else 0.0
    print(f'실제 개선율: {actual_improvement:.1f}%')
    print(f'속도 향상: {seq_time / elapsed_total:.1f}배')

    # 성공률 확인
    print('\n[성공률]')
    if summary['success_count'] == len(test_files):
        print('✅ 모든 파일 전처리 성공!')
    else:
        print(f'⚠️  {summary["failure_count"]}개 파일 실패')
        for result in failure_results[:10]:  # 처음 10개만
            print(f'   - {Path(result.original_path).name}: {result.error_message}')
        if len(failure_results) > 10:
            print(f'   ... 외 {len(failure_results) - 10}개')

    print('=' * 70)
