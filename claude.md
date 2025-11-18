# HwpAutomation MCP Server 개발 로그

## 프로젝트 개요
한글(HWP) 문서를 MCP(Model Context Protocol)를 통해 자동화하는 서버

### 기술 스택
- **형식 명세**: Idris2 (타입 안전성 검증)
- **MCP 서버**: Python 3.10+
- **한글 연동**: pywin32 (COM)
- **참조 문서**: ActionTable_2504.pdf (400+ 액션)

---

## 진행 단계

### ✅ Step 1: 프로젝트 초기 설정 (2025-11-13)
**커밋**: Initial project setup with Idris2 spec

**완료 내용**:
- `Specs/HwpMCP.idr`: Idris2 형식 명세 작성
  - ActionID 정의 (400+ 액션)
  - DocumentState 상태 관리
  - HwpResult 모나드
  - 타입 안전 ParameterSet
- `pyproject.toml`: Python 프로젝트 설정
- `.gitignore`: Git 제외 파일 설정
- `src/types.py`: Idris 스펙 기반 Python 타입 정의

**주요 타입**:
```python
DocumentState: Closed → Opened → Modified → Saved
ActionRequirement: NoParam | OptionalParam | RequiredParam | ReadOnly
HwpResult: Success | Failure
```

---

### ✅ Step 2: 한글 COM 클라이언트 구현 (2025-11-13)
**커밋**: Implement HWP COM client wrapper

**완료 내용**:
- `src/hwp_client.py`: HwpClient 클래스 구현
  - 문서 생성: `create_new_document()` (Closed → Opened)
  - 문서 열기: `open_document(path)` (Closed → Opened)
  - 문서 닫기: `close_document()` (Opened → Closed)
  - 문서 저장: `save_document()` (Modified → Saved)
  - 텍스트 삽입: `insert_text(text)` (Opened → Modified)
  - 표 생성: `create_table(rows, cols)` (Opened → Modified)
- 상태 전환 검증 로직
- COM 리소스 정리 (cleanup)

**주요 특징**:
- Idris 스펙 기반 상태 전환 보장
- HwpResult로 타입 안전한 에러 처리
- Action Table PDF 참조한 정확한 Action 호출

---

### ✅ Step 3: MCP Tools 및 서버 구현 (2025-11-13)
**커밋**: Implement MCP tools and server

**완료 내용**:
- `src/tools.py`: MCP 도구 정의 및 핸들러
  - 7개 도구: create, open, close, save, insert_text, create_table, get_state
  - ToolHandler 클래스로 도구 호출 라우팅
  - 한글/영문 에러 메시지
- `src/server.py`: MCP 서버 메인 엔트리포인트
  - stdio transport 사용
  - 비동기 처리
  - 리소스 정리
- `README.md`: 사용 설명서
  - 설치 방법 (uv/pip)
  - Claude Desktop 설정
  - 도구 사용법
  - 아키텍처 설명
- `claude_desktop_config.json`: Claude Desktop 설정 예제

**주요 특징**:
- Idris mcpTools 스펙 완벽 구현
- 타입 안전 파라미터 검증
- 상태 기반 에러 메시지

---

### ✅ Step 4: 테스트 스위트 구현 (2025-11-13)
**커밋**: Add test suite for ActionTable validation

**완료 내용**:
- `TestActionTable_2504/test_basic_workflow.py`: 기본 워크플로우 테스트
  - 전체 문서 생명주기 검증 (Closed → Opened → Modified → Saved → Closed)
  - 각 상태 전환 단계별 assertions
  - 실제 HWP 작업 시뮬레이션 (텍스트 삽입, 표 생성)
- `TestActionTable_2504/test_action_table.py`: Action Table 검증 테스트
  - ActionTable_2504.pdf 기반 액션 커버리지 확인
  - 파라미터 요구사항 검증 (NoParam/RequiredParam)
  - 상태 전환 검증 (Idris 스펙 기반)
  - 6개 핵심 액션 구현 확인
- `TestActionTable_2504/README.md`: 테스트 문서
  - 실행 방법
  - 테스트 대상 액션 목록
  - 상태 전환 다이어그램

