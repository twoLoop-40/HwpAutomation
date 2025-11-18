||| HwpAutomation V2 - Automation 플러그인 명세
|||
||| 목적: 각 자동화 작업을 독립적인 플러그인으로 정의
|||
||| 구조:
||| ```
||| automations/
||| ├── __init__.py
||| ├── base.py            # AutomationBase 추상 클래스
||| ├── registry.py        # 플러그인 레지스트리
||| ├── merger/            # 문제 파일 병합 (기존 AppV1)
||| │   ├── __init__.py
||| │   ├── plugin.py      # MergerPlugin
||| │   ├── merger.py
||| │   ├── preprocessor.py
||| │   └── config.py
||| └── mcp/               # MCP 서버 (기존 src)
|||     ├── __init__.py
|||     ├── plugin.py      # MCPPlugin
|||     ├── server.py
|||     └── tools.py
||| ```

module Automation

import Core

%default total

||| Automation 플러그인 타입
public export
data AutomationType : Type where
  ||| 문제 파일 병합 (기존 AppV1)
  ProblemMerger : AutomationType

  ||| MCP 서버 (기존 src)
  MCPServer : AutomationType

  ||| 향후 추가: 표 자동 생성
  TableGenerator : AutomationType

  ||| 향후 추가: 문서 변환
  DocumentConverter : AutomationType

  ||| 향후 추가: 일괄 서식 적용
  BatchFormatter : AutomationType

||| 플러그인 메타데이터
public export
record PluginMetadata where
  constructor MkPluginMetadata
  ||| 플러그인 ID (고유)
  id : String

  ||| 표시 이름
  name : String

  ||| 설명
  description : String

  ||| 버전
  version : String

  ||| 작성자
  author : String

||| 플러그인 상태
public export
data PluginState : Type where
  ||| 비활성 (로드 안됨)
  Inactive : PluginState

  ||| 활성 (실행 가능)
  Active : PluginState

  ||| 실행 중
  Running : PluginState

  ||| 오류
  Error : String -> PluginState

||| Automation 플러그인 인터페이스
||| 모든 플러그인이 이 인터페이스를 구현해야 함
public export
record AutomationPlugin where
  constructor MkAutomationPlugin
  ||| 메타데이터
  metadata : PluginMetadata

  ||| 현재 상태
  state : PluginState

  ||| Core API 의존성
  requiresCoreAPI : Bool

  ||| UI에서 실행 가능 여부
  hasUI : Bool

  ||| CLI에서 실행 가능 여부
  hasCLI : Bool

||| ProblemMerger 플러그인 메타데이터
public export
mergerMetadata : PluginMetadata
mergerMetadata = MkPluginMetadata
  { id = "problem_merger"
  , name = "문제 파일 병합"
  , description = "HWP 문제 파일들을 2단 편집 양식으로 병합"
  , version = "1.0.0"
  , author = "HwpAutomation Team"
  }

||| MCPServer 플러그인 메타데이터
public export
mcpMetadata : PluginMetadata
mcpMetadata = MkPluginMetadata
  { id = "mcp_server"
  , name = "MCP 서버"
  , description = "Claude Desktop 통합을 위한 MCP 서버"
  , version = "1.0.0"
  , author = "HwpAutomation Team"
  }

||| 플러그인 생성 헬퍼
public export
createMergerPlugin : AutomationPlugin
createMergerPlugin = MkAutomationPlugin
  { metadata = mergerMetadata
  , state = Inactive
  , requiresCoreAPI = True
  , hasUI = True
  , hasCLI = True
  }

public export
createMCPPlugin : AutomationPlugin
createMCPPlugin = MkAutomationPlugin
  { metadata = mcpMetadata
  , state = Inactive
  , requiresCoreAPI = True
  , hasUI = False
  , hasCLI = True
  }

||| 플러그인 디렉토리 구조
public export
data PluginDirectory : AutomationType -> Type where
  ||| merger/ 디렉토리
  MergerDir : PluginDirectory ProblemMerger

  ||| mcp/ 디렉토리
  MCPDir : PluginDirectory MCPServer

||| 플러그인 필수 파일
public export
data PluginFile : Type where
  ||| __init__.py
  InitFile : PluginFile

  ||| plugin.py (플러그인 메인 클래스)
  MainFile : PluginFile

  ||| config.py (설정)
  ConfigFile : PluginFile

  ||| requirements.txt (의존성)
  RequirementsFile : PluginFile

||| ProblemMerger 전용 파일
public export
data MergerFile : Type where
  ||| merger.py (메인 병합 로직)
  MergerLogic : MergerFile

  ||| preprocessor.py (전처리)
  Preprocessor : MergerFile

  ||| para_scanner.py
  ParaScanner : MergerFile

  ||| column.py
  ColumnSetup : MergerFile

||| MCP 전용 파일
public export
data MCPFile : Type where
  ||| server.py (MCP 서버)
  ServerMain : MCPFile

  ||| tools.py (MCP 도구)
  ToolsDefinition : MCPFile

||| 플러그인 설정
public export
record PluginConfig where
  constructor MkPluginConfig
  ||| 활성화 여부
  enabled : Bool

  ||| 설정 파일 경로
  configPath : String

  ||| 로그 레벨
  logLevel : String

||| 플러그인 레지스트리
||| UI에서 플러그인 목록을 표시하기 위해 사용
public export
data PluginRegistry : Type where
  ||| 빈 레지스트리
  EmptyRegistry : PluginRegistry

  ||| 플러그인 등록
  RegisterPlugin :
    (plugin : AutomationPlugin) ->
    (rest : PluginRegistry) ->
    PluginRegistry

||| 레지스트리 크기
public export
registrySize : PluginRegistry -> Nat
registrySize EmptyRegistry = 0
registrySize (RegisterPlugin _ rest) = 1 + registrySize rest

||| 플러그인 검색
public export
findPlugin : String -> PluginRegistry -> Maybe AutomationPlugin
findPlugin _ EmptyRegistry = Nothing
findPlugin id (RegisterPlugin p rest) =
  if p.metadata.id == id
    then Just p
    else findPlugin id rest

||| 초기 레지스트리 (Merger + MCP)
public export
initialRegistry : PluginRegistry
initialRegistry =
  RegisterPlugin createMergerPlugin $
  RegisterPlugin createMCPPlugin $
  EmptyRegistry
