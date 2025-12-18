||| HwpAutomation - Tkinter → PyQt5 UI 이전 명세 (의존 타입 기반)
|||
||| 목표:
||| - 위젯 매핑(Tk -> Qt)을 타입으로 강제
||| - 리스트 인덱스 이벤트를 Fin n 으로 안전화
||| - 다이얼로그 설정(필터/모드) 제약을 타입으로 표현
|||
||| 이 파일은 "명세"이며, 실제 구현은 Python(ui/main_pyqt.py 등)에서 수행됨.
module Specs.UI.PyQtMigration

import Data.Fin
import Data.Vect
import Data.List
import Data.String

%default total

--------------------------------------------------------------------------------
-- 1. Tkinter → PyQt5 위젯 매핑 (의존 타입)
--------------------------------------------------------------------------------

||| Tkinter 위젯
public export
data TkWidget : Type where
  TkRoot : TkWidget
  TkFrame : TkWidget
  TkLabel : TkWidget
  TkButton : TkWidget
  TkListbox : TkWidget
  TkEntry : TkWidget
  TkText : TkWidget
  TkScrollbar : TkWidget
  TkToplevel : TkWidget
  TkMessageBox : TkWidget

||| PyQt5 위젯
public export
data PyQtWidget : Type where
  QMainWindow : PyQtWidget
  QWidget : PyQtWidget
  QLabel : PyQtWidget
  QPushButton : PyQtWidget
  QListWidget : PyQtWidget
  QLineEdit : PyQtWidget
  QTextEdit : PyQtWidget
  QScrollArea : PyQtWidget
  QDialog : PyQtWidget
  QMessageBox : PyQtWidget
  QFileDialog : PyQtWidget
  QVBoxLayout : PyQtWidget
  QHBoxLayout : PyQtWidget
  QGridLayout : PyQtWidget

||| TkWidget -> PyQtWidget 매핑 관계(증명)
public export
data WidgetMap : TkWidget -> PyQtWidget -> Type where
  MapRoot : WidgetMap TkRoot QMainWindow
  MapFrame : WidgetMap TkFrame QWidget
  MapLabel : WidgetMap TkLabel QLabel
  MapButton : WidgetMap TkButton QPushButton
  MapListbox : WidgetMap TkListbox QListWidget
  MapEntry : WidgetMap TkEntry QLineEdit
  MapText : WidgetMap TkText QTextEdit
  MapScrollbar : WidgetMap TkScrollbar QScrollArea
  MapToplevel : WidgetMap TkToplevel QDialog
  MapMessageBox : WidgetMap TkMessageBox QMessageBox

||| 매핑 함수: 결과 위젯과 그 증명을 함께 반환 (Sigma)
public export
mapWidget : (tk : TkWidget) -> (qt ** WidgetMap tk qt)
mapWidget TkRoot = (QMainWindow ** MapRoot)
mapWidget TkFrame = (QWidget ** MapFrame)
mapWidget TkLabel = (QLabel ** MapLabel)
mapWidget TkButton = (QPushButton ** MapButton)
mapWidget TkListbox = (QListWidget ** MapListbox)
mapWidget TkEntry = (QLineEdit ** MapEntry)
mapWidget TkText = (QTextEdit ** MapText)
mapWidget TkScrollbar = (QScrollArea ** MapScrollbar)
mapWidget TkToplevel = (QDialog ** MapToplevel)
mapWidget TkMessageBox = (QMessageBox ** MapMessageBox)

--------------------------------------------------------------------------------
-- 2. 메인 윈도우 구조 (섹션 수/구성을 Vect로 강제)
--------------------------------------------------------------------------------

||| 메인 윈도우 섹션
public export
data MainWindowSection : Type where
  Header : MainWindowSection
  PluginList : MainWindowSection
  ButtonBar : MainWindowSection
  StatusBar : MainWindowSection

||| 메인 윈도우 레이아웃
||| sections는 정확히 4개(순서 포함)를 강제한다.
public export
record MainWindowLayout where
  constructor MkMainWindowLayout
  title : String
  width : Nat
  height : Nat
  sections : Vect 4 MainWindowSection

