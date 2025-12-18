module Specs.Seperate2Img.HwpxConversion

import Specs.Seperate2Img.Types
import Specs.Common.File
import Specs.Common.Result
import Data.String
import Data.Maybe
import Data.List

%default total

-- Forward declaration for Seperate2ImgOps (실제 구현은 Workflow.idr)
public export
interface Seperate2ImgOps where
  preprocessInput : String -> Seperate2ImgConfig -> IO String
  separateProblems : Seperate2ImgConfig -> IO (List String)
  convertToPdf : List String -> IO (List String)
  convertToImage : List String -> Seperate2ImgConfig -> IO (List String)

{-
HWPX → HWP 변환 명세
=====================

문제 상황:
  - HWPX 파일은 XML 기반으로 분리가 잘 됨
  - 하지만 이미지 변환(OLE Automation) 시 일부 내용이 누락되거나,
    기존 HWP 기반 워크플로우 도구들과 호환되지 않는 경우가 있음
  - HWP 파일은 이미지 변환 및 기존 자동화 도구가 완벽하게 작동함

해결 방안:
  1. HWPX 파일을 HWP로 먼저 변환 (전처리 단계)
  2. 변환된 HWP로 전체 워크플로우 진행

워크플로우 변경:
  Before: Input(HWPX) → Separate → PDF → Image
  After:  Input(HWPX) → HWP → Separate → PDF → Image
-}

-- ============================================================
-- Types (공통 Outcome/Error/Format 사용)
-- ============================================================

||| HWPX -> HWP 변환 성공 시 산출물
public export
record HwpxConverted where
  constructor MkHwpxConverted
  inputPath : String
  outputPath : String

-- ============================================================
-- HWPX → HWP 변환 인터페이스
-- ============================================================

||| HWPX를 HWP로 변환하는 작업
|||
||| 구현:
|||   - pyhwpx 사용
|||   - hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule") -- 필수
|||   - hwp.Open(hwpx_path)
|||   - hwp.SaveAs(hwp_path, format="HWP")
|||   - 원본 HWPX는 유지
public export
interface HwpxConverter where
  ||| HWPX → HWP 변환
  ||| Args:
  |||   hwpxPath: 입력 HWPX 파일 경로
  |||   outputPath: 출력 HWP 파일 경로 (Nothing이면 자동 생성)
  ||| Returns:
  |||   Outcome ok HwpxConverted
  |||   - ok=True: 변환된 outputPath가 반드시 존재
  |||   - ok=False: Error가 반드시 존재
  convertHwpxToHwp : String -> Maybe String -> IO (ok ** Outcome ok HwpxConverted)

-- ============================================================
-- 워크플로우 통합
-- ============================================================

||| 입력 파일 형식 감지
||| 대소문자 무시하고 확장자 확인
public export
detectFileFormat : String -> Maybe DocFormat
detectFileFormat = detectDocFormat

||| 파일 경로에서 파일명만 추출 (확장자 포함)
||| 예: "C:/Temp/file.hwpx" -> "file.hwpx"
getFileName : String -> String
getFileName path =
    case reverse (unpack path) of
        [] => ""
        cs => case break (\c => c == '/' || c == '\\') cs of
                  (name, _) => pack (reverse name)

||| 파일명에서 확장자 제거
||| 예: "file.hwpx" -> "file"
||| 확장자가 없으면 원본 그대로 반환
stripExtension : String -> String
stripExtension filename =
    let chars = unpack filename in
    case break (== '.') chars of
        (name, []) => pack name      -- 점이 없음: 원본 반환
        (name, _ :: _) => pack name  -- 점 발견: 점 앞부분 반환
        _ => filename                -- 기타: 원본 반환

||| 필요시 HWPX를 HWP로 자동 변환
|||
||| 로직:
|||   1. 파일 형식 감지
|||   2. HWPX인 경우:
|||      a. HWP로 변환 (파일명 유지, 확장자만 .hwp로 변경)
|||      b. 변환된 HWP 경로 반환 (Right path)
|||      c. 실패 시 에러 반환 (Left error)
|||   3. HWP인 경우:
|||      - 원본 경로 그대로 반환
|||   4. 기타:
|||      - 오류 반환
public export
ensureHwpFormat : HwpxConverter => String -> String -> IO (ok ** Outcome ok String)
ensureHwpFormat inputPath tempDir = do
  case detectFileFormat inputPath of
    Just HWP => pure (True ** Ok inputPath)  -- 이미 HWP, 변환 불필요
    Just HWPX => do
      -- HWPX → HWP 변환 필요
      -- 파일명 충돌 방지를 위해 원본 파일명 활용
      let fileName = getFileName inputPath
      -- Python 구현 가이드에 따라 확장자 교체 방식 권장
      -- 명시적으로 지정하여 제어권 확보

      -- 임시 경로 생성: 확장자 제거 후 .converted.hwp 추가
      let baseName = stripExtension fileName
      let outputName = baseName ++ ".converted.hwp"
      let hwpPath = tempDir ++ "/" ++ outputName

      (ok ** out) <- convertHwpxToHwp inputPath (Just hwpPath)
      case out of
        Ok conv => pure (True ** Ok conv.outputPath)
        Fail e  => pure (False ** Fail e)

    _ => pure (False ** Fail (MkError Unsupported ("Unsupported file format: " ++ inputPath)))

