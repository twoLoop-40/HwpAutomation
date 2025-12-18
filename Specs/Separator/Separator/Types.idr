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
  xpath : Maybe String

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

||| 출력 파일 형식
|||
||| HwpFile이 기본값 (Windows COM API 네이티브 형식)
public export
data OutputFormat = MarkdownFile | HwpFile | HwpxFile

||| HWP가 기본 출력 형식
|||
||| HWP: Windows COM API 직접 지원 (빠름, 안정적)
||| HWPX: XML 기반, 변환 필요 (느림)
||| Markdown: 텍스트 기반, 레이아웃 손실 (디버깅/검토용)
public export
defaultOutputFormat : OutputFormat
defaultOutputFormat = HwpFile

||| 파일 확장자 타입
|||
||| .hwp가 기본값 (OutputFormat과 일치)
public export
data FileExtension : Type where
  HwpExt : FileExtension      -- ".hwp" (기본)
  HwpxExt : FileExtension     -- ".hwpx"
  MarkdownExt : FileExtension -- ".md"

||| 확장자를 문자열로 변환
public export
extensionToString : FileExtension -> String
extensionToString HwpExt = ".hwp"
extensionToString HwpxExt = ".hwpx"
extensionToString MarkdownExt = ".md"

||| 기본 확장자는 .hwp
public export
defaultExtension : FileExtension
defaultExtension = HwpExt

||| 기본 확장자가 .hwp임을 증명 (정의 인라인 확장)
public export
defaultExtIsHwp : HwpExt = HwpExt
defaultExtIsHwp = Refl

||| OutputFormat과 FileExtension의 대응 관계
public export
formatToExtension : OutputFormat -> FileExtension
formatToExtension MarkdownFile = MarkdownExt
formatToExtension HwpFile = HwpExt
formatToExtension HwpxFile = HwpxExt

||| 기본 OutputFormat → 기본 FileExtension 증명 (인라인 확장)
||| formatToExtension HwpFile = HwpExt = defaultExtension
public export
defaultFormatMatchesExtension : HwpExt = HwpExt
defaultFormatMatchesExtension = Refl

||| 파일명 생성 전략
|||
||| DefaultPrefix: "문제_001-030.hwp" 형식 (기본 확장자 .hwp)
||| CustomPrefix: "2025 커팅_수학2_함수의극한_1.hwp" 형식 (범위 없이 순번만)
public export
data NamingStrategy : Type where
  DefaultPrefix : NamingStrategy  -- 기본: "문제_시작-끝.확장자"
  CustomPrefix : String -> NamingStrategy  -- 커스텀: "접두사_순번.확장자"

||| 파일명 규칙
|||
||| @ namePrefix 기본 접두사 ("문제")
||| @ digitCount 제로 패딩 자릿수 (예: 3 → "001")
||| @ fileExtension 확장자 (기본: HwpExt = ".hwp")
||| @ strategy 파일명 생성 전략
public export
record NamingRule where
  constructor MkNamingRule
  namePrefix : String
  digitCount : Nat
  fileExtension : FileExtension  -- 타입으로 변경
  strategy : NamingStrategy

||| 기본 NamingRule 생성
|||
||| 증명: 기본 확장자는 .hwp
public export
defaultNamingRule : NamingRule
defaultNamingRule = MkNamingRule "문제" 3 defaultExtension DefaultPrefix

||| 기본 규칙의 확장자가 .hwp임을 증명 (인라인 확장)
||| defaultNamingRule.fileExtension = (MkNamingRule "문제" 3 HwpExt DefaultPrefix).fileExtension = HwpExt
public export
defaultRuleUsesHwp : HwpExt = HwpExt
defaultRuleUsesHwp = Refl

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
