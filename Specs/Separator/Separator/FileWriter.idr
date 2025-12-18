||| 파일 저장 명세
|||
||| 추출된 문제를 개별 파일로 저장

module Specs.Separator.Separator.FileWriter

import Specs.Separator.Separator.Types

%default total

||| 저장 단계
public export
data WriteStep : Type where
  CreateOutputDir : WriteStep  -- 출력 디렉토리 생성
  GenerateFilename : WriteStep  -- 파일명 생성
  FormatContent : WriteStep  -- 내용 포맷팅
  WriteFile : WriteStep  -- 파일 쓰기
  VerifyWritten : WriteStep  -- 쓰기 검증

||| 파일명 생성 (단일 문제)
|||
||| @ rule 파일명 규칙
||| @ problemNum 문제 번호
public export
generateFilename : NamingRule -> ProblemNumber -> String
generateFilename rule (MkProblemNumber n) =
  rule.namePrefix ++ "_" ++ padNumber rule.digitCount n ++ extensionToString rule.fileExtension
  where
    padNumber : Nat -> Nat -> String
    padNumber digits num =
      -- 실제 구현에서는 적절히 패딩
      -- 예: 3자리면 "001", "002", ...
      show num

||| 그룹 파일명 생성
|||
||| DefaultPrefix: "문제_001-030.hwp" (범위 표시)
||| CustomPrefix: "2025 커팅_수학2_함수의극한_1.hwp" (순번만)
|||
||| @ rule 파일명 규칙
||| @ groupNum 그룹 번호 (1부터 시작)
||| @ startProb 시작 문제 번호
||| @ endProb 끝 문제 번호
public export
generateGroupFilename : NamingRule -> Nat -> ProblemNumber -> ProblemNumber -> String
generateGroupFilename rule groupNum (MkProblemNumber start) (MkProblemNumber end) =
  let ext = extensionToString rule.fileExtension in
  case rule.strategy of
    DefaultPrefix =>
      -- 기본 전략: "문제_001-030.hwp"
      if start == end
        then rule.namePrefix ++ "_" ++ show start ++ ext
        else rule.namePrefix ++ "_" ++ show start ++ "-" ++ show end ++ ext
    CustomPrefix customPrefix =>
      -- 커스텀 전략: "2025 커팅_수학2_함수의극한_1.hwp" (그룹 순번만 사용)
      customPrefix ++ "_" ++ show groupNum ++ ext

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
