"""
Seperate to Image Plugin

HWP 파일의 내용을 이미지로 분리/변환하는 플러그인입니다.
Idris2 명세: Specs/Seperate2Img/Workflow.idr
"""

from pathlib import Path
from typing import Dict, Any

from automations.base import AutomationBase, PluginMetadata
from automations.registry import register_plugin
from .workflow import Seperate2ImgWorkflow
from .ui import Seperate2ImgUI


@register_plugin
class Seperate2ImgPlugin(AutomationBase):
    """Seperate to Image 플러그인"""

    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터"""
        return PluginMetadata(
            id="seperate2img",
            name="이미지 분리 (Seperate2Img)",
            description="HWP 파일의 문제를 분리하고 각각을 이미지(PNG)로 변환합니다.",
            version="1.0.0",
            author="User",
        )

    def has_ui(self) -> bool:
        """UI 지원 여부"""
        return True

    def run(self, **kwargs) -> Dict[str, Any]:
        """플러그인 실행"""
        if kwargs.get('ui', False):
            self.run_ui()
            return {"success": True}
        
        return self.run_cli(kwargs)

    def run_ui(self):
        """UI 실행 로직"""
        ui = Seperate2ImgUI()

        # 1. 파일 선택
        input_path = ui.open_file_selection()
        if not input_path:
            return

        # 2. 출력 폴더 설정 (자동)
        output_dir = str(Path(input_path).parent / f"{Path(input_path).stem}_images")

        # 3. 옵션 다이얼로그
        options = ui.show_options_dialog()
        if not options:
            return

        # 4. 워크플로우 실행
        ui.show_progress_dialog()
        
        workflow = Seperate2ImgWorkflow(progress_callback=ui.update_progress)

        try:
            result = workflow.run(
                input_path,
                output_dir,
                dpi=options['dpi'],
                format=options['format'],
                trim_whitespace=options['trim_whitespace'],
                cleanup_temp=options['cleanup_temp']
            )

            ui.close_progress_dialog()

            # 결과 표시
            if result['success']:
                ui.show_success(
                    f"작업이 완료되었습니다.\n\n총 이미지: {result['success_count']}개\n저장 위치: {output_dir}"
                )
            else:
                ui.show_warning(
                    "완료 (일부 실패)",
                    f"작업이 완료되었으나 일부 실패가 있습니다.\n\n성공: {result['success_count']}개\n실패: {result['fail_count']}개"
                )

        except Exception as e:
            ui.close_progress_dialog()
            ui.show_error(f"작업 중 오류가 발생했습니다:\n{str(e)}")

    def run_cli(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """CLI 실행 로직"""
        input_path = kwargs.get('input_path')
        if not input_path:
            return {"success": False, "message": "Input path required"}
            
        output_dir = kwargs.get('output_dir')
        if not output_dir:
            output_dir = str(Path(input_path).parent / f"{Path(input_path).stem}_images")

        workflow = Seperate2ImgWorkflow()
        return workflow.run(input_path, output_dir)