**주요 특징**:
- Idris 스펙 기반 상태 전환 검증
- ActionTable PDF 참조한 파라미터 검증
- 실패 케이스 테스트 (잘못된 상태 전환)
- uv 기반 테스트 실행

**테스트 커버리지**:
- 6/400+ 액션 구현 (FileNew, FileOpen, FileClose, FileSave, InsertText, TableCreate)
- 핵심 문서 조작 기능 완료

---

---

### ✅ Step 5: 모듈화 리팩토링 (2025-11-13)
**커밋**: Refactor to modular structure for future Automation support

**완료 내용**:
- 확장 가능한 모듈 구조로 리팩토링
- `src/common/`: 공통 타입 및 유틸리티
  - `types.py`: DocumentState, HwpResult, ParameterSet 등
- `src/action_table/`: ActionTable 모듈 (HwpBooks/ActionTable_2504.pdf 기반)
  - `client.py`: ActionTableClient (기존 HwpClient)
  - `tools.py`: ACTION_TABLE_TOOLS, ActionTableToolHandler
- `src/tools.py`: 통합 도구 레지스트리
  - UnifiedToolHandler로 ActionTable + Automation 통합
  - 네임스페이스 기반 라우팅 (hwp_action_*, hwp_auto_*)
- `src/server.py`: 단일 MCP 서버로 모든 도구 제공
- 테스트 파일 import 경로 업데이트

**새로운 구조**:
```
src/
├── common/           # 공통 타입 및 유틸리티
│   ├── __init__.py
│   └── types.py
├── action_table/     # ActionTable 모듈
│   ├── __init__.py
│   ├── client.py     # ActionTableClient
│   └── tools.py      # ACTION_TABLE_TOOLS
├── automation/       # (향후) Automation 모듈
│   ├── __init__.py
│   ├── client.py     # AutomationClient
│   └── tools.py      # AUTOMATION_TOOLS
├── server.py         # 단일 통합 MCP 서버
└── tools.py          # UnifiedToolHandler
```

**주요 특징**:
- 단일 서버에서 ActionTable + Automation 통합 제공
- 네임스페이스로 도구 구분 (hwp_action_*, hwp_auto_*)
- 공통 코드 재사용 (types, 상태 관리)
- 확장성: Automation 모듈 추가 준비 완료

---

### ✅ Step 6: Automation API 구현 (2025-11-13)
**커밋**: Implement Automation API with OLE Object Model

**완료 내용**:
- **형식 명세 재구성**:
  - `Specs/HwpCommon.idr`: 공통 타입 (DocumentState, HwpResult, ParamValue)
  - `Specs/ActionTableMCP.idr`: ActionTable 전용 스펙 (기존 HwpMCP.idr에서 분리)
  - `Specs/AutomationMCP.idr`: Automation 전용 스펙 (OLE Object Model)

- **Automation API 구현**:
  - `src/automation/client.py`: AutomationClient 클래스
    - OLE Object Model 기반 (IHwpObject, IXHwpDocuments, IXHwpDocument)
    - 속성 접근: get_property, set_property
    - 메서드 호출: invoke_method
    - 문서 작업: open_document, save_document, close_document
  - `src/automation/tools.py`: AUTOMATION_TOOLS 정의
    - 11개 도구: get_documents, open_document, get_active_document, etc.
    - AutomationToolHandler 구현

- **통합**:
  - `src/tools.py`: UnifiedToolHandler에 Automation 라우팅 추가
  - 네임스페이스 분리: hwp_action_* vs hwp_auto_*
  - 단일 서버에서 ActionTable + Automation 동시 제공

- **테스트 구조 개선**:
  - `Tests/` 디렉토리로 통합
    - `Tests/ActionTable/`: ActionTable API 테스트
    - `Tests/Automation/`: Automation API 테스트
  - Automation 테스트:
    - `test_automation_basic.py`: 기본 워크플로우
    - `test_automation_spec.py`: Idris 스펙 검증

- **계획 문서**:
  - `Schema/Step6_Automation_Plan.md`: 구현 계획 및 API 차이점 정리

