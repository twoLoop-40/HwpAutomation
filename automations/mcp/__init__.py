"""
MCP Server Plugin

Claude Desktop 연동을 위한 MCP 서버 (기존 src)
"""

from .plugin import MCPPlugin
from .config import MCPConfig

__all__ = ["MCPPlugin", "MCPConfig"]
