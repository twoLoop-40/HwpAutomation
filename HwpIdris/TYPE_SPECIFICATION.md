# HWP Automation 전체 타입 명세

HwpIdris 디렉토리의 Idris2 형식 명세 전체 개요

---

## 목차

1. [Action Table](#1-action-table)
2. [Automation Objects](#2-automation-objects)
3. [ParameterSets](#3-parametersets)
4. [워크플로우 명세](#4-워크플로우-명세)
5. [AppV1 명세](#5-appv1-명세)

---

## 1. Action Table

**위치**: `HwpIdris/Actions/*.idr` (12 modules, 1,279 actions)
**참조 문서**: `HwpBooks/ActionTable_2504.pdf`
**용도**: `hwp.Run()` 명령어 타입 안전 호출

### 주요 액션 모듈

| 모듈 | 파일 | 주요 액션 | 설명 |
|------|------|----------|------|
| File | `Actions/File.idr` | FileNew, FileOpen, FileSave, FileClose | 파일 조작 (23개) |
| Text | `Actions/Text.idr` | **InsertFile**, **BreakColumn**, **BreakSection**, Delete | 텍스트/삽입 (70+개) |
| Navigation | `Actions/Navigation.idr` | MoveDocBegin, MoveParaEnd, MoveSelDown | 커서 이동 |
| Format | `Actions/Format.idr` | PageSetup, ColDef, ParaShape, CharShape | 서식 |
| Table | `Actions/Table.idr` | TableCreate, CellBorderFill | 표 조작 |
| Selection | `Actions/Selection.idr` | Select, SelectAll, Cancel | 선택 영역 |
| FindReplace | `Actions/FindReplace.idr` | RepeatFind, Replace | 찾기/바꾸기 |
| Document | `Actions/Document.idr` | InsertText, GetText | 문서 조작 |
| Shape | `Actions/Shape.idr` | ShapeObjDialog, PictureWizard | 개체 |
| Field | `Actions/Field.idr` | InsertFieldHyperlink, FieldCode | 필드 |
| Misc | `Actions/Misc.idr` | ViewOptionDialog, ToolOptionsDialog | 기타 |

### 핵심 액션 타입

#### InsertFile (파일 끼워넣기)

```idris
-- HwpIdris/Actions/Text.idr
data TextAction
    = ...
    | InsertFile  -- 끼워 넣기
    | ...

-- ParameterSet: HInsertFile
-- 필수 파라미터:
--   - FileName : String (파일 경로)
--   - FileFormat : String (파일 형식, 예: "HWP")
--   - KeepSection : Int (0: 구역 정보 무시, 1: 유지)
```

**동작 방식** (검증 결과):
- 파일 내용을 **문서 끝**에 삽입
- 커서 위치는 **변경하지 않음** (GetPos() 동일)
- 각 파일을 **별도 List**로 분리 (List 0, 1, 2, ...)
- `KeepSection=0`: 원본 파일의 단 구성 무시

#### BreakColumn (칼럼 나누기)

```idris
-- HwpIdris/Actions/Text.idr
data TextAction
    = BreakColDef    -- 단 정의 삽입
    | BreakColumn    -- 단 나누기
    | BreakPage      -- 쪽 나누기
    | BreakPara      -- 문단 나누기
    | BreakSection   -- 구역 나누기
```

**동작 조건** (추정):
- **같은 List 내**에서만 작동?
- 2단 구성이 이미 설정된 문서에서만?
- InsertFile로 삽입된 파일들(별도 List)에서는 작동 안 함?

**검증 결과** (5개 파일 테스트):
- `hwp.Run("BreakColumn")` 실행 시 칼럼 구분 0개
- 파일들이 List 0~4로 분리됨
- 예상: BreakColumn은 같은 List 내 Para에서만 작동

#### BreakSection (구역 나누기)

```idris
data TextAction
    = ...
    | BreakSection  -- 구역 나누기
```

**ParameterSet**: `HSecDef` (구역 속성)
**용도**: 페이지 설정이 다른 섹션 생성

---

## 2. Automation Objects

**위치**: `HwpIdris/Automation/Objects.idr`
**참조 문서**: `HwpBooks/HwpAutomation_2504.pdf`
**용도**: OLE Object Model 타입 정의 (93개 객체)

### 주요 Object 계층

```idris
-- 최상위 객체
data AutomationObject
    = IHwpObject             -- 최상위 Automation Object (hwp)
    | IXHwpDocuments         -- 문서 Collection Object
    | IXHwpDocument          -- 단일 문서 Object
    | IXHwpWindow            -- 창 Object
    | IXHwpSelection         -- 선택 영역 Object
    | IXHwpRange             -- 범위 Object
    | IXHwpFind              -- 찾기 Object
    | IXHwpPrint             -- 인쇄 Object
    | IXHwpCharacterShape    -- 글자 모양 Object
    | IXHwpParagraphShape    -- 문단 모양 Object
    | ...
```

### Object 계층 구조

```
IHwpObject (hwp)
├── XHwpDocuments (hwp.XHwpDocuments)
│   └── Item(n) → IXHwpDocument
├── XHwpWindows (hwp.XHwpWindows)
│   └── Item(n) → IXHwpWindow
├── HAction (hwp.HAction)
│   ├── GetDefault(ActionID, ParameterSet)
│   └── Execute(ActionID, ParameterSet)
├── HParameterSet (hwp.HParameterSet)
│   ├── HInsertFile
│   ├── HColDef
│   ├── HSecDef
│   └── ...
└── 속성/메서드
    ├── PageCount : Nat
    ├── EditMode : Int
    ├── GetPos() : (Nat, Nat, Nat)
    ├── SetPos(List, Para, Pos)
    ├── GetText() : String
    └── Run(ActionID)
```

### 주요 속성 및 메서드

```idris
-- 문서 위치 (List, Para, Pos)
public export
record HwpPosition where
    constructor MkHwpPosition
    list : Nat  -- List 번호 (0부터 시작)
    para : Nat  -- Para 번호 (0부터 시작)
    pos  : Nat  -- Para 내 문자 위치 (0부터 시작)

-- GetPos() : (Nat, Nat, Nat)
-- SetPos(list, para, pos) : Bool
```

**List 개념**:
- HWP 문서는 여러 List로 구성
- 각 List는 독립적인 컨텍스트
- InsertFile은 각 파일을 **새 List**로 삽입
- BreakColumn은 **같은 List 내**에서만 작동 (추정)

---

## 3. ParameterSets

**위치**: `HwpIdris/ParameterSets/*.idr`
**참조 문서**: `HwpBooks/ParameterSet_extracted.txt`
**용도**: HAction.Execute() 파라미터 타입 정의

### 주요 ParameterSet

| ParameterSet | 파일 | 용도 | 관련 액션 |
|-------------|------|------|----------|
| HInsertFile | `ParameterSets/InsertFile.idr` | 파일 삽입 파라미터 | InsertFile |
| HColDef | `ParameterSets/ColDef.idr` | 단 정의 속성 | ColDef, BreakColDef |
| HSecDef | `ParameterSets/SecDef.idr` | 구역 속성 | PageSetup, BreakSection |
| HCharShape | `ParameterSets/CharShape.idr` | 글자 모양 | CharShape |
| HParaShape | `ParameterSets/ParaShape.idr` | 문단 모양 | ParaShape |
| HBorderFill | `ParameterSets/BorderFill.idr` | 테두리/배경 | CellBorderFill |
| HFieldCtrl | `ParameterSets/FieldCtrl.idr` | 필드 컨트롤 | InsertField* |

### InsertFile ParameterSet 상세

```python
# Python 구현 예시
hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
insert_params = hwp.HParameterSet.HInsertFile

# 필수 파라미터
insert_params.HSet.SetItem("FileName", str(file_path.absolute()))
insert_params.HSet.SetItem("FileFormat", "HWP")
insert_params.HSet.SetItem("KeepSection", 0)  # 0: 구역 무시, 1: 유지

# 실행
result = hwp.HAction.Execute("InsertFile", insert_params.HSet)
```

**KeepSection 파라미터**:
- `0`: 원본 파일의 구역 정보 무시 (기본값)
- `1`: 원본 파일의 구역 정보 유지

**문제점** (검증 결과):
- `KeepSection=0`으로 설정 시 2단 구성이 무시됨
- 각 파일이 별도 List로 삽입되어 BreakColumn이 작동하지 않음

### ColDef ParameterSet 상세

```idris
-- HwpIdris/ParameterSets/ColDef.idr
public export
record ColDefParams where
    constructor MkColDefParams
    -- 단 개수
    columnCount : Nat
    -- 단 사이 간격
    columnGap : Double
    -- 단 구분선
    columnLine : Bool
```

**용도**:
- 2단, 3단 등 다단 레이아웃 설정
- PageSetup 액션과 함께 사용

---

## 4. 워크플로우 명세

### 4.1 MergeWorkflow (Specs/MergeWorkflow.idr)

Copy/Paste 기반 합병 워크플로우

```idris
-- 워크플로우 단계
data WorkflowStep
    = Step1_OpenSource String         -- 원본 파일 열기
    | Step2_ConvertToSingle           -- 1단으로 변환
    | Step3_RemoveEmptyParas Nat      -- 빈 Para 제거
    | Step4_CopyContent               -- 내용 복사
    | Step5_CloseSource               -- 원본 닫기
    | Step6_CreateTarget              -- 대상 문서 생성
    | Step7_ConfigureTarget           -- B4 + 2단 설정
    | Step8_PasteContent Nat Nat      -- 붙여넣기 (페이지, 칼럼)
    | Step9_BreakColumn               -- 칼럼 구분
    | Step10_SaveTarget String        -- 결과 저장

-- 상태 전환
data TargetState
    = TargetNotCreated
    | TargetCreated
    | TargetConfigured
    | TargetReady Nat Nat             -- (page, column)
    | TargetInserted Nat Nat Nat      -- (page, column, count)
    | TargetSaved String

-- Step9_BreakColumn 상태 전환
transitionTarget (TargetInserted page col n) Step9_BreakColumn =
    if col == 2
        then Just (TargetReady (page + 1) 1)  -- 다음 페이지 첫 칼럼
        else Just (TargetReady page (col + 1))  -- 같은 페이지 다음 칼럼
```

### 4.2 TemplateMerge (Specs/TemplateMerge.idr)

양식 기반 합병 워크플로우

```idris
-- 칼럼 위치 계산
-- SetPos(0, 1 + 2*(N-1), 0) for Nth column
columnParaNumber : Nat -> Nat
columnParaNumber Z = 1        -- 첫 번째 칼럼: Para 1
columnParaNumber (S n) = 1 + 2 * (S n)  -- N번째 칼럼: Para 1 + 2*(N-1)

-- BreakColumn 개수 계산
breakColumnsNeeded : Nat -> Nat
breakColumnsNeeded Z = Z
breakColumnsNeeded (S n) = n  -- N개 칼럼 = N-1번 BreakColumn

-- 제약 조건
useBreakColumnNotMoveNext : String
useBreakColumnNotMoveNext =
    "MoveNextColumn fails. Use BreakColumn to create next column"

neverBreakPage : String
neverBreakPage =
    "BreakPage corrupts endnote page. Expand Page 1 with BreakColumn only"
```

**핵심 제약**:
- BreakColumn 사용 (MoveNextColumn 실패)
- BreakPage 절대 금지 (2페이지 미주 보존)
- SetPos로 칼럼 위치 이동

---

## 5. AppV1 명세

### 5.1 MergeProblemFiles (HwpIdris/AppV1/MergeProblemFiles.idr)

Copy/Paste 기반 문항 합병 애플리케이션

```idris
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

-- 워크플로우 인터페이스
public export
interface Monad m => MergeWorkflowSpec m where
    loadTemplate : String -> m Bool
    createNewDocument : m Bool
    convertToSingleColumn : m Bool
    scanParas : m (List ParaInfo)
    removeEmptyParas : List ParaInfo -> m Nat
    copyAll : m Bool
    paste : m Bool
    breakColumn : m Bool
    saveDocument : String -> m Bool
    getPageCount : m Nat

-- 단일 문항 처리
processSingleProblem : (Monad m, MergeWorkflowSpec m)
                     => ProblemFile -> m ProcessResult

-- 전체 합병
mergeProblemFiles : (Monad m, MergeWorkflowSpec m)
                  => MergeConfig -> m (Either String Nat)

-- 페이지 수 검증
expectedPageCount : List ProblemFile -> Nat
expectedPageCount files = divBy2Ceil (length files)

validatePageCount : Nat -> Nat -> Bool
validatePageCount expected actual =
    let diff = safeDiff expected actual
    in diff <= 2  -- ±2 페이지 허용
```

### 5.2 ParallelMerge (HwpIdris/AppV1/ParallelMerge.idr)

**InsertFile 기반 병렬 처리 워크플로우** (현재 구현 중)

```idris
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

-- BreakColumn 대기 시간 (초)
public export
breakColumnDelay : Double
breakColumnDelay = 0.15

-- 전처리 워크플로우
public export
interface Monad m => PreprocessWorkflowSpec m where
    openDocument : String -> m Bool
    convertToSingleColumn : m Bool
    scanParas : m Nat
    removeEmptyParas : m Nat
    saveToTemp : String -> m Bool
    closeDocument : m Bool

-- 합병 워크플로우
public export
interface Monad m => MergeWorkflowSpec m where
    openTemplate : String -> m Bool
    moveToDocStart : m Bool
    insertFile : String -> m Bool  -- InsertFile 액션
    breakColumn : m Bool           -- BreakColumn 액션
    saveDocument : String -> m Bool
    getPageCount : m Nat

-- 순차 합병 (InsertFile 기반)
mergeProcessedFiles : (Monad m, MergeWorkflowSpec m)
                   => String                     -- 양식 경로
                   -> List ProcessedFile         -- 전처리된 파일들
                   -> String                     -- 출력 경로
                   -> m (Either String Nat)      -- Nat = 최종 페이지 수

-- 성능 예측
estimateMergeTime : Nat -> Double
estimateMergeTime fileCount =
    let insertTime = cast fileCount * 0.17   -- InsertFile: 0.17초/파일
        breakCount = fileCount - 1
        breakTime = cast breakCount * 0.15   -- BreakColumn: 0.15초/구분
    in insertTime + breakTime

-- 예제: 40문항 약 15.65초
example40FilesTime : Double
example40FilesTime = estimateTotalTime 40
```

**핵심 특징**:
- 병렬 전처리 (최대 20개 동시)
- 순차 InsertFile 합병
- LangGraph Send 패턴 지원

---

## 6. 타입 안전성 보장

### 6.1 상태 전환 검증

```idris
-- 워크플로우 상태 전환 검증
public export
canTransition : WorkflowState -> WorkflowState -> Bool

-- 올바른 전환만 허용
canTransition NotStarted TemplateLoaded = True
canTransition TemplateLoaded (ProcessingProblems _ _) = True
canTransition (ProcessingProblems _ _) AllProcessed = True
canTransition AllProcessed Saved = True
canTransition _ (Failed _) = True  -- 언제든 실패 가능
canTransition _ _ = False  -- 그 외 전환 금지
```

### 6.2 페이지 수 계산

```idris
-- 2로 나누기 (올림)
divBy2Ceil : Nat -> Nat
divBy2Ceil Z = Z
divBy2Ceil (S Z) = S Z  -- 1 / 2 = 1 (올림)
divBy2Ceil (S (S n)) = S (divBy2Ceil n)  -- (n+2) / 2 = 1 + (n / 2)

-- 안전한 차이 계산 (Nat용)
safeDiff : Nat -> Nat -> Nat
safeDiff Z y = y
safeDiff x Z = x
safeDiff (S x) (S y) = safeDiff x y
```

---

## 7. 현재 이슈 및 조사 필요 사항

### 7.1 InsertFile + BreakColumn 동기화 문제

**증상** (5개 파일 테스트):
- InsertFile 실행 시 각 파일이 별도 List (0~4)로 삽입됨
- BreakColumn이 작동하지 않음 (칼럼 구분 0개)
- 예상 4페이지 → 실제 5페이지

**가설**:
1. **InsertFile 커서 위치 문제**: GetPos() 변화 없음
2. **KeepSection=0 문제**: 단 구성 무시
3. **List 분리 문제**: BreakColumn은 같은 List 내에서만 작동?

**조사 필요**:
- `HwpAutomation_2504.pdf`에서 InsertFile 정확한 동작 명세
- BreakColumn 사용 조건 및 제약사항
- InsertFile 대안 (Copy/Paste, 직접 텍스트 삽입 등)

### 7.2 동기화 개선

**현재 구현**:
```python
from src.common.sync import wait_for_hwp_ready

def insert_file_and_break_column(hwp, file_path, is_last):
    # 1. InsertFile 실행
    hwp.HAction.Execute("InsertFile", ...)

    # 2. InsertFile 완료 대기
    if not wait_for_hwp_ready(hwp, timeout=5.0):
        return False

    # 3. 문서 끝으로 이동
    hwp.Run("MoveDocEnd")
    if not wait_for_hwp_ready(hwp, timeout=2.0):
        return False

    # 4. BreakColumn (마지막 제외)
    if not is_last:
        hwp.Run("BreakColumn")
        if not wait_for_hwp_ready(hwp, timeout=3.0):
            return False

    return True
```

**wait_for_hwp_ready() 로직**:
```python
def wait_for_hwp_ready(hwp, timeout=5.0, check_interval=0.1):
    while time.time() - start_time < timeout:
        try:
            # EditMode 또는 PageCount 접근 가능하면 준비 완료
            if hasattr(hwp, 'EditMode'):
                _ = hwp.EditMode
                return True

            if hasattr(hwp, 'PageCount'):
                _ = hwp.PageCount
                return True

            return True
        except Exception:
            # COM 객체가 바쁘면 예외 발생
            time.sleep(check_interval)
            continue

    return False
```

**성능**:
- 전처리: 69.5초 (기존 72.7초에서 3.2초 개선)
- 삽입: 0.8초 (기존 1.6초에서 50% 개선)
- 하지만 여전히 칼럼 구분 문제 존재

---

## 8. 참조 문서

### HWP API 문서
- `HwpBooks/ActionTable_2504.pdf`: Action Table 전체 목록
- `HwpBooks/HwpAutomation_2504.pdf`: Automation API 전체 목록
- `HwpBooks/ParameterSet_extracted.txt`: ParameterSet 목록

### Idris2 명세
- `HwpIdris/ActionTable.idr`: Action Table 기본 타입
- `HwpIdris/Actions/*.idr`: 12개 액션 모듈 (1,279개 액션)
- `HwpIdris/Automation/Objects.idr`: 93개 Automation Object
- `HwpIdris/ParameterSets/*.idr`: ParameterSet 타입
- `HwpIdris/AppV1/MergeProblemFiles.idr`: Copy/Paste 기반 합병
- `HwpIdris/AppV1/ParallelMerge.idr`: InsertFile 기반 병렬 합병

### 분석 문서
- `Schema/InsertFile_Sync_Analysis.md`: InsertFile + BreakColumn 동기화 분석
- `HwpIdris/API_Index.md`: HWP API 전체 인덱스
- `HwpIdris/ParameterSets/Index.md`: ParameterSet 인덱스

### 테스트 파일
- `Tests/AppV1/test_insertfile_5files.py`: InsertFile 5개 파일 테스트
- `Tests/AppV1/test_insertfile_debug.py`: 커서 위치 디버깅
- `Tests/AppV1/verify_column_layout.py`: 칼럼 레이아웃 검증

---

## 9. 전체 타입 계층 다이어그램

```
HWP COM API
├── ActionTable API (hwp.Run, hwp.HAction)
│   ├── File Actions (23)
│   ├── Text Actions (70+)
│   │   ├── InsertFile
│   │   ├── BreakColumn
│   │   ├── BreakSection
│   │   └── ...
│   ├── Navigation Actions
│   ├── Format Actions
│   └── ...
│
├── Automation API (hwp.속성/메서드)
│   ├── IHwpObject (hwp)
│   │   ├── XHwpDocuments
│   │   ├── XHwpWindows
│   │   ├── HAction
│   │   ├── HParameterSet
│   │   │   ├── HInsertFile
│   │   │   ├── HColDef
│   │   │   ├── HSecDef
│   │   │   └── ...
│   │   ├── PageCount
│   │   ├── EditMode
│   │   ├── GetPos()
│   │   ├── SetPos()
│   │   └── GetText()
│   └── IXHwpDocument
│       ├── Path
│       ├── Modified
│       └── ...
│
├── Idris2 형식 명세
│   ├── ActionTable.idr
│   ├── Actions/*.idr (12 modules)
│   ├── Automation/Objects.idr
│   ├── ParameterSets/*.idr
│   └── AppV1/*.idr
│
└── Python 구현
    ├── src/action_table/
    ├── src/automation/
    ├── src/common/
    │   ├── types.py
    │   └── sync.py (wait_for_hwp_ready)
    └── AppV1/
        ├── file_inserter.py
        ├── column.py
        ├── para_scanner.py
        └── types.py
```

---

## 10. 빠른 참조

### InsertFile 사용법

```python
# 파일 삽입
hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
insert_params = hwp.HParameterSet.HInsertFile
insert_params.HSet.SetItem("FileName", str(file_path.absolute()))
insert_params.HSet.SetItem("FileFormat", "HWP")
insert_params.HSet.SetItem("KeepSection", 0)

result = hwp.HAction.Execute("InsertFile", insert_params.HSet)
```

### BreakColumn 사용법

```python
# 칼럼 나누기
hwp.Run("BreakColumn")

# 또는
hwp.HAction.Run("BreakColumn")
```

### 동기화 대기

```python
from src.common.sync import wait_for_hwp_ready

# HWP 준비 상태 대기
if wait_for_hwp_ready(hwp, timeout=5.0):
    print("준비 완료")
else:
    print("시간 초과")
```

### 문서 위치 확인

```python
# 현재 위치 (List, Para, Pos)
pos = hwp.GetPos()
print(f'List={pos[0]}, Para={pos[1]}, Pos={pos[2]}')

# 위치 이동
hwp.SetPos(0, 1, 0)  # List 0, Para 1, Pos 0
```

---

**작성일**: 2025-11-14
**버전**: 1.0
**기반 코드**: HwpIdris 전체 + AppV1 구현
