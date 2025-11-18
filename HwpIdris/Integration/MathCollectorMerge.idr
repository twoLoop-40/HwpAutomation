-- MathCollectorMerge.idr
-- AutoHwp 병합 기능을 math-collector 프로젝트에 통합하는 형식 명세
--
-- 목적: math-collector의 단순 병합을 AutoHwp의 고급 전처리+병합으로 대체
-- 추가: HwpIdris 형식 명세도 함께 이동하여 타입 안전성 문서화

module HwpIdris.Integration.MathCollectorMerge

import Data.List
import Data.String

-- ═══════════════════════════════════════════════════════════════
-- 1. 프로젝트 구조 비교
-- ═══════════════════════════════════════════════════════════════

||| math-collector 현재 구조
data MathCollectorProject : Type where
  ||| 검색 모듈: CSV 기반 문제 검색
  SearchNodes : MathCollectorProject
  ||| 메인 워크플로우: LangGraph 기반
  MainNodes : MathCollectorProject
  ||| HWP 처리: 개별 추출 + 단순 병합
  ToolsHandleHwp : MathCollectorProject
  ||| UI: tkinter 기반
  UI : MathCollectorProject

||| math-collector의 병합 방식
data CombineProblemsStrategy : Type where
  ||| 단순 InsertFile만 사용
  ||| - 전처리 없음
  ||| - 빈 Para 제거 없음
  ||| - 단 변환 없음
  SimpleInsertFile : CombineProblemsStrategy

||| AutoHwp의 병합 방식
data AutoHwpMergeStrategy : Type where
  ||| 고급 전처리 + Copy/Paste
  ||| - 1단 변환: convert_to_single_column
  ||| - 빈 Para 제거: remove_empty_paras (역순)
  ||| - Copy/Paste 방식
  ||| - BreakColumn 삽입
  AdvancedPreprocessAndMerge : AutoHwpMergeStrategy

-- ═══════════════════════════════════════════════════════════════
-- 2. 파일 이동 명세
-- ═══════════════════════════════════════════════════════════════

||| 복사할 AutoHwp 모듈
data AutoHwpModule : Type where
  ||| AppV1 디렉토리 전체 (12 파일)
  AppV1Dir : AutoHwpModule
  ||| src/automation/ (AutomationClient)
  SrcAutomation : AutoHwpModule
  ||| src/common/ (types, sync)
  SrcCommon : AutoHwpModule
  ||| HwpIdris/ (Idris2 형식 명세, 20+ 파일)
  HwpIdrisDir : AutoHwpModule

||| 대상 위치 (math-collector 기준)
data TargetLocation : Type where
  ||| hwp_merger/ (새로 생성)
  HwpMergerDir : TargetLocation
  ||| src/automation/ (기존 src 없음, 새로 생성)
  SrcAutomationDir : TargetLocation
  ||| src/common/
  SrcCommonDir : TargetLocation
  ||| .specs/HwpIdris/ (기존 .specs 활용)
  SpecsHwpIdrisDir : TargetLocation

||| 파일 복사 명세
record FileCopySpec where
  constructor MkFileCopySpec
  source : String       -- AutoHwp 경로
  target : String       -- math-collector 경로
  moduleType : AutoHwpModule
  purpose : String      -- 복사 목적

||| 전체 복사 계획
copyPlan : List FileCopySpec
copyPlan = [
  -- AppV1 → hwp_merger
  MkFileCopySpec
    "AutoHwp/AppV1/"
    "math-collector/hwp_merger/"
    AppV1Dir
    "메인 병합 로직 (merger.py, integrated_merger.py, parallel_workflow.py 등)",

  -- src/automation
  MkFileCopySpec
    "AutoHwp/src/automation/"
    "math-collector/src/automation/"
    SrcAutomation
    "HWP Automation API 클라이언트 (AutomationClient)",

  -- src/common
  MkFileCopySpec
    "AutoHwp/src/common/"
    "math-collector/src/common/"
    SrcCommon
    "공통 타입 및 유틸리티 (HwpResult, sync)",

  -- HwpIdris → .specs/HwpIdris
  MkFileCopySpec
    "AutoHwp/HwpIdris/"
    "math-collector/.specs/HwpIdris/"
    HwpIdrisDir
    "Idris2 형식 명세 (Actions, ParameterSets, Automation, 워크플로우)"
]

