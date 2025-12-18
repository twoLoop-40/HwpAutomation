# LaTeX to HWP Converter - Idris2 Formal Specification

## 개요

LaTeX 수식을 한글(HWP) 문서에 삽입하는 자동화 플러그인의 형식 명세

**기반**: 인프런 강의 스크린샷 분석 (LatexToHwpImage/)

## 명세 파일 구조

```
Specs/Latex2Hwp/
├── Types.idr         # 핵심 타입 정의 (State Machine)
├── Workflow.idr      # 워크플로우 및 Python 구현 가이드
├── UI.idr            # UI 명세 및 Threading 패턴
├── Exceptions.idr    # 예외 처리 및 Result 타입
└── README.md         # 이 문서
```

## 핵심 개념

### 1. State Machine (Types.idr)

LaTeX → HWP 변환 과정을 **타입 레벨에서 증명 가능한 상태 전이**로 모델링:

```idris
Idle → MmlFileReady → EditorOpen → ImportDialogOpen → FileSelected → Done
```

각 전이는 `ValidTransition` 타입으로 증명됨.

### 2. 기술 스택

| Layer | Technology |
|-------|-----------|
| LaTeX → MathML | `latex2mathml` (Python) |
| GUI Automation | `pywinauto` (+ win32gui/con) |
| Subprocess | `eq_proc.py` (별도 프로세스) |
| HWP Control | `pyhwpx.Hwp` |
| UI | Tkinter (Threading) |

### 3. 핵심 워크플로우 (강의 기반)

1. **LaTeX → MathML 변환**
   ```python
   from latex2mathml import converter
   mathml = converter.convert(r"x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}")
   ```

2. **MathML 파일 저장**
   ```python
   with open("C:\\Temp\\eq.mml", 'w', encoding='utf-8') as f:
       f.write(mathml)
   ```

3. **Subprocess 실행** (중요!)
   ```python
   import subprocess, sys
   from pyhwpx import Hwp

   hwp = Hwp()
   subproc = subprocess.Popen([sys.executable, "eq_proc.py", mml_path])
   hwp.EquationCreate()  # 블로킹! (수식편집기가 닫힐 때까지 대기)
   subproc.wait()
   ```

   **왜 Subprocess?**
   - `hwp.EquationCreate()`는 수식편집기가 닫힐 때까지 블로킹
   - 같은 프로세스에서 `pywinauto` 키 입력 불가능
   - → 별도 Python 인터프리터로 자동화 코드 실행

4. **eq_proc.py 자동화** (Subprocess)
   ```python
   # pywinauto를 이용한 GUI 자동화
   find_window_and_send_key("수식 편집기", "%m")  # Alt-M (MathML 불러오기)
   set_text("MathML 파일 불러오기", mml_path)    # 파일 경로 입력
   find_window_and_send_key("MathML 파일 불러오기", "%O")  # Alt-O (확인)
   find_window_and_send_key("수식 편집기", "+{ESC}")  # Shift-Esc (닫기)
   ```

### 4. UI Threading 패턴 (UI.idr)

Tkinter는 **단일 스레드 UI 프레임워크**이므로, 무거운 작업은 Worker Thread에서 실행:

```
Main Thread (UI)  ←──queue.Queue──→  Worker Thread (Automation)
     │                                       │
     ├─ button.click()                      ├─ convert_and_insert()
     ├─ update_status()                     ├─ subprocess.Popen()
     └─ process_queue() (100ms polling)     └─ hwp.EquationCreate()
```

## Python 프로젝트 구조

```
automations/latex2hwp/
├── __init__.py
├── plugin.py              # UI 진입점 (AutomationBase 상속)
├── converter.py           # 메인 변환 로직 (State Machine 구현)
├── eq_proc.py             # Subprocess 자동화 스크립트
├── automation_utils.py    # find_window_and_send_key, set_text 등
├── exceptions.py          # 커스텀 예외 클래스
└── result.py              # Result<E, T> 타입 (선택)

core/
└── (공통 유틸리티)
```

