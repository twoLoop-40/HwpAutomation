"""UI 런처 실행"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from ui.main import HwpAutomationLauncher

if __name__ == "__main__":
    app = HwpAutomationLauncher()
    app.run()
