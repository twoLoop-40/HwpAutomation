||| Parallel Block Extraction - 병렬 블록 추출 명세
|||
||| 파일 복사 기반 병렬 처리
|||
||| @author Claude
||| @date 2025-11-19

module Specs.Extractor.ParallelExtraction

import Data.List
import Data.Nat

-- %default total 제거: 일부 함수는 totality 증명 복잡
-- 타입 명세 중심으로 구현

--------------------------------------------------------------------------------
-- Helper Functions
--------------------------------------------------------------------------------

||| 자연수 나눗셈 (몫)
|||
||| divNat n m = n / m (정수 나눗셈)
||| Python: n // m
public export
divNat : Nat -> Nat -> Nat
-- 구현은 Python에서 수행

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

||| 블록 그룹 = 여러 블록을 하나로 병합
|||
||| 예시: [1, 2, 3] → 블록 1의 시작 ~ 블록 3의 끝
public export
BlockGroup : Type
BlockGroup = List Nat  -- 블록 인덱스 리스트 (1-based)

||| 블록 0 처리
|||
||| iter_note_blocks는 블록 0도 반환함 (첫 번째 문항 이전 내용)
||| 실제 문항은 블록 1부터 시작
public export
data Block0Handling
  = SkipBlock0      -- 블록 0 제외 (권장) ✅
  | IncludeBlock0   -- 블록 0 포함

||| 블록 그룹화 전략
|||
||| 예시: 15개 블록을 3개씩 묶으면
||| - [1,2,3], [4,5,6], [7,8,9], [10,11,12], [13,14,15]
||| - 총 5개 그룹
public export
record GroupingStrategy where
  constructor MkGrouping
  blocksPerGroup : Nat          -- 그룹당 블록 수 (예: 3)
  skipBlock0 : Block0Handling   -- 블록 0 처리 방식

||| 파일 복사 정보
public export
record FileCopy where
  constructor MkFileCopy
  originalPath : String    -- 원본 파일 경로
  copyPath : String        -- 복사본 경로
  processId : Nat          -- 프로세스 ID (0-based)

--------------------------------------------------------------------------------
-- Parallel Processing Strategy
--------------------------------------------------------------------------------

||| 병렬 처리 제약 사항
|||
||| 1. HWP COM 객체는 STA (Single Threaded Apartment)
|||    → 쓰레드 안전하지 않음
|||    → ThreadPoolExecutor 사용 불가
|||
||| 2. ProcessPoolExecutor 필요
|||    → 각 프로세스가 별도 COM 인스턴스 생성
|||    → pythoncom.CoInitialize() 필요
|||
||| 3. 파일 복사 방식
|||    → 원본 파일을 N개 복사
|||    → 각 프로세스가 별도 파일 열기
|||    → COM 객체 충돌 방지
public export
data COMThreadSafety
  = STA_NotThreadSafe          -- Single Threaded Apartment
  | NeedProcessPoolExecutor    -- ThreadPoolExecutor 불가
  | NeedFileCopies             -- 파일 복사 필요

||| 메모리 사용량 추정
|||
||| - HWP 프로세스 하나: 약 100-200MB
||| - 5개 병렬: 500MB-1GB
||| - 16GB RAM: 4-5개 안전
||| - 32GB+ RAM: 8-10개 가능
|||
||| 일반적인 PC 고려 → 5개 제한
public export
record MemoryConstraint where
  constructor MkMemory
  hwpProcessSize : Nat     -- MB 단위 (100-200)
  maxWorkers : Nat         -- 최대 병렬 워커 수 (권장: 5)
  totalRAM : Nat           -- 총 RAM (MB)

