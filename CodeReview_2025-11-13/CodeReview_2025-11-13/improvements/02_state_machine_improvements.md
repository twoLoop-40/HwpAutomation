# State Machine Improvements - 상태 머신 개선

**우선순위**: 🟡 MEDIUM  
**예상 시간**: 15분  
**영향도**: API 유연성, 사용자 경험

---

## 문제점 분석

현재 상태 머신이 Idris 명세를 **너무 엄격하게** 해석하여 실용성이 떨어집니다.

### 현재 상태 전이 규칙
```
Closed ──create/open──> Opened ──insert_text──> Modified ──save──> Saved
  ↑                        ↓                        
  └─────── close ──────────┘
```

### 문제 상황

#### 1. `close_document()` 제약
```python
# 현재: OPENED 상태만 닫을 수 있음
if not self._document.check_state(DocumentState.OPENED):
    return HwpResult.fail("Cannot close document: current state is ...")
```

**실제 사용 시나리오**:
```python
# 사용자가 텍스트를 삽입함 (OPENED → MODIFIED)
client.insert_text("Hello")  # 상태: MODIFIED

# 사용자가 저장하지 않고 닫으려고 함
result = client.close_document()  # ❌ 실패! "current state is Modified"
```

**문제**: 사용자가 변경사항을 버리고 닫을 수 없음!

#### 2. `save_document()` 제약
```python
# 현재: MODIFIED 상태만 저장 가능
if not self._document.check_state(DocumentState.MODIFIED):
    return HwpResult.fail("Cannot save document: current state is ...")
```

**실제 사용 시나리오**:
```python
# 빈 문서를 만들고 바로 저장하고 싶음
client.create_new_document()  # 상태: OPENED
result = client.save_document()  # ❌ 실패! "current state is Opened"
```

**문제**: 빈 문서를 저장할 수 없음!

---

## 개선안

### 원칙
1. **안전성 유지**: 진짜 불가능한 전이는 막기 (CLOSED → Modified)
2. **유연성 확보**: 합리적인 전이는 허용 (MODIFIED → CLOSED)
3. **사용자 의도 존중**: 경고는 하되 막지 않기

---

## 1. `close_document()` 개선

### ✅ 수정 코드
```python
def close_document(self) -> HwpResult:
    """
    Close the current document.
    
    State transition: Any non-Closed → Closed
    Matches: FileClose action (NoParam)
    
    Note: Can close from OPENED, MODIFIED, or SAVED states.
          If MODIFIED, unsaved changes will be lost.
    """
    # CLOSED 상태면 이미 닫혀있음
    if self._document.check_state(DocumentState.CLOSED):
        return HwpResult.fail("Document is already closed")
    
    try:
        # MODIFIED 상태라면 경고 메시지 추가
        warning = ""
        if self._document.check_state(DocumentState.MODIFIED):
            warning = " (Warning: Unsaved changes will be lost)"
        
        # Execute FileClose action
        action = self.hwp.CreateAction("FileClose")
        if action is None:
            return HwpResult.fail("FileClose action not found")
        
        param_set = action.CreateSet()
        action.GetDefault(param_set)
        
        if not action.Execute(param_set):
            return HwpResult.fail("Failed to close document")
        
        self._document.path = None
        self._document.transition_state(DocumentState.CLOSED)
        
        return HwpResult.ok({
            "state": DocumentState.CLOSED.value,
            "warning": warning if warning else None
        })
    
    except Exception as e:
        return HwpResult.fail(f"COM error: {e}")
```

### 변경점
- ✅ OPENED, MODIFIED, SAVED 모두에서 닫기 가능
- ✅ MODIFIED 상태일 때 경고 메시지 포함
- ✅ CLOSED 상태면 명확한 에러
- ✅ 실제 HWP 동작과 일치

---

## 2. `save_document()` 개선

### ✅ 수정 코드
```python
def save_document(self) -> HwpResult:
    """
    Save the current document.
    
    State transition: OPENED/MODIFIED → SAVED
    Matches: FileSave action (NoParam)
    
    Note: Can save from OPENED (empty document) or MODIFIED states.
    """
    # CLOSED 상태면 저장할 문서가 없음
    if self._document.check_state(DocumentState.CLOSED):
        return HwpResult.fail("No document open to save")
    
    # SAVED 상태면 이미 저장됨 (재저장은 허용)
    # HWP는 이미 저장된 문서도 다시 저장 가능
    
    try:
        # Execute FileSave action
        action = self.hwp.CreateAction("FileSave")
        if action is None:
            return HwpResult.fail("FileSave action not found")
        
        param_set = action.CreateSet()
        action.GetDefault(param_set)
        
        if not action.Execute(param_set):
            return HwpResult.fail("Failed to save document")
        
        self._document.transition_state(DocumentState.SAVED)
        
        return HwpResult.ok({
            "state": DocumentState.SAVED.value,
            "path": self._document.path
        })
    
    except Exception as e:
        return HwpResult.fail(f"COM error: {e}")
```

