||| HwpAutomation V2 - 확장 가능한 프로젝트 구조
|||
||| 목적: 다양한 HWP 자동화 작업을 플러그인 방식으로 추가 가능하도록 설계
|||
||| 구조:
||| ```
||| HwpAutomation/
||| ├── core/              # 공통 HWP API 래퍼
||| ├── automations/       # 자동화 작업들 (플러그인)
||| │   ├── merger/        # 문제 파일 병합 (기존 AppV1)
||| │   ├── mcp/           # MCP 서버 (기존 src)
||| │   └── [future]/      # 향후 추가 작업들
||| ├── ui/                # Tkinter 메인 UI (런처)
||| └── tests/             # 테스트
||| ```

module ProjectStructure

%default total

||| 프로젝트의 주요 구성 요소
public export
data ProjectComponent : Type where
  ||| 핵심 HWP API 래퍼 및 유틸리티
  CoreModule : ProjectComponent

  ||| 자동화 작업 플러그인
  AutomationPlugin : ProjectComponent

  ||| UI 런처
  UILauncher : ProjectComponent

  ||| 테스트 스위트
  TestSuite : ProjectComponent

||| 디렉토리 구조
public export
data DirectoryStructure : Type where
  ||| core/ - HWP API 공통 래퍼
  CoreDir : DirectoryStructure

  ||| automations/ - 플러그인 디렉토리
  AutomationsDir : DirectoryStructure

  ||| ui/ - Tkinter UI
  UIDir : DirectoryStructure

  ||| tests/ - 테스트
  TestsDir : DirectoryStructure

||| 디렉토리 경로 매핑
public export
dirPath : DirectoryStructure -> String
dirPath CoreDir = "core/"
dirPath AutomationsDir = "automations/"
dirPath UIDir = "ui/"
dirPath TestsDir = "tests/"

||| 디렉토리 설명
public export
dirDescription : DirectoryStructure -> String
dirDescription CoreDir = "HWP API 공통 래퍼 (pywin32 기반)"
dirDescription AutomationsDir = "자동화 작업 플러그인들"
dirDescription UIDir = "Tkinter 메인 UI (런처)"
dirDescription TestsDir = "통합 테스트 스위트"

||| 마이그레이션 매핑 (기존 → 새 구조)
public export
data MigrationMapping : Type where
  ||| AppV1/ → automations/merger/
  MergerMigration : MigrationMapping

  ||| src/ → automations/mcp/
  MCPMigration : MigrationMapping

  ||| src/automation/ + src/common/ → core/
  CoreMigration : MigrationMapping

  ||| Tests/AppV1/ → tests/merger/
  MergerTestMigration : MigrationMapping

||| 마이그레이션 소스 경로
public export
migrationSource : MigrationMapping -> String
migrationSource MergerMigration = "AppV1/"
migrationSource MCPMigration = "src/"
migrationSource CoreMigration = "src/automation/ + src/common/"
migrationSource MergerTestMigration = "Tests/AppV1/"

||| 마이그레이션 대상 경로
public export
migrationTarget : MigrationMapping -> String
migrationTarget MergerMigration = "automations/merger/"
migrationTarget MCPMigration = "automations/mcp/"
migrationTarget CoreMigration = "core/"
migrationTarget MergerTestMigration = "tests/merger/"

||| 프로젝트 구조 검증
||| 모든 필수 디렉토리가 존재해야 함
public export
data ProjectValid : Type where
  ValidProject :
    (coreExists : Bool) ->
    (automationsExists : Bool) ->
    (uiExists : Bool) ->
    (testsExists : Bool) ->
    {auto prf : coreExists = True} ->
    {auto prf2 : automationsExists = True} ->
    {auto prf3 : uiExists = True} ->
    {auto prf4 : testsExists = True} ->
    ProjectValid
