||| Automation API 상태 조회 형식 명세
|||
||| EventHandler 대안: 이벤트 폴링 대신 상태 조회 기반 변경 감지
|||
||| 참조:
|||   - HwpBooks/HwpAutomation_2504.pdf (OLE Object Model)
|||   - HwpBooks/한글오토메이션EventHandler추가_2504.pdf (이벤트 참조)
|||   - Specs/AutomationMCP.idr (기본 Automation 타입)

module Specs.AutomationState

import public Specs.HwpCommon
import Specs.Common.Result

%default total

--------------------------------------------------------------------------------
-- 문서 상태 속성
--------------------------------------------------------------------------------

||| 편집 모드 (EditMode 속성)
public export
data EditMode
  = ReadOnly      -- 읽기 전용
  | Editable      -- 편집 가능
  | Locked        -- 잠김 (다른 사용자가 편집 중)

export
Eq EditMode where
  ReadOnly == ReadOnly = True
  Editable == Editable = True
  Locked == Locked = True
  _ == _ = False

export
Show EditMode where
  show ReadOnly = "ReadOnly"
  show Editable = "Editable"
  show Locked = "Locked"

||| 문서 수정 여부 (IsModified 속성)
public export
data ModificationStatus
  = Unmodified    -- 수정되지 않음
  | Modified      -- 수정됨 (저장 필요)

export
Eq ModificationStatus where
  Unmodified == Unmodified = True
  Modified == Modified = True
  _ == _ = False

export
Show ModificationStatus where
  show Unmodified = "Unmodified"
  show Modified = "Modified"

||| 문서 경로 정보 (Path 속성)
public export
record DocumentPath where
  constructor MkDocumentPath
  hasPath : Bool         -- 경로 존재 여부
  path : String          -- 파일 경로 (hasPath = True일 때만 유효)

export
Eq DocumentPath where
  (MkDocumentPath h1 p1) == (MkDocumentPath h2 p2) = h1 == h2 && p1 == p2

export
Show DocumentPath where
  show (MkDocumentPath False _) = "No path (new document)"
  show (MkDocumentPath True p) = "Path: " ++ p

--------------------------------------------------------------------------------
-- 문서 상태 스냅샷 (State Snapshot)
--------------------------------------------------------------------------------

||| 문서의 현재 상태 스냅샷
|||
||| EventHandler 이벤트를 대체하는 상태 조회 결과
||| 이전 스냅샷과 비교하여 변경 감지 가능
public export
record DocumentStateSnapshot where
  constructor MkSnapshot
  isModified : ModificationStatus   -- 수정 여부
  documentPath : DocumentPath       -- 문서 경로
  editMode : EditMode               -- 편집 모드
  documentCount : Nat               -- 열린 문서 개수

export
Show DocumentStateSnapshot where
  show (MkSnapshot mod path mode count) =
    "DocumentSnapshot:\n" ++
    "  Modified: " ++ show mod ++ "\n" ++
    "  Path: " ++ show path ++ "\n" ++
    "  EditMode: " ++ show mode ++ "\n" ++
    "  DocumentCount: " ++ show count

--------------------------------------------------------------------------------
-- 상태 변경 감지 (Change Detection)
--------------------------------------------------------------------------------

||| 상태 변경 유형
public export
data StateChange
  = NoChange                                -- 변경 없음
  | ModificationChanged ModificationStatus  -- 수정 상태 변경
  | PathChanged DocumentPath                -- 경로 변경 (저장/다른 이름으로 저장)
  | EditModeChanged EditMode                -- 편집 모드 변경
  | DocumentCountChanged Nat                -- 문서 개수 변경 (열기/닫기)

export
Show StateChange where
  show NoChange = "No change"
  show (ModificationChanged s) = "Modification changed to: " ++ show s
  show (PathChanged p) = "Path changed to: " ++ show p
  show (EditModeChanged m) = "EditMode changed to: " ++ show m
  show (DocumentCountChanged n) = "DocumentCount changed to: " ++ show n

||| 두 스냅샷 비교하여 변경 감지
export
detectChanges : DocumentStateSnapshot -> DocumentStateSnapshot -> List StateChange
detectChanges old new =
  let changes : List StateChange = []
      changes = if old.isModified /= new.isModified
                then ModificationChanged new.isModified :: changes
                else changes
      changes = if old.documentPath /= new.documentPath
                then PathChanged new.documentPath :: changes
                else changes
      changes = if old.editMode /= new.editMode
                then EditModeChanged new.editMode :: changes
                else changes
      changes = if old.documentCount /= new.documentCount
                then DocumentCountChanged new.documentCount :: changes
                else changes
  in if null changes then [NoChange] else changes

--------------------------------------------------------------------------------
-- EventHandler 이벤트 매핑 (참조용)
--------------------------------------------------------------------------------

