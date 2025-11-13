"""HWP MCP Server - Hangul Word Processor automation via MCP."""

from .common.types import DocumentState, HwpResult, DocumentHandle
from .action_table.client import ActionTableClient

# Legacy aliases for backward compatibility
HwpClient = ActionTableClient

__all__ = [
    "DocumentState",
    "HwpResult",
    "DocumentHandle",
    "ActionTableClient",
    "HwpClient",  # Legacy alias
]
