"""
원본 파일들의 BreakColumn 조사

BreakColumn은 HWP API로 직접 감지하기 어려우므로
단 정보(ColDef)를 확인하거나 GetCurFieldName으로 감지
"""
import sys
import codecs
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from src.automation.client import AutomationClient

# 테스트할 파일들 (처음 10개)
problem_dir = Path("Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905")
all_files = sorted(problem_dir.glob("*.hwp"))
problem_files_paths = [f for f in all_files if not f.name.startswith('[문항')][:10]

print('=' * 70)
print('원본 파일 BreakColumn 조사 (처음 10개)')
print('=' * 70)
print()

# 클라이언트 초기화
client = AutomationClient()
hwp = client.hwp

# 보안 모듈
hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

# 창 숨기기
try:
    hwp.XHwpWindows.Item(0).Visible = False
except:
    pass

try:
    for i, file_path in enumerate(problem_files_paths, 1):
        print(f'[{i:2d}] {file_path.name[:50]:50s}', end='')

        try:
            # 파일 열기
            hwp.Open(str(file_path.absolute()), "HWP", "")
            time.sleep(0.1)

            pages = hwp.PageCount

            # BreakColumn 감지 방법 1: Para를 순회하며 GetCurFieldName 확인
            hwp.Run("MoveDocBegin")
            time.sleep(0.02)

            breakcolumn_count = 0
            para_count = 0
            max_paras = 200

            while para_count < max_paras:
                # 현재 위치의 필드 확인
                try:
                    field_name = hwp.GetCurFieldName()
                    if field_name and 'BreakColumn' in str(field_name):
                        breakcolumn_count += 1
                except:
                    pass

                # Para 끝으로 이동
                hwp.Run("MoveParaEnd")
                time.sleep(0.01)

                # 다음 Para로 이동
                before_pos = hwp.GetPos()
                hwp.Run("MoveNextParaBegin")
                time.sleep(0.01)
                after_pos = hwp.GetPos()

                # 위치가 변하지 않으면 마지막
                if after_pos == before_pos:
                    break

                para_count += 1

            # BreakColumn 감지 방법 2: 단 정보 확인 (PageDef의 ColCount)
            # 여러 단이 존재하는지 확인
            hwp.Run("MoveDocBegin")
            time.sleep(0.02)

            try:
                # HWPControl 또는 ParameterSet으로 ColCount 확인
                act = hwp.CreateAction("ColDef")
                pset = act.CreateSet()
                act.GetDefault(pset)

                col_count = pset.Item("Count")

                print(f' P:{pages:2d} Para:{para_count:3d} Col:{col_count} BC:{breakcolumn_count}')

            except Exception as e:
                print(f' P:{pages:2d} Para:{para_count:3d} BC:{breakcolumn_count} (ColDef 실패)')

            # 파일 닫기
            hwp.Clear(1)  # 저장하지 않고 닫기
            time.sleep(0.05)

        except Exception as e:
            print(f' ❌ 실패: {str(e)[:30]}')
            try:
                hwp.Clear(1)
            except:
                pass

    print('\n' + '=' * 70)
    print('조사 완료')
    print('=' * 70)

except Exception as e:
    print(f'\n💥 오류 발생: {e}')
    import traceback
    traceback.print_exc()

finally:
    # 정리
    client.cleanup()
    time.sleep(0.5)
