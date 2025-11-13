"""ActionTable HWP COM client wrapper with state management.

Based on HwpBooks/ActionTable_2504.pdf
"""

import os
from pathlib import Path
from typing import Optional, Any

try:
    import win32com.client as win32
    import pythoncom
except ImportError:
    raise ImportError(
        "pywin32 is required for HWP automation. "
        "Install it with: uv pip install pywin32"
    )

from ..common.types import (
    DocumentHandle,
    DocumentState,
    ParameterSet,
    HwpResult,
    ActionNotFound,
    InvalidParameter,
    DocumentNotOpen,
    DocumentAlreadyOpen,
    InvalidState,
    FileNotFoundError,
    COMError,
)


class ActionTableClient:
    """
    ActionTable HWP COM client wrapper with type-safe state management.

    Based on the Idris2 formal specification in Specs/HwpMCP.idr and
    ActionTable_2504.pdf reference document.

    Ensures safe state transitions and parameter validation for ActionTable operations.
    """

    def __init__(self):
        """Initialize HWP COM client."""
        self._hwp: Optional[Any] = None
        self._document: DocumentHandle = DocumentHandle()

    def _ensure_com_initialized(self) -> None:
        """Ensure COM is initialized for the current thread."""
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass  # Already initialized

    def _create_hwp_instance(self) -> Any:
        """Create HWP COM instance."""
        self._ensure_com_initialized()
        try:
            hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
            return hwp
        except Exception as e:
            raise COMError(f"Failed to create HWP instance: {e}")

    @property
    def hwp(self) -> Any:
        """Get HWP COM object, creating it if necessary."""
        if self._hwp is None:
            self._hwp = self._create_hwp_instance()
        return self._hwp

    @property
    def document(self) -> DocumentHandle:
        """Get current document handle."""
        return self._document

    def create_new_document(self) -> HwpResult:
        """
        Create a new HWP document.

        State transition: Closed → Opened
        Matches: FileNew action (NoParam)
        """
        if not self._document.check_state(DocumentState.CLOSED):
            return HwpResult.fail(
                f"Cannot create new document: current state is {self._document.state}"
            )

        try:
            # Execute FileNew action
            action = self.hwp.CreateAction("FileNew")
            if action is None:
                return HwpResult.fail("FileNew action not found")

            param_set = action.CreateSet()
            action.GetDefault(param_set)

            if not action.Execute(param_set):
                return HwpResult.fail("Failed to execute FileNew")

            self._document.transition_state(DocumentState.OPENED)
            return HwpResult.ok({"state": DocumentState.OPENED.value})

        except Exception as e:
            return HwpResult.fail(f"COM error: {e}")

    def open_document(self, path: str) -> HwpResult:
        """
        Open an existing HWP document.

        State transition: Closed → Opened
        Matches: FileOpen action (RequiredParam)
        """
        if not self._document.check_state(DocumentState.CLOSED):
            return HwpResult.fail(
                f"Cannot open document: current state is {self._document.state}"
            )

        # Validate file exists
        file_path = Path(path)
        if not file_path.exists():
            return HwpResult.fail(f"File not found: {path}")

        try:
            # Execute FileOpen action
            action = self.hwp.CreateAction("FileOpen")
            if action is None:
                return HwpResult.fail("FileOpen action not found")

            param_set = action.CreateSet()
            action.GetDefault(param_set)
            param_set.SetItem("filename", str(file_path.absolute()))

            if not action.Execute(param_set):
                return HwpResult.fail(f"Failed to open document: {path}")

            self._document.path = str(file_path.absolute())
            self._document.transition_state(DocumentState.OPENED)

            return HwpResult.ok({
                "state": DocumentState.OPENED.value,
                "path": self._document.path
            })

        except Exception as e:
            return HwpResult.fail(f"COM error: {e}")

    def close_document(self) -> HwpResult:
        """
        Close the current document.

        State transition: Opened → Closed
        Matches: FileClose action (NoParam)
        """
        if not self._document.check_state(DocumentState.OPENED):
            return HwpResult.fail(
                f"Cannot close document: current state is {self._document.state}"
            )

        try:
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

            return HwpResult.ok({"state": DocumentState.CLOSED.value})

        except Exception as e:
            return HwpResult.fail(f"COM error: {e}")

    def save_document(self) -> HwpResult:
        """
        Save the current document.

        State transition: Modified → Saved
        Matches: FileSave action (NoParam)
        """
        if not self._document.check_state(DocumentState.MODIFIED):
            return HwpResult.fail(
                f"Cannot save document: current state is {self._document.state}"
            )

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

    def insert_text(self, text: str) -> HwpResult:
        """
        Insert text into the document.

        State transition: Opened → Modified
        Matches: InsertText action (RequiredParam)
        """
        if not self._document.check_state(DocumentState.OPENED):
            return HwpResult.fail(
                f"Cannot insert text: current state is {self._document.state}"
            )

        try:
            # Execute InsertText action
            action = self.hwp.CreateAction("InsertText")
            if action is None:
                return HwpResult.fail("InsertText action not found")

            param_set = action.CreateSet()
            action.GetDefault(param_set)
            param_set.SetItem("Text", text)

            if not action.Execute(param_set):
                return HwpResult.fail("Failed to insert text")

            self._document.transition_state(DocumentState.MODIFIED)

            return HwpResult.ok({
                "state": DocumentState.MODIFIED.value,
                "text_length": len(text)
            })

        except Exception as e:
            return HwpResult.fail(f"COM error: {e}")

    def create_table(self, rows: int, cols: int) -> HwpResult:
        """
        Create a table in the document.

        State transition: Opened → Modified
        Matches: TableCreate action (RequiredParam)
        """
        if not self._document.check_state(DocumentState.OPENED):
            return HwpResult.fail(
                f"Cannot create table: current state is {self._document.state}"
            )

        if rows < 1 or cols < 1:
            return HwpResult.fail(f"Invalid table size: {rows}x{cols}")

        try:
            # Execute TableCreate action
            action = self.hwp.CreateAction("TableCreate")
            if action is None:
                return HwpResult.fail("TableCreate action not found")

            param_set = action.CreateSet()
            action.GetDefault(param_set)
            param_set.SetItem("Rows", rows)
            param_set.SetItem("Cols", cols)

            if not action.Execute(param_set):
                return HwpResult.fail(f"Failed to create table {rows}x{cols}")

            self._document.transition_state(DocumentState.MODIFIED)

            return HwpResult.ok({
                "state": DocumentState.MODIFIED.value,
                "rows": rows,
                "cols": cols
            })

        except Exception as e:
            return HwpResult.fail(f"COM error: {e}")

    def cleanup(self) -> None:
        """Clean up COM resources."""
        if self._hwp is not None:
            try:
                if not self._document.check_state(DocumentState.CLOSED):
                    self.close_document()
                self._hwp.Quit()
            except Exception:
                pass
            finally:
                self._hwp = None
                pythoncom.CoUninitialize()
