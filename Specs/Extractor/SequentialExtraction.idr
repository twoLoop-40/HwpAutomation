||| Sequential Block Extraction - 순차 블록 추출 명세
|||
||| 발견한 문제와 해결책 정리
|||
||| @author Claude
||| @date 2025-11-19

module SequentialExtraction

import Data.List

%default total

--------------------------------------------------------------------------------
-- Base Types
--------------------------------------------------------------------------------

||| HWP 위치 (List, Para, Pos)
public export
HwpPosition : Type
HwpPosition = (Nat, Nat, Nat)

||| 블록 = (시작 위치, 끝 위치)
public export
Block : Type
Block = (HwpPosition, HwpPosition)

||| 제너레이터 (Python generator 추상화)
public export
Generator : Type -> Type
Generator a = List a  -- 단순화: Idris에서는 List로 표현

--------------------------------------------------------------------------------
-- Problem Analysis: FileSaveAs_S의 동작
--------------------------------------------------------------------------------

||| FileSaveAs_S 액션의 실제 동작
|||
||| 검증 결과:
||| 1. 선택 영역이 있으면 → 전체 문서를 저장 (예상과 다름!)
||| 2. 선택 영역이 없으면 → 전체 문서를 저장
||| 3. 첫 번째 저장 후 선택이 해제됨
|||
||| 증거:
||| - 홀수 파일 (1, 3, 5, ...): 15KB (빈 HWP 기본 크기)
||| - 짝수 파일 (2, 4, 6, ...): 3.2MB (전체 원본 파일)
|||
||| 결론: FileSaveAs_S는 블록 저장에 적합하지 않음
data FileSaveAsS_Behavior
  = SavesWholeDocument    -- 항상 전체 문서 저장
  | ClearsSelection       -- 저장 후 선택 해제

||| math-collector가 성공한 이유
|||
||| 1. 한 번에 한 블록만 처리 (extract_problem 함수)
||| 2. HWP를 매번 열고 닫음 (루프 없음)
||| 3. 따라서 "저장 후 선택 해제" 문제를 만나지 않음
data MathCollectorSuccess
  = OneBlockAtATime       -- 한 번에 한 블록
  | OpenCloseEachTime     -- HWP 매번 열고 닫기
  | NoLoopIssue           -- 루프 없음

--------------------------------------------------------------------------------
-- Core Data Types
--------------------------------------------------------------------------------

||| 블록 선택 범위
public export
record BlockSelection where
  constructor MkBlockSelection
  indices : List Nat  -- 선택할 블록 인덱스 (1-based)

||| 단일 블록 vs 여러 블록 병합
public export
data SelectionStrategy
  = SingleBlock Nat              -- 한 블록만 (idx)
  | MergedBlocks (List Nat)      -- 여러 블록 병합 ([1,2,3])
  | AllBlocks                    -- 전체 블록

||| 블록 추출 요청
public export
record ExtractionRequest where
  constructor MkRequest
  hwpFilePath : String           -- 원본 HWP 파일
  selection : SelectionStrategy  -- 추출할 블록들
  outputPath : String            -- 저장 경로

--------------------------------------------------------------------------------
-- Solutions
--------------------------------------------------------------------------------

||| 해결책 1: math-collector 방식 (각 블록마다 HWP 열고 닫기)
|||
||| 타입 명세:
||| - 입력: HWP 파일 경로, 추출할 블록 인덱스 리스트
||| - 출력: 각 블록의 성공 여부 + 저장 경로
|||
||| 장점: 안전하고 확실함
||| 단점: 느림 (N개 블록 = HWP를 N번 열어야 함)
public export
Solution1_MultipleOpen : Type
Solution1_MultipleOpen =
  (hwp_file_path : String)
  -> (selected_blocks : List Nat)  -- [1, 3, 5] = 1번, 3번, 5번 블록만
  -> IO (List (Bool, String))      -- [(성공여부, 저장경로), ...]

