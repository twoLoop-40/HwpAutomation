||| HWP Extractor - EndNote 기반 문제 추출
|||
||| math-collector의 검증된 로직을 기반으로 한
||| HWP 파일에서 개별 문제 추출 시스템
|||
||| @author Claude
||| @date 2025-11-19

module HwpExtractor

import Data.List
import Data.String

%default total

--------------------------------------------------------------------------------
-- Core Types
--------------------------------------------------------------------------------

||| HWP 위치 (List, Para, Pos)
public export
record HwpPosition where
  constructor MkPos
  list : Nat
  para : Nat
  pos : Nat

||| 블록 = (시작 위치, 끝 위치)
public export
Block : Type
Block = (HwpPosition, HwpPosition)

||| EndNote 정보
public export
record EndNoteInfo where
  constructor MkEndNote
  number : Nat           -- EndNote 번호 (1부터 시작)
  position : HwpPosition -- 본문에서의 앵커 위치
  ctrlID : String        -- "en" (EndNote)

||| 추출 결과
public export
data ExtractResult = Success String | Failure String

||| 파일 형식
public export
data FileFormat = HWP | HWPX

--------------------------------------------------------------------------------
-- Core Operations
--------------------------------------------------------------------------------

||| EndNote 앵커를 순회하며 블록 생성
|||
||| 핵심 패턴 (math-collector 검증됨):
||| 1. HeadCtrl로 EndNote 순회
||| 2. GetAnchorPos(0)로 본문 앵커 위치 얻기
||| 3. 이전 앵커 ~ 현재 앵커 = 하나의 블록
public export
iter_note_blocks : (hwp : AnyPtr) -> List Block
-- hwp.Run("MoveDocBegin")
-- start = hwp.GetPos()
-- ctrl = hwp.HeadCtrl
-- while ctrl:
--   if ctrl.CtrlID == 'en':
--     pset = ctrl.GetAnchorPos(0)
--     end = (pset.Item("List"), pset.Item("Para"), pset.Item("Pos"))
--     yield (start, end)
--     start = end
--   ctrl = ctrl.Next
-- hwp.Run("MoveDocEnd")
-- yield (start, hwp.GetPos())

||| 전체 블록 개수 반환
public export
get_block_count : (hwp : AnyPtr) -> Nat
get_block_count hwp = length (iter_note_blocks hwp)

||| 인덱스로 블록 가져오기 (1-based)
public export
get_block_by_idx : (hwp : AnyPtr) -> (idx : Nat) -> Maybe Block
get_block_by_idx hwp idx =
  if idx == 0
    then Nothing
    else case drop (idx - 1) (iter_note_blocks hwp) of
           [] => Nothing
           (block :: _) => Just block

||| 블록 선택
|||
||| hwp.SetPos(*start)
||| hwp.Run("Select")
||| hwp.SetPos(*end)
public export
select_block : (hwp : AnyPtr) -> Block -> IO ()

