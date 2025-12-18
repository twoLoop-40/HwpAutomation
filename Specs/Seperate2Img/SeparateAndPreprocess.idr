module Specs.Seperate2Img.SeparateAndPreprocess

import Specs.Seperate2Img.Types
import Specs.Seperate2Img.HwpxConversion
import Specs.Common.Result
import Data.List
import Data.String

%default total

{-
Separate → Parallel Preprocess Workflow
========================================

문제 상황:
  - 원본 파일 전체를 전처리(1단 변환, 빈문단 제거)하면 메모리 부족이나 COM 오류로 실패하는 경우가 있음
  - 특히 파일이 크거나(수백 페이지) 구조가 복잡할 때 발생
  - 하지만 이미 분리된 작은 파일들(1~2페이지)은 전처리가 매우 잘 됨

해결 방안:
  1. 먼저 파일을 분리 (Separator) - 전처리 없이 순수 분리만 수행
  2. 분리된 각 파일에 병렬 전처리 적용 (ParallelPreprocessor) - 작은 파일 단위라 안정적
  3. 전처리된 파일들을 PDF → 이미지로 변환

워크플로우:
  Before: HWPX→HWP → Preprocess(전체, 순차) → Separate → PDF → Image
  After:  HWPX→HWP → Separate → Preprocess(개별, 병렬) → PDF → Image
-}

-- ============================================================
-- 병렬 전처리 인터페이스
-- ============================================================

||| 분리된 파일들에 대한 병렬 전처리 작업
|||
||| math-collector의 ParallelPreprocessor 재사용
|||
||| 구현 참고 (Python):
|||   - automations.merger.parallel_preprocessor.ParallelPreprocessor
|||   - maxWorkers = min(20, len(hwpFiles))
|||   - outputDir = config.tempDir / "preprocessed"
public export
interface ParallelPreprocessor where
  ||| 분리된 파일들에 병렬 전처리 적용
  ||| Args:
  |||   hwpFiles: 분리된 HWP 파일 경로 리스트
  |||   config: Seperate2Img 설정
  ||| Returns:
  |||   전처리된 파일 경로 리스트 (실패한 파일은 제외됨)
  preprocessSeparatedFiles : List String -> Seperate2ImgConfig -> IO (List String)

-- ============================================================
-- 수정된 워크플로우
-- ============================================================

||| Separate → Parallel Preprocess 워크플로우
|||
||| 순서:
|||   0. HWPX → HWP 변환 (필요시)
|||   1. Separator로 문제별로 분리 (전처리 건너뜀)
|||   2. 분리된 파일들에 병렬 전처리 적용
|||   3. PDF 변환
|||   4. 이미지 변환
public export
runWorkflowWithSeparateFirst : (HwpxConverter, ParallelPreprocessor, Seperate2ImgOps) 
                            => Seperate2ImgConfig 
                            -> IO ProcessingResult
runWorkflowWithSeparateFirst config = do
  -- 0. HWPX → HWP 변환 (필요시)
  -- ensureHwpFormat은 HwpxConversion.idr에 정의됨 (Outcome 기반 반환)
  convertResult <- ensureHwpFormat config.inputPath config.tempDir

  case convertResult of
    (_ ** Fail _) =>
      -- 변환 실패
      pure $ MkResult False 0 0 0 []

    (_ ** Ok hwpPath) => do
      -- 1. 분리 (전처리 없이 원본 HWP 바로 분리)
      -- config 업데이트: 입력 경로를 변환된 HWP로 변경
      let splitConfig = { inputPath := hwpPath } config
      hwpFiles <- separateProblems splitConfig

      if null hwpFiles
        then pure $ MkResult False 0 0 0 []
        else do
          -- 2. 분리된 파일들에 병렬 전처리 적용
          -- preprocessedFiles에는 성공한 파일만 포함됨
          preprocessedFiles <- preprocessSeparatedFiles hwpFiles config

          if null preprocessedFiles
            then pure $ MkResult False (length hwpFiles) 0 (length hwpFiles) []
            else do
              -- 3. PDF 변환
              pdfFiles <- convertToPdf preprocessedFiles

              -- 4. 이미지 변환
              imgFiles <- convertToImage pdfFiles config

              -- 결과 반환
              -- total: 분리된 파일 수
              -- success: 최종 이미지 수
              -- failed: 중간에 탈락한 파일 수
              pure $ MkResult
                True
                (length hwpFiles)
                (length imgFiles)
                (minus (length hwpFiles) (length imgFiles))
                imgFiles

{-
Python Implementation Guide
============================

File: automations/seperate2Img/workflow.py

주요 변경 사항:
1. `ParallelPreprocessor` 클래스 활용 (기존 `merger` 모듈)
2. 워크플로우 순서 재배치

```python
def _preprocess_separated_files(self, hwp_files: List[str], temp_dir: str) -> List[str]:
    """분리된 파일들에 병렬 전처리 적용"""
    try:
        from automations.merger.parallel_preprocessor import (
            ParallelPreprocessor,
            PreprocessConfig
        )
    except ImportError:
        print("[Error] ParallelPreprocessor not found. Skipping preprocessing.")
        return hwp_files

    # 전처리 출력 디렉토리
    preprocess_dir = Path(temp_dir) / "preprocessed"
    preprocess_dir.mkdir(parents=True, exist_ok=True)

    # 병렬 전처리 설정
    config = PreprocessConfig(
        max_workers=min(20, len(hwp_files)),  # 파일 수에 맞게 조정
        output_dir=str(preprocess_dir),
        keep_original=False,  # 원본 불필요
        timeout=30.0
    )

    preprocessor = ParallelPreprocessor(config)

    print(f"Starting parallel preprocessing for {len(hwp_files)} files...")
    # 병렬 전처리 실행
    success_results, failed_results = preprocessor.preprocess_parallel(hwp_files)

    # 성공한 파일들의 경로만 반환 (순서 유지 여부 확인 필요하나, 여기선 집합 처리)
    # ParallelPreprocessor 결과는 순서가 보장되지 않을 수 있으므로, 
    # 원본 순서를 유지하려면 파일명 인덱스 등으로 정렬 필요.
    # 여기서는 단순 리스트 반환.
    preprocessed_paths = [r.preprocessed_path for r in success_results if r.preprocessed_path]
    
    # 정렬 (파일명 기준)
    preprocessed_paths.sort()

    print(f"[Preprocessing Done] Success: {len(preprocessed_paths)}, Failed: {len(failed_results)}")

    return preprocessed_paths
```
-}





