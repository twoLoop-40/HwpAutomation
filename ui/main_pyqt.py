# -*- coding: utf-8 -*-
"""
HwpAutomation UI - PyQt5 메인 윈도우

Specs/UI/PyQtMigration.idr 명세 기반 구현

주요 기능:
- 플러그인 목록 표시 (더블클릭으로 실행)
- 플러그인 실행 화면 (QStackedWidget으로 전환)
- 진행률 표시 (QProgressBar)
- 실시간 로그 출력 (QTextEdit)
- 다크 테마 적용
- 다중 폴더 선택 (Consolidator용 QTreeView)
"""

import sys
import io
import os
import string
from datetime import datetime
from typing import Optional, Callable, List
from pathlib import Path

# UTF-8 출력 설정 (Windows CP949 호환성)
# main() 함수에서 설정 (import 시점 문제 방지)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox,
    QStackedWidget, QProgressBar, QTextEdit, QFileDialog, QLineEdit,
    QGroupBox, QCheckBox, QSpinBox, QComboBox, QSplitter, QFrame,
    QDialog, QTreeWidget, QTreeWidgetItem, QDialogButtonBox, QInputDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QColor, QIcon

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# =============================================================================
# 로그 레벨 색상 (Specs/UI/PyQtMigration.idr Section 9)
# =============================================================================
LOG_COLORS = {
    'info': '#ffffff',      # 흰색
    'warning': '#f39c12',   # 주황
    'error': '#e74c3c',     # 빨강
    'success': '#27ae60',   # 초록
}


# =============================================================================
# 다크 테마 스타일시트 (Specs/UI/PyQtMigration.idr Section 8)
# =============================================================================
DARK_STYLE = """
QMainWindow {
    background-color: #2b2b2b;
}
QLabel {
    color: #ffffff;
}
QListWidget {
    background-color: #313335;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 8px;
    padding: 15px;
    font-size: 22px;
}
QListWidget::item {
    padding: 26px;
    border-bottom: 1px solid #444;
}
QListWidget::item:hover {
    background-color: #3c3f41;
}
QListWidget::item:selected {
    background-color: #2d5a88;
}
QPushButton {
    background-color: #4a4a4a;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 20px 50px;
    font-size: 18px;
}
QPushButton:hover {
    background-color: #5a5a5a;
}
QPushButton:disabled {
    background-color: #3a3a3a;
    color: #777;
}
QPushButton#run_btn {
    background-color: #27ae60;
}
QPushButton#run_btn:hover {
    background-color: #2ecc71;
}
QPushButton#quit_btn, QPushButton#cancel_btn {
    background-color: #c0392b;
}
QPushButton#quit_btn:hover, QPushButton#cancel_btn:hover {
    background-color: #e74c3c;
}
QPushButton#back_btn {
    background-color: #3498db;
}
QPushButton#back_btn:hover {
    background-color: #5dade2;
}
QProgressBar {
    background-color: #313335;
    border: 1px solid #555;
    border-radius: 5px;
    text-align: center;
    color: #ffffff;
    height: 25px;
}
QProgressBar::chunk {
    background-color: #3574f0;
    border-radius: 4px;
}
QTextEdit {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 5px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
}
QLineEdit {
    background-color: #313335;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 8px;
    font-size: 13px;
}
QGroupBox {
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QCheckBox {
    color: #ffffff;
}
QSpinBox, QComboBox {
    background-color: #313335;
    color: #ffffff;
    border: 1px solid #555;
    border-radius: 5px;
    padding: 5px;
}
QStatusBar {
    color: #888;
    background-color: #1e1e1e;
}
QSplitter::handle {
    background-color: #555;
}
"""


# =============================================================================
# 워커 스레드 (백그라운드 작업용)
# =============================================================================
class WorkerThread(QThread):
    """플러그인 실행을 위한 워커 스레드"""
    progress = pyqtSignal(int)           # 진행률 (0-100)
    log = pyqtSignal(str, str)           # (level, message)
    finished_signal = pyqtSignal(bool, str)  # (success, message)

    def __init__(self, task_func: Callable, *args, **kwargs):
        super().__init__()
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def run(self):
        try:
            # 콜백 함수들 주입
            self.kwargs['progress_callback'] = self._emit_progress
            self.kwargs['log_callback'] = self._emit_log
            self.kwargs['cancel_check'] = lambda: self._is_cancelled

            result = self.task_func(*self.args, **self.kwargs)

            if self._is_cancelled:
                self.finished_signal.emit(False, "작업이 취소되었습니다.")
            else:
                success = result.get('success', False) if isinstance(result, dict) else bool(result)
                message = result.get('message', '완료') if isinstance(result, dict) else '완료'
                self.finished_signal.emit(success, message)

        except Exception as e:
            self.finished_signal.emit(False, f"오류: {str(e)}")

    def _emit_progress(self, percent: int):
        self.progress.emit(min(100, max(0, percent)))

    def _emit_log(self, level: str, message: str):
        self.log.emit(level, message)

    def cancel(self):
        self._is_cancelled = True


