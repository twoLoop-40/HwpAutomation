# Step 7: ActionTable 파라미터 검증 통합 계획

**작성일**: 2025-11-13
**목표**: parameter_table.json을 활용하여 타입 안전한 ActionTable 파라미터 검증 구현

---

## 📋 개요

### 현황
- ✅ `Schema/parameter_table.json` 생성 완료 (132개 액션, 1,154개 파라미터)
- ✅ Idris2 형식 명세 작성 완료 (`Specs/ParameterTypes.idr`)
- ✅ 형식 명세 컴파일 검증 완료
- ⏳ MCP 서버에 파라미터 검증 미통합

### 목표
1. 범용 Action 실행 도구 추가 (`hwp_action_execute`)
2. 파라미터 타입 검증 유틸리티 구현
3. ActionTableClient 확장 (범용 execute_action)
4. 기존 도구 개선 (선택사항)

---

## 🏗️ 아키텍처

### 데이터 흐름
```
[parameter_table.json]
         ↓
[param_validator.py] ← PIT_ 타입 검증
         ↓
[ActionTableClient] ← execute_action(action_id, params)
         ↓
[COM CreateAction] → ParameterSet → Execute
         ↓
[HWP Document]
```

### 모듈 구조
```
src/action_table/
├── param_validator.py    # 신규: 파라미터 검증
├── client.py             # 확장: execute_action 메서드 추가
└── tools.py              # 확장: hwp_action_execute 도구 추가

Schema/
└── parameter_table.json  # 런타임 로드 (읽기 전용)

Specs/
├── HwpCommon.idr         # 기존: 공통 타입
├── ParameterTypes.idr    # 신규: PIT_ 타입 시스템
└── ActionTableMCP.idr    # 업데이트: ParameterTypes 통합
```

---

## 📝 구현 명세 (Idris2 스펙 기반)

### 1. ParameterTypes.idr (완료 ✅)

**PIT 타입 시스템**:
```idris
data PITType =
  PIT_BSTR |      -- 문자열
  PIT_UI1 |       -- 1바이트 부호 없는 정수 (0-255)
  PIT_UI2 |       -- 2바이트 부호 없는 정수 (0-65535)
  PIT_UI4 |       -- 4바이트 부호 없는 정수
  PIT_I1 |        -- 1바이트 정수 (-128-127)
  PIT_I2 |        -- 2바이트 정수
  PIT_I4 |        -- 4바이트 정수
  PIT_SET |       -- 중첩 ParameterSet
  PIT_ARRAY       -- 배열
```

**검증 함수**:
```idris
validateType : PITType -> ParamValue -> Either ValidationError ()
validateParameter : ParameterDef -> ParamValue -> Either ValidationError ()
makeParameter : String -> PITType -> ParamValue -> Either ValidationError (String, ParamValue)
```

**액션 스키마**:
```idris
record ActionSchema where
  constructor MkActionSchema
  actionName : String
  paramDefs : List ParameterDef
```

---

## 🔧 구현 단계

### Phase 1: 파라미터 검증기 구현

#### 파일: `src/action_table/param_validator.py`

**역할**:
- `parameter_table.json` 로드 및 캐싱
- PIT_ 타입별 검증 로직
- Python 타입 → PIT_ 타입 변환
- 에러 메시지 생성 (한글/영문)

**핵심 클래스**:
```python
class ParameterValidator:
    """Idris2 Specs/ParameterTypes.idr 구현"""

    def __init__(self):
        self.schemas: Dict[str, ActionSchema] = {}
        self._load_parameter_table()

    def _load_parameter_table(self) -> None:
        """parameter_table.json 로드"""
        # Schema/parameter_table.json 읽기
        # ActionSchema 객체로 변환

    def validate_parameter(
        self,
        action_id: str,
        param_name: str,
        value: Any
    ) -> ValidationResult:
        """단일 파라미터 검증 (validateParameter)"""
        # 1. ActionSchema 조회
        # 2. ParameterDef 찾기
        # 3. PIT_ 타입 검증
        # 4. 범위 체크

    def validate_all_parameters(
        self,
        action_id: str,
        params: Dict[str, Any]
    ) -> ValidationResult:
        """모든 파라미터 검증 (validateParameters)"""
        # 1. 각 파라미터 개별 검증
        # 2. 필수 파라미터 누락 체크
        # 3. 알 수 없는 파라미터 경고

    def convert_to_pit_type(
        self,
        pit_type: str,
        value: Any
    ) -> Any:
        """Python 타입 → PIT_ 타입 변환"""
        # PIT_BSTR: str
        # PIT_UI1: int (0-255)
        # PIT_I4: int
        # etc.
```

