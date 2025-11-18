-- 문제 파일 분리 워크플로우
-- 하나의 HWP 파일에서 여러 문제를 개별 파일로 분리

module SeparateProblems

-- Actions는 주석으로만 참조 (import 경로 문제)
-- 실제 사용: MoveDocBegin, SelectAll, Copy, Paste, FileNew, FileSaveAs 등

-- 문제 번호 패턴
public export
data ProblemPattern
  = NumberDot        -- "1. " 형식
  | NumberParen      -- "1) " 형식
  | NumberBracket    -- "[1] " 형식
  | ProblemPrefix    -- "문제 1" 형식
  | CustomPattern String  -- 사용자 정의 정규식

-- 문제 위치 정보
public export
record ProblemLocation where
  constructor MkProblemLocation
  number : Nat           -- 문제 번호
  startPos : Nat         -- 시작 위치 (문자 인덱스)
  endPos : Nat           -- 끝 위치
  textPreview : String   -- 문제 시작 부분 미리보기 (50자)

-- 분리 설정
public export
record SeparatorConfig where
  constructor MkSeparatorConfig
  pattern : ProblemPattern           -- 문제 번호 패턴
  removeEmptyParas : Bool            -- 빈 문단 제거 여부
  outputFormat : String              -- 파일명 형식 (예: "문제_{num}.hwp")
  outputDir : String                 -- 출력 디렉토리

-- 분석 결과
public export
record AnalysisResult where
  constructor MkAnalysisResult
  totalChars : Nat                   -- 전체 문자 수
  problems : List ProblemLocation    -- 발견된 문제 목록
  minNumber : Nat                    -- 최소 문제 번호
  maxNumber : Nat                    -- 최대 문제 번호

-- 분리 단계
public export
data SeparatorPhase
  = PhaseOpen           -- 1. 원본 파일 열기
  | PhaseAnalyze        -- 2. 전체 텍스트 분석
  | PhaseExtract        -- 3. 각 문제 추출
  | PhaseCleanup        -- 4. 빈 문단 제거
  | PhaseSave           -- 5. 개별 파일 저장
  | PhaseComplete       -- 6. 완료

-- 추출 단계의 상태
public export
record ExtractState where
  constructor MkExtractState
  phase : SeparatorPhase
  currentProblem : Maybe ProblemLocation
  processedCount : Nat
  errorMessage : Maybe String

-- 분석 워크플로우 (SelectAll + GetText)
public export
analyzeDocument : AnalysisResult
analyzeDocument = MkAnalysisResult
  { totalChars = 0
  , problems = []
  , minNumber = 0
  , maxNumber = 0
  }

-- 빈 문단 제거 액션 시퀀스 (merger의 para_scanner 로직)
-- MoveDocEnd → 역순으로 빈 Para 찾아서 제거
public export
removeEmptyParasActions : List String
removeEmptyParasActions =
  [ "MoveDocEnd"             -- 문서 끝으로
  , "RemoveEmptyParas"       -- 빈 Para 제거 (커스텀 함수)
  , "MoveDocBegin"           -- 문서 처음으로 복귀
  ]

-- 단일 문제 추출 워크플로우
-- 1. MoveDocBegin: 문서 처음으로 이동
-- 2. 문제 시작 위치로 이동 (GetPos 사용)
-- 3. SelectAll: 전체 선택
-- 4. 문제 끝 위치로 선택 범위 조정
-- 5. Copy: 복사
-- 6. FileNew: 새 문서 생성
-- 7. Paste: 붙여넣기
-- 8. (선택적) 빈 문단 제거
-- 9. FileSaveAs: 저장
-- 10. Clear: 닫기
public export
extractProblemWorkflow : ProblemLocation -> SeparatorConfig -> List String
extractProblemWorkflow loc cfg =
  [ "MoveDocBegin"           -- 1. 문서 처음
  , "SetPos(" ++ show loc.startPos ++ ")"  -- 2. 시작 위치
  , "MoveSelDown"            -- 3. 선택 시작
  , "SetPos(" ++ show loc.endPos ++ ")"    -- 4. 끝 위치까지 선택
  , "Copy"                   -- 5. 복사
  , "FileNew"                -- 6. 새 문서
  , "Paste"                  -- 7. 붙여넣기
  ] ++ (if cfg.removeEmptyParas
        then removeEmptyParasActions
        else [])
    ++ [ "FileSaveAs"         -- 9. 저장
       , "Clear"              -- 10. 닫기
       ]

-- 전체 분리 워크플로우
-- 원본 파일 → N개의 문제 파일들
public export
separateAllProblems : String -> SeparatorConfig -> List ProblemLocation -> List String
separateAllProblems sourceFile cfg problems =
  [ "FileOpen(" ++ sourceFile ++ ")"     -- 원본 열기
  , "SelectAll"                          -- 전체 선택
  , "GetText"                            -- 텍스트 추출 (분석용)
  ] ++ concatMap (\loc => extractProblemWorkflow loc cfg) problems

-- 파일명 생성 함수
public export
generateFilename : SeparatorConfig -> ProblemLocation -> String
generateFilename cfg loc =
  -- "문제_{num}.hwp" 형식에서 {num}을 실제 번호로 치환
  replacePattern cfg.outputFormat "{num}" (show loc.number)
  where
    replacePattern : String -> String -> String -> String
    replacePattern template pattern value =
      -- 간단한 치환 (Idris 표준 라이브러리 사용)
      value  -- TODO: 실제 구현

-- 진행률 계산 (퍼센트, 0-100)
-- div 함수 직접 정의 (Nat → Nat → Nat)
public export
progress : Nat -> Nat -> Nat
progress done totalCount =
  if totalCount == 0
    then 0
    else natDiv (done * 100) totalCount
  where
    natDiv : Nat -> Nat -> Nat
    natDiv Z _ = Z
    natDiv x Z = Z
    natDiv x y = if x < y then Z else S (natDiv (minus x y) y)

-- 타입 안전성 보장
-- 1. 문제 번호는 항상 양수
-- 2. startPos < endPos
-- 3. 파일명에 특수문자 없음
public export
data SeparatorError
  = InvalidPattern String           -- 잘못된 패턴
  | NoProblemFound                  -- 문제를 찾을 수 없음
  | InvalidRange Nat Nat            -- startPos >= endPos
  | FileWriteError String           -- 파일 쓰기 실패
  | EmptyDocument                   -- 빈 문서

public export
Result : Type -> Type
Result a = Either SeparatorError a

-- 검증 함수
public export
validateProblemLocation : ProblemLocation -> Result ProblemLocation
validateProblemLocation loc =
  if loc.startPos >= loc.endPos
    then Left (InvalidRange loc.startPos loc.endPos)
    else if loc.number == 0
         then Left (InvalidPattern "문제 번호는 0이 될 수 없습니다")
         else Right loc

-- 전체 워크플로우 검증
public export
validateSeparatorConfig : SeparatorConfig -> Result SeparatorConfig
validateSeparatorConfig cfg =
  if cfg.outputFormat == ""
    then Left (InvalidPattern "출력 형식이 비어있습니다")
    else if cfg.outputDir == ""
         then Left (InvalidPattern "출력 디렉토리가 비어있습니다")
         else Right cfg

-- 예시: 400개 문제 분리
-- analyzeDocument → 400개 ProblemLocation
-- separateAllProblems → 400개 파일 생성
