module Specs.Separator.Separator.Types

%default total

public export
data ElementID = MkElementID Nat

public export
data EndNoteNumber = MkEndNoteNumber Nat

public export
data ProblemNumber = MkProblemNumber Nat

public export
data ParaType = BodyPara | EndNotePara

public export
record ElementPosition where
  constructor MkElementPosition
  index : Nat
  lineNumber : Maybe Nat

||| 정답 형식 (향후 확장용)
|||
||| TODO: 정답 패턴 검증 및 추출
||| - WithAnswer: "\d\.\s*\[정답\]" 패턴
||| - OnlyExplanation: 해설만
||| - Empty: 빈 미주
public export
data AnswerFormat : Type where
  WithAnswer : AnswerFormat
  OnlyExplanation : AnswerFormat
  Empty : AnswerFormat

public export
record EndNoteInfo where
  constructor MkEndNote
  number : EndNoteNumber
  position : ElementPosition
  suffixChar : String
  instId : String
  paraCount : Nat
  charCount : Nat
  -- TODO: answerFormat : AnswerFormat 추가 예정

||| 문제 정보
|||
||| **핵심 로직 (iter_note_blocks 패턴)**:
||| - EndNote는 본문에 **앵커**를 가짐
||| - 문제 i번 = EndNote[i-1] 앵커 ~ EndNote[i] 앵커
||| - 첫 문제 = 문서 시작(0) ~ EndNote[0] 앵커
|||
||| @ number 문제 번호 (1부터 시작)
||| @ startPosition 본문 시작 위치 (이전 EndNote 앵커 or 0)
||| @ endPosition 본문 끝 위치 (현재 EndNote 앵커)
||| @ endnote 해당 해설 정보 (참조용, EndNote[i])
||| @ bodyParaCount 본문 문단 수
||| @ totalCharCount 본문 글자 수
public export
record ProblemInfo where
  constructor MkProblem
  number : ProblemNumber
  startPosition : ElementPosition  -- 본문 시작 (이전 EndNote 앵커 or 문서 시작)
  endPosition : ElementPosition    -- 본문 끝 (현재 EndNote 앵커)
  endnote : EndNoteInfo            -- 해당 해설 (EndNote[i])
  bodyParaCount : Nat
  totalCharCount : Nat

public export
data SeparationResult : Type where
  Success : (problemCount : Nat) -> (problems : List ProblemInfo) -> SeparationResult
  Failure : (error : String) -> SeparationResult

public export
data OutputFormat = TextFile | HwpFile | HwpxFile

public export
record NamingRule where
  constructor MkNamingRule
  namePrefix : String
  digitCount : Nat
  fileExtension : String

public export
data InputFormat = HwpInput | HwpxInput

public export
record ConversionConfig where
  constructor MkConversionConfig
  keepOriginal : Bool
  tempDir : String
  timeout : Nat

||| 그룹화 전략
|||
||| 문제를 몇 개씩 묶을지 결정
public export
data GroupingStrategy : Type where
  OnePerFile : GroupingStrategy  -- 1문제 = 1파일
  GroupByCount : Nat -> GroupingStrategy  -- N문제 = 1파일 (예: 30개씩)
  GroupByRange : List (Nat, Nat) -> GroupingStrategy  -- 범위 지정 (예: [(1,30), (31,60), ...])

||| 그룹 정보
|||
||| @ groupNum 그룹 번호 (1부터 시작)
||| @ startProblem 시작 문제 번호
||| @ endProblem 끝 문제 번호
||| @ problemCount 이 그룹의 문제 개수
public export
record GroupInfo where
  constructor MkGroup
  groupNum : Nat
  startProblem : ProblemNumber
  endProblem : ProblemNumber
  problemCount : Nat

public export
record SeparatorConfig where
  constructor MkConfig
  inputPath : String
  inputFormat : InputFormat
  outputDir : String
  namingRule : NamingRule
  outputFormat : OutputFormat
  includeEndNote : Bool
  groupingStrategy : GroupingStrategy  -- 그룹화 전략 추가
  conversionConfig : Maybe ConversionConfig
  verbose : Bool
