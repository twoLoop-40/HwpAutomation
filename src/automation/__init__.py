"""HWP Automation API module (OLE Object Model)."""

from .client import AutomationClient
from .tools import AUTOMATION_TOOLS, AutomationToolHandler

__all__ = ["AutomationClient", "AUTOMATION_TOOLS", "AutomationToolHandler"]
