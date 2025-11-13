"""
양식 기반 문제 병합 (Template-based Merging)

기반 명세: Specs/TemplateMerge.idr
템플릿: Tests/E2ETest/[양식]mad모의고사.hwp

핵심 원칙:
1. 첫 번째 단 위치: SetPos(0, 1, 0)
2. 단 생성: BreakColumn (MoveNextColumn 아님!)
3. 페이지 확장: BreakColumn으로 Page 1만 확장
4. 페이지 나누기 금지: Page 2는 미주 전용
"""

import sys
import csv
import time
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

# Windows console UTF-8 setup
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.common.sync import wait_for_hwp_ready
except ImportError:
    print("❌ 필수 모듈을 import할 수 없습니다.")
    sys.exit(1)


# ============================================================================
# Idris2 명세 기반 타입 정의 (Specs/TemplateMerge.idr)
# ============================================================================

class DocPosition:
    """Specs.TemplateMerge.DocPosition"""
    def __init__(self, list_num, para, pos):
        self.list_num = list_num
        self.para = para
        self.pos = pos

    def __str__(self):
        return f"({self.list_num}, {self.para}, {self.pos})"


def first_column_start() -> DocPosition:
    """firstColumnStart from Idris2 spec"""
    return DocPosition(0, 1, 0)


def nth_column_position(n: int) -> DocPosition:
    """nthColumnPosition from Idris2 spec"""
    return DocPosition(0, 1 + 2 * (n - 1), 0)


# ============================================================================
# CSV 파싱 및 파일 찾기
# ============================================================================

def parse_csv(csv_path: Path) -> Dict[int, List[Dict]]:
    """CSV 파일을 파싱하여 origin_num별로 그룹화"""
    problems_by_num = defaultdict(list)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            origin_num = int(row['origin_num'])
            problems_by_num[origin_num].append({
                'id': row['id'],
                'src': row['src'],
                'mongo_id': row['mongo_id']
            })

    return dict(problems_by_num)


def find_hwp_file(base_dir: Path, src_name: str) -> Path:
    """src 이름으로 HWP 파일 찾기"""
    for hwp_file in base_dir.glob("*.hwp"):
        file_stem = hwp_file.stem
        if file_stem.startswith(src_name):
            return hwp_file

    raise FileNotFoundError(f"HWP 파일을 찾을 수 없습니다: {src_name}")


# ============================================================================
# 복사-붙여넣기
# ============================================================================

def copy_paste_content(source_file: Path, target_hwp, source_hwp_pool) -> bool:
    """
    원본 파일의 내용을 복사-붙여넣기로 가져오기
    """
    try:
        # 원본 파일 열기
        source_hwp_pool.Open(str(source_file.absolute()), "HWP", "readonly:true")
        time.sleep(0.3)

        # 원본 전체 선택
        source_hwp_pool.Run("MoveDocBegin")
        source_hwp_pool.Run("Select")
        source_hwp_pool.Run("MoveDocEnd")

        # 복사
        source_hwp_pool.Run("Copy")
        time.sleep(0.2)

        # 원본 파일 닫기
        source_hwp_pool.Run("Cancel")
        source_hwp_pool.HAction.Run("FileClose")
        time.sleep(0.2)

        # 대상 문서에 붙여넣기
        target_hwp.Run("Paste")
        time.sleep(0.3)
        wait_for_hwp_ready(target_hwp, timeout=3.0)

        return True

    except Exception as e:
        print(f"    ❌ 복사-붙여넣기 실패: {e}")
        return False


# ============================================================================
# 템플릿 기반 병합 (Idris2 명세 준수)
# ============================================================================

