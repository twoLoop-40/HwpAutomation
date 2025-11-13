# Quick Fixes - v2 리뷰

## 🔴 Critical (5분)

### 1. src/common/types.py

**변경 사항**:
```python
# Line 4: import 수정
- from typing import Union, Optional
+ from typing import Union, Optional, Any

# Line 92: 클래스 이름 변경
- class FileNotFoundError(HwpError):
+ class HwpFileNotFoundError(HwpError):

# Line 115-116: 타입 수정
- value: Optional[any] = None
+ value: Optional[Any] = None

# Line 119: 타입 수정
- def ok(cls, value: any = None) -> "HwpResult":
+ def ok(cls, value: Any = None) -> "HwpResult":
```

### 2. src/action_table/client.py

**변경 사항**:
```python
# Line 6: 삭제
- import os
```

## 🟡 Important (30분)

### 3. src/automation/tools.py

**전체 파일 수정** - dict 리스트를 Tool 객체 리스트로 변환

**변경 전**:
```python
AUTOMATION_TOOLS = [
    {
        "name": "hwp_auto_get_documents",
        "description": "...",
        "inputSchema": {...}
    },
]
```

**변경 후**:
```python
from mcp.types import Tool

AUTOMATION_TOOLS = [
    Tool(
        name="hwp_auto_get_documents",
        description="문서 컬렉션(IXHwpDocuments) 가져오기",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # ... 나머지도 동일하게
]
```

## 🟢 Nice to Have (1시간)

### 4. README.md 디렉토리 구조 업데이트

Line 143-161 섹션을 다음으로 교체:

```markdown
### 디렉토리 구조

```
AutoHwp/
├── Specs/                     # Idris2 형식 명세
│   ├── HwpCommon.idr         # 공통 타입
│   ├── ActionTableMCP.idr    # ActionTable API
│   └── AutomationMCP.idr     # Automation API
├── HwpBooks/                  # 참조 문서
│   ├── ActionTable_2504.pdf
│   └── HwpAutomation_2504.pdf
├── src/                       # Python 구현
│   ├── common/               # 공통 타입
│   │   └── types.py
│   ├── action_table/         # ActionTable API
│   │   ├── client.py
│   │   └── tools.py
│   ├── automation/           # Automation API
│   │   ├── client.py
│   │   └── tools.py
│   ├── tools.py              # 통합 라우터
│   └── server.py             # MCP 서버
├── Tests/                     # 테스트
│   ├── ActionTable/
│   └── Automation/
├── CodeReview/                # 코드 리뷰
├── Schema/                    # 설계 문서
├── pyproject.toml
├── README.md
├── CLAUDE.md                  # 개발 로그
└── IDRIS2_USAGE.md           # Idris2 가이드
```
```

### 5. README.md에 Automation 도구 추가

"사용 가능한 도구" 섹션 다음에 추가:

```markdown
## Automation API 도구

### 8. `hwp_auto_get_documents`
문서 컬렉션 가져오기 (IXHwpDocuments)

### 9. `hwp_auto_open_document`
Automation API로 문서 열기

### 10. `hwp_auto_get_active_document`
현재 활성 문서 조회

### 11. `hwp_auto_get_document_property`
문서 속성 읽기 (Path, IsModified, DocumentName)

### 12. `hwp_auto_save_document`
Automation API로 문서 저장

### 13. `hwp_auto_close_document`
Automation API로 문서 닫기

### 14. `hwp_auto_get_windows`
창 컬렉션 가져오기

### 15. `hwp_auto_get_hwp_property`
HWP 애플리케이션 속성 읽기

### 16. `hwp_auto_set_hwp_property`
HWP 애플리케이션 속성 쓰기

### 17. `hwp_auto_quit`
HWP 애플리케이션 종료

### API 비교

| 항목 | ActionTable (`hwp_action_*`) | Automation (`hwp_auto_*`) |
|------|------------------------------|---------------------------|
| 패러다임 | Action 기반 | Object-Oriented (OLE) |
| 추상화 | 높음 (Action ID) | 낮음 (직접 제어) |
| 호출 예시 | `CreateAction("FileNew")` | `hwp.XHwpDocuments.Open()` |
| 상태 관리 | DocumentState | Object properties |
| 유연성 | 제한적 | 높음 |
| 배우기 | 쉬움 | 어려움 |
```

## 적용 방법

### 옵션 1: 수동 수정
각 파일을 직접 열어서 수정

### 옵션 2: 패치 파일 적용 (선호)
```bash
# Fixed 파일들이 준비되면
cp CodeReview/fixed_v2/* src/
```

## 검증

```bash
# 1. 타입 체크
mypy src/

# 2. Import 테스트
python -c "from src.common.types import HwpResult; print('OK')"
python -c "from src.automation.tools import AUTOMATION_TOOLS; print(len(AUTOMATION_TOOLS))"

# 3. 테스트 실행
cd Tests
pytest ActionTable/
pytest Automation/

# 4. MCP 서버 실행 테스트
cd ..
python -m src.server
# Ctrl+C로 종료
```

## 예상 결과

- ✅ mypy 타입 에러 0개
- ✅ 모든 테스트 통과
- ✅ MCP 서버 정상 기동
- ✅ Claude Desktop에서 18개 도구 모두 표시

## 완료 후 품질 점수

**9.3/10 → 9.8/10** 🎯

