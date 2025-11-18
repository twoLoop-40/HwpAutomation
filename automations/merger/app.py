"""
AppV1 애플리케이션 엔트리포인트

실행 예제:
    python -m AppV1.app
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from AppV1.types import ProblemFile, MergeConfig
from AppV1.merger import ProblemMerger


def load_problem_files(problem_dir: Path, csv_path: Path = None) -> list[ProblemFile]:
    """
    문제 파일 로드

    CSV 파일이 있으면 origin_num 순서로 로드,
    없으면 [문항원본], [문항합본] 제외한 실제 문항 파일만 스캔
    """
    # CSV 파일이 있으면 CSV 기반 로드
    if csv_path and csv_path.exists():
        import csv
        problem_files = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                file_name = row['file_name']
                file_path = problem_dir / file_name

                if file_path.exists():
                    problem_files.append(ProblemFile(
                        path=file_path,
                        name=file_name,
                        index=idx
                    ))

        return problem_files

    # CSV가 없으면 디렉토리 스캔
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = []

    for idx, file_path in enumerate(all_files, 1):
        # 제외할 파일 패턴
        if file_path.name.startswith('[문항'):
            continue
        if file_path.name.startswith('~'):
            continue

        problem_files.append(ProblemFile(
            path=file_path,
            name=file_path.name,
            index=idx
        ))

    return problem_files


def main():
    """메인 함수"""

    # 파일 경로 설정
    template_file = Path("Tests/E2ETest/[양식]mad모의고사.hwp")
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    csv_path = problem_dir / "problem_files.csv"
    output_path = Path("AppV1/결과_AppV1_문항합병.hwp")

    # 검증
    if not template_file.exists():
        print(f'❌ 양식 파일이 없습니다: {template_file}')
        return False

    if not problem_dir.exists():
        print(f'❌ 문항 디렉토리가 없습니다: {problem_dir}')
        return False

    # 문항 파일 로드 (CSV 우선)
    problem_files = load_problem_files(problem_dir, csv_path)

    if csv_path.exists():
        print(f'✅ CSV 파일 사용: {csv_path.name}')
    else:
        print(f'⚠️  CSV 파일 없음, 디렉토리 전체 스캔')

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다: {problem_dir}')
        return False

    print(f'✅ 로드된 문항: {len(problem_files)}개')

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
        print('\n✅ AppV1 워크플로우 완료!')
        return True
    else:
        print('\n❌ AppV1 워크플로우 실패')
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
