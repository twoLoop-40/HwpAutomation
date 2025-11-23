"""
Folder Consolidator Plugin - V2 플러그인 시스템 연동

Idris2 명세: Specs/Consolidator/UI.idr

UI 워크플로우 (간결한 4단계):
1. SelectMultipleFolders    - 여러 폴더 선택 (Ctrl+클릭)
2. SelectOrCreateTarget     - 결과 폴더 선택/생성
3. ChooseCopyOrMove         - 복사/이동 선택
4. ExecuteConsolidation     - 실행
5. ShowCompletionMessage    - 완료 메시지
6. Exit                     - 종료
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from typing import Dict, Any, List, Optional
from enum import Enum
import string

from automations.base import AutomationBase, PluginMetadata
from automations.registry import register_plugin

from core.folder_consolidator import consolidate_parallel


# Idris2 명세: UIState (Specs/Consolidator/UI.idr)
class UIState(Enum):
    """UI 상태"""
    INITIAL = "Initial"
    SELECTING_SOURCES = "SelectingSources"
    SELECTING_TARGET = "SelectingTarget"
    CHOOSING_MODE = "ChoosingMode"
    PROCESSING = "Processing"
    SHOWING_RESULT = "ShowingResult"
    CLOSED = "Closed"


@register_plugin
class ConsolidatorPlugin(AutomationBase):
    """Folder Consolidator 플러그인"""

    def __init__(self):
        super().__init__()
        self.state = UIState.INITIAL
        self.source_folders: List[str] = []
        self.target_parent: str = ""
        self.target_name: str = ""
        self.mode: str = "copy"
        self.stats: tuple = (0, 0, 0)
        self.progress_dialog: Optional[tk.Toplevel] = None

    def get_metadata(self) -> PluginMetadata:
        """플러그인 메타데이터"""
        return PluginMetadata(
            id="consolidator",
            name="폴더 통합기 (Consolidator)",
            description="여러 폴더의 파일을 하나의 폴더로 통합합니다 (병렬 처리 지원)",
            version="1.0.0",
            author="Claude"
        )

    def has_ui(self) -> bool:
        """UI 지원"""
        return True

    def run(self, **kwargs) -> Dict[str, Any]:
        """플러그인 실행 (메인 엔트리포인트)"""
        if kwargs.get('ui', False):
            self.run_ui()
            return {"success": True}
        return self.run_cli(kwargs)

    def run_ui(self):
        """UI에서 실행

        Idris2 명세 기반 상태 전환 (6단계):
        Initial → SelectingSources → SelectingTarget → ChoosingMode
          → Processing → ShowingResult → Closed
        """
        # 1. SelectMultipleFolders: 여러 폴더 선택
        self.state = UIState.SELECTING_SOURCES
        if not self._select_multiple_folders():
            self.state = UIState.CLOSED
            return

        # 2. SelectOrCreateTarget: 결과 폴더 선택/생성
        self.state = UIState.SELECTING_TARGET
        if not self._select_or_create_target():
            self.state = UIState.CLOSED
            return

        # 3. ChooseCopyOrMove: 복사/이동 선택
        self.state = UIState.CHOOSING_MODE
        if not self._choose_copy_or_move():
            self.state = UIState.CLOSED
            return

        # 4. ExecuteConsolidation: 실행
        self.state = UIState.PROCESSING
        self._execute_consolidation()

        # 5. ShowCompletionMessage: 완료 메시지
        self.state = UIState.SHOWING_RESULT
        self._show_completion_message()

        # 6. Exit: 종료
        self.state = UIState.CLOSED

    def _select_multiple_folders(self) -> bool:
        """1단계: 여러 폴더 선택

        Idris2 명세: FolderTreeView.idr

        Treeview 기반 폴더 브라우저 (Windows 탐색기 스타일)
        """
        dialog = tk.Toplevel()
        dialog.title("통합할 폴더 선택")
        dialog.geometry("1320x792")
        dialog.transient()
        dialog.grab_set()

        # 상단 타이틀
        tk.Label(
            dialog,
            text="통합할 소스 폴더들을 선택하세요",
            font=("맑은 고딕", 14, "bold")
        ).pack(pady=15)

        # 메인 컨테이너 (양분할)
        main_container = tk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === 왼쪽: 폴더 트리뷰 ===
        left_frame = tk.Frame(main_container, relief=tk.RIDGE, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(left_frame, text="📂 폴더 브라우저", font=("맑은 고딕", 13, "bold"), bg="#e8f4f8").pack(fill=tk.X, pady=8)

        selected_folders = []
        # 경로 → 트리 노드 ID 매핑 (선택 해제 시 필요)
        path_to_node = {}

        # Treeview 생성
        tree_frame = tk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 트리뷰 스타일 설정
        style = ttk.Style()
        style.configure("Treeview", font=("맑은 고딕", 11), rowheight=30, indent=25)
        style.configure("Treeview.Heading", font=("맑은 고딕", 12, "bold"))
        # indicator 크기 증가
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])

        tree = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)

        # 트리뷰 스타일
        tree.heading('#0', text='폴더', anchor='w')

        # 초기 트리: "내 PC" 루트 노드
        root_node = tree.insert('', 'end', text='💻 내 PC', values=('내 PC',), open=False)
        tree.insert(root_node, 'end', text='로딩 중...', values=('loading',))  # 더미 노드

        def load_drives():
            """드라이브 목록 로드 (A-Z)"""
            # 기존 자식 제거
            for child in tree.get_children(root_node):
                tree.delete(child)

            # 드라이브 열거
            for letter in string.ascii_uppercase:
                drive_path = Path(f"{letter}:\\")
                if drive_path.exists():
                    drive_node = tree.insert(
                        root_node,
                        'end',
                        text=f'☐ 💾 {letter}:',
                        values=(str(drive_path),)
                    )
                    # 경로 → 노드 매핑 저장
                    path_to_node[str(drive_path)] = drive_node
                    # 더미 노드 추가 (펼침 가능 표시)
                    tree.insert(drive_node, 'end', text='로딩 중...', values=('loading',))

        def load_folders(parent_node, path):
            """특정 경로의 폴더 로드"""
            # 기존 자식 제거
            for child in tree.get_children(parent_node):
                tree.delete(child)

            try:
                folders = sorted([d for d in path.iterdir() if d.is_dir()], key=lambda x: x.name.lower())

                if not folders:
                    # 빈 폴더
                    tree.insert(parent_node, 'end', text='(빈 폴더)', values=('empty',))
                else:
                    for folder in folders:
                        folder_node = tree.insert(
                            parent_node,
                            'end',
                            text=f'☐ 📁 {folder.name}',
                            values=(str(folder),)
                        )
                        # 경로 → 노드 매핑 저장
                        path_to_node[str(folder)] = folder_node
                        # 더미 노드 추가 (하위 폴더가 있을 수 있음을 표시)
                        tree.insert(folder_node, 'end', text='로딩 중...', values=('loading',))
            except PermissionError:
                tree.insert(parent_node, 'end', text='(접근 거부)', values=('error',))
            except Exception as e:
                tree.insert(parent_node, 'end', text=f'(오류: {e})', values=('error',))

        def on_tree_open(event):
            """노드가 펼쳐질 때 자식 로드"""
            node = tree.focus()
            values = tree.item(node, 'values')

            if not values:
                return

            path_str = values[0]

            # 로딩 노드 체크
            children = tree.get_children(node)
            if children and tree.item(children[0], 'values') == ('loading',):
                # "내 PC" 노드
                if path_str == '내 PC':
                    load_drives()
                else:
                    # 일반 폴더 노드
                    try:
                        path = Path(path_str)
                        if path.exists():
                            load_folders(node, path)
                    except:
                        pass

        def on_tree_single_click(event):
            """단일 클릭: 체크박스 토글"""
            # 클릭한 노드 가져오기
            item_id = tree.identify_row(event.y)
            if not item_id:
                return

            # 화살표 영역 체크 (x < 20 정도가 화살표 영역)
            # identify_element로 정확히 확인
            element = tree.identify_element(event.x, event.y)
            if element == 'Treeitem.indicator':
                # 화살표(+/-) 클릭 - 무시
                return

            values = tree.item(item_id, 'values')
            if not values or len(values) == 0:
                return

            path_str = values[0]

            # 로딩/에러/빈폴더 노드는 선택 불가
            if path_str in ('내 PC', 'loading', 'empty', 'error'):
                return

            # 현재 텍스트 가져오기
            current_text = tree.item(item_id, 'text')

            # 토글 방식: 체크박스 아이콘 변경
            if path_str in selected_folders:
                # 제거 - 체크 해제
                selected_folders.remove(path_str)
                # Listbox에서도 제거
                for i in range(folder_listbox.size()):
                    if folder_listbox.get(i) == path_str:
                        folder_listbox.delete(i)
                        break
                # 체크박스 해제: ☑ → ☐
                if current_text.startswith('☑'):
                    new_text = '☐' + current_text[1:]
                    tree.item(item_id, text=new_text)
            else:
                # 추가 - 체크 활성화
                selected_folders.append(path_str)
                folder_listbox.insert(tk.END, path_str)
                folder_listbox.see(tk.END)
                # 체크박스 활성화: ☐ → ☑
                if current_text.startswith('☐'):
                    new_text = '☑' + current_text[1:]
                    tree.item(item_id, text=new_text)
                # 매핑 업데이트
                path_to_node[path_str] = item_id

        tree.bind('<<TreeviewOpen>>', on_tree_open)
        tree.bind('<ButtonRelease-1>', on_tree_single_click)

        # === 오른쪽: 선택된 폴더 목록 ===
        right_frame = tk.Frame(main_container, relief=tk.RIDGE, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(right_frame, text="✅ 선택된 폴더", font=("맑은 고딕", 13, "bold"), bg="#e8f8e8").pack(fill=tk.X, pady=8)

        list_frame = tk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar_right = tk.Scrollbar(list_frame)
        scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)

        folder_listbox = tk.Listbox(
            list_frame,
            font=("맑은 고딕", 12),
            yscrollcommand=scrollbar_right.set
        )
        folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_right.config(command=folder_listbox.yview)

        # 오른쪽 버튼 (제거)
        def remove_selected():
            selection = folder_listbox.curselection()
            if selection:
                idx = selection[0]
                path_str = folder_listbox.get(idx)
                folder_listbox.delete(idx)
                selected_folders.remove(path_str)

                # 트리에서도 체크박스 해제
                if path_str in path_to_node:
                    node_id = path_to_node[path_str]
                    try:
                        current_text = tree.item(node_id, 'text')
                        if current_text.startswith('☑'):
                            new_text = '☐' + current_text[1:]
                            tree.item(node_id, text=new_text)
                    except:
                        pass  # 노드가 더 이상 존재하지 않을 수 있음

        tk.Button(
            right_frame,
            text="선택 제거",
            command=remove_selected,
            font=("맑은 고딕", 12),
            bg="#ff6b6b",
            fg="white",
            width=15
        ).pack(pady=8)

        # 하단: 안내 및 버튼
        info_label = tk.Label(
            dialog,
            text="💡 왼쪽: 화살표=펼치기/접기, 폴더 클릭=체크박스 토글 (☑=선택됨) | 오른쪽: 선택된 폴더 목록",
            font=("맑은 고딕", 10),
            fg="gray"
        )
        info_label.pack(pady=8)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        def on_ok():
            if selected_folders:
                self.source_folders = selected_folders
                dialog.destroy()
            else:
                messagebox.showwarning("경고", "최소 1개 이상의 폴더를 선택하세요.")

        def on_cancel():
            self.source_folders = []
            dialog.destroy()

        tk.Button(
            btn_frame,
            text="확인",
            command=on_ok,
            width=15,
            height=2,
            font=("맑은 고딕", 11, "bold"),
            bg="#27ae60",
            fg="white"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="취소",
            command=on_cancel,
            width=15,
            height=2,
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)

        dialog.wait_window()
        return len(self.source_folders) > 0

    def _select_or_create_target(self) -> bool:
        """2단계: 결과 폴더 선택/생성

        Idris2 명세: UIAction.SelectOrCreateTarget
        """
        # 임시 윈도우 생성 (폴더 선택 다이얼로그의 parent용)
        temp_window = tk.Toplevel()
        temp_window.withdraw()  # 보이지 않게

        # 부모 폴더 선택
        parent = filedialog.askdirectory(
            parent=temp_window,
            title="통합 파일을 저장할 폴더의 위치를 선택하세요",
            mustexist=True
        )

        if not parent:
            temp_window.destroy()
            return False

        self.target_parent = parent

        # 임시 윈도우를 폴더 이름 입력 다이얼로그로 재활용
        temp_window.destroy()

        # 폴더 이름 입력 다이얼로그
        dialog = tk.Toplevel()
        dialog.title("대상 폴더 이름")
        dialog.geometry("450x230")
        dialog.transient()
        dialog.grab_set()

        tk.Label(
            dialog,
            text="새 폴더 이름을 입력하세요:",
            font=("맑은 고딕", 12, "bold")
        ).pack(pady=20)

        name_var = tk.StringVar(value="통합폴더")
        entry = tk.Entry(dialog, textvariable=name_var, font=("맑은 고딕", 11), width=30)
        entry.pack(pady=10)
        entry.focus()

        result = [False]

        def on_ok():
            self.target_name = name_var.get().strip()
            if self.target_name:
                result[0] = True
                dialog.destroy()

        def on_cancel():
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=30)

        tk.Button(
            btn_frame,
            text="확인",
            command=on_ok,
            width=15,
            height=2,
            font=("맑은 고딕", 11, "bold"),
            bg="#27ae60",
            fg="white"
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            btn_frame,
            text="취소",
            command=on_cancel,
            width=15,
            height=2,
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=10)

        dialog.wait_window()
        return result[0]

    def _choose_copy_or_move(self) -> bool:
        """3단계: 복사/이동 선택

        Idris2 명세: UIAction.ChooseCopyOrMove
        """
        dialog = tk.Toplevel()
        dialog.title("작업 모드 선택")
        dialog.geometry("650x300")
        dialog.transient()
        dialog.grab_set()

        tk.Label(
            dialog,
            text="작업 모드를 선택하세요:",
            font=("맑은 고딕", 14, "bold")
        ).pack(pady=40)

        result = [False]

        def choose_copy():
            self.mode = "copy"
            result[0] = True
            dialog.destroy()

        def choose_move():
            self.mode = "move"
            result[0] = True
            dialog.destroy()

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=30)

        tk.Button(
            btn_frame,
            text="복사 (원본 유지)",
            command=choose_copy,
            width=18,
            height=3,
            font=("맑은 고딕", 11, "bold")
        ).pack(side=tk.LEFT, padx=15)

        tk.Button(
            btn_frame,
            text="이동 (원본 삭제)",
            command=choose_move,
            width=18,
            height=3,
            font=("맑은 고딕", 11, "bold"),
            bg="#e74c3c",
            fg="white"
        ).pack(side=tk.LEFT, padx=15)

        dialog.wait_window()
        return result[0]

    def _execute_consolidation(self):
        """4단계: 작업 실행

        Idris2 명세: UIAction.ExecuteConsolidation

        병렬 처리로 파일들을 복사 또는 이동합니다.
        """
        try:
            self.stats = consolidate_parallel(
                source_folders=self.source_folders,
                target_parent=self.target_parent,
                target_name=self.target_name,
                mode=self.mode,
                max_workers=5,
                verbose=True
            )
        except Exception as e:
            self.stats = (0, 0, 0)
            messagebox.showerror("오류", f"작업 실패: {e}")

    def _show_completion_message(self):
        """5단계: 완료 메시지 표시

        Idris2 명세: UIAction.ShowCompletionMessage
        """
        total, success, failed = self.stats
        target_path = Path(self.target_parent) / self.target_name

        if failed == 0:
            # 성공 다이얼로그 - 경로 강조
            dialog = tk.Toplevel()
            dialog.title("완료")
            dialog.geometry("500x250")
            dialog.transient()
            dialog.grab_set()

            tk.Label(
                dialog,
                text="✅ 통합 완료!",
                font=("맑은 고딕", 14, "bold"),
                fg="#27ae60"
            ).pack(pady=20)

            tk.Label(
                dialog,
                text=f"성공적으로 {success}개 파일을 통합했습니다.",
                font=("맑은 고딕", 11)
            ).pack(pady=10)

            tk.Label(
                dialog,
                text="대상 폴더:",
                font=("맑은 고딕", 10, "bold")
            ).pack(pady=5)

            # 경로 표시 (읽기 전용 Entry)
            path_entry = tk.Entry(
                dialog,
                font=("맑은 고딕", 10),
                width=50,
                justify='center'
            )
            path_entry.insert(0, str(target_path))
            path_entry.config(state='readonly')
            path_entry.pack(pady=10)

            def open_folder():
                import subprocess
                subprocess.Popen(f'explorer "{target_path}"')
                dialog.destroy()

            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=20)

            tk.Button(
                btn_frame,
                text="폴더 열기",
                command=open_folder,
                width=15,
                height=2,
                font=("맑은 고딕", 10),
                bg="#3498db",
                fg="white"
            ).pack(side=tk.LEFT, padx=5)

            tk.Button(
                btn_frame,
                text="확인",
                command=dialog.destroy,
                width=15,
                height=2,
                font=("맑은 고딕", 10)
            ).pack(side=tk.LEFT, padx=5)

            dialog.wait_window()
        else:
            messagebox.showwarning(
                "부분 완료",
                f"전체: {total}개\n성공: {success}개\n실패: {failed}개\n\n"
                f"대상: {target_path}"
            )

    def run_cli(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """CLI에서 실행"""
        sources = kwargs.get('sources', [])
        target_parent = kwargs.get('target_parent', '')
        target_name = kwargs.get('target_name', '통합폴더')
        mode = kwargs.get('mode', 'copy')
        max_workers = kwargs.get('max_workers', 5)

        if not sources or not target_parent:
            return {"success": False, "error": "소스 또는 대상이 지정되지 않았습니다"}

        total, success, failed = consolidate_parallel(
            source_folders=sources,
            target_parent=target_parent,
            target_name=target_name,
            mode=mode,
            max_workers=max_workers,
            verbose=True
        )

        return {
            "success": failed == 0,
            "total": total,
            "success_count": success,
            "failed_count": failed
        }
