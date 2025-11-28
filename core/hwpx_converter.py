# -*- coding: utf-8 -*-
"""
HWPX to HWP Converter

Idris2 명세: Specs/Seperate2Img/HwpxConversion.idr
"""

from pathlib import Path
from typing import Optional, Tuple
import os

from core.automation_client import AutomationClient


def convert_hwpx_to_hwp(
    hwpx_path: str,
    output_path: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    HWPX를 HWP로 변환

    Idris2 명세: HwpxConverter.convertHwpxToHwp

    Args:
        hwpx_path: 입력 HWPX 파일 경로
        output_path: 출력 HWP 파일 경로 (None이면 자동 생성)

    Returns:
        Tuple[success, output_path, error_message]
        - success: 변환 성공 여부
        - output_path: 생성된 HWP 파일 경로 (실패 시 None)
        - error_message: 에러 메시지 (성공 시 None)
    """
    client = None
    try:
        hwpx_path_obj = Path(hwpx_path).absolute()

        if not hwpx_path_obj.exists():
            return False, None, f"File not found: {hwpx_path}"

        # 출력 경로 생성
        if output_path is None:
            # 같은 폴더에 확장자만 변경
            output_path = str(hwpx_path_obj.with_suffix('.hwp'))

        output_path_obj = Path(output_path).absolute()

        # AutomationClient 사용
        client = AutomationClient()

        # 보안 모듈 등록 (팝업 방지)
        client.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # HWPX 파일 열기
        open_result = client.open_document(str(hwpx_path_obj))
        if not open_result.success:
            return False, None, f"Failed to open HWPX: {open_result.error}"

        # HWP 형식으로 저장
        save_result = client.save_document_as(str(output_path_obj), format="HWP")

        # HWP 종료
        client.cleanup()
        client = None

        if save_result.success:
            return True, str(output_path_obj), None
        else:
            return False, None, f"SaveAs failed: {save_result.error}"

    except Exception as e:
        # 에러 발생 시 클라이언트 정리
        if client is not None:
            try:
                client.cleanup()
            except:
                pass
        return False, None, f"Exception: {str(e)}"


def ensure_hwp_format(input_path: str, temp_dir: str) -> Optional[str]:
    """
    HWPX 확인 및 자동 변환

    Idris2 명세: HwpxConverter.ensureHwpFormat

    Args:
        input_path: 입력 파일 경로 (.hwp 또는 .hwpx)
        temp_dir: 변환된 파일을 저장할 임시 디렉토리

    Returns:
        HWP 파일 경로 (변환 실패 또는 지원하지 않는 형식이면 None)

    로직:
        1. 파일 형식 감지 (detectFileFormat)
        2. HWP: 원본 경로 반환
        3. HWPX: HWP로 변환 후 경로 반환
        4. 기타: None 반환
    """
    ext = os.path.splitext(input_path)[1].lower()

    # Case 1: 이미 HWP 형식 (변환 불필요)
    if ext == '.hwp':
        return input_path

    # Case 2: HWPX 형식 (변환 필요)
    if ext == '.hwpx':
        # 임시 폴더에 변환 파일 생성
        # Idris 명세: baseName = stripExtension fileName
        #            outputName = baseName ++ ".converted.hwp"
        filename = Path(input_path).stem  # 확장자 제거
        output_path = os.path.join(temp_dir, f"{filename}.converted.hwp")

        success, path, err = convert_hwpx_to_hwp(input_path, output_path)

        if success:
            print(f"[OK] HWPX -> HWP 변환 완료: {path}")
            return path
        else:
            print(f"[FAIL] HWPX 변환 실패: {err}")
            return None

    # Case 3: 지원하지 않는 형식
    print(f"[FAIL] 지원하지 않는 파일 형식: {ext}")
    return None
