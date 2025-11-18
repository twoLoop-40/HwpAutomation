"""
HWP COM Client

pywin32 기반 한글 COM 클라이언트
모든 플러그인이 이 클라이언트를 통해 HWP를 제어합니다.
"""

import win32com.client
from typing import Optional
from .types import DocumentState


class HwpClient:
    """HWP COM 클라이언트"""

    def __init__(self):
        self.hwp = None
        self.state = DocumentState.CLOSED

    def start(self) -> bool:
        """HWP 프로세스 시작"""
        try:
            self.hwp = win32com.client.gencache.EnsureDispatch("HWPFrame.HwpObject")
            return True
        except Exception as e:
            print(f"Failed to start HWP: {e}")
            return False

    def quit(self):
        """HWP 프로세스 종료"""
        if self.hwp:
            try:
                self.hwp.Quit()
            except:
                pass
            self.hwp = None
            self.state = DocumentState.CLOSED

    def get_hwp(self):
        """HWP 객체 반환"""
        if not self.hwp:
            self.start()
        return self.hwp

    def __enter__(self):
        """Context manager 진입"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.quit()
