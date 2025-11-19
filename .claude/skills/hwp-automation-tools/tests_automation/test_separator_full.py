"""Separator 전체 테스트"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from automations.separator import SeparatorConfig, separate_problems, OnePerFile, GroupByCount

def test_one_per_file():
    """1문제 = 1파일 테스트"""
    print("\n" + "=" * 60)
    print("테스트 1: 1문제 = 1파일 (처음 10개만)")
    print("=" * 60)
    
    config = SeparatorConfig.for_hwpx(
        "Tests/seperation/6. 명제_2023.hwpx",
        "Tests/seperation/output_one_per_file"
    )
    
    result = separate_problems(config)
    
    print(f"\n결과: {result.success_count}개 성공")
    print(f"파일: {result.output_files[:5]}")

def test_grouped():
    """30개씩 묶기 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: 30개씩 묶기")
    print("=" * 60)
    
    config = SeparatorConfig.grouped(
        "Tests/seperation/6. 명제_2023.hwpx",
        "Tests/seperation/output_grouped_30",
        30
    )
    
    result = separate_problems(config)
    
    print(f"\n결과: {result.success_count}개 그룹 생성")
    print(f"파일: {result.output_files}")

if __name__ == "__main__":
    test_one_per_file()
    test_grouped()
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("=" * 60)
