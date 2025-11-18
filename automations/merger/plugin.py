"""
Merger Plugin

문제 파일 병합 플러그인
"""

from automations import AutomationBase, PluginMetadata, register_plugin
from typing import Dict, Any


@register_plugin
class MergerPlugin(AutomationBase):
    """문제 파일 병합 플러그인"""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            id="merger",
            name="문제 파일 병합",
            description="HWP 문제 파일들을 2단 편집 양식으로 병합",
            version="1.0.0",
            author="HwpAutomation Team",
            icon="icons/merger.png"
        )

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        병합 실행

        Args:
            csv_path: CSV 파일 경로
            template_path: 양식 파일 경로
            output_path: 출력 파일 경로
            parallel: 병렬 전처리 사용 여부

        Returns:
            {"success": bool, "message": str, "output_path": str}
        """
        try:
            from .merger import ProblemMerger

            csv_path = kwargs.get("csv_path")
            template_path = kwargs.get("template_path")
            output_path = kwargs.get("output_path", "output.hwp")
            parallel = kwargs.get("parallel", True)

            if not csv_path or not template_path:
                return {
                    "success": False,
                    "message": "CSV 파일과 양식 파일 경로가 필요합니다."
                }

            merger = ProblemMerger(csv_path, template_path)
            result = merger.merge(output_path, parallel=parallel)

            return {
                "success": True,
                "message": f"병합 완료: {result['processed_files']}개 파일 처리",
                "output_path": output_path,
                "processed_files": result["processed_files"],
                "duration": result.get("duration", 0)
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"병합 실패: {str(e)}"
            }

    def has_ui(self) -> bool:
        """UI 있음"""
        return True

    def get_config_schema(self) -> Dict[str, Any]:
        """설정 스키마"""
        return {
            "type": "object",
            "properties": {
                "parallel_preprocess": {
                    "type": "boolean",
                    "description": "병렬 전처리 활성화",
                    "default": True
                },
                "max_workers": {
                    "type": "integer",
                    "description": "최대 동시 처리 수",
                    "default": 4,
                    "minimum": 1,
                    "maximum": 20
                },
                "cleanup_temp": {
                    "type": "boolean",
                    "description": "완료 후 임시 파일 삭제",
                    "default": True
                }
            }
        }
