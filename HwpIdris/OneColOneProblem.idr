-- OneColOneProblem Workflow Specification
-- 칼럼당 1개 문제 삽입 로직 (Schema/OneColOneProblemLogic.md 기반)

module HwpIdris.OneColOneProblem

import Data.String
import Data.List

-- Para 정보
public export
record ParaInfo where
    constructor MkParaInfo
    index : Nat
    isEmpty : Bool
    startPos : (Nat, Nat, Nat)  -- List, Para, Pos
    endPos : (Nat, Nat, Nat)

-- 문서 상태
public export
data DocState = Closed | Opened | Modified

-- 칼럼 상태
public export
data ColumnState = SingleColumn | MultiColumn Nat

-- 페이지 상태
public export
data PageState = SinglePage | MultiPage Nat

-- 문제 파일 정보
public export
record ProblemFile where
    constructor MkProblemFile
    path : String
    columnState : ColumnState
    pageState : PageState
    paras : List ParaInfo
    emptyParaCount : Nat

-- 대상 문서 정보
public export
record TargetDoc where
    constructor MkTargetDoc
    templatePath : String
    currentColumns : Nat
    problems : List ProblemFile

-- 작업 결과
public export
data WorkflowResult : Type -> Type where
    Success : a -> WorkflowResult a
    Failure : String -> WorkflowResult a

-- Functor instance
public export
Functor WorkflowResult where
    map f (Success x) = Success (f x)
    map f (Failure e) = Failure e

-- Para가 비어있는지 확인
public export
isEmptyPara : ParaInfo -> Bool
isEmptyPara para =
    let (_, _, startP) = para.startPos
        (_, _, endP) = para.endPos
    in startP == endP

-- 빈 Para 필터링
public export
filterEmptyParas : List ParaInfo -> List ParaInfo
filterEmptyParas = filter isEmptyPara

-- 빈 Para 개수 세기
public export
countEmptyParas : List ParaInfo -> Nat
countEmptyParas paras = length (filterEmptyParas paras)

-- 워크플로우 단계
public export
data WorkflowStep
    = CopyTemplate String                    -- 양식 파일 복사
    | OpenSourceFile String                  -- 소스 파일 열기
    | CheckColumnCount                       -- 단 개수 확인
    | ConvertToSingleColumn                  -- 1단으로 변환
    | ScanParas                              -- Para 스캔
    | RemoveEmptyParas                       -- 빈 Para 제거
    | CheckPageCount                         -- 페이지 수 확인
    | RemoveEmptyParasUntilOnePage           -- 1페이지 될 때까지 빈 Para 제거
    | CopyToTarget                           -- 대상에 복사
    | BreakColumn                            -- 칼럼 나누기
    | SaveAndClose String                    -- 저장 및 종료

-- 워크플로우 상태
public export
record WorkflowState where
    constructor MkWorkflowState
    currentStep : WorkflowStep
    sourceFile : Maybe ProblemFile
    targetDoc : TargetDoc
    remainingFiles : List String
    error : Maybe String

-- 초기 상태
public export
initialState : String -> List String -> WorkflowState
initialState templatePath files = MkWorkflowState
    { currentStep = CopyTemplate templatePath
    , sourceFile = Nothing
    , targetDoc = MkTargetDoc templatePath 0 []
    , remainingFiles = files
    , error = Nothing
    }

-- 상태 전환 검증
public export
canTransition : WorkflowStep -> WorkflowStep -> Bool
canTransition (CopyTemplate _) (OpenSourceFile _) = True
canTransition (OpenSourceFile _) CheckColumnCount = True
canTransition CheckColumnCount ConvertToSingleColumn = True
canTransition CheckColumnCount ScanParas = True  -- 이미 1단이면
canTransition ConvertToSingleColumn ScanParas = True
canTransition ScanParas RemoveEmptyParas = True
canTransition RemoveEmptyParas CheckPageCount = True
canTransition CheckPageCount RemoveEmptyParasUntilOnePage = True
canTransition CheckPageCount CopyToTarget = True  -- 이미 1페이지면
canTransition RemoveEmptyParasUntilOnePage CopyToTarget = True
canTransition CopyToTarget BreakColumn = True
canTransition CopyToTarget (SaveAndClose _) = True  -- 마지막 파일
canTransition BreakColumn (OpenSourceFile _) = True  -- 다음 파일
canTransition _ _ = False

-- 워크플로우 실행 타입
public export
data WorkflowExecution : WorkflowStep -> Type where
    ExecuteCopyTemplate : String -> WorkflowExecution (CopyTemplate path)
    ExecuteOpenSource : String -> WorkflowExecution (OpenSourceFile path)
    ExecuteCheckColumn : WorkflowExecution CheckColumnCount
    ExecuteConvertColumn : WorkflowExecution ConvertToSingleColumn
    ExecuteScanParas : WorkflowExecution ScanParas
    ExecuteRemoveEmpty : WorkflowExecution RemoveEmptyParas
    ExecuteCheckPage : WorkflowExecution CheckPageCount
    ExecuteRemoveUntilOne : WorkflowExecution RemoveEmptyParasUntilOnePage
    ExecuteCopy : WorkflowExecution CopyToTarget
    ExecuteBreak : WorkflowExecution BreakColumn
    ExecuteSave : String -> WorkflowExecution (SaveAndClose path)

-- 워크플로우 명세
public export
interface WorkflowSpec (m : Type -> Type) where
    -- 양식 복사
    copyTemplate : String -> m Bool

    -- 파일 열기/닫기
    openFile : String -> m Bool
    closeFile : m ()

    -- 칼럼 작업
    getColumnCount : m Nat
    convertToSingleColumn : m Bool

    -- Para 작업
    scanParas : m (List ParaInfo)
    removeEmptyPara : ParaInfo -> m Bool

    -- 페이지 작업
    getPageCount : m Nat

    -- 복사/붙여넣기
    selectAll : m ()
    copy : m ()
    paste : m ()

    -- 칼럼 나누기
    breakColumn : m ()

    -- 저장
    saveAs : String -> m ()

-- 안전한 빈 Para 제거 (MoveSelLeft 활용)
-- 주의: 비어있지 않은 Para는 건드리지 않음
public export
data RemoveStrategy
    = FromEnd      -- 마지막부터 제거
    | FromStart    -- 처음부터 제거
    | All          -- 모두 제거

-- Para 제거 결과
public export
record RemovalResult where
    constructor MkRemovalResult
    removed : Nat
    remaining : List ParaInfo
    pageCount : Nat

-- 1페이지가 될 때까지 제거 로직
public export
removeUntilOnePage : (Applicative m, WorkflowSpec m)
                   => List ParaInfo
                   -> Nat  -- 현재 페이지 수
                   -> m RemovalResult
removeUntilOnePage emptyParas currentPages =
    -- TODO: 구현 필요 (Python에서 구현)
    pure (MkRemovalResult 0 [] 1)

-- 전체 워크플로우 타입
public export
runWorkflow : (Applicative m, WorkflowSpec m)
            => String              -- 템플릿 경로
            -> List String         -- 문제 파일 목록
            -> String              -- 출력 경로
            -> m (WorkflowResult String)
runWorkflow templatePath files outputPath =
    -- TODO: 구현 필요 (Python에서 구현)
    pure (Success outputPath)
