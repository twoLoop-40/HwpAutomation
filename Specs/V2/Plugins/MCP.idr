||| HwpAutomation V2 - MCP 플러그인 명세
|||
||| 목적: Claude Desktop 연동을 위한 MCP 서버 플러그인 (기존 src)
|||
||| 구조:
||| ```
||| automations/mcp/
||| ├── __init__.py
||| ├── plugin.py          # MCPPlugin 클래스
||| ├── server.py          # MCP 서버
||| ├── tools.py           # MCP 도구 정의
||| └── config.py          # 설정
||| ```

module Plugins.MCP

import Core
import Automation

%default total

||| MCP 플러그인 모듈
public export
data MCPModule : Type where
  ||| 플러그인 메인 클래스
  PluginMain : MCPModule

  ||| MCP 서버
  ServerMain : MCPModule

  ||| MCP 도구 정의
  ToolsDefinition : MCPModule

  ||| 설정 관리
  ConfigManager : MCPModule

||| 모듈 파일명
public export
mcpModuleFile : MCPModule -> String
mcpModuleFile PluginMain = "plugin.py"
mcpModuleFile ServerMain = "server.py"
mcpModuleFile ToolsDefinition = "tools.py"
mcpModuleFile ConfigManager = "config.py"

||| MCP 서버 상태
public export
data MCPServerState : Type where
  ||| 중지됨
  Stopped : MCPServerState

  ||| 시작 중
  Starting : MCPServerState

  ||| 실행 중
  Running : (port : Nat) -> MCPServerState

  ||| 에러
  Error : (message : String) -> MCPServerState

||| MCP 도구 카테고리
public export
data ToolCategory : Type where
  ||| 문서 관리 (열기, 닫기, 저장)
  DocumentManagement : ToolCategory

  ||| 편집 (텍스트 삽입, 표 생성)
  Editing : ToolCategory

  ||| 서식 (글꼴, 단락)
  Formatting : ToolCategory

  ||| 페이지 설정
  PageSetup : ToolCategory

  ||| 자동화 (병합, 변환)
  Automation : ToolCategory

||| MCP 도구 정의
public export
record MCPTool where
  constructor MkMCPTool
  name : String  -- 도구 이름
  description : String  -- 설명
  category : ToolCategory  -- 카테고리
  paramSchema : String  -- 파라미터 스키마
  handler : String  -- 핸들러 함수명

||| 기본 MCP 도구들
public export
data DefaultTool : Type where
  ||| hwp_create_document
  CreateDocument : DefaultTool

  ||| hwp_open_document
  OpenDocument : DefaultTool

  ||| hwp_close_document
  CloseDocument : DefaultTool

  ||| hwp_save_document
  SaveDocument : DefaultTool

  ||| hwp_insert_text
  InsertText : DefaultTool

  ||| hwp_create_table
  CreateTable : DefaultTool

  ||| hwp_get_state
  GetState : DefaultTool

||| 도구 메타데이터
public export
toolMetadata : DefaultTool -> MCPTool
toolMetadata CreateDocument = MkMCPTool
  { name = "hwp_create_document"
  , description = "새 HWP 문서 생성"
  , category = DocumentManagement
  , paramSchema = "{}"
  , handler = "handle_create_document"
  }
toolMetadata OpenDocument = MkMCPTool
  { name = "hwp_open_document"
  , description = "HWP 문서 열기"
  , category = DocumentManagement
  , paramSchema = "{\"path\": {\"type\": \"string\"}}"
  , handler = "handle_open_document"
  }
toolMetadata CloseDocument = MkMCPTool
  { name = "hwp_close_document"
  , description = "현재 문서 닫기"
  , category = DocumentManagement
  , paramSchema = "{}"
  , handler = "handle_close_document"
  }
toolMetadata SaveDocument = MkMCPTool
  { name = "hwp_save_document"
  , description = "문서 저장"
  , category = DocumentManagement
  , paramSchema = "{}"
  , handler = "handle_save_document"
  }
toolMetadata InsertText = MkMCPTool
  { name = "hwp_insert_text"
  , description = "텍스트 삽입"
  , category = Editing
  , paramSchema = "{\"text\": {\"type\": \"string\"}}"
  , handler = "handle_insert_text"
  }
toolMetadata CreateTable = MkMCPTool
  { name = "hwp_create_table"
  , description = "표 생성"
  , category = Editing
  , paramSchema = "{\"rows\": {\"type\": \"integer\"}, \"cols\": {\"type\": \"integer\"}}"
  , handler = "handle_create_table"
  }
