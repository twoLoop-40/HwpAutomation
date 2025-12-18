module Latex2Hwp.UI

import Latex2Hwp.Types

%default total

-- ============================================================
-- LaTeX to HWP Plugin UI Specification
-- ============================================================

{-
Python Implementation Guide (Tkinter with Threading):

1. **UI Architecture**:
   - Main Thread: UI 렌더링 및 이벤트 처리 (Tkinter Loop)
   - Worker Thread: `convert_and_insert` 등 무거운 자동화 작업 수행
   - Communication: `queue.Queue`를 통해 작업 상태(State)를 UI로 전달

2. **Recommended UI Components**:
   - [Input] `ScrolledText`: LaTeX 소스 입력 (Syntax highlighting 추천)
   - [Preview] `Label` (Image): MathML 렌더링 미리보기 (선택 사항, matplotlib 등 활용)
   - [Config] `Toplevel`: 설정 변경 창 (딜레이, 파일 경로 등)
   - [Log] `Listbox` or `Text`: 진행 로그 출력 (실시간)

3. **Example Code Structure**:

   ```python
   import tkinter as tk
   from tkinter import ttk, scrolledtext, messagebox
   import threading
   import queue
   from automations.latex2hwp.converter import HwpEquationConverter
   
   class Latex2HwpUI:
       def __init__(self, root):
           self.root = root
           self.root.title("LaTeX to HWP (v2.0)")
           self.queue = queue.Queue()
           # Converter 인스턴스 (설정 주입 가능)
           self.converter = HwpEquationConverter()
           
           self._setup_ui()
           # 주기적으로 큐 확인 (100ms)
           self.root.after(100, self._process_queue)
           
       def _setup_ui(self):
           # 1. Settings Panel (Top)
           frame_top = ttk.Frame(self.root)
           frame_top.pack(fill=tk.X, padx=5, pady=5)
           ttk.Label(frame_top, text="Delay(s):").pack(side=tk.LEFT)
           self.delay_var = tk.StringVar(value="0.1")
           ttk.Entry(frame_top, textvariable=self.delay_var, width=5).pack(side=tk.LEFT)
           
           # 2. LaTeX Input (Middle)
           frame_mid = ttk.LabelFrame(self.root, text="LaTeX Source")
           frame_mid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
           self.txt_input = scrolledtext.ScrolledText(frame_mid, height=10)
           self.txt_input.pack(fill=tk.BOTH, expand=True)
           
           # Default Example
           self.txt_input.insert("1.0", r"x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}")
           
           # 3. Control & Status (Bottom)
           frame_bot = ttk.Frame(self.root)
           frame_bot.pack(fill=tk.X, padx=5, pady=5)
           
           self.btn_run = ttk.Button(frame_bot, text="Insert to HWP", command=self.start_conversion)
           self.btn_run.pack(side=tk.RIGHT)
           
           self.lbl_status = ttk.Label(frame_bot, text="Ready", foreground="blue")
           self.lbl_status.pack(side=tk.LEFT, fill=tk.X)
           
           self.progress = ttk.Progressbar(frame_bot, mode='indeterminate')
           
       def start_conversion(self):
           latex = self.txt_input.get("1.0", tk.END).strip()
           if not latex:
               messagebox.showwarning("Warning", "Please enter LaTeX code.")
               return
               
           # UI Lock
           self.btn_run.config(state=tk.DISABLED)
           self.progress.pack(side=tk.LEFT, padx=5)
           self.progress.start()
           
           # Start Thread (Daemon으로 실행하여 메인 종료 시 같이 종료)
           threading.Thread(target=self._worker, args=(latex,), daemon=True).start()
           
       def _worker(self, latex_source):
           try:
               self.queue.put(("STATUS", "Generating MathML..."))
               # Call core logic (Synchronous) - 실제로는 Types.ConversionState 흐름을 따름
               self.converter.process(latex_source)
               self.queue.put(("DONE", None))
           except Exception as e:
               self.queue.put(("ERROR", str(e)))
               
       def _process_queue(self):
           try:
               while True:
                   msg_type, data = self.queue.get_nowait()
                   if msg_type == "STATUS":
                       self.lbl_status.config(text=data, foreground="black")
                   elif msg_type == "DONE":
                       self.lbl_status.config(text="Success!", foreground="green")
                       self._reset_ui()
                       messagebox.showinfo("Success", "Equation Inserted.")
                   elif msg_type == "ERROR":
                       self.lbl_status.config(text=f"Error: {data}", foreground="red")
                       self._reset_ui()
                       messagebox.showerror("Error", data)
           except queue.Empty:
               pass
           finally:
               self.root.after(100, self._process_queue)
               
       def _reset_ui(self):
           self.btn_run.config(state=tk.NORMAL)
           self.progress.stop()
           self.progress.pack_forget()
   ```
-}

-- ============================================================
-- 4. UI Logic Specification (MVC Pattern)
-- ============================================================

||| UI에 표시될 현재 상태 메시지
public export
data UIStatusMessage : Type where
    MsgReady : UIStatusMessage
    MsgConverting : UIStatusMessage
    MsgOpeningEditor : UIStatusMessage
    MsgImporting : UIStatusMessage
    MsgSuccess : UIStatusMessage
    MsgError : String -> UIStatusMessage

export
Show UIStatusMessage where
    show MsgReady = "Ready"
    show MsgConverting = "Converting LaTeX to MathML..."
    show MsgOpeningEditor = "Opening Equation Editor..."
    show MsgImporting = "Importing MathML File..."
    show MsgSuccess = "Done!"
    show (MsgError s) = "Error: " ++ s

||| Core 상태(Types.ConversionState)를 UI 메시지로 매핑
||| 이 함수는 Worker Thread가 Queue에 넣을 메시지를 결정하는 로직입니다.
public export
stateToMessage : ConversionState -> UIStatusMessage
stateToMessage (Idle _) = MsgReady
stateToMessage (MmlFileReady _) = MsgOpeningEditor
stateToMessage (EditorOpen _ _) = MsgImporting
stateToMessage (ImportDialogOpen _ _ _) = MsgImporting -- 세부 단계는 퉁쳐서 표현
stateToMessage (FileSelected _) = MsgImporting
stateToMessage Done = MsgSuccess
stateToMessage (ErrorState (LatexToMmlError s)) = MsgError ("LaTeX Invalid: " ++ s)
stateToMessage (ErrorState (WindowNotFound s)) = MsgError ("HWP Not Found: " ++ s)
stateToMessage (ErrorState err) = MsgError (show err)

-- ============================================================
-- 5. Integration Interfaces
-- ============================================================

{-
**핵심 연동 포인트 (Core <-> UI)**:

1. `converter.py` (Core)는 순수 함수형 로직에 가깝게 작성하거나,
   콜백(Callback)을 인자로 받아 상태 변경 시마다 호출해주어야 합니다.
   
   ```python
   # core/converter.py
   class HwpEquationConverter:
       def __init__(self, callback=None):
           self.callback = callback # func(state_msg: str)
           
       def notify(self, msg):
           if self.callback: self.callback(msg)
           
       def process(self, latex):
           self.notify("Generating MathML...")
           # ... logic ...
           self.notify("Opening Editor...")
           # ... logic ...
   ```

2. `Types.HwpError` 클래스의 예외들은 Python의 사용자 정의 Exception으로 매핑되어야 합니다.
   - `class HwpWindowNotFoundError(Exception): ...`
   - `class LatexSyntaxError(Exception): ...`
-}









