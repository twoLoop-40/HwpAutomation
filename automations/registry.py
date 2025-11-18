"""
Plugin Registry

플러그인 등록 및 관리
"""

from typing import Dict, List, Optional, Type
from .base import AutomationBase, PluginMetadata


class PluginRegistry:
    """플러그인 레지스트리"""

    def __init__(self):
        self._plugins: Dict[str, Type[AutomationBase]] = {}
        self._instances: Dict[str, AutomationBase] = {}

    def register(self, plugin_class: Type[AutomationBase]):
        """
        플러그인 등록

        Args:
            plugin_class: AutomationBase를 상속한 플러그인 클래스
        """
        # 임시 인스턴스로 메타데이터 가져오기
        temp_instance = plugin_class()
        metadata = temp_instance.get_metadata()

        self._plugins[metadata.id] = plugin_class
        print(f"Registered plugin: {metadata.name} (v{metadata.version})")

    def get_plugin(self, plugin_id: str) -> Optional[AutomationBase]:
        """
        플러그인 인스턴스 가져오기 (싱글톤)

        Args:
            plugin_id: 플러그인 ID

        Returns:
            플러그인 인스턴스 또는 None
        """
        if plugin_id not in self._plugins:
            return None

        # 싱글톤 패턴
        if plugin_id not in self._instances:
            self._instances[plugin_id] = self._plugins[plugin_id]()

        return self._instances[plugin_id]

    def get_all_metadata(self) -> List[PluginMetadata]:
        """등록된 모든 플러그인의 메타데이터 반환"""
        metadata_list = []
        for plugin_class in self._plugins.values():
            temp_instance = plugin_class()
            metadata_list.append(temp_instance.get_metadata())
        return metadata_list

    def list_plugins(self) -> List[str]:
        """등록된 플러그인 ID 목록"""
        return list(self._plugins.keys())


# 전역 레지스트리
_global_registry = PluginRegistry()


def get_registry() -> PluginRegistry:
    """전역 레지스트리 반환"""
    return _global_registry


def register_plugin(plugin_class: Type[AutomationBase]):
    """플러그인 등록 (데코레이터로도 사용 가능)"""
    _global_registry.register(plugin_class)
    return plugin_class