toolMetadata GetState = MkMCPTool
  { name = "hwp_get_state"
  , description = "문서 상태 조회"
  , category = DocumentManagement
  , paramSchema = "{}"
  , handler = "handle_get_state"
  }

||| MCP 설정
public export
record MCPConfig where
  constructor MkMCPConfig
  ||| 서버 포트 (사용 안함, stdio만)
  port : Nat

  ||| Transport 방식 (stdio)
  transport : String

  ||| 활성화된 도구 목록
  enabledTools : List String

  ||| 로그 레벨
  logLevel : String

  ||| Claude Desktop 설정 경로
  claudeConfigPath : String

||| 기본 MCP 설정
public export
defaultMCPConfig : MCPConfig
defaultMCPConfig = MkMCPConfig
  { port = 0  -- stdio 사용
  , transport = "stdio"
  , enabledTools = ["hwp_create_document", "hwp_open_document", "hwp_close_document",
                    "hwp_save_document", "hwp_insert_text", "hwp_create_table", "hwp_get_state"]
  , logLevel = "INFO"
  , claudeConfigPath = "%APPDATA%\\Claude\\claude_desktop_config.json"
  }

||| MCP 플러그인 상태
public export
data MCPPluginState : Type where
  ||| 대기 중
  PluginIdle : MCPPluginState

  ||| 서버 시작 중
  PluginStarting : MCPPluginState

  ||| 서버 실행 중
  PluginRunning : (config : MCPConfig) -> MCPPluginState

  ||| 서버 중지 중
  PluginStopping : MCPPluginState

  ||| 에러
  PluginError : (message : String) -> MCPPluginState

||| MCP 이벤트
public export
data MCPEvent : Type where
  ||| 클라이언트 연결됨
  ClientConnected : MCPEvent

  ||| 클라이언트 연결 해제됨
  ClientDisconnected : MCPEvent

  ||| 도구 호출됨
  ToolInvoked : (toolName : String) -> MCPEvent

  ||| 에러 발생
  ErrorOccurred : (error : String) -> MCPEvent

||| MCP 서버 워크플로우
public export
data MCPServerWorkflow : Type where
  ||| 1. 설정 로드
  LoadConfig : MCPServerWorkflow

  ||| 2. Core API 초기화
  InitializeCoreAPI : MCPServerWorkflow

  ||| 3. 도구 등록
  RegisterTools : MCPServerWorkflow

  ||| 4. 서버 시작 (stdio)
  StartServer : MCPServerWorkflow

  ||| 5. 이벤트 루프
  EventLoop : MCPServerWorkflow

  ||| 6. 서버 종료
  Shutdown : MCPServerWorkflow

||| 도구 호출 결과
public export
data ToolResult : Type where
  ||| 성공
  Success : (content : String) -> ToolResult

  ||| 실패
  Failure : (error : String) -> ToolResult

||| Claude Desktop 설정 생성
public export
record ClaudeDesktopConfig where
  constructor MkClaudeDesktopConfig
  ||| 서버 이름
  serverName : String

  ||| uv 커맨드 경로
  uvCommand : String

  ||| 프로젝트 디렉토리
  projectDir : String

  ||| Python 모듈 경로
  modulePath : String

||| 기본 Claude Desktop 설정
public export
defaultClaudeConfig : ClaudeDesktopConfig
defaultClaudeConfig = MkClaudeDesktopConfig
  { serverName = "hwp"
  , uvCommand = "uv"
  , projectDir = "C:\\\\Users\\\\YourName\\\\Projects\\\\HwpAutomation"
  , modulePath = "automations.mcp.server"
  }

||| Claude Desktop 설정 JSON 생성
public export
generateClaudeConfigJSON : ClaudeDesktopConfig -> String
generateClaudeConfigJSON config =
  "{\n" ++
  "  \"mcpServers\": {\n" ++
  "    \"" ++ config.serverName ++ "\": {\n" ++
  "      \"command\": \"" ++ config.uvCommand ++ "\",\n" ++
  "      \"args\": [\n" ++
  "        \"--directory\",\n" ++
  "        \"" ++ config.projectDir ++ "\",\n" ++
  "        \"run\",\n" ++
  "        \"python\",\n" ++
  "        \"-m\",\n" ++
  "        \"" ++ config.modulePath ++ "\"\n" ++
  "      ]\n" ++
  "    }\n" ++
  "  }\n" ++
  "}"
