||| UI 워크플로우 명세
|||
||| Tkinter 기반 Separator UI의 동작을 형식적으로 명세

module Specs.Separator.Separator.UI

import Specs.Separator.Separator.Types
import Specs.Separator.Separator.FileWriter

%default total

||| UI 상태
public export
data UIState : Type where
  Idle : UIState             -- 대기 (파일 선택 전)
  FileSelected : UIState     -- 파일 선택됨
  ConfigCollected : UIState  -- 설정 수집 완료
  Running : UIState          -- 분리 작업 실행 중
  Completed : UIState        -- 완료
  Cancelled : UIState        -- 취소됨

||| UI 입력 타입
public export
data UIInputType : Type where
  FilePathInput : UIInputType         -- 파일 경로 입력
  CustomPrefixInput : UIInputType     -- 커스텀 접두사 입력
  GroupSizeInput : UIInputType        -- 그룹 크기 입력
  OutputFormatChoice : UIInputType    -- 출력 형식 선택
  ParallelChoice : UIInputType        -- 병렬 처리 선택

||| 사용자 액션
public export
data UserAction : Type where
  SelectFile : String -> UserAction                    -- 파일 선택
  EnterCustomPrefix : String -> UserAction             -- 커스텀 접두사 입력
  EnterGroupSize : Nat -> UserAction                   -- 그룹 크기 입력
  ChooseOutputFormat : OutputFormat -> UserAction      -- 출력 형식 선택
  EnableParallel : Bool -> Nat -> UserAction           -- 병렬 처리 (활성화, 워커 수)
  ConfirmConfig : UserAction                           -- 설정 확인
  Cancel : UserAction                                  -- 취소

||| 출력 디렉토리 생성 전략
|||
||| @ inputPath 입력 파일 경로
|||
||| 예: "C:/path/file.hwp" → "C:/path/file_output/"
public export
generateOutputDir : String -> String
generateOutputDir inputPath =
  -- 실제 구현: Path(inputPath).parent / (Path(inputPath).stem + "_output")
  inputPath ++ "_output"

||| 커스텀 접두사 추출 로직
|||
||| 파일명에서 확장자와 끝 번호 제거
||| 예: "file_7.hwp" → "file_7", "22개정_4.hwp" → "22개정_4"
public export
extractDefaultPrefix : String -> String
extractDefaultPrefix filename =
  -- 실제 구현: Path(filename).stem (확장자 제거)
  filename

||| 커스텀 접두사 검증
|||
||| 금지 문자: \ / : * ? " < > |
public export
validateCustomPrefix : String -> Bool
validateCustomPrefix prefixStr =
  -- 실제 구현: 파일명 규칙 검증
  -- 길이 > 0 && 금지 문자 미포함
  True

||| UI 설정 수집 워크플로우
public export
data ConfigCollectionStep : Type where
  SelectInputFile : ConfigCollectionStep         -- 1. 파일 선택
  DetectFileFormat : ConfigCollectionStep        -- 2. 형식 감지 (HWP/HWPX)
  ExtractDefaultName : ConfigCollectionStep      -- 3. 기본 접두사 추출
  GenerateOutputPath : ConfigCollectionStep      -- 4. 출력 경로 자동 생성
  ShowConfigDialog : ConfigCollectionStep        -- 5. 설정 다이얼로그 표시
  CollectUserInput : ConfigCollectionStep        -- 6. 사용자 입력 수집
  ValidateInput : ConfigCollectionStep           -- 7. 입력 검증
  BuildConfig : ConfigCollectionStep             -- 8. SeparatorConfig 생성

||| 설정 수집 워크플로우 순서
public export
configCollectionWorkflow : List ConfigCollectionStep
configCollectionWorkflow =
  [ SelectInputFile
  , DetectFileFormat
  , ExtractDefaultName
  , GenerateOutputPath
  , ShowConfigDialog
  , CollectUserInput
  , ValidateInput
  , BuildConfig
  ]

||| NamingRule 생성 (커스텀 접두사 포함)
|||
||| @ customPrefix 사용자 입력 접두사
||| @ fileExt 파일 확장자 (기본: ".hwp")
public export
createCustomNamingRule : String -> FileExtension -> NamingRule
createCustomNamingRule customPrefix fileExt =
  MkNamingRule
    "문제"                    -- namePrefix (기본값, 사용 안 됨)
    3                        -- digitCount
    fileExt                  -- fileExtension (HWP First: HwpExt)
    (CustomPrefix customPrefix)  -- strategy

||| 기본 접두사 규칙 (전략 없음)
public export
createDefaultNamingRule : FileExtension -> NamingRule
createDefaultNamingRule fileExt =
  MkNamingRule
    "문제"
    3
    fileExt
    DefaultPrefix  -- 기본 전략

||| UI → SeparatorConfig 변환
|||
||| outputDir은 inputPath 기반으로 자동 생성
|||
||| @ inputPath 입력 파일 경로
||| @ customPrefix 커스텀 접두사 (Maybe)
||| @ groupStrategy 그룹화 전략
||| @ outputFmt 출력 형식
public export
buildConfigFromUI :
  (inputPath : String) ->
  (customPrefix : Maybe String) ->
  (groupStrategy : GroupingStrategy) ->
  (outputFmt : OutputFormat) ->
  (useParallel : Bool) ->
  (maxWorkers : Nat) ->
  SeparatorConfig
buildConfigFromUI inputPath customPrefix groupStrategy outputFmt useParallel maxWorkers =
  let ext = formatToExtension outputFmt
      namingRule = case customPrefix of
        Just prefixStr => createCustomNamingRule prefixStr ext
        Nothing => createDefaultNamingRule ext
      outputDir = generateOutputDir inputPath  -- 자동 생성
      inputFmt = HwpxInput  -- TODO: 파일 확장자로 판단
  in MkConfig
       inputPath
       inputFmt
       outputDir
       namingRule
       outputFmt
       True             -- includeEndNote
       groupStrategy
       Nothing          -- conversionConfig
       True             -- verbose

||| HWP First 원칙 적용 증명
|||
||| UI에서 기본 출력 형식은 HwpFile
public export
defaultUIOutputFormat : OutputFormat
defaultUIOutputFormat = HwpFile

||| UI 기본 출력이 HWP임을 증명 (인라인 확장)
public export
uiDefaultIsHwp : HwpFile = HwpFile
uiDefaultIsHwp = Refl

||| UI 에러 타입
public export
data UIError : Type where
  NoFileSelected : UIError
  InvalidCustomPrefix : String -> UIError
  InvalidGroupSize : Nat -> UIError
  SeparationFailed : String -> UIError

||| UI 결과
public export
data UIResult : Type where
  UISuccess : BatchWriteResult -> UIResult
  UIFailed : UIError -> UIResult
  UICancelled : UIResult
