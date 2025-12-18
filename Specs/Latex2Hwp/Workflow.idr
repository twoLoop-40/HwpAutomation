module Latex2Hwp.Workflow

import Latex2Hwp.Types

%default total

-- ============================================================
-- LaTeX to HWP Conversion Workflow Specification
-- ============================================================

{-
Python Implementation Guide (강의 기반):

1. **Dependencies**:
   ```python
   pip install latex2mathml
   pip install pywinauto  # (또는 %pip install pywinauto)
   ```

2. **Core Modules**:
   - `latex2mathml`: LaTeX → MathML 변환
   - `pywinauto.Application`: 윈도우 애플리케이션 제어
   - `pywinauto.keyboard.send_keys`: 키 입력 전송
   - `win32gui`, `win32con`: 윈도우 핸들 조작
   - `subprocess`: eq_proc.py 실행용
   - `time`: 대기 시간 제어

3. **Main Workflow** (`eq_proc.py` 참조):

   ```python
   import os
   from pywinauto import Application
   from pywinauto.keyboard import send_keys
   import win32gui
   import win32con
   import time

   def find_window_and_send_key(window_name, key, retries=5, delay=0.1):
       """윈도우를 찾아서 키 입력 (재시도 로직 포함)"""
       for attempt in range(retries):
           try:
               app = Application().connect(title=window_name, timeout=10)
               window = app[window_name]
               window.wait('ready', timeout=5)
               window.set_focus()
               time.sleep(delay)
               send_keys(key)
               return
           except Exception as e:
               time.sleep(delay)

   def set_text(window_name, filepath):
       """콤보박스에 파일 경로 설정 (대화상자 자동화)"""
       max_wait_time = 3
       try:
           app = Application().connect(title=window_name, timeout=10)
           window = app[window_name]
           start_time = time.time()
           while time.time() - start_time < max_wait_time:
               comboboxes = window.descendants(class_name="ComboBox")
               comboboxes[0].children()[0].set_text(filepath)
               return
       except Exception as e:
           print(e)

   # === Main Execution (단계별) ===

   # Step 1: LaTeX → MathML 변환
   from latex2mathml import converter
   latex_str = r"x = {-b \pm \sqrt{b^2-4ac} \over 2a}"
   mathml = converter.convert(latex_str)

   # Step 2: MathML을 임시 파일로 저장
   mml_path = r"C:\Users\Administrator\...\m_txt.mathml"
   with open(mml_path, 'w', encoding='utf-8') as f:
       f.write(mathml)

   # Step 3: HWP 수식 편집기 열기 (Shift-Esc 또는 %m)
   find_window_and_send_key("수식 편집기", "%m")

   # Step 4: MathML 파일 불러오기 대화상자 열기
   set_text("MathML 파일 불러오기", mml_path)

   # Step 5: 확인 버튼 (Alt-O)
   find_window_and_send_key("MathML 파일 불러오기", "%O")

   # Step 6: 수식 편집기 닫기 (Shift-Esc)
   find_window_and_send_key("수식 편집기", "+{ESC}")
   ```

4. **Subprocess 방식** (메인 프로세스와 분리):

   ```python
   import sys
   import subprocess
   from pyhwpx import Hwp

   hwp = Hwp()
   subproc = subprocess.Popen([sys.executable, "eq_proc.py"])
   hwp.EquationCreate()  # 수식 객체 생성하고 대기
   subproc.wait()  # 서브프로세스가 완료될 때까지 대기
   ```

   **이유**: EquationModify()는 대화상자가 닫힐 때까지 블로킹되므로,
   pywinauto의 키 입력이 실행되지 않음 → 별도 파이썬 인터프리터로 분리

5. **수식 편집기가 열린 상태에서 실행되는 코드는**:
   - **별도 파일(eq_proc.py)**에 작성
   - **EquationModify 메서드 아래의 모든 코드를 포함하지 않음**
     (왜냐하면 수식편집기가 닫힐 때까지 다음 코드가 실행되지 않기 때문)

6. **키 입력 문법** (pywinauto.keyboard.send_keys):
   - `Shift`: `+` (예: `+{ESC}` = Shift-Esc)
   - `Alt`: `%` (예: `%m` = Alt-M)
   - `Ctrl`: `^` (예: `^n` = Ctrl-N)

7. **주의사항**:
   - pywinauto는 send_keys가 긴 문자열 입력에 적합하지 않음 (비교적 느림)
   - 파일 경로 입력 시 콤보박스의 `set_text()` 사용 권장
   - 수식편집기가 닫힌 후 다시 열면 `hwp.EquationModify()` 사용 가능
-}

-- ============================================================
-- Workflow Steps (Idris2 Proof-Carrying Type)
-- ============================================================

||| 전체 워크플로우 실행 (타입 레벨 증명 포함)
public export
data WorkflowExecution : ConversionState -> ConversionState -> Type where
  ||| 단일 단계 실행
  SingleStep : ValidTransition from to -> WorkflowExecution from to

  ||| 여러 단계 체이닝
  ThenStep : ValidTransition from mid -> WorkflowExecution mid to -> WorkflowExecution from to

||| 성공적인 전체 워크플로우 증명
public export
CompleteWorkflow : LatexSource -> Type
CompleteWorkflow src = WorkflowExecution (Idle src) Done

-- ============================================================
-- Python Mapping Examples
-- ============================================================

{-
**Idris2 Type → Python Function Mapping**:

| Idris2 Type              | Python Implementation                        |
|--------------------------|----------------------------------------------|
| PyConvertLatex latex     | converter.convert(latex)                     |
| WriteFile path content   | open(path, 'w').write(content)               |
| FindWindow title         | Application().connect(title=title)           |
| SendKeys win keys        | find_window_and_send_key(win, keys)          |
| SetComboBoxText win text | set_text(win, text)                          |
| Sleep secs               | time.sleep(secs)                             |

**State Transition → Python Code**:

| Transition           | Python Code                                    |
|----------------------|------------------------------------------------|
| Step_GenMml          | mml = converter.convert(latex); save_file()    |
| Step_OpenEditor      | find_window_and_send_key("수식 편집기", "%m")  |
| Step_OpenImportDialog| set_text("MathML 파일 불러오기", mml_path)     |
| Step_SelectFile      | find_window_and_send_key("...", "%O")          |
| Step_CloseAndSave    | find_window_and_send_key("수식 편집기", "+{ESC}") |
-}

-- ============================================================
-- Recommended Project Structure
-- ============================================================

{-
```
automations/latex2hwp/
├── plugin.py              # UI 및 플러그인 엔트리포인트
├── converter.py           # 메인 변환 로직
├── eq_proc.py             # 수식편집기 자동화 (subprocess용)
├── automation_utils.py    # find_window_and_send_key, set_text 등
└── __init__.py

core/
└── latex_converter.py     # latex2mathml 래퍼 (선택)
```

**실행 흐름**:
1. `plugin.py`: UI에서 LaTeX 입력 받음
2. `converter.py`: ConverterConfig 기반 실행
3. `subprocess.Popen(["python", "eq_proc.py"])`: 별도 프로세스
4. `hwp.EquationCreate()`: 블로킹 대기
5. `eq_proc.py`: pywinauto로 자동화 실행
6. 완료 후 메인 프로세스 재개
-}
