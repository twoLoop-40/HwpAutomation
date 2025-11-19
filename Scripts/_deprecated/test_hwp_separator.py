"""HWP 파일로 Separator 테스트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from automations.separator.types import SeparatorConfig
from automations.separator.separator import separate_problems

# 테스트 HWP 파일
input_file = r"Tests\E2ETest\[내신대비]휘문고_2_기말_1회_20251112_0905\[문항원본]휘문고_기말_1회.hwp"
output_dir = "Tests/seperation/output_hwp_test"

# 10개씩 묶어서 테스트
config = SeparatorConfig.grouped(input_file, output_dir, 10)
config.verbose = True

# 실행
print("="*60)
print("HWP 파일 테스트 시작")
print(f"입력: {input_file}")
print("="*60)

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
        print(f"내용 미리보기 (처음 1000자):")
        print("-" * 60)
        print(content[:1000])
        print("-" * 60)
