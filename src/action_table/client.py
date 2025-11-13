"""ActionTable HWP COM client wrapper with state management.

Based on HwpBooks/ActionTable_2504.pdf
"""

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
    HwpFileNotFoundError,
    COMError,
)

from .param_validator import ParameterValidator


class ActionTableClient:
    """
    ActionTable HWP COM client wrapper with type-safe state management.

    Based on the Idris2 formal specification in Specs/ActionTableMCP.idr and
    ActionTable_2504.pdf reference document.

    Ensures safe state transitions and parameter validation for ActionTable operations.
    """

    def __init__(self):
        """Initialize HWP COM client."""
        self._hwp: Optional[Any] = None
        self._document: DocumentHandle = DocumentHandle()
        self._validator: ParameterValidator = ParameterValidator()

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

    def execute_action(
        self,
        action_id: str,
        params: Optional[dict[str, Any]] = None
    ) -> HwpResult:
        """
        Execute any ActionTable API action with type-safe parameter validation.

        Based on Idris2 spec: executeAction : ActionID -> ParameterSet -> HwpResult

        This is a universal action executor that supports all 132 ActionTable actions.
        Parameters are validated against Schema/parameter_table.json and Specs/ParameterTypes.idr.

        Args:
            action_id: Action name (e.g., "InsertText", "CharShape", "BorderFill")
            params: Parameter dictionary (e.g., {"Text": "Hello"})

        Returns:
            HwpResult with success/failure

        Examples:
            >>> # Insert text
            >>> client.execute_action("InsertText", {"Text": "안녕하세요"})

            >>> # Change character shape
            >>> client.execute_action("CharShape", {
            ...     "FaceNameHangul": "맑은 고딕",
            ...     "Height": 1000,
            ...     "Bold": 1
            ... })

            >>> # Set border/fill
            >>> client.execute_action("BorderFill", {
            ...     "BorderTypeLeft": 1,
            ...     "BorderWidthLeft": 10
            ... })
        """
        params = params or {}

        # Step 1: Validate parameters
        if params:
            validation = self._validator.validate_all_parameters(action_id, params)

            if not validation.success:
                error_messages = [
                    f"{err.param_name}: {err.message}" if err.param_name
                    else err.message
                    for err in validation.errors
                ]
                return HwpResult.fail(
                    f"Parameter validation failed for {action_id}:\n" +
                    "\n".join(f"  - {msg}" for msg in error_messages)
                )

            # Log warnings (unknown parameters, etc.)
            if validation.warnings:
                # Warnings don't block execution
                pass

        # Step 2: Create action
        try:
            action = self.hwp.CreateAction(action_id)
            if action is None:
                return HwpResult.fail(f"Action '{action_id}' not found")
        except Exception as e:
            return HwpResult.fail(f"Failed to create action '{action_id}': {e}")

        # Step 3: Create and configure ParameterSet
        try:
            param_set = action.CreateSet()
            action.GetDefault(param_set)

            # Set parameters with type conversion
            for param_name, value in params.items():
                # Convert to appropriate PIT type
                converted_value = self._validator.convert_to_pit_type(
                    action_id, param_name, value
                )
                param_set.SetItem(param_name, converted_value)

        except Exception as e:
            return HwpResult.fail(f"Failed to set parameters for '{action_id}': {e}")

        # Step 4: Execute action
        try:
            result = action.Execute(param_set)

            if not result:
                return HwpResult.fail(f"Action '{action_id}' execution returned false")

            # Update document state for actions that modify the document
            # (Note: This is a simplified heuristic - ideally we'd track this per action)
            if action_id not in ["FileNew", "FileOpen", "FileClose", "FileSave", "FileQuit"]:
                if self._document.check_state(DocumentState.OPENED):
                    self._document.transition_state(DocumentState.MODIFIED)

            return HwpResult.ok({
                "action_id": action_id,
                "parameters": params,
                "state": self._document.state.value
            })

        except Exception as e:
            return HwpResult.fail(f"Execution error for '{action_id}': {e}")

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
