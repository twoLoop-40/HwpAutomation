"""
Script Organization - Scripts 디렉토리 구조 명세

목적:
- 74개의 스크립트를 체계적으로 분류
- 필요한 도구만 유지하고 나머지는 아카이브
- 카테고리별 명확한 구분

결정:
- 보존: 15개 (API 파싱, 유틸리티, 핵심 테스트)
- 삭제: 59개 (일회성, 구버전, 중복)
"""

module Specs.Tools.ScriptOrganization

%default total

-- ============================================================================
-- 스크립트 카테고리
-- ============================================================================

public export
data ScriptCategory
  = ApiParsing      -- PDF, API 문서 → Idris2 명세 생성
  | DevUtility      -- 개발 유틸리티 (kill_hwp, find_file)
  | CoreTest        -- core/ 모듈 테스트
  | AutomationTest  -- automations/ 플러그인 테스트
  | Deprecated      -- 일회성, 구버전, 중복

public export
Show ScriptCategory where
  show ApiParsing = "api_parsing"
  show DevUtility = "dev_utils"
  show CoreTest = "tests_core"
  show AutomationTest = "tests_automation"
  show Deprecated = "deprecated"

-- ============================================================================
-- 스크립트 메타데이터
-- ============================================================================

public export
record ScriptInfo where
  constructor MkScript
  filename : String
  category : ScriptCategory
  purpose : String
  keepReason : Maybe String  -- 보존 이유 (Nothing이면 삭제)

-- ============================================================================
-- 보존할 스크립트 (15개)
-- ============================================================================

-- API 파싱 도구 (7개)
public export
apiParsingScripts : List ScriptInfo
apiParsingScripts = [
  MkScript "extract_hwp_api.py" ApiParsing
    "HWP API PDF → Idris2 형식 추출"
    (Just "명세 생성 도구"),

  MkScript "parse_action_table.py" ApiParsing
    "ActionTable_extracted.txt → Idris2 주제별 명세"
    (Just "명세 생성 도구"),

  MkScript "parse_automation_api.py" ApiParsing
    "Automation API → Idris2 형식 파싱"
    (Just "명세 생성 도구"),

  MkScript "parse_eventhandler_pdf.py" ApiParsing
    "EventHandler PDF 파싱"
    (Just "API 문서화"),

  MkScript "parse_parameter_sets.py" ApiParsing
    "ParameterSet Table → Idris2 파싱"
    (Just "명세 생성 도구"),

  MkScript "extract_all_hwp_docs.py" ApiParsing
    "모든 HWP API 문서를 텍스트로 통합 추출"
    (Just "통합 문서화"),

  MkScript "split_pdf.py" ApiParsing
    "PDF 파일을 작은 파일로 분할"
    (Just "PDF 처리 유틸리티")
]

-- 개발 유틸리티 (2개)
public export
devUtilityScripts : List ScriptInfo
devUtilityScripts = [
  MkScript "kill_hwp.py" DevUtility
    "모든 HWP 프로세스 강제 종료"
    (Just "개발 중 필수 도구"),

  MkScript "find_file.py" DevUtility
    "문제 디렉토리에서 파일 검색"
    (Just "파일 검색 유틸리티")
]

-- Core 모듈 테스트 (3개)
public export
coreTestScripts : List ScriptInfo
coreTestScripts = [
  MkScript "test_copypaste_extraction.py" CoreTest
    "Copy/Paste 추출 방식 검증"
    (Just "core/hwp_extractor_copypaste.py 검증"),

  MkScript "test_hwp_extractor_full.py" CoreTest
    "core/hwp_extractor.py 전체 API 테스트"
    (Just "core API 완전 검증"),

  MkScript "test_merge_3blocks_parallel.py" CoreTest
    "3문항씩 병렬 추출 테스트"
    (Just "core/hwp_extractor_parallel.py 검증")
]

-- Automation 플러그인 테스트 (3개)
public export
automationTestScripts : List ScriptInfo
automationTestScripts = [
  MkScript "test_separator_full.py" AutomationTest
    "Separator 완전 테스트"
    (Just "automations/separator 전체 검증"),

  MkScript "test_separator_new.py" AutomationTest
    "새 Separator 로직 테스트"
    (Just "automations/separator 신규 기능 검증"),

  MkScript "test_separator_parser.py" AutomationTest
    "Separator XML 파서 테스트"
    (Just "automations/separator/xml_parser.py 검증")
]

-- ============================================================================
-- 보존할 스크립트 전체 목록
-- ============================================================================

public export
keepScripts : List ScriptInfo
keepScripts =
  apiParsingScripts ++
  devUtilityScripts ++
  coreTestScripts ++
  automationTestScripts

public export
totalKeepCount : Nat
totalKeepCount = length keepScripts
-- 예상: 15

-- ============================================================================
-- 삭제할 스크립트 (59개) - 카테고리별
-- ============================================================================