def merge_with_template(
    template_path: Path,
    problems_by_num: Dict[int, List[Dict]],
    hwp_dir: Path,
    output_path: Path
):
    """
    템플릿 기반 문제 병합

    Idris2 명세 (Specs/TemplateMerge.idr) 준수:
    1. Template opened
    2. For each problem:
       - Position at Nth column using SetPos
       - Insert content via copy-paste
       - Create next column using BreakColumn
    3. Save (Page 1 expanded, Page 2 endnotes preserved)
    """

    import pythoncom
    import win32com.client as win32

    pythoncom.CoInitialize()

    try:
        print("=" * 70)
        print("템플릿 기반 문제 병합 (Template-based Merging)")
        print(f"기반 명세: Specs/TemplateMerge.idr")
        print("=" * 70)

        # HWP 인스턴스 생성
        print("\n[0/6] HWP 초기화...")
        target_hwp = win32.DispatchEx("HwpFrame.HwpObject")
        target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        target_hwp.XHwpWindows.Item(0).Visible = False

        source_hwp = win32.DispatchEx("HwpFrame.HwpObject")
        source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        source_hwp.XHwpWindows.Item(0).Visible = False

        print("✅ HWP 초기화 완료")

        # 템플릿 열기
        print(f"\n[1/6] 템플릿 열기: {template_path.name}")
        if not template_path.exists():
            print(f"❌ 템플릿 파일이 없습니다: {template_path}")
            return

        target_hwp.Open(str(template_path.absolute()), "HWP", "")
        time.sleep(0.5)
        print("✅ 템플릿 로드 완료")
        print("   페이지 1: B4 2단 (확장 가능)")
        print("   페이지 2: 미주 전용 (자동 관리)")

        # 문제 삽입
        print("\n[2/6] 문제 삽입 (단별)")
        total_problems = sum(len(probs) for probs in problems_by_num.values())
        inserted = 0
        column_index = 1

        # origin_num 순서대로 처리
        for origin_num in sorted(problems_by_num.keys()):
            problems = problems_by_num[origin_num]
            print(f"\n[문제 {origin_num}] {len(problems)}개 파일")

            for i, problem in enumerate(problems):
                src = problem['src']

                try:
                    hwp_file = find_hwp_file(hwp_dir, src)
                    print(f"  [{inserted+1}/{total_problems}] {hwp_file.name}")

                    # N번째 단 위치로 이동 (Idris2 명세 준수)
                    col_pos = nth_column_position(column_index)
                    print(f"    → 단 {column_index}: SetPos{col_pos}")

                    target_hwp.SetPos(col_pos.list_num, col_pos.para, col_pos.pos)
                    time.sleep(0.1)

                    # 복사-붙여넣기
                    if copy_paste_content(hwp_file, target_hwp, source_hwp):
                        inserted += 1
                        print(f"    ✅ 삽입 완료 ({inserted}/{total_problems})")
                    else:
                        print(f"    ⚠️  삽입 실패")

                    # 다음 단 생성 (BreakColumn)
                    # 마지막 파일이 아니면 단 나누기
                    if inserted < total_problems:
                        target_hwp.Run("MoveDocEnd")
                        target_hwp.Run("BreakColumn")
                        time.sleep(0.1)
                        column_index += 1
                        print(f"    → BreakColumn (다음 단: {column_index})")

                except FileNotFoundError as e:
                    print(f"    ❌ {e}")
                except Exception as e:
                    print(f"    ❌ 오류: {e}")

        # 최종 상태 확인
        print("\n[3/6] 최종 문서 상태")
        final_page_count = target_hwp.PageCount
        print(f"  페이지 수: {final_page_count}")
        print(f"  삽입된 단: {column_index}개")
        print(f"  예상: 페이지 1 확장됨, 페이지 2는 미주")

        # 문서 저장
        print(f"\n[4/6] 문서 저장: {output_path}")
        target_hwp.HAction.GetDefault("FileSaveAs_S", target_hwp.HParameterSet.HFileOpenSave.HSet)
        target_hwp.HParameterSet.HFileOpenSave.filename = str(output_path.absolute())
        target_hwp.HParameterSet.HFileOpenSave.Format = "HWP"
        target_hwp.HParameterSet.HFileOpenSave.Attributes = 1
        result = target_hwp.HAction.Execute("FileSaveAs_S", target_hwp.HParameterSet.HFileOpenSave.HSet)

        time.sleep(1.0)
        wait_for_hwp_ready(target_hwp, timeout=5.0)

        if result and output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ 문서 저장 완료 (크기: {file_size:,} bytes)")
        else:
            print("⚠️  문서 저장 실패")

        # 문서 닫기
        print("\n[5/6] 문서 닫기...")
        time.sleep(1.0)
        target_hwp.HAction.Run("FileClose")
        source_hwp.Quit()
        target_hwp.Quit()
        time.sleep(0.5)
        print("✅ 작업 완료!")

        print(f"\n📊 통계:")
        print(f"  - 총 문제 수: {len(problems_by_num)}개")
        print(f"  - 삽입된 파일: {inserted}/{total_problems}개")
        print(f"  - 생성된 단: {column_index}개")
        print(f"  - 출력 파일: {output_path}")

    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pythoncom.CoUninitialize()


def main():
    """메인 실행"""

    # 경로 설정
    template_path = project_root / "Tests/E2ETest/[양식]mad모의고사.hwp"
    test_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    csv_path = test_dir / "[내신대비]휘문고_2_기말_1회_20251112_0905.csv"
    output_path = test_dir / "[문항합본]휘문고_2_기말_1회_Template.hwp"

    # 템플릿 확인
    if not template_path.exists():
        print(f"❌ 템플릿 파일이 없습니다: {template_path}")
        return

    if not csv_path.exists():
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return

    print("=" * 70)
    print("템플릿 기반 문제 병합")
    print("=" * 70)
    print(f"템플릿: {template_path.name}")
    print(f"CSV: {csv_path.name}")
    print(f"출력: {output_path.name}")
    print("=" * 70)

    # CSV 파싱
    print("\n[파싱] CSV 파일 읽기...")
    problems_by_num = parse_csv(csv_path)
    print(f"✅ {len(problems_by_num)}개 문제 그룹 발견")

    # 문제 병합
    print("\n[실행] 템플릿 기반 병합 시작...\n")
    merge_with_template(template_path, problems_by_num, test_dir, output_path)


if __name__ == "__main__":
    main()
