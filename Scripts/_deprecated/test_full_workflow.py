"""
전체 워크플로우 테스트 - 실제 CSV 파일 사용
"""
import sys
import codecs
import csv
from pathlib import Path

# UTF-8 출력
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

# math-collector 코드 복사
import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from typing import Generator

Block = tuple[tuple[int, int, int], tuple[int, int, int]]


@contextmanager
def open_hwp(file_path: str):
    """HWP 파일 열기 (context manager)"""
    pythoncom.CoInitialize()
    try:
        hwp = win32.DispatchEx('HwpFrame.HwpObject')
        hwp.RegisterModule('FilePathCheckDLL', 'FilePathCheckerModule')
        hwp.Open(file_path, 'HWP', 'lock:false;forceopen:true')
        hwp.XHwpWindows.Item(0).Visible = False

        yield hwp

        hwp.Quit()
    finally:
        pythoncom.CoUninitialize()


def iter_note_blocks(hwp) -> Generator[Block, None, None]:
    """EndNote 앵커 기반 블록 나누기"""
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl

    while ctrl:
        if ctrl.CtrlID == 'en':
            pset = ctrl.GetAnchorPos(0)
            lst = pset.Item("List")
            para = pset.Item("Para")
            pos = pset.Item("Pos")

            end = (lst, para, pos)
            yield start, end
            start = end

        ctrl = ctrl.Next

    hwp.Run("MoveDocEnd")
    yield start, hwp.GetPos()


def save_block(hwp, filepath: str, fmt: str = "HWP") -> bool:
    """선택된 블록 저장"""
    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    return result


# CSV 파일 읽기
csv_path = r"C:\Users\joonho.lee\Downloads\[맞춤형]사준호_7_내신대비_집합_20251115_1756.csv"
output_dir = Path("Tests/seperation/output_full_workflow")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== 전체 워크플로우 테스트 ===\n")
print(f"CSV: {Path(csv_path).name}\n")

# CSV 읽기
problems = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        problems.append({
            'id': row['id'],
            'origin_num': int(row['origin_num']),
            'src': row['src'],
            'mongo_id': row['mongo_id']
        })

print(f"총 {len(problems)}개 문제\n")

# 각 문제 처리 (처음 3개만)
for i, problem in enumerate(problems[:3], 1):
    print(f"\n{'='*80}")
    print(f"문제 {i}: origin_num={problem['origin_num']}")
    print(f"src: {problem['src'][:50]}...")
    print(f"mongo_id: {problem['mongo_id']}")

    # mongo_id로 파일 찾기 (mad-label DB에서)
    # 실제로는 검색 필요하지만, 일단 하드코딩으로 테스트
    # 예: 22개정 EBS 올림포스 기출문제집 공통수학2 파일 중 하나

    # 여기서는 파일 경로를 어떻게 찾는지 확인 필요
    print(f"  ⚠️  파일 경로 검색 필요 (LangGraph 워크플로우)")
    print(f"     mongo_id: {problem['mongo_id']}")

print(f"\n{'='*80}")
print("\n다음 단계:")
print("1. mongo_id → 파일 경로 매핑 확인")
print("2. 실제 파일 열기")
print("3. iter_note_blocks로 블록 분리")
print("4. save_block으로 저장")
