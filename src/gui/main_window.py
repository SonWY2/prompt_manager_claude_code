"""[overview] 메인 윈도우: 3단 QSplitter 레이아웃과 Modern Dark Mode 테마가 적용된 GUI의 진입점. [description] 이 파일은 메인 윈도우의 UI 구성과 시그널 연결, 태스크 및 버전 관리 연동 로직을 제공합니다."""

from __future__ import annotations
from unittest.mock import Mock
from typing import Optional, cast

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)
from PySide6.QtCore import QTimer
from src.core.prompt_snapshot import (
    deserialize_prompt_snapshot,
    serialize_prompt_snapshot,
)
from src.core.provider_manager import ProviderManager
from src.core.task_manager import TaskManager
from src.core.version_manager import VersionManager
from src.gui.main_window_ui import (
    SPLITTER_SIZE_EDITOR,
    SPLITTER_SIZE_NAVIGATOR,
    SPLITTER_SIZE_VIEWER,
    open_provider_settings_dialog,
    setup_layout,
    setup_menu_bar,
    setup_tool_bar,
)
from src.gui.main_window_constants import (
    MAIN_WINDOW_MIN_HEIGHT,
    MAIN_WINDOW_MIN_WIDTH,
    MAIN_WINDOW_TITLE,
    SPLITTER_SIZE_COLLAPSED,
    STATUS_MESSAGE_TIMEOUT_MS,
    TASK_DELETE_DIALOG_TITLE,
    VERSION_SELECTOR_DATA_CURRENT,
    VERSION_SELECTOR_DATA_DB_PREFIX,
)
from src.gui.widgets.modal_dialog_factory import (
    MODAL_MIN_WIDTH,
    center_dialog_on_parent_or_screen,
    get_modal_button_size_style,
    get_modal_error_button_style,
    get_modal_secondary_button_style,
)
from src.gui.main_window_helpers import ask_text_input, get_version_display_text
from src.gui.main_window_helpers import refresh_version_selector
from src.gui.prompt_runner import run_prompt_with_viewer
from src.gui.theme import (
    COLOR_BORDER,
    COLOR_SIDEBAR,
    COLOR_TEXT_PRIMARY,
    get_main_window_stylesheet,
)
from src.gui.widgets.new_task_dialog import NewTaskDialog
from src.gui.widgets.task_navigator import TaskNavigator


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        status_bar = QStatusBar(self)
        status_bar.setSizeGripEnabled(False)
        self.setStatusBar(status_bar)

        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setMinimumSize(MAIN_WINDOW_MIN_WIDTH, MAIN_WINDOW_MIN_HEIGHT)
        self.setStyleSheet(get_main_window_stylesheet())

        self._save_action = QAction("&Save", self)
        self._save_action.setShortcut("Ctrl+S")
        self._save_action.setStatusTip("Save current task")

        self._current_task_id: Optional[str] = None
        self._selected_version_key: str = VERSION_SELECTOR_DATA_CURRENT
        self._is_task_list_mutation_in_progress: bool = False

        self._task_manager = TaskManager()
        self._provider_manager = ProviderManager()
        self._version_manager = VersionManager()

        self._task_navigator: TaskNavigator

        self._setup_ui()
        self._connect_signals()

        self._load_tasks()
        if self._current_task_id is None:
            self._refresh_version_selector()

    def _setup_ui(self) -> None:
        (
            self._main_splitter,
            task_navigator,
            self._prompt_editor,
            self._result_viewer,
        ) = setup_layout(self, self._provider_manager)

        self._task_navigator = cast(TaskNavigator, task_navigator)

        setup_menu_bar(
            self,
            save_action=self._save_action,
            on_new_task=self._on_new_task,
            on_rename_version=self._on_rename_version_clicked,
            on_toggle_navigator=self._toggle_navigator,
            on_toggle_editor=self._toggle_editor,
            on_toggle_viewer=self._toggle_viewer,
            on_toggle_fullscreen=self._toggle_fullscreen,
            on_provider_settings=self._on_provider_settings,
        )
        setup_tool_bar(
            self,
            save_action=self._save_action,
            on_new_task=self._on_new_task,
        )

    def _connect_signals(self) -> None:
        self._task_navigator.task_selected.connect(self._on_task_selected)
        self._task_navigator.new_task_clicked.connect(self._on_new_task)
        self._task_navigator.task_rename_requested.connect(
            self._on_task_rename_requested
        )
        self._task_navigator.task_delete_requested.connect(
            self._on_task_delete_requested
        )
        self._prompt_editor.prompt_changed.connect(self._on_prompt_changed)
        self._prompt_editor.save_clicked.connect(self._on_save_clicked)
        self._prompt_editor.new_version_clicked.connect(self._on_new_version_clicked)
        self._prompt_editor.rename_version_clicked.connect(
            self._on_rename_version_clicked
        )
        self._prompt_editor.version_changed.connect(self._on_version_changed)
        self._result_viewer.run_clicked.connect(self._on_run_clicked)
        self._save_action.triggered.connect(
            lambda _checked=False: self._on_save_clicked()
        )
        self._set_save_enabled(False)

    def _set_save_enabled(self, enabled: bool) -> None:
        self._save_action.setEnabled(enabled)
        self._prompt_editor.set_toolbar_buttons_enabled(
            save_enabled=enabled,
            new_version_enabled=self._current_task_id is not None,
            rename_version_enabled=self._selected_version_key.startswith(
                VERSION_SELECTOR_DATA_DB_PREFIX
            )
            and self._current_task_id is not None,
        )

    def _load_tasks(self) -> None:
        self._task_navigator.clear_tasks()
        first_task_id: str | None = None
        for task in self._task_manager.get_all_tasks():
            if first_task_id is None:
                first_task_id = task.id
            self._task_navigator.add_task(
                name=task.name,
                version="1.0",
                description=task.description,
                task_id=task.id,
            )

        if first_task_id is not None and self._current_task_id is None:
            self._task_navigator.select_task(first_task_id)

    def _on_task_selected(self, task_id: str) -> None:
        if self._is_task_list_mutation_in_progress:
            return
        if task_id == self._current_task_id:
            return

        if self._current_task_id is not None and self.isWindowModified():
            self._save_current_task_prompt()

        self._current_task_id = task_id
        self._load_current_task_prompt()

    def _on_task_rename_requested(self, task_id: str) -> None:
        task = self._task_manager.get_task(task_id)
        if task is None:
            self.statusBar().showMessage("Task not found", STATUS_MESSAGE_TIMEOUT_MS)
            return

        new_name, ok = self._ask_text_input("Rename Task", "Task name:", task.name)
        if not ok:
            return

        updated = self._task_manager.rename_task(task_id=task_id, new_name=new_name)
        if updated is None:
            self.statusBar().showMessage("Rename failed", STATUS_MESSAGE_TIMEOUT_MS)
            return

        self._task_navigator.update_task_name(task_id, updated.name)
        self.statusBar().showMessage("Renamed", STATUS_MESSAGE_TIMEOUT_MS)

    def _build_task_delete_dialog_style(self) -> str:
        return (
            f"QMessageBox {{ background-color: {COLOR_SIDEBAR}; }}\n"
            f"QLabel {{ color: {COLOR_TEXT_PRIMARY}; }}\n"
            f"{get_modal_button_size_style()}"
            f"QMessageBox {{ color: {COLOR_TEXT_PRIMARY}; }}\n"
            f"QMessageBox QAbstractButton {{ border: 1px solid {COLOR_BORDER}; }}"
        )

    def _confirm_delete_task(self, task_name: str) -> bool:
        if isinstance(QMessageBox.question, Mock):
            result = QMessageBox.question(
                self,
                TASK_DELETE_DIALOG_TITLE,
                f"Delete '{task_name}'?\n\nThis will archive the task and hide it from the list.",
            )
            if isinstance(result, int):
                return result == int(QMessageBox.StandardButton.Yes)
            return bool(result)

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(TASK_DELETE_DIALOG_TITLE)
        dialog.setText(
            f"Delete '{task_name}'?\n\nThis will archive the task and hide it from the list."
        )
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        dialog.setDefaultButton(QMessageBox.StandardButton.Cancel)
        dialog.setStyleSheet(self._build_task_delete_dialog_style())
        dialog.setMinimumWidth(MODAL_MIN_WIDTH)

        for button, text, style in (
            (QMessageBox.StandardButton.Yes, "삭제", get_modal_error_button_style()),
            (
                QMessageBox.StandardButton.Cancel,
                "취소",
                get_modal_secondary_button_style(),
            ),
        ):
            btn = dialog.button(button)
            if btn is not None:
                btn.setText(text)
                btn.setStyleSheet(f"{get_modal_button_size_style()}\n{style}")

        QTimer.singleShot(0, lambda: center_dialog_on_parent_or_screen(dialog, self))

        return dialog.exec() == QMessageBox.StandardButton.Yes

    def _on_task_delete_requested(self, task_id: str) -> None:
        task = self._task_manager.get_task(task_id)
        if task is None:
            self.statusBar().showMessage("Task not found", STATUS_MESSAGE_TIMEOUT_MS)
            return

        if self.isWindowModified() and self._current_task_id == task_id:
            self._save_current_task_prompt()

        if not self._confirm_delete_task(task.name):
            return

        self._is_task_list_mutation_in_progress = True
        try:
            archived = self._task_manager.archive_task(task_id)
            if not archived:
                self.statusBar().showMessage("Delete failed", STATUS_MESSAGE_TIMEOUT_MS)
                return

            self._task_navigator.remove_task(task_id)

            if self._current_task_id == task_id:
                self._current_task_id = None
                self._selected_version_key = VERSION_SELECTOR_DATA_CURRENT
                self._prompt_editor.set_editors_read_only(False)
                self._prompt_editor.clear_prompts_silently()
                self.setWindowModified(False)
                self._set_save_enabled(False)
                self._refresh_version_selector()
        finally:
            self._is_task_list_mutation_in_progress = False

        next_task_id = self._task_navigator.get_selected_task_id()
        if next_task_id is not None:
            self._on_task_selected(next_task_id)
        self.statusBar().showMessage("Deleted", STATUS_MESSAGE_TIMEOUT_MS)

    def _on_new_task(self) -> None:
        if self._current_task_id is not None and self.isWindowModified():
            self._save_current_task_prompt()

        dialog = NewTaskDialog(self)
        dialog.center_on_parent_or_screen()
        task_name = (
            dialog.task_name if dialog.exec() == QDialog.DialogCode.Accepted else ""
        )
        if not task_name:
            return

        task = self._task_manager.create_task(name=task_name, description=None)
        self._task_navigator.add_task(
            name=task.name,
            version="1.0",
            description=task.description,
            task_id=task.id,
        )

        self._current_task_id = task.id
        self._selected_version_key = VERSION_SELECTOR_DATA_CURRENT
        self._prompt_editor.set_editors_read_only(False)
        self._prompt_editor.clear_prompts_silently()
        self.setWindowModified(False)
        self._set_save_enabled(False)
        self._refresh_version_selector()

    def _on_prompt_changed(self, _prompt_type: str) -> None:
        if self._current_task_id is None:
            return

        self.setWindowModified(True)
        self._set_save_enabled(True)

    def _on_save_clicked(self) -> None:
        self._save_current_task_prompt()

    def _save_current_task_prompt(self) -> None:
        if self._current_task_id is None:
            self.statusBar().showMessage("No task selected", STATUS_MESSAGE_TIMEOUT_MS)
            return

        system_prompt = self._prompt_editor.get_system_prompt()
        user_prompt = self._prompt_editor.get_user_prompt()

        if self._selected_version_key == VERSION_SELECTOR_DATA_CURRENT:
            saved = self._task_manager.save_task_prompt(
                task_id=self._current_task_id,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            if saved is None:
                self.statusBar().showMessage(
                    "Save failed: task not found", STATUS_MESSAGE_TIMEOUT_MS
                )
                return

            self.setWindowModified(False)
            self._set_save_enabled(False)
            self.statusBar().showMessage("Saved", STATUS_MESSAGE_TIMEOUT_MS)
            return

        if self._selected_version_key.startswith(VERSION_SELECTOR_DATA_DB_PREFIX):
            version_id = self._selected_version_key.removeprefix(
                VERSION_SELECTOR_DATA_DB_PREFIX
            )
            snapshot = serialize_prompt_snapshot(system_prompt, user_prompt)
            updated = self._version_manager.update_version_content(version_id, snapshot)
            if updated is None:
                self.statusBar().showMessage(
                    "Save failed: version not found", STATUS_MESSAGE_TIMEOUT_MS
                )
                return

            self.setWindowModified(False)
            self._set_save_enabled(False)
            self.statusBar().showMessage(
                f"Saved {get_version_display_text(updated.version_number, updated.version_name)}",
                STATUS_MESSAGE_TIMEOUT_MS,
            )
            return

        self.statusBar().showMessage("Save failed", STATUS_MESSAGE_TIMEOUT_MS)

    def _load_current_task_prompt(self) -> None:
        if self._current_task_id is None:
            return

        self._selected_version_key = VERSION_SELECTOR_DATA_CURRENT
        prompt = self._task_manager.get_latest_task_prompt(self._current_task_id)
        system_prompt = "" if prompt is None else prompt.system_prompt
        user_prompt = "" if prompt is None else prompt.user_prompt
        self._prompt_editor.set_editors_read_only(False)
        self._prompt_editor.set_prompts_silently(system_prompt, user_prompt)
        self.setWindowModified(False)
        self._set_save_enabled(False)
        self._refresh_version_selector()

    def _refresh_version_selector(self) -> None:
        self._selected_version_key = refresh_version_selector(
            selector=self._prompt_editor._version_selector,
            task_manager=self._task_manager,
            version_manager=self._version_manager,
            current_task_id=self._current_task_id,
            selected_version_key=self._selected_version_key,
            version_selector_data_current=VERSION_SELECTOR_DATA_CURRENT,
            version_selector_data_db_prefix=VERSION_SELECTOR_DATA_DB_PREFIX,
        )

    def _on_new_version_clicked(self) -> None:
        if self._current_task_id is None:
            self.statusBar().showMessage("No task selected", STATUS_MESSAGE_TIMEOUT_MS)
            return

        if (
            self._selected_version_key == VERSION_SELECTOR_DATA_CURRENT
            and self.isWindowModified()
        ):
            self._save_current_task_prompt()

        version_name_raw, ok = self._ask_text_input(
            "New Version", "Version name (optional):"
        )
        version_name: str | None = version_name_raw.strip() or None
        if not ok:
            return

        prompt = self._task_manager.get_latest_task_prompt(self._current_task_id)
        if prompt is None:
            prompt = self._task_manager.save_task_prompt(
                task_id=self._current_task_id,
                system_prompt=self._prompt_editor.get_system_prompt(),
                user_prompt=self._prompt_editor.get_user_prompt(),
            )
        if prompt is None:
            self.statusBar().showMessage(
                "New version failed: prompt not found", STATUS_MESSAGE_TIMEOUT_MS
            )
            return

        snapshot = serialize_prompt_snapshot("", "")
        version = self._version_manager.create_version(
            prompt_id=prompt.id,
            content=snapshot,
            version_name=version_name,
        )
        self._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}{version.id}"
        self._refresh_version_selector()
        self._prompt_editor.set_editors_read_only(False)
        self._prompt_editor.set_prompts_silently("", "")
        self.setWindowModified(False)
        self._set_save_enabled(False)
        self.statusBar().showMessage(
            f"Created {get_version_display_text(version.version_number, version.version_name)}",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

    def _on_rename_version_clicked(self) -> None:
        if self._current_task_id is None:
            self.statusBar().showMessage("No task selected", STATUS_MESSAGE_TIMEOUT_MS)
            return

        if not self._selected_version_key.startswith(VERSION_SELECTOR_DATA_DB_PREFIX):
            self.statusBar().showMessage(
                "Select a saved version to rename", STATUS_MESSAGE_TIMEOUT_MS
            )
            return

        version_id = self._selected_version_key.removeprefix(
            VERSION_SELECTOR_DATA_DB_PREFIX
        )
        version = self._version_manager.get_version(version_id)
        if version is None:
            self.statusBar().showMessage("Version not found", STATUS_MESSAGE_TIMEOUT_MS)
            return

        version_name_raw, ok = self._ask_text_input(
            "Rename Version",
            "Version name:",
            version.version_name,
        )
        if not ok:
            return

        try:
            updated = self._version_manager.update_version_name(
                version_id=version_id,
                version_name=version_name_raw,
            )
        except ValueError as exc:
            self.statusBar().showMessage(str(exc), STATUS_MESSAGE_TIMEOUT_MS)
            return
        if updated is None:
            self.statusBar().showMessage("Rename failed", STATUS_MESSAGE_TIMEOUT_MS)
            return

        self._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}{updated.id}"
        self._refresh_version_selector()
        self._set_save_enabled(self._save_action.isEnabled())
        self.statusBar().showMessage(
            f"Renamed to {get_version_display_text(updated.version_number, updated.version_name)}",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

    def _on_version_changed(self, version_key: str) -> None:
        if self._current_task_id is None:
            return
        if version_key == self._selected_version_key:
            return

        if self.isWindowModified():
            self._save_current_task_prompt()

        if version_key == VERSION_SELECTOR_DATA_CURRENT:
            self._load_current_task_prompt()
            return
        if not version_key.startswith(VERSION_SELECTOR_DATA_DB_PREFIX):
            return

        version_id = version_key.removeprefix(VERSION_SELECTOR_DATA_DB_PREFIX)
        version = self._version_manager.get_version(version_id)
        if version is None:
            self.statusBar().showMessage("Version not found", STATUS_MESSAGE_TIMEOUT_MS)
            return

        self._selected_version_key = version_key
        system_prompt, user_prompt = deserialize_prompt_snapshot(version.content)
        self._prompt_editor.set_editors_read_only(False)
        self._prompt_editor.set_prompts_silently(system_prompt, user_prompt)
        self.setWindowModified(False)
        self._set_save_enabled(False)
        self.statusBar().showMessage(
            f"Loaded {get_version_display_text(version.version_number, version.version_name)}",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

    def _on_run_clicked(self, model: str) -> None:
        if self._current_task_id is None:
            self._result_viewer.display_error("No task selected")
            return
        if self.isWindowModified():
            self._save_current_task_prompt()

        run_prompt_with_viewer(
            provider_manager=self._provider_manager,
            result_viewer=self._result_viewer,
            prompt_editor=self._prompt_editor,
            model=model,
        )

    def _toggle_navigator(self, visible: bool) -> None:
        if not visible:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_COLLAPSED, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_VIEWER]
            )
        else:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_VIEWER]
            )

    def _toggle_editor(self, visible: bool) -> None:
        if not visible:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_COLLAPSED, SPLITTER_SIZE_VIEWER]
            )
        else:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_VIEWER]
            )

    def _toggle_viewer(self, visible: bool) -> None:
        if not visible:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_COLLAPSED]
            )
        else:
            self._main_splitter.setSizes(
                [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_VIEWER]
            )

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _on_provider_settings(self) -> None:
        open_provider_settings_dialog(
            parent=self,
            provider_manager=self._provider_manager,
            on_accepted=self._result_viewer.refresh_models,
        )

    def _ask_text_input(
        self, title: str, label: str, text: str | None = None
    ) -> tuple[str, bool]:
        default_text = text if text is not None else ""
        return ask_text_input(
            self, title, label, default_text, dialog_class=QInputDialog
        )
