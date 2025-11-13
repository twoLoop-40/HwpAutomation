# Code Quality Refactoring - 코드 품질 개선

**우선순위**: 🟢 LOW (Nice to Have)  
**예상 시간**: 30분  
**영향도**: 유지보수성, 확장성

---

## 문제점: 중복 코드 패턴

### 📍 위치: `src/tools.py` 107-248줄

모든 핸들러 메서드가 동일한 구조를 반복합니다:

```python
def handle_xxx(self, arguments):
    result = self.client.xxx()
    
    if result.success:
        return [TextContent(type="text", text=f"✅ 성공: ...")]
    else:
        return [TextContent(type="text", text=f"❌ 실패: {result.error}")]
```

**7개 핸들러 × 10줄 = 70줄의 유사한 코드**

---

## 개선 방향

### DRY 원칙 적용
**Don't Repeat Yourself** - 반복되는 로직을 추상화

### 리팩토링 전략
1. 공통 응답 생성 로직을 헬퍼 메서드로 분리
2. 성공/실패 메시지 포맷터 통일
3. 파라미터 검증 로직 공통화

---

## 리팩토링 1: 응답 헬퍼 메서드

### ✅ 개선 코드

```python
class ToolHandler:
    """Handler for MCP tool calls."""

    def __init__(self):
        """Initialize tool handler with HWP client."""
        self.client = HwpClient()
    
    # ========== 헬퍼 메서드 ==========
    
    def _create_response(
        self, 
        success: bool, 
        message: str
    ) -> list[TextContent]:
        """Create a standardized response with emoji."""
        icon = "✅" if success else "❌"
        return [TextContent(type="text", text=f"{icon} {message}")]
    
    def _format_success_message(
        self, 
        action: str, 
        details: dict[str, Any]
    ) -> str:
        """Format success message with details."""
        lines = [f"{action} 성공"]
        for key, value in details.items():
            if value is not None:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _format_error_message(self, action: str, error: str) -> str:
        """Format error message."""
        return f"{action} 실패: {error}"
    
    def _validate_required_params(
        self, 
        arguments: dict[str, Any], 
        required: list[str]
    ) -> tuple[bool, str]:
        """
        Validate required parameters.
        
        Returns:
            (is_valid, error_message)
        """
        for param in required:
            if param not in arguments or arguments[param] is None:
                return False, f"필수 파라미터 '{param}'가 없습니다."
        return True, ""
```

---

## 리팩토링 2: 핸들러 단순화

### Before (현재)
```python
def handle_create_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_create_document tool call."""
    result = self.client.create_new_document()
    
    if result.success:
        return [
            TextContent(
                type="text",
                text=f"✅ 새 문서를 생성했습니다.\n상태: {result.value['state']}",
            )
        ]
    else:
        return [
            TextContent(
                type="text",
                text=f"❌ 문서 생성 실패: {result.error}",
            )
        ]
```

### After (개선)
```python
def handle_create_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_create_document tool call."""
    result = self.client.create_new_document()
    
    if result.success:
        msg = self._format_success_message("문서 생성", {
            "상태": result.value['state']
        })
    else:
        msg = self._format_error_message("문서 생성", result.error)
    
    return self._create_response(result.success, msg)
```

**10줄 → 8줄, 가독성 향상**

---

## 리팩토링 3: 파라미터 검증 통합

### Before (현재)
```python
def handle_open_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_open_document tool call."""
    path = arguments.get("path")
    if not path:
        return [
            TextContent(
                type="text",
                text="❌ 파일 경로가 필요합니다.",
            )
        ]
    
    result = self.client.open_document(path)
    # ... 나머지 코드 ...
```

### After (개선)
```python
def handle_open_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_open_document tool call."""
    # 파라미터 검증
    valid, error_msg = self._validate_required_params(arguments, ["path"])
    if not valid:
        return self._create_response(False, error_msg)
    
    # 실행
    result = self.client.open_document(arguments["path"])
    
    if result.success:
        msg = self._format_success_message("문서 열기", {
            "경로": result.value['path'],
            "상태": result.value['state']
        })
    else:
        msg = self._format_error_message("문서 열기", result.error)
    
    return self._create_response(result.success, msg)
```

---

## 리팩토링 4: 제네릭 실행 래퍼

### 최상위 추상화
```python
def _execute_action(
    self,
    action_name: str,
    action_func: callable,
    arguments: dict[str, Any],
    required_params: list[str] = None,
    success_details_extractor: callable = None
) -> list[TextContent]:
    """
    Generic action executor with validation and formatting.
    
    Args:
        action_name: Display name for the action
        action_func: Client method to call
        arguments: Tool arguments
        required_params: List of required parameter names
        success_details_extractor: Function to extract details from result
    """
    # 1. 파라미터 검증
    if required_params:
        valid, error_msg = self._validate_required_params(
            arguments, required_params
        )
        if not valid:
            return self._create_response(False, error_msg)
    
    # 2. 액션 실행
    result = action_func(**arguments)
    
    # 3. 응답 생성
    if result.success:
        if success_details_extractor:
            details = success_details_extractor(result.value)
        else:
            details = result.value or {}
        msg = self._format_success_message(action_name, details)
    else:
        msg = self._format_error_message(action_name, result.error)
    
    return self._create_response(result.success, msg)
```

