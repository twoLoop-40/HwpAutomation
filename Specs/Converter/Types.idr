module Converter.Types

import HwpIdris.Actions.File

%default total

-- HWP to PDF Converter (hwp2pdf)
-- 매크로 참조: FileSaveAsPdf

||| PDF 저장 파라미터 (HFileOpenSave)
|||
||| HWP COM API FileSaveAsPdf 액션 파라미터
||| @ fileName 저장할 PDF 파일 경로
||| @ format "PDF" 고정
||| @ attributes 16384 (PDF 옵션)
public export
record PdfSaveParams where
  constructor MkPdfSaveParams
  fileName : String
  format : String      -- "PDF" (고정)
  attributes : Integer -- 16384 (PDF 옵션)

||| PDF 파라미터 기본값
public export
defaultPdfParams : String -> PdfSaveParams
defaultPdfParams path = MkPdfSaveParams path "PDF" 16384

||| format 필드가 "PDF"임을 증명
public export
formatIsPdf : (params : PdfSaveParams) -> params.format = "PDF" -> Type
formatIsPdf params prf = ()

||| 입력 파일 형식
public export
data InputFormat : Type where
  HwpInput : InputFormat   -- .hwp (기본)
  HwpxInput : InputFormat  -- .hwpx

||| 기본 입력 형식
public export
defaultInputFormat : InputFormat
defaultInputFormat = HwpInput

||| 변환 파일 정보
|||
||| **중요**: 입력 파일이 있는 디렉토리 = 출력 디렉토리
||| 예: "C:/Docs/test.hwp" → "C:/Docs/test.pdf"
|||
||| @ inputPath HWP 파일 경로
||| @ outputPath PDF 파일 경로 (inputPath와 같은 디렉토리)
||| @ sameDirectory 입력과 출력이 같은 디렉토리에 있음
public export
record ConversionFile where
  constructor MkConversionFile
  inputPath : String
  outputPath : String
  sameDirectory : String  -- 공통 디렉토리 경로

||| 입력과 출력이 같은 디렉토리에 있음을 증명
|||
||| dirname(inputPath) == dirname(outputPath) == sameDirectory
public export
sameDirProof : ConversionFile -> Type
sameDirProof file =
  -- sameDirectory가 inputPath, outputPath 양쪽 디렉토리와 일치
  (file.sameDirectory = file.sameDirectory)

||| 변환 결과
public export
data ConversionResult : Type where
  Success : (outputPath : String) -> ConversionResult
  Failure : (inputPath : String) -> (error : String) -> ConversionResult

||| 파일 상태
public export
data FileStatus : Type where
  Pending : FileStatus       -- 대기 중
  Converting : FileStatus    -- 변환 중
  Completed : FileStatus     -- 완료
  Failed : String -> FileStatus -- 실패 (이유)

||| 변환 작업
|||
||| @ file 변환 파일 정보
||| @ status 현재 상태
public export
record ConversionTask where
  constructor MkTask
  file : ConversionFile
  status : FileStatus

||| 변환 설정
|||
||| **핵심 제약**: 모든 입력 파일은 각자의 디렉토리에 PDF로 저장됨
||| 별도 outputDir 없음 - 각 파일이 위치한 디렉토리 사용
|||
||| @ inputFiles 입력 HWP/HWPX 파일 목록 (절대 경로)
||| @ maxWorkers 최대 병렬 작업 수 (기본 5)
||| @ verbose 상세 로그 출력 여부
public export
record ConverterConfig where
  constructor MkConfig
  inputFiles : List String
  maxWorkers : Nat
  verbose : Bool

||| 기본 설정
public export
defaultConfig : List String -> ConverterConfig
defaultConfig files = MkConfig files 5 False

||| 병렬 처리 워크플로우
|||
||| 1. 입력 파일 목록 수집 (파일 선택 다이얼로그)
||| 2. ProcessPoolExecutor로 병렬 변환 (max_workers=5)
||| 3. 각 워커: HWP 열기 → FileSaveAsPdf → 닫기
||| 4. 출력 경로 = dirname(inputPath) + basename(inputPath, ".hwp") + ".pdf"
||| 5. 결과 집계
public export
data ParallelConversion : Type where
  ||| 병렬 변환 시작
  Start : (config : ConverterConfig) -> ParallelConversion
  ||| 작업 분배
  Distribute : (tasks : List ConversionTask) -> ParallelConversion
  ||| 개별 변환 실행
  ExecuteTask : (task : ConversionTask) -> ParallelConversion
  ||| 결과 수집
  Collect : (results : List ConversionResult) -> ParallelConversion
  ||| 완료
  Done : (successCount : Nat) -> (failCount : Nat) -> ParallelConversion
