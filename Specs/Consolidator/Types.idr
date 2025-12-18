module Specs.Consolidator.Types

import Specs.Common.Result

%default total

-- Folder Consolidator 핵심 타입
-- 여러 폴더 → 하나의 폴더로 통합 (병렬)

||| 작업 모드
public export
data OperationMode = CopyMode | MoveMode

||| 파일 경로 정보
public export
record FilePath where
  constructor MkFilePath
  path : String
  size : Integer  -- 실제 파일 크기 (바이트)

||| 대상 폴더
|||
||| fullPath = parentPath + "/" + folderName
public export
record TargetFolder where
  constructor MkTarget
  parentPath : String
  folderName : String

||| 완전 경로 계산
public export
fullPath : TargetFolder -> String
fullPath t = t.parentPath ++ "/" ++ t.folderName

||| 작업 결과
public export
OpOutcome : (ok : Bool) -> Type
OpOutcome ok = Outcome ok String

||| (레거시) 작업 결과
||| 기존 명세/문서 호환을 위해 남겨두되, 신규 코드/명세에서는 OpOutcome를 사용
public export
data OpResult = Success String | Failed String

||| 작업 통계
public export
record OperationStats where
  constructor MkStats
  totalFiles : Nat
  successCount : Nat
  failedCount : Nat

||| 통계 유효성(의존 타입): totalFiles = successCount + failedCount 를 증명으로 강제
public export
record ValidOperationStats where
  constructor MkValidStats
  stats : OperationStats
  prf : stats.totalFiles = stats.successCount + stats.failedCount

||| 설정
public export
record Config where
  constructor MkConfig
  sources : List String      -- 소스 폴더 목록
  target : TargetFolder      -- 대상 폴더
  mode : OperationMode       -- 복사/이동
  workers : Nat              -- 병렬 워커 수 (기본 5)
