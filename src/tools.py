"""Unified MCP tools registry for HWP automation.

Integrates tools from:
- ActionTable (action_table.tools) - Action-based API
- Automation (automation.tools) - OLE Object Model API

Matches Idris MCPTool specifications:
- Specs/ActionTableMCP.idr
- Specs/AutomationMCP.idr
"""

from typing import Any
from mcp.types import Tool, TextContent

from .action_table import ACTION_TABLE_TOOLS, ActionTableToolHandler
from .automation import AUTOMATION_TOOLS, AutomationToolHandler


# Unified tool registry
ALL_TOOLS = ACTION_TABLE_TOOLS + AUTOMATION_TOOLS


class UnifiedToolHandler:
    """Unified handler for all MCP tool calls."""

    def __init__(self):
        """Initialize all tool handlers."""
        self.action_table_handler = ActionTableToolHandler()
        self.automation_handler = AutomationToolHandler()

    def handle_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool call to appropriate handler based on name prefix."""
        # ActionTable tools: hwp_action_*
        if name.startswith("hwp_action_"):
            return self.action_table_handler.handle_call(name, arguments)

        # Automation tools: hwp_auto_*
        if name.startswith("hwp_auto_"):
            result = self.automation_handler.handle_tool(name, arguments)
            if result.get("success"):
                return [
                    TextContent(
                        type="text",
                        text=f"✅ {name} succeeded: {result}",
                    )
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"❌ {name} failed: {result.get('error')}",
                    )
                ]

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
        self.automation_handler.cleanup()
