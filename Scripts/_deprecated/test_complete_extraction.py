"""
전체 추출 워크플로우 테스트 - math-collector 방식
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
db_root = Path(r"C:\db\mad-label")
output_dir = Path("Tests/seperation/output_complete")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"=== 전체 추출 워크플로우 테스트 ===\n")

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

# 처음 3개 문제만 처리
success_count = 0
fail_count = 0

for i, problem in enumerate(problems[:3], 1):
    src = problem['src']
    origin_num = problem['origin_num']

    print(f"\n{'='*80}")
    print(f"문제 {i}/{len(problems[:3])}")
    print(f"src: {src}")
    print(f"origin_num: {origin_num}")

    # 파일 찾기
    parts = src.rsplit('_', 1)
    if len(parts) != 2:
        print(f"  ✗ src 패턴 오류")
        fail_count += 1
        continue

    base_name = parts[0]
    idx = int(parts[1])  # 블록 인덱스

    possible_file = f"{base_name}.hwp"
    found_files = list(db_root.rglob(possible_file))

    if not found_files:
        print(f"  ✗ 파일 못찾음: {possible_file}")
        fail_count += 1
        continue

    file_path = found_files[0]
    print(f"  ✓ 파일: {file_path.name}")
    print(f"  ✓ 블록 idx: {idx}")

    # 파일 열어서 블록 추출
    try:
        with open_hwp(str(file_path)) as hwp:
            # 블록 리스트 생성
            blocks = list(iter_note_blocks(hwp))
            print(f"  ✓ 총 {len(blocks)}개 블록")

            # idx 번째 블록 가져오기 (1-based index)
            if idx < 1 or idx > len(blocks):
                print(f"  ✗ idx={idx} 범위 초과 (1~{len(blocks)})")
                fail_count += 1
                continue

            block_idx = idx - 1  # 0-based index
            start, end = blocks[block_idx]

            print(f"  ✓ 블록 {idx}: {start} → {end}")

            # 빈 블록 체크
            if start == end:
                print(f"  ⊘ 빈 블록 건너뜀")
                fail_count += 1
                continue

            # 블록 선택
            hwp.SetPos(*start)
            hwp.Run("Select")
            hwp.SetPos(*end)

            # 저장
            output_path = output_dir / f"문제_{origin_num:03d}.hwp"
            result = save_block(hwp, str(output_path))

            if result:
                file_size = output_path.stat().st_size if output_path.exists() else 0
                print(f"  ✓ 저장 성공: {file_size:,} bytes")
                success_count += 1
            else:
                print(f"  ✗ 저장 실패")
                fail_count += 1

    except Exception as e:
        print(f"  ✗ 에러: {e}")
        fail_count += 1

print(f"\n{'='*80}")
print(f"\n결과: 성공 {success_count}/{len(problems[:3])}, 실패 {fail_count}/{len(problems[:3])}")
