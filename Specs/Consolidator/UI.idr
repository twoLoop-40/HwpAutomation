module Consolidator.UI

import Consolidator.Types

%default total

-- Folder Consolidator UI 워크플로우 명세
-- 간결한 4단계 흐름

||| UI 상태 (4단계 + Initial/Closed)
public export
data UIState : Type where
  Initial : UIState           -- 초기 상태
  SelectingSources : UIState  -- 1단계: 여러 폴더 선택
  SelectingTarget : UIState   -- 2단계: 결과 폴더 선택/생성
  ChoosingMode : UIState      -- 3단계: 복사/이동 선택
  Processing : UIState        -- 4단계: 실행 중
  ShowingResult : UIState     -- 5단계: 결과 표시
  Closed : UIState            -- 종료

||| UI 액션 (각 단계별)
public export
data UIAction : Type where
  SelectMultipleFolders : UIAction  -- 1. 소스 폴더 다중 선택 (Ctrl+클릭)
  SelectOrCreateTarget : UIAction   -- 2. 대상 폴더 선택 또는 생성
  ChooseCopyOrMove : UIAction       -- 3. 복사/이동 모드 선택
  ExecuteConsolidation : UIAction   -- 4. 작업 실행
  ShowCompletionMessage : UIAction  -- 5. 완료 메시지 표시
  Exit : UIAction                   -- 6. 종료 (Closed로 전환)

||| UI 상태 전환 규칙
public export
transition : UIState -> UIAction -> UIState
transition Initial SelectMultipleFolders = SelectingSources
transition SelectingSources SelectOrCreateTarget = SelectingTarget
transition SelectingTarget ChooseCopyOrMove = ChoosingMode
transition ChoosingMode ExecuteConsolidation = Processing
transition Processing ShowCompletionMessage = ShowingResult
transition ShowingResult Exit = Closed
transition _ _ = Closed  -- 잘못된 전환 또는 취소 시 종료

||| 정상 워크플로우 (6단계)
|||
||| 흐름:
||| 1. 여러 폴더 선택 (Ctrl+클릭으로 동시 선택)
||| 2. 결과 폴더 선택/생성 (폴더 브라우저 또는 새 폴더 생성)
||| 3. 복사/이동 선택 (2개 버튼 중 선택)
||| 4. 실행 (진행 표시 + 병렬 처리)
||| 5. 완료 메시지 (성공/실패 통계)
||| 6. 종료
public export
normalFlow : List UIAction
normalFlow =
  [ SelectMultipleFolders     -- 1. 소스 선택
  , SelectOrCreateTarget      -- 2. 대상 선택
  , ChooseCopyOrMove          -- 3. 모드 선택
  , ExecuteConsolidation      -- 4. 실행
  , ShowCompletionMessage     -- 5. 결과
  , Exit                      -- 6. 종료
  ]

||| 워크플로우 길이 검증 (6단계)
public export
flowLengthProof : List.length Consolidator.UI.normalFlow = 6
flowLengthProof = Refl
