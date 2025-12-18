-- 문항 합병 워크플로우 형식 명세
-- B4 2단 문서에 여러 문항 파일을 합병하는 전체 프로세스

module Specs.MergeWorkflow

import Specs.HwpCommon
import Specs.Common.Result
import Specs.Common.Workflow
import Data.List
import Data.Nat

%default total

-- ============================================================================
-- 1. 문서 상태 정의
-- ============================================================================

-- 소스 파일 상태
public export
data SourceFileState
    = SourceClosed                    -- 소스 파일 닫힘
    | SourceOpened                    -- 소스 파일 열림
    | SourceAnalyzed Nat             -- Para 분석 완료 (총 Para 수)
    | SourceCleaned Nat Nat          -- 빈 Para 제거 완료 (제거 전, 제거 후)
    | SourceReady                     -- 복사 준비 완료

-- 대상 문서 상태
public export
data TargetDocState
    = TargetClosed                    -- 대상 문서 닫힘
    | TargetCreated                   -- 새 문서 생성
    | TargetConfigured                -- B4 + 2단 설정 완료
    | TargetReady Nat Nat            -- 삽입 준비 (현재 페이지, 현재 칼럼)
    | TargetInserted Nat Nat Nat     -- 문항 삽입 완료 (페이지, 칼럼, 문항 번호)
    | TargetCompleted Nat            -- 모든 문항 삽입 완료 (총 문항 수)

-- 전체 워크플로우 상태 (값은 유지하되, 전이/실행결과는 의존 타입으로 강제)
public export
data WorkflowState
    = WorkflowInit
    | SourceProcessing SourceFileState TargetDocState
    | TargetProcessing TargetDocState
    | WorkflowCompleted Nat
    | WorkflowFailed Error

-- ============================================================================
-- 2. Para 정보
-- ============================================================================

-- Para 위치
public export
record ParaPosition where
    constructor MkParaPosition
    list : Nat
    para : Nat
    pos : Nat

-- Para 정보
public export
record ParaInfo where
    constructor MkParaInfo
    paraNum : Nat
    startPos : ParaPosition
    endPos : ParaPosition
    isEmpty : Bool

-- Para 스캔 결과
public export
record ParaScanResult where
    constructor MkParaScanResult
    totalParas : Nat
    emptyParas : List ParaInfo
    contentParas : List ParaInfo

-- ============================================================================
-- 3. 빈 Para 삭제 전략
-- ============================================================================

-- MoveSel 명령
public export
data MoveSelCommand
    = MoveSelLeft
    | MoveSelRight
    | MoveSelUp
    | MoveSelDown

-- 빈 Para 삭제 전략
public export
data EmptyParaStrategy
    = UseSelLeft Nat    -- MoveSelLeft n회 (검증됨, n=2)
    | UseSelRight Nat   -- MoveSelRight n회
    | UseSelDown Nat    -- MoveSelDown n회 (권장, n=1)

-- 전략별 명령 시퀀스
public export
strategyCommands : EmptyParaStrategy -> List MoveSelCommand
strategyCommands (UseSelLeft n) = replicate n MoveSelLeft
strategyCommands (UseSelRight n) = replicate n MoveSelRight
strategyCommands (UseSelDown n) = replicate n MoveSelDown

-- 전략 설명
public export
strategyDescription : EmptyParaStrategy -> String
strategyDescription (UseSelLeft 2) = "Para 시작에서 MoveSelLeft x2 (검증됨)"
strategyDescription (UseSelRight n) = "Para 시작에서 MoveSelRight x" ++ show n
strategyDescription (UseSelDown 1) = "Para 시작에서 MoveSelDown x1 (권장)"
strategyDescription _ = "사용자 정의 전략"

-- ============================================================================
-- 4. 워크플로우 단계
-- ============================================================================

