module Specs.Seperate2Img.Types

import System.File

%default total

||| 플러그인 설정
public export
record Seperate2ImgConfig where
  constructor MkConfig
  inputPath : String
  outputDir : String
  dpi : Int             -- 이미지 해상도 (기본 300)
  format : String       -- 이미지 포맷 (png, jpg)
  trimWhitespace : Bool -- 이미지 여백 제거 여부
  tempDir : String      -- 중간 HWP/PDF 저장 경로
  verbose : Bool

||| 작업 진행 상태
public export
data ProcessingState = 
    Initial
  | Separating          -- 1. 문제 분리 중 (HWP -> HWP files)
  | ConvertingToPdf     -- 2. PDF 변환 중 (HWP files -> PDF files)
  | ConvertingToImg     -- 3. 이미지 변환 중 (PDF files -> Image files)
  | CleaningUp          -- 4. 임시 파일 정리
  | Completed
  | Failed String

||| 처리 결과
public export
record ProcessingResult where
  constructor MkResult
  success : Bool
  totalCount : Nat
  successCount : Nat
  failedCount : Nat
  outputFiles : List String
