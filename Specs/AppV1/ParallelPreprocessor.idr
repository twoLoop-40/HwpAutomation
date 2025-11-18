||| 병렬 전처리 명세 (Parallel Preprocessing Specification)
|||
||| HWP 문항 파일들을 병렬로 전처리하는 타입 안전 명세
||| Python multiprocessing.ProcessPoolExecutor 기반 구현
|||
||| @ author Claude
||| @ date 2025-11-14

module HwpIdris.AppV1.ParallelPreprocessor

import Data.List
import Data.Vect

%default total

--------------------------------------------------------------------------------
-- 타입 정의
--------------------------------------------------------------------------------

||| 병렬 처리 상태
public export
data ParallelState
  = Idle                    -- 대기 중
  | Preprocessing Nat       -- 전처리 중 (진행률)
  | Completed Nat Nat       -- 완료 (성공 개수, 실패 개수)
  | Failed String           -- 실패 (에러 메시지)

||| 전처리 작업 결과
public export
record PreprocessResult where
  constructor MkPreprocessResult
  success : Bool                    -- 성공 여부
  originalPath : String             -- 원본 파일 경로
  preprocessedPath : Maybe String   -- 전처리된 파일 경로 (성공 시)
  paraCount : Nat                   -- Para 개수
  removedCount : Nat                -- 제거된 빈 Para 개수
  processingTime : Double           -- 처리 시간 (초)
  errorMessage : Maybe String       -- 에러 메시지 (실패 시)

||| 전처리 설정
public export
record PreprocessConfig where
  constructor MkPreprocessConfig
  maxWorkers : Nat                  -- 최대 워커 수 (기본: 20)
  outputDir : String                -- 출력 디렉토리
  keepOriginal : Bool               -- 원본 파일 유지 여부
  timeout : Maybe Double            -- 타임아웃 (초)

--------------------------------------------------------------------------------
-- 기본 설정
--------------------------------------------------------------------------------

||| 기본 전처리 설정
||| HwpIdris 명세 기반: maxWorkers = 20
public export
defaultPreprocessConfig : PreprocessConfig
defaultPreprocessConfig = MkPreprocessConfig
  { maxWorkers = 20
  , outputDir = "Tests/AppV1/Preprocessed"
  , keepOriginal = True
  , timeout = Just 30.0
  }

--------------------------------------------------------------------------------
-- 전처리 작업 명세
--------------------------------------------------------------------------------

||| 단일 파일 전처리 작업
|||
||| 순서:
||| 1. 파일 열기
||| 2. 1단으로 변환
||| 3. Para 스캔
||| 4. 빈 Para 제거 (뒤에서부터)
||| 5. 임시 파일로 저장
||| 6. 파일 닫기
public export
data PreprocessTask : Type where
  ||| 전처리 작업 생성
  ||| @filePath 원본 파일 경로
  ||| @outputDir 출력 디렉토리
  ||| @fileIndex 파일 인덱스 (로깅용)
  MkPreprocessTask : (filePath : String)
                  -> (outputDir : String)
                  -> (fileIndex : Nat)
                  -> PreprocessTask

||| 전처리 작업 실행 명세
|||
||| ProcessPoolExecutor.submit(preprocess_single_file, task)
|||
||| 반환: PreprocessResult
public export
preprocessSingleFile : PreprocessTask -> PreprocessResult

--------------------------------------------------------------------------------
-- 병렬 처리 명세
--------------------------------------------------------------------------------

||| 병렬 전처리 워크플로우
|||
||| 순서:
||| 1. ProcessPoolExecutor 생성 (max_workers=config.maxWorkers)
||| 2. 모든 파일에 대해 submit(preprocess_single_file)
||| 3. as_completed()로 완료된 작업부터 수집
||| 4. 진행률 업데이트
||| 5. 모든 작업 완료 대기
||| 6. Executor 종료
public export
data ParallelPreprocessor : Type where
  ||| 병렬 전처리기 생성
  ||| @config 전처리 설정
  MkParallelPreprocessor : (config : PreprocessConfig)
                        -> ParallelPreprocessor

||| 병렬 전처리 실행
|||
||| @preprocessor 병렬 전처리기
||| @filePaths 전처리할 파일 경로 리스트
|||
||| Returns: (성공 결과 리스트, 실패 결과 리스트)
public export
preprocessParallel : (preprocessor : ParallelPreprocessor)
                  -> (filePaths : List String)
                  -> (List PreprocessResult, List PreprocessResult)

--------------------------------------------------------------------------------
-- 진행률 추적
--------------------------------------------------------------------------------

||| 진행률 계산
||| @completed 완료된 작업 수
||| @total 전체 작업 수
public export
calculateProgress : (completed : Nat) -> (total : Nat) -> Double
calculateProgress completed total =
  if total == 0
    then 0.0
    else (cast completed / cast total) * 100.0

||| 진행률 콜백 타입
public export
ProgressCallback : Type
ProgressCallback = Nat -> Nat -> IO ()

--------------------------------------------------------------------------------
-- 에러 처리
--------------------------------------------------------------------------------

