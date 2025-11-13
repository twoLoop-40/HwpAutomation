"""MCP tools for HWP automation - matches Idris MCPTool specification."""

from typing import Any, Optional, Callable
from mcp.types import Tool, TextContent
import mcp.server.stdio

from .hwp_client import HwpClient
from .types import HwpResult


# Tool definitions matching Specs/HwpMCP.idr mcpTools
TOOLS = [
    Tool(
        name="hwp_create_document",
        description="새 한글 문서 생성 (Create new HWP document)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_open_document",
        description="한글 문서 열기 (Open existing HWP document)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the HWP file to open",
                }
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="hwp_close_document",
        description="현재 문서 닫기 (Close current document)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_save_document",
        description="문서 저장 (Save current document)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_insert_text",
        description="텍스트 삽입 (Insert text into document)",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to insert into the document",
                }
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="hwp_create_table",
        description="표 만들기 (Create table in document)",
        inputSchema={
            "type": "object",
            "properties": {
                "rows": {
                    "type": "integer",
                    "description": "Number of rows",
                    "minimum": 1,
                },
                "cols": {
                    "type": "integer",
                    "description": "Number of columns",
                    "minimum": 1,
                },
            },
            "required": ["rows", "cols"],
        },
    ),
    Tool(
        name="hwp_get_document_state",
        description="현재 문서 상태 조회 (Get current document state)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]


class ToolHandler:
    """Handler for MCP tool calls."""

    def __init__(self):
        """Initialize tool handler with HWP client."""
        self.client = HwpClient()

    # ========== Helper Methods ==========

    def _create_response(self, success: bool, message: str) -> list[TextContent]:
        """Create a standardized response with emoji."""
        icon = "✅" if success else "❌"
        return [TextContent(type="text", text=f"{icon} {message}")]

    def _format_success_message(
        self, action: str, details: dict[str, Any]
    ) -> str:
        """Format success message with details."""
        lines = [f"{action}"]
        for key, value in details.items():
            if value is not None:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    def _format_error_message(self, action: str, error: str) -> str:
        """Format error message."""
        return f"{action} 실패: {error}"

    def _validate_required_params(
        self, arguments: dict[str, Any], required: list[str]
    ) -> tuple[bool, str]:
        """
        Validate required parameters.

        Returns:
            (is_valid, error_message)
        """
        for param in required:
            if param not in arguments or arguments[param] is None:
                return False, f"필수 파라미터 '{param}'가 없습니다."
        return True, ""

    def _execute_action(
        self,
        action_name: str,
        action_func: Callable,
        arguments: dict[str, Any],
        required_params: Optional[list[str]] = None,
        success_details_extractor: Optional[Callable] = None,
    ) -> list[TextContent]:
        """
        Generic action executor with validation and formatting.

        Args:
            action_name: Display name for the action
            action_func: Client method to call
            arguments: Tool arguments
            required_params: List of required parameter names
            success_details_extractor: Function to extract details from result
        """
        # 1. Validate parameters
        if required_params:
            valid, error_msg = self._validate_required_params(
                arguments, required_params
            )
            if not valid:
                return self._create_response(False, error_msg)

        # 2. Execute action
        try:
            result = action_func(**arguments)
        except Exception as e:
            return self._create_response(False, f"실행 오류: {str(e)}")

        # 3. Format response
        if result.success:
            if success_details_extractor:
                details = success_details_extractor(result.value)
            else:
                details = result.value or {}
            msg = self._format_success_message(action_name, details)
        else:
            msg = self._format_error_message(action_name, result.error)

        return self._create_response(result.success, msg)

    # ========== Tool Handlers ==========

    def handle_create_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_create_document tool call."""
        return self._execute_action(
            action_name="새 문서 생성",
            action_func=self.client.create_new_document,
            arguments={},
            success_details_extractor=lambda v: {"상태": v["state"]},
        )

    def handle_open_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_open_document tool call."""
        return self._execute_action(
            action_name="문서 열기",
            action_func=self.client.open_document,
            arguments=arguments,
            required_params=["path"],
            success_details_extractor=lambda v: {
                "경로": v["path"],
                "상태": v["state"],
            },
        )

    def handle_close_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_close_document tool call."""
        return self._execute_action(
            action_name="문서 닫기",
            action_func=self.client.close_document,
            arguments={},
            success_details_extractor=lambda v: {
                "상태": v["state"],
                "경고": v.get("warning"),
            },
        )

    def handle_save_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_save_document tool call."""
        return self._execute_action(
            action_name="문서 저장",
            action_func=self.client.save_document,
            arguments={},
            success_details_extractor=lambda v: {
                "경로": v["path"],
                "상태": v["state"],
            },
        )

    def handle_insert_text(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_insert_text tool call."""
        return self._execute_action(
            action_name="텍스트 삽입",
            action_func=self.client.insert_text,
            arguments=arguments,
            required_params=["text"],
            success_details_extractor=lambda v: {
                "길이": f"{v['text_length']} 글자",
                "상태": v["state"],
            },
        )

    def handle_create_table(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_create_table tool call."""
        return self._execute_action(
            action_name="표 생성",
            action_func=self.client.create_table,
            arguments=arguments,
            required_params=["rows", "cols"],
            success_details_extractor=lambda v: {
                "크기": f"{v['rows']}x{v['cols']}",
                "상태": v["state"],
            },
        )

    def handle_get_document_state(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle hwp_get_document_state tool call."""
        doc = self.client.document
        state_info = f"""📄 현재 문서 상태:
상태: {doc.state.value}
경로: {doc.path or '(없음)'}
"""
        return [TextContent(type="text", text=state_info)]

    # ========== Router ==========

    def handle_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool call to appropriate handler."""
        handlers = {
            "hwp_create_document": self.handle_create_document,
            "hwp_open_document": self.handle_open_document,
            "hwp_close_document": self.handle_close_document,
            "hwp_save_document": self.handle_save_document,
            "hwp_insert_text": self.handle_insert_text,
            "hwp_create_table": self.handle_create_table,
            "hwp_get_document_state": self.handle_get_document_state,
        }

        handler = handlers.get(name)
        if handler is None:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Unknown tool: {name}",
                )
            ]

        try:
            return handler(arguments)
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Error executing {name}: {str(e)}",
                )
            ]

    def cleanup(self) -> None:
        """Clean up resources."""
        self.client.cleanup()

