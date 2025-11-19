"""Separator XML 파서 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from automations.separator.xml_parser import HwpxParser

def test_parser():
    hwpx_path = "Tests/seperation/6. 명제_2023.hwpx"
    
    print("=" * 60)
    print("Separator XML Parser 테스트")
    print("=" * 60)
    print()
    
    # 파서 생성
    parser = HwpxParser(hwpx_path, verbose=True)
    
    # 파싱 실행
    endnotes = parser.parse()
    
    print()
    print("=" * 60)
    print("파싱 결과")
    print("=" * 60)
    print(f"총 EndNote: {len(endnotes)}개")
    print()
    
    # 처음 10개 EndNote 정보
    print("처음 10개 EndNote:")
    for endnote in endnotes[:10]:
        print(f"  {endnote}")
    
    print()
    
    # 마지막 5개 EndNote 정보
    print("마지막 5개 EndNote:")
    for endnote in endnotes[-5:]:
        print(f"  {endnote}")
    
    print()
    print("=" * 60)
    print("✅ 파서 테스트 성공!")
    print("=" * 60)

if __name__ == "__main__":
    test_parser()
