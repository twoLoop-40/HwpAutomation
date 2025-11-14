"""
생성된 결과 파일 분석

목적: OneColOneProblem 워크플로우의 결과가 제대로 생성되었는지 확인
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


def analyze_result_file(file_path: Path):
    """결과 파일 분석"""

    print('=' * 70)
    print('결과 파일 분석')
    print('=' * 70)
    print(f'파일: {file_path.name}')
    print(f'크기: {file_path.stat().st_size:,} bytes')

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

        # 기본 정보
        print(f'\n[1/3] 기본 정보')
        print(f'  페이지 수: {hwp.PageCount}')

        # 칼럼 정보
        try:
            hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)
            col_def = hwp.HParameterSet.HColDef
            col_count = col_def.Count
            print(f'  칼럼 수: {col_count}')
        except:
            print(f'  칼럼 수: (확인 실패)')

        # Para 정보
        print(f'\n[2/3] Para 정보')
        hwp.Run('MoveDocBegin')
        time.sleep(0.05)

        para_count = 0
        while True:
            para_count += 1
            result = hwp.Run('MoveNextPara')
            if not result:
                break
            if para_count > 100:
                break

        print(f'  총 Para: {para_count}개')

        # 내용 미리보기
        print(f'\n[3/3] 내용 미리보기')
        hwp.Run('MoveDocBegin')
        time.sleep(0.05)

        # 첫 100글자
        hwp.Run('MoveRight')
        hwp.SetPos(0, 0, 0)

        for i in range(100):
            hwp.Run('MoveRight')

        hwp.Run('MoveSelDocBegin')
        time.sleep(0.05)

        preview = hwp.GetSelectedText()
        hwp.Run('Cancel')

        print(f'  첫 100글자: {preview[:100]}...')

        print(f'\n' + '=' * 70)

    finally:
        client.close_document()
        client.cleanup()


if __name__ == "__main__":
    result_file = Path("Tests/E2E/결과_OneColOneProblem.hwp")

    if not result_file.exists():
        print(f'❌ 결과 파일이 없습니다: {result_file}')
    else:
        analyze_result_file(result_file)
