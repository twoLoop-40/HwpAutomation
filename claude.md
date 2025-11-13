# AutoHwp MCP Server 개발 로그

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

### 📋 다음 단계
7. 의존성 설치 및 통합 테스트
8. Claude Desktop 연동 테스트
9. 문서화 및 예제 추가

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
