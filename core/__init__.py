"""
HwpAutomation Core Module

공통 HWP API 래퍼 및 유틸리티
모든 플러그인이 이 모듈을 사용하여 HWP를 제어합니다.
"""

from .hwp_client import HwpClient
from .automation_client import AutomationClient
from .types import DocumentState
from .sync import wait_for_idle

__all__ = [
    "HwpClient",
    "AutomationClient",
    "DocumentState",
    "wait_for_idle",
]

__version__ = "2.0.0"
