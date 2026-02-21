"""
[overview]
메인 윈도우

[description]
3단 QSplitter 레이아웃과 Modern Dark Mode 테마가 적용된 메인 윈도우
"""

from typing import Optional

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QToolBar,
)

from src.gui.widgets.task_navigator import TaskNavigator
from src.gui.widgets.prompt_editor import PromptEditor
from src.gui.widgets.result_viewer import ResultViewer
from src.gui.widgets.provider_management_widget import ProviderManagementWidget
from src.gui.theme import (
    COLOR_BACKGROUND,
    COLOR_SIDEBAR,
    COLOR_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_BORDER,
)
from src.core.task_manager import TaskManager
from src.core.provider_manager import ProviderManager
from src.core.llm_service import LLMService
from src.core.template_engine import TemplateEngine
from PySide6.QtWidgets import QInputDialog, QDialog, QVBoxLayout


def _get_stylesheet() -> str:
    """Modern Dark Mode QSS 스타일시트 생성

    Returns:
        str: QSS 스타일시트 문자열
    """
    return f"""
    QMainWindow {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT_PRIMARY};
    }}

    QWidget {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT_PRIMARY};
        border: none;
    }}

    QSplitter::handle:horizontal {{
        background-color: {COLOR_BORDER};
        width: 1px;
    }}

    QSplitter::handle:hover {{
        background-color: {COLOR_ACCENT};
    }}

    QLabel {{
        color: {COLOR_TEXT_PRIMARY};
        background-color: transparent;
    }}

    QMenuBar {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_PRIMARY};
        border-bottom: 1px solid {COLOR_BORDER};
    }}

    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 16px;
    }}

    QMenuBar::item:selected {{
        background-color: {COLOR_ACCENT};
    }}

    QMenu {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
    }}

    QMenu::item {{
        padding: 8px 24px;
    }}

    QMenu::item:selected {{
        background-color: {COLOR_ACCENT};
    }}

    QToolBar {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_PRIMARY};
        border-bottom: 1px solid {COLOR_BORDER};
        spacing: 4px;
    }}

    QToolBar::item {{
        background-color: transparent;
        padding: 4px;
    }}

    QToolBar::item:hover {{
        background-color: rgba(0, 122, 204, 0.2);
    }}
    """


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""

    def __init__(self) -> None:
        """MainWindow 초기화"""
        super().__init__()

        self.setWindowTitle("Prompt Manager")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(_get_stylesheet())

        self._current_task_id: Optional[str] = None
        self._task_manager = TaskManager()
        self._provider_manager = ProviderManager()

        self._setup_ui()
        self._connect_signals()

        self._load_tasks()

    def _setup_ui(self) -> None:
        """UI 설정"""
        self._setup_menu_bar()
        self._setup_tool_bar()
        self._setup_layout()

    def _load_tasks(self) -> None:
        self._task_navigator.clear_tasks()

        tasks = self._task_manager.get_all_tasks()
        for task in tasks:
            self._task_navigator.add_task(
                name=task.name,
                version="1.0",
                description=task.description,
                task_id=task.id,
            )

    def _setup_menu_bar(self) -> None:
        """메뉴바 설정"""
        menubar = self.menuBar()

        # File 메뉴
        file_menu = menubar.addMenu("&File")
        file_menu.setObjectName("File")

        new_task_action = QAction("&New Task", self)
        new_task_action.setShortcut("Ctrl+T")
        new_task_action.setStatusTip("Create a new task")
        file_menu.addAction(new_task_action)

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save current task")
        file_menu.addAction(save_action)

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        file_menu.addAction(exit_action)

        # Edit 메뉴
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.setObjectName("Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        # View 메뉴
        view_menu = menubar.addMenu("&View")
        view_menu.setObjectName("View")

        toggle_navigator_action = QAction("Toggle &Navigator", self)
        toggle_navigator_action.setShortcut("Ctrl+1")
        toggle_navigator_action.setCheckable(True)
        toggle_navigator_action.setChecked(True)
        toggle_navigator_action.triggered.connect(self._toggle_navigator)
        view_menu.addAction(toggle_navigator_action)

        toggle_editor_action = QAction("Toggle &Editor", self)
        toggle_editor_action.setShortcut("Ctrl+2")
        toggle_editor_action.setCheckable(True)
        toggle_editor_action.setChecked(True)
        toggle_editor_action.triggered.connect(self._toggle_editor)
        view_menu.addAction(toggle_editor_action)

        toggle_viewer_action = QAction("Toggle &Viewer", self)
        toggle_viewer_action.setShortcut("Ctrl+3")
        toggle_viewer_action.setCheckable(True)
        toggle_viewer_action.setChecked(True)
        toggle_viewer_action.triggered.connect(self._toggle_viewer)
        view_menu.addAction(toggle_viewer_action)

        view_menu.addSeparator()

        fullscreen_action = QAction("&Full Screen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        settings_menu = menubar.addMenu("&Settings")
        settings_menu.setObjectName("Settings")

        provider_settings_action = QAction("&LLM Providers", self)
        provider_settings_action.setStatusTip("Manage LLM providers")
        provider_settings_action.triggered.connect(self._on_provider_settings)
        settings_menu.addAction(provider_settings_action)

    def _setup_tool_bar(self) -> None:
        """툴바 설정"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New Task 버튼
        new_task_action = QAction("New Task", self)
        new_task_action.setStatusTip("Create a new task")
        toolbar.addAction(new_task_action)

        toolbar.addSeparator()

        # Save 버튼
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save current task")
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Run 버튼
        run_action = QAction("Run", self)
        run_action.setShortcut("F5")
        run_action.setStatusTip("Run prompt")
        toolbar.addAction(run_action)

    def _setup_layout(self) -> None:
        """3단 QSplitter 레이아웃 설정"""
        self._main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._main_splitter.setHandleWidth(1)
        self._main_splitter.setObjectName("main_splitter")

        # 왼쪽 패널: Task Navigator
        self._task_navigator = TaskNavigator()
        self._main_splitter.addWidget(self._task_navigator)

        # 중앙 패널: Prompt Editor
        self._prompt_editor = PromptEditor()
        self._main_splitter.addWidget(self._prompt_editor)

        # 오른쪽 패널: Result Viewer
        self._result_viewer = ResultViewer(self._provider_manager)
        self._main_splitter.addWidget(self._result_viewer)

        # 초기 비율 설정
        self._main_splitter.setStretchFactor(0, 0)
        self._main_splitter.setStretchFactor(1, 1)
        self._main_splitter.setStretchFactor(2, 0)
        self._main_splitter.setSizes([250, 600, 350])

        self.setCentralWidget(self._main_splitter)

    def _connect_signals(self) -> None:
        """시그널 연결"""
        self._task_navigator.task_selected.connect(self._on_task_selected)
        self._task_navigator.new_task_clicked.connect(self._on_new_task)
        self._prompt_editor.prompt_changed.connect(self._on_prompt_changed)
        self._result_viewer.run_clicked.connect(self._on_run_clicked)

        for action in self.findChildren(QAction):
            if action.text() == "&New Task" or action.text() == "New Task":
                action.triggered.connect(self._on_new_task)

    def _on_task_selected(self, task_id: str) -> None:
        """태스크 선택 핸들러

        Args:
            task_id: 선택된 태스크 ID
        """
        self._current_task_id = task_id

    def _on_new_task(self) -> None:
        """새 태스크 생성 핸들러"""
        task_name, ok = QInputDialog.getText(
            self,
            "New Task",
            "Enter task name:",
        )

        if ok and task_name.strip():
            task = self._task_manager.create_task(
                name=task_name.strip(),
                description=None,
            )

            self._task_navigator.add_task(
                name=task.name,
                version="1.0",
                description=task.description,
                task_id=task.id,
            )

            self._current_task_id = task.id
            self._prompt_editor.clear_prompts()

    def _on_prompt_changed(self, prompt_type: str) -> None:
        """프롬프트 변경 핸들러

        Args:
            prompt_type: 변경된 프롬프트 타입 ("system" 또는 "user")
        """
        if self._current_task_id is None:
            return

        self.setWindowModified(True)

    def _on_run_clicked(self, model: str) -> None:
        """RUN 버튼 클릭 핸들러

        Args:
            model: 선택된 모델 이름
        """
        if self._current_task_id is None:
            self._result_viewer.display_error("No task selected")
            return

        system_prompt = self._prompt_editor.get_system_prompt()
        user_prompt = self._prompt_editor.get_user_prompt()
        template_variables = self._prompt_editor.get_variable_values()

        if not system_prompt and not user_prompt:
            self._result_viewer.display_error("Prompt is empty")
            return

        self._result_viewer.set_loading(True)

        try:
            provider_id = self._result_viewer.get_selected_provider_id()
            if provider_id is None:
                self._result_viewer.display_error(
                    "No provider selected. Configure and select a provider first."
                )
                return

            provider = self._provider_manager.get_provider(provider_id)
            if provider is None:
                self._result_viewer.display_error("Selected provider not found")
                return

            llm_service = LLMService(provider)
            rendered_system_prompt = TemplateEngine(system_prompt).render(
                template_variables
            )
            rendered_user_prompt = TemplateEngine(user_prompt).render(
                template_variables
            )
            rendered_prompt = f"System Prompt:\n{rendered_system_prompt}\n\nUser Prompt:\n{rendered_user_prompt}"
            result = llm_service.call_llm(rendered_prompt)

            output = str(result.get("output", ""))
            execution_time_ms = int(result.get("execution_time_ms", 0))
            tokens_used = result.get("tokens_used")

            self._result_viewer.display_result(output)
            latency_seconds = execution_time_ms / 1000
            input_tokens = len(rendered_system_prompt.split()) + len(
                rendered_user_prompt.split()
            )
            output_tokens = int(tokens_used or 0)
            self._result_viewer.set_metrics(
                latency=latency_seconds,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,
            )
            self._result_viewer.add_to_history(
                output,
                model=model,
                latency=latency_seconds,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=0.0,
            )
        except requests.exceptions.RequestException as e:
            self._result_viewer.display_error(f"LLM request failed: {str(e)}")
        except ValueError as e:
            self._result_viewer.display_error(f"Invalid LLM response: {str(e)}")
        except RuntimeError as e:
            self._result_viewer.display_error(f"Execution failed: {str(e)}")
        except KeyError as e:
            self._result_viewer.display_error(f"Response missing field: {str(e)}")
        except TypeError as e:
            self._result_viewer.display_error(str(e))
        finally:
            self._result_viewer.set_loading(False)

    def _toggle_navigator(self, visible: bool) -> None:
        """Task Navigator 토글

        Args:
            visible: 표시 여부
        """
        if not visible:
            self._main_splitter.setSizes([0, 600, 350])
        else:
            self._main_splitter.setSizes([250, 600, 350])

    def _toggle_editor(self, visible: bool) -> None:
        """Prompt Editor 토글

        Args:
            visible: 표시 여부
        """
        if not visible:
            self._main_splitter.setSizes([250, 0, 350])
        else:
            self._main_splitter.setSizes([250, 600, 350])

    def _toggle_viewer(self, visible: bool) -> None:
        """Result Viewer 토글

        Args:
            visible: 표시 여부
        """
        if not visible:
            self._main_splitter.setSizes([250, 600, 0])
        else:
            self._main_splitter.setSizes([250, 600, 350])

    def _toggle_fullscreen(self) -> None:
        """전체화면 토글"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _on_provider_settings(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("LLM Provider Settings")
        dialog.setMinimumSize(1100, 700)

        layout = QVBoxLayout()
        provider_management = ProviderManagementWidget(self._provider_manager)
        layout.addWidget(provider_management)
        dialog.setLayout(layout)

        provider_management.load_providers()

        result = dialog.exec()

        # Provider 설정이 변경되었으므로 모델 목록 새로고침
        if result == QDialog.DialogCode.Accepted:
            self._result_viewer.refresh_models()
