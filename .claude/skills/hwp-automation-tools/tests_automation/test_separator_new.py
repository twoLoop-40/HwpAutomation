"""새 Separator 로직 테스트 (iter_note_blocks 패턴)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automations.separator.types import SeparatorConfig
from automations.separator.separator import separate_problems

# 테스트 파일
input_file = "Tests/seperation/6. 명제_2023.hwpx"
output_dir = "Tests/seperation/output_test_new"

# 10개씩 묶어서 테스트 (빠른 확인)
config = SeparatorConfig.grouped(input_file, output_dir, 10)
config.verbose = True

# 실행
result = separate_problems(config)

# 결과
print("\n" + "="*60)
print(f"총 문제 수: {result.total_problems}")
print(f"성공: {result.success_count}")
print(f"실패: {result.failed_count}")
print(f"출력 파일: {len(result.output_files)}개")

# 첫 번째 파일 내용 확인
if result.output_files:
    first_file = Path(result.output_files[0])
    print(f"\n첫 번째 파일: {first_file}")
    if first_file.exists():
        content = first_file.read_text(encoding='utf-8')
        print(f"파일 크기: {len(content)} bytes")
        print(f"내용 미리보기 (처음 500자):")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)