-- ═══════════════════════════════════════════════════════════════
-- 3. HwpIdris 디렉토리 구조
-- ═══════════════════════════════════════════════════════════════

||| HwpIdris 하위 모듈
data HwpIdrisModule : Type where
  ||| Actions/ (12개 파일)
  ||| - Navigation.idr, Selection.idr, Text.idr, File.idr 등
  ActionsModule : HwpIdrisModule

  ||| ParameterSets/ (7개 파일)
  ||| - ColDef.idr, CharShape.idr, ParaShape.idr 등
  ParameterSetsModule : HwpIdrisModule

  ||| Automation/ (OLE Object Model)
  AutomationModule : HwpIdrisModule

  ||| 워크플로우 명세
  ||| - OneColOneProblem.idr
  ||| - AppV1/MergeProblemFiles.idr
  ||| - ActionTable.idr
  WorkflowSpecs : HwpIdrisModule

  ||| 추출 데이터
  ||| - *_extracted.txt (PDF 파싱 결과)
  ||| - API_Index.md, MoveSel_commands.txt
  ExtractedData : HwpIdrisModule

||| HwpIdris 복사 후 위치
|||
||| math-collector/.specs/HwpIdris/
||| ├── Actions/           # HWP 액션 타입 정의
||| ├── ParameterSets/     # 파라미터 타입 정의
||| ├── Automation/        # Automation API 명세
||| ├── AppV1/             # 병합 워크플로우
||| ├── OneColOneProblem.idr
||| ├── ActionTable.idr
||| └── API_Index.md
hwpIdrisLocation : String
hwpIdrisLocation = ".specs/HwpIdris/"

||| HwpIdris 복사 이유
data HwpIdrisCopyReason : Type where
  ||| 1. 타입 안전성 문서화
  ||| - 모든 HWP API가 Idris2 타입으로 정의됨
  TypeSafetyDoc : HwpIdrisCopyReason

  ||| 2. Python 구현 참조
  ||| - AppV1 구현 시 HwpIdris 참조
  ImplementationRef : HwpIdrisCopyReason

  ||| 3. API 검색 용이성
  ||| - PDF보다 .idr 파일이 검색하기 쉬움
  EasySearch : HwpIdrisCopyReason

  ||| 4. 워크플로우 명세
  ||| - MergeProblemFiles.idr이 전체 로직 설명
  WorkflowSpec : HwpIdrisCopyReason

-- ═══════════════════════════════════════════════════════════════
-- 4. Import 경로 변경
-- ═══════════════════════════════════════════════════════════════

||| 기존 AutoHwp import
data AutoHwpImport : Type where
  ||| from src.automation.client import AutomationClient
  FromSrcAutomation : AutoHwpImport
  ||| from src.common.sync import wait_for_hwp_ready
  FromSrcCommonSync : AutoHwpImport
  ||| from .types import ProblemFile, ProcessResult
  FromAppV1Types : AutoHwpImport

||| math-collector로 이동 후 import (변경 불필요)
||| 이유: 동일한 상대 경로 유지
|||   - hwp_merger/merger.py → from src.automation.client (동일)
|||   - hwp_merger/types.py → from .types (동일)
data MathCollectorImport : Type where
  ||| from src.automation.client import AutomationClient
  ||| (math-collector/src/automation/client.py)
  SameAsAutoHwp : MathCollectorImport

||| Import 변경 필요 여부
needsImportChange : AutoHwpImport -> Bool
needsImportChange _ = False  -- 상대 경로 구조 동일하므로 변경 불필요

-- ═══════════════════════════════════════════════════════════════
-- 5. 통합 후 디렉토리 구조
-- ═══════════════════════════════════════════════════════════════

