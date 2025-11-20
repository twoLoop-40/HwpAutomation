"""
HWP to PDF 변환 - 병렬 처리

Idris2 명세: Specs/Converter/Types.idr

주요 기능:
- HWP/HWPX → PDF 변환
- 병렬 처리 (ProcessPoolExecutor, max_workers=5)
- 입력 파일과 같은 디렉토리에 PDF 저장

FileSaveAsPdf 액션:
- HAction.GetDefault("FileSaveAsPdf", HParameterSet.HFileOpenSave.HSet)
- HParameterSet.HFileOpenSave.filename = "경로.pdf"
- HParameterSet.HFileOpenSave.Format = "PDF"
- HParameterSet.HFileOpenSave.Attributes = 16384
- HAction.Execute("FileSaveAsPdf", HParameterSet.HFileOpenSave.HSet)
"""
import win32com.client as win32
import pythoncom
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Tuple, Optional, List
import os


def worker_convert_to_pdf(
    hwp_file_path: str,
    verbose: bool = False
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    워커 함수: 별도 프로세스에서 HWP → PDF 변환

    Idris2 명세:
    WorkerFunction =
      (inputPath : String)
      -> IO (Bool, Maybe String, Maybe String)
      -- (성공 여부, 출력 경로, 에러 메시지)

    Args:
        hwp_file_path: HWP/HWPX 파일 경로
        verbose: 상세 로그 출력 여부

    Returns:
        (success, output_path, error_message)
    """
    pythoncom.CoInitialize()

    try:
        hwp_path = Path(hwp_file_path)
        if not hwp_path.exists():
            return False, None, f"파일 없음: {hwp_file_path}"

        # PDF 경로: 같은 디렉토리, 확장자만 .pdf로 변경
        pdf_path = hwp_path.with_suffix('.pdf')

        if verbose:
            print(f"[변환 시작] {hwp_path.name} → {pdf_path.name}")

        # HWP COM 객체 생성
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 파일 열기
        hwp.Open(str(hwp_path.absolute()), "HWP", "")

        # FileSaveAsPdf 액션 실행
        hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = str(pdf_path.absolute())
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        hwp.HParameterSet.HFileOpenSave.Attributes = 16384

        result = hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)

        if not result:
            hwp.Quit()
            return False, None, f"FileSaveAsPdf 실행 실패: {hwp_path.name}"

        # 파일 닫기
        hwp.Clear(1)  # 저장하지 않고 닫기
        hwp.Quit()

        # PDF 파일 생성 확인
        if not pdf_path.exists():
            return False, None, f"PDF 파일 생성 실패: {pdf_path}"

        if verbose:
            pdf_size = pdf_path.stat().st_size / 1024  # KB
            print(f"[변환 완료] {pdf_path.name} ({pdf_size:.1f} KB)")

        return True, str(pdf_path), None

    except Exception as e:
        return False, None, f"변환 중 에러: {str(e)}"

    finally:
        pythoncom.CoUninitialize()


def convert_hwp_to_pdf_parallel(
    hwp_files: List[str],
    max_workers: int = 5,
    verbose: bool = False
) -> List[Tuple[bool, Optional[str], Optional[str]]]:
    """
    여러 HWP 파일을 병렬로 PDF로 변환

    Idris2 명세:
    ParallelConversion =
      Start (config : ConverterConfig)
      -> Distribute (tasks : List ConversionTask)
      -> ExecuteTask (task : ConversionTask)  -- 병렬 실행
      -> Collect (results : List ConversionResult)
      -> Done (successCount : Nat) (failCount : Nat)

    Args:
        hwp_files: HWP/HWPX 파일 경로 목록
        max_workers: 최대 병렬 워커 수 (기본 5)
        verbose: 상세 로그 출력 여부

    Returns:
        List of (success, output_path, error_message)
    """
    if not hwp_files:
        return []

    if verbose:
        print(f"[병렬 변환 시작] {len(hwp_files)}개 파일, {max_workers} 워커")

    results = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 작업 제출
        futures = {
            executor.submit(worker_convert_to_pdf, hwp_file, verbose): hwp_file
            for hwp_file in hwp_files
        }

        # 결과 수집
        for future in as_completed(futures):
            hwp_file = futures[future]
            try:
                success, output_path, error = future.result()
                results.append((success, output_path, error))

                if verbose:
                    if success:
                        print(f"[성공] {Path(hwp_file).name}")
                    else:
                        print(f"[실패] {Path(hwp_file).name}: {error}")

            except Exception as e:
                results.append((False, None, f"워커 예외: {str(e)}"))
                if verbose:
                    print(f"[실패] {Path(hwp_file).name}: 워커 예외 {e}")

    # 통계
    success_count = sum(1 for s, _, _ in results if s)
    fail_count = len(results) - success_count

    if verbose:
        print(f"\n[변환 완료] 성공: {success_count}, 실패: {fail_count}")

    return results


def convert_single_hwp_to_pdf(
    hwp_file_path: str,
    verbose: bool = False
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    단일 HWP 파일을 PDF로 변환 (병렬 처리 없음)

    Args:
        hwp_file_path: HWP/HWPX 파일 경로
        verbose: 상세 로그 출력 여부

    Returns:
        (success, output_path, error_message)
    """
    return worker_convert_to_pdf(hwp_file_path, verbose)
