"""Unified MCP tools registry for HWP automation.

Integrates tools from:
- ActionTable (action_table.tools)
- Automation (automation.tools) - to be added

Matches Idris MCPTool specification in Specs/HwpMCP.idr
"""

from typing import Any
from mcp.types import Tool, TextContent

from .action_table import ACTION_TABLE_TOOLS, ActionTableToolHandler

# Future: from .automation import AUTOMATION_TOOLS, AutomationToolHandler


# Unified tool registry
ALL_TOOLS = ACTION_TABLE_TOOLS  # + AUTOMATION_TOOLS (future)


class UnifiedToolHandler:
    """Unified handler for all MCP tool calls."""

    def __init__(self):
        """Initialize all tool handlers."""
        self.action_table_handler = ActionTableToolHandler()
        # Future: self.automation_handler = AutomationToolHandler()

    def handle_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool call to appropriate handler based on name prefix."""
        # ActionTable tools: hwp_action_*
        if name.startswith("hwp_action_"):
            return self.action_table_handler.handle_call(name, arguments)

        # Future: Automation tools: hwp_auto_*
        # if name.startswith("hwp_auto_"):
        #     return self.automation_handler.handle_call(name, arguments)

        # Unknown tool
        return [
            TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}",
            )
        ]

    def cleanup(self) -> None:
        """Clean up all handler resources."""
        self.action_table_handler.cleanup()
        # Future: self.automation_handler.cleanup()
