"""
HwpAutomation Plugins

자동화 작업 플러그인들
"""

from .base import AutomationBase, PluginMetadata
from .registry import PluginRegistry, get_registry, register_plugin

__all__ = [
    "AutomationBase",
    "PluginMetadata",
    "PluginRegistry",
    "get_registry",
    "register_plugin",
]

__version__ = "2.0.0"