||| EventHandler 이벤트와 상태 조회의 매핑 관계
|||
||| 이 타입은 구현되지 않고 문서화 목적으로만 사용됨
||| 실제 이벤트 핸들러는 C++ ATL로만 구현 가능
public export
data EventHandlerEvent
  = Quit                    -- 한글 종료
  | CreateXHwpWindow        -- 창 생성
  | CloseXHwpWindow         -- 창 닫기
  | NewDocument             -- 새 문서 생성
  | DocumentBeforeOpen      -- 문서 열기 전
  | DocumentAfterOpen       -- 문서 열기 후
  | DocumentBeforeClose     -- 문서 닫기 전
  | DocumentAfterClose      -- 문서 닫기 후
  | DocumentBeforeSave      -- 문서 저장 전
  | DocumentAfterSave       -- 문서 저장 후
  | DocumentChange          -- 문서 변경

export
Show EventHandlerEvent where
  show Quit = "Quit"
  show CreateXHwpWindow = "CreateXHwpWindow"
  show CloseXHwpWindow = "CloseXHwpWindow"
  show NewDocument = "NewDocument"
  show DocumentBeforeOpen = "DocumentBeforeOpen"
  show DocumentAfterOpen = "DocumentAfterOpen"
  show DocumentBeforeClose = "DocumentBeforeClose"
  show DocumentAfterClose = "DocumentAfterClose"
  show DocumentBeforeSave = "DocumentBeforeSave"
  show DocumentAfterSave = "DocumentAfterSave"
  show DocumentChange = "DocumentChange"

||| EventHandler 이벤트를 상태 변경으로 근사 (Approximation)
|||
||| Before 이벤트는 감지 불가 (상태 조회의 한계)
export
eventToStateChange : EventHandlerEvent -> Maybe StateChange
eventToStateChange DocumentChange = Just (ModificationChanged Modified)
eventToStateChange DocumentAfterSave = Just (ModificationChanged Unmodified)
eventToStateChange DocumentAfterOpen = Just (DocumentCountChanged 1)  -- 예시
eventToStateChange DocumentAfterClose = Just (DocumentCountChanged 0) -- 예시
eventToStateChange _ = Nothing  -- Before 이벤트는 상태 조회로 감지 불가

--------------------------------------------------------------------------------
-- MCP 도구 정의
--------------------------------------------------------------------------------

||| Automation 상태 조회 도구 타입
public export
data AutomationStateTool
  = IsDocumentModified     -- hwp_auto_is_document_modified
  | GetDocumentPath        -- hwp_auto_get_document_path
  | GetEditMode            -- hwp_auto_get_edit_mode
  | GetDocumentCount       -- hwp_auto_get_document_count
  | GetStateSnapshot       -- hwp_auto_get_state_snapshot (통합 조회)

export
Show AutomationStateTool where
  show IsDocumentModified = "hwp_auto_is_document_modified"
  show GetDocumentPath = "hwp_auto_get_document_path"
  show GetEditMode = "hwp_auto_get_edit_mode"
  show GetDocumentCount = "hwp_auto_get_document_count"
  show GetStateSnapshot = "hwp_auto_get_state_snapshot"

||| 상태 조회 결과 타입
public export
data StateQueryResult : AutomationStateTool -> Type where
  IsModifiedResult : ModificationStatus -> StateQueryResult IsDocumentModified
  PathResult : DocumentPath -> StateQueryResult GetDocumentPath
  EditModeResult : EditMode -> StateQueryResult GetEditMode
  CountResult : Nat -> StateQueryResult GetDocumentCount
  SnapshotResult : DocumentStateSnapshot -> StateQueryResult GetStateSnapshot

--------------------------------------------------------------------------------
-- 검증 규칙
--------------------------------------------------------------------------------

||| 상태 조회는 문서가 열려있을 때만 유효
export
requiresOpenDocument : AutomationStateTool -> Bool
requiresOpenDocument IsDocumentModified = True
requiresOpenDocument GetDocumentPath = True
requiresOpenDocument GetEditMode = True
requiresOpenDocument GetDocumentCount = False  -- 문서 개수는 항상 조회 가능
requiresOpenDocument GetStateSnapshot = False  -- 스냅샷도 항상 가능 (count=0일 수 있음)

||| 상태 조회 실행 검증
export
validateStateQuery : AutomationStateTool -> DocumentState -> Either Error ()
validateStateQuery tool state =
  if requiresOpenDocument tool && state == Closed
    then Left (MkError InvalidInput ("Error: " ++ show tool ++ " requires an open document"))
    else Right ()

||| Outcome 버전(의존 타입): 성공 시 ()가 반드시 존재, 실패 시 Error가 반드시 존재
public export
validateStateQueryOutcome : AutomationStateTool -> DocumentState -> (ok ** Outcome ok ())
validateStateQueryOutcome tool state = fromEither (validateStateQuery tool state)
