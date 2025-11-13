"""Type definitions based on Specs/HwpCommon.idr formal specification."""

from enum import Enum
from typing import Union, Optional, Any
from pydantic import BaseModel, Field


class DocumentState(str, Enum):
    """Document state lifecycle - matches Idris spec."""
    CLOSED = "Closed"
    OPENED = "Opened"
    MODIFIED = "Modified"
    SAVED = "Saved"


class ActionRequirement(str, Enum):
    """Parameter requirements for actions - matches Idris spec."""
    NO_PARAM = "NoParam"  # No ParameterSet needed (-)
    OPTIONAL_PARAM = "OptionalParam"  # ParameterSet optional
    REQUIRED_PARAM = "RequiredParam"  # ParameterSet required
    READ_ONLY = "ReadOnly"  # Read-only action (*)


class ParamValue(BaseModel):
    """Parameter value types supported by HWP COM."""
    value: Union[str, int, bool, float]

    @property
    def type_name(self) -> str:
        if isinstance(self.value, str):
            return "PString"
        elif isinstance(self.value, int):
            return "PInt"
        elif isinstance(self.value, bool):
            return "PBool"
        elif isinstance(self.value, float):
            return "PDouble"
        raise ValueError(f"Unsupported type: {type(self.value)}")


class ParameterSet(BaseModel):
    """Parameter set for actions that require parameters."""
    params: dict[str, ParamValue] = Field(default_factory=dict)

    def add_param(self, name: str, value: Union[str, int, bool, float]) -> None:
        self.params[name] = ParamValue(value=value)


class HwpError(Exception):
    """Base class for HWP operation errors."""
    pass


class ActionNotFound(HwpError):
    """Action ID not found."""
    def __init__(self, action_id: str):
        super().__init__(f"Action not found: {action_id}")


class InvalidParameter(HwpError):
    """Invalid parameter provided."""
    def __init__(self, msg: str):
        super().__init__(f"Invalid parameter: {msg}")


class DocumentNotOpen(HwpError):
    """Document is not open."""
    def __init__(self):
        super().__init__("Document is not open")


class DocumentAlreadyOpen(HwpError):
    """Document is already open."""
    def __init__(self):
        super().__init__("Document is already open")


class COMError(HwpError):
    """COM operation error."""
    def __init__(self, msg: str):
        super().__init__(f"COM error: {msg}")


class InvalidState(HwpError):
    """Invalid document state for operation."""
    def __init__(self, current: DocumentState, expected: DocumentState):
        super().__init__(
            f"Invalid state: current={current.value}, expected={expected.value}"
        )


class HwpFileNotFoundError(HwpError):
    """HWP file not found."""
    def __init__(self, path: str):
        super().__init__(f"File not found: {path}")


class DocumentHandle(BaseModel):
    """A document handle that tracks state - matches Idris spec."""
    path: Optional[str] = None
    state: DocumentState = DocumentState.CLOSED

    def transition_state(self, new_state: DocumentState) -> None:
        """Transition document state."""
        self.state = new_state

    def check_state(self, expected: DocumentState) -> bool:
        """Check if document is in expected state."""
        return self.state == expected


class HwpResult(BaseModel):
    """Result type for HWP operations - matches Idris HwpResult monad."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, value: Any = None) -> "HwpResult":
        return cls(success=True, value=value)

    @classmethod
    def fail(cls, error: str) -> "HwpResult":
        return cls(success=False, error=error)