### 사용 예시
```python
def handle_create_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_create_document tool call."""
    return self._execute_action(
        action_name="문서 생성",
        action_func=self.client.create_new_document,
        arguments={},
        success_details_extractor=lambda v: {"상태": v['state']}
    )

def handle_open_document(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_open_document tool call."""
    return self._execute_action(
        action_name="문서 열기",
        action_func=self.client.open_document,
        arguments=arguments,
        required_params=["path"],
        success_details_extractor=lambda v: {
            "경로": v['path'],
            "상태": v['state']
        }
    )

def handle_insert_text(self, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle hwp_insert_text tool call."""
    return self._execute_action(
        action_name="텍스트 삽입",
        action_func=self.client.insert_text,
        arguments=arguments,
        required_params=["text"],
        success_details_extractor=lambda v: {
            "길이": f"{v['text_length']} 글자",
            "상태": v['state']
        }
    )
```

**각 핸들러가 10줄 → 3줄로 단축!**

---

## 전체 리팩토링 비교

### Before
```python
class ToolHandler:
    def __init__(self):
        self.client = HwpClient()
    
    def handle_create_document(self, arguments):
        # 10줄
    
    def handle_open_document(self, arguments):
        # 15줄
    
    def handle_insert_text(self, arguments):
        # 15줄
    
    # ... 7개 핸들러 × 평균 12줄 = 84줄
    
    def handle_call(self, name, arguments):
        # 30줄
    
    def cleanup(self):
        # 2줄

# 총 약 120줄
```

### After
```python
class ToolHandler:
    def __init__(self):
        self.client = HwpClient()
    
    # === 헬퍼 메서드 (30줄) ===
    def _create_response(self, success, message): ...
    def _format_success_message(self, action, details): ...
    def _format_error_message(self, action, error): ...
    def _validate_required_params(self, arguments, required): ...
    def _execute_action(self, ...): ...
    
    # === 핸들러 (7개 × 3줄 = 21줄) ===
    def handle_create_document(self, arguments):
        return self._execute_action(...)
    
    def handle_open_document(self, arguments):
        return self._execute_action(...)
    
    # ...
    
    # === 라우팅 (30줄) ===
    def handle_call(self, name, arguments): ...
    
    def cleanup(self): ...

# 총 약 85줄 (-35줄, -30%)
```

---

## 장점

### 1. 유지보수성 ⬆️
- 응답 포맷 변경 시 한 곳만 수정
- 새 핸들러 추가가 매우 간단

### 2. 테스트 용이성 ⬆️
- 헬퍼 메서드를 독립적으로 테스트 가능
- Mock이 쉬워짐

### 3. 확장성 ⬆️
```python
# 새 핸들러 추가가 3줄로 끝남
def handle_new_action(self, arguments):
    return self._execute_action(
        "새 액션", self.client.new_action, arguments
    )
```

### 4. 일관성 ⬆️
- 모든 응답이 동일한 포맷
- 파라미터 검증이 통일됨

---

## 마이그레이션 전략

### Phase 1: 헬퍼 메서드 추가
기존 코드를 유지하면서 헬퍼 메서드만 추가

### Phase 2: 점진적 리팩토링
한 번에 하나씩 핸들러를 새 방식으로 변경

### Phase 3: 테스트 및 검증
각 단계마다 기존 테스트가 통과하는지 확인

### Phase 4: 정리
사용하지 않는 코드 제거

---

## 추가 개선 아이디어

### 1. 로깅 추가
```python
def _execute_action(self, ...):
    logger.info(f"Executing action: {action_name}")
    result = action_func(**arguments)
    if result.success:
        logger.info(f"Action succeeded: {action_name}")
    else:
        logger.error(f"Action failed: {action_name}, {result.error}")
    return ...
```

### 2. 메트릭 수집
```python
def _execute_action(self, ...):
    start_time = time.time()
    result = action_func(**arguments)
    duration = time.time() - start_time
    metrics.record_action(action_name, result.success, duration)
    return ...
```

### 3. 재시도 로직
```python
def _execute_action(self, ..., max_retries=3):
    for attempt in range(max_retries):
        result = action_func(**arguments)
        if result.success:
            return ...
        if attempt < max_retries - 1:
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    return ...
```

---

## 체크리스트

- [ ] 헬퍼 메서드 구현
- [ ] `handle_create_document` 리팩토링
- [ ] `handle_open_document` 리팩토링
- [ ] `handle_close_document` 리팩토링
- [ ] `handle_save_document` 리팩토링
- [ ] `handle_insert_text` 리팩토링
- [ ] `handle_create_table` 리팩토링
- [ ] `handle_get_document_state` 리팩토링
- [ ] 기존 테스트 통과 확인
- [ ] 코드 리뷰

---

**완료 시 예상 개선**: 코드 라인 -30%, 유지보수성 +50% 🎯