-- 워크플로우 단계 정의
public export
data WorkflowStep
    = Step1_OpenSource String          -- 소스 파일 열기
    | Step2_AnalyzeParas               -- Para 스캔
    | Step3_RemoveEmptyParas EmptyParaStrategy  -- 빈 Para 제거
    | Step4_CopyContent                -- 내용 복사
    | Step5_CloseSource                -- 소스 파일 닫기
    | Step6_CreateTarget               -- 대상 문서 생성
    | Step7_ConfigureTarget            -- B4 + 2단 설정
    | Step8_PasteContent Nat Nat       -- 내용 붙여넣기 (페이지, 칼럼)
    | Step9_BreakColumn                -- 칼럼 구분
    | Step10_SaveTarget String         -- 결과 저장

-- 단계 설명
public export
stepDescription : WorkflowStep -> String
stepDescription (Step1_OpenSource path) = "소스 파일 열기: " ++ path
stepDescription Step2_AnalyzeParas = "Para 스캔 (MoveNextParaBegin)"
stepDescription (Step3_RemoveEmptyParas strategy) = "빈 Para 제거: " ++ strategyDescription strategy
stepDescription Step4_CopyContent = "전체 선택 + 복사 (SelectAll + Copy)"
stepDescription Step5_CloseSource = "소스 파일 닫기"
stepDescription Step6_CreateTarget = "새 문서 생성 (FileNew)"
stepDescription Step7_ConfigureTarget = "B4 페이지 + 2단 레이아웃 설정"
stepDescription (Step8_PasteContent page col) = "붙여넣기 (페이지 " ++ show page ++ ", 칼럼 " ++ show col ++ ")"
stepDescription Step9_BreakColumn = "칼럼 구분 (BreakColumn)"
stepDescription (Step10_SaveTarget path) = "결과 저장: " ++ path

-- ============================================================================
-- 5. 상태 전환
-- ============================================================================

-- 소스 파일 상태 전환
public export
transitionSource : SourceFileState -> WorkflowStep -> Maybe SourceFileState
transitionSource SourceClosed (Step1_OpenSource _) = Just SourceOpened
transitionSource SourceOpened Step2_AnalyzeParas = Nothing
transitionSource (SourceAnalyzed n) (Step3_RemoveEmptyParas _) = Nothing
transitionSource (SourceCleaned n m) Step4_CopyContent = Just SourceReady
transitionSource SourceReady Step5_CloseSource = Just SourceClosed
transitionSource _ _ = Nothing

-- 대상 문서 상태 전환
public export
transitionTarget : TargetDocState -> WorkflowStep -> Maybe TargetDocState
transitionTarget TargetClosed Step6_CreateTarget = Just TargetCreated
transitionTarget TargetCreated Step7_ConfigureTarget = Just TargetConfigured
transitionTarget TargetConfigured (Step8_PasteContent page col) = Just (TargetReady page col)
transitionTarget (TargetReady page col) (Step8_PasteContent _ _) = Just (TargetInserted page col 0)
transitionTarget (TargetInserted page col n) Step9_BreakColumn =
    if col == 2
        then Just (TargetReady (page + 1) 1)  -- 다음 페이지 첫 칼럼
        else Just (TargetReady page (col + 1))  -- 같은 페이지 다음 칼럼
transitionTarget (TargetInserted _ _ n) (Step10_SaveTarget _) = Just (TargetCompleted (n + 1))
transitionTarget _ _ = Nothing

-- ============================================================================
-- 6. 단일 문항 처리 워크플로우
-- ============================================================================

-- 단일 문항 처리 단계
public export
SingleProblemWorkflow : List WorkflowStep
SingleProblemWorkflow =
    [ Step1_OpenSource "source.hwp"
    , Step2_AnalyzeParas
    , Step3_RemoveEmptyParas (UseSelDown 1)
    , Step4_CopyContent
    , Step5_CloseSource
    ]

-- ============================================================================
-- 7. 전체 합병 워크플로우
-- ============================================================================

