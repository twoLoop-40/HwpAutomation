||| 문제 추출 명세
|||
||| EndNote 기준으로 문제 본문 추출

module Specs.Separator.Separator.Extractor

import Specs.Separator.Separator.Types

%default total

||| 리스트 쌍으로 묶기
|||
||| 두 리스트의 각 요소를 쌍으로 묶음 (짧은 리스트 길이만큼)
||| @ xs 첫 번째 리스트
||| @ ys 두 번째 리스트
||| 구현: Python의 zip(xs, ys) 또는 [(x, y) for x, y in zip(xs, ys)]
public export
zip : List a -> List b -> List (a, b)
zip [] _ = []
zip _ [] = []
zip (x :: xs) (y :: ys) = (x, y) :: zip xs ys

||| 리스트에서 처음 n개 요소 가져오기
|||
||| @ n 가져올 개수
||| @ xs 리스트
public export
takeList : Nat -> List a -> List a
takeList Z _ = []
takeList _ [] = []
takeList (S k) (x :: xs) = x :: takeList k xs

||| 리스트에서 처음 n개 요소 버리기
|||
||| @ n 버릴 개수
||| @ xs 리스트
public export
dropList : Nat -> List a -> List a
dropList Z xs = xs
dropList _ [] = []
dropList (S k) (_ :: xs) = dropList k xs

||| 추출 단계
public export
data ExtractStep : Type where
  IdentifyBoundaries : ExtractStep  -- 문제 경계 식별
  ExtractBodyParas : ExtractStep  -- 본문 문단 추출
  ExtractEndNoteText : ExtractStep  -- 미주 텍스트 추출
  CombineTexts : ExtractStep  -- 본문+미주 결합
  ValidateResult : ExtractStep  -- 결과 검증

||| 문제 경계 (iter_note_blocks 패턴)
|||
||| **핵심 로직**:
||| - EndNote는 본문에 앵커를 가짐
||| - 문제 i번 = EndNote[i-1] 앵커 ~ EndNote[i] 앵커
||| - 첫 문제 = 문서 시작(0) ~ EndNote[0] 앵커
|||
||| @ problemNum 문제 번호 (1부터 시작)
||| @ startPos 본문 시작 (이전 EndNote 앵커 or 0)
||| @ endPos 본문 끝 (현재 EndNote 앵커)
||| @ isFirst 첫 번째 문제 여부
public export
record ProblemBoundary where
  constructor MkBoundary
  problemNum : ProblemNumber
  startPos : ElementPosition  -- 이전 EndNote 앵커 (첫 문제는 0)
  endPos : ElementPosition    -- 현재 EndNote 앵커
  isFirst : Bool              -- 첫 번째 문제 여부

||| 문제 블록 추출 (iter_note_blocks 로직)
|||
||| **참조**: math-collector/src/tools/handle_hwp.py:iter_note_blocks
|||
||| **알고리즘**:
||| 1. 첫 문제: (문서 시작=0) ~ EndNote[0] 앵커
||| 2. 문제 i (i >= 2): EndNote[i-2] 앵커 ~ EndNote[i-1] 앵커
|||
||| **예시 (408문제)**:
||| - 문제 1: index 0 ~ EndNote[0].position (index 44)
||| - 문제 2: EndNote[0].position (44) ~ EndNote[1].position (418)
||| - ...
||| - 문제 408: EndNote[406].position ~ EndNote[407].position
|||
||| @ endNotes 정렬된 EndNote 리스트 (408개)
||| @ totalElements 전체 요소 개수 (사용 안 함, 해설 영역은 제외)
public export
covering
extractProblemBlocks : (endNotes : List EndNoteInfo) ->
                      (totalElements : Nat) ->
                      List ProblemBoundary
extractProblemBlocks [] _ = []
extractProblemBlocks (first :: rest) _ =
  -- 첫 문제: 문서 시작 ~ EndNote[0] 앵커
  let firstBoundary = MkBoundary
        (MkProblemNumber 1)
        (MkElementPosition 0 Nothing)  -- 문서 시작
        first.position                 -- EndNote[0] 앵커
        True                           -- 첫 번째 문제

      -- 나머지 문제들: EndNote[i-1] ~ EndNote[i]
      restBoundaries = makeRestBoundaries 2 first rest

  in firstBoundary :: restBoundaries
  where
    -- 재귀적으로 나머지 문제 생성
    covering
    makeRestBoundaries : Nat -> EndNoteInfo -> List EndNoteInfo -> List ProblemBoundary
    makeRestBoundaries _ _ [] = []
    makeRestBoundaries num prev (curr :: remaining) =
      MkBoundary
        (MkProblemNumber num)
        prev.position  -- 이전 EndNote 앵커 = 본문 시작
        curr.position  -- 현재 EndNote 앵커 = 본문 끝
        False
      :: makeRestBoundaries (num + 1) curr remaining

||| 본문 문단 필터
|||
||| 주어진 범위 내에서 EndNotePara 제외
public export
filterBodyParas : (startPos : Nat) ->
                 (endPos : Nat) ->
                 (allParas : List (Nat, ParaType)) ->
                 List Nat
filterBodyParas start end paras =
  map fst $ filter isInRangeAndBody paras
  where
    isInRangeAndBody : (Nat, ParaType) -> Bool
    isInRangeAndBody (pos, BodyPara) = pos >= start && pos < end
    isInRangeAndBody (pos, EndNotePara) = False

||| 문제 추출 워크플로우
public export
extractWorkflow : List ExtractStep
extractWorkflow =
  [ IdentifyBoundaries
  , ExtractBodyParas
  , ExtractEndNoteText
  , CombineTexts
  , ValidateResult
  ]

