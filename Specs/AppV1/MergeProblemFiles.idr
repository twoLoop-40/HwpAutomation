-- AppV1: 문항 파일 합병 애플리케이션
--
-- 기능: 여러 개의 HWP 문항 파일을 하나의 2단 레이아웃 문서로 합병
-- 기반: Tests/E2E/test_merge_40_problems_clean.py (가장 깔끔한 결과)
-- 개선: v3의 모든 학습 내용 통합

module AppV1.MergeProblemFiles

import Data.List
import Data.String

-- 문항 파일 정보
public export
record ProblemFile where
    constructor MkProblemFile
    path : String
    name : String
    index : Nat

-- Para 정보
public export
record ParaInfo where
    constructor MkParaInfo
    paraNum : Nat
    startPos : (Nat, Nat, Nat)  -- (list, para, pos)
    endPos : (Nat, Nat, Nat)
    isEmpty : Bool

-- 문항 처리 결과
public export
record ProcessResult where
    constructor MkProcessResult
    success : Bool
    paraCount : Nat
    emptyParaCount : Nat
    removedCount : Nat

-- 합병 설정
public export
record MergeConfig where
    constructor MkMergeConfig
    templatePath : String
    problemFiles : List ProblemFile
    outputPath : String
    useTemplate : Bool  -- True: 양식 사용, False: 새 문서 생성

-- 워크플로우 상태
public export
data WorkflowState
    = NotStarted
    | TemplateLoaded
    | ProcessingProblems Nat Nat  -- (현재 인덱스, 전체 개수)
    | AllProcessed
    | Saved
    | Failed String

-- 상태 전환 검증
public export
canTransition : WorkflowState -> WorkflowState -> Bool
canTransition NotStarted TemplateLoaded = True
canTransition TemplateLoaded (ProcessingProblems _ _) = True
canTransition (ProcessingProblems _ _) (ProcessingProblems _ _) = True
canTransition (ProcessingProblems _ _) AllProcessed = True
canTransition AllProcessed Saved = True
canTransition _ (Failed _) = True
canTransition _ _ = False

-- 워크플로우 스펙 인터페이스
public export
interface Monad m => MergeWorkflowSpec m where
    -- 문서 조작
    loadTemplate : String -> m Bool
    createNewDocument : m Bool

    -- 칼럼 변환
    convertToSingleColumn : m Bool

    -- Para 스캔
    scanParas : m (List ParaInfo)

    -- 빈 Para 제거 (MoveSelDown 방식)
    removeEmptyParas : List ParaInfo -> m Nat

    -- 복사/붙여넣기
    copyAll : m Bool
    paste : m Bool
    breakColumn : m Bool

    -- 문서 저장
    saveDocument : String -> m Bool

    -- 페이지 수 확인
    getPageCount : m Nat

-- 단일 문항 처리 워크플로우
public export
processSingleProblem : (Monad m, MergeWorkflowSpec m)
                     => ProblemFile
                     -> m ProcessResult
processSingleProblem problem = do
    -- 1. 파일 열기 (구현체에서 처리)

    -- 2. 1단으로 변환
    _ <- convertToSingleColumn

    -- 3. Para 스캔
    paras <- scanParas
    let emptyParas = filter isEmpty paras

    -- 4. 빈 Para 제거
    removed <- removeEmptyParas emptyParas

    -- 5. 복사
    _ <- copyAll

    pure $ MkProcessResult {
        success = True,
        paraCount = length paras,
        emptyParaCount = length emptyParas,
        removedCount = removed
    }

-- 전체 합병 워크플로우
public export
mergeProblemFiles : (Monad m, MergeWorkflowSpec m)
                  => MergeConfig
                  -> m (Either String Nat)  -- Nat = 최종 페이지 수
mergeProblemFiles config =
    let processAllProblems : List ProblemFile -> m (List ProcessResult)
        processAllProblems [] = pure []
        processAllProblems (p :: ps) = do
            result <- processSingleProblem p

            -- 마지막 문항이 아니면 BreakColumn
            case ps of
                [] => pure ()
                _  => do
                    _ <- breakColumn
                    pure ()

            rest <- processAllProblems ps
            pure (result :: rest)
    in do
        -- 1. 양식 또는 새 문서 준비
        loaded <- if config.useTemplate
                  then loadTemplate config.templatePath
                  else createNewDocument

        case loaded of
            False => pure (Left "Failed to load template or create document")
            True => do
                -- 2. 각 문항 파일 처리
                results <- processAllProblems config.problemFiles

                -- 3. 문서 저장
                saved <- saveDocument config.outputPath

                case saved of
                    False => pure (Left "Failed to save document")
                    True => do
                        -- 4. 최종 페이지 수 반환
                        pages <- getPageCount
                        pure (Right pages)

-- 2로 나누기 (올림)
divBy2Ceil : Nat -> Nat
divBy2Ceil Z = Z
divBy2Ceil (S Z) = S Z  -- 1 / 2 = 1 (올림)
divBy2Ceil (S (S n)) = S (divBy2Ceil n)  -- (n+2) / 2 = 1 + (n / 2)

-- 검증: 예상 페이지 수 계산
public export
expectedPageCount : List ProblemFile -> Nat
expectedPageCount files =
    -- 2단 레이아웃: 2개 문항당 1페이지
    -- 올림 계산
    divBy2Ceil (length files)

-- 안전한 차이 계산 (Nat용)
safeDiff : Nat -> Nat -> Nat
safeDiff Z y = y
safeDiff x Z = x
safeDiff (S x) (S y) = safeDiff x y

-- 검증: 페이지 수 일치 확인
public export
validatePageCount : Nat -> Nat -> Bool
validatePageCount expected actual =
    -- ±2 페이지 이내면 성공으로 간주
    let diff = safeDiff expected actual
    in diff <= 2