**API 비교**:

| 항목 | ActionTable | Automation |
|------|-------------|------------|
| 패러다임 | Action 기반 | Object-Oriented (OLE) |
| 호출 방식 | CreateAction("FileNew") | hwp.XHwpDocuments.Open() |
| 도구 접두사 | hwp_action_* | hwp_auto_* |
| 상태 관리 | DocumentState | Object properties |
| 형식 명세 | ActionTableMCP.idr | AutomationMCP.idr |

**주요 특징**:
- 두 API 완전 병행 지원
- 단일 MCP 서버, 네임스페이스로 구분
- Idris 형식 명세 기반 타입 안전성
- 공통 코드 재사용 (HwpCommon.idr, common/types.py)

---

### ✅ Step 8: E2E Test - Problem Merge Workflow (2025-11-13)
**커밋**: (Pending) E2E test: Merge 40 HWP files with Automation API

**완료 내용**:
- **E2E 테스트 시나리오**: CSV 기반 문제 파일 합치기
  - 테스트 데이터: `Tests/E2ETest/[내신대비]휘문고_2_기말_1회_20251112_0905/`
  - 40개 HWP 파일 (20문제 × 2파일씩)
  - CSV로 origin_num 그룹화 정의

- **스크립트 구현**:
  - `Scripts/merge_problems.py`: ActionTable API 방식 (action 미구현으로 실패)
  - `Scripts/merge_problems_automation.py`: Automation API 방식 ✅ **성공**
  - `Scripts/merge_problems_mcp.py`: MCP 클라이언트 방식 (연결 이슈로 보류)

- **성공한 작업 흐름** (`merge_problems_automation.py`):
  1. 새 문서 생성 (`HAction.Run("FileNew")`)
  2. B4 용지 설정 (257mm × 364mm)
  3. 2단 편집 설정 (`ColumnDef` action)
  4. CSV 순서대로 40개 파일 삽입 (`InsertFile` action)
  5. 단 나누기 (`BreakColumn`) - 같은 문제 내 파일 사이
  6. 페이지 나누기 (`BreakPage`) - 다른 문제 사이
  7. 문서 저장 (`FileSaveAs_S`)

- **결과**:
  - ✅ 40/40 파일 성공적으로 삽입
  - ✅ 1.3MB 출력 파일 생성
  - ✅ B4 2단 레이아웃 적용 확인
  - ✅ Automation API 실전 검증 완료

- **교훈**:
  - Automation API가 ActionTable보다 더 직관적
  - `HAction.GetDefault()` + `Execute()` 패턴 유효
  - 일부 속성은 존재하지 않을 수 있음 (예: `ColumnGap`)
  - 파일 삽입 시 KeepSection, KeepCharshape, KeepParashape 옵션 중요

- **MCP 방식 이슈 및 TODO**:
  - `merge_problems_mcp.py` 작성 완료했으나 연결 타임아웃 발생
  - 사용자 요청으로 직접 Python 방식 우선 실행
  - `TODO.md`에 MCP 디버깅 및 AI Agent 테스트 계획 문서화
  - 향후 Claude Desktop 통합 테스트 예정

**주요 특징**:
- 실제 업무 시나리오 검증 (문제 파일 합치기)
- Automation API 전 기능 활용 (문서 생성, 설정, 삽입, 저장)
- CSV 기반 메타데이터 처리
- 복잡한 레이아웃 제어 (B4, 2단, 페이지/단 나누기)

**테스트 통계**:
- 입력: 40개 HWP 파일 (20문제 그룹)
- 출력: 1.3MB HWP 문서
- 성공률: 100% (40/40)
- 레이아웃: B4 용지, 2단 편집

---

### ✅ Step 9: AppV1 Copy/Paste 기반 문항 합병 성공 (2025-11-14)
**커밋**: Add Idris2 ParallelMerge spec and InsertFile workflow

**완료 내용**:

**1. InsertFile 방식 실험 (실패)**:
- HwpIdris ParameterSet 명세 기반 `KeepSection` 파라미터 테스트
  - `KeepSection=0`: 구역 정보 무시
  - `KeepSection=1`: 구역 정보 유지 (2단 구성 보존)