**타입 정의**:
```python
@dataclass
class ParameterDef:
    """Idris ParameterDef 대응"""
    param_name: str
    param_type: str  # "PIT_BSTR", "PIT_UI1", etc.
    subtype: str
    description: str

@dataclass
class ActionSchema:
    """Idris ActionSchema 대응"""
    action_name: str
    param_defs: List[ParameterDef]

@dataclass
class ValidationError:
    """Idris ValidationError 대응"""
    error_type: str  # "TypeMismatch", "ValueOutOfRange", etc.
    message: str
    param_name: str

@dataclass
class ValidationResult:
    """검증 결과"""
    success: bool
    errors: List[ValidationError]
    warnings: List[str]
```

---

### Phase 2: ActionTableClient 확장

#### 파일: `src/action_table/client.py`

**새 메서드 추가**:
```python
class ActionTableClient:
    def __init__(self):
        self.hwp = ...
        self.validator = ParameterValidator()  # 신규

    def execute_action(
        self,
        action_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> HwpResult:
        """
        범용 Action 실행 (Idris executeAction 구현)

        Args:
            action_id: 액션 ID (e.g., "InsertText", "CharShape")
            params: 파라미터 dict (e.g., {"Text": "Hello"})

        Returns:
            HwpResult: 성공/실패 결과

        예제:
            >>> client.execute_action("InsertText", {"Text": "안녕하세요"})
            >>> client.execute_action("CharShape", {
            ...     "FaceNameHangul": "맑은 고딕",
            ...     "Height": 1000,
            ...     "Bold": 1
            ... })
        """
        # 1. 파라미터 검증
        if params:
            validation = self.validator.validate_all_parameters(action_id, params)
            if not validation.success:
                return HwpResult.failure(f"Parameter validation failed: {validation.errors}")

        # 2. Action 생성
        try:
            action = self.hwp.CreateAction(action_id)
            if not action:
                return HwpResult.failure(f"Action '{action_id}' not found")
        except Exception as e:
            return HwpResult.failure(f"COM error: {e}")

        # 3. ParameterSet 생성 및 설정
        if params:
            param_set = action.CreateSet()
            action.GetDefault(param_set)

            for param_name, value in params.items():
                # PIT_ 타입으로 변환
                converted = self.validator.convert_to_pit_type(
                    action_id, param_name, value
                )
                param_set.SetItem(param_name, converted)

        # 4. 실행
        try:
            result = action.Execute(param_set if params else None)
            return HwpResult.success({
                "action_id": action_id,
                "result": result,
                "state": self.document.state
            })
        except Exception as e:
            return HwpResult.failure(f"Execution error: {e}")
```

---

### Phase 3: MCP 도구 추가

#### 파일: `src/action_table/tools.py`

**새 도구 정의**:
```python
Tool(
    name="hwp_action_execute",
    description="""
    [ActionTable] 범용 Action 실행

    132개 모든 ActionTable API 액션을 실행할 수 있습니다.
    파라미터는 자동으로 타입 검증됩니다.

    예제:
    - InsertText: {"Text": "안녕하세요"}
    - CharShape: {"FaceNameHangul": "맑은 고딕", "Height": 1000, "Bold": 1}
    - BorderFill: {"BorderTypeLeft": 1, "BorderWidthLeft": 10}
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "action_id": {
                "type": "string",
                "description": "Action ID (e.g., InsertText, CharShape, BorderFill)",
            },
            "parameters": {
                "type": "object",
                "description": "Action parameters as key-value pairs",
                "additionalProperties": True,
            },
        },
        "required": ["action_id"],
    },
)
```

