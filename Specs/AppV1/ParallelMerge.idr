-- LangGraph Send를 활용한 병렬 문항 합병 워크플로우
--
-- 핵심 아이디어:
-- 1. 병렬 전처리 (최대 20개 동시): 각 파일을 1단 변환 + 빈 Para 제거
-- 2. 순차 합병: InsertFile + BreakColumn으로 순차 삽입
--
-- LangGraph Send 패턴:
-- - batch_node에서 최대 20개씩 Send로 전송
-- - 각 preprocess_worker가 독립적으로 파일 전처리
-- - collect_node에서 결과 수집
-- - merge_node에서 순차 InsertFile 합병

module HwpIdris.AppV1.ParallelMerge

import Data.List

%default total

-- ============================================================
-- 기본 타입
-- ============================================================

-- 문항 파일 정보
public export
record ProblemFile where
    constructor MkProblemFile
    path : String
    name : String
    index : Nat

-- 전처리된 파일 정보
public export
record ProcessedFile where
    constructor MkProcessedFile
    original : ProblemFile
    processedPath : String
    paraCount : Nat
    emptyParasRemoved : Nat

-- 병렬 처리 제약
public export
maxWorkers : Nat
maxWorkers = 20

-- ============================================================
-- LangGraph 노드 타입
-- ============================================================

-- 노드 종류
public export
data NodeType
    = StartNode                 -- 시작 노드
    | BatchNode                 -- 배치 생성 노드
    | PreprocessWorkerNode      -- 전처리 워커 (병렬 실행)
    | CollectNode               -- 결과 수집 노드
    | MergeNode                 -- 순차 합병 노드
    | EndNode                   -- 종료 노드

-- ============================================================
-- 워크플로우 상태
-- ============================================================

-- 워크플로우 단계
public export
data WorkflowState
    = Initial                   -- 초기 상태
    | Batching                  -- 배치 생성 중
    | Preprocessing Nat Nat     -- 전처리 중 (완료/전체)
    | Collecting                -- 결과 수집 중
    | Merging Nat Nat           -- 합병 중 (완료/전체)
    | Completed                 -- 완료
    | Failed String             -- 실패

-- 상태 전환 검증
public export
canTransition : WorkflowState -> WorkflowState -> Bool
canTransition Initial Batching = True
canTransition Batching (Preprocessing _ _) = True
canTransition (Preprocessing _ _) (Preprocessing _ _) = True
canTransition (Preprocessing _ _) Collecting = True
canTransition Collecting (Merging _ _) = True
canTransition (Merging _ _) (Merging _ _) = True
canTransition (Merging _ _) Completed = True
canTransition _ (Failed _) = True
canTransition _ _ = False

-- ============================================================
-- 전처리 워크플로우 스펙
-- ============================================================

-- 전처리 작업 인터페이스
public export
interface Monad m => PreprocessWorkflowSpec m where
    -- 파일 열기
    openDocument : String -> m Bool

    -- 1단 변환
    convertToSingleColumn : m Bool

    -- Para 스캔
    scanParas : m Nat

    -- 빈 Para 제거
    removeEmptyParas : m Nat

    -- 임시 파일 저장
    saveToTemp : String -> m Bool

    -- 문서 닫기
    closeDocument : m Bool

-- 단일 파일 전처리
public export
preprocessSingleFile : (Monad m, PreprocessWorkflowSpec m)
                    => ProblemFile
                    -> String  -- 임시 디렉토리
                    -> m (Either String ProcessedFile)
preprocessSingleFile problem tempDir = do
    -- 1. 파일 열기
    opened <- openDocument problem.path
    case opened of
        False => pure (Left "Failed to open file")
        True => do
            -- 2. 1단 변환
            _ <- convertToSingleColumn

            -- 3. Para 스캔 및 제거
            paraCount <- scanParas
            removed <- removeEmptyParas

            -- 4. 임시 파일 저장
            let processedPath = tempDir ++ "/processed_"
                            ++ show problem.index ++ ".hwp"
            saved <- saveToTemp processedPath

            -- 5. 문서 닫기
            _ <- closeDocument

            case saved of
                False => pure (Left "Failed to save")
                True => pure (Right $ MkProcessedFile {
                    original = problem,
                    processedPath = processedPath,
                    paraCount = paraCount,
                    emptyParasRemoved = removed
                })

-- ============================================================
-- 합병 워크플로우 스펙
-- ============================================================

-- 합병 작업 인터페이스
public export
interface Monad m => MergeWorkflowSpec m where
    -- 양식 열기
    openTemplate : String -> m Bool

    -- 문서 시작으로 이동
    moveToDocStart : m Bool

    -- InsertFile로 파일 삽입
    insertFile : String -> m Bool

    -- BreakColumn 실행
    breakColumn : m Bool

    -- 최종 저장
    saveDocument : String -> m Bool

    -- 페이지 수 확인
    getPageCount : m Nat

