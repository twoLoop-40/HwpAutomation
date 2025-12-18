module Specs.Converter.UI

import Specs.Converter.Types

%default total

-- HWP to PDF Converter UI 워크플로우
-- Tkinter 다이얼로그 기반

||| UI 상태
public export
data UIState : Type where
  Initial : UIState              -- 초기 상태
  FileSelecting : UIState        -- 파일 선택 중
  Confirming : UIState           -- 변환 확인 중
  Converting : UIState           -- 변환 진행 중
  ShowingResult : UIState        -- 결과 표시 중
  Closed : UIState               -- 종료

||| UI 이벤트
public export
data UIEvent : Type where
  OpenFileDialog : UIEvent       -- 파일 선택 다이얼로그 열기
  FilesSelected : List String -> UIEvent  -- 파일 선택됨
  UserConfirmed : UIEvent        -- 사용자 확인
  UserCancelled : UIEvent        -- 사용자 취소
  ConversionStarted : UIEvent    -- 변환 시작됨
  ConversionCompleted : List ConversionResult -> UIEvent  -- 변환 완료
  ResultAcknowledged : UIEvent   -- 결과 확인됨

||| UI 전환 규칙
|||
||| 상태 전환은 이벤트에 의해서만 발생
public export
transition : UIState -> UIEvent -> UIState
transition Initial OpenFileDialog = FileSelecting
transition FileSelecting (FilesSelected _) = Confirming
transition FileSelecting UserCancelled = Closed
transition Confirming UserConfirmed = Converting
transition Confirming UserCancelled = Closed
transition Converting (ConversionCompleted _) = ShowingResult
transition ShowingResult ResultAcknowledged = Closed
transition _ _ = Closed  -- 기타 모든 경우 종료

||| 파일 선택 다이얼로그 결과
public export
record FileDialogResult where
  constructor MkFileDialogResult
  files : List String       -- 선택된 파일 목록
  cancelled : Bool          -- 취소 여부

||| 파일이 선택되었음 (취소되지 않음)
public export
filesSelected : FileDialogResult -> Bool
filesSelected result = not result.cancelled && (length result.files > 0)

||| 확인 다이얼로그 결과
public export
data ConfirmResult : Type where
  Confirmed : ConfirmResult     -- 확인
  Cancelled : ConfirmResult     -- 취소

||| 진행 상황 다이얼로그
|||
||| @ title 다이얼로그 제목
||| @ message 표시할 메시지
||| @ fileCount 처리할 파일 개수
public export
record ProgressDialog where
  constructor MkProgressDialog
  title : String                -- "변환 중..."
  message : String              -- "PDF 변환 중..."
  fileCount : Nat               -- 처리할 파일 개수
  visible : Bool                -- 표시 여부

||| 결과 다이얼로그
|||
||| @ success 성공 여부 (모든 파일 성공 시 True)
||| @ successCount 성공한 파일 수
||| @ failCount 실패한 파일 수
||| @ failedFiles 실패한 파일 목록
public export
record ResultDialog where
  constructor MkResultDialog
  success : Bool
  successCount : Nat
  failCount : Nat
  failedFiles : List String

||| 완전 성공 여부 (실패 없음)
public export
allSuccess : ResultDialog -> Bool
allSuccess result = result.failCount == 0

||| UI 워크플로우
|||
||| 1. 파일 선택 다이얼로그
||| 2. 확인 메시지박스
||| 3. 진행 상황 다이얼로그 (모달)
||| 4. 병렬 변환 실행
||| 5. 결과 다이얼로그
public export
data UIWorkflow : UIState -> Type where
  ||| 1단계: 파일 선택 다이얼로그 열기
  OpenFileSelection : UIWorkflow Initial

  ||| 2단계: 파일 선택 결과 처리
  ProcessFileSelection : FileDialogResult -> UIWorkflow FileSelecting

  ||| 3단계: 확인 다이얼로그 표시
  ShowConfirmation : (fileCount : Nat) -> UIWorkflow Confirming

  ||| 4단계: 진행 상황 다이얼로그 생성 및 표시
  ShowProgress : (fileCount : Nat) -> UIWorkflow Converting

  ||| 5단계: 병렬 변환 실행
  ExecuteConversion : (files : List String) -> (maxWorkers : Nat) -> UIWorkflow Converting

  ||| 6단계: 진행 상황 다이얼로그 닫기
  CloseProgress : UIWorkflow Converting

  ||| 7단계: 결과 다이얼로그 표시
  ShowResult : ResultDialog -> UIWorkflow ShowingResult

  ||| 8단계: 종료
  Close : UIWorkflow Closed

||| 전체 UI 실행 시퀀스
|||
||| Initial → FileSelecting → Confirming → Converting → ShowingResult → Closed
public export
data UISequence : UIState -> UIState -> Type where
  ||| 단일 단계
  Step : UIWorkflow from -> UISequence from to

  ||| 연속 단계
  Then : UIWorkflow from -> UISequence mid to -> UISequence from to

||| 완전한 UI 워크플로우 (Initial → Closed)
|||
||| 예제:
||| completeWorkflow =
|||   OpenFileSelection `Then`
|||   ProcessFileSelection fileResult `Then`
|||   ShowConfirmation (length files) `Then`
|||   ShowProgress (length files) `Then`
|||   ExecuteConversion files 5 `Then`
|||   CloseProgress `Then`
|||   ShowResult resultDialog `Then`
|||   Step Close
public export
CompleteWorkflow : Type
CompleteWorkflow = UISequence Initial Closed

||| Tkinter 다이얼로그 명세
public export
record TkinterDialog where
  constructor MkDialog
  dialogType : String           -- "file", "messagebox", "toplevel"
  title : String
  message : String
  modal : Bool                  -- grab_set() 여부
  resizable : Bool

||| 파일 선택 다이얼로그 생성
public export
createFileDialog : TkinterDialog
createFileDialog = MkDialog
  "file"
  "변환할 HWP 파일 선택"
  ""
  False
  False

||| 확인 다이얼로그 생성
public export
createConfirmDialog : Nat -> TkinterDialog
createConfirmDialog n = MkDialog
  "messagebox"
  "변환 확인"
  (show n ++ "개 파일을 PDF로 변환하시겠습니까?")
  False
  False

||| 진행 상황 다이얼로그 생성
public export
createProgressDialog : Nat -> TkinterDialog
createProgressDialog n = MkDialog
  "toplevel"
  "변환 중..."
  ("PDF 변환 중...\n" ++ show n ++ "개 파일 처리 중 (병렬)")
  True   -- modal
  False  -- not resizable

||| 결과 다이얼로그 생성
public export
createResultDialog : ResultDialog -> TkinterDialog
createResultDialog result =
  if allSuccess result
    then MkDialog
      "messagebox"
      "완료"
      ("성공적으로 " ++ show result.successCount ++ "개 파일을 PDF로 변환했습니다.")
      False
      False
    else MkDialog
      "messagebox"
      "부분 완료"
      (show result.successCount ++ "개 성공, " ++ show result.failCount ++ "개 실패")
      False
      False

||| UI 실행 결과
public export
record UIResult where
  constructor MkUIResult
  completed : Bool              -- 완료 여부 (취소되지 않음)
  convertedCount : Nat          -- 변환된 파일 수
  failedCount : Nat             -- 실패한 파일 수
