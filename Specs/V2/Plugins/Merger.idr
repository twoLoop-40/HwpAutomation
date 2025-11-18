||| HwpAutomation V2 - Merger 플러그인 명세
|||
||| 목적: 문제 파일 병합 플러그인 (기존 AppV1)
|||
||| 구조:
||| ```
||| automations/merger/
||| ├── __init__.py
||| ├── plugin.py          # MergerPlugin 클래스
||| ├── merger.py          # 병합 로직
||| ├── preprocessor.py    # 전처리
||| ├── para_scanner.py    # 빈 단락 제거
||| ├── column.py          # 단 설정
||| ├── config.py          # 설정
||| └── ui/                # Merger 전용 UI
|||     ├── main.py        # Tkinter 창
|||     └── file_selector.py
||| ```

module Plugins.Merger

import Core
import Automation

%default total

||| Merger 플러그인 모듈
public export
data MergerModule : Type where
  ||| 플러그인 메인 클래스
  PluginMain : MergerModule

  ||| 병합 로직 (ProblemMerger)
  MergerLogic : MergerModule

  ||| 전처리 (Preprocessor)
  Preprocessor : MergerModule

  ||| 빈 단락 스캔
  ParaScanner : MergerModule

  ||| 단 설정
  ColumnSetup : MergerModule

  ||| 설정 관리
  ConfigManager : MergerModule

||| 모듈 파일명
public export
mergerModuleFile : MergerModule -> String
mergerModuleFile PluginMain = "plugin.py"
mergerModuleFile MergerLogic = "merger.py"
mergerModuleFile Preprocessor = "preprocessor.py"
mergerModuleFile ParaScanner = "para_scanner.py"
mergerModuleFile ColumnSetup = "column.py"
mergerModuleFile ConfigManager = "config.py"

||| Merger 워크플로우 단계
public export
data MergerWorkflow : Type where
  ||| 1. 설정 로드
  LoadConfig : MergerWorkflow

  ||| 2. 파일 선택 (CSV + 양식 + 문제 파일들)
  SelectFiles : MergerWorkflow

  ||| 3. 전처리 (병렬/순차)
  PreprocessFiles : (parallel : Bool) -> MergerWorkflow

  ||| 4. 병합 실행
  MergeFiles : MergerWorkflow

  ||| 5. 결과 저장
  SaveResult : (outputPath : String) -> MergerWorkflow

  ||| 6. 완료
  Done : MergerWorkflow

||| 전처리 단계
public export
data PreprocessStep : Type where
  ||| 1단 변환
  ConvertToOneColumn : PreprocessStep

  ||| 빈 단락 제거
  RemoveEmptyParas : PreprocessStep

  ||| 임시 파일 저장
  SaveTemp : PreprocessStep

||| 병합 단계
public export
data MergeStep : Type where
  ||| 양식 파일 열기
  OpenTemplate : MergeStep

  ||| 문제 파일 열기
  OpenProblem : MergeStep

  ||| 내용 복사
  CopyContent : MergeStep

  ||| 내용 붙여넣기
  PasteContent : MergeStep

  ||| 단 나누기
  BreakColumn : MergeStep

  ||| 페이지 나누기
  BreakPage : MergeStep

  ||| 문제 파일 닫기
  CloseProblem : MergeStep

||| Merger 설정
public export
record MergerConfig where
  constructor MkMergerConfig
  ||| CSV 파일 경로
  csvPath : String

  ||| 양식 파일 경로
  templatePath : String

  ||| 출력 파일 경로
  outputPath : String

  ||| 병렬 전처리 활성화
  parallelPreprocess : Bool

  ||| 최대 동시 처리 수
  maxWorkers : Nat

  ||| 임시 파일 디렉토리
  tempDir : String

  ||| 완료 후 임시 파일 삭제
  cleanupTemp : Bool

||| 기본 Merger 설정
public export
defaultMergerConfig : MergerConfig
defaultMergerConfig = MkMergerConfig
  { csvPath = ""
  , templatePath = ""
  , outputPath = "output.hwp"
  , parallelPreprocess = True
  , maxWorkers = 4
  , tempDir = "temp/"
  , cleanupTemp = True
  }

||| Merger UI 컴포넌트
public export
data MergerUIComponent : Type where
  ||| 파일 선택 패널
  FileSelector : MergerUIComponent

  ||| 진행 상태 표시
  ProgressBar : MergerUIComponent

  ||| 로그 뷰어
  LogView : MergerUIComponent

  ||| 설정 패널
  SettingsPanel : MergerUIComponent

  ||| 실행/취소 버튼
  ActionButtons : MergerUIComponent

||| UI 이벤트
public export
data MergerUIEvent : Type where
  ||| CSV 파일 선택
  CSVSelected : (path : String) -> MergerUIEvent

  ||| 양식 파일 선택
  TemplateSelected : (path : String) -> MergerUIEvent

  ||| 출력 경로 선택
  OutputSelected : (path : String) -> MergerUIEvent

  ||| 시작 버튼 클릭
  StartClicked : MergerUIEvent

  ||| 취소 버튼 클릭
  CancelClicked : MergerUIEvent

  ||| 설정 변경
  ConfigChanged : MergerConfig -> MergerUIEvent

||| 진행 상태
public export
record MergerProgress where
  constructor MkMergerProgress
  ||| 현재 단계
  currentStep : String

  ||| 처리된 파일 수
  processedFiles : Nat

  ||| 전체 파일 수
  totalFiles : Nat

  ||| 진행률 (0-100, 정수 표현)
  percentage : Nat

  ||| 예상 남은 시간 (초)
  estimatedTime : Nat

||| 진행률 계산은 Python 구현에서 수행
||| (processed / total) * 100
||| Idris에서는 타입 명세만 정의

||| Merger 결과
public export
data MergerResult : Type where
  ||| 성공
  Success :
    (outputPath : String) ->
    (processedFiles : Nat) ->
    (duration : Double) ->
    MergerResult

  ||| 실패
  Failure :
    (error : String) ->
    (failedAt : String) ->
    MergerResult

  ||| 취소됨
  Cancelled : MergerResult

||| 에러 타입
public export
data MergerError : Type where
  ||| CSV 파일 읽기 실패
  CSVReadError : MergerError

  ||| 양식 파일 열기 실패
  TemplateOpenError : MergerError

  ||| 문제 파일 열기 실패
  ProblemOpenError : (filePath : String) -> MergerError

  ||| 전처리 실패
  PreprocessError : (filePath : String) -> MergerError

  ||| 병합 실패
  MergeError : (reason : String) -> MergerError

  ||| 저장 실패
  SaveError : MergerError

||| 플러그인 상태
public export
data MergerPluginState : Type where
  ||| 대기 중 (설정 필요)
  Idle : MergerPluginState

  ||| 준비됨 (실행 가능)
  Ready : MergerConfig -> MergerPluginState

  ||| 전처리 중
  Preprocessing : MergerProgress -> MergerPluginState

  ||| 병합 중
  Merging : MergerProgress -> MergerPluginState

  ||| 완료
  Completed : MergerResult -> MergerPluginState

  ||| 에러
  Error : MergerError -> MergerPluginState
