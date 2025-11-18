"""
MCP Server Plugin

Claude Desktop 연동을 위한 MCP 서버
"""

from automations import AutomationBase, PluginMetadata, register_plugin
from typing import Dict, Any
import asyncio


@register_plugin
class MCPPlugin(AutomationBase):
    """MCP 서버 플러그인"""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="mcp",
            name="MCP 서버",
            description="Claude Desktop 통합을 위한 MCP 서버",
            version="1.0.0",
            author="HwpAutomation Team",
            icon="icons/mcp.png"
        )

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        MCP 서버 실행

        Args:
            background: 백그라운드 실행 여부

        Returns:
            {"success": bool, "message": str}
        """
        try:
            from .server import main as mcp_main

            background = kwargs.get("background", False)

            if background:
                # 백그라운드 실행
                return {
                    "success": True,
                    "message": "MCP 서버를 백그라운드에서 시작합니다."
                }
            else:
                # 포그라운드 실행 (블로킹)
                asyncio.run(mcp_main())
                return {
                    "success": True,
                    "message": "MCP 서버가 종료되었습니다."
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"MCP 서버 실행 실패: {str(e)}"
            }

    def has_ui(self) -> bool:
        """UI 없음 (CLI만)"""
        return False

    def has_cli(self) -> bool:
        """CLI 있음"""
        return True

    def get_config_schema(self) -> Dict[str, Any]:
        """설정 스키마"""
        return {
            "type": "object",
            "properties": {
                "transport": {
                    "type": "string",
                    "description": "Transport 방식",
                    "enum": ["stdio"],
                    "default": "stdio"
                },
                "log_level": {
                    "type": "string",
                    "description": "로그 레벨",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR"],
                    "default": "INFO"
                }
            }
        }
