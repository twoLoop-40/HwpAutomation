# Test Suite for HWP MCP Server

ActionTable_2504.pdf 참조 문서 기반 테스트

## 테스트 파일

### 1. `test_basic_workflow.py`
**기본 워크플로우 테스트**

문서 생명주기 전체를 테스트:
```
Closed → Opened → Modified → Saved → Closed
```

실행:
```bash
cd TestActionTable_2504
uv run python test_basic_workflow.py
```

### 2. `test_action_table.py`
**Action Table 검증 테스트**

ActionTable_2504.pdf의 액션 구현 검증:
- ✅ 액션 커버리지 확인
- ✅ 파라미터 요구사항 검증 (NoParam/RequiredParam)
- ✅ 상태 전환 검증 (Idris 스펙 기반)

실행:
```bash
cd TestActionTable_2504
uv run python test_action_table.py
```

## 테스트 대상 액션

### ActionTable_2504.pdf 참조

| Action ID | ParameterSet | Description | 구현 여부 |
|-----------|--------------|-------------|----------|
| FileNew | - | 새 문서 | ✅ |
| FileOpen | RequiredParam | 파일 열기 | ✅ |
| FileClose | - | 문서 닫기 | ✅ |
| FileSave | - | 파일 저장 | ✅ |
| InsertText | RequiredParam | 텍스트 삽입 | ✅ |
| TableCreate | RequiredParam | 표 만들기 | ✅ |

**진행률**: 6/400+ 액션 (핵심 문서 조작 기능)

## 상태 전환 다이어그램

```
┌─────────┐
│ Closed  │◄─────────────────┐
└────┬────┘                  │
     │ create_new_document   │
     │ open_document         │
     ▼                       │
┌─────────┐                  │
│ Opened  │                  │ close_document
└────┬────┘                  │
     │ insert_text           │
     │ create_table          │
     ▼                       │
┌─────────┐                  │
│Modified │                  │
└────┬────┘                  │
     │ save_document         │
     ▼                       │
┌─────────┐                  │
│ Saved   │──────────────────┘
└─────────┘
```

## 모든 테스트 실행

```bash
# 가상환경 활성화
source ../.venv/Scripts/activate

# 모든 테스트 실행
python test_basic_workflow.py && python test_action_table.py
```

## 참고

- **Idris 스펙**: `../Specs/HwpMCP.idr`
- **Action Table**: `../HwpBooks/ActionTable_2504.pdf`
- **구현**: `../src/hwp_client.py`
