"""
문서 분리 분석 스크립트 V2

CtrlList를 사용한 더 정확한 분석
"""

import sys
import codecs
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.automation_client import AutomationClient


def analyze_via_ctrl_list(file_path: str):
    """CtrlList를 사용한 문서 구조 분석"""
    print(f"\n{'='*60}")
    print(f"문서 분석 V2: {Path(file_path).name}")
    print(f"{'='*60}\n")

    client = AutomationClient()
    hwp = client.hwp

    try:
        # FilePathChecker DLL 등록
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 문서 열기
        print(f"문서 열기: {file_path}")
        hwp.Open(file_path, "HWP", "forceopen:true")
        print("✓ 문서 열기 성공\n")

        # 기본 정보
        print("=== 기본 정보 ===")
        page_count = hwp.PageCount
        print(f"페이지 수: {page_count}")
        print(f"편집 모드: {hwp.EditMode}")

        # Ctrl 정보 분석
        print("\n=== Ctrl 구조 분석 ===")

        hwp.Run("MoveDocBegin")
        ctrl_count = 0
        table_count = 0
        section_count = 0

        # 전체 문서 순회
        pset = hwp.HParameterSet.HFindReplace
        hwp.HAction.GetDefault("RepeatFind", pset.HSet)

        # 모든 컨트롤 찾기
        try:
            ctrl_info = hwp.HeadCtrl
            while ctrl_info:
                ctrl_count += 1
                ctrl_type = ctrl_info.CtrlID
                print(f"Ctrl {ctrl_count}: Type={ctrl_type}")

                if ctrl_type == "tbl":
                    table_count += 1
                elif ctrl_type == "secd":
                    section_count += 1

                ctrl_info = ctrl_info.Next
        except:
            pass

        print(f"\n총 Ctrl 수: {ctrl_count}")
        print(f"표 수: {table_count}")
        print(f"구역 수: {section_count}")

        # 문서 닫기
        hwp.Clear(1)
        print("\n✓ 분석 완료")

    except Exception as e:
        print(f"\n✗ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.quit()


if __name__ == "__main__":
    test_file = r"Tests\seperation\6. 명제_2023.hwp"

    if not Path(test_file).exists():
        print(f"파일이 존재하지 않습니다: {test_file}")
        sys.exit(1)

    analyze_via_ctrl_list(test_file)