-- BreakColumn 대기 시간 (초)
public export
breakColumnDelay : Double
breakColumnDelay = 0.15

-- 순차 합병 워크플로우
public export
mergeProcessedFiles : (Monad m, MergeWorkflowSpec m)
                   => String                     -- 양식 경로
                   -> List ProcessedFile         -- 전처리된 파일들
                   -> String                     -- 출력 경로
                   -> m (Either String Nat)      -- Nat = 최종 페이지 수
mergeProcessedFiles templatePath files outputPath =
    let insertAllFiles : List ProcessedFile -> m (Either String Nat)
        insertAllFiles [] = pure (Right 0)
        insertAllFiles (f :: rest) = do
            -- InsertFile
            inserted <- insertFile f.processedPath
            case inserted of
                False => pure (Left "InsertFile failed")
                True => do
                    -- 마지막 파일이 아니면 BreakColumn
                    case rest of
                        [] => pure ()
                        _  => do
                            _ <- breakColumn
                            pure ()

                    -- 다음 파일 처리
                    insertAllFiles rest
    in do
        -- 1. 양식 열기
        opened <- openTemplate templatePath
        case opened of
            False => pure (Left "Failed to open template")
            True => do
                -- 2. 문서 시작으로
                _ <- moveToDocStart

                -- 3. 파일들 삽입
                result <- insertAllFiles files

                case result of
                    Left err => pure (Left err)
                    Right _ => do
                        -- 4. 최종 저장
                        saved <- saveDocument outputPath
                        case saved of
                            False => pure (Left "Failed to save")
                            True => do
                                -- 5. 페이지 수 반환
                                pages <- getPageCount
                                pure (Right pages)

-- ============================================================
-- 페이지 수 검증
-- ============================================================

-- 2로 나누기 (올림)
divBy2Ceil : Nat -> Nat
divBy2Ceil Z = Z
divBy2Ceil (S Z) = S Z
divBy2Ceil (S (S n)) = S (divBy2Ceil n)

-- 예상 페이지 수 계산
public export
expectedPageCount : List ProcessedFile -> Nat
expectedPageCount files = divBy2Ceil (length files)

-- 안전한 차이 계산
safeDiff : Nat -> Nat -> Nat
safeDiff Z y = y
safeDiff x Z = x
safeDiff (S x) (S y) = safeDiff x y

-- 페이지 수 검증 (±2 페이지 허용)
public export
validatePageCount : Nat -> Nat -> Bool
validatePageCount expected actual =
    let diff = safeDiff expected actual
    in diff <= 2

-- ============================================================
-- 성능 예측
-- ============================================================

-- 배치 개수 계산 (올림 나누기)
batchCountHelper : Nat -> Nat -> Nat
batchCountHelper Z _ = Z
batchCountHelper (S n) Z = S n  -- div by 0 방지
batchCountHelper fileCount (S k) =
    if fileCount <= S k
    then 1
    else S (batchCountHelper (assert_smaller fileCount (minus fileCount (S k))) (S k))

-- 20개씩 배치
batchCount20 : Nat -> Nat
batchCount20 files = batchCountHelper files 20

-- 전처리 시간 예측 (초)
-- 20개 병렬이므로 배치당 시간
public export
estimatePreprocessTime : Nat -> Double
estimatePreprocessTime fileCount =
    let batches : Nat = batchCount20 fileCount
        avgTimePerFile : Double = 1.5
    in cast batches * avgTimePerFile

-- 합병 시간 예측 (초)
-- InsertFile: 0.17초/파일
-- BreakColumn: 0.15초/구분
public export
estimateMergeTime : Nat -> Double
estimateMergeTime Z = 0.0
estimateMergeTime fileCount =
    let insertTime = cast fileCount * 0.17
        breakCount : Nat = case fileCount of
                        Z => Z
                        S n => n  -- fileCount - 1
        breakTime = cast breakCount * 0.15
    in insertTime + breakTime

-- 전체 예상 시간
public export
estimateTotalTime : Nat -> Double
estimateTotalTime fileCount =
    estimatePreprocessTime fileCount + estimateMergeTime fileCount

-- ============================================================
-- 예제: 40문항 처리
-- ============================================================

-- 40문항, 20개 워커:
-- - 전처리: 2배치 × 1.5초 = 3초
-- - 합병: 40 × 0.17초 + 39 × 0.15초 = 12.65초
-- - 총: 약 15.65초
public export
example40FilesTime : Double
example40FilesTime = estimateTotalTime 40