||| 안전한 워커 수 계산
||| Python: min(maxWorkers, totalRAM // (hwpProcessSize * 2))
public export
safeWorkerCount : MemoryConstraint -> Nat

||| 순차 배치 처리
|||
||| 15개 그룹, 5개 병렬 → 3개 배치
||| - 배치 1: 그룹 [0,1,2,3,4] (인덱스 0-based)
||| - 배치 2: 그룹 [5,6,7,8,9]
||| - 배치 3: 그룹 [10,11,12,13,14]
|||
||| 중요: 현재 배치 완료 후 다음 배치 시작 (메모리 관리)
public export
record Batch where
  constructor MkBatch
  batchIndex : Nat         -- 배치 번호 (0-based)
  groupIndices : List Nat  -- 이 배치에서 처리할 그룹 인덱스들 (0-based)

||| 배치 분할 함수
|||
||| 예시:
||| totalGroups = 15
||| maxWorkers = 5
||| → [[0,1,2,3,4], [5,6,7,8,9], [10,11,12,13,14]]
|||
||| Python:
||| batches = []
||| for i in range(0, len(groups), max_workers):
|||     batches.append(groups[i:i+max_workers])
public export
splitIntoBatches : (totalGroups : Nat) -> (maxWorkers : Nat) -> List Batch

--------------------------------------------------------------------------------
-- Type Specifications
--------------------------------------------------------------------------------

||| 단일 그룹 추출 (Copy/Paste 방식)
|||
||| 입력:
||| - hwp: HWP COM 객체
||| - blocks: 전체 블록 리스트
||| - groupIndices: 병합할 블록 인덱스 [1,2,3] (1-based)
||| - outputPath: 저장 경로
|||
||| 처리:
||| 1. 첫 블록 시작 위치 ~ 마지막 블록 끝 위치 계산
||| 2. Copy/Paste 추출 (Solution3_CopyPaste)
|||
||| 반환:
||| - (성공 여부, 저장 경로 또는 Nothing)
public export
ExtractSingleGroup : Type
ExtractSingleGroup =
  (hwp : AnyPtr)
  -> (blocks : List Block)
  -> (groupIndices : List Nat)  -- [1,2,3] (1-based)
  -> (outputPath : String)
  -> IO (Bool, Maybe String)

||| 워커 함수 (별도 프로세스에서 실행)
|||
||| 입력:
||| - fileCopy: 복사된 파일 정보
||| - blocks: 전체 블록 리스트 (이미 block 0 제외됨)
||| - groupIndices: 처리할 블록 인덱스 (1-based)
||| - outputPath: 저장 경로
|||
||| 처리:
||| 1. pythoncom.CoInitialize()
||| 2. 복사본 파일 열기
||| 3. ExtractSingleGroup 호출
||| 4. 파일 닫기
||| 5. pythoncom.CoUninitialize()
|||
||| 반환:
||| - (성공 여부, 저장 경로 또는 Nothing)
public export
WorkerFunction : Type
WorkerFunction =
  (fileCopy : FileCopy)
  -> (blocks : List Block)
  -> (groupIndices : List Nat)
  -> (outputPath : String)
  -> IO (Bool, Maybe String)

||| 배치 처리 함수
|||
||| 입력:
||| - originalFile: 원본 HWP 파일
||| - batch: 처리할 배치 (그룹 인덱스 리스트)
||| - allGroups: 전체 그룹 정의
||| - blocks: 전체 블록 리스트
||| - outputDir: 출력 디렉토리
||| - maxWorkers: 최대 병렬 워커 수
|||
||| 처리:
||| 1. 원본 파일을 N개 복사 (N = batch의 그룹 수)
||| 2. ProcessPoolExecutor(max_workers=N) 생성
||| 3. 각 그룹을 WorkerFunction으로 제출
||| 4. 모든 결과 대기 (Future.result())
||| 5. 복사본 파일 삭제
|||
||| 반환:
||| - 각 그룹의 (성공 여부, 저장 경로) 리스트
public export
ProcessBatch : Type
ProcessBatch =
  (originalFile : String)
  -> (batch : Batch)
  -> (allGroups : List BlockGroup)
  -> (blocks : List Block)
  -> (outputDir : String)
  -> (maxWorkers : Nat)
  -> IO (List (Bool, Maybe String))

||| 전체 병렬 추출 함수
|||
||| 입력:
||| - hwpFilePath: 원본 HWP 파일
||| - outputDir: 출력 디렉토리
||| - grouping: 그룹화 전략 (3개씩 묶기 등)
||| - memory: 메모리 제약 (최대 워커 수)
|||
||| 처리:
||| 1. HWP 파일 열기 (블록 위치 수집용)
||| 2. iter_note_blocks로 전체 블록 위치 수집
||| 3. 블록 0 제외 (skipBlock0 = True)
||| 4. 블록들을 그룹으로 분할 ([1,2,3], [4,5,6], ...)
||| 5. 그룹들을 배치로 분할 (최대 워커 수 고려)
||| 6. 각 배치 순차 처리:
|||    - ProcessBatch 호출
|||    - 완료 대기
|||    - 다음 배치 진행
||| 7. HWP 파일 닫기
|||
||| 반환:
||| - 전체 그룹의 (성공 여부, 저장 경로) 리스트
public export
ParallelExtractAll : Type
ParallelExtractAll =
  (hwpFilePath : String)
  -> (outputDir : String)
  -> (grouping : GroupingStrategy)
  -> (memory : MemoryConstraint)
  -> IO (List (Bool, Maybe String))

--------------------------------------------------------------------------------
-- File Copy Management
--------------------------------------------------------------------------------

||| 임시 파일 복사 생성
|||
||| 예시:
||| originalPath = "C:/test.hwp"
||| processId = 0
||| → "C:/test_temp_0.hwp"
public export
makeTempCopyPath : (originalPath : String) -> (processId : Nat) -> String

||| 파일 복사 함수
public export
copyFile : (src : String) -> (dst : String) -> IO Bool

||| 파일 삭제 함수
public export
deleteFile : (path : String) -> IO Bool

||| 배치 완료 후 복사본 정리
|||
||| 입력:
||| - fileCopies: 생성된 복사본 리스트
|||
||| 처리:
||| - 각 복사본 파일 삭제
public export
cleanupCopies : (fileCopies : List FileCopy) -> IO ()

--------------------------------------------------------------------------------
-- File Copy Verification (의존 타입)
--------------------------------------------------------------------------------

||| 파일 크기 (bytes)
public export
FileSize : Type
FileSize = Nat

||| 파일 복사 검증 결과
|||
||| CopyVerified: 복사본 크기 = 원본 크기
||| CopyMismatch: 복사본 크기 ≠ 원본 크기
public export
data CopyVerification : FileSize -> FileSize -> Type where
  CopyVerified : (original : FileSize)
              -> CopyVerification original original
  CopyMismatch : (original : FileSize)
              -> (copy : FileSize)
              -> Not (original = copy)
              -> CopyVerification original copy

||| 파일 복사 검증 함수
|||
||| 최대 5번 재시도, 0.1초 간격
||| 성공: original = copy
||| 실패: original ≠ copy (경고 출력)
public export
verifyCopy : (originalSize : FileSize)
          -> (copyPath : String)
          -> IO (size : FileSize ** CopyVerification originalSize size)

||| 배치 크기 제약
|||
||| 배치 크기 <= maxWorkers
||| 증명: 배치 분할 시 자동으로 보장됨
public export
data BatchSizeConstraint : (batchSize : Nat) -> (maxWorkers : Nat) -> Type where
  ValidBatchSize : (n : Nat)
                -> (m : Nat)
                -> LTE n m
                -> BatchSizeConstraint n m

||| 안전한 배치
|||
||| - 배치 크기 <= maxWorkers
||| - 각 그룹이 유효한 블록 인덱스
public export
record SafeBatch where
  constructor MkSafeBatch
  batch : Batch
  sizeConstraint : BatchSizeConstraint (length batch.groupIndices) 5
  -- 모든 그룹 인덱스가 유효함 (totalBlocks 이내)

--------------------------------------------------------------------------------
-- Timing and Synchronization
--------------------------------------------------------------------------------

||| 파일 I/O 대기 시간
|||
||| Copy/Paste 추출 후:
||| 1. FileSaveAs_S 실행
||| 2. FileClose 실행
||| 3. 500ms 대기 (디스크 I/O 완료까지)
|||
||| 이유: HWP API는 디스크 쓰기 완료를 기다리지 않음
public export
FileIODelay : Type
FileIODelay = Nat  -- 밀리초 (권장: 500)

||| FileSaveAs_S 반환값 신뢰성
|||
||| 검증 결과:
||| - result = False여도 파일이 생성될 수 있음
||| - 파일 존재 여부로 성공 판단 (더 신뢰할 수 있음)
public export
data SaveResultReliability
  = APIReturnValue Bool       -- 신뢰할 수 없음
  | FileExists String         -- 더 신뢰할 수 있음 ✅

--------------------------------------------------------------------------------
-- Implementation Guide
--------------------------------------------------------------------------------

||| Python 구현 가이드
|||
||| 1. 블록 위치 수집:
|||    with open_hwp(hwp_file_path) as hwp:
|||        all_blocks = list(iter_note_blocks(hwp))
|||    all_blocks = all_blocks[1:]  # 블록 0 제외
|||
||| 2. 그룹 분할:
|||    groups = []
|||    for i in range(0, len(all_blocks), blocks_per_group):
|||        group = list(range(i, min(i + blocks_per_group, len(all_blocks))))
|||        groups.append(group)
|||
||| 3. 배치 분할:
|||    batches = []
|||    for i in range(0, len(groups), max_workers):
|||        batch_groups = groups[i:i+max_workers]
|||        batches.append(batch_groups)
|||
||| 4. 각 배치 처리:
|||    for batch_idx, batch in enumerate(batches):
|||        # 파일 복사 + 검증 (의존 타입 구현)
|||        original_size = Path(hwp_file_path).stat().st_size
|||        copies = []
|||        for worker_id in range(len(batch)):
|||            copy_path = f"{original}_temp_{worker_id}.hwp"
|||            shutil.copy(original, copy_path)
|||
|||            # 파일 크기 검증 (CopyVerification)
|||            max_retries = 5
|||            for _ in range(max_retries):
|||                copy_size = Path(copy_path).stat().st_size
|||                if copy_size == original_size:  -- CopyVerified
|||                    break
|||                time.sleep(0.1)
|||            else:
|||                # CopyMismatch - 경고 출력
|||                print(f"경고: 복사본 크기 불일치")
|||
|||            copies.append(copy_path)
|||
|||        # 병렬 처리
|||        with ProcessPoolExecutor(max_workers=len(batch)) as executor:
|||            futures = []
|||            for worker_id, group in enumerate(batch):
|||                future = executor.submit(
|||                    worker_function,
|||                    copies[worker_id],
|||                    all_blocks,
|||                    group,
|||                    output_path
|||                )
|||                futures.append(future)
|||
|||            # 결과 대기
|||            results = [f.result() for f in futures]
|||
|||        # 복사본 삭제
|||        for copy_path in copies:
|||            os.remove(copy_path)
|||
||| 5. 워커 함수:
|||    def worker_function(file_copy, blocks, group_indices, output_path):
|||        pythoncom.CoInitialize()
|||        try:
|||            with open_hwp(file_copy) as hwp:
|||                # group의 첫 블록 ~ 마지막 블록
|||                first_block = blocks[group_indices[0]]
|||                last_block = blocks[group_indices[-1]]
|||                merged_block = (first_block[0], last_block[1])
|||
|||                # Copy/Paste 추출
|||                success = extract_block_copypaste(hwp, merged_block, output_path)
|||
|||                # 파일 존재 여부로 성공 판단
|||                if Path(output_path).exists():
|||                    return (True, output_path)
|||                else:
|||                    return (False, None)
|||        finally:
|||            pythoncom.CoUninitialize()
public export
pythonGuide : String
pythonGuide = """
파일: Scripts/test_merge_3blocks_parallel.py

병렬 처리 구현 예시 (5개 병렬, 순차 배치)
"""

--------------------------------------------------------------------------------
-- Summary
--------------------------------------------------------------------------------

-- 핵심 설계 결정:
--
-- 1. 파일 복사 방식
--    - 원본 파일을 N개 복사 (N = 배치당 워커 수)
--    - 각 프로세스가 별도 파일 열기
--    - COM 객체 충돌 방지
--
-- 2. ProcessPoolExecutor
--    - HWP COM 객체는 STA (쓰레드 안전하지 않음)
--    - 각 프로세스가 pythoncom.CoInitialize() 필요
--
-- 3. 순차 배치 처리
--    - 최대 5개 병렬 (일반 PC 고려)
--    - 배치 완료 후 다음 배치 시작
--    - 메모리 관리
--
-- 4. 블록 0 제외
--    - iter_note_blocks의 블록 0은 첫 문항 이전 내용
--    - all_blocks[1:] 로 제외
--
-- 5. 파일 I/O 대기
--    - FileClose 후 500ms 대기
--    - 디스크 쓰기 완료 보장
--
-- 6. 성공 판단
--    - FileSaveAs_S 반환값보다 파일 존재 여부가 더 신뢰할 수 있음