-- 일회성 분석 스크립트 (12개)
public export
deprecatedAnalysis : List String
deprecatedAnalysis = [
  "analyze_hwpx.py",
  "analyze_hwpx_detailed.py",
  "analyze_hwpx_structure.py",
  "analyze_problem_structure.py",
  "analyze_separator.py",       -- v2/v3로 대체
  "analyze_separator_v2.py",     -- v3로 대체
  "analyze_separator_v3.py",     -- automations/separator 구현
  "deep_ctrl_scan.py",
  "debug_gettext.py",
  "find_problem_numbers.py",
  "organize_hwp_docs.py",
  "compare_code.py"
]

-- 일회성 검증 스크립트 (11개)
public export
deprecatedChecks : List String
deprecatedChecks = [
  "check_all_22files.py",
  "check_all_hwp_endnotes.py",
  "check_block_content.py",
  "check_endnotes.py",
  "check_endnotes_answer.py",
  "check_math_collector_output.py",
  "check_mathcollector_hwp.py",
  "count_endnote_anchors.py",
  "count_endnotes_hwpx.py",
  "verify_output.py",
  "test_output_to_txt.py"
]

-- 일회성 추출/분리 실험 (9개)
public export
deprecatedExtract : List String
deprecatedExtract = [
  "extract_problems_from_hwpx.py",  -- automations/separator로 구현
  "extract_single_hwp.py",           -- automations/separator로 구현
  "find_endnote_anchors.py",
  "find_endnote_anchors_hwpx.py",
  "find_endnote_refs_hwpx.py",
  "find_endnotes_hwpx.py",
  "separate_body_endnotes.py",
  "separate_by_answer_pattern.py",
  "split_by_endnotes.py"
]

-- math-collector 복사/검증용 (12개)
public export
deprecatedMathCollector : List String
deprecatedMathCollector = [
  "test_block_save.py",
  "test_ebs_file.py",
  "test_full_workflow.py",
  "test_iter_note_blocks.py",
  "test_math_collector_exact.py",
  "test_mathcollector_method.py",
  "test_real_file.py",
  "test_with_mathcollector_copy.py",
  "test_with_saveblock.py",
  "separate_hwp_working.py",
  "merge_with_template.py",
  "test_preprocessed.py"
]

-- API 실험용 (4개)
public export
deprecatedApiExperiment : List String
deprecatedApiExperiment = [
  "goto_endnote.py",
  "scan_notes_action.py",
  "test_endnote_simple.py",
  "test_saveblock_action.py"
]

-- 기타 일회성 테스트 (11개)
public export
deprecatedOtherTests : List String
deprecatedOtherTests = [
  "test_complete_extraction.py",
  "test_file_finding.py",
  "test_hwp_separator.py",        -- test_separator_full.py로 대체
  "test_merge_3blocks.py",        -- test_merge_3blocks_parallel.py로 대체
  "test_single_block_extraction.py",
  "test_text_based_separator.py",
  "test_text_extraction.py",
  "find_file4.py",                -- find_file.py로 충분
  "separate_hwp_working.py"
]

-- ============================================================================
-- 삭제 대상 전체 목록
-- ============================================================================

public export
deleteScripts : List String
deleteScripts =
  deprecatedAnalysis ++
  deprecatedChecks ++
  deprecatedExtract ++
  deprecatedMathCollector ++
  deprecatedApiExperiment ++
  deprecatedOtherTests

public export
totalDeleteCount : Nat
totalDeleteCount = length deleteScripts
-- 예상: 59

-- ============================================================================
-- 새 디렉토리 구조
-- ============================================================================

public export
data TargetDirectory
  = ApiParsing_Dir      -- Scripts/api_parsing/
  | DevUtils_Dir        -- Scripts/dev_utils/
  | TestsCore_Dir       -- Scripts/tests_core/
  | TestsAutomation_Dir -- Scripts/tests_automation/
  | Deprecated_Dir      -- Scripts/_deprecated/

public export
Show TargetDirectory where
  show ApiParsing_Dir = "api_parsing"
  show DevUtils_Dir = "dev_utils"
  show TestsCore_Dir = "tests_core"
  show TestsAutomation_Dir = "tests_automation"
  show Deprecated_Dir = "_deprecated"

public export
getTargetDirectory : ScriptCategory -> TargetDirectory
getTargetDirectory ApiParsing = ApiParsing_Dir
getTargetDirectory DevUtility = DevUtils_Dir
getTargetDirectory CoreTest = TestsCore_Dir
getTargetDirectory AutomationTest = TestsAutomation_Dir
getTargetDirectory Deprecated = Deprecated_Dir

-- ============================================================================
-- 정리 워크플로우
-- ============================================================================

public export
data CleanupStep
  = CreateDirectories
  | MoveKeepScripts
  | MoveDeprecatedScripts
  | CreateReadme
  | VerifyStructure

public export
cleanupWorkflow : List CleanupStep
cleanupWorkflow = [
  CreateDirectories,
  MoveKeepScripts,
  MoveDeprecatedScripts,
  CreateReadme,
  VerifyStructure
]

-- ============================================================================
-- 검증
-- ============================================================================

public export
totalScripts : Nat
totalScripts = totalKeepCount + totalDeleteCount
-- 예상: 15 + 59 = 74

-- Idris2 컴파일 시 검증
-- total 키워드로 모든 함수가 전체 함수임을 보장
