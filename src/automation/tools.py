"""MCP tools for HWP Automation API.

Based on Specs/AutomationMCP.idr formal specification.
"""

from typing import Any
from mcp.types import Tool
from .client import AutomationClient


# MCP Tool definitions for Automation API
AUTOMATION_TOOLS = [
    Tool(
        name="hwp_auto_get_documents",
        description="문서 컬렉션(IXHwpDocuments) 가져오기",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_open_document",
        description="HWP 문서 열기 (Automation API 사용)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "열 HWP 파일 경로"
                },
                "format": {
                    "type": "string",
                    "description": "파일 포맷 (선택사항)"
                }
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="hwp_auto_get_active_document",
        description="현재 활성 문서 가져오기",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_document_property",
        description="문서 속성 값 가져오기 (Path, IsModified, DocumentName 등)",
        inputSchema={
            "type": "object",
            "properties": {
                "property_name": {
                    "type": "string",
                    "description": "속성 이름 (Path, IsModified, DocumentName, ParentWindow)"
                }
            },
            "required": ["property_name"]
        }
    ),
    Tool(
        name="hwp_auto_save_document",
        description="문서 저장 (Automation API 사용)",
        inputSchema={
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "description": "저장 포맷 (선택사항)"
                },
                "options": {
                    "type": "string",
                    "description": "저장 옵션 (선택사항)"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_close_document",
        description="문서 닫기 (Automation API 사용)",
        inputSchema={
            "type": "object",
            "properties": {
                "save_changes": {
                    "type": "boolean",
                    "description": "닫기 전 변경사항 저장 여부",
                    "default": False
                }
            },
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_windows",
        description="창 컬렉션(IXHwpWindows) 가져오기",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_active_window",
        description="현재 활성 창 가져오기",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_hwp_property",
        description="HWP 어플리케이션 속성 가져오기 (Version, IsEmpty, EditMode, Path)",
        inputSchema={
            "type": "object",
            "properties": {
                "property_name": {
                    "type": "string",
                    "description": "속성 이름 (Version, IsEmpty, EditMode, Path)"
                }
            },
            "required": ["property_name"]
        }
    ),
    Tool(
        name="hwp_auto_set_edit_mode",
        description="편집 모드 설정 (0=읽기전용, 1-16=다양한 편집 모드)",
        inputSchema={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "integer",
                    "description": "편집 모드 (0: 읽기전용, 1-16: 편집 모드)"
                }
            },
            "required": ["mode"]
        }
    ),
    Tool(
        name="hwp_auto_quit",
        description="HWP 어플리케이션 종료",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # State Query Tools (EventHandler Alternative - Option B)
    # Based on Specs/AutomationState.idr
    Tool(
        name="hwp_auto_is_document_modified",
        description="""[상태 조회] 문서 수정 여부 확인 (EventHandler DocumentChange 대체)

        Agent 활용: 저장 여부 판단, 변경사항 감지
        반환: {"is_modified": bool, "status": str}
        """,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_document_path",
        description="""[상태 조회] 문서 경로 가져오기 (EventHandler DocumentAfterOpen/Save 대체)

        Agent 활용: 문서 열림/저장 상태 감지, 파일 경로 확인
        반환: {"has_path": bool, "path": str, "status": str}
        """,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_edit_mode",
        description="""[상태 조회] 편집 모드 확인 (ReadOnly/Editable)

        Agent 활용: 편집 가능 여부 사전 검증, 읽기 전용 감지
        반환: {"edit_mode": str, "raw_value": int}
        """,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_document_count",
        description="""[상태 조회] 열린 문서 개수 확인 (EventHandler DocumentAfterOpen/Close 대체)

        Agent 활용: 문서 열림/닫힘 감지, 작업 전 문서 존재 확인
        반환: {"count": int}
        """,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="hwp_auto_get_state_snapshot",
        description="""[상태 조회] 문서 상태 스냅샷 (통합 조회)

        Agent 활용: 전체 상태를 한 번에 조회하여 효율적인 변경 감지
        반환: {
            "is_modified": bool,
            "has_path": bool,
            "path": str,
            "edit_mode": str,
            "document_count": int
        }
        """,
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]


class AutomationToolHandler:
    """Handler for Automation API MCP tools."""

    def __init__(self):
        """Initialize automation tool handler."""
        self.client = AutomationClient()
        self._active_doc: Any = None  # Track active document for operations

    def handle_tool(self, name: str, arguments: dict) -> dict:
        """
        Route tool calls to appropriate handler methods.

        Args:
            name: Tool name (hwp_auto_*)
            arguments: Tool arguments

        Returns:
            dict with result
        """
        handlers = {
            "hwp_auto_get_documents": self._handle_get_documents,
            "hwp_auto_open_document": self._handle_open_document,
            "hwp_auto_get_active_document": self._handle_get_active_document,
            "hwp_auto_get_document_property": self._handle_get_document_property,
            "hwp_auto_save_document": self._handle_save_document,
            "hwp_auto_close_document": self._handle_close_document,
            "hwp_auto_get_windows": self._handle_get_windows,
            "hwp_auto_get_active_window": self._handle_get_active_window,
            "hwp_auto_get_hwp_property": self._handle_get_hwp_property,
            "hwp_auto_set_edit_mode": self._handle_set_edit_mode,
            "hwp_auto_quit": self._handle_quit,
            # State query handlers (EventHandler alternative)
            "hwp_auto_is_document_modified": self._handle_is_document_modified,
            "hwp_auto_get_document_path": self._handle_get_document_path,
            "hwp_auto_get_edit_mode": self._handle_get_edit_mode,
            "hwp_auto_get_document_count": self._handle_get_document_count,
            "hwp_auto_get_state_snapshot": self._handle_get_state_snapshot,
        }

        handler = handlers.get(name)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown tool: {name}"
            }

        return handler(arguments)

    def _handle_get_documents(self, args: dict) -> dict:
        """Handle hwp_auto_get_documents."""
        result = self.client.get_documents()
        if result.success:
            return {
                "success": True,
                "count": result.value.get("count", 0)
            }
        return {"success": False, "error": result.error}

    def _handle_open_document(self, args: dict) -> dict:
        """Handle hwp_auto_open_document."""
        path = args.get("path")
        format_str = args.get("format")

        result = self.client.open_document(path, format_str)
        if result.success:
            self._active_doc = result.value.get("document")
            return {
                "success": True,
                "path": result.value.get("path")
            }
        return {"success": False, "error": result.error}

    def _handle_get_active_document(self, args: dict) -> dict:
        """Handle hwp_auto_get_active_document."""
        result = self.client.get_active_document()
        if result.success:
            self._active_doc = result.value.get("document")
            return {
                "success": True,
                "message": "Active document retrieved"
            }
        return {"success": False, "error": result.error}

    def _handle_get_document_property(self, args: dict) -> dict:
        """Handle hwp_auto_get_document_property."""
        if self._active_doc is None:
            return {
                "success": False,
                "error": "No active document. Open or get a document first."
            }

        property_name = args.get("property_name")
        result = self.client.get_document_property(self._active_doc, property_name)

        if result.success:
            return {
                "success": True,
                "property": property_name,
                "value": result.value.get(property_name)
            }
        return {"success": False, "error": result.error}

    def _handle_save_document(self, args: dict) -> dict:
        """Handle hwp_auto_save_document."""
        if self._active_doc is None:
            return {
                "success": False,
                "error": "No active document. Open or get a document first."
            }

        format_str = args.get("format")
        options = args.get("options")

        result = self.client.save_document(self._active_doc, format_str, options)
        if result.success:
            return {
                "success": True,
                "saved": result.value.get("saved")
            }
        return {"success": False, "error": result.error}

    def _handle_close_document(self, args: dict) -> dict:
        """Handle hwp_auto_close_document."""
        if self._active_doc is None:
            return {
                "success": False,
                "error": "No active document. Open or get a document first."
            }

        save_changes = args.get("save_changes", False)
        result = self.client.close_document(self._active_doc, save_changes)

        if result.success:
            self._active_doc = None
            return {
                "success": True,
                "closed": result.value.get("closed")
            }
        return {"success": False, "error": result.error}

    def _handle_get_windows(self, args: dict) -> dict:
        """Handle hwp_auto_get_windows."""
        result = self.client.get_windows()
        if result.success:
            return {
                "success": True,
                "count": result.value.get("count", 0)
            }
        return {"success": False, "error": result.error}

    def _handle_get_active_window(self, args: dict) -> dict:
        """Handle hwp_auto_get_active_window."""
        result = self.client.get_active_window()
        if result.success:
            return {
                "success": True,
                "message": "Active window retrieved"
            }
        return {"success": False, "error": result.error}

    def _handle_get_hwp_property(self, args: dict) -> dict:
        """Handle hwp_auto_get_hwp_property."""
        property_name = args.get("property_name")
        result = self.client.get_hwp_property(property_name)

        if result.success:
            return {
                "success": True,
                "property": property_name,
                "value": result.value.get(property_name)
            }
        return {"success": False, "error": result.error}

    def _handle_set_edit_mode(self, args: dict) -> dict:
        """Handle hwp_auto_set_edit_mode."""
        mode = args.get("mode")
        result = self.client.set_hwp_property("EditMode", mode)

        if result.success:
            return {
                "success": True,
                "edit_mode": mode
            }
        return {"success": False, "error": result.error}

    def _handle_quit(self, args: dict) -> dict:
        """Handle hwp_auto_quit."""
        result = self.client.quit()
        if result.success:
            self._active_doc = None
            return {
                "success": True,
                "quit": True
            }
        return {"success": False, "error": result.error}

    # State Query Handlers (EventHandler Alternative - Option B)
    # Based on Specs/AutomationState.idr

    def _handle_is_document_modified(self, args: dict) -> dict:
        """Handle hwp_auto_is_document_modified."""
        result = self.client.is_document_modified()
        if result.success:
            return {
                "success": True,
                "is_modified": result.value["is_modified"],
                "status": result.value["status"]
            }
        return {"success": False, "error": result.error}

    def _handle_get_document_path(self, args: dict) -> dict:
        """Handle hwp_auto_get_document_path."""
        result = self.client.get_document_path()
        if result.success:
            return {
                "success": True,
                "has_path": result.value["has_path"],
                "path": result.value["path"],
                "status": result.value["status"]
            }
        return {"success": False, "error": result.error}

    def _handle_get_edit_mode(self, args: dict) -> dict:
        """Handle hwp_auto_get_edit_mode."""
        result = self.client.get_edit_mode()
        if result.success:
            return {
                "success": True,
                "edit_mode": result.value["edit_mode"],
                "raw_value": result.value["raw_value"]
            }
        return {"success": False, "error": result.error}

    def _handle_get_document_count(self, args: dict) -> dict:
        """Handle hwp_auto_get_document_count."""
        result = self.client.get_document_count()
        if result.success:
            return {
                "success": True,
                "count": result.value["count"]
            }
        return {"success": False, "error": result.error}

    def _handle_get_state_snapshot(self, args: dict) -> dict:
        """Handle hwp_auto_get_state_snapshot."""
        result = self.client.get_state_snapshot()
        if result.success:
            return {
                "success": True,
                **result.value  # Spread all snapshot fields
            }
        return {"success": False, "error": result.error}

    def cleanup(self) -> None:
        """Clean up resources."""
        self.client.cleanup()
        self._active_doc = None
