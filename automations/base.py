"""
Automation Base Class

모든 플러그인이 상속해야 하는 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PluginMetadata:
    """플러그인 메타데이터"""
    id: str  # 고유 ID
    name: str  # 표시 이름
    description: str  # 설명
    version: str  # 버전
    author: str  # 작성자
    icon: Optional[str] = None  # 아이콘 경로


class AutomationBase(ABC):
    """
    자동화 플러그인 기본 클래스

    모든 플러그인은 이 클래스를 상속하고
    필수 메서드들을 구현해야 합니다.
    """

    def __init__(self):
        self.metadata = self.get_metadata()
        self.config = {}

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터 반환"""
        pass

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        플러그인 실행

        Returns:
            결과 딕셔너리 {"success": bool, "message": str, ...}
        """
        pass

    def has_ui(self) -> bool:
        """UI가 있는지 여부 (기본: False)"""
        return False

    def has_cli(self) -> bool:
        """CLI가 있는지 여부 (기본: True)"""
        return True

    def load_config(self, config: Dict[str, Any]):
        """설정 로드"""
        self.config = config

    def get_config_schema(self) -> Dict[str, Any]:
        """설정 스키마 반환 (JSON Schema 형식)"""
        return {}

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """설정 유효성 검증"""
        return True
