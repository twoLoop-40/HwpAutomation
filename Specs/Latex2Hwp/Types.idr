module Latex2Hwp.Types

import Data.String

%default total

-- ============================================================
-- 1. Configuration & Basic Types
-- ============================================================

||| 윈도우 핸들 (타입 안전성을 위해 추상화)
public export
data WindowHandle = MkHandle Int

||| 자동화 도구 백엔드
public export
data AutomationBackend =
    ||| pywinauto 사용 (권장, 스크린샷 기반 구현)
    PyWinAuto

||| 변환기 설정
public export
record ConverterConfig where
  constructor MkConfig
  ||| 임시 파일 저장 경로 (예: "C:\\Temp\\eq.mml")
  tempFilePath : String
  ||| HWP 윈도우 제목 패턴
  hwpTitlePattern : String
  ||| 단계별 대기 시간 (초, 예: 0.1)
  stepDelay : Double
  ||| 키 입력 사이의 대기 시간
  typingDelay : Double

-- ============================================================
-- 2. Domain Data Types (LaTeX & MathML)
-- ============================================================

||| LaTeX 입력 소스
public export
data LatexSource
  = ||| LaTeX 문자열 직접 입력
    LatexRaw String
  | ||| LaTeX 파일 경로
    LatexFilePath String

||| MathML 데이터
public export
record MathML where
  constructor MkMathML
  ||| 변환된 MathML 원본 문자열
  content : String
  ||| 저장된 임시 파일 경로 (중요: HWP Import용)
  filepath : String

-- ============================================================
-- 3. Error Handling
-- ============================================================

||| 자동화 과정에서 발생할 수 있는 구체적인 에러들
public export
data HwpError : Type where
  ||| latex2mathml 변환 실패
  LatexToMmlError : String -> HwpError
  ||| 임시 파일 쓰기 실패
  FileWriteError : String -> HwpError
  ||| HWP 창을 찾을 수 없음
  WindowNotFound : String -> HwpError
  ||| 다이얼로그(파일열기 등) 찾기 실패
  DialogNotFound : String -> HwpError
  ||| 타임아웃 발생
  TimeoutError : String -> HwpError
  ||| 기타 시스템 에러
  SystemError : String -> HwpError

export
Show HwpError where
  show (LatexToMmlError msg) = "latex2mathml Error: " ++ msg
  show (FileWriteError path) = "Failed to write file: " ++ path
  show (WindowNotFound title) = "Window not found: " ++ title
  show (DialogNotFound title) = "Dialog not found: " ++ title
  show (TimeoutError stage) = "Timeout during: " ++ stage
  show (SystemError msg) = "System Error: " ++ msg

-- ============================================================
-- 4. State Machine Types (Reflecting Screenshot Workflow)
-- ============================================================

||| 변환 프로세스의 각 단계
public export
data ConversionState : Type where
  ||| 1. 초기 상태: LaTeX 소스 보유
  Idle : LatexSource -> ConversionState

  ||| 2. MathML 파일 생성 완료 (latex2mathml -> file save)
  MmlFileReady : MathML -> ConversionState

  ||| 3. 수식 편집기 열림 (수식 입력 상태)
  EditorOpen : (hwnd : WindowHandle) -> (mml : MathML) -> ConversionState

  ||| 4. 'MathML 불러오기' 다이얼로그 열림 (Alt-M)
  ImportDialogOpen : (editorHwnd : WindowHandle) -> (dialogHwnd : WindowHandle) -> (mml : MathML) -> ConversionState

  ||| 5. 파일 경로 입력 및 확인 완료
  FileSelected : (editorHwnd : WindowHandle) -> ConversionState

  ||| 6. 완료 (Shift-Esc로 닫음)
  Done : ConversionState

  ||| 실패 상태
  ErrorState : HwpError -> ConversionState

-- ============================================================
-- 5. State Transitions (Proof)
-- ============================================================

||| 유효한 상태 전이 증명
public export
data ValidTransition : ConversionState -> ConversionState -> Type where
  ||| LaTeX -> MathML 변환 및 파일 저장
  Step_GenMml : ValidTransition (Idle src) (MmlFileReady mml)

  ||| HWP에서 수식 편집기 열기 (Ctrl+N, M)
  Step_OpenEditor : ValidTransition (MmlFileReady mml) (EditorOpen hwnd mml)

  ||| 수식 편집기에서 불러오기 다이얼로그 열기 (Alt-M)
  Step_OpenImportDialog : ValidTransition (EditorOpen h mml) (ImportDialogOpen h d mml)

  ||| 다이얼로그에 경로 입력하고 확인 (Alt-O)
  Step_SelectFile : ValidTransition (ImportDialogOpen h d mml) (FileSelected h)

  ||| 수식 편집기 닫고 저장 (Shift-Esc)
  Step_CloseAndSave : ValidTransition (FileSelected h) Done

  ||| 에러 처리
  Step_Fail : {state : ConversionState} -> ValidTransition state (ErrorState err)

-- ============================================================
-- 6. Abstract Commands
-- ============================================================

||| 자동화 명령 (PyWinAuto 맵핑용)
public export
data AutomationCmd : Type where
  ||| Python 함수 호출: latex2mathml.converter.convert()
  PyConvertLatex : String -> AutomationCmd
  ||| 파일 쓰기
  WriteFile : String -> String -> AutomationCmd
  ||| 윈도우 찾기 및 연결 (connect)
  FindWindow : (title : String) -> AutomationCmd
  ||| 키 입력 전송 (send_keys)
  SendKeys : (targetWindow : String) -> (keys : String) -> AutomationCmd
  ||| 콤보박스 텍스트 설정 (긴 경로 입력 최적화)
  SetComboBoxText : (window : String) -> (text : String) -> AutomationCmd
  ||| 대기
  Sleep : (seconds : Double) -> AutomationCmd
