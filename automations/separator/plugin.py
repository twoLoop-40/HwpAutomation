"""
Separator Plugin - V2 플러그인 시스템 연동

HWPX 파일에서 EndNote 기반으로 문제를 분리하는 플러그인
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Any

from automations.base import AutomationBase, PluginMetadata
from automations.registry import register_plugin

from .separator import separate_problems
from .types import SeparatorConfig, OnePerFile, GroupByCount, InputFormat, OutputFormat


@register_plugin
class SeparatorPlugin(AutomationBase):
    """Separator 플러그인"""

    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터"""
        return PluginMetadata(
            id="separator",
            name="문제 분리기 (Separator)",
            description="HWP/HWPX 파일에서 EndNote 기반으로 문제를 분리합니다 (병렬 처리 지원)",
            version="2.0.0",
            author="Claude"
        )

    def has_ui(self) -> bool:
        """UI 지원"""
        return True

    def run(self, **kwargs) -> Dict[str, Any]:
        """플러그인 실행 (메인 엔트리포인트)"""
        # UI 모드
        if kwargs.get('ui', False):
            self.run_ui()
            return {"success": True}

        # CLI 모드
        return self.run_cli(kwargs)

    def run_ui(self):
        """UI에서 실행 (Tkinter 다이얼로그)"""
        # 설정 수집
        config = self._collect_config_via_ui()
        if not config:
            return

        # 실행
        try:
            result = separate_problems(config)

            # 결과 표시
            if result.is_success():
                messagebox.showinfo(
                    "완료",
                    f"성공적으로 {result.success_count}개 파일을 생성했습니다.\n\n"
                    f"출력 디렉토리: {config.output_dir}"
                )
            else:
                messagebox.showwarning(
                    "부분 완료",
                    f"{result.success_count}개 성공, {result.failed_count}개 실패"
                )

        except Exception as e:
            messagebox.showerror("오류", f"실행 중 오류가 발생했습니다:\n{e}")

    def run_cli(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """CLI에서 실행"""
        # CLI 인자로부터 설정 생성
        config = self._create_config_from_args(args)

        # 실행
        result = separate_problems(config)

        # 결과 출력
        print(f"\n총 {result.total_problems}개 중:")
        print(f"  성공: {result.success_count}개")
        print(f"  실패: {result.failed_count}개")

        return {
            "success": result.is_success(),
            "total": result.total_problems,
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "output_files": result.output_files
        }

    def _collect_config_via_ui(self) -> SeparatorConfig | None:
        """UI를 통해 설정 수집

        Idris2: buildConfigFromUI (outputDir 자동 생성)
        """
        # 입력 파일 선택 (HWP + HWPX 지원)
        input_path = filedialog.askopenfilename(
            title="HWP/HWPX 파일 선택",
            filetypes=[
                ("HWP 파일", "*.hwp"),
                ("HWPX 파일", "*.hwpx"),
                ("모든 파일", "*.*")
            ]
        )
        if not input_path:
            return None

        # 파일 형식 확인
        is_hwp = input_path.lower().endswith('.hwp')

        # 기본 접두사 추출 (Idris2: extractDefaultPrefix)
        default_prefix = Path(input_path).stem

        # 출력 디렉토리 자동 생성 (Idris2: generateOutputDir)
        output_dir = str(Path(input_path).parent / f"{Path(input_path).stem}_output")

        # 그룹화 옵션 다이얼로그 (HWP 파일은 병렬 옵션 제공)
        dialog = GroupingDialog(is_hwp=is_hwp, default_prefix=default_prefix)
        result = dialog.show()

        if not result or not result[0]:  # strategy가 None이면
            return None

        strategy, output_format, use_parallel, max_workers, custom_prefix = result

        # 설정 생성
        if isinstance(strategy, OnePerFile):
            config = SeparatorConfig.for_hwpx(input_path, output_dir)
        elif isinstance(strategy, GroupByCount):
            config = SeparatorConfig.grouped(input_path, output_dir, strategy.count)
        else:
            config = SeparatorConfig.for_hwpx(input_path, output_dir)

        # 커스텀 접두사 적용 (Idris2: createCustomNamingRule)
        if custom_prefix:
            from .types import NamingStrategy
            config.naming_rule.strategy = NamingStrategy.CUSTOM
            config.naming_rule.custom_prefix = custom_prefix

        # HWP 병렬 처리 옵션 적용
        if is_hwp:
            config.use_parallel = use_parallel
            config.max_workers = max_workers

        # 출력 형식 적용
        config.output_format = output_format

        return config

    def _create_config_from_args(self, args: Dict[str, Any]) -> SeparatorConfig:
        """CLI 인자로부터 설정 생성"""
        input_path = args.get('input', '')
        output_dir = args.get('output', 'output_problems')
        group_size = args.get('group_size', 0)

        if group_size > 0:
            return SeparatorConfig.grouped(input_path, output_dir, group_size)
        else:
            return SeparatorConfig.for_hwpx(input_path, output_dir)


class GroupingDialog:
    """그룹화 옵션 선택 다이얼로그

    Idris2: ConfigCollectionStep
    """

    def __init__(self, is_hwp: bool = False, default_prefix: str = ""):
        self.is_hwp = is_hwp
        self.default_prefix = default_prefix
        self.strategy = None
        self.output_format = OutputFormat.HWP  # HWP First
        self.use_parallel = False
        self.max_workers = 5
        self.custom_prefix = None

    def show(self):
        """다이얼로그 표시

        Returns:
            (strategy, output_format, use_parallel, max_workers, custom_prefix)
        """
        dialog = tk.Toplevel()
        dialog.title("그룹화 옵션")

        # HWP 파일이면 높이 증가 (병렬 옵션 + 커스텀 접두사)
        height = "550" if self.is_hwp else "400"
        dialog.geometry(f"500x{height}")
        dialog.resizable(False, False)

        # 중앙 정렬
        dialog.transient()
        dialog.grab_set()

        # 커스텀 접두사 입력 (Idris2: CustomPrefixInput)
        prefix_frame = tk.Frame(dialog)
        prefix_frame.pack(pady=10, fill=tk.X, padx=40)

        tk.Label(
            prefix_frame,
            text="파일명 접두사:",
            font=("맑은 고딕", 10, "bold")
        ).pack(anchor="w")

        prefix_var = tk.StringVar(value=self.default_prefix)
        self.prefix_var = prefix_var

        prefix_entry = tk.Entry(prefix_frame, textvariable=prefix_var, width=50)
        prefix_entry.pack(fill=tk.X, pady=5)

        tk.Label(
            prefix_frame,
            text=f"예: {self.default_prefix}_1.hwp, {self.default_prefix}_2.hwp, ...",
            fg="gray",
            font=("맑은 고딕", 8)
        ).pack(anchor="w")

        # 설명
        tk.Label(
            dialog,
            text="문제를 어떻게 분리하시겠습니까?",
            font=("맑은 고딕", 11, "bold")
        ).pack(pady=10)

        # 옵션 1: 1문제 = 1파일
        frame1 = tk.Frame(dialog)
        frame1.pack(pady=8, fill=tk.X, padx=40)

        tk.Button(
            frame1,
            text="1문제 = 1파일",
            width=20,
            command=lambda: self._set_strategy(OnePerFile(), dialog)
        ).pack()

        tk.Label(
            frame1,
            text="(400문제 → 400개 파일)",
            fg="gray"
        ).pack()

        # 옵션 2: N개씩 묶기
        frame2 = tk.Frame(dialog)
        frame2.pack(pady=8, fill=tk.X, padx=40)

        group_size_var = tk.IntVar(value=3)

        sub_frame = tk.Frame(frame2)
        sub_frame.pack()

        tk.Entry(
            sub_frame,
            textvariable=group_size_var,
            width=5
        ).pack(side=tk.LEFT)

        tk.Label(sub_frame, text="개씩 묶기").pack(side=tk.LEFT)

        tk.Button(
            frame2,
            text="그룹으로 나누기",
            width=20,
            command=lambda: self._set_strategy(
                GroupByCount(group_size_var.get()),
                dialog
            )
        ).pack(pady=5)

        tk.Label(
            frame2,
            text="(예: 3개씩 → 134개 파일)",
            fg="gray"
        ).pack()

        # 출력 형식 (HWP 파일만)
        if self.is_hwp:
            tk.Label(
                dialog,
                text="\n출력 형식:",
                font=("맑은 고딕", 10, "bold")
            ).pack(anchor="w", padx=40, pady=(10, 5))

            format_var = tk.StringVar(value="hwp")
            self.format_var = format_var

            tk.Radiobutton(
                dialog,
                text="HWP 파일 (.hwp) - 원본 형식 유지",
                variable=format_var,
                value="hwp"
            ).pack(anchor="w", padx=60)

            tk.Radiobutton(
                dialog,
                text="Markdown 파일 (.md) - 텍스트만 추출 (디버깅용)",
                variable=format_var,
                value="md"
            ).pack(anchor="w", padx=60)

            # 병렬 처리 옵션 (HWP → HWP만)
            tk.Label(
                dialog,
                text="\n병렬 처리 (HWP → HWP 전용):",
                font=("맑은 고딕", 10, "bold")
            ).pack(anchor="w", padx=40, pady=(10, 5))

            parallel_var = tk.BooleanVar(value=False)
            self.parallel_var = parallel_var

            tk.Checkbutton(
                dialog,
                text="병렬 처리 활성화 (최대 5배 빠름)",
                variable=parallel_var
            ).pack(anchor="w", padx=60)

            # 워커 수
            worker_frame = tk.Frame(dialog)
            worker_frame.pack(anchor="w", padx=80, pady=5)

            tk.Label(worker_frame, text="최대 워커:").pack(side="left")
            workers_var = tk.IntVar(value=5)
            self.workers_var = workers_var

            tk.Spinbox(
                worker_frame,
                from_=1,
                to=10,
                textvariable=workers_var,
                width=5
            ).pack(side="left", padx=5)
            tk.Label(worker_frame, text="개 (권장: 5)").pack(side="left")

        # 취소 버튼
        tk.Button(
            dialog,
            text="취소",
            command=dialog.destroy
        ).pack(pady=15)

        dialog.wait_window()

        # 커스텀 접두사 수집
        custom_prefix_value = self.prefix_var.get().strip()
        if custom_prefix_value and custom_prefix_value != self.default_prefix:
            self.custom_prefix = custom_prefix_value
        else:
            self.custom_prefix = None  # 기본값 사용

        # 반환값 구성
        if self.is_hwp:
            # 출력 형식 결정 (HWP First)
            if self.format_var.get() == "hwp":
                self.output_format = OutputFormat.HWP  # HWP First!
            else:
                self.output_format = OutputFormat.MARKDOWN

            # 병렬 처리 옵션
            self.use_parallel = self.parallel_var.get()
            self.max_workers = self.workers_var.get()

        return (self.strategy, self.output_format, self.use_parallel, self.max_workers, self.custom_prefix)

    def _set_strategy(self, strategy, dialog):
        """전략 선택 후 닫기"""
        self.strategy = strategy
        dialog.destroy()