## 구현 가이드

### Step 1: Dependencies 설치

```bash
pip install latex2mathml
pip install pywinauto
pip install pyhwpx
```

### Step 2: automation_utils.py 구현

```python
# 강의 코드 기반
def find_window_and_send_key(window_name, key, retries=5, delay=0.1):
    # ... (Workflow.idr 참조)

def set_text(window_name, filepath):
    # ... (Workflow.idr 참조)
```

### Step 3: eq_proc.py 구현

```python
import sys
from automation_utils import find_window_and_send_key, set_text

if __name__ == "__main__":
    mml_path = sys.argv[1]
    # 4단계 자동화 (Workflow.idr 참조)
```

### Step 4: converter.py 구현

```python
class HwpEquationConverter:
    def process(self, latex_str):
        # Types.ConversionState 흐름을 따라 구현
        # Idle → MmlFileReady → ... → Done
```

### Step 5: plugin.py UI 구현

```python
@register_plugin
class Latex2HwpPlugin(AutomationBase):
    def execute(self):
        # UI.idr의 Threading 패턴 적용
```

## 에러 처리 전략

### 1. Custom Exceptions (Exceptions.idr)

```python
try:
    converter.process(latex)
except HwpWindowNotFoundError:
    # HWP가 실행되지 않음 → 사용자에게 안내
except LatexSyntaxError:
    # LaTeX 구문 오류 → 입력값 검증
except AutomationTimeoutError:
    # 타임아웃 → 재시도 또는 중단
```

### 2. Retry Policy (Exceptions.idr)

```python
from retry import retry_with_policy

retry_with_policy(
    lambda: find_window_and_send_key("수식 편집기", "%m"),
    max_retries=5,
    delay=0.1
)
```

## 테스트 전략

```
Tests/Latex2Hwp/
├── test_latex2mathml.py      # LaTeX → MathML 단위 테스트
├── test_subprocess.py         # eq_proc.py 실행 검증
├── test_integration.py        # 전체 워크플로우 E2E
└── fixtures/
    ├── simple.tex             # 간단한 수식
    ├── complex.tex            # 복잡한 수식 (분수, 루트, 적분 등)
    └── invalid.tex            # 잘못된 구문
```

## 주의사항

1. **pywinauto는 32-bit vs 64-bit 주의**
   - 강의: 64-bit Python에서 32-bit 애플리케이션 제어 시 경고 발생
   - 해결: 같은 아키텍처 사용 권장

2. **send_keys 문법**
   - `+` = Shift
   - `%` = Alt
   - `^` = Ctrl
   - `{ESC}` = Escape

3. **파일 경로는 RAW String 사용**
   ```python
   mml_path = r"C:\Temp\eq.mml"  # ✅
   mml_path = "C:\\Temp\\eq.mml"  # ✅
   mml_path = "C:\Temp\eq.mml"    # ❌ (이스케이프 오류)
   ```

4. **EquationModify() vs EquationCreate()**
   - `EquationCreate()`: 새 수식 생성
   - `EquationModify()`: 기존 수식 수정 (커서가 수식 위에 있어야 함)

## 참고 자료

- 강의 스크린샷: `LatexToHwpImage/Screenshot*.png`
- pywinauto 문서: https://pywinauto.readthedocs.io/
- latex2mathml: https://pypi.org/project/latex2mathml/
- pyhwpx: https://github.com/mete0r/pyhwpx

## Idris2 Proof Goals (향후)

현재 명세는 타입 정의 중심이며, 다음 증명을 추가할 수 있음:

1. **Totality**: 모든 상태 전이가 유한 시간 내에 완료됨
2. **Reachability**: `Idle` 상태에서 `Done` 상태로 항상 도달 가능
3. **Error Recovery**: 모든 `ErrorState`에서 `Idle`로 복귀 가능
4. **Resource Safety**: 파일 핸들, 윈도우 핸들이 항상 정리됨

---

**작성일**: 2025-11-24
**버전**: 1.0.0
**라이선스**: MIT