-- ============================================================
-- 수정된 워크플로우
-- ============================================================

||| 수정된 Seperate2Img 워크플로우
|||
||| Before:
|||   preprocessInput -> separateProblems -> convertToPdf -> convertToImage
|||
||| After:
|||   ensureHwpFormat -> preprocessInput -> separateProblems -> convertToPdf -> convertToImage
public export
runWorkflowWithConversion : (HwpxConverter, Seperate2ImgOps) => Seperate2ImgConfig -> IO ProcessingResult
runWorkflowWithConversion config = do
  -- 0a. HWPX → HWP 변환 (필요시)
  convertResult <- ensureHwpFormat config.inputPath config.tempDir

  case convertResult of
    (_ ** Fail _) =>
      -- 변환 실패 시 즉시 종료
      -- ProcessingResult에 에러 메시지를 담을 필드가 없다면(기존 타입 유지 시)
      -- success=False로 반환하고 로그를 남겨야 함.
      pure $ MkResult False 0 0 0 []

    (_ ** Ok hwpPath) => do
      -- 변환된 HWP로 설정 업데이트
      -- 주의: config 레코드 업데이트 구문은 Idris 버전에 따라 다름.
      -- 여기서는 일반적인 레코드 업데이트 구문 사용 가정
      let processedConfig = { inputPath := hwpPath } config

      -- 기존 워크플로우 계속 진행
      -- 0b. 전처리
      preprocessedInput <- preprocessInput processedConfig.inputPath processedConfig

      -- 1. 분리
      hwpFiles <- separateProblems ({ inputPath := preprocessedInput } processedConfig)

      -- 2. PDF 변환
      pdfFiles <- convertToPdf hwpFiles

      -- 3. 이미지 변환
      imgFiles <- convertToImage pdfFiles processedConfig

      -- 결과 반환
      pure $ MkResult
        True
        (length hwpFiles)
        (length imgFiles)
        (minus (length hwpFiles) (length imgFiles))
        imgFiles

{-
Python Implementation Guide
============================

File: core/hwpx_converter.py

Dependencies:
    - pyhwpx
    - pathlib

Key Improvements:
1. **Security Module**: `RegisterModule` is crucial for automation stability.
2. **Path Handling**: Use `Path` for robust extension replacement.
3. **Error Handling**: Capture COM exceptions explicitly.

```python
from pyhwpx import Hwp
from pathlib import Path
from typing import Optional, Tuple
import os

def convert_hwpx_to_hwp(
    hwpx_path: str,
    output_path: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    HWPX를 HWP로 변환
    """
    try:
        hwpx_path_obj = Path(hwpx_path).absolute()

        if not hwpx_path_obj.exists():
             return False, None, f"File not found: {hwpx_path}"

        # 출력 경로 생성
        if output_path is None:
            # 같은 폴더에 확장자만 변경
            output_path = str(hwpx_path_obj.with_suffix('.hwp'))

        output_path_obj = Path(output_path).absolute()

        # HWP 열기
        hwp = Hwp()
        # 보안 모듈 등록 (팝업 방지)
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        hwp.Open(str(hwpx_path_obj))

        # HWP 형식으로 저장
        pset = hwp.HParameterSet.HFileOpenSave
        hwp.HAction.GetDefault("FileSaveAs_S", pset.HSet)
        pset.FileName = str(output_path_obj)
        pset.Format = "HWP"
        pset.Attributes = 0

        result = hwp.HAction.Execute("FileSaveAs_S", pset.HSet)

        hwp.Quit()

        if result:
            return True, str(output_path_obj), None
        else:
            return False, None, "SaveAs action failed (Execute returned False)"

    except Exception as e:
        return False, None, f"Exception: {str(e)}"


def ensure_hwp_format(input_path: str, temp_dir: str) -> Optional[str]:
    """
    HWPX 확인 및 자동 변환
    """
    ext = os.path.splitext(input_path)[1].lower()

    if ext == '.hwp':
        return input_path

    if ext == '.hwpx':
        # 임시 폴더에 변환 파일 생성
        filename = Path(input_path).stem
        output_path = os.path.join(temp_dir, f"{filename}_converted.hwp")

        success, path, err = convert_hwpx_to_hwp(input_path, output_path)

        if success:
            return path
        else:
            print(f"[Error] HWPX conversion failed: {err}")
            return None

    return None  # Unsupported format
```
-}
