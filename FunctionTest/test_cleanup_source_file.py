"""
소스 파일 빈 문단 정리 테스트

목적: 복사-붙여넣기 전에 소스 파일의 빈 Para 삭제
"""

import sys
import time
from pathlib import Path

# UTF-8 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.automation.client import AutomationClient


def remove_empty_paras(hwp) -> int:
    """
    빈 문단 제거

    전략:
    1. 문서를 끝에서 시작으로 역순 순회
    2. 각 Para의 시작 == 끝 → 빈 Para → 삭제
    3. 역순 순회 이유: 앞에서 삭제하면 Para 번호가 밀림

    Returns:
        int: 삭제된 Para 개수
    """
    removed_count = 0

    # 먼저 총 Para 개수 파악
    max_para = 0
    for para_num in range(1000):  # 최대 1000개 검사
        if not hwp.SetPos(0, para_num, 0):
            max_para = para_num
            break

    print(f'  총 Para 수: {max_para}')

    # 역순으로 순회하며 빈 Para 삭제
    for para_num in range(max_para - 1, -1, -1):
        # Para 시작으로 이동
        if not hwp.SetPos(0, para_num, 0):
            continue

        start_pos = hwp.GetPos()

        # Para 끝으로 이동
        hwp.Run("MoveParagraphEnd")
        end_pos = hwp.GetPos()

        # 빈 Para 확인 (시작 == 끝)
        if start_pos == end_pos:
            # 빈 Para 선택
            hwp.SetPos(0, para_num, 0)
            hwp.Run("Select")
            hwp.Run("MoveParagraphEnd")

            # Para 삭제 (Backspace로)
            hwp.Run("Delete")
            removed_count += 1

            print(f'  Para {para_num:2d} 삭제 (빈 문단)')

    return removed_count


def cleanup_and_copy(source_file: Path, hwp_source, hwp_target) -> bool:
    """
    소스 파일 정리 후 복사

    1. 소스 파일 열기
    2. 빈 Para 삭제
    3. 전체 선택 → 복사
    4. 대상에 붙여넣기
    """
    try:
        print(f'\n[소스 파일 정리 + 복사]')
        print(f'  파일: {source_file.name[:50]}...')

        # 1. 소스 파일 열기
        from src.automation.client import AutomationClient
        source_client = AutomationClient()
        source_hwp = source_client.hwp

        source_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        try:
            source_hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        result = source_client.open_document(str(source_file))
        if not result.success:
            print(f'  ❌ 파일 열기 실패: {result.error}')
            return False

        time.sleep(0.2)

        # 2. 빈 Para 삭제
        print(f'\n  빈 문단 삭제 중...')
        removed = remove_empty_paras(source_hwp)
        print(f'  ✅ {removed}개 빈 문단 삭제 완료')

        # 3. 전체 선택 → 복사
        print(f'\n  전체 선택 + 복사...')
        source_hwp.Run("MoveDocBegin")
        source_hwp.Run("SelectAll")
        source_hwp.Run("Copy")
        time.sleep(0.2)

        # 4. 대상에 붙여넣기
        print(f'  대상 문서에 붙여넣기...')
        hwp_target.Run("Paste")
        time.sleep(0.2)

        # 소스 파일 닫기
        source_hwp.Run("Cancel")
        source_client.close_document()
        source_client.cleanup()

        print(f'  ✅ 복사-붙여넣기 완료')
        return True

    except Exception as e:
        print(f'  ❌ 실패: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_cleanup_source_file():
    """빈 문단 정리 후 복사 테스트"""

    print('=' * 70)
    print('소스 파일 빈 문단 정리 테스트')
    print('=' * 70)

    # 테스트할 소스 파일 1개
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    problem_files = sorted(problem_dir.glob("*.hwp"))[:1]  # 첫 번째 파일만

    if not problem_files:
        print(f'❌ 문항 파일이 없습니다')
        return False

    source_file = problem_files[0]
    print(f'\n소스 파일: {source_file.name}')

    # 대상 클라이언트 생성
    target_client = AutomationClient()
    target_hwp = target_client.hwp

    target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    try:
        target_hwp.XHwpWindows.Item(0).Visible = False
    except:
        pass

    try:
        # 새 문서 생성
        print('\n[1/3] 새 문서 생성')
        target_hwp.HAction.Run("FileNew")
        time.sleep(0.5)
        print('✅ 문서 생성 완료')

        # 빈 문단 정리 + 복사
        print('\n[2/3] 빈 문단 정리 + 복사')
        if not cleanup_and_copy(source_file, None, target_hwp):
            return False

        # 결과 확인
        print('\n[3/3] 결과 확인')

        # Para 개수 확인
        para_count = 0
        for para_num in range(100):
            if target_hwp.SetPos(0, para_num, 0):
                para_count += 1
            else:
                break

        print(f'  대상 문서 Para 수: {para_count}')

        # 전체 텍스트 확인
        target_hwp.Run("MoveDocBegin")
        target_hwp.Run("SelectAll")
        target_hwp.Run("Copy")
        time.sleep(0.2)

        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()

            print(f'  텍스트 길이: {len(text)}자')
            print(f'  미리보기: {text[:200]}...')
        except:
            print(f'  ⚠️  클립보드 읽기 실패')

        target_hwp.Run("Cancel")

        # 결과 저장
        output_path = Path("FunctionTest/결과_빈문단정리.hwp")
        print(f'\n결과 저장: {output_path.name}')
        target_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.3)

        if output_path.exists():
            print(f'✅ 저장 완료: {output_path}')
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
        target_client.cleanup()
        print('✅ 정리 완료')


if __name__ == "__main__":
    success = test_cleanup_source_file()
    sys.exit(0 if success else 1)
