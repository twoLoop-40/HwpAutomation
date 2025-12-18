module Specs.Consolidator.Workflow

import Specs.Consolidator.Types

%default total

-- 병렬 워크플로우 명세 (실행 계획 Blueprint)

||| 워크플로우 단계 (실행 전 계획)
public export
data WorkflowStep : Type where
  ScanSources : WorkflowStep                               -- 1. 소스 폴더 스캔
  CreateTarget : String -> WorkflowStep                    -- 2. 대상 폴더 생성 (경로)
  ProcessFiles : String -> Nat -> OperationMode -> WorkflowStep  -- 3. 파일 처리 (대상경로, 워커수, 모드)
  RemoveEmptyFolders : WorkflowStep                        -- 4. 빈 폴더 삭제 (MoveMode만)
  CollectStats : WorkflowStep                              -- 5. 통계 수집

||| 워크플로우 시퀀스 (순서 보장)
public export
Workflow : Type
Workflow = List WorkflowStep

||| 복사 워크플로우 (4단계)
public export
copyWorkflow : TargetFolder -> Nat -> Workflow
copyWorkflow target workers =
  [ ScanSources
  , CreateTarget (fullPath target)
  , ProcessFiles (fullPath target) workers CopyMode
  , CollectStats
  ]

||| 이동 워크플로우 (5단계)
public export
moveWorkflow : TargetFolder -> Nat -> Workflow
moveWorkflow target workers =
  [ ScanSources
  , CreateTarget (fullPath target)
  , ProcessFiles (fullPath target) workers MoveMode
  , RemoveEmptyFolders
  , CollectStats
  ]

||| 모드별 워크플로우 생성 (Blueprint)
public export
createWorkflow : Config -> Workflow
createWorkflow config =
  case config.mode of
    CopyMode => copyWorkflow config.target config.workers
    MoveMode => moveWorkflow config.target config.workers