# =============================================================================
# 다중 폴더 선택 다이얼로그 (Specs/UI/PyQtMigration.idr - MultipleDirectories)
# =============================================================================
class MultiFolderSelectDialog(QDialog):
    """
    여러 폴더를 선택할 수 있는 다이얼로그

    Idris2 명세: Specs/Consolidator/UI.idr - SelectMultipleFolders
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folders: List[str] = []
        self.path_to_item = {}  # 경로 → TreeWidgetItem 매핑
        self._setup_ui()
        self._load_drives()

    def _setup_ui(self):
        self.setWindowTitle("통합할 폴더 선택")
        self.setMinimumSize(1400, 900)
        self.resize(1400, 900)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 상단 타이틀
        title = QLabel("통합할 소스 폴더들을 선택하세요")
        title.setFont(QFont("맑은 고딕", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3574f0; padding: 15px;")
        layout.addWidget(title)

        # 메인 영역 (좌: 트리뷰, 우: 선택 목록)
        main_splitter = QSplitter(Qt.Horizontal)

        # === 왼쪽: 폴더 트리뷰 ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_header = QLabel("📂 폴더 브라우저")
        left_header.setFont(QFont("맑은 고딕", 14, QFont.Bold))
        left_header.setStyleSheet("background-color: #1e3a5f; color: white; padding: 12px; border-radius: 5px;")
        left_layout.addWidget(left_header)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("폴더")
        self.tree.setFont(QFont("맑은 고딕", 13))
        self.tree.setIndentation(30)
        self.tree.itemExpanded.connect(self._on_item_expanded)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #313335;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QTreeWidget::item {
                padding: 8px;
                min-height: 35px;
            }
            QTreeWidget::item:hover {
                background-color: #3c3f41;
            }
            QTreeWidget::item:selected {
                background-color: #2d5a88;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                image: url(none);
                border-image: none;
            }
        """)
        left_layout.addWidget(self.tree)

        main_splitter.addWidget(left_widget)

        # === 오른쪽: 선택된 폴더 목록 ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_header = QLabel("✅ 선택된 폴더")
        right_header.setFont(QFont("맑은 고딕", 14, QFont.Bold))
        right_header.setStyleSheet("background-color: #1e5f3a; color: white; padding: 12px; border-radius: 5px;")
        right_layout.addWidget(right_header)

        self.selected_list = QListWidget()
        self.selected_list.setFont(QFont("맑은 고딕", 12))
        self.selected_list.setStyleSheet("""
            QListWidget {
                background-color: #313335;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #2d5a88;
            }
        """)
        right_layout.addWidget(self.selected_list)

        # 제거 버튼
        remove_btn = QPushButton("선택 제거")
        remove_btn.setFont(QFont("맑은 고딕", 12))
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        remove_btn.clicked.connect(self._remove_selected)
        right_layout.addWidget(remove_btn)

        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([700, 600])

        layout.addWidget(main_splitter, stretch=1)

        # 안내 라벨
        info_label = QLabel("💡 폴더를 클릭하면 체크박스가 토글됩니다 (☑=선택됨). 화살표로 하위 폴더를 펼칠 수 있습니다.")
        info_label.setFont(QFont("맑은 고딕", 11))
        info_label.setStyleSheet("color: #888; padding: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 하단 버튼
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        ok_btn = QPushButton("확인")
        ok_btn.setFont(QFont("맑은 고딕", 14, QFont.Bold))
        ok_btn.setMinimumSize(150, 50)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        ok_btn.clicked.connect(self._on_ok)

        cancel_btn = QPushButton("취소")
        cancel_btn.setFont(QFont("맑은 고딕", 14))
        cancel_btn.setMinimumSize(150, 50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _load_drives(self):
        """드라이브 목록 로드 - Documents 폴더를 시작점으로"""
        # Documents 폴더를 기본 시작점으로
        documents_path = Path.home() / "Documents"
        if documents_path.exists():
            docs_item = QTreeWidgetItem(self.tree, [f"📁 문서 ({documents_path})"])
            docs_item.setData(0, Qt.UserRole, str(documents_path))
            self.path_to_item[str(documents_path)] = docs_item

            # 더미 노드 추가
            dummy = QTreeWidgetItem(docs_item, ["로딩 중..."])
            dummy.setData(0, Qt.UserRole, "loading")

            # Documents 폴더 자동 펼침
            docs_item.setExpanded(True)

        # 내 PC (드라이브 목록)
        root = QTreeWidgetItem(self.tree, ["💻 내 PC"])
        root.setData(0, Qt.UserRole, "내 PC")
        root.setExpanded(False)

        # 더미 노드 추가 (펼침 표시용)
        dummy = QTreeWidgetItem(root, ["로딩 중..."])
        dummy.setData(0, Qt.UserRole, "loading")

        self.tree.addTopLevelItem(root)

    def _on_item_expanded(self, item: QTreeWidgetItem):
        """노드가 펼쳐질 때 자식 로드"""
        path_str = item.data(0, Qt.UserRole)

        # 첫 번째 자식이 로딩 노드인지 확인
        if item.childCount() == 1:
            first_child = item.child(0)
            if first_child.data(0, Qt.UserRole) == "loading":
                # 로딩 노드 제거
                item.removeChild(first_child)

                if path_str == "내 PC":
                    self._load_drives_list(item)
                else:
                    self._load_folders(item, Path(path_str))

    def _load_drives_list(self, parent_item: QTreeWidgetItem):
        """드라이브 열거"""
        for letter in string.ascii_uppercase:
            drive_path = Path(f"{letter}:\\")
            if drive_path.exists():
                item = QTreeWidgetItem(parent_item, [f"☐ 💾 {letter}:"])
                item.setData(0, Qt.UserRole, str(drive_path))
                self.path_to_item[str(drive_path)] = item

                # 더미 노드 추가
                dummy = QTreeWidgetItem(item, ["로딩 중..."])
                dummy.setData(0, Qt.UserRole, "loading")

    def _load_folders(self, parent_item: QTreeWidgetItem, path: Path):
        """특정 경로의 폴더 로드"""
        try:
            folders = sorted(
                [d for d in path.iterdir() if d.is_dir()],
                key=lambda x: x.name.lower()
            )

            if not folders:
                empty = QTreeWidgetItem(parent_item, ["(빈 폴더)"])
                empty.setData(0, Qt.UserRole, "empty")
            else:
                for folder in folders:
                    # 선택 상태 확인
                    is_selected = str(folder) in self.selected_folders
                    checkbox = "☑" if is_selected else "☐"

                    item = QTreeWidgetItem(parent_item, [f"{checkbox} 📁 {folder.name}"])
                    item.setData(0, Qt.UserRole, str(folder))
                    self.path_to_item[str(folder)] = item

                    # 더미 노드 추가 (하위 폴더가 있을 수 있음)
                    dummy = QTreeWidgetItem(item, ["로딩 중..."])
                    dummy.setData(0, Qt.UserRole, "loading")

        except PermissionError:
            error = QTreeWidgetItem(parent_item, ["(접근 거부)"])
            error.setData(0, Qt.UserRole, "error")
        except Exception as e:
            error = QTreeWidgetItem(parent_item, [f"(오류: {e})"])
            error.setData(0, Qt.UserRole, "error")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """아이템 클릭 시 체크박스 토글"""
        path_str = item.data(0, Qt.UserRole)

        # 로딩/에러/빈폴더/내PC 노드는 선택 불가
        if path_str in ("내 PC", "loading", "empty", "error"):
            return

        current_text = item.text(0)

        if path_str in self.selected_folders:
            # 선택 해제
            self.selected_folders.remove(path_str)

            # 리스트에서 제거
            for i in range(self.selected_list.count()):
                if self.selected_list.item(i).text() == path_str:
                    self.selected_list.takeItem(i)
                    break

            # 체크박스 해제: ☑ → ☐
            if current_text.startswith("☑"):
                item.setText(0, "☐" + current_text[1:])
        else:
            # 선택 추가
            self.selected_folders.append(path_str)
            self.selected_list.addItem(path_str)
            self.selected_list.scrollToBottom()

            # 체크박스 활성화: ☐ → ☑
            if current_text.startswith("☐"):
                item.setText(0, "☑" + current_text[1:])

        # 매핑 업데이트
        self.path_to_item[path_str] = item

    def _remove_selected(self):
        """선택된 항목 제거"""
        current = self.selected_list.currentItem()
        if not current:
            return

        path_str = current.text()
        row = self.selected_list.row(current)
        self.selected_list.takeItem(row)

        if path_str in self.selected_folders:
            self.selected_folders.remove(path_str)

        # 트리에서 체크박스 해제
        if path_str in self.path_to_item:
            item = self.path_to_item[path_str]
            current_text = item.text(0)
            if current_text.startswith("☑"):
                item.setText(0, "☐" + current_text[1:])

    def _on_ok(self):
        """확인 버튼"""
        if not self.selected_folders:
            QMessageBox.warning(self, "경고", "최소 1개 이상의 폴더를 선택하세요.")
            return
        self.accept()

    def get_selected_folders(self) -> List[str]:
        """선택된 폴더 목록 반환"""
        return self.selected_folders.copy()


# =============================================================================
# 플러그인 목록 페이지 (Specs Section 2: MainWindowLayout)
# =============================================================================
class PluginListPage(QWidget):
    """플러그인 목록 화면"""
    plugin_selected = pyqtSignal(str)  # plugin_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.plugins = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 헤더
        header = QLabel("HwpAutomation")
        header.setFont(QFont("Arial", 48, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #3574f0; padding: 40px;")
        layout.addWidget(header)

        subtitle = QLabel("플러그인을 선택하세요 (더블클릭으로 실행)")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #888; margin-bottom: 25px;")
        layout.addWidget(subtitle)

        # 플러그인 리스트
        self.plugin_list = QListWidget()
        self.plugin_list.setFont(QFont("Arial", 22))
        self.plugin_list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.plugin_list, stretch=1)

        # 버튼 바
        button_bar = QHBoxLayout()
        button_bar.setSpacing(15)

        self.run_btn = QPushButton("실행")
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setFont(QFont("Arial", 18, QFont.Bold))
        self.run_btn.clicked.connect(self._on_run_click)

        self.info_btn = QPushButton("정보")
        self.info_btn.setFont(QFont("Arial", 18))
        self.info_btn.clicked.connect(self._show_info)

        self.quit_btn = QPushButton("종료")
        self.quit_btn.setObjectName("quit_btn")
        self.quit_btn.setFont(QFont("Arial", 18))
        self.quit_btn.clicked.connect(QApplication.quit)

        button_bar.addWidget(self.run_btn)
        button_bar.addWidget(self.info_btn)
        button_bar.addStretch()
        button_bar.addWidget(self.quit_btn)
        layout.addLayout(button_bar)

    def load_plugins(self):
        """플러그인 로드 (mcp 제외)"""
        from automations import get_registry
        registry = get_registry()

        # 플러그인 import
        plugin_modules = [
            ('automations.merger', 'MergerPlugin'),
            ('automations.separator', 'SeparatorPlugin'),
            ('automations.converter', 'ConverterPlugin'),
            ('automations.consolidator', 'ConsolidatorPlugin'),
            ('automations.seperate2Img', 'Seperate2ImgPlugin'),
            ('automations.latex2hwp', 'Latex2HwpPlugin'),
        ]

        for module_name, class_name in plugin_modules:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                print(f"[WARN] Failed to load {module_name}: {e}")

        self.plugins = registry.get_all_metadata()
        self.plugin_list.clear()

        for plugin in self.plugins:
            item = QListWidgetItem(f"{plugin.name} (v{plugin.version}) - {plugin.description}")
            item.setData(Qt.UserRole, plugin.id)
            self.plugin_list.addItem(item)

    def _on_double_click(self, item: QListWidgetItem):
        plugin_id = item.data(Qt.UserRole)
        self.plugin_selected.emit(plugin_id)

    def _on_run_click(self):
        item = self.plugin_list.currentItem()
        if item:
            self._on_double_click(item)
        else:
            QMessageBox.warning(self, "경고", "플러그인을 선택하세요.")

    def _show_info(self):
        item = self.plugin_list.currentItem()
        if not item:
            QMessageBox.warning(self, "경고", "플러그인을 선택하세요.")
            return

        plugin_id = item.data(Qt.UserRole)
        for p in self.plugins:
            if p.id == plugin_id:
                info = f"이름: {p.name}\nID: {p.id}\n버전: {p.version}\n작성자: {p.author}\n설명: {p.description}"
                QMessageBox.information(self, "플러그인 정보", info)
                return


# =============================================================================
# 플러그인 실행 페이지 (Specs Section 10: PluginExecutionSection)
# =============================================================================
class PluginExecutionPage(QWidget):
    """플러그인 실행 화면"""
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_plugin_id = None
        self.current_plugin = None
        self.worker: Optional[WorkerThread] = None

        # Consolidator 전용 상태
        self.consolidator_sources: List[str] = []
        self.consolidator_target_parent: str = ""
        self.consolidator_target_name: str = ""
        self.consolidator_mode: str = "copy"

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # 1. 헤더 (PluginHeader)
        header_layout = QHBoxLayout()

        self.back_btn = QPushButton("← 뒤로")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setFont(QFont("Arial", 11))
        self.back_btn.clicked.connect(self._on_back)
        header_layout.addWidget(self.back_btn)

        self.plugin_title = QLabel("플러그인 이름")
        self.plugin_title.setFont(QFont("Arial", 20, QFont.Bold))
        self.plugin_title.setStyleSheet("color: #3574f0;")
        header_layout.addWidget(self.plugin_title, stretch=1)

        layout.addLayout(header_layout)

        # 구분선
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #555;")
        layout.addWidget(line)

        # 2. 입력 영역 (InputArea) - 일반 플러그인용
        self.input_group = QGroupBox("입력 설정")
        input_layout = QVBoxLayout(self.input_group)

        # 파일/폴더 선택
        file_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("파일 또는 폴더를 선택하세요...")
        self.browse_btn = QPushButton("찾아보기...")
        self.browse_btn.clicked.connect(self._browse_path)
        file_layout.addWidget(self.path_input, stretch=1)
        file_layout.addWidget(self.browse_btn)
        input_layout.addLayout(file_layout)

        # 옵션 영역 (플러그인별로 동적 구성)
        self.options_widget = QWidget()
        self.options_layout = QVBoxLayout(self.options_widget)
        self.options_layout.setContentsMargins(0, 10, 0, 0)
        input_layout.addWidget(self.options_widget)

        layout.addWidget(self.input_group)

        # 2-1. Consolidator 전용 입력 영역
        self.consolidator_input_group = QGroupBox("폴더 통합 설정")
        consolidator_layout = QVBoxLayout(self.consolidator_input_group)

        # 소스 폴더 선택
        source_layout = QHBoxLayout()
        source_label = QLabel("소스 폴더:")
        source_label.setFont(QFont("맑은 고딕", 12))
        source_label.setMinimumWidth(100)
        source_layout.addWidget(source_label)

        self.source_folders_list = QListWidget()
        self.source_folders_list.setMaximumHeight(150)
        self.source_folders_list.setStyleSheet("""
            QListWidget {
                background-color: #313335;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
        """)
        source_layout.addWidget(self.source_folders_list, stretch=1)

        source_btn_layout = QVBoxLayout()
        self.select_sources_btn = QPushButton("폴더 선택...")
        self.select_sources_btn.setFont(QFont("맑은 고딕", 11))
        self.select_sources_btn.clicked.connect(self._select_consolidator_sources)
        source_btn_layout.addWidget(self.select_sources_btn)

        self.clear_sources_btn = QPushButton("초기화")
        self.clear_sources_btn.setFont(QFont("맑은 고딕", 11))
        self.clear_sources_btn.clicked.connect(self._clear_consolidator_sources)
        source_btn_layout.addWidget(self.clear_sources_btn)
        source_btn_layout.addStretch()

        source_layout.addLayout(source_btn_layout)
        consolidator_layout.addLayout(source_layout)

        # 대상 폴더 선택
        target_layout = QHBoxLayout()
        target_label = QLabel("대상 폴더:")
        target_label.setFont(QFont("맑은 고딕", 12))
        target_label.setMinimumWidth(100)
        target_layout.addWidget(target_label)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("통합 파일을 저장할 폴더 위치...")
        target_layout.addWidget(self.target_input, stretch=1)

        self.select_target_btn = QPushButton("선택...")
        self.select_target_btn.setFont(QFont("맑은 고딕", 11))
        self.select_target_btn.clicked.connect(self._select_consolidator_target)
        target_layout.addWidget(self.select_target_btn)

        consolidator_layout.addLayout(target_layout)

        # 새 폴더 이름
        name_layout = QHBoxLayout()
        name_label = QLabel("새 폴더 이름:")
        name_label.setFont(QFont("맑은 고딕", 12))
        name_label.setMinimumWidth(100)
        name_layout.addWidget(name_label)

        self.folder_name_input = QLineEdit()
        self.folder_name_input.setText("통합폴더")
        self.folder_name_input.setPlaceholderText("생성할 폴더 이름...")
        name_layout.addWidget(self.folder_name_input, stretch=1)

        consolidator_layout.addLayout(name_layout)

        # 작업 모드 선택
        mode_layout = QHBoxLayout()
        mode_label = QLabel("작업 모드:")
        mode_label.setFont(QFont("맑은 고딕", 12))
        mode_label.setMinimumWidth(100)
        mode_layout.addWidget(mode_label)

        self.copy_radio = QCheckBox("복사 (원본 유지)")
        self.copy_radio.setChecked(True)
        self.copy_radio.setFont(QFont("맑은 고딕", 11))
        self.copy_radio.stateChanged.connect(lambda: self._set_consolidator_mode("copy"))
        mode_layout.addWidget(self.copy_radio)

        self.move_radio = QCheckBox("이동 (원본 삭제)")
        self.move_radio.setFont(QFont("맑은 고딕", 11))
        self.move_radio.setStyleSheet("color: #e74c3c;")
        self.move_radio.stateChanged.connect(lambda: self._set_consolidator_mode("move"))
        mode_layout.addWidget(self.move_radio)

        mode_layout.addStretch()
        consolidator_layout.addLayout(mode_layout)

        layout.addWidget(self.consolidator_input_group)
        self.consolidator_input_group.hide()  # 기본적으로 숨김

        # 3. 진행 표시 (ProgressArea)
        progress_group = QGroupBox("진행 상태")
        progress_layout = QVBoxLayout(progress_group)

        self.status_label = QLabel("대기 중...")
        self.status_label.setFont(QFont("Arial", 11))
        progress_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(progress_group)

        # 4. 로그 영역 (LogArea)
        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_group, stretch=1)

        # 5. 액션 버튼 (ActionButtons)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        self.run_btn = QPushButton("실행")
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.run_btn.clicked.connect(self._run_plugin)

        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setFont(QFont("Arial", 12))
        self.cancel_btn.clicked.connect(self._cancel_task)
        self.cancel_btn.setEnabled(False)

        self.open_folder_btn = QPushButton("결과 폴더 열기")
        self.open_folder_btn.setFont(QFont("Arial", 12))
        self.open_folder_btn.clicked.connect(self._open_result_folder)
        self.open_folder_btn.setEnabled(False)

        action_layout.addWidget(self.run_btn)
        action_layout.addWidget(self.cancel_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.open_folder_btn)

        layout.addLayout(action_layout)

    def set_plugin(self, plugin_id: str):
        """플러그인 설정"""
        from automations import get_registry
        registry = get_registry()

        self.current_plugin_id = plugin_id
        self.current_plugin = registry.get_plugin(plugin_id)

        if self.current_plugin:
            metadata = self.current_plugin.get_metadata()
            self.plugin_title.setText(metadata.name)

        # 초기화
        self.path_input.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("대기 중...")
        self.log_text.clear()
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.open_folder_btn.setEnabled(False)
        self.result_path = None

        # Consolidator 전용 초기화
        self.consolidator_sources = []
        self.consolidator_target_parent = ""
        self.consolidator_target_name = ""
        self.consolidator_mode = "copy"
        self.source_folders_list.clear()
        self.target_input.clear()
        self.folder_name_input.setText("통합폴더")
        self.copy_radio.setChecked(True)
        self.move_radio.setChecked(False)

        # 플러그인별 옵션 설정
        self._setup_plugin_options()

    def _setup_plugin_options(self):
        """플러그인별 옵션 위젯 설정"""
        # 기존 옵션 제거
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Consolidator인 경우 전용 UI 표시
        if self.current_plugin_id == "consolidator":
            self.input_group.hide()
            self.consolidator_input_group.show()
        else:
            self.input_group.show()
            self.consolidator_input_group.hide()

    def _browse_path(self):
        """파일/폴더 선택 다이얼로그"""
        # 플러그인 타입에 따라 파일/폴더 선택
        if self.current_plugin_id == 'merger':
            path = QFileDialog.getExistingDirectory(self, "폴더 선택")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "파일 선택", "",
                "HWP 파일 (*.hwp *.hwpx);;모든 파일 (*.*)"
            )

        if path:
            self.path_input.setText(path)

    # =========================================================================
    # Consolidator 전용 메서드들
    # =========================================================================
    def _select_consolidator_sources(self):
        """Consolidator: 소스 폴더 다중 선택"""
        dialog = MultiFolderSelectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.consolidator_sources = dialog.get_selected_folders()
            self.source_folders_list.clear()
            for folder in self.consolidator_sources:
                self.source_folders_list.addItem(folder)
            self._log('info', f"{len(self.consolidator_sources)}개 소스 폴더 선택됨")

    def _clear_consolidator_sources(self):
        """Consolidator: 소스 폴더 목록 초기화"""
        self.consolidator_sources = []
        self.source_folders_list.clear()
        self._log('info', "소스 폴더 목록 초기화됨")

    def _select_consolidator_target(self):
        """Consolidator: 대상 폴더 선택"""
        path = QFileDialog.getExistingDirectory(self, "통합 파일을 저장할 폴더의 위치 선택")
        if path:
            self.consolidator_target_parent = path
            self.target_input.setText(path)

    def _set_consolidator_mode(self, mode: str):
        """Consolidator: 작업 모드 설정"""
        if mode == "copy" and self.copy_radio.isChecked():
            self.consolidator_mode = "copy"
            self.move_radio.setChecked(False)
        elif mode == "move" and self.move_radio.isChecked():
            self.consolidator_mode = "move"
            self.copy_radio.setChecked(False)
        elif mode == "copy" and not self.copy_radio.isChecked():
            # copy가 해제되면 move 활성화
            self.move_radio.setChecked(True)
            self.consolidator_mode = "move"
        elif mode == "move" and not self.move_radio.isChecked():
            # move가 해제되면 copy 활성화
            self.copy_radio.setChecked(True)
            self.consolidator_mode = "copy"

    def _run_plugin(self):
        """플러그인 실행"""
        # Consolidator 전용 실행
        if self.current_plugin_id == "consolidator":
            self._run_consolidator()
            return

        # 일반 플러그인 실행
        input_path = self.path_input.text().strip()
        if not input_path:
            QMessageBox.warning(self, "경고", "파일 또는 폴더를 선택하세요.")
            return

        if not os.path.exists(input_path):
            QMessageBox.warning(self, "경고", "선택한 경로가 존재하지 않습니다.")
            return

        # UI 상태 변경
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.browse_btn.setEnabled(False)
        self.path_input.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.status_label.setText("실행 중...")

        self._log('info', f"입력 경로: {input_path}")
        self._log('info', f"플러그인: {self.current_plugin_id}")

        # 플러그인 실행 (직접 호출 - 기존 방식 유지)
        try:
            if self.current_plugin and self.current_plugin.has_ui():
                # 기존 Tkinter UI 호출 (임시 - 나중에 PyQt로 통합)
                self.current_plugin.run(ui=True)
                self._on_task_finished(True, "작업 완료")
            else:
                self._log('error', "UI가 없는 플러그인입니다.")
                self._on_task_finished(False, "UI 없음")
        except Exception as e:
            self._log('error', str(e))
            self._on_task_finished(False, str(e))

    def _run_consolidator(self):
        """Consolidator 전용 실행"""
        # 유효성 검사
        if not self.consolidator_sources:
            QMessageBox.warning(self, "경고", "소스 폴더를 선택하세요.")
            return

        target_parent = self.target_input.text().strip()
        if not target_parent:
            QMessageBox.warning(self, "경고", "대상 폴더 위치를 선택하세요.")
            return

        if not os.path.exists(target_parent):
            QMessageBox.warning(self, "경고", "대상 폴더 위치가 존재하지 않습니다.")
            return

        target_name = self.folder_name_input.text().strip()
        if not target_name:
            QMessageBox.warning(self, "경고", "새 폴더 이름을 입력하세요.")
            return

        # UI 상태 변경
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.select_sources_btn.setEnabled(False)
        self.select_target_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.status_label.setText("실행 중...")

        self._log('info', f"소스 폴더: {len(self.consolidator_sources)}개")
        for folder in self.consolidator_sources:
            self._log('info', f"  - {folder}")
        self._log('info', f"대상 위치: {target_parent}")
        self._log('info', f"새 폴더 이름: {target_name}")
        self._log('info', f"작업 모드: {self.consolidator_mode}")

        # 작업 실행
        try:
            from core.folder_consolidator import consolidate_parallel

            total, success, failed = consolidate_parallel(
                source_folders=self.consolidator_sources,
                target_parent=target_parent,
                target_name=target_name,
                mode=self.consolidator_mode,
                max_workers=5,
                verbose=True
            )

            # 결과 경로 저장
            self.result_path = os.path.join(target_parent, target_name)

            if failed == 0:
                self._on_task_finished(True, f"성공: {success}개 파일 통합 완료")
            else:
                self._on_task_finished(False, f"전체: {total}개, 성공: {success}개, 실패: {failed}개")

        except Exception as e:
            self._log('error', str(e))
            self._on_task_finished(False, str(e))

    def _cancel_task(self):
        """작업 취소"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self._log('warning', "작업 취소 요청...")

    def _on_progress(self, percent: int):
        """진행률 업데이트"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"진행 중... {percent}%")

    def _on_task_finished(self, success: bool, message: str):
        """작업 완료 처리"""
        self.run_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.browse_btn.setEnabled(True)
        self.path_input.setEnabled(True)

        # Consolidator 전용 버튼 복원
        if self.current_plugin_id == "consolidator":
            self.select_sources_btn.setEnabled(True)
            self.select_target_btn.setEnabled(True)

        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("완료!")
            self._log('success', message)
            self.open_folder_btn.setEnabled(True)
        else:
            self.status_label.setText("실패")
            self._log('error', message)

    def _log(self, level: str, message: str):
        """로그 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = LOG_COLORS.get(level, '#ffffff')

        # HTML 포맷으로 추가
        html = f'<span style="color: #888;">[{timestamp}]</span> '
        html += f'<span style="color: {color};">{message}</span><br>'

        self.log_text.moveCursor(QTextCursor.End)
        self.log_text.insertHtml(html)
        self.log_text.moveCursor(QTextCursor.End)

    def _open_result_folder(self):
        """결과 폴더 열기"""
        # Consolidator인 경우 결과 경로 사용
        if self.current_plugin_id == "consolidator" and self.result_path:
            folder = self.result_path
        else:
            path = self.path_input.text().strip()
            if not path:
                return
            folder = path if os.path.isdir(path) else os.path.dirname(path)

        if folder and os.path.exists(folder):
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

    def _on_back(self):
        """뒤로가기"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "확인",
                "작업이 진행 중입니다. 취소하고 돌아가시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.worker.cancel()
                self.worker.wait()
            else:
                return

        self.back_requested.emit()


# =============================================================================
# 메인 윈도우 (Specs Section 2: MainWindowLayout)
# =============================================================================
class MainWindow(QMainWindow):
    """PyQt 메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("HwpAutomation v2.0")
        self.setGeometry(30, 30, 1500, 1000)  # 더 크게
        self.setMinimumSize(1000, 800)

        self._setup_ui()
        self._apply_style()
        self._load_plugins()

    def _setup_ui(self):
        # QStackedWidget으로 화면 전환 (Specs Section 6)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 페이지 0: 플러그인 목록
        self.list_page = PluginListPage()
        self.list_page.plugin_selected.connect(self._on_plugin_selected)
        self.stack.addWidget(self.list_page)

        # 페이지 1: 플러그인 실행
        self.exec_page = PluginExecutionPage()
        self.exec_page.back_requested.connect(self._show_list_page)
        self.stack.addWidget(self.exec_page)

        # 상태바
        self.statusBar().showMessage("플러그인을 선택하세요")

    def _apply_style(self):
        """다크 테마 적용"""
        self.setStyleSheet(DARK_STYLE)

    def _load_plugins(self):
        """플러그인 로드"""
        self.list_page.load_plugins()

    def _on_plugin_selected(self, plugin_id: str):
        """플러그인 선택 시 실행 화면으로 전환"""
        self.exec_page.set_plugin(plugin_id)
        self.stack.setCurrentIndex(1)
        self.statusBar().showMessage(f"플러그인: {plugin_id}")

    def _show_list_page(self):
        """목록 화면으로 돌아가기"""
        self.stack.setCurrentIndex(0)
        self.statusBar().showMessage("플러그인을 선택하세요")


# =============================================================================
# 로깅 설정 (Specs/UI/WindowsAppBuild.idr - Windowed 모드용)
# =============================================================================
def setup_logging():
    """
    Windowed 모드(PyInstaller --windowed)에서 에러 로그를 파일로 저장

    Idris2 명세: Specs/UI/WindowsAppBuild.idr - ConsoleMode.Windowed
    - WithConsole: 콘솔에서 에러 확인 가능 (개발/디버깅용)
    - Windowed: 콘솔 숨김, 로그 파일로 저장 (배포용)
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        log_dir = os.path.dirname(sys.executable)
        log_file = os.path.join(log_dir, 'hwpautomation.log')

        try:
            # 로그 파일 열기 (append 모드, UTF-8)
            log_handle = open(log_file, 'a', encoding='utf-8')
            sys.stdout = log_handle
            sys.stderr = log_handle

            # 시작 로그
            print(f"\n{'='*60}")
            print(f"=== HwpAutomation 시작: {datetime.now()} ===")
            print(f"{'='*60}")
            print(f"실행 파일: {sys.executable}")
            print(f"로그 파일: {log_file}")
            print(f"Python 버전: {sys.version}")
            print()

        except Exception as e:
            # 로그 파일 생성 실패 시 무시 (GUI는 정상 작동)
            pass


# =============================================================================
# 메인 함수
# =============================================================================
def main():
    # 로깅 설정 (Windowed 모드에서 에러 로그를 파일로 저장)
    setup_logging()

    # UTF-8 출력 설정 (Windows CP949 호환성) - frozen이 아닌 경우만
    if sys.platform == 'win32' and not getattr(sys, 'frozen', False):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 크로스 플랫폼 일관성

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
