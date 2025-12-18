||| Separator 전체 워크플로우
|||
||| 파싱 → 추출 → 저장 통합

module Specs.Separator.Separator.Workflow

import Specs.Separator.Separator.Types
import Specs.Separator.Separator.XmlParser
import Specs.Separator.Separator.Extractor
import Specs.Separator.Separator.FileWriter
import Specs.Common.Result
import Specs.Common.Workflow

%default total

||| 전체 워크플로우 단계
public export
data WorkflowStage : Type where
  Input : WorkflowStage  -- 입력 파일 처리
  Parse : WorkflowStage  -- XML 파싱
  Extract : WorkflowStage  -- 문제 추출
  Write : WorkflowStage  -- 파일 저장
  Complete : WorkflowStage  -- 완료

||| 워크플로우 상태
public export
data WorkflowState : Type where
  NotStarted : WorkflowState
  Processing : WorkflowStage -> WorkflowState
  Succeeded : BatchWriteResult -> WorkflowState
  Failed : WorkflowStage -> Error -> WorkflowState

||| 전체 파이프라인
|||
||| HWP/HWPX → Parse → Extract → Write → Result
public export
separatorPipeline : SeparatorConfig -> WorkflowState
separatorPipeline config =
  let stage1 = processInput config.inputPath config.inputFormat
      stage2 = parseXml stage1
      stage3 = extractProblems stage2 config.includeEndNote
      stage4 = writeFiles stage3 config.outputDir config.namingRule
  in evaluateResult stage4
  where
    processInput : String -> InputFormat -> WorkflowState
    processInput path HwpInput = Processing Input
    processInput path HwpxInput = Processing Parse

    parseXml : WorkflowState -> WorkflowState
    parseXml (Processing Input) = Processing Parse
    parseXml (Processing Parse) = Processing Extract
    parseXml other = other

    extractProblems : WorkflowState -> Bool -> WorkflowState
    extractProblems (Processing Extract) includeNote = Processing Write
    extractProblems other _ = other

    writeFiles : WorkflowState -> String -> NamingRule -> WorkflowState
    writeFiles (Processing Write) outDir naming = Processing Complete
    writeFiles other _ _ = other

    evaluateResult : WorkflowState -> WorkflowState
    evaluateResult (Processing Complete) =
      Succeeded (MkBatchResult 408 408 0 0 [])  -- 임시
    evaluateResult other = other

||| 단계별 진행률
public export
calculateProgress : WorkflowStage -> Nat
calculateProgress Input = 0
calculateProgress Parse = 20
calculateProgress Extract = 50
calculateProgress Write = 80
calculateProgress Complete = 100

||| 예상 소요 시간 (초)
|||
||| @ problemCount 문제 개수
public export
estimateTime : (problemCount : Nat) -> Nat
estimateTime count =
  let parseTime = 10  -- 파싱 10초
      extractTime = count * 1  -- 문제당 1초
      writeTime = count * 2  -- 파일당 2초
  in parseTime + extractTime + writeTime

||| 408개 문제 예상 시간
public export
estimated408Problems : Nat
estimated408Problems = estimateTime 408  -- 약 1234초 = 20분

||| 워크플로우 검증
|||
||| 모든 단계가 순차적으로 진행되는지 확인
public export
isValidTransition : WorkflowStage -> WorkflowStage -> Bool
isValidTransition Input Parse = True
isValidTransition Parse Extract = True
isValidTransition Extract Write = True
isValidTransition Write Complete = True
isValidTransition _ _ = False

||| 전체 단계 순서
public export
allStages : List WorkflowStage
allStages = [Input, Parse, Extract, Write, Complete]

||| 최종 성공 조건
|||
||| @ expected 예상 문제 개수 (408)
public export
isSuccessful : (expected : Nat) -> WorkflowState -> Bool
isSuccessful expected (Succeeded result) =
  result.totalProblems == expected &&
  result.successCount == expected &&
  result.failedCount == 0
isSuccessful _ _ = False

||| 상태 전이(의존 타입): 이 Step이 존재하는 전이만 합법
public export
data Step : WorkflowState -> WorkflowState -> Type where
  Start : Step NotStarted (Processing Input)
  ToParse : Step (Processing Input) (Processing Parse)
  ToExtract : Step (Processing Parse) (Processing Extract)
  ToWrite : Step (Processing Extract) (Processing Write)
  ToComplete : Step (Processing Write) (Processing Complete)
  Finish : (r : BatchWriteResult) -> Step (Processing Complete) (Succeeded r)
  FailAt : (s : WorkflowStage) -> (e : Error) -> Step (Processing s) (Failed s e)

||| 전체 파이프라인의 이상적 전이 시퀀스(타입으로 강제)
public export
pipelineTrace : (r : BatchWriteResult) -> Trace WorkflowState Step NotStarted (Succeeded r)
pipelineTrace r =
  Start :::
  ToParse :::
  ToExtract :::
  ToWrite :::
  ToComplete :::
  Finish r :::
  Done