**핸들러 구현**:
```python
class ActionTableToolHandler:
    def handle_execute_action(self, arguments: dict[str, Any]) -> list[TextContent]:
        """hwp_action_execute 핸들러"""
        action_id = arguments.get("action_id")
        params = arguments.get("parameters", {})

        if not action_id:
            return [TextContent(
                type="text",
                text="❌ action_id가 필요합니다."
            )]

        # 범용 실행
        result = self.client.execute_action(action_id, params)

        if result.success:
            return [TextContent(
                type="text",
                text=f"✅ {action_id} 실행 완료\n"
                     f"파라미터: {params}\n"
                     f"상태: {result.value['state']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"❌ {action_id} 실행 실패: {result.error}"
            )]
```

---

### Phase 4: 기존 도구 개선 (선택사항)

**FileOpen 파라미터 확장**:
```python
Tool(
    name="hwp_action_open_document",
    inputSchema={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "read_only": {
                "type": "boolean",
                "description": "읽기 전용으로 열기 (OpenReadOnly)",
                "default": False
            },
            # ... 나머지 8개 파라미터 추가
        },
        "required": ["path"],
    },
)
```

---

## 🧪 테스트 계획

### 단위 테스트: `Tests/ActionTable/test_parameter_validation.py`

```python
def test_pit_type_validation():
    """PIT_ 타입 검증 테스트"""
    validator = ParameterValidator()

    # PIT_BSTR
    assert validator.validate_parameter("InsertText", "Text", "Hello").success
    assert not validator.validate_parameter("InsertText", "Text", 123).success

    # PIT_UI1 (0-255)
    assert validator.validate_parameter("CharShape", "Bold", 1).success
    assert not validator.validate_parameter("CharShape", "Bold", 256).success
    assert not validator.validate_parameter("CharShape", "Bold", -1).success

    # PIT_I4
    assert validator.validate_parameter("CharShape", "Height", 1000).success
    assert validator.validate_parameter("CharShape", "Height", -100).success

def test_action_schema_lookup():
    """ActionSchema 조회 테스트"""
    validator = ParameterValidator()

    schema = validator.schemas.get("InsertText")
    assert schema is not None
    assert len(schema.param_defs) == 1
    assert schema.param_defs[0].param_name == "Text"
    assert schema.param_defs[0].param_type == "PIT_BSTR"

def test_execute_action():
    """범용 액션 실행 테스트"""
    client = ActionTableClient()

    # InsertText
    result = client.execute_action("InsertText", {"Text": "테스트"})
    assert result.success

    # CharShape (복잡한 파라미터)
    result = client.execute_action("CharShape", {
        "FaceNameHangul": "맑은 고딕",
        "Height": 1000,
        "Bold": 1,
        "Italic": 0
    })
    assert result.success
```

### 통합 테스트: `Tests/ActionTable/test_action_execute_workflow.py`

```python
def test_full_document_workflow():
    """전체 문서 작업 워크플로우"""
    client = ActionTableClient()

    # 1. 문서 생성
    client.create_new_document()

    # 2. 텍스트 삽입 (범용 execute_action 사용)
    result = client.execute_action("InsertText", {"Text": "제목\n"})
    assert result.success

    # 3. 글자 모양 변경
    result = client.execute_action("CharShape", {
        "FaceNameHangul": "맑은 고딕",
        "Height": 1200,
        "Bold": 1
    })
    assert result.success

    # 4. 표 생성 (기존 메서드도 계속 사용 가능)
    client.create_table(3, 3)

    # 5. 저장
    client.save_document()

    # 6. 닫기
    client.close_document()
```

---

## 📊 예상 결과

### 커버리지 확대
- **이전**: 6개 액션 (FileNew, FileOpen, FileClose, FileSave, InsertText, TableCreate)
- **이후**: **132개 액션** (CharShape, BorderFill, ParaShape, DrawFillAttr 등)

### 타입 안전성
- ✅ PIT_ 타입별 자동 검증
- ✅ 범위 체크 (PIT_UI1: 0-255, PIT_I4: -2B-2B 등)
- ✅ 필수 파라미터 누락 감지
- ✅ 명확한 에러 메시지 (한글/영문)

