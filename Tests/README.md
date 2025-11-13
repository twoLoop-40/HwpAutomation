# AutoHwp Tests

통합 테스트 스위트

## 구조

```
Tests/
├── ActionTable/        # ActionTable API 테스트 (Step 4)
│   ├── test_action_table.py
│   └── test_basic_workflow.py
└── Automation/         # Automation API 테스트 (Step 6)
    ├── test_automation_basic.py
    └── test_automation_spec.py
```

## 실행

### 전체 테스트 실행
```bash
uv run pytest Tests/
```

### ActionTable 테스트만
```bash
uv run pytest Tests/ActionTable/
```

### Automation 테스트만
```bash
uv run pytest Tests/Automation/
```

## 테스트 대상

### ActionTable API (Action-based)
- 문서 생명주기 (Closed → Opened → Modified → Saved → Closed)
- ActionTable 액션 실행 (FileNew, FileOpen, InsertText, TableCreate, etc.)
- 파라미터 검증
- 상태 전환 검증

### Automation API (OLE Object Model)
- 객체 계층 (IHwpObject → IXHwpDocuments → IXHwpDocument)
- 속성 접근 (읽기 전용 / 읽기-쓰기)
- 메서드 호출 (Open, Save, Close)
- Idris 스펙 기반 검증
