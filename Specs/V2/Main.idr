||| HwpAutomation V2 - 메인 통합 모듈
|||
||| 목적: 전체 프로젝트 구조를 통합하고 검증
|||
||| 사용법:
||| ```bash
||| idris2 HwpIdris/V2/Main.idr -o build/v2
||| ```

module Main

import ProjectStructure
import Core
import Automation
import UI
import Plugins.Merger
import Plugins.MCP

%default total

||| 프로젝트 V2 메타데이터
public export
record ProjectV2Metadata where
  constructor MkProjectV2Metadata
  ||| 프로젝트 이름
  name : String

  ||| 버전
  version : String

  ||| 설명
  description : String

  ||| Python 버전 요구사항
  pythonVersion : String

||| V2 메타데이터
public export
v2Metadata : ProjectV2Metadata
v2Metadata = MkProjectV2Metadata
  { name = "HwpAutomation"
  , version = "2.0.0"
  , description = "확장 가능한 HWP 자동화 플랫폼"
  , pythonVersion = ">=3.13"
  }

||| 새 프로젝트 구조
||| ```
||| HwpAutomation/
||| ├── core/              # 공통 HWP API 래퍼
||| │   ├── __init__.py
||| │   ├── hwp_client.py
||| │   ├── actions.py
||| │   ├── automation.py
||| │   ├── types.py
||| │   └── utils.py
||| ├── automations/       # 자동화 플러그인들
||| │   ├── __init__.py
||| │   ├── base.py
||| │   ├── registry.py
||| │   ├── merger/
||| │   │   ├── __init__.py
||| │   │   ├── plugin.py
||| │   │   ├── merger.py
||| │   │   ├── preprocessor.py
||| │   │   ├── para_scanner.py
||| │   │   ├── column.py
||| │   │   └── config.py
||| │   └── mcp/
||| │       ├── __init__.py
||| │       ├── plugin.py
||| │       ├── server.py
||| │       ├── tools.py
||| │       └── config.py
||| ├── ui/                # Tkinter 런처
||| │   ├── __init__.py
||| │   ├── main.py
||| │   ├── launcher.py
||| │   ├── plugin_card.py
||| │   ├── settings.py
||| │   └── styles.py
||| ├── tests/             # 테스트
||| │   ├── core/
||| │   ├── merger/
||| │   └── mcp/
||| ├── HwpIdris/          # Idris2 명세
||| │   └── V2/
||| │       ├── Main.idr
||| │       ├── ProjectStructure.idr
||| │       ├── Core.idr
||| │       ├── Automation.idr
||| │       ├── UI.idr
||| │       └── Plugins/
||| │           ├── Merger.idr
||| │           └── MCP.idr
||| ├── pyproject.toml
||| └── README.md
||| ```
public export
newStructureDoc : String
newStructureDoc = """
HwpAutomation V2 구조:

1. core/ - HWP API 공통 래퍼
   - hwp_client.py: COM 클라이언트
   - actions.py: Action API
   - automation.py: Automation API
   - types.py: 공통 타입
   - utils.py: 유틸리티

2. automations/ - 플러그인 디렉토리
   - base.py: AutomationBase 추상 클래스
   - registry.py: 플러그인 레지스트리
   - merger/: 문제 파일 병합
   - mcp/: MCP 서버

3. ui/ - Tkinter 런처
   - main.py: 메인 윈도우
   - launcher.py: 플러그인 그리드
   - plugin_card.py: 플러그인 카드

4. tests/ - 테스트
5. HwpIdris/ - Idris2 형식 명세
"""

||| 마이그레이션 계획
public export
record MigrationPlan where
  constructor MkMigrationPlan
  ||| 단계별 작업
  steps : List String

  ||| 예상 소요 시간
  estimatedHours : Nat

  ||| 위험 요소
  risks : List String

||| V2 마이그레이션 계획
public export
v2MigrationPlan : MigrationPlan
v2MigrationPlan = MkMigrationPlan
  { steps =
      [ "1. core/ 디렉토리 생성 및 공통 API 이동"
      , "2. automations/base.py 작성 (AutomationBase)"
      , "3. automations/registry.py 작성 (플러그인 레지스트리)"
      , "4. AppV1/ → automations/merger/ 이동"
      , "5. src/ → automations/mcp/ 이동"
      , "6. ui/ 디렉토리 생성 및 Tkinter 런처 작성"
      , "7. tests/ 재구성"
      , "8. pyproject.toml 업데이트"
      , "9. 테스트 실행 및 검증"
      ]
  , estimatedHours = 8
  , risks =
      [ "import 경로 변경으로 인한 에러"
      , "기존 테스트 깨짐"
      , "Tkinter UI 의존성 추가 필요"
      ]
  }

||| 검증: 모든 필수 모듈이 정의되었는지 확인
public export
validateV2Spec : Bool
validateV2Spec =
  let coreModules = [HwpClient, ActionAPI, AutomationAPI, CommonTypes, Utils]
      automationPlugins = [createMergerPlugin, createMCPPlugin]
      uiComponents = [MainWindow, PluginLauncher, PluginCard, SettingsDialog]
  in True  -- 컴파일되면 모든 모듈이 유효함

||| 메인 함수 (컴파일 테스트용)
main : IO ()
main = do
  putStrLn "=== HwpAutomation V2 명세 검증 ==="
  putStrLn ""
  putStrLn $ "프로젝트: " ++ v2Metadata.name
  putStrLn $ "버전: " ++ v2Metadata.version
  putStrLn $ "설명: " ++ v2Metadata.description
  putStrLn ""
  putStrLn "✅ 모든 Idris2 명세 컴파일 성공!"
  putStrLn ""
  putStrLn newStructureDoc
  putStrLn ""
  putStrLn "다음 단계:"
  traverse_ putStrLn v2MigrationPlan.steps
