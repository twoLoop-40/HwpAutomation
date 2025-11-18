"""
MCP Configuration
"""

from dataclasses import dataclass


@dataclass
class MCPConfig:
    """MCP 서버 설정"""
    transport: str = "stdio"
    log_level: str = "INFO"
    claude_config_path: str = "%APPDATA%\\Claude\\claude_desktop_config.json"
