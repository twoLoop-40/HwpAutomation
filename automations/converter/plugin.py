"""
HWP to PDF Converter Plugin - V2 플러그인 시스템 연동

Idris2 명세: Specs/Converter/UI.idr

UI 워크플로우:
Initial → FileSelecting → Confirming → Converting → ShowingResult → Closed
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum

from automations.base import AutomationBase, PluginMetadata
from automations.registry import register_plugin

from core.hwp_to_pdf import convert_hwp_to_pdf_parallel


# Idris2 명세: UIState
class UIState(Enum):
    """UI 상태 (Specs/Converter/UI.idr)"""
    INITIAL = "Initial"
    FILE_SELECTING = "FileSelecting"
    CONFIRMING = "Confirming"
    CONVERTING = "Converting"
    SHOWING_RESULT = "ShowingResult"
    CLOSED = "Closed"


@register_plugin
class ConverterPlugin(AutomationBase):
    """HWP to PDF Converter 플러그인"""

    def __init__(self):
        super().__init__()
        self.state = UIState.INITIAL
        self.selected_files: List[str] = []
        self.results: List[tuple] = []
        self.progress_dialog: Optional[tk.Toplevel] = None

    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터"""
        return PluginMetadata(
            id="hwp2pdf",
            name="HWP → PDF 변환기 (hwp2pdf)",
            description="HWP/HWPX 파일을 PDF로 변환합니다 (병렬 처리 지원)",
            version="1.0.0",
            author="Claude"
        )

    def has_ui(self) -> bool:
        """UI 지원"""
        return True

    def run(self, **kwargs) -> Dict[str, Any]:
        """플러그인 실행 (메인 엔트리포인트)"""
        # UI 모드
        if kwargs.get('ui', False):
            self.run_ui()
            return {"success": True}

        # CLI 모드
        return self.run_cli(kwargs)

    def run_ui(self):
        """UI에서 실행 (Tkinter 다이얼로그)

        Idris2 명세 기반 상태 전환:
        Initial → FileSelecting → Confirming → Converting → ShowingResult → Closed
        """
        # 1. Initial → FileSelecting
        self.state = UIState.FILE_SELECTING
        if not self._open_file_selection():
            self.state = UIState.CLOSED
            return

        # 2. FileSelecting → Confirming
        self.state = UIState.CONFIRMING
        if not self._show_confirmation():
            self.state = UIState.CLOSED
            return

        # 3. Confirming → Converting
        self.state = UIState.CONVERTING
        self._show_progress()
        self._execute_conversion()
        self._close_progress()

        # 4. Converting → ShowingResult
        self.state = UIState.SHOWING_RESULT
        self._show_result()

        # 5. ShowingResult → Closed
        self.state = UIState.CLOSED

    def _open_file_selection(self) -> bool:
        """1단계: 파일 선택 다이얼로그

        Idris2 명세: OpenFileSelection : UIWorkflow Initial

        Returns:
            bool: 파일이 선택되었는지 여부 (filesSelected)
        """
        files = filedialog.askopenfilenames(
            title="변환할 HWP 파일 선택",
            filetypes=[
                ("HWP 파일", "*.hwp"),
                ("HWPX 파일", "*.hwpx"),
                ("모든 HWP 파일", "*.hwp *.hwpx")
            ]
        )

        if not files:
            # UserCancelled 이벤트
            return False

        # FilesSelected 이벤트
        self.selected_files = list(files)
        return True

    def _show_confirmation(self) -> bool:
        """2단계: 확인 다이얼로그

        Idris2 명세: ShowConfirmation : (fileCount : Nat) -> UIWorkflow Confirming

        Returns:
            bool: 사용자가 확인했는지 여부
        """
        file_count = len(self.selected_files)

        # Idris2: createConfirmDialog
        confirm = messagebox.askyesno(
            "변환 확인",
            f"{file_count}개 파일을 PDF로 변환하시겠습니까?\n\n"
            f"PDF 파일은 각 HWP 파일과 같은 디렉토리에 저장됩니다."
        )

        if not confirm:
            # UserCancelled 이벤트
            return False

        # UserConfirmed 이벤트
        return True

    def _show_progress(self):
        """3단계: 진행 상황 다이얼로그 표시

        Idris2 명세: ShowProgress : (fileCount : Nat) -> UIWorkflow Converting
        """
        file_count = len(self.selected_files)

        # Idris2: createProgressDialog
        # MkProgressDialog title message fileCount visible
        self.progress_dialog = tk.Toplevel()
        self.progress_dialog.title("변환 중...")
        self.progress_dialog.geometry("400x150")
        self.progress_dialog.resizable(False, False)
        self.progress_dialog.transient()
        self.progress_dialog.grab_set()  # modal = True

        # 진행상황 라벨
        status_label = tk.Label(
            self.progress_dialog,
            text="PDF 변환 중...",
            font=("맑은 고딕", 12, "bold")
        )
        status_label.pack(pady=30)

        progress_label = tk.Label(
            self.progress_dialog,
            text=f"{file_count}개 파일 처리 중 (병렬)",
            font=("맑은 고딕", 10),
            fg="gray"
        )
        progress_label.pack(pady=10)

        # 화면 갱신
        self.progress_dialog.update()

    def _execute_conversion(self):
        """4단계: 병렬 변환 실행

        Idris2 명세: ExecuteConversion : (files : List String) -> (maxWorkers : Nat) -> UIWorkflow Converting
        """
        try:
            # Idris2: convert_hwp_to_pdf_parallel
            self.results = convert_hwp_to_pdf_parallel(
                hwp_files=self.selected_files,
                max_workers=5,
                verbose=True
            )
        except Exception as e:
            self.results = [(False, None, str(e))]

    def _close_progress(self):
        """5단계: 진행 상황 다이얼로그 닫기

        Idris2 명세: CloseProgress : UIWorkflow Converting
        """
        if self.progress_dialog:
            self.progress_dialog.destroy()
            self.progress_dialog = None

    def _show_result(self):
        """6단계: 결과 다이얼로그 표시

        Idris2 명세: ShowResult : ResultDialog -> UIWorkflow ShowingResult
        """
        # 결과 분석
        success_count = sum(1 for s, _, _ in self.results if s)
        fail_count = len(self.results) - success_count

        # Idris2: ResultDialog
        # MkResultDialog success successCount failCount failedFiles
        all_success = (fail_count == 0)

        if all_success:
            # Idris2: createResultDialog (allSuccess = True)
            messagebox.showinfo(
                "완료",
                f"성공적으로 {success_count}개 파일을 PDF로 변환했습니다."
            )
        else:
            # Idris2: createResultDialog (allSuccess = False)
            # 실패한 파일 목록
            failed_files = [
                Path(self.selected_files[i]).name
                for i, (s, _, _) in enumerate(self.results)
                if not s
            ]
            messagebox.showwarning(
                "부분 완료",
                f"{success_count}개 성공, {fail_count}개 실패\n\n"
                f"실패한 파일:\n" + "\n".join(failed_files[:5]) +
                (f"\n... 외 {len(failed_files)-5}개" if len(failed_files) > 5 else "")
            )

    def run_cli(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """CLI에서 실행"""
        files = kwargs.get('files', [])
        max_workers = kwargs.get('max_workers', 5)
        verbose = kwargs.get('verbose', False)

        if not files:
            return {"success": False, "error": "파일이 지정되지 않았습니다"}

        results = convert_hwp_to_pdf_parallel(
            hwp_files=files,
            max_workers=max_workers,
            verbose=verbose
        )

        success_count = sum(1 for s, _, _ in results if s)
        fail_count = len(results) - success_count

        return {
            "success": fail_count == 0,
            "success_count": success_count,
            "fail_count": fail_count,
            "results": results
        }
