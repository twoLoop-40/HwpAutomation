||| HwpAutomation V2 - UI 모듈 명세
|||
||| 목적: Tkinter 기반 런처 UI
|||
||| 구조:
||| ```
||| ui/
||| ├── __init__.py
||| ├── main.py            # 메인 윈도우
||| ├── launcher.py        # 플러그인 런처
||| ├── plugin_card.py     # 플러그인 카드 위젯
||| ├── settings.py        # 설정 다이얼로그
||| └── styles.py          # UI 스타일
||| ```

module UI

import Automation

%default total

||| UI 컴포넌트
public export
data UIComponent : Type where
  ||| 메인 윈도우
  MainWindow : UIComponent

  ||| 플러그인 런처 (그리드 뷰)
  PluginLauncher : UIComponent

  ||| 플러그인 카드 (개별 항목)
  PluginCard : UIComponent

  ||| 설정 다이얼로그
  SettingsDialog : UIComponent

  ||| 로그 뷰어
  LogViewer : UIComponent

||| 메인 윈도우 레이아웃
public export
data MainWindowLayout : Type where
  ||| 헤더 (제목, 설정 버튼)
  Header : MainWindowLayout

  ||| 플러그인 그리드 (카드들)
  PluginGrid : MainWindowLayout

  ||| 푸터 (상태바)
  Footer : MainWindowLayout

||| 플러그인 카드 정보
public export
record PluginCardInfo where
  constructor MkPluginCardInfo
  ||| 플러그인 메타데이터
  plugin : AutomationPlugin

  ||| 아이콘 경로
  iconPath : String

  ||| 활성화 여부 (클릭 가능)
  enabled : Bool

  ||| 즐겨찾기 여부
  favorite : Bool

||| 카드 액션
public export
data CardAction : Type where
  ||| 플러그인 실행
  Launch : CardAction

  ||| 설정 열기
  OpenSettings : CardAction

  ||| 즐겨찾기 토글
  ToggleFavorite : CardAction

  ||| 상세 정보 보기
  ShowDetails : CardAction

||| UI 이벤트
public export
data UIEvent : Type where
  ||| 플러그인 선택
  PluginSelected : (pluginId : String) -> UIEvent

  ||| 플러그인 실행 요청
  LaunchRequested : (pluginId : String) -> UIEvent

  ||| 설정 변경
  SettingsChanged : UIEvent

  ||| 앱 종료
  AppExit : UIEvent

||| 플러그인 실행 모드
public export
data LaunchMode : Type where
  ||| 새 창에서 실행 (독립)
  NewWindow : LaunchMode

  ||| 메인 창에서 실행 (내장)
  Embedded : LaunchMode

  ||| 백그라운드 실행 (서비스)
  Background : LaunchMode

||| 플러그인 그리드 설정
public export
record GridConfig where
  constructor MkGridConfig
  ||| 열 개수
  columns : Nat

  ||| 카드 너비
  cardWidth : Nat

  ||| 카드 높이
  cardHeight : Nat

  ||| 여백
  padding : Nat

||| 기본 그리드 설정 (3x3)
public export
defaultGridConfig : GridConfig
defaultGridConfig = MkGridConfig
  { columns = 3
  , cardWidth = 200
  , cardHeight = 150
  , padding = 10
  }

||| UI 테마
public export
data Theme : Type where
  ||| 라이트 모드
  Light : Theme

  ||| 다크 모드
  Dark : Theme

  ||| 시스템 따라가기
  System : Theme

||| 테마 색상
public export
record ThemeColors where
  constructor MkThemeColors
  ||| 배경색
  background : String

  ||| 전경색 (텍스트)
  foreground : String

  ||| 강조색
  accent : String

  ||| 카드 배경
  cardBackground : String

||| 라이트 테마 색상
public export
lightColors : ThemeColors
lightColors = MkThemeColors
  { background = "#FFFFFF"
  , foreground = "#000000"
  , accent = "#007ACC"
  , cardBackground = "#F5F5F5"
  }

||| 다크 테마 색상
public export
darkColors : ThemeColors
darkColors = MkThemeColors
  { background = "#1E1E1E"
  , foreground = "#FFFFFF"
  , accent = "#007ACC"
  , cardBackground = "#2D2D2D"
  }

||| UI 상태
public export
record UIState where
  constructor MkUIState
  ||| 현재 테마
  theme : Theme

  ||| 선택된 플러그인
  selectedPlugin : Maybe String

  ||| 그리드 설정
  gridConfig : GridConfig

  ||| 즐겨찾기 목록
  favorites : List String

||| 초기 UI 상태
public export
initialUIState : UIState
initialUIState = MkUIState
  { theme = System
  , selectedPlugin = Nothing
  , gridConfig = defaultGridConfig
  , favorites = []
  }

||| 메인 윈도우 워크플로우
public export
data MainWindowWorkflow : Type where
  ||| 1. 앱 시작 → 플러그인 로드
  StartApp : MainWindowWorkflow

  ||| 2. 플러그인 표시 (그리드)
  DisplayPlugins : (registry : PluginRegistry) -> MainWindowWorkflow

  ||| 3. 사용자 선택 대기
  WaitUserInput : MainWindowWorkflow

  ||| 4. 플러그인 실행
  LaunchPlugin : (pluginId : String) -> (mode : LaunchMode) -> MainWindowWorkflow

  ||| 5. 결과 표시 또는 종료
  ShowResult : (result : String) -> MainWindowWorkflow

||| UI 컴포넌트 파일
public export
componentFile : UIComponent -> String
componentFile MainWindow = "main.py"
componentFile PluginLauncher = "launcher.py"
componentFile PluginCard = "plugin_card.py"
componentFile SettingsDialog = "settings.py"
componentFile LogViewer = "log_viewer.py"

||| Tkinter 위젯 매핑
public export
data TkWidget : UIComponent -> Type where
  ||| MainWindow → tk.Tk
  TkRoot : TkWidget MainWindow

  ||| PluginLauncher → tk.Frame
  TkFrame : TkWidget PluginLauncher

  ||| PluginCard → tk.Frame + tk.Button
  TkCard : TkWidget PluginCard

  ||| SettingsDialog → tk.Toplevel
  TkDialog : TkWidget SettingsDialog

||| 플러그인 카드 렌더링 정보
public export
record CardRenderInfo where
  constructor MkCardRenderInfo
  ||| 카드 제목
  title : String

  ||| 카드 설명 (짧게)
  shortDesc : String

  ||| 아이콘 이미지
  icon : String

  ||| 상태 텍스트 (활성/비활성)
  statusText : String

  ||| 버튼 텍스트
  buttonText : String

||| 플러그인 메타데이터 → 카드 렌더링 정보
public export
toCardRenderInfo : PluginMetadata -> CardRenderInfo
toCardRenderInfo meta = MkCardRenderInfo
  { title = meta.name
  , shortDesc = meta.description
  , icon = "icons/" ++ meta.id ++ ".png"
  , statusText = "v" ++ meta.version
  , buttonText = "실행"
  }