||| 표준 레이아웃(명세상 기본)
||| 기존 Tkinter: 600x400 → PyQt: 800x600 (더 넓고 여유롭게)
public export
defaultLayout : MainWindowLayout
defaultLayout = MkMainWindowLayout
  { title = "HwpAutomation v2.0"
  , width = 800
  , height = 600
  , sections = [Header, PluginList, ButtonBar, StatusBar]
  }

--------------------------------------------------------------------------------
-- 3. 플러그인 리스트 동작 (Fin n으로 인덱스 안전화)
--------------------------------------------------------------------------------

||| 리스트 아이템 클릭 이벤트 (n = 아이템 개수)
public export
data ListItemEvent : (n : Nat) -> Type where
  SingleClick : Fin n -> ListItemEvent n
  DoubleClick : Fin n -> ListItemEvent n
  ContextMenu : Fin n -> ListItemEvent n

||| 리스트 아이템 표시 형식
public export
record ListItemDisplay where
  constructor MkListItemDisplay
  name : String
  version : String
  description : String
  icon : Maybe String

||| 리스트 아이템 포맷팅 (아이콘은 UI에서 별도 처리 가능)
public export
formatListItem : ListItemDisplay -> String
formatListItem item =
  item.name ++ " (v" ++ item.version ++ ") - " ++ item.description

--------------------------------------------------------------------------------
-- 4. 파일 브라우저(다이얼로그) 설정 (mode에 따른 filters 제약)
--------------------------------------------------------------------------------

||| 파일 선택 모드
public export
data FileSelectMode : Type where
  SingleFile : FileSelectMode
  MultipleFiles : FileSelectMode
  Directory : FileSelectMode
  MultipleDirectories : FileSelectMode  -- 여러 폴더 선택 (Consolidator용)

||| 파일 필터
public export
record FileFilter where
  constructor MkFileFilter
  name : String
  pattern : String

||| mode별 필터 타입:
||| - Directory, MultipleDirectories: 필터 없음(단위 타입)
||| - 파일 선택: 최소 1개 이상의 필터(Vect (S k))
public export
DialogFilters : FileSelectMode -> Type
DialogFilters Directory = ()
DialogFilters MultipleDirectories = ()
DialogFilters _ = (k ** Vect (S k) FileFilter)

||| QFileDialog 설정(의존 타입)
public export
record FileDialogConfig (mode : FileSelectMode) where
  constructor MkFileDialogConfig
  title : String
  startDir : String
  filters : DialogFilters mode

||| HWP 파일 필터(단일)
public export
hwpFilter : FileFilter
hwpFilter = MkFileFilter "HWP 파일" "*.hwp *.hwpx"

||| 모든 파일 필터(단일)
public export
allFilesFilter : FileFilter
allFilesFilter = MkFileFilter "모든 파일" "*.*"

||| 기본 HWP 파일 선택 설정(단일 파일)
public export
defaultHwpFileDialog : FileDialogConfig SingleFile
defaultHwpFileDialog = MkFileDialogConfig
  { title = "HWP 파일 선택"
  , startDir = ""
  , filters = (1 ** [hwpFilter, allFilesFilter])
  }

||| 디렉토리 선택 설정(Merger 용)
public export
directorySelectDialog : FileDialogConfig Directory
directorySelectDialog = MkFileDialogConfig
  { title = "폴더 선택"
  , startDir = ""
  , filters = ()
  }

||| 다중 디렉토리 선택 설정(Consolidator 용)
||| QFileDialog는 단일 폴더만 지원하므로
||| "폴더 추가" 버튼 + QListWidget으로 구현
||| Specs/Consolidator/UI.idr의 SelectMultipleFolders 구현
public export
multiDirectorySelectDialog : FileDialogConfig MultipleDirectories
multiDirectorySelectDialog = MkFileDialogConfig
  { title = "폴더 추가"
  , startDir = ""
  , filters = ()
  }

--------------------------------------------------------------------------------
-- 5. PyQt 이벤트 처리 (시그널-슬롯)
--------------------------------------------------------------------------------