||| 추출 결과 검증
|||
||| 모든 문제가 유효한 데이터를 가지는지 확인
public export
validateProblem : ProblemInfo -> Bool
validateProblem prob =
  prob.bodyParaCount > 0 || prob.totalCharCount > 0

||| 전체 문제 검증
public export
validateAllProblems : List ProblemInfo -> Bool
validateAllProblems probs = all validateProblem probs

||| 예상 문제 수 확인
public export
checkProblemCount : (expected : Nat) -> List ProblemInfo -> Bool
checkProblemCount expected probs = length probs == expected

||| N개씩 묶기 헬퍼 (Structural recursion on list)
|||
||| @ groupSize 그룹 크기
||| @ groupNum 현재 그룹 번호
||| @ remaining 남은 문제 리스트
covering
groupByCountHelper : Nat -> Nat -> List ProblemInfo -> List GroupInfo
groupByCountHelper _ _ [] = []
groupByCountHelper groupSize groupNum remaining =
  let taken = takeList groupSize remaining
      dropped = dropList groupSize remaining
      count = length taken
  in case (taken, reverse taken) of
       (first :: _, last :: _) =>
         MkGroup groupNum first.number last.number count ::
         groupByCountHelper groupSize (groupNum + 1) dropped
       _ => []

||| 범위별 그룹화 헬퍼
|||
||| @ groupNum 현재 그룹 번호
||| @ ranges 범위 리스트
||| @ allProbs 전체 문제 리스트
covering
groupByRangeHelper : Nat -> List (Nat, Nat) -> List ProblemInfo -> List GroupInfo
groupByRangeHelper _ [] _ = []
groupByRangeHelper groupNum ((start, end) :: rest) allProbs =
  let inRange : ProblemInfo -> Bool
      inRange prob = case prob.number of
                       MkProblemNumber n => n >= start && n <= end
      filtered = filter inRange allProbs
      count = length filtered
  in case (filtered, reverse filtered) of
       (first :: _, last :: _) =>
         MkGroup groupNum first.number last.number count ::
         groupByRangeHelper (groupNum + 1) rest allProbs
       _ => groupByRangeHelper (groupNum + 1) rest allProbs

||| 문제 그룹화
|||
||| @ strategy 그룹화 전략
||| @ problems 전체 문제 리스트
|||
||| 구현 로직:
|||
||| 1. OnePerFile:
|||    - 각 문제를 개별 그룹으로 (1문제 = 1파일)
|||    - groups = [MkGroup i prob.number prob.number 1 for i, prob in enumerate(probs, 1)]
|||
||| 2. GroupByCount n (예: n=30):
|||    - n개씩 묶어서 그룹 생성
|||    - 408개 → 30개씩 → 14개 그룹 (13×30 + 1×18)
|||    - Python: chunks = [probs[i:i+n] for i in range(0, len(probs), n)]
|||    - 각 chunk에서 first.number ~ last.number로 GroupInfo 생성
|||
||| 3. GroupByRange [(1,30), (31,60), ...]:
|||    - 지정된 범위대로 그룹 생성
|||    - 각 범위 (start, end)에서 문제 번호가 start <= n <= end인 것만 필터링
|||    - filtered_probs = [p for p in probs if start <= p.number <= end]
public export
covering
groupProblems : GroupingStrategy -> List ProblemInfo -> List GroupInfo
groupProblems OnePerFile probs =
  -- 1문제 = 1파일: 각 문제가 하나의 그룹
  let indexed = zip [1..length probs] probs
      makeGroup : (Nat, ProblemInfo) -> GroupInfo
      makeGroup (idx, prob) =
        MkGroup idx prob.number prob.number 1
  in map makeGroup indexed
groupProblems (GroupByCount n) probs =
  -- N개씩 묶기: 408개 → 30개씩 → 14개 그룹 (마지막 18개)
  groupByCountHelper n 1 probs
groupProblems (GroupByRange ranges) probs =
  -- 범위 지정: [(1,30), (31,60), (61,90), ...]
  groupByRangeHelper 1 ranges probs

||| 그룹별 파일명 생성
|||
||| @ rule 파일명 규칙
||| @ group 그룹 정보
||| 예: "문제_001-030.hwpx" (30개 묶음)
|||     "문제_001.hwpx" (1개)
public export
generateGroupFilename : NamingRule -> GroupInfo -> String
generateGroupFilename rule group =
  case (group.startProblem, group.endProblem) of
    (MkProblemNumber start, MkProblemNumber end) =>
      if start == end
      then -- 1문제만: "문제_001.hwpx"
        rule.namePrefix ++ "_" ++ padNumber rule.digitCount start ++ rule.fileExtension
      else -- 여러 문제: "문제_001-030.hwpx"
        rule.namePrefix ++ "_" ++
        padNumber rule.digitCount start ++ "-" ++
        padNumber rule.digitCount end ++ rule.fileExtension
  where
    padNumber : Nat -> Nat -> String
    padNumber digits num = show num  -- 실제로는 제로 패딩

||| 그룹화 예제: 408개를 30개씩
|||
||| 결과: 14개 그룹 (13개는 30문제, 마지막은 18문제)
||| 구현 시 계산: 408 / 30 = 13 ... 18
|||              → 13개 전체 그룹 + 1개 부분 그룹 = 14개 그룹
public export
example408By30 : String
example408By30 =
  "408개 문제를 30개씩 묶으면: 14개 그룹 (13×30 + 1×18)"