- 결과: 두 방식 모두 파일들이 **별도 List로 분리**되어 BreakColumn 미작동
- 근본 문제: InsertFile은 각 파일을 새 List(0, 1, 2, ...)로 삽입
- BreakColumn은 **같은 List 내**에서만 작동 (추정)

**2. Copy/Paste 방식으로 전환 (성공!)**:
- `AppV1/merger.py`: 40문항 성공 로직 기반 ProblemMerger 클래스
  - 검증된 워크플로우:
    1. 양식 파일 열기
    2. 각 문항 처리:
       - 원본 파일 열기
       - 1단으로 변환 (`convert_to_single_column`)
       - 빈 Para 제거 (`remove_empty_paras`, 역순)
       - SelectAll → Copy
       - 대상에 Paste
       - BreakColumn (마지막 제외)
    3. 결과 저장

- `AppV1/para_scanner.py`: **뒤에서부터** 빈 Para 제거
  - `MoveDocEnd`에서 시작
  - `MoveSelDown` + `Delete` 방식
  - 빈 Para 연속 제거 가능
  - 최종 위치: 문서 시작 (Copy 준비)

**3. 테스트 결과**:

| 테스트 | 문항 수 | 시간 | 페이지 | 성공률 | 평가 |
|--------|---------|------|--------|--------|------|
| 5개 파일 | 5 | 49.4초 | 6 | 100% | ✅ |
| **41개 파일** | 41 | 403초 (6.7분) | 31 | **100%** | ✅ **상당히 깨끗함** |
| 제거된 빈 Para | - | - | - | 140개 | - |

**4. 성능 분석**:
- 원본 E2E 테스트: 58.9초 (1.4초/문항)
- AppV1 Merger: 403초 (9.8초/문항)
- **차이 이유**: 각 파일 열기 → 전처리 → 닫기 반복
- 최적화 방향: 전처리 병렬화 (LangGraph Send 패턴)

**5. 주요 발견**:
- BreakColumn은 **양식 파일(target)**에서 실행
- Paste는 **전처리된 파일(source)**의 내용을 target에 붙여넣기
- Copy/Paste 방식이 InsertFile보다 안정적
- 페이지 수: 예상(21페이지) vs 실제(31페이지) - 허용 범위

**변경 파일**:
- `AppV1/merger.py`: 메인 합병 로직
- `AppV1/para_scanner.py`: Para 스캔 및 역순 제거
- `AppV1/column.py`: 1단 변환
- `AppV1/file_inserter.py`: InsertFile 실험 (KeepSection 추가)
- `AppV1/preprocessor.py`: 전처리 모듈 분리
- `Tests/AppV1/test_merger_5files.py`: 5개 파일 테스트
- `Tests/AppV1/test_merger_40files.py`: 41개 파일 테스트 ✅
- `Tests/AppV1/test_insertfile_debug.py`: InsertFile 디버깅
- `Tests/AppV1/test_keepsection_experiment.py`: KeepSection 실험

**참조 문서**:
- `HwpIdris/AppV1/ParallelMerge.idr`: 병렬 처리 명세
- `HwpIdris/TYPE_SPECIFICATION.md`: HWP API 전체 타입 명세
- `Schema/InsertFile_Sync_Analysis.md`: InsertFile 동기화 분석
- `Tests/E2E/test_merge_40_problems_clean.py`: 검증된 40문항 성공 코드

**다음 최적화 목표**:
- 전처리 병렬화 (최대 20개 동시 처리)
- LangGraph Send 패턴 적용
- 전체 소요 시간 80% 단축 목표 (403초 → ~80초)

---

### ✅ Step 10: 프로젝트 정리 및 문서화 (2025-11-14)
**커밋**: Add comprehensive HWP type specs, schemas, and test suites

**완료 내용**:

**1. Idris2 타입 명세 체계화** (`HwpIdris/`):
- Actions 모듈 (12개): Navigation, Selection, Text, File, Format, Table, Document, etc.
- ParameterSets 모듈 (7개): ColDef, CharShape, ParaShape, SecDef, etc.
- Automation 모듈: OLE Object Model
- 워크플로우 명세: OneColOneProblem, MergeProblemFiles, ActionTable