||| PyQt 시그널
public export
data Signal : Type where
  Clicked : Signal
  ItemClicked : Signal
  ItemDoubleClicked : Signal
  TextChanged : Signal
  CloseEvent : Signal

||| 슬롯(이벤트 핸들러)
public export
data Slot : Type where
  RunPlugin : Slot
  ShowPluginInfo : Slot
  QuitApp : Slot
  UpdateStatus : (message : String) -> Slot

||| 시그널-슬롯 연결
public export
record Connection where
  constructor MkConnection
  signal : Signal
  slot : Slot

--------------------------------------------------------------------------------
-- 6. 플러그인별 PyQt 위젯 타입
--------------------------------------------------------------------------------

public export
data PluginUIType : Type where
  SimpleFileInput : PluginUIType
  DirectoryWithOptions : PluginUIType
  MultiFileWithOptions : PluginUIType
  MultiDirectoryWithOptions : PluginUIType  -- 여러 폴더 선택 (Consolidator)
  CLIOnly : PluginUIType

||| 플러그인 → UI 타입 매핑
||| (mcp는 더 이상 사용하지 않음)
public export
pluginUIType : String -> PluginUIType
pluginUIType "merger" = DirectoryWithOptions
pluginUIType "separator" = SimpleFileInput
pluginUIType "converter" = MultiFileWithOptions
pluginUIType "seperate2img" = SimpleFileInput
pluginUIType "consolidator" = MultiDirectoryWithOptions  -- 여러 폴더 선택
pluginUIType "latex2hwp" = SimpleFileInput
pluginUIType _ = SimpleFileInput

--------------------------------------------------------------------------------
-- 7. 진행 상태 및 로그 표시
--------------------------------------------------------------------------------

||| 진행 상태 타입
public export
data ProgressState : Type where
  ||| 대기 중 (아직 시작 안 함)
  Idle : ProgressState
  ||| 진행 중 (0~100%)
  Running : (percent : Nat) -> ProgressState
  ||| 완료
  Completed : ProgressState
  ||| 오류 발생
  Error : (message : String) -> ProgressState

||| 진행률 범위 제약 (0 <= percent <= 100)
public export
validPercent : Nat -> Bool
validPercent n = n <= 100

||| 로그 레벨
public export
data LogLevel : Type where
  LogInfo : LogLevel
  LogWarning : LogLevel
  LogError : LogLevel
  LogSuccess : LogLevel

||| 로그 항목
public export
record LogEntry where
  constructor MkLogEntry
  level : LogLevel
  message : String
  timestamp : String  -- "HH:MM:SS" 형식

||| 플러그인 실행 결과 (메인 창에 표시)
public export
record PluginResult where
  constructor MkPluginResult
  pluginId : String
  success : Bool
  successCount : Nat
  failCount : Nat
  outputPath : Maybe String
  logs : List LogEntry

--------------------------------------------------------------------------------
-- 8. 스타일시트 (QSS)
--------------------------------------------------------------------------------

public export
data Theme : Type where
  Light : Theme
  Dark : Theme
  System : Theme

public export
record DarkThemeColors where
  constructor MkDarkThemeColors
  background : String
  foreground : String
  accent : String
  headerBg : String
  listBg : String
  listHover : String
  listSelected : String
  buttonBg : String
  buttonHover : String

public export
defaultDarkColors : DarkThemeColors
defaultDarkColors = MkDarkThemeColors
  { background = "#2b2b2b"
  , foreground = "#ffffff"
  , accent = "#3574f0"
  , headerBg = "#1e1e1e"
  , listBg = "#313335"
  , listHover = "#3c3f41"
  , listSelected = "#2d5a88"
  , buttonBg = "#4a4a4a"
  , buttonHover = "#5a5a5a"
  }

--------------------------------------------------------------------------------
-- 8. 마이그레이션 체크리스트
--------------------------------------------------------------------------------