### 사용성
```python
# Before: 제한된 액션만 가능
client.insert_text("Hello")
client.create_table(3, 3)

# After: 모든 액션 가능
client.execute_action("InsertText", {"Text": "Hello"})
client.execute_action("CharShape", {"FaceNameHangul": "맑은 고딕", "Height": 1000})
client.execute_action("BorderFill", {"BorderTypeLeft": 1, "BorderWidthLeft": 10})
client.execute_action("ParaShape", {"Align": 1, "LineSpacing": 160})
```

---

## 📁 파일 변경 사항

### 신규 파일
- ✅ `Specs/ParameterTypes.idr` - PIT_ 타입 시스템 (완료)
- ⏳ `src/action_table/param_validator.py` - 파라미터 검증기
- ⏳ `Tests/ActionTable/test_parameter_validation.py` - 검증 테스트
- ⏳ `Tests/ActionTable/test_action_execute_workflow.py` - 통합 테스트

### 수정 파일
- ✅ `Specs/ActionTableMCP.idr` - ParameterTypes import (완료)
- ⏳ `src/action_table/client.py` - execute_action 메서드 추가
- ⏳ `src/action_table/tools.py` - hwp_action_execute 도구 추가
- ⏳ `src/common/types.py` - ValidationError 타입 추가 (선택사항)

### 참조 파일 (변경 없음)
- `Schema/parameter_table.json` - 런타임 로드
- `HwpBooks/ParameterSetTable_2504.pdf` - 원본 참조

---

## ✅ 검증 완료 사항

### Idris2 형식 명세
```bash
$ idris2 --check Specs/ParameterTypes.idr
2/2: Building Specs.ParameterTypes (Specs/ParameterTypes.idr)
✓ Success

$ idris2 --check Specs/ActionTableMCP.idr
3/3: Building Specs.ActionTableMCP (Specs/ActionTableMCP.idr)
✓ Success
```

### 타입 안전성 보장
- ✅ PITType 정의 및 파싱
- ✅ validateType 함수 (범위 검증)
- ✅ ActionSchema 구조
- ✅ ValidationError 타입

---

## 🚀 다음 단계

### 우선순위 1 (핵심 기능)
1. `src/action_table/param_validator.py` 구현
2. `src/action_table/client.py`에 `execute_action` 추가
3. `src/action_table/tools.py`에 `hwp_action_execute` 도구 추가
4. 단위 테스트 작성 및 실행

### 우선순위 2 (품질 개선)
5. 통합 테스트 작성
6. 기존 도구에 파라미터 검증 적용
7. 에러 메시지 다국어 지원 (한글/영문)

### 우선순위 3 (문서화)
8. README.md 업데이트 (사용 예제 추가)
9. MCP 도구 설명서 작성
10. CLAUDE.md 업데이트 (Step 7 기록)

---

## 📚 참고 자료

### 형식 명세
- `Specs/ParameterTypes.idr` - PIT_ 타입 시스템
- `Specs/ActionTableMCP.idr` - ActionTable MCP 스펙
- `Specs/HwpCommon.idr` - 공통 타입

### 데이터
- `Schema/parameter_table.json` - 132개 액션 파라미터 정의
- `Schema/PARAMETER_PROCESSING_SUMMARY.md` - 처리 보고서
- `HwpBooks/ParameterSetTable_2504.pdf` - 원본 PDF

### 기존 구현
- `src/action_table/client.py` - ActionTableClient
- `src/action_table/tools.py` - MCP 도구
- `src/common/types.py` - 공통 타입

---

## 💡 핵심 설계 원칙

1. **Idris2 스펙 우선**: 모든 구현은 Idris2 형식 명세에서 파생
2. **타입 안전성**: PIT_ 타입별 엄격한 검증
3. **하위 호환성**: 기존 6개 도구는 그대로 유지
4. **확장성**: parameter_table.json 업데이트만으로 새 액션 추가
5. **명확한 에러**: 사용자 친화적인 에러 메시지

---

**승인 후 Phase 1부터 순차적으로 구현 시작**