||| 통합 후 math-collector 구조
|||
||| math-collector/
||| ├── .specs/              # 기존: Idris2 형식 명세
||| │   ├── HwpIdris/        # 신규: AutoHwp 타입 명세
||| │   │   ├── Actions/
||| │   │   ├── ParameterSets/
||| │   │   ├── Automation/
||| │   │   └── AppV1/
||| │   ├── GRAPH_ANALYSIS.md
||| │   └── README.md
||| ├── main_nodes/          # 기존: LangGraph 워크플로우
||| ├── search_nodes/        # 기존: 검색 로직
||| ├── tools/
||| │   └── handle_hwp.py   # 기존: 단순 병합
||| ├── hwp_merger/          # 신규: AutoHwp 고급 병합
||| │   ├── merger.py
||| │   ├── integrated_merger.py
||| │   ├── parallel_workflow.py
||| │   ├── parallel_preprocessor.py
||| │   ├── preprocessor.py
||| │   ├── para_scanner.py
||| │   ├── column.py
||| │   ├── page_setup.py
||| │   ├── file_inserter.py
||| │   ├── types.py
||| │   └── __init__.py
||| └── src/                 # 신규: HWP API 클라이언트
|||     ├── automation/
|||     │   ├── client.py
|||     │   ├── tools.py
|||     │   └── __init__.py
|||     └── common/
|||         ├── types.py
|||         ├── sync.py
|||         └── __init__.py
data IntegratedStructure : Type where
  ||| 기존 기능
  ExistingFeatures : (search : MathCollectorProject)
                  -> (tools : MathCollectorProject)
                  -> (specs : String)  -- .specs/ (기존)
                  -> IntegratedStructure

  ||| 새로 추가된 AutoHwp 병합
  NewMergeFeature : (hwpMerger : String)     -- hwp_merger/
                 -> (srcAuto : String)       -- src/automation/
                 -> (srcCommon : String)     -- src/common/
                 -> (hwpIdris : String)      -- .specs/HwpIdris/
                 -> IntegratedStructure

-- ═══════════════════════════════════════════════════════════════
-- 6. 사용 시나리오
-- ═══════════════════════════════════════════════════════════════

||| 사용자가 선택할 수 있는 병합 방식
data MergeOption : Type where
  ||| 기존 방식: tools.handle_hwp.combine_problems()
  ||| - 빠름
  ||| - 전처리 없음
  UseLegacyMerge : MergeOption

  ||| AutoHwp 방식: hwp_merger.integrated_merger.IntegratedMerger
  ||| - 느림 (전처리 시간)
  ||| - 깨끗한 결과 (빈 Para 제거, 1단 변환)
  ||| - .specs/HwpIdris/ 참조하여 구현됨
  UseAutoHwpMerge : MergeOption

||| 병합 워크플로우
data MergeWorkflow : Type where
  ||| 1. CSV 검색 → 문제 추출 (기존)
  SearchAndExtract : List String -> MergeWorkflow

  ||| 2. 병합 방식 선택 (신규)
  SelectMergeStrategy : MergeOption -> MergeWorkflow

  ||| 3a. 기존 방식 실행
  ExecuteLegacy : MergeWorkflow

  ||| 3b. AutoHwp 방식 실행
  ||| - .specs/HwpIdris/AppV1/MergeProblemFiles.idr 참조
  ExecuteAutoHwp : (preprocess : Bool) -> (parallel : Bool) -> MergeWorkflow

||| 예시: AutoHwp 병합 사용
|||
||| # HwpIdris 명세 참조
||| # .specs/HwpIdris/AppV1/MergeProblemFiles.idr
||| # .specs/HwpIdris/Actions/Navigation.idr
|||
||| from hwp_merger.integrated_merger import IntegratedMerger
|||
||| merger = IntegratedMerger(
|||     template_path="[양식].hwp",
|||     csv_path="problems.csv"
||| )
||| merger.merge_all_parallel()  # 병렬 전처리 + 순차 병합
exampleUsage : String
exampleUsage = """
# math-collector UI에서 선택
if use_advanced_merge:
    from hwp_merger.integrated_merger import IntegratedMerger
    merger = IntegratedMerger(template_path, csv_path)
    merger.merge_all_parallel()
else:
    from tools.handle_hwp import combine_problems
    combine_problems(target_list)

# HWP API 참조 시
# .specs/HwpIdris/Actions/ 에서 필요한 액션 찾기
# .specs/HwpIdris/ParameterSets/ 에서 파라미터 확인
"""

