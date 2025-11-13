# HWP MCP Server

**한글(HWP) 문서 자동화를 위한 Model Context Protocol (MCP) 서버**

## 개요

이 프로젝트는 한글과컴퓨터의 HWP 문서를 Claude Desktop을 통해 자동화할 수 있게 해주는 MCP 서버입니다.

### 주요 특징

- ✅ **타입 안전성**: Idris2 형식 명세 기반 상태 관리
- ✅ **상태 전환 검증**: 문서 생명주기 자동 관리 (Closed → Opened → Modified → Saved)
- ✅ **COM 자동화**: pywin32를 통한 한글 COM API 연동
- ✅ **MCP 표준**: Claude Desktop과 완전 호환

## 필요 조건

- **OS**: Windows (한글 프로그램 필요)
- **Python**: 3.10 이상
- **한글**: 한글과컴퓨터 워드프로세서 설치 필요
- **패키지 관리자**: uv 권장

## 설치

### 1. uv로 설치 (권장)

```bash
# uv 설치 (없는 경우)
pip install uv

# 프로젝트 의존성 설치
uv pip install -e .
```

### 2. pip로 설치

```bash
pip install -e .
```

## Claude Desktop 설정

`claude_desktop_config.json` 파일에 다음 내용 추가:

**Windows**:
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hwp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourName\\Projects\\AutoHwp",
        "run",
        "python",
        "-m",
        "src.server"
      ]
    }
  }
}
```

## 사용 가능한 도구 (Tools)

### 1. `hwp_create_document`
새 한글 문서 생성

```
상태 전환: Closed → Opened
파라미터: 없음
```

### 2. `hwp_open_document`
기존 한글 문서 열기

```
상태 전환: Closed → Opened
파라미터:
  - path (string): 열 파일 경로
```

### 3. `hwp_close_document`
현재 문서 닫기

```
상태 전환: Opened → Closed
파라미터: 없음
```

### 4. `hwp_save_document`
문서 저장

```
상태 전환: Modified → Saved
파라미터: 없음
```

### 5. `hwp_insert_text`
텍스트 삽입

```
상태 전환: Opened → Modified
파라미터:
  - text (string): 삽입할 텍스트
```

### 6. `hwp_create_table`
표 만들기

```
상태 전환: Opened → Modified
파라미터:
  - rows (integer): 행 개수
  - cols (integer): 열 개수
```

### 7. `hwp_get_document_state`
현재 문서 상태 조회

```
파라미터: 없음
반환: 문서 상태 및 경로 정보
```

## 사용 예제

Claude Desktop에서 다음과 같이 요청할 수 있습니다:

```
새 한글 문서를 만들고 "안녕하세요, MCP!"라는 텍스트를 넣어주세요.
그리고 3x3 표를 하나 만들어주세요.
```

Claude가 자동으로:
1. `hwp_create_document` 호출
2. `hwp_insert_text` 호출
3. `hwp_create_table` 호출

## 아키텍처

### 디렉토리 구조

```
AutoHwp/
├── Specs/
│   └── HwpMCP.idr          # Idris2 형식 명세
├── HwpBooks/
│   └── ActionTable_2504.pdf # 한글 Action 참조 문서
├── src/
│   ├── __init__.py
│   ├── types.py            # 타입 정의 (Idris 스펙 기반)
│   ├── hwp_client.py       # HWP COM 클라이언트
│   ├── tools.py            # MCP 도구 정의
│   └── server.py           # MCP 서버 진입점
├── pyproject.toml
├── README.md
└── claude.md               # 개발 로그
```

### 상태 다이어그램

```
Closed ──create/open──> Opened ──insert_text/create_table──> Modified
  ↑                        ↓                                      ↓
  └────── close ───────────┘                                      │
                                                                  │
                                         Saved <───── save ───────┘
```

## 개발

### Idris2 스펙 컴파일

```bash
cd Specs
idris2 HwpMCP.idr -o build/hwp_mcp
```

### 타입 검증

```bash
mypy src/
```

### 테스트

```bash
pytest tests/
```

## 참고 자료

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Claude Desktop MCP](https://docs.anthropic.com/claude/docs/mcp)
- HWP COM API: `HwpBooks/ActionTable_2504.pdf`
- Idris2 Spec: `Specs/HwpMCP.idr`

## 라이선스

MIT License

## 기여

이슈 및 Pull Request 환영합니다!

## 문제 해결

### HWP 프로그램이 열리지 않는 경우
- 한글과컴퓨터 워드프로세서가 설치되어 있는지 확인
- Windows에서만 동작합니다

### COM 초기화 오류
```bash
uv pip install --upgrade pywin32
python -m win32com.client.makepy "HWPFrame.HwpObject"
```

### 권한 오류
- 관리자 권한으로 실행
- 한글 프로그램이 다른 프로세스에서 사용 중이지 않은지 확인
