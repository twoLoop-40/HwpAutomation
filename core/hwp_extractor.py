"""
HWP 문제 추출 모듈 - math-collector의 검증된 로직 사용

이 모듈은 math-collector/src/tools/handle_hwp.py의 검증된 로직을 기반으로 합니다.
EndNote 앵커를 사용하여 HWP 파일에서 개별 문제를 추출합니다.
"""
import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Tuple, Optional
from itertools import islice

# 타입 정의
Block = Tuple[Tuple[int, int, int], Tuple[int, int, int]]


@contextmanager
def open_hwp(file_path: str):
    """
    HWP 파일을 열고 context manager로 관리합니다.

    Args:
        file_path: HWP 파일 경로

    Yields:
        HWP COM 객체
    """
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
    """
    주석 번호(미주·각주)가 붙어 있는 구간을 앞에서부터 차례로 내보냅니다.

    Args:
        hwp: HWP COM 객체

    Yields:
        (start_pos, end_pos) 튜플, 각 pos는 (list, para, pos)
    """
    hwp.Run("MoveDocBegin")
    start = hwp.GetPos()

    ctrl = hwp.HeadCtrl

    while ctrl:
        if ctrl.CtrlID == 'en':  # EndNote 발견
            pset = ctrl.GetAnchorPos(0)
            lst = pset.Item("List")
            para = pset.Item("Para")
            pos = pset.Item("Pos")

            end = (lst, para, pos)
            yield start, end
            start = end

        ctrl = ctrl.Next

    # 마지막 블록 (마지막 EndNote ~ 문서 끝)
    hwp.Run("MoveDocEnd")
    yield start, hwp.GetPos()


def get_block_count(hwp) -> int:
    """HWP 문서에서 사용 가능한 블록 수를 반환합니다."""
    return sum(1 for _ in iter_note_blocks(hwp))


def get_block_by_idx(hwp, idx: int) -> Optional[Block]:
    """
    인덱스로 블록을 가져옵니다. 범위를 벗어나면 None을 반환합니다.

    Args:
        hwp: HWP COM 객체
        idx: 블록 인덱스 (1-based)

    Returns:
        (start_pos, end_pos) 튜플 또는 None
    """
    if idx < 1:
        print(f"경고: idx는 1 이상이어야 합니다. 입력값: {idx}")
        return None

    # 사용 가능한 블록 수 확인
    total_blocks = get_block_count(hwp)
    if idx > total_blocks:
        print(f"경고: 요청한 인덱스 {idx}가 사용 가능한 블록 수 {total_blocks}를 초과합니다.")
        return None

    # idx 번째 블록 가져오기 (0-based로 변환)
    return next(islice(iter_note_blocks(hwp), idx - 1, idx), None)


def save_block(hwp, *, filepath: str | Path, fmt: str = "HWP") -> bool:
    """
    현재 선택된 블록을 파일로 저장합니다.

    Args:
        hwp: HWP COM 객체
        filepath: 저장할 파일 경로
        fmt: 파일 형식 (기본값: "HWP")

    Returns:
        저장 성공 여부
    """
    filepath_str = str(filepath)

    hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
    hwp.HParameterSet.HFileOpenSave.filename = filepath_str
    hwp.HParameterSet.HFileOpenSave.Format = fmt
    hwp.HParameterSet.HFileOpenSave.Attributes = 1

    result_bool: bool = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

    return result_bool


def make_hwp_path(
    src: str,
    file_id: int,
    *,
    out_dir: str | Path | None = None,
    origin_dir: str | None = None,
    csv_filename: str | None = None,
    fmt: str = "HWP",
) -> Path:
    """
    저장할 HWP 파일 경로를 생성합니다.

    Args:
        src: 문제 이름
        file_id: 파일 ID (origin_num)
        out_dir: 출력 디렉토리 (선택)
        origin_dir: 원본 디렉토리 (선택)
        csv_filename: CSV 파일명 (폴더명 결정용, 선택)
        fmt: 파일 형식

    Returns:
        생성된 파일 경로
    """
    if out_dir:
        base_dir = Path(out_dir)
    elif origin_dir:
        base_dir = Path(origin_dir)
    elif csv_filename:
        # CSV 파일명에서 확장자 제거하여 폴더명으로 사용
        folder_name = Path(csv_filename).stem
        base_dir = Path.cwd() / folder_name
    else:
        base_dir = Path.cwd()

    base_dir.mkdir(parents=True, exist_ok=True)

    # 파일명 생성: src_파일ID.확장자
    ext = fmt.lower()
    if ext == "hwp":
        ext = "hwp"

    filename = f"{src}_{file_id}.{ext}"
    return base_dir / filename


def select_and_save(
    hwp,
    *,
    origin_dir: str | Path = None,
    idx: int,
    origin_num: int | None = None,
    csv_filename: str | None = None,
    get_block = get_block_by_idx
):
    """
    주어진 인덱스의 블록을 선택하고 저장하는 함수를 반환합니다.

    Args:
        hwp: HWP COM 객체
        origin_dir: 출력 디렉토리
        idx: 블록 인덱스
        origin_num: 문제 고유 번호 (파일명에 사용)
        csv_filename: CSV 파일명 (폴더 결정용)
        get_block: 블록 가져오기 함수

    Returns:
        save_selected_block 함수 (src를 받아서 저장)

    Raises:
        IndexError: 인덱스가 범위를 벗어난 경우
    """
    block = get_block(hwp, idx)
    if block is None:
        raise IndexError(f"idx={idx} out of range")

    def save_selected_block(src: str):
        start, end = block

        # 블록 선택
        hwp.SetPos(*start)
        hwp.Run("Select")  # 블록 선택 시작
        hwp.SetPos(*end)

        # origin_num이 있으면 그걸 사용, 없으면 idx 사용 (하위 호환)
        file_id = origin_num if origin_num is not None else idx
        target_path = make_hwp_path(src, file_id, origin_dir=origin_dir, csv_filename=csv_filename)
        result = save_block(hwp, filepath=target_path)

        return result, target_path

    return save_selected_block


def extract_problem(
    hwp_file_path: str,
    idx: int,
    src: str,
    origin_num: int,
    output_dir: str | None = None,
    csv_filename: str | None = None
) -> Tuple[bool, Path | None]:
    """
    HWP 파일에서 특정 인덱스의 문제를 추출합니다.

    Args:
        hwp_file_path: HWP 파일 경로
        idx: 블록 인덱스 (1-based)
        src: 문제 이름
        origin_num: 문제 고유 번호
        output_dir: 출력 디렉토리 (선택)
        csv_filename: CSV 파일명 (폴더 결정용, 선택)

    Returns:
        (성공 여부, 저장된 파일 경로) 튜플
    """
    try:
        with open_hwp(hwp_file_path) as hwp:
            saver = select_and_save(
                hwp,
                idx=idx,
                origin_num=origin_num,
                origin_dir=output_dir,
                csv_filename=csv_filename
            )
            return saver(src)
    except Exception as e:
        print(f"추출 오류: {e}")
        return False, None
