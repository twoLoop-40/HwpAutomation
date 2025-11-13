# Critical Fixes - 즉시 수정 필요

**우선순위**: 🔴 HIGH  
**예상 시간**: 5분  
**영향도**: 타입 체커 오류, 런타임 잠재적 충돌

---

## 1. 타입 힌트 오류 수정

### 📍 위치: `src/types.py` 115-116줄

### ❌ 현재 코드
```python
class HwpResult(BaseModel):
    """Result type for HWP operations - matches Idris HwpResult monad."""
    success: bool
    value: Optional[any] = None  # ❌ 'any'는 Python에 없음!
    error: Optional[str] = None
```

### 문제점
- `any`는 Python의 유효한 타입이 아닙니다
- mypy, pyright 등 타입 체커가 에러 발생
- IDE에서 자동완성이 작동하지 않음

### ✅ 수정 코드
```python
from typing import Union, Optional, Any  # Any 추가

class HwpResult(BaseModel):
    """Result type for HWP operations - matches Idris HwpResult monad."""
    success: bool
    value: Optional[Any] = None  # ✅ Any 사용
    error: Optional[str] = None

    @classmethod
    def ok(cls, value: Any = None) -> "HwpResult":  # any → Any
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> "HwpResult":
        return cls(success=False, error=error)
```

### 영향 범위
- `hwp_client.py`: 모든 메서드가 `HwpResult` 반환
- `tools.py`: 모든 핸들러가 `result.value` 접근

---

## 2. 이름 충돌 해결

### 📍 위치: `src/types.py` 92-95줄

### ❌ 현재 코드
```python
class FileNotFoundError(HwpError):  # ❌ Python 내장과 충돌!
    """File not found."""
    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")
```

### 문제점
- Python 내장 `builtins.FileNotFoundError`와 이름 충돌
- 예상치 못한 동작 발생 가능
- 명시적 import 시 혼란

### ✅ 수정 옵션 1: 클래스 이름 변경 (권장)
```python
class HwpFileNotFoundError(HwpError):
    """HWP file not found."""
    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")
```

### ✅ 수정 옵션 2: 모듈 내에서만 사용
```python
class FileNotFoundError(HwpError):
    """File not found."""
    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")

# __init__.py에서
from .types import FileNotFoundError as HwpFileNotFoundError
```

### 영향 범위
- `hwp_client.py` 16-27줄: import 문 수정 필요
- 현재 코드에서 사용되지 않음 (정의만 있음)

---

## 3. 미사용 Import 제거

### 📍 위치: `src/hwp_client.py` 3줄

### ❌ 현재 코드
```python
import os  # ❌ 사용되지 않음
from pathlib import Path
from typing import Optional, Any
```

### ✅ 수정 코드
```python
from pathlib import Path  # Path만으로 충분
from typing import Optional, Any
```

### 이유
- Line 115: `Path.exists()` 사용
- Line 116-117: `Path.absolute()` 사용
- `os` 모듈은 어디에도 사용되지 않음

---

## 적용 방법

### 방법 1: 수동 수정
각 파일을 열어서 위 코드로 직접 수정

### 방법 2: 수정된 파일 사용
```bash
# 리뷰 폴더의 수정된 파일 복사
cp CodeReview_2025-11-13/fixed_code/types.py src/types.py
cp CodeReview_2025-11-13/fixed_code/hwp_client.py src/hwp_client.py
```

---

## 검증

### 1. 타입 체커 실행
```bash
mypy src/
```

**기대 결과**: 에러 없음

### 2. 기존 테스트 실행
```bash
cd TestActionTable_2504
python test_basic_workflow.py
python test_action_table.py
```

**기대 결과**: 모든 테스트 통과

---

## 체크리스트

- [ ] `types.py`: `any` → `Any` 수정
- [ ] `types.py`: `FileNotFoundError` → `HwpFileNotFoundError` 변경
- [ ] `hwp_client.py`: `import os` 제거
- [ ] `hwp_client.py`: import 문에서 `HwpFileNotFoundError` 수정
- [ ] mypy 실행하여 타입 에러 확인
- [ ] 테스트 실행하여 기능 정상 확인

---

**완료 시 예상 품질 향상**: 8/10 → 9/10 🎯

