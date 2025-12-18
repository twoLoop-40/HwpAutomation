||| HWPX XML 파싱 명세
|||
||| HWP → HWPX 변환 → XML → EndNote 추출

module Specs.Separator.Separator.XmlParser

import Specs.Separator.Separator.Types

%default total

||| XML 파싱 단계
public export
data ParseStep : Type where
  ConvertToHwpx : ParseStep  -- HWP → HWPX 변환 (필요시)
  OpenZip : ParseStep  -- ZIP 파일 열기
  ReadSection : ParseStep  -- section0.xml 읽기
  ParseXml : ParseStep  -- XML 파싱
  FindEndNotes : ParseStep  -- endNote 찾기
  SortByPosition : ParseStep  -- 위치 순 정렬

||| 파싱 상태
public export
data ParseState : Type where
  Initial : ParseState
  HwpxReady : ParseState  -- HWPX 파일 준비됨
  ZipOpened : ParseState
  XmlLoaded : ParseState
  EndNotesFound : (count : Nat) -> ParseState
  Sorted : (endNotes : List EndNoteInfo) -> ParseState
  Failed : (step : ParseStep) -> (error : String) -> ParseState

||| 상태 전환
public export
nextState : ParseState -> ParseStep -> ParseState
nextState Initial ConvertToHwpx = HwpxReady
nextState HwpxReady OpenZip = ZipOpened
nextState ZipOpened ReadSection = XmlLoaded
nextState XmlLoaded ParseXml = XmlLoaded
nextState XmlLoaded FindEndNotes = EndNotesFound 0  -- 실제론 파싱 후 개수
nextState (EndNotesFound n) SortByPosition = Sorted []  -- 실제론 정렬된 리스트
nextState _ _ = Failed OpenZip "Invalid state transition"

||| 파일 형식 감지
public export
data FileFormat : Type where
  HwpFormat : FileFormat  -- .hwp (binary)
  HwpxFormat : FileFormat  -- .hwpx (ZIP+XML)
  Unknown : FileFormat

||| 파일 경로에서 형식 추론
|||
||| Python 구현에서 처리하므로 임시로 HwpxFormat 반환
public export
detectFormat : String -> FileFormat
detectFormat path = HwpxFormat

||| 변환 필요 여부
public export
needsConversion : FileFormat -> Bool
needsConversion HwpFormat = True
needsConversion HwpxFormat = False
needsConversion Unknown = False

||| EndNote 속성 추출
public export
data EndNoteAttribute : Type where
  Number : Nat -> EndNoteAttribute  -- number="1"
  SuffixChar : String -> EndNoteAttribute  -- suffixChar="46"
  InstId : String -> EndNoteAttribute  -- instId="298702148"

||| EndNote 검증
public export
isValidEndNote : EndNoteInfo -> Bool
isValidEndNote endnote =
  let MkEndNoteNumber n = endnote.number
  in n >= 1 && n <= 408  -- 1~408 범위

||| EndNote 정렬 (위치 기준)
public export
compareEndNotes : EndNoteInfo -> EndNoteInfo -> Ordering
compareEndNotes en1 en2 =
  compare en1.position.index en2.position.index

||| 파싱 워크플로우 (HWPX 입력)
public export
hwpxWorkflow : List ParseStep
hwpxWorkflow =
  [ OpenZip
  , ReadSection
  , ParseXml
  , FindEndNotes
  , SortByPosition
  ]

||| 파싱 워크플로우 (HWP 입력 - 변환 포함)
public export
hwpWorkflow : List ParseStep
hwpWorkflow =
  [ ConvertToHwpx
  , OpenZip
  , ReadSection
  , ParseXml
  , FindEndNotes
  , SortByPosition
  ]

||| 입력 형식에 따른 워크플로우 선택
public export
selectWorkflow : FileFormat -> List ParseStep
selectWorkflow HwpFormat = hwpWorkflow
selectWorkflow HwpxFormat = hwpxWorkflow
selectWorkflow Unknown = []

||| 예상 결과
|||
||| @ inputPath 입력 파일 경로
||| @ expected 예상 미주 개수
public export
expectedResult : (inputPath : String) -> (expected : Nat) -> Type
expectedResult path expected =
  (result : ParseState **
   case result of
     Sorted endNotes => length endNotes = expected
     _ => Void)
