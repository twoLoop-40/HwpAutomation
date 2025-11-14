"""
칼럼 추적기를 사용한 E2E 테스트

목적: BreakColumn 카운팅으로 page, col, line 정보 추적
해결: 일부 칼럼이 빈 상태가 되는 문제 해결
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


def mili_to_hwp_unit(mili: float) -> int:
    """밀리미터를 HWP 단위로 변환"""
    return int(mili * 283.465)


def setup_b4_page(hwp) -> bool:
    """B4 페이지 설정"""
    try:
        hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)

        sec_def = hwp.HParameterSet.HSecDef
        sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)
        sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)
        sec_def.PageDef.LeftMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.RightMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.TopMargin = mili_to_hwp_unit(20.0)
        sec_def.PageDef.BottomMargin = mili_to_hwp_unit(15.0)
        sec_def.PageDef.HeaderLen = mili_to_hwp_unit(15.0)
        sec_def.PageDef.FooterLen = mili_to_hwp_unit(15.0)
        sec_def.HSet.SetItem("ApplyClass", 24)
        sec_def.HSet.SetItem("ApplyTo", 3)

        result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f'  ❌ B4 페이지 설정 실패: {e}')
        return False


def create_two_column_layout(hwp) -> bool:
    """2단 레이아웃 설정"""
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 2
        col_def.SameGap = mili_to_hwp_unit(8.0)
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception as e:
        print(f'  ❌ 2단 레이아웃 설정 실패: {e}')
        return False


class ColumnTracker:
    """
    페이지/칼럼 추적기

    HWP API는 직접적인 page/column 정보를 제공하지 않으므로,
    BreakColumn 호출을 카운팅하여 수동으로 추적합니다.
    """

    def __init__(self, columns_per_page: int = 2):
        self.columns_per_page = columns_per_page
        self.current_page = 1
        self.current_column = 1
        self.insertions: List[Dict] = []

    def insert_and_track(
        self,
        hwp,
        problem_file: Path,
        source_client: AutomationClient,
        problem_num: int,
    ) -> bool:
        """
        문항 삽입 + 위치 추적

        Args:
            hwp: 대상 HWP 객체
            problem_file: 문항 파일 경로
            source_client: 원본 파일용 클라이언트
            problem_num: 문항 번호

        Returns:
            bool: 성공 여부
        """
        try:
            # 삽입 전 위치
            start_pos = hwp.GetPos()

            print(f'   삽입 전 위치: {start_pos}')
            print(f'   → Page {self.current_page}, Column {self.current_column}')

            # 복사-붙여넣기
            if not self._copy_paste_problem(problem_file, hwp, source_client):
                return False

            # 삽입 후 위치
            end_pos = hwp.GetPos()
            print(f'   삽입 후 위치: {end_pos}')

            # 추적 정보 저장
            self.insertions.append({
                'problem_num': problem_num,
                'problem_file': problem_file.name,
                'page': self.current_page,
                'column': self.current_column,
                'start_pos': start_pos,
                'end_pos': end_pos,
            })

            # BreakColumn (마지막 문항이 아닌 경우)
            hwp.Run("BreakColumn")
            time.sleep(0.1)

            break_pos = hwp.GetPos()
            print(f'   BreakColumn 후: {break_pos}')

            # 칼럼/페이지 증가
            self.current_column += 1
            if self.current_column > self.columns_per_page:
                self.current_column = 1
                self.current_page += 1

            print(f'   ✅ 다음: Page {self.current_page}, Column {self.current_column}')

            return True

        except Exception as e:
            print(f'   ❌ 삽입 실패: {e}')
            return False

    def _copy_paste_problem(
        self,
        source_file: Path,
        target_hwp,
        source_client: AutomationClient,
    ) -> bool:
        """문항 파일 복사-붙여넣기"""
        try:
            source_hwp = source_client.hwp

            # 원본 파일 열기
            result = source_client.open_document(str(source_file), options="readonly:true")
            if not result.success:
                print(f'      ❌ 파일 열기 실패: {result.error}')
                return False

            time.sleep(0.2)

            # 원본 전체 선택
            source_hwp.Run("MoveDocBegin")
            source_hwp.Run("Select")
            source_hwp.Run("MoveDocEnd")

            # 복사
            source_hwp.Run("Copy")
            time.sleep(0.2)

            # 원본 파일 닫기
            source_hwp.Run("Cancel")
            source_client.close_document()
            time.sleep(0.1)

            # 대상 문서에 붙여넣기
            target_hwp.Run("Paste")
            time.sleep(0.2)

            return True

        except Exception as e:
            print(f'      ❌ 복사-붙여넣기 실패: {e}')
            return False

    def print_summary(self):
        """추적 결과 요약 출력"""
        print('\n' + '=' * 70)
        print('칼럼 추적 결과')
        print('=' * 70)

        for insertion in self.insertions:
            print(f'문항 {insertion["problem_num"]:2d}: '
                  f'Page {insertion["page"]}, Column {insertion["column"]} | '
                  f'Para {insertion["start_pos"][1]} → {insertion["end_pos"][1]} | '
                  f'{insertion["problem_file"][:40]}...')

        print('=' * 70)


def test_column_tracker():
    """칼럼 추적기를 사용한 E2E 테스트"""

    print('=' * 70)
    print('칼럼 추적기 E2E 테스트')
    print('=' * 70)

    # 파일 경로
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    output_path = Path("FunctionTest/결과_칼럼추적기.hwp")

    if not problem_dir.exists():
        print(f'❌ 문항 디렉토리가 없습니다: {problem_dir}')
        return False

    # 문항 파일 목록 (처음 10개 테스트)
    problem_files = sorted(problem_dir.glob("*.hwp"))[:10]

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다: {problem_dir}')
        return False

    print(f'\n테스트할 문항 수: {len(problem_files)}개')
    for i, pf in enumerate(problem_files, 1):
        print(f'  {i}. {pf.name[:50]}...')

    # MCP 클라이언트 2개 생성
    print('\n[1/6] MCP 클라이언트 초기화...')
    target_client = AutomationClient()
    source_client = AutomationClient()

    target_hwp = target_client.hwp
    source_hwp = source_client.hwp

    # 보안 모듈 등록
    target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

    # 창 숨기기
    try:
        target_hwp.XHwpWindows.Item(0).Visible = False
        source_hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    print('✅ 클라이언트 초기화 완료')

    try:
        # 새 문서 생성
        print('\n[2/6] 새 문서 생성')
        target_hwp.HAction.Run("FileNew")
        time.sleep(0.5)
        print('✅ 문서 생성 완료')

        # B4 페이지 설정
        print('\n[3/6] B4 페이지 설정')
        if not setup_b4_page(target_hwp):
            return False
        print('✅ B4 페이지 설정 완료')

        # 2단 레이아웃 설정
        print('\n[4/6] 2단 레이아웃 설정')
        if not create_two_column_layout(target_hwp):
            return False
        print('✅ 2단 레이아웃 설정 완료')

        # 첫 번째 칼럼 시작 위치로 이동
        print('\n[5/6] 문항 삽입 (칼럼 추적)')
        print('첫 번째 칼럼 시작 위치로 이동...')
        target_hwp.SetPos(0, 0, 0)
        time.sleep(0.1)

        initial_pos = target_hwp.GetPos()
        print(f'  실제 위치: {initial_pos}')

        # 칼럼 추적기 생성
        tracker = ColumnTracker(columns_per_page=2)

        # 각 문항 삽입
        for i, problem_file in enumerate(problem_files, 1):
            print(f'\n--- 문항 {i}/{len(problem_files)} ---')
            print(f'   파일: {problem_file.name[:40]}...')

            if not tracker.insert_and_track(
                target_hwp,
                problem_file,
                source_client,
                i,
            ):
                print(f'   ⚠️  문항 {i} 삽입 실패')

        # 추적 결과 출력
        tracker.print_summary()

        # 최종 상태
        print('\n[6/6] 최종 문서 상태')
        page_count = target_hwp.PageCount
        final_pos = target_hwp.GetPos()
        print(f'PageCount: {page_count}')
        print(f'최종 커서 위치: {final_pos}')
        print(f'삽입된 문항: {len(tracker.insertions)}개')

        # 결과 저장
        print(f'\n결과 저장: {output_path.name}')
        target_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f'✅ 저장 완료')
            print(f'   파일: {output_path}')
            print(f'   크기: {file_size:,} bytes')
        else:
            print(f'⚠️  저장 실패')

        return True

    except Exception as e:
        print(f'\n💥 오류 발생: {e}')
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 정리
        print('\n[정리] 문서 닫기...')
        target_client.close_document()
        source_client.cleanup()
        target_client.cleanup()
        time.sleep(0.5)
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_column_tracker()
    sys.exit(0 if success else 1)
