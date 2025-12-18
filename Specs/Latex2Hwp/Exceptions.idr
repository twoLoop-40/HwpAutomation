module Latex2Hwp.Exceptions

import Latex2Hwp.Types

%default total

-- ============================================================
-- Python Exception Mapping
-- ============================================================

{-
Python Implementation Guide (Custom Exceptions):

**파일**: `automations/latex2hwp/exceptions.py`

```python
class HwpLatexError(Exception):
    """Base exception for LaTeX to HWP conversion errors"""
    pass

class LatexSyntaxError(HwpLatexError):
    """LaTeX 구문 오류"""
    def __init__(self, latex_source, latex2mathml_error):
        self.latex_source = latex_source
        self.original_error = latex2mathml_error
        super().__init__(f"Invalid LaTeX: {latex2mathml_error}")

class MathMLFileError(HwpLatexError):
    """MathML 파일 쓰기 오류"""
    def __init__(self, filepath, os_error):
        self.filepath = filepath
        self.original_error = os_error
        super().__init__(f"Cannot write MathML file: {filepath}")

class HwpWindowNotFoundError(HwpLatexError):
    """HWP 윈도우를 찾을 수 없음"""
    def __init__(self, window_title, timeout):
        self.window_title = window_title
        self.timeout = timeout
        super().__init__(f"Window not found after {timeout}s: {window_title}")

class DialogNotFoundError(HwpLatexError):
    """다이얼로그를 찾을 수 없음"""
    def __init__(self, dialog_name, timeout):
        self.dialog_name = dialog_name
        self.timeout = timeout
        super().__init__(f"Dialog not found after {timeout}s: {dialog_name}")

class AutomationTimeoutError(HwpLatexError):
    """자동화 타임아웃"""
    def __init__(self, stage, timeout):
        self.stage = stage
        self.timeout = timeout
        super().__init__(f"Timeout during '{stage}' (>{timeout}s)")

class SubprocessFailureError(HwpLatexError):
    """eq_proc.py 서브프로세스 실패"""
    def __init__(self, returncode, stderr):
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(f"eq_proc.py exited with code {returncode}: {stderr}")
```

**사용 예시**:

```python
from latex2mathml import converter
from .exceptions import LatexSyntaxError

try:
    mathml = converter.convert(latex_str)
except Exception as e:
    raise LatexSyntaxError(latex_str, str(e))
```
-}

-- ============================================================
-- Error Handling Pattern (Result Type)
-- ============================================================

||| Result 타입 (Haskell Either, Rust Result와 유사)
public export
data Result : Type -> Type -> Type where
    Ok : a -> Result e a
    Err : e -> Result e a

||| Result의 Functor 인스턴스
export
Functor (Result e) where
    map f (Ok x) = Ok (f x)
    map _ (Err e) = Err e

||| Result의 Applicative 인스턴스
export
Applicative (Result e) where
    pure = Ok
    (Ok f) <*> (Ok x) = Ok (f x)
    (Err e) <*> _ = Err e
    _ <*> (Err e) = Err e

||| Result의 Monad 인스턴스 (do-notation 지원)
export
Monad (Result e) where
    (Ok x) >>= f = f x
    (Err e) >>= _ = Err e

{-
**Python 구현** (`automations/latex2hwp/result.py`):

```python
from typing import TypeVar, Generic, Callable, Union

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[E, T]):
    def __init__(self, is_ok: bool, value: Union[T, E]):
        self._is_ok = is_ok
        self._value = value

    @staticmethod
    def Ok(value: T) -> 'Result[E, T]':
        return Result(True, value)

    @staticmethod
    def Err(error: E) -> 'Result[E, T]':
        return Result(False, error)

    def is_ok(self) -> bool:
        return self._is_ok

    def is_err(self) -> bool:
        return not self._is_ok

    def unwrap(self) -> T:
        if not self._is_ok:
            raise ValueError(f"Called unwrap on Err value: {self._value}")
        return self._value

    def unwrap_or(self, default: T) -> T:
        return self._value if self._is_ok else default

    def map(self, f: Callable[[T], T]) -> 'Result[E, T]':
        if self._is_ok:
            return Result.Ok(f(self._value))
        return self

    def and_then(self, f: Callable[[T], 'Result[E, T]']) -> 'Result[E, T]':
        if self._is_ok:
            return f(self._value)
        return self

# Usage:
def convert_latex(latex: str) -> Result[str, MathML]:
    try:
        mml = converter.convert(latex)
        return Result.Ok(MathML(mml, "/tmp/eq.mml"))
    except Exception as e:
        return Result.Err(f"Conversion failed: {e}")

result = convert_latex(r"\\frac{1}{2}")
if result.is_ok():
    print(result.unwrap().content)
else:
    print("Error:", result._value)
```
-}

-- ============================================================
-- Error Recovery Strategies
-- ============================================================

||| 재시도 정책
public export
record RetryPolicy where
    constructor MkRetryPolicy
    ||| 최대 재시도 횟수
    maxRetries : Nat
    ||| 재시도 간격 (초)
    retryDelay : Double
    ||| 백오프 배수 (exponential backoff)
    backoffMultiplier : Double

||| 기본 재시도 정책
public export
defaultRetryPolicy : RetryPolicy
defaultRetryPolicy = MkRetryPolicy
    { maxRetries = 5
    , retryDelay = 0.1
    , backoffMultiplier = 1.0  -- linear retry
    }

{-
**Python 구현** (`automations/latex2hwp/retry.py`):

```python
import time
from typing import Callable, TypeVar

T = TypeVar('T')

def retry_with_policy(
    func: Callable[[], T],
    max_retries: int = 5,
    delay: float = 0.1,
    backoff: float = 1.0,
    exception_type: type = Exception
) -> T:
    '''
    함수를 재시도하며 실행

    Args:
        func: 실행할 함수 (인자 없음)
        max_retries: 최대 재시도 횟수
        delay: 초기 대기 시간
        backoff: 백오프 배수 (1.0 = linear, 2.0 = exponential)
        exception_type: 잡을 예외 타입
    '''
    current_delay = delay
    for attempt in range(max_retries):
        try:
            return func()
        except exception_type as e:
            if attempt == max_retries - 1:
                raise  # 마지막 시도에서는 예외 전파
            time.sleep(current_delay)
            current_delay *= backoff
    raise RuntimeError("Unreachable")

# Usage in find_window_and_send_key:
def find_window_and_send_key(window_name, key):
    def _attempt():
        app = Application().connect(title=window_name, timeout=10)
        window = app[window_name]
        window.wait('ready', timeout=5)
        window.set_focus()
        time.sleep(0.1)
        send_keys(key)

    retry_with_policy(_attempt, max_retries=5, delay=0.1)
```
-}
