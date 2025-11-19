"""텍스트 추출 테스트"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automations.separator import SeparatorConfig, separate_problems

# 10개씩 묶어서 테스트
config = SeparatorConfig.grouped(
    'Tests/seperation/6. 명제_2023.hwpx',
    'Tests/seperation/output_test_text',
    10
)

result = separate_problems(config)
print(f'\n테스트 완료: {result.success_count}개 파일 생성')

# 첫 번째 파일 내용 확인
if result.output_files:
    first_file = Path(result.output_files[0])
    content = first_file.read_text(encoding='utf-8')
    print(f'\n첫 번째 파일 ({first_file.name}) 내용 미리보기:')
    print(content[:800])
    print(f'...\n전체 {len(content)}자')
