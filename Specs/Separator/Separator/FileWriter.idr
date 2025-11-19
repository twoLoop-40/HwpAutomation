||| 파일 저장 명세
|||
||| 추출된 문제를 개별 파일로 저장

module FileWriter

import Types

%default total

||| 저장 단계
public export
data WriteStep : Type where
  CreateOutputDir : WriteStep  -- 출력 디렉토리 생성
  GenerateFilename : WriteStep  -- 파일명 생성
  FormatContent : WriteStep  -- 내용 포맷팅
  WriteFile : WriteStep  -- 파일 쓰기
  VerifyWritten : WriteStep  -- 쓰기 검증

||| 파일명 생성
|||
||| @ rule 파일명 규칙
||| @ problemNum 문제 번호
public export
generateFilename : NamingRule -> ProblemNumber -> String
generateFilename rule (MkProblemNumber n) =
  rule.namePrefix ++ "_" ++ padNumber rule.digitCount n ++ rule.fileExtension
  where
    padNumber : Nat -> Nat -> String
    padNumber digits num =
      -- 실제 구현에서는 적절히 패딩
      -- 예: 3자리면 "001", "002", ...
      show num

||| 내용 포맷팅
|||
||| @ includeEndNote 미주 포함 여부
||| @ problem 문제 정보
public export
data ContentFormat : Type where
  BodyOnly : ContentFormat  -- 본문만
  BodyWithEndNote : ContentFormat  -- 본문 + 미주
  EndNoteOnly : ContentFormat  -- 미주만

||| 포맷 선택
public export
selectFormat : Bool -> ContentFormat
selectFormat True = BodyWithEndNote
selectFormat False = BodyOnly

||| 파일 쓰기 결과
public export
data WriteResult : Type where
  Written : (filepath : String) -> (bytes : Nat) -> WriteResult
  Skipped : (reason : String) -> WriteResult
  Failed : (filepath : String) -> (error : String) -> WriteResult

||| 일괄 저장 결과
public export
record BatchWriteResult where
  constructor MkBatchResult
  totalProblems : Nat
  successCount : Nat
  failedCount : Nat
  skippedCount : Nat
  outputFiles : List String

||| 저장 워크플로우
public export
writeWorkflow : List WriteStep
writeWorkflow =
  [ CreateOutputDir
  , GenerateFilename
  , FormatContent
  , WriteFile
  , VerifyWritten
  ]

||| 성공 여부 판정
public export
isSuccess : WriteResult -> Bool
isSuccess (Written _ _) = True
isSuccess _ = False

||| 일괄 저장 성공 여부
public export
isBatchSuccess : BatchWriteResult -> Bool
isBatchSuccess result =
  result.failedCount == 0 &&
  result.successCount == result.totalProblems