public export
data MigrationStep : Type where
  InstallPyQt : MigrationStep
  CreateMainWindow : MigrationStep
  ImplementPluginList : MigrationStep
  IntegrateFileBrowser : MigrationStep
  MigratePluginUIs : MigrationStep
  ApplyStyles : MigrationStep
  TestAll : MigrationStep

public export
migrationOrder : List MigrationStep
migrationOrder =
  [ InstallPyQt
  , CreateMainWindow
  , ImplementPluginList
  , IntegrateFileBrowser
  , MigratePluginUIs
  , ApplyStyles
  , TestAll
  ]

--------------------------------------------------------------------------------
-- 10. 플러그인 실행 화면 구조
--------------------------------------------------------------------------------

||| 플러그인 실행 시 화면 구조
||| 플러그인 선택 후 실행하면 메인 창이 실행 화면으로 전환됨
public export
data PluginExecutionSection : Type where
  ||| 상단: 플러그인 이름 + 뒤로가기 버튼
  PluginHeader : PluginExecutionSection
  ||| 입력 영역: 파일/폴더 선택, 옵션 설정
  InputArea : PluginExecutionSection
  ||| 진행 표시: ProgressBar + 현재 상태 텍스트
  ProgressArea : PluginExecutionSection
  ||| 로그 출력: QTextEdit (읽기 전용, 스크롤)
  LogArea : PluginExecutionSection
  ||| 하단 버튼: 실행, 취소, 결과 폴더 열기
  ActionButtons : PluginExecutionSection

||| 실행 화면 레이아웃 (5개 섹션)
public export
executionLayout : Vect 5 PluginExecutionSection
executionLayout = [PluginHeader, InputArea, ProgressArea, LogArea, ActionButtons]

||| 화면 전환 상태
public export
data ViewState : Type where
  ||| 플러그인 목록 화면 (초기)
  PluginListView : ViewState
  ||| 플러그인 실행 화면
  PluginExecutionView : (pluginId : String) -> ViewState

--------------------------------------------------------------------------------
-- 11. 구현 가이드
--------------------------------------------------------------------------------

{-
=== PyQt5 구현 가이드 ===

1. 설치
   uv pip install PyQt5

2. 파일 구조
   ui/
   ├── main.py              # 기존 Tkinter (deprecated)
   ├── main_pyqt.py         # 새 PyQt 메인 윈도우
   └── styles/
       └── dark.qss         # 다크 테마 (옵션)

3. 핵심 변경점
   - 창 크기: 600x400 → 800x600
   - 리스트: 더블클릭으로 플러그인 즉시 실행
   - 스타일: 다크 테마 적용
   - 상태바: 작업 진행 상태 표시
   - 진행 표시: QProgressBar로 작업 진행률 표시
   - 로그 영역: QTextEdit으로 실시간 로그 출력

4. 위젯 매핑 요약
   tk.Tk()         → QMainWindow
   tk.Frame        → QWidget + QLayout
   tk.Listbox      → QListWidget (더블클릭 지원)
   tk.Button       → QPushButton
   messagebox      → QMessageBox
   filedialog      → QFileDialog
   (없음)          → QProgressBar (진행률)
   tk.Text         → QTextEdit (로그 출력)

5. 시그널-슬롯 연결
   button.clicked.connect(handler)
   list.itemDoubleClicked.connect(handler)
   list.itemClicked.connect(handler)

6. 화면 전환 (QStackedWidget)
   - 페이지 0: 플러그인 목록 (PluginListView)
   - 페이지 1: 플러그인 실행 (PluginExecutionView)
   - setCurrentIndex(0/1)로 전환

7. 실행
   PYTHONPATH=. python ui/main_pyqt.py

8. 이전 대상 플러그인 (mcp 제외)
   - merger: 문제 파일 병합
   - separator: 문서 분리
   - converter: HWP → PDF 변환
   - seperate2img: 분리 → 이미지 변환
   - consolidator: 폴더 통합
   - latex2hwp: LaTeX → HWP 변환

9. 로그 출력 색상 (LogLevel별)
   - Info: #ffffff (흰색)
   - Warning: #f39c12 (주황)
   - Error: #e74c3c (빨강)
   - Success: #27ae60 (초록)
-}
