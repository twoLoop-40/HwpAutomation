"""
HWP Copy/Paste 추출 - AppV1 Merger 패턴

Idris2 명세: Specs/Extractor/SequentialExtraction.idr (Solution3_CopyPaste)

검증됨: AppV1 Merger에서 40문항 100% 성공

방식:
1. 블록 선택
2. Copy
3. 새 문서 생성
4. Paste
5. 새 문서 저장
6. 새 문서 닫기
"""
import win32com.client as win32
import pythoncom
from contextlib import contextmanager
from pathlib import Path
from typing import Tuple, Optional, List

from .hwp_extractor import open_hwp, iter_note_blocks, Block


def extract_block_copypaste(
    hwp,
    block: Block,
    filepath: str | Path,
    verbose: bool = False
) -> bool:
    """
    Copy/Paste 방식으로 단일 블록 추출

    Idris2 명세:
    Solution3_CopyPaste =
      (hwp : AnyPtr)
      -> (block : Block)
      -> (filepath : String)
      -> IO Bool

    Args:
        hwp: HWP COM 객체 (원본 파일)
        block: (start_pos, end_pos) 블록
        filepath: 저장할 경로
        verbose: 상세 로그 출력 여부

    Returns:
        성공 여부
    """
    start, end = block
    filepath_str = str(filepath)

    try:
        if verbose:
            print(f"  [1] 블록 선택: {start} → {end}")

        # 1. 블록 선택 (MovePos 방식으로 변경)
        # SetPos로 시작 위치 이동
        hwp.SetPos(*start)
        # Select 시작
        hwp.Run("Select")
        # MovePos로 끝 위치까지 선택 확장
        hwp.MovePos(*end)

        if verbose:
            print(f"  [2] Copy")
        # 2. Copy
        hwp.Run("Copy")

        if verbose:
            print(f"  [3] 새 문서 생성")
        # 3. 새 문서 생성
        hwp.Run("FileNew")

        if verbose:
            print(f"  [4] Paste")
        # 4. Paste
        hwp.Run("Paste")

        if verbose:
            print(f"  [5] 저장: {filepath_str}")
        # 5. 새 문서 저장
        hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = filepath_str
        hwp.HParameterSet.HFileOpenSave.Format = "HWP"
        hwp.HParameterSet.HFileOpenSave.Attributes = 1
        result = hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)

        if verbose:
            print(f"  [6] 새 문서 닫기")
        # 6. 새 문서 닫기
        hwp.Run("FileClose")

        # 7. 파일 저장 완료 대기 (디스크 I/O 완료까지)
        import time
        time.sleep(0.5)  # 500ms 대기

        if verbose:
            print(f"  [OK] 완료: result={result}")
        return result

    except Exception as e:
        print(f"  [FAIL] Copy/Paste 추출 오류: {e}")
        import traceback
        traceback.print_exc()

        # 오류 발생 시 새 문서 닫기 시도
        try:
            hwp.Run("FileClose")
        except:
            pass

        return False


def extract_all_blocks_copypaste(
    hwp_file_path: str,
    selected_blocks: List[int],
    output_dir: str | Path
) -> List[Tuple[bool, Optional[Path]]]:
    """
    Copy/Paste 방식으로 여러 블록 추출

    Idris2 명세:
    Solution3_CopyPaste_Multiple =
      (hwp_file_path : String)
      -> (selected_blocks : List Nat)
      -> (output_dir : String)
      -> IO (List (Bool, String))

    Args:
        hwp_file_path: 원본 HWP 파일
        selected_blocks: 추출할 블록 인덱스 [1, 3, 5] (1-based)
        output_dir: 출력 디렉토리

    Returns:
        [(성공여부, 저장경로), ...] 리스트
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    with open_hwp(hwp_file_path) as hwp:
        # 전체 블록 수집 (제너레이터 → 리스트)
        all_blocks = list(iter_note_blocks(hwp))

        for idx in selected_blocks:
            # 1-based → 0-based
            if idx < 1 or idx > len(all_blocks):
                print(f"경고: 인덱스 {idx}가 범위를 벗어남 (전체 {len(all_blocks)}개)")
                results.append((False, None))
                continue

            block = all_blocks[idx - 1]

            # 저장 경로
            filename = f"문제_{idx:03d}.hwp"
            filepath = output_path / filename

            # Copy/Paste 추출
            success = extract_block_copypaste(hwp, block, filepath)

            if success and filepath.exists():
                results.append((True, filepath))
            else:
                results.append((False, None))

    return results


def extract_all_sequential_copypaste(
    hwp_file_path: str,
    output_dir: str | Path
) -> List[Tuple[bool, Optional[Path]]]:
    """
    모든 블록을 순차적으로 Copy/Paste 추출

    Args:
        hwp_file_path: 원본 HWP 파일
        output_dir: 출력 디렉토리

    Returns:
        [(성공여부, 저장경로), ...] 리스트
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []

    with open_hwp(hwp_file_path) as hwp:
        for idx, block in enumerate(iter_note_blocks(hwp), 1):
            # 저장 경로
            filename = f"문제_{idx:03d}.hwp"
            filepath = output_path / filename

            # Copy/Paste 추출
            success = extract_block_copypaste(hwp, block, filepath)

            if success and filepath.exists():
                results.append((True, filepath))
            else:
                results.append((False, None))

    return results