**2. 분석 문서** (`Schema/`): HWP 위치 제어, MoveSel 가이드, 문제 로직 분석 (4개)

**3. 유틸리티** (`Scripts/`): PDF 파싱, API 추출, 문서 정리 (8개)

**4. 테스트 구조화** (`Tests/`):
- AppV1/: 구현 테스트 (6개)
- E2E/: End-to-End 워크플로우 (7개)
- Experiments/: 실험 코드 (11개, 루트에서 이동)
- FunctionTest/: 기능 단위 테스트 (37개)

**5. 기타**:
- Specs/MergeWorkflow.idr
- .gitignore 업데이트 (출력 디렉토리, CSV 제외)
- ErrorImages/ 추가

**통계**: 107 files, 28,706 insertions

**프로젝트 구조**:
```
HwpAutomation/
├── HwpIdris/          # Idris2 타입 명세
├── Schema/            # 분석 문서
├── Scripts/           # 유틸리티
├── Specs/             # 형식 명세
├── Tests/             # 테스트 (AppV1, E2E, Experiments)
├── FunctionTest/      # 기능 테스트
├── AppV1/             # 메인 구현
└── src/               # MCP 서버
```

---

### 📋 다음 단계
11. 전처리 병렬화 구현 (LangGraph Send 또는 multiprocessing)
12. MCP 연결 디버깅 및 AI Agent 통합 테스트
13. Claude Desktop 연동 및 사용자 문서화

---

## 참고 자료
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- HWP COM API:
  - ActionTable: `HwpBooks/ActionTable_2504.pdf`
  - Automation: `HwpBooks/HwpAutomation_2504.pdf`
- Idris2 Specs:
  - Common: `Specs/HwpCommon.idr`
  - ActionTable: `Specs/ActionTableMCP.idr`
  - Automation: `Specs/AutomationMCP.idr`
- Test Suites: `Tests/ActionTable/`, `Tests/Automation/`
- Planning: `Schema/Step6_Automation_Plan.md`

---

## 개발 가이드라인

### HWP API 사용 시 참조 순서
1. **HwpIdris 디렉토리 먼저 확인** (`HwpIdris/`)
   - Idris2로 작성된 타입 안전 형식 명세
   - 모든 HWP Action과 ParameterSet이 타입으로 정의됨
   - 사용 예: 라인 이동이 필요하면 `HwpIdris/Actions/Navigation.idr` 확인

2. **HwpIdris 주요 모듈**:
   - `HwpIdris/Actions/` - 모든 HWP 액션 타입 정의
     - `Navigation.idr`: 이동 관련 (MoveLineDown, MoveParaBegin 등)
     - `Text.idr`: 텍스트 관련
     - `Selection.idr`: 선택 관련
     - `File.idr`: 파일 관련
     - `Format.idr`: 서식 관련
   - `HwpIdris/ParameterSets/` - Parameter 타입 정의
     - `ColDef.idr`: 단 설정
     - `CharShape.idr`: 글자 모양
     - `ParaShape.idr`: 문단 모양
   - `HwpIdris/Automation/Objects.idr` - Automation 객체 모델

3. **HwpBooks PDF 문서** (상세 명세)
   - ActionTable PDF는 보조 자료
   - HwpIdris가 더 검색하기 쉽고 타입 안전함

### 작업 순서
```
필요한 기능 확인
  ↓
HwpIdris에서 타입 검색 (*.idr 파일)
  ↓
Python 구현 (src/automation/ 또는 Tests/)
  ↓
테스트 작성 및 실행
```

### 예시
- **라인별 텍스트 읽기 필요**
  → `HwpIdris/Actions/Navigation.idr` 확인
  → MoveLineDown, MoveLineBegin 등 발견
  → Python으로 구현

- **단 설정 필요**
  → `HwpIdris/ParameterSets/ColDef.idr` 확인
  → Count, SameGap 등 속성 확인
  → Python으로 구현
