||| HwpAutomation V2 - Core 모듈 명세
|||
||| 목적: 모든 Automation이 공유하는 HWP API 래퍼
|||
||| 구조:
||| ```
||| core/
||| ├── __init__.py
||| ├── hwp_client.py      # HWP COM 클라이언트
||| ├── actions.py         # Action API 래퍼
||| ├── automation.py      # Automation API 래퍼
||| ├── types.py           # 공통 타입
||| └── utils.py           # 유틸리티
||| ```

module Core

%default total

||| 문서 상태 (HwpCommon에서 가져옴)
public export
data DocumentState : Type where
  ||| 문서 닫힘
  Closed : DocumentState
  ||| 문서 열림
  Opened : DocumentState
  ||| 문서 수정됨
  Modified : DocumentState
  ||| 문서 저장됨
  Saved : DocumentState

||| HWP 작업 결과
public export
data HwpResult : Type where
  ||| 성공
  Success : (content : String) -> HwpResult
  ||| 실패
  Failure : (error : String) -> HwpResult

||| Core 모듈의 구성 요소
public export
data CoreModule : Type where
  ||| HWP COM 클라이언트 (기본 연결)
  HwpClient : CoreModule

  ||| Action API 래퍼 (ActionTable 방식)
  ActionAPI : CoreModule

  ||| Automation API 래퍼 (OLE Object Model)
  AutomationAPI : CoreModule

  ||| 공통 타입 정의
  CommonTypes : CoreModule

  ||| 유틸리티 함수
  Utils : CoreModule

||| 모듈 파일명
public export
moduleFile : CoreModule -> String
moduleFile HwpClient = "hwp_client.py"
moduleFile ActionAPI = "actions.py"
moduleFile AutomationAPI = "automation.py"
moduleFile CommonTypes = "types.py"
moduleFile Utils = "utils.py"

||| 모듈 책임
public export
moduleResponsibility : CoreModule -> String
moduleResponsibility HwpClient = "pywin32 COM 연결 및 기본 제어"
moduleResponsibility ActionAPI = "HAction.Run() 기반 API"
moduleResponsibility AutomationAPI = "hwp.XHwpDocuments 기반 API"
moduleResponsibility CommonTypes = "DocumentState, HwpResult 등 공통 타입"
moduleResponsibility Utils = "동기화, 에러 처리 등 유틸리티"

||| HwpClient 기본 기능
public export
data HwpClientCapability : Type where
  ||| HWP 프로세스 시작/종료
  ProcessControl : HwpClientCapability

  ||| 문서 열기/닫기/저장
  DocumentControl : HwpClientCapability

  ||| 문서 상태 조회
  StateQuery : HwpClientCapability

  ||| 리소스 정리
  ResourceCleanup : HwpClientCapability

||| Action API 주요 기능
public export
data ActionAPICapability : Type where
  ||| Action 실행 (HAction.Run)
  RunAction : (actionId : String) -> ActionAPICapability

  ||| Action 파라미터 설정 (HAction.GetDefault)
  SetParameter : (actionId : String) -> ActionAPICapability

  ||| Action 결과 조회
  GetResult : ActionAPICapability

||| Automation API 주요 기능
public export
data AutomationAPICapability : Type where
  ||| 속성 조회 (hwp.속성)
  GetProperty : (path : String) -> AutomationAPICapability

  ||| 속성 설정 (hwp.속성 = 값)
  SetProperty : (path : String) -> AutomationAPICapability

  ||| 메서드 호출 (hwp.메서드())
  InvokeMethod : (path : String) -> AutomationAPICapability

||| Core API 인터페이스
||| 모든 Automation이 이 인터페이스를 통해 HWP 제어
public export
record CoreAPI where
  constructor MkCoreAPI
  ||| 문서 상태
  state : DocumentState

  ||| Action API 사용 가능 여부
  hasActionAPI : Bool

  ||| Automation API 사용 가능 여부
  hasAutomationAPI : Bool

  ||| 에러 처리 활성화
  errorHandling : Bool

||| Core API 생성
public export
createCoreAPI : CoreAPI
createCoreAPI = MkCoreAPI
  { state = Closed
  , hasActionAPI = True
  , hasAutomationAPI = True
  , errorHandling = True
  }

||| API 선택 전략
public export
data APIStrategy : Type where
  ||| Action API 우선 (간단한 작업)
  PreferAction : APIStrategy

  ||| Automation API 우선 (복잡한 작업)
  PreferAutomation : APIStrategy

  ||| 둘 다 사용 (하이브리드)
  Hybrid : APIStrategy

||| 작업 유형에 따른 권장 API
public export
recommendedAPI : String -> APIStrategy
recommendedAPI "simple_edit" = PreferAction
recommendedAPI "complex_merge" = PreferAutomation
recommendedAPI "mcp_server" = Hybrid
recommendedAPI _ = PreferAutomation