-- ═══════════════════════════════════════════════════════════════
-- 7. 의존성 검증
-- ═══════════════════════════════════════════════════════════════

||| AutoHwp 의존성
data AutoHwpDependency : Type where
  ||| pywin32 (HWP COM)
  PyWin32 : AutoHwpDependency
  ||| pathlib, typing, time (표준 라이브러리)
  StdLib : AutoHwpDependency
  ||| Idris2 (형식 명세, 런타임 불필요)
  Idris2Spec : AutoHwpDependency

||| math-collector 의존성
data MathCollectorDependency : Type where
  ||| pywin32 (이미 있음)
  ExistingPyWin32 : MathCollectorDependency
  ||| LangChain, LangGraph
  LangChain : MathCollectorDependency
  ||| tkinter
  Tkinter : MathCollectorDependency
  ||| Idris2 (이미 .specs에 사용 중)
  ExistingIdris2 : MathCollectorDependency

||| 의존성 충돌 검사
checkDependencyConflict : AutoHwpDependency -> MathCollectorDependency -> Bool
checkDependencyConflict PyWin32 ExistingPyWin32 = False  -- 충돌 없음
checkDependencyConflict Idris2Spec ExistingIdris2 = False  -- 충돌 없음
checkDependencyConflict _ _ = False

||| 추가 설치 필요 여부
needsAdditionalInstall : Bool
needsAdditionalInstall = False  -- pywin32, Idris2 모두 이미 있음

-- ═══════════════════════════════════════════════════════════════
-- 8. HwpIdris 활용 방법
-- ═══════════════════════════════════════════════════════════════

||| HwpIdris 참조 시나리오
data HwpIdrisUsage : Type where
  ||| 1. API 검색
  ||| - 라인 이동이 필요하면 .specs/HwpIdris/Actions/Navigation.idr 확인
  SearchAPI : String -> HwpIdrisUsage

  ||| 2. 파라미터 확인
  ||| - 단 설정이 필요하면 .specs/HwpIdris/ParameterSets/ColDef.idr 확인
  CheckParameter : String -> HwpIdrisUsage

  ||| 3. 워크플로우 이해
  ||| - 병합 로직 전체 흐름은 .specs/HwpIdris/AppV1/MergeProblemFiles.idr
  UnderstandWorkflow : HwpIdrisUsage

  ||| 4. 타입 안전성 검증
  ||| - Python 구현이 Idris 명세와 일치하는지 확인
  VerifyTypeSafety : HwpIdrisUsage

||| HwpIdris 파일 탐색 예시
|||
||| # 필요한 기능: 라인별 텍스트 읽기
||| → .specs/HwpIdris/Actions/Navigation.idr 확인
||| → MoveLineDown, MoveLineBegin 발견
||| → Python에서 구현
|||
||| # 필요한 기능: 단 설정
||| → .specs/HwpIdris/ParameterSets/ColDef.idr 확인
||| → Count, SameGap 등 속성 확인
||| → Python에서 구현
hwpIdrisExample : String
hwpIdrisExample = """
작업 순서:
필요한 기능 확인
  ↓
.specs/HwpIdris/에서 타입 검색 (*.idr 파일)
  ↓
Python 구현 (hwp_merger/ 또는 src/)
  ↓
테스트 작성 및 실행
"""

-- ═══════════════════════════════════════════════════════════════
-- 9. 통합 검증
-- ═══════════════════════════════════════════════════════════════

||| 검증 항목
data ValidationItem : Type where
  ||| Import 경로가 올바른가?
  ValidateImports : ValidationItem
  ||| AutomationClient가 정상 동작하는가?
  ValidateAutomationClient : ValidationItem
  ||| 병합이 정상 동작하는가?
  ValidateMerge : ValidationItem
  ||| 기존 math-collector 기능이 여전히 동작하는가?
  ValidateExistingFeatures : ValidationItem
  ||| HwpIdris 파일이 올바른 위치에 있는가?
  ValidateHwpIdrisLocation : ValidationItem

||| 통합 검증 절차
record IntegrationValidation where
  constructor MkValidation
  items : List ValidationItem
  status : ValidationItem -> Bool

