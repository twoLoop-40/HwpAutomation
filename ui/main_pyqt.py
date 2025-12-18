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
"""

import sys
import io
import os
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path

# UTF-8 출력 설정 (Windows CP949 호환성)
# main() 함수에서 설정 (import 시점 문제 방지)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPushButton, QMessageBox,
    QStackedWidget, QProgressBar, QTextEdit, QFileDialog, QLineEdit,
    QGroupBox, QCheckBox, QSpinBox, QComboBox, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor, QColor

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

        # 2. 입력 영역 (InputArea)
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

        # 플러그인별 옵션 설정
        self._setup_plugin_options()

    def _setup_plugin_options(self):
        """플러그인별 옵션 위젯 설정"""
        # 기존 옵션 제거
        while self.options_layout.count():
            item = self.options_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 플러그인별 옵션 추가 (필요시 확장)
        # 현재는 기본 옵션만

    def _browse_path(self):
        """파일/폴더 선택 다이얼로그"""
        # 플러그인 타입에 따라 파일/폴더 선택
        if self.current_plugin_id in ['merger', 'consolidator']:
            path = QFileDialog.getExistingDirectory(self, "폴더 선택")
        else:
            path, _ = QFileDialog.getOpenFileName(
                self, "파일 선택", "",
                "HWP 파일 (*.hwp *.hwpx);;모든 파일 (*.*)"
            )

        if path:
            self.path_input.setText(path)

    def _run_plugin(self):
        """플러그인 실행"""
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
        path = self.path_input.text().strip()
        if path:
            folder = path if os.path.isdir(path) else os.path.dirname(path)
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
# 메인 함수
# =============================================================================
def main():
    # UTF-8 출력 설정 (Windows CP949 호환성)
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 크로스 플랫폼 일관성

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
