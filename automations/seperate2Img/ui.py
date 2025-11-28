"""
Seperate to Image UI Components
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any


class Seperate2ImgUI:
    """UI 헬퍼 클래스"""

    def __init__(self):
        self.progress_dialog = None
        self.status_label = None

    def open_file_selection(self) -> Optional[str]:
        """파일 선택 다이얼로그"""
        return filedialog.askopenfilename(
            title="HWP 파일 선택",
            filetypes=[("HWP 파일", "*.hwp"), ("HWPX 파일", "*.hwpx")]
        )

    def show_options_dialog(self) -> Optional[Dict[str, Any]]:
        """옵션 설정 다이얼로그"""
        dialog = tk.Toplevel()
        dialog.title("변환 옵션")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient()
        dialog.grab_set()

        result = {}

        # DPI 설정
        tk.Label(dialog, text="해상도 (DPI):", font=("맑은 고딕", 11)).pack(pady=(20, 5))
        dpi_var = tk.IntVar(value=300)
        dpi_frame = tk.Frame(dialog)
        dpi_frame.pack()
        for dpi in [150, 300, 600]:
            tk.Radiobutton(
                dpi_frame,
                text=f"{dpi} DPI",
                variable=dpi_var,
                value=dpi,
                font=("맑은 고딕", 10)
            ).pack(side=tk.LEFT, padx=10)

        # 포맷 설정
        tk.Label(dialog, text="이미지 포맷:", font=("맑은 고딕", 11)).pack(pady=(20, 5))
        format_var = tk.StringVar(value="png")
        format_frame = tk.Frame(dialog)
        format_frame.pack()
        for fmt in ["png", "jpg"]:
            tk.Radiobutton(
                format_frame,
                text=fmt.upper(),
                variable=format_var,
                value=fmt,
                font=("맑은 고딕", 10)
            ).pack(side=tk.LEFT, padx=10)

        # 여백 제거 옵션
        trim_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            dialog,
            text="이미지 여백 자동 제거 (Auto-Crop)",
            variable=trim_var,
            font=("맑은 고딕", 10)
        ).pack(pady=(20, 5))

        # 임시 파일 정리 옵션
        cleanup_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            dialog,
            text="작업 완료 후 임시 파일 삭제",
            variable=cleanup_var,
            font=("맑은 고딕", 10)
        ).pack(pady=(5, 10))

        # 버튼
        def on_ok():
            result['dpi'] = dpi_var.get()
            result['format'] = format_var.get()
            result['trim_whitespace'] = trim_var.get()
            result['cleanup_temp'] = cleanup_var.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="확인",
            command=on_ok,
            width=10,
            font=("맑은 고딕", 10)
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="취소",
            command=on_cancel,
            width=10,
            font=("맑은 고딕", 10)
        ).pack(side=tk.LEFT, padx=5)

        dialog.wait_window()
        return result if result else None

    def show_progress_dialog(self):
        """진행 상황 다이얼로그 표시"""
        self.progress_dialog = tk.Toplevel()
        self.progress_dialog.title("처리 중...")
        self.progress_dialog.geometry("400x150")
        self.progress_dialog.resizable(False, False)
        self.progress_dialog.transient()
        self.progress_dialog.grab_set()
        
        self.status_label = tk.Label(
            self.progress_dialog,
            text="준비 중...",
            font=("맑은 고딕", 12)
        )
        self.status_label.pack(pady=40)
        self.progress_dialog.update()

    def update_progress(self, message: str):
        """진행 상황 업데이트"""
        if self.progress_dialog and self.status_label:
            self.status_label.config(text=message)
            self.progress_dialog.update()
            
    def close_progress_dialog(self):
        """진행 상황 다이얼로그 닫기"""
        if self.progress_dialog:
            self.progress_dialog.destroy()
            self.progress_dialog = None
            self.status_label = None

    def show_success(self, message: str):
        messagebox.showinfo("완료", message)

    def show_warning(self, title: str, message: str):
        messagebox.showwarning(title, message)

    def show_error(self, message: str):
        messagebox.showerror("오류", message)