||| 검증 계획
validationPlan : IntegrationValidation
validationPlan = MkValidation
  [ ValidateImports
  , ValidateAutomationClient
  , ValidateMerge
  , ValidateExistingFeatures
  , ValidateHwpIdrisLocation
  ]
  (\_ => True)  -- 모두 통과 예상

-- ═══════════════════════════════════════════════════════════════
-- 10. 최종 이점
-- ═══════════════════════════════════════════════════════════════

||| 통합 이점
data IntegrationBenefit : Type where
  ||| math-collector: 검색 + 추출 (기존 기능)
  SearchAndExtractBenefit : IntegrationBenefit

  ||| AutoHwp: 전처리 + 고급 병합 (신규 기능)
  AdvancedMergeBenefit : IntegrationBenefit

  ||| HwpIdris: 타입 안전 문서화 (신규)
  TypeSafetyDocBenefit : IntegrationBenefit

  ||| 선택 가능: 빠른 병합 vs 깨끗한 병합
  ChoiceFlexibility : IntegrationBenefit

  ||| 코드 재사용: 중복 제거
  CodeReuse : IntegrationBenefit

  ||| API 검색 용이: HwpIdris 참조
  EasyAPISearch : IntegrationBenefit

||| 최종 결론
|||
||| AutoHwp의 AppV1 + src + HwpIdris를 math-collector로 복사하면
||| 두 프로젝트의 장점을 모두 활용할 수 있다.
|||
||| - 충돌 없음 (의존성, import 경로)
||| - 선택적 사용 (기존 병합 vs AutoHwp 병합)
||| - 최소 변경 (import 경로 동일)
||| - 타입 안전 문서화 (HwpIdris)
conclusion : String
conclusion = """
복사 계획:
1. AutoHwp/AppV1/          → math-collector/hwp_merger/
2. AutoHwp/src/automation/ → math-collector/src/automation/
3. AutoHwp/src/common/     → math-collector/src/common/
4. AutoHwp/HwpIdris/       → math-collector/.specs/HwpIdris/

변경 사항:
- Import 경로: 변경 불필요 (구조 동일)
- 의존성: 추가 설치 불필요 (pywin32, Idris2 이미 있음)
- .specs: 기존 .specs에 HwpIdris 추가

결과:
- math-collector: 검색/추출 + 단순 병합 (기존)
- AutoHwp 병합: 전처리 + 고급 병합 (신규)
- HwpIdris 명세: 타입 안전 문서화 (신규)
- 사용자 선택 가능
- API 참조 용이 (.specs/HwpIdris/*.idr)

통계:
- 복사 파일: AppV1 (12), src (8), HwpIdris (20+) = 40+ 파일
- 디스크 사용: ~500KB (코드) + ~2MB (HwpIdris 명세)
- 추가 의존성: 없음
"""

-- ═══════════════════════════════════════════════════════════════
-- 11. 실행 계획
-- ═══════════════════════════════════════════════════════════════

||| 복사 실행 단계
data CopyStep : Type where
  ||| 1. 디렉토리 생성
  CreateDirectories : List String -> CopyStep

  ||| 2. 파일 복사
  CopyFiles : FileCopySpec -> CopyStep

  ||| 3. 검증
  Validate : ValidationItem -> CopyStep

||| 실행 순서
executionOrder : List CopyStep
executionOrder = [
  CreateDirectories ["hwp_merger", "src/automation", "src/common", ".specs/HwpIdris"],
  CopyFiles (MkFileCopySpec "AutoHwp/AppV1/" "math-collector/hwp_merger/" AppV1Dir "병합 로직"),
  CopyFiles (MkFileCopySpec "AutoHwp/src/automation/" "math-collector/src/automation/" SrcAutomation "API 클라이언트"),
  CopyFiles (MkFileCopySpec "AutoHwp/src/common/" "math-collector/src/common/" SrcCommon "공통 유틸"),
  CopyFiles (MkFileCopySpec "AutoHwp/HwpIdris/" "math-collector/.specs/HwpIdris/" HwpIdrisDir "형식 명세"),
  Validate ValidateImports,
  Validate ValidateMerge
]