-- 예시:
-- solution1 "test.hwp" [1, 2, 3]
-- → [(True, "문제_001_1.hwp"), (True, "문제_002_2.hwp"), (True, "문제_003_3.hwp")]
--
-- 구현:
-- for idx in selected_blocks:
--     with open_hwp(hwp_file_path) as hwp:
--         block = get_block_by_idx(hwp, idx)
--         select_block(hwp, block)
--         result = save_block(hwp, make_path(idx))
--     # HWP 자동으로 닫힘

||| 해결책 2: 블록 위치를 미리 저장하고 순차 처리
|||
||| 타입 명세:
||| - 입력: HWP 객체, 추출할 블록 인덱스 리스트
||| - 출력: 각 블록의 성공 여부
|||
||| 1단계: iter_note_blocks로 모든 블록 위치 수집
||| 2단계: selected_blocks의 인덱스에 해당하는 블록만 선택 → 저장
|||
||| 문제: FileSaveAs_S가 선택 영역을 무시하고 전체 문서 저장
||| 상태: 실패 (이미 검증됨)
public export
Solution2_PositionList : Type
Solution2_PositionList =
  (hwp : AnyPtr)
  -> (selected_blocks : List Nat)     -- [1, 3, 5] = 1번, 3번, 5번만
  -> IO (List (Bool, String))         -- [(성공여부, 경로), ...]

-- 예시:
-- solution2 hwp [1, 3, 5]
-- → 1번, 3번, 5번 블록만 추출
--
-- 구현:
-- with open_hwp(hwp_file_path) as hwp:
--     all_blocks = list(iter_note_blocks(hwp))  -- 전체 블록 위치 수집
--
--     for idx in selected_blocks:
--         start, end = all_blocks[idx - 1]  -- 1-based → 0-based
--         hwp.SetPos(*start)
--         hwp.Run("Select")
--         hwp.SetPos(*end)
--         result = save_block(hwp, filepath)  -- 실패: 전체 문서 저장됨

||| 해결책 3: Copy/Paste 방식 (AppV1 Merger 패턴)
|||
||| 검증됨! 40문항 100% 성공
|||
||| 1. 블록 선택
||| 2. Copy
||| 3. 새 문서 생성
||| 4. Paste
||| 5. 새 문서 저장
|||
||| 장점: 확실하게 작동
||| 단점: 새 문서 생성 오버헤드
public export
Solution3_CopyPaste : Type
Solution3_CopyPaste =
  (hwp : AnyPtr)
  -> (block : Block)
  -> (filepath : String)
  -> IO Bool

-- hwp.SetPos(*start)
-- hwp.Run("Select")
-- hwp.SetPos(*end)
-- hwp.Run("Copy")
-- hwp.Run("FileNew")
-- hwp.Run("Paste")
-- hwp.HAction.Execute("FileSaveAs_S", ...)
-- hwp.Run("FileClose")

||| 해결책 4: SaveBlockAction 액션 사용
|||
||| HwpIdris/Actions/File.idr에서 발견:
||| - SaveBlockAction: 블록 저장 전용 액션
|||
||| 상태: 미검증 (테스트 필요)
public export
Solution4_SaveBlockAction : Type
Solution4_SaveBlockAction =
  (hwp : AnyPtr)
  -> (block : Block)
  -> (filepath : String)
  -> IO Bool

-- hwp.SetPos(*start)
-- hwp.Run("Select")
-- hwp.SetPos(*end)
-- hwp.HAction.GetDefault("SaveBlockAction", ...)
-- hwp.HAction.Execute("SaveBlockAction", ...)

--------------------------------------------------------------------------------
-- Generator Pattern (iter_note_blocks)
--------------------------------------------------------------------------------

||| iter_note_blocks 제너레이터의 특성
|||
||| 1. Lazy evaluation: 블록을 하나씩 yield
||| 2. list() 변환 시: 모든 블록을 소비하고 커서가 마지막으로 이동
||| 3. 각 yield 시점에서 HWP 커서 위치가 변함
|||
||| 주의사항:
||| - list(iter_note_blocks(hwp)) 후에는 커서가 문서 끝에 있음
||| - 다시 처음부터 처리하려면 새로 iter_note_blocks 호출 필요
public export
data GeneratorPattern
  = LazyYield              -- 하나씩 yield
  | CursorMoves            -- 각 yield마다 커서 이동
  | ListConsumesAll        -- list() 변환 시 전체 소비

