"""MCP tools for ActionTable operations.

Based on HwpBooks/ActionTable_2504.pdf and Specs/HwpMCP.idr
"""

from typing import Any
from mcp.types import Tool, TextContent

from .client import ActionTableClient
from ..common.types import HwpResult


# ActionTable tool definitions - prefix with hwp_action_
ACTION_TABLE_TOOLS = [
    Tool(
        name="hwp_action_create_document",
        description="[ActionTable] 새 한글 문서 생성 (Create new HWP document) - FileNew",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_action_open_document",
        description="[ActionTable] 한글 문서 열기 (Open existing HWP document) - FileOpen",
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
        name="hwp_action_close_document",
        description="[ActionTable] 현재 문서 닫기 (Close current document) - FileClose",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_action_save_document",
        description="[ActionTable] 문서 저장 (Save current document) - FileSave",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
    Tool(
        name="hwp_action_insert_text",
        description="[ActionTable] 텍스트 삽입 (Insert text into document) - InsertText",
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
        name="hwp_action_create_table",
        description="[ActionTable] 표 만들기 (Create table in document) - TableCreate",
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
        name="hwp_action_get_document_state",
        description="[ActionTable] 현재 문서 상태 조회 (Get current document state)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    ),
]


class ActionTableToolHandler:
    """Handler for ActionTable MCP tool calls."""

    def __init__(self):
        """Initialize tool handler with ActionTable client."""
        self.client = ActionTableClient()

    def handle_create_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_create_document tool call."""
        result = self.client.create_new_document()

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 새 문서를 생성했습니다.\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 문서 생성 실패: {result.error}",
                )
            ]

    def handle_open_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_open_document tool call."""
        path = arguments.get("path")
        if not path:
            return [
                TextContent(
                    type="text",
                    text="❌ 파일 경로가 필요합니다.",
                )
            ]

        result = self.client.open_document(path)

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 문서를 열었습니다.\n경로: {result.value['path']}\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 문서 열기 실패: {result.error}",
                )
            ]

    def handle_close_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_close_document tool call."""
        result = self.client.close_document()

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 문서를 닫았습니다.\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 문서 닫기 실패: {result.error}",
                )
            ]

    def handle_save_document(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_save_document tool call."""
        result = self.client.save_document()

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 문서를 저장했습니다.\n경로: {result.value['path']}\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 문서 저장 실패: {result.error}",
                )
            ]

    def handle_insert_text(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_insert_text tool call."""
        text = arguments.get("text")
        if not text:
            return [
                TextContent(
                    type="text",
                    text="❌ 삽입할 텍스트가 필요합니다.",
                )
            ]

        result = self.client.insert_text(text)

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 텍스트를 삽입했습니다.\n길이: {result.value['text_length']} 글자\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 텍스트 삽입 실패: {result.error}",
                )
            ]

    def handle_create_table(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle hwp_action_create_table tool call."""
        rows = arguments.get("rows")
        cols = arguments.get("cols")

        if rows is None or cols is None:
            return [
                TextContent(
                    type="text",
                    text="❌ 행(rows)과 열(cols) 개수가 필요합니다.",
                )
            ]

        result = self.client.create_table(rows, cols)

        if result.success:
            return [
                TextContent(
                    type="text",
                    text=f"✅ 표를 생성했습니다.\n크기: {result.value['rows']}x{result.value['cols']}\n상태: {result.value['state']}",
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"❌ 표 생성 실패: {result.error}",
                )
            ]

    def handle_get_document_state(
        self, arguments: dict[str, Any]
    ) -> list[TextContent]:
        """Handle hwp_action_get_document_state tool call."""
        doc = self.client.document
        state_info = f"""📄 현재 문서 상태:
- 상태: {doc.state.value}
- 경로: {doc.path or '(없음)'}
"""

        return [TextContent(type="text", text=state_info)]

    def handle_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Route tool call to appropriate handler."""
        handlers = {
            "hwp_action_create_document": self.handle_create_document,
            "hwp_action_open_document": self.handle_open_document,
            "hwp_action_close_document": self.handle_close_document,
            "hwp_action_save_document": self.handle_save_document,
            "hwp_action_insert_text": self.handle_insert_text,
            "hwp_action_create_table": self.handle_create_table,
            "hwp_action_get_document_state": self.handle_get_document_state,
        }

        handler = handlers.get(name)
        if handler is None:
            return [
                TextContent(
                    type="text",
                    text=f"❌ Unknown ActionTable tool: {name}",
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
