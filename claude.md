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

### 📋 다음 단계
4. 의존성 설치 및 테스트
5. Claude Desktop 연동 테스트
6. 문서화 완성

---

## 참고 자료
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- HWP COM API: `HwpBooks/ActionTable_2504.pdf`
- Idris2 Spec: `Specs/HwpMCP.idr`