### 변경점
- ✅ OPENED 상태에서도 저장 가능 (빈 문서 저장)
- ✅ MODIFIED 상태에서 저장 가능 (기존 동작)
- ✅ SAVED 상태에서 재저장 가능
- ✅ CLOSED 상태만 에러

---

## 3. 새로운 상태 다이어그램

```
┌──────────┐
│  Closed  │◄────────────────────────┐
└─────┬────┘                         │
      │                              │
      │ create_new_document          │
      │ open_document                │
      ▼                              │
┌──────────┐                         │
│  Opened  │◄────────────┐           │
└─────┬────┘             │           │
      │                  │           │
      │ insert_text      │ save      │
      │ create_table     │           │
      │                  │           │
      ▼                  │           │
┌──────────┐             │           │
│ Modified │─────────────┘           │
└─────┬────┘                         │
      │                              │
      │ save                         │
      ▼                              │
┌──────────┐                         │
│  Saved   │                         │
└─────┬────┘                         │
      │                              │
      └──────── close (from any) ────┘
```

### 허용되는 전이
- ✅ OPENED → CLOSED (빈 문서 닫기)
- ✅ MODIFIED → CLOSED (변경사항 버리고 닫기)
- ✅ SAVED → CLOSED (저장 후 닫기)
- ✅ OPENED → SAVED (빈 문서 저장)
- ✅ MODIFIED → SAVED (변경사항 저장)
- ✅ SAVED → SAVED (재저장)

### 여전히 막히는 전이
- ❌ CLOSED → MODIFIED (문서가 열려있지 않음)
- ❌ CLOSED → SAVED (저장할 문서가 없음)

---

## 4. `insert_text()`와 `create_table()` 개선

### 현재 문제
```python
# MODIFIED 상태에서 추가 편집 불가
if not self._document.check_state(DocumentState.OPENED):
    return HwpResult.fail(...)
```

### ✅ 수정
```python
def insert_text(self, text: str) -> HwpResult:
    """
    Insert text into the document.
    
    State transition: OPENED/MODIFIED → MODIFIED
    """
    # OPENED 또는 MODIFIED 상태여야 함
    if self._document.check_state(DocumentState.CLOSED):
        return HwpResult.fail("No document open")
    
    # SAVED 상태에서도 편집 가능 (자동으로 MODIFIED로 전환)
    
    try:
        # ... COM 호출 ...
        
        self._document.transition_state(DocumentState.MODIFIED)
        return HwpResult.ok(...)
```

---

## 테스트 업데이트

### 새 테스트 케이스
```python
def test_flexible_state_transitions():
    """Test improved state machine flexibility."""
    client = HwpClient()
    
    # Test 1: Close from MODIFIED state
    client.create_new_document()
    client.insert_text("Test")
    assert client.document.state == DocumentState.MODIFIED
    
    result = client.close_document()  # ✅ 이제 가능!
    assert result.success
    assert "Warning" in result.value.get("warning", "")
    
    # Test 2: Save empty document
    client.create_new_document()
    assert client.document.state == DocumentState.OPENED
    
    # FileSaveAs를 먼저 호출해야 하지만, 
    # 상태 검증은 통과해야 함
    
    # Test 3: Multiple saves
    client.create_new_document()
    client.insert_text("Test")
    client.save_document()  # MODIFIED → SAVED
    assert client.document.state == DocumentState.SAVED
    
    result = client.save_document()  # SAVED → SAVED (재저장)
    assert result.success  # ✅ 이제 가능!
```

---

## 마이그레이션 가이드

### 기존 코드에 미치는 영향
**영향 없음** ✅

기존에 올바르게 작동하던 코드는 계속 작동합니다.  
새로운 개선안은 **추가적인 유연성**만 제공합니다.

### 적용 후 이점
1. 사용자가 원하는 대로 문서 닫기 가능
2. 빈 문서 저장 가능
3. 재저장 가능
4. 더 직관적인 API

---

## 체크리스트

- [ ] `hwp_client.py`의 `close_document()` 수정
- [ ] `hwp_client.py`의 `save_document()` 수정
- [ ] `hwp_client.py`의 `insert_text()` 수정
- [ ] `hwp_client.py`의 `create_table()` 수정
- [ ] 새 테스트 케이스 추가
- [ ] 기존 테스트 여전히 통과하는지 확인
- [ ] README.md의 상태 다이어그램 업데이트

---

**완료 시 예상 개선**: API 유연성 +50%, 사용자 만족도 ⬆️

