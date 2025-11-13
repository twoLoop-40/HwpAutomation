# AutoHwp MCP Server - TODO List

## 🔮 Future Work

### 1. MCP-based Problem Merge (AI Agent Testing)
**Priority**: Medium
**Status**: Deferred
**Script**: `Scripts/merge_problems_mcp.py`

#### Context
사용자가 요청: "여태 작성한게 의미가 있는지 궁금하고 나중에 ai agent방식으로 변경할거니까 그것도 미리 테스트 해보고 싶음"

#### Current Status
- ✅ MCP 클라이언트 스크립트 작성 완료 (`merge_problems_mcp.py`)
- ✅ 직접 Python 방식으로 문제 합치기 성공 (`merge_problems_automation.py`)
- ❌ MCP 서버 연결 타임아웃 이슈 발생

#### Issues Encountered
```
mcp.shared.exceptions.McpError: Connection closed
ExceptionGroup: unhandled errors in a TaskGroup
```

#### What Works
- MCP 서버는 `python -m src.server`로 단독 실행 가능
- ActionTable, Automation 도구 모두 정의됨
- Stdio transport 설정 완료

#### What Needs Investigation
1. **MCP 연결 타임아웃 원인**
   - Server initialization 문제인지
   - Stdio transport 설정 문제인지
   - Async 처리 오류인지

2. **테스트 계획**
   - 간단한 MCP 클라이언트로 연결 테스트
   - `hwp_action_create_document` 단일 호출 테스트
   - 성공 시 전체 workflow 실행

3. **장점 검증**
   - MCP 방식이 실제로 유용한지
   - AI Agent가 도구를 제대로 활용할 수 있는지
   - 복잡한 작업을 agent에게 위임 가능한지

#### Implementation Plan
1. **Phase 1: 기본 연결 테스트**
   ```bash
   # 간단한 테스트 스크립트 작성
   python Scripts/test_mcp_connection.py
   ```

2. **Phase 2: 단일 도구 호출**
   ```python
   # hwp_action_create_document 호출
   # hwp_action_execute로 InsertFile 1회 호출
   ```

3. **Phase 3: 전체 워크플로우**
   ```python
   # merge_problems_mcp.py 전체 실행
   # 40개 파일 합치기
   ```

4. **Phase 4: AI Agent 통합**
   - Claude Desktop에 서버 등록
   - Claude에게 "문제 파일 합쳐줘" 요청
   - Agent가 MCP 도구를 활용하는지 확인

#### Files
- `Scripts/merge_problems_mcp.py` - MCP 클라이언트 (준비됨)
- `Scripts/merge_problems_automation.py` - 직접 Python (작동 확인됨) ✅
- `src/server.py` - MCP 서버 (단독 실행 가능)

#### Expected Outcome
MCP 방식이 성공하면:
- ✅ MCP 서버 아키텍처 검증
- ✅ AI Agent 통합 가능성 확인
- ✅ 실제 사용 사례로 전체 시스템 E2E 테스트

---

### 2. ActionTable Parameter Completion
**Priority**: Low
**Status**: Not Started

#### Current Coverage
- ✅ 6/400+ actions implemented (FileNew, FileOpen, FileClose, FileSave, InsertText, TableCreate)
- ✅ 핵심 문서 조작 동작 확인됨

#### Needed
- [ ] ParameterSetTable_2504.pdf 파싱
- [ ] 주요 액션 30-50개 파라미터 정의
- [ ] JSON → Idris 스펙 자동 생성
- [ ] Python 코드 생성 자동화

#### Reference
`Schema/PARAMETER_TABLE_GUIDE.md` 참조

---

### 3. E2E Test Suite Expansion
**Priority**: Medium
**Status**: In Progress

#### Completed
- ✅ 문제 파일 합치기 (40 files, B4 2-column layout)
- ✅ Automation API 활용 검증
- ✅ 실제 업무 시나리오 검증

#### Next Tests
- [ ] 다른 CSV 데이터셋으로 테스트
- [ ] A4 1단 편집 테스트
- [ ] 다양한 페이지/단 나누기 시나리오
- [ ] 에러 케이스 처리 (파일 없음, 잘못된 경로 등)

---

### 4. Rust Port Preparation
**Priority**: Low (미래 작업)

#### Analysis Complete
`Schema/EventHandler_Analysis.md`에 Option A/B/C 비교 완료

#### For Rust Implementation
- Option B (State Query) remains best for MCP
- Option A (Polling) possible as background task with Tokio
- windows-rs for COM interop
- Hybrid approach: State Query MCP + Optional Polling

---

## 📝 Notes

### User Requests
1. ✅ "mcp 방식으로 해줘" - `merge_problems_mcp.py` 작성 완료
2. ✅ "일단 python 방식으로 하고 ToDo 작성할 때 남겨줘" - 이 파일

### Lessons Learned
1. **HWP COM API**:
   - HAction.Run() for simple actions
   - HAction.GetDefault() + Execute() for parameterized actions
   - Some properties may not exist (e.g., ColumnGap)

2. **Automation vs ActionTable**:
   - Automation API 더 직관적
   - HAction으로 직접 액션 호출 가능
   - ActionTable은 파라미터 문서화가 더 필요

3. **File Insertion**:
   - InsertFile action works well
   - BreakColumn, BreakPage for layout control
   - Keep section/char/para shape settings important

### Success Metrics
- ✅ 40/40 files merged successfully
- ✅ B4 paper + 2-column layout applied
- ✅ Page/column breaks correctly inserted
- ✅ 1.3MB output file created

---

## 🚀 Next Steps

1. **Immediate** (This Week):
   - **MCP 도구 검색 기능 추가** - ActionTable/Automation 도구가 많아서 검색이 어려움
     - [ ] `hwp_search_actions` 도구 구현 (ActionTable 액션 검색)
     - [ ] `hwp_get_action_info` 도구 구현 (액션 상세 정보)
     - [ ] `hwp_list_automation_methods` 도구 구현 (Automation 메서드 목록)
     - [ ] 파라미터 정보 조회 기능
   - Debug MCP connection timeout
   - Create `Scripts/test_mcp_connection.py`

2. **Short-term** (This Month):
   - Complete MCP E2E test
   - Test with Claude Desktop integration

3. **Long-term** (Future):
   - Expand action parameter coverage
   - Consider Rust port for performance
   - Build AI agent workflows
