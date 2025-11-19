"""
HwpAutomation UI - Main Window

Tkinter 기반 플러그인 런처
"""

import tkinter as tk
from tkinter import ttk, messagebox
from automations import get_registry


class HwpAutomationLauncher:
    """메인 런처 윈도우"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HwpAutomation v2.0")
        self.root.geometry("600x400")

        # 플러그인 레지스트리
        self.registry = get_registry()

        # 플러그인 로드
        self._load_plugins()

        # UI 구성
        self._setup_ui()

    def _load_plugins(self):
        """플러그인 로드"""
        # Merger 플러그인
        try:
            from automations.merger import MergerPlugin
        except ImportError as e:
            print(f"Failed to load Merger plugin: {e}")

        # MCP 플러그인
        try:
            from automations.mcp import MCPPlugin
        except ImportError as e:
            print(f"Failed to load MCP plugin: {e}")

        # Separator 플러그인
        try:
            from automations.separator import SeparatorPlugin
        except ImportError as e:
            print(f"Failed to load Separator plugin: {e}")

    def _setup_ui(self):
        """UI 구성"""
        # 헤더
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="HwpAutomation",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=15)

        # 플러그인 리스트
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 리스트박스
        self.plugin_list = tk.Listbox(
            list_frame,
            font=("Arial", 12),
            yscrollcommand=scrollbar.set,
            height=10
        )
        self.plugin_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.plugin_list.yview)

        # 플러그인 목록 채우기
        self.plugins = self.registry.get_all_metadata()
        for plugin in self.plugins:
            display_text = f"{plugin.name} (v{plugin.version}) - {plugin.description}"
            self.plugin_list.insert(tk.END, display_text)

        # 버튼 프레임
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        run_button = tk.Button(
            button_frame,
            text="실행",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10,
            command=self._run_plugin
        )
        run_button.pack(side=tk.LEFT, padx=5)

        info_button = tk.Button(
            button_frame,
            text="정보",
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10,
            command=self._show_info
        )
        info_button.pack(side=tk.LEFT, padx=5)

        quit_button = tk.Button(
            button_frame,
            text="종료",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=10,
            command=self.root.quit
        )
        quit_button.pack(side=tk.RIGHT, padx=5)

    def _run_plugin(self):
        """선택된 플러그인 실행"""
        selection = self.plugin_list.curselection()
        if not selection:
            messagebox.showwarning("경고", "플러그인을 선택하세요.")
            return

        index = selection[0]
        plugin_metadata = self.plugins[index]

        try:
            plugin = self.registry.get_plugin(plugin_metadata.id)
            if not plugin:
                messagebox.showerror("오류", "플러그인을 찾을 수 없습니다.")
                return

            # UI가 있으면 UI 모드로 실행
            if plugin.has_ui():
                plugin.run(ui=True)
            else:
                # CLI 모드
                messagebox.showinfo(
                    "정보",
                    f"{plugin_metadata.name}은 CLI 전용입니다.\n명령줄에서 실행하세요."
                )

        except Exception as e:
            messagebox.showerror("오류", f"플러그인 실행 실패:\n{str(e)}")

    def _show_info(self):
        """플러그인 정보 표시"""
        selection = self.plugin_list.curselection()
        if not selection:
            messagebox.showwarning("경고", "플러그인을 선택하세요.")
            return

        index = selection[0]
        plugin = self.plugins[index]

        info = f"""
플러그인 정보

이름: {plugin.name}
ID: {plugin.id}
버전: {plugin.version}
작성자: {plugin.author}
설명: {plugin.description}
        """.strip()

        messagebox.showinfo("플러그인 정보", info)

    def run(self):
        """UI 실행"""
        self.root.mainloop()


def main():
    """메인 함수"""
    app = HwpAutomationLauncher()
    app.run()


if __name__ == "__main__":
    main()