||| 전처리 에러 타입
public export
data PreprocessError
  = FileNotFound String             -- 파일을 찾을 수 없음
  | OpenFailed String               -- 파일 열기 실패
  | ScanFailed String               -- Para 스캔 실패
  | SaveFailed String               -- 저장 실패
  | TimeoutError String             -- 타임아웃
  | UnknownError String             -- 알 수 없는 에러

||| 에러 메시지 생성
public export
errorMessage : PreprocessError -> String
errorMessage (FileNotFound path) = "File not found: " ++ path
errorMessage (OpenFailed path) = "Failed to open: " ++ path
errorMessage (ScanFailed path) = "Failed to scan paras: " ++ path
errorMessage (SaveFailed path) = "Failed to save: " ++ path
errorMessage (TimeoutError path) = "Timeout: " ++ path
errorMessage (UnknownError msg) = "Unknown error: " ++ msg

--------------------------------------------------------------------------------
-- 결과 집계
--------------------------------------------------------------------------------

||| 전처리 결과 집계
public export
record PreprocessSummary where
  constructor MkPreprocessSummary
  totalFiles : Nat                  -- 전체 파일 수
  successCount : Nat                -- 성공 개수
  failureCount : Nat                -- 실패 개수
  totalParas : Nat                  -- 전체 Para 수
  totalRemoved : Nat                -- 전체 제거된 Para 수
  totalTime : Double                -- 전체 처리 시간 (초)
  avgTimePerFile : Double           -- 파일당 평균 시간

||| 결과 리스트로부터 집계 생성
public export
summarizeResults : List PreprocessResult -> PreprocessSummary
summarizeResults results =
  let successCount = length $ filter success results
      failureCount = length results - successCount
      totalParas = sum $ map paraCount results
      totalRemoved = sum $ map removedCount results
      totalTime = sum $ map processingTime results
      avgTime = if length results == 0
                  then 0.0
                  else totalTime / (cast $ length results)
  in MkPreprocessSummary
       { totalFiles = length results
       , successCount = successCount
       , failureCount = failureCount
       , totalParas = totalParas
       , totalRemoved = totalRemoved
       , totalTime = totalTime
       , avgTimePerFile = avgTime
       }

--------------------------------------------------------------------------------
-- 성능 예측
--------------------------------------------------------------------------------

||| 병렬 처리 성능 예측
|||
||| 순차 처리 시간: fileCount * avgTimePerFile
||| 병렬 처리 시간: (fileCount / maxWorkers) * avgTimePerFile
|||
||| 예상 개선율: (순차 시간 - 병렬 시간) / 순차 시간 * 100
public export
predictPerformance : (fileCount : Nat)
                  -> (avgTimePerFile : Double)
                  -> (maxWorkers : Nat)
                  -> (sequentialTime : Double, parallelTime : Double, improvement : Double)
predictPerformance fileCount avgTime workers =
  let seqTime = (cast fileCount) * avgTime
      parTime = ((cast fileCount) / (cast workers)) * avgTime
      improve = if seqTime == 0.0
                  then 0.0
                  else ((seqTime - parTime) / seqTime) * 100.0
  in (seqTime, parTime, improve)

--------------------------------------------------------------------------------
-- 예시 사용 시나리오
--------------------------------------------------------------------------------

||| 예시: 41개 파일 병렬 전처리
|||
||| 현재 성능:
||| - 순차 처리: 41 files * 9.8s/file = 401.8초 (~6.7분)
|||
||| 예상 성능 (20 workers):
||| - 병렬 처리: (41 / 20) * 9.8s = 20.09초 (~20초)
||| - 개선율: 95%
|||
||| 실제 고려사항:
||| - 프로세스 생성 오버헤드: ~2초
||| - COM 초기화 오버헤드: ~1초/worker
||| - 예상 실제 시간: 40-50초
||| - 예상 개선율: 87-90%
public export
example41FilesParallel : PreprocessSummary
example41FilesParallel =
  let (seqTime, parTime, improve) = predictPerformance 41 9.8 20
  in MkPreprocessSummary
       { totalFiles = 41
       , successCount = 41
       , failureCount = 0
       , totalParas = 0  -- 실제 실행 후 측정
       , totalRemoved = 0  -- 실제 실행 후 측정
       , totalTime = parTime + 20.0  -- 오버헤드 포함
       , avgTimePerFile = (parTime + 20.0) / 41.0
       }

--------------------------------------------------------------------------------
-- 타입 안전성 보장
--------------------------------------------------------------------------------

||| 모든 파일이 전처리되었음을 보장
|||
||| 입력: n개 파일
||| 출력: n개 결과 (성공 + 실패 = n)
public export
preprocessingCompleteness : (inputs : Vect n String)
                         -> (results : List PreprocessResult)
                         -> {auto prf : length results = n}
                         -> Bool
preprocessingCompleteness _ _ = True

||| 워커 수가 0보다 큼을 보장
public export
validWorkerCount : (workers : Nat) -> {auto prf : GT workers 0} -> Nat
validWorkerCount workers = workers

||| 타임아웃이 양수임을 보장
public export
validTimeout : (timeout : Double) -> {auto prf : GT timeout 0.0} -> Double
validTimeout timeout = timeout
