from automations.separator.types import SeparatorConfig, NamingStrategy, GroupInfo, ProblemNumber

# 테스트 config 생성
config = SeparatorConfig.grouped('test.hwp', 'output', 3)

# Custom prefix 설정
config.naming_rule.strategy = NamingStrategy.CUSTOM
config.naming_rule.custom_prefix = 'TEST_PREFIX'

# GroupInfo 생성 및 파일명 테스트
group_info = GroupInfo(
    group_num=1,
    start_problem=ProblemNumber(1),
    end_problem=ProblemNumber(3),
    problem_count=3
)

filename = config.naming_rule.generate_group_filename(group_info)
print(f'Generated filename: {filename}')
print(f'Expected: TEST_PREFIX_1.hwp')
print(f'Match: {filename == "TEST_PREFIX_1.hwp"}')
