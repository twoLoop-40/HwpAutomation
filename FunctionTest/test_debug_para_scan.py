"""
Para 스캔 디버깅

목적: 왜 Para가 1개만 스캔되는지 확인
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


def debug_para_scan(file_path: Path):
    """Para 스캔 디버깅"""

    print('=' * 70)
    print('Para 스캔 디버깅')
    print('=' * 70)
    print(f'파일: {file_path.name}')

    client = AutomationClient()
    hwp = client.hwp

    try:
        # 보안 모듈
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')

        # 창 숨기기
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # 파일 열기
        result = client.open_document(str(file_path.absolute()))
        if not result.success:
            print(f'❌ 파일 열기 실패: {result.error}')
            return

        time.sleep(0.3)

        print(f'\n[1/2] 기본 정보')
        print(f'  페이지 수: {hwp.PageCount}')

        # Para 스캔 시도 1: MoveNextPara
        print(f'\n[2/2] Para 스캔 (MoveNextPara)')
        hwp.Run('MoveDocBegin')
        time.sleep(0.05)

        para_idx = 0
        for i in range(20):  # 최대 20개
            pos_before = hwp.GetPos()
            print(f'  Para {i}: pos_before={pos_before}')

            # Para 끝으로
            hwp.Run('MoveParaEnd')
            pos_end = hwp.GetPos()
            print(f'         pos_end={pos_end}')

            # 다음 Para로
            hwp.Run('MoveNextPara')
            pos_after = hwp.GetPos()
            print(f'         pos_after={pos_after}')

            if pos_end == pos_after:
                print(f'         → 마지막 Para (위치 변화 없음)')
                break

            para_idx += 1

        print(f'\n  총 Para: {para_idx + 1}개')

    finally:
        client.close_document()
        client.cleanup()


if __name__ == "__main__":
    # 테스트 파일
    problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
    all_files = sorted(problem_dir.glob("*.hwp"))
    problem_files = [
        f for f in all_files
        if '문항원본' not in f.name and '문항합본' not in f.name and not f.name.startswith('~')
    ]

    if len(problem_files) > 0:
        test_file = problem_files[0]
        debug_para_scan(test_file)
    else:
        print('❌ 테스트 파일이 없습니다')