||| 블록 위치 저장 방식
|||
||| 좋은 방법: 위치만 튜플로 저장
||| - blocks = [(list, para, pos), ...] 형태로 저장
||| - 나중에 hwp.SetPos(*pos)로 직접 이동 가능
|||
||| 나쁜 방법: 제너레이터를 list() 변환 후 순회
||| - 커서 위치가 마지막으로 가서 다시 처음부터 못 감
public export
data BlockStoragePattern
  = StorePositions (List (Nat, Nat, Nat))  -- ✅ 권장
  | StoreGenerator (Generator Block)        -- ❌ 재사용 불가

--------------------------------------------------------------------------------
-- Recommended Solution
--------------------------------------------------------------------------------

||| 최종 권장 방안
|||
||| 옵션 A: math-collector 방식 (안전)
||| - 각 블록마다 HWP 열고 닫기
||| - 느리지만 확실함
||| - 15개 블록 = 약 60초 예상
|||
||| 옵션 B: Copy/Paste 방식 (빠름)
||| - HWP 한 번만 열기
||| - iter_note_blocks로 블록 위치 yield
||| - 각 블록: 선택 → Copy → 새 문서 → Paste → 저장 → 닫기
||| - AppV1 Merger에서 검증됨 (40문항 100%)
|||
||| 선택: 옵션 B (Copy/Paste)
||| 이유: AppV1에서 이미 검증되었고, 성능도 좋음
public export
data RecommendedSolution
  = OptionA_MultipleOpen  -- 안전하지만 느림
  | OptionB_CopyPaste     -- 빠르고 검증됨 ✅

--------------------------------------------------------------------------------
-- Implementation Spec
--------------------------------------------------------------------------------

||| Copy/Paste 방식 구현 명세
public export
record CopyPasteExtractor where
  constructor MkExtractor

  ||| 1단계: HWP 파일 열기 (한 번만)
  openFile : (path : String) -> IO AnyPtr

  ||| 2단계: 블록 순회 (제너레이터)
  iterBlocks : (hwp : AnyPtr) -> Generator Block

  ||| 3단계: 단일 블록 추출 (Copy/Paste)
  extractBlock : (hwp : AnyPtr)
              -> (block : Block)
              -> (filepath : String)
              -> IO Bool
  -- hwp.SetPos(*start)
  -- hwp.Run("Select")
  -- hwp.SetPos(*end)
  -- hwp.Run("Copy")
  -- hwp.Run("FileNew")
  -- hwp.Run("Paste")
  -- hwp.FileSaveAs(filepath)
  -- hwp.Run("FileClose")

  ||| 4단계: 전체 워크플로우
  extractAll : (path : String)
            -> (output_dir : String)
            -> IO (Nat, Nat, List String)
  -- with openFile(path) as hwp:
  --     for idx, block in enumerate(iterBlocks(hwp), 1):
  --         extractBlock(hwp, block, make_path(idx))

--------------------------------------------------------------------------------
-- Summary
--------------------------------------------------------------------------------

-- 핵심 발견 사항:
--
-- 1. FileSaveAs_S는 블록 저장에 부적합
--    - 선택 영역 무시
--    - 전체 문서만 저장
--
-- 2. math-collector는 운이 좋았음
--    - 한 블록만 처리
--    - 루프 없음
--    - 선택 해제 문제 미발생
--
-- 3. 여러 블록 처리는 Copy/Paste 필요
--    - AppV1 Merger에서 검증됨
--    - 40문항 100% 성공
--
-- 4. iter_note_blocks는 제너레이터
--    - Lazy evaluation
--    - list() 변환 시 커서가 마지막으로 이동
--    - 위치만 저장하고 나중에 SetPos로 이동