-- 페이지/칼럼 계산 헬퍼 (0-indexed에서 1-indexed로)
calcPageCol : Nat -> (Nat, Nat)
calcPageCol Z = (1, 1)
calcPageCol idx =
    let page = idx `div` 2 + 1
        col = if idx `mod` 2 == 0 then 1 else 2
    in (page, col)

-- 전체 워크플로우 (n개 문항)
public export
FullMergeWorkflow : Nat -> List String -> List WorkflowStep
FullMergeWorkflow numProblems sourcePaths =
    [ Step6_CreateTarget
    , Step7_ConfigureTarget
    ] ++ concatMap processProblem (zip [0..(numProblems `minus` 1)] sourcePaths)
  where
    processProblem : (Nat, String) -> List WorkflowStep
    processProblem (idx, path) =
        let (page, col) = calcPageCol idx
            isLast = (S idx == numProblems)
        in [ Step1_OpenSource path
           , Step2_AnalyzeParas
           , Step3_RemoveEmptyParas (UseSelDown 1)
           , Step4_CopyContent
           , Step5_CloseSource
           , Step8_PasteContent page col
           ] ++ (if not isLast then [Step9_BreakColumn] else [])
          ++ (if isLast then [Step10_SaveTarget "result.hwp"] else [])

-- ============================================================================
-- 8. 워크플로우 검증
-- ============================================================================

-- 단계 시퀀스 유효성 검증
public export
validateWorkflow : List WorkflowStep -> Bool
validateWorkflow [] = True
validateWorkflow (Step1_OpenSource _ :: Step2_AnalyzeParas :: rest) = validateWorkflow rest
validateWorkflow (Step2_AnalyzeParas :: Step3_RemoveEmptyParas _ :: rest) = validateWorkflow rest
validateWorkflow (Step3_RemoveEmptyParas _ :: Step4_CopyContent :: rest) = validateWorkflow rest
validateWorkflow (Step4_CopyContent :: Step5_CloseSource :: rest) = validateWorkflow rest
validateWorkflow (Step6_CreateTarget :: Step7_ConfigureTarget :: rest) = validateWorkflow rest
validateWorkflow (Step8_PasteContent _ _ :: Step9_BreakColumn :: rest) = validateWorkflow rest
validateWorkflow (Step8_PasteContent _ _ :: Step10_SaveTarget _ :: rest) = validateWorkflow rest
validateWorkflow (_ :: rest) = validateWorkflow rest

-- ============================================================================
-- 9. 워크플로우 실행 결과
-- ============================================================================

-- 실행 결과
public export
record WorkflowStats where
    constructor MkWorkflowStats
    totalProblems : Nat
    insertedProblems : Nat
    totalPages : Nat
    finalParaCount : Nat
    emptyParaCount : Nat

||| 실행 결과(의존 타입): ok=True면 통계가 반드시 존재, ok=False면 Error가 반드시 존재
public export
WorkflowResult : (ok : Bool) -> Type
WorkflowResult ok = Outcome ok WorkflowStats

-- 성공 결과 생성
public export
successResult : Nat -> Nat -> Nat -> Nat -> WorkflowResult True
successResult inserted pages paras emptyParas =
    Ok (MkWorkflowStats inserted inserted pages paras emptyParas)

-- 실패 결과 생성
public export
failureResult : String -> WorkflowResult False
failureResult err =
    Fail (MkError Unknown err)

-- ============================================================================
-- 10. 예제
-- ============================================================================

-- 3개 문항 합병 예제
public export
example3ProblemsWorkflow : List WorkflowStep
example3ProblemsWorkflow = FullMergeWorkflow 3
    [ "problem1.hwp"
    , "problem2.hwp"
    , "problem3.hwp"
    ]

-- 예제 검증
public export
exampleIsValid : Bool
exampleIsValid = validateWorkflow example3ProblemsWorkflow

-- 기대 결과: 3문항, 2페이지 (1페이지 2칼럼 + 2페이지 1칼럼)
public export
exampleExpectedResult : WorkflowResult True
exampleExpectedResult = successResult 3 2 0 0  -- Para 수는 실행 후 결정