||| 선택된 블록을 파일로 저장
|||
||| FileSaveAs_S 액션 사용:
||| hwp.HAction.GetDefault("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
||| hwp.HParameterSet.HFileOpenSave.filename = filepath
||| hwp.HParameterSet.HFileOpenSave.Format = "HWP"
||| hwp.HParameterSet.HFileOpenSave.Attributes = 1
||| hwp.HAction.Execute("FileSaveAs_S", hwp.HParameterSet.HFileOpenSave.HSet)
public export
save_block : (hwp : AnyPtr) -> (filepath : String) -> (fmt : FileFormat) -> IO Bool

--------------------------------------------------------------------------------
-- File Path Generation
--------------------------------------------------------------------------------

||| 파일 경로 생성 규칙
public export
record PathConfig where
  constructor MkPathConfig
  src : String              -- 문제 이름 (예: "2022_내신기출_3")
  file_id : Nat             -- 파일 ID (origin_num)
  out_dir : Maybe String    -- 출력 디렉토리 (None이면 현재 디렉토리)
  csv_filename : Maybe String -- CSV 파일명 (폴더명 결정용)
  format : FileFormat       -- 파일 형식

||| 저장 경로 생성
|||
||| 규칙:
||| - out_dir 있으면: out_dir/src_file_id.ext
||| - csv_filename 있으면: csv_파일명/src_file_id.ext
||| - 둘 다 없으면: ./src_file_id.ext
public export
make_hwp_path : PathConfig -> String

--------------------------------------------------------------------------------
-- High-Level API
--------------------------------------------------------------------------------

||| 클로저 패턴 (math-collector 검증됨)
|||
||| select_and_save(hwp, idx, origin_num, ...) -> (src -> (Bool, Path))
|||
||| 이유: 블록을 미리 선택해두고, 나중에 src로 파일명 결정
public export
record SaveClosure where
  constructor MkSaveClosure
  hwp : AnyPtr
  block : Block
  config : PathConfig

||| 클로저 실행: src를 받아서 저장
public export
execute_save : SaveClosure -> String -> IO (Bool, String)
execute_save closure src = do
  select_block closure.hwp closure.block
  let path = make_hwp_path (record { src = src } closure.config)
  result <- save_block closure.hwp path (closure.config.format)
  pure (result, path)

||| 클로저 생성
public export
select_and_save : (hwp : AnyPtr)
               -> (idx : Nat)
               -> (origin_num : Nat)
               -> (csv_filename : Maybe String)
               -> (out_dir : Maybe String)
               -> Maybe SaveClosure
select_and_save hwp idx origin_num csv_filename out_dir = do
  block <- get_block_by_idx hwp idx
  let config = MkPathConfig "" origin_num out_dir csv_filename HWP
  pure $ MkSaveClosure hwp block config

||| 단일 문제 추출 (최상위 API)
|||
||| @param hwp_file_path HWP 파일 경로
||| @param idx 블록 인덱스 (1-based)
||| @param src 문제 이름
||| @param origin_num 문제 고유 번호
||| @param output_dir 출력 디렉토리
public export
extract_problem : (hwp_file_path : String)
               -> (idx : Nat)
               -> (src : String)
               -> (origin_num : Nat)
               -> (output_dir : Maybe String)
               -> IO (Bool, Maybe String)
-- Python:
-- with open_hwp(hwp_file_path) as hwp:
--     saver = select_and_save(hwp, idx=idx, origin_num=origin_num, ...)
--     return saver(src)

--------------------------------------------------------------------------------
-- Batch Processing
--------------------------------------------------------------------------------

||| 배치 처리 전략
public export
data ProcessStrategy
  = Sequential     -- 순차 처리 (HWP 한 번만 열기)
  | Parallel Nat   -- 병렬 처리 (각각 HWP 열기, workers 수)

||| 단일 파일에서 모든 문제 추출
|||
||| Sequential: HWP를 한 번만 열고 모든 블록 순차 저장 (빠름, 권장)
||| Parallel: 각 블록마다 HWP를 열어서 병렬 저장 (느림, COM 충돌 가능)
public export
extract_all_problems : (hwp_file_path : String)
                    -> (output_dir : String)
                    -> (strategy : ProcessStrategy)
                    -> IO (Nat, Nat, List String)
                    -- (success_count, total_count, output_files)

-- Sequential 구현 (개선안: 블록 병합):
-- with open_hwp(hwp_file_path) as hwp:
--     blocks = list(iter_note_blocks(hwp))
--
--     for idx, block in enumerate(blocks, 1):
--         start, end = block
--         # 블록 선택 (시작 ~ 끝)
--         select_block(hwp, block)
--         save_block(hwp, make_path(...))
--
--     # 또는 여러 블록을 합쳐서 한 번에:
--     for group_indices in [[1,2,3], [4,5,6], ...]:
--         first_block_start = blocks[group_indices[0]-1][0]
--         last_block_end = blocks[group_indices[-1]-1][1]
--         merged_block = (first_block_start, last_block_end)
--         select_block(hwp, merged_block)
--         save_block(hwp, make_path(...))

-- Parallel 구현:
-- with ProcessPoolExecutor(max_workers=N) as executor:
--     futures = [executor.submit(extract_problem, ...) for idx in range(...)]
--     results = [f.result() for f in as_completed(futures)]

--------------------------------------------------------------------------------
-- Output Directory Management
--------------------------------------------------------------------------------

||| 출력 디렉토리 생성 규칙
public export
data OutputDirRule
  = CurrentDir                    -- 현재 디렉토리
  | SpecifiedDir String           -- 지정된 디렉토리
  | InputFileNameDir String       -- 입력 파일명으로 디렉토리 생성
  | CSVFileNameDir String         -- CSV 파일명으로 디렉토리 생성

||| 출력 디렉토리 경로 생성
public export
resolve_output_dir : OutputDirRule -> String

-- InputFileNameDir 예시:
-- 입력: "C:\...\6. 명제_2023.hwp"
-- 출력: "C:\...\6. 명제_2023\"

-- CSVFileNameDir 예시:
-- CSV: "문제집_20251115.csv"
-- 출력: "문제집_20251115\"

--------------------------------------------------------------------------------
-- Workflow
--------------------------------------------------------------------------------

||| 단일 파일 추출 워크플로우
public export
data ExtractWorkflow : Type where
  ||| 1. HWP 열기
  OpenFile : (path : String) -> ExtractWorkflow

  ||| 2. EndNote 탐색
  FindEndNotes : (hwp : AnyPtr) -> ExtractWorkflow

  ||| 3. 블록 추출
  ExtractBlocks : (hwp : AnyPtr) -> (blocks : List Block) -> ExtractWorkflow

  ||| 4. 파일 저장
  SaveFiles : (hwp : AnyPtr)
           -> (blocks : List Block)
           -> (output_dir : String)
           -> ExtractWorkflow

  ||| 5. HWP 닫기
  CloseFile : (hwp : AnyPtr) -> ExtractWorkflow

  ||| 완료
  Complete : (success_count : Nat)
          -> (total_count : Nat)
          -> (output_files : List String)
          -> ExtractWorkflow

||| 워크플로우 실행
public export
run_extract_workflow : (input_file : String)
                    -> (output_rule : OutputDirRule)
                    -> (strategy : ProcessStrategy)
                    -> IO ExtractWorkflow

--------------------------------------------------------------------------------
-- Integration with Separator Plugin
--------------------------------------------------------------------------------

||| Separator 플러그인 통합
|||
||| HWP 파일을 처리할 때:
||| 1. HwpParser가 EndNote 위치 찾기
||| 2. FileWriter가 각 블록을 save_block으로 저장
|||
||| HWPX 파일을 처리할 때:
||| 1. HwpxParser가 XML 파싱
||| 2. FileWriter가 텍스트 추출 후 저장
public export
data SeparatorBackend
  = HwpExtractorBackend   -- core/hwp_extractor.py 사용
  | XmlParserBackend      -- automations/separator/xml_parser.py 사용

||| Separator에서 사용할 추출 인터페이스
public export
interface SeparatorExtractor where
  ||| 파일 형식 감지
  detect_format : String -> FileFormat

  ||| 백엔드 선택
  select_backend : FileFormat -> SeparatorBackend

  ||| 문제 추출
  extract : (backend : SeparatorBackend)
         -> (input_file : String)
         -> (output_dir : String)
         -> IO (Nat, List String)

--------------------------------------------------------------------------------
-- Summary
--------------------------------------------------------------------------------

||| 전체 시스템 요약:
|||
||| 1. Core 추출 로직 (math-collector 검증됨)
|||    - iter_note_blocks: EndNote 순회
|||    - get_block_by_idx: 인덱스로 블록 가져오기
|||    - save_block: FileSaveAs_S로 저장
|||
||| 2. 클로저 패턴 (함수 반환)
|||    - select_and_save -> execute_save(src)
|||    - 블록 미리 선택 → 나중에 파일명 결정
|||
||| 3. 배치 처리
|||    - Sequential: HWP 한 번만 열기 (권장)
|||    - Parallel: 멀티프로세싱 (COM 충돌 주의)
|||
||| 4. 출력 디렉토리
|||    - 입력 파일명으로 폴더 자동 생성
|||    - CSV 파일명으로 폴더 생성
|||
||| 5. Separator 통합
|||    - HWP: HwpExtractorBackend (core/hwp_extractor.py)
|||    - HWPX: XmlParserBackend (xml_parser.py)
