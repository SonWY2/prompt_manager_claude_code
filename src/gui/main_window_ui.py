"""\
[overview]
메인 윈도우 UI 빌더

[description]
MainWindow의 메뉴/툴바/레이아웃 생성 로직을 분리해 main_window.py의 책임을 줄입니다.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.core.provider_manager import ProviderManager
from src.gui.widgets.prompt_editor import PromptEditor
from src.gui.widgets.provider_management_widget import ProviderManagementWidget
from src.gui.widgets.result_viewer import ResultViewer
from src.gui.widgets.task_navigator import TaskNavigator


SPLITTER_SIZE_NAVIGATOR: int = 250
SPLITTER_SIZE_EDITOR: int = 600
SPLITTER_SIZE_VIEWER: int = 350


def _action(
    parent: QMainWindow,
    text: str,
    shortcut: str | None = None,
    status_tip: str | None = None,
    triggered: Callable[[bool], None] | None = None,
    checkable: bool = False,
    checked: bool = False,
) -> QAction:
    action = QAction(text, parent)
    if shortcut is not None:
        action.setShortcut(shortcut)
    if status_tip is not None:
        action.setStatusTip(status_tip)
    if checkable:
        action.setCheckable(True)
        action.setChecked(checked)
    if triggered is not None:
        action.triggered.connect(triggered)
    return action


def _ignore_checked(callback: Callable[[], None]) -> Callable[[bool], None]:
    def _wrapped(_checked: bool = False) -> None:
        callback()

    return _wrapped


def setup_menu_bar(
    main_window: QMainWindow,
    save_action: QAction,
    on_new_task: Callable[[], None],
    on_rename_version: Callable[[], None],
    on_toggle_navigator: Callable[[bool], None],
    on_toggle_editor: Callable[[bool], None],
    on_toggle_viewer: Callable[[bool], None],
    on_toggle_fullscreen: Callable[[], None],
    on_provider_settings: Callable[[], None],
) -> None:
    menubar = main_window.menuBar()

    def _on_exit(_checked: bool = False) -> None:
        main_window.close()

    file_menu = menubar.addMenu("&File")
    file_menu.setObjectName("File")
    file_menu.addAction(
        _action(
            main_window,
            "&New Task",
            shortcut="Ctrl+T",
            status_tip="Create a new task",
            triggered=_ignore_checked(on_new_task),
        )
    )
    file_menu.addSeparator()
    file_menu.addAction(save_action)
    file_menu.addAction(
        _action(
            main_window,
            "E&xit",
            shortcut="Ctrl+Q",
            status_tip="Exit application",
            triggered=_on_exit,
        )
    )

    edit_menu = menubar.addMenu("&Edit")
    edit_menu.setObjectName("Edit")
    edit_menu.addAction(_action(main_window, "&Undo", shortcut="Ctrl+Z"))
    edit_menu.addAction(_action(main_window, "&Redo", shortcut="Ctrl+Y"))
    edit_menu.addSeparator()
    edit_menu.addAction(
        _action(
            main_window,
            "Rename &Version",
            shortcut="Ctrl+Shift+R",
            status_tip="Rename selected version",
            triggered=_ignore_checked(on_rename_version),
        )
    )

    view_menu = menubar.addMenu("&View")
    view_menu.setObjectName("View")
    view_menu.addAction(
        _action(
            main_window,
            "Toggle &Navigator",
            shortcut="Ctrl+1",
            triggered=on_toggle_navigator,
            checkable=True,
            checked=True,
        )
    )
    view_menu.addAction(
        _action(
            main_window,
            "Toggle &Editor",
            shortcut="Ctrl+2",
            triggered=on_toggle_editor,
            checkable=True,
            checked=True,
        )
    )
    view_menu.addAction(
        _action(
            main_window,
            "Toggle &Viewer",
            shortcut="Ctrl+3",
            triggered=on_toggle_viewer,
            checkable=True,
            checked=True,
        )
    )
    view_menu.addSeparator()
    view_menu.addAction(
        _action(
            main_window,
            "&Full Screen",
            shortcut="F11",
            triggered=_ignore_checked(on_toggle_fullscreen),
        )
    )

    settings_menu = menubar.addMenu("&Settings")
    settings_menu.setObjectName("Settings")
    settings_menu.addAction(
        _action(
            main_window,
            "&LLM Providers",
            status_tip="Manage LLM providers",
            triggered=_ignore_checked(on_provider_settings),
        )
    )


def setup_tool_bar(
    main_window: QMainWindow,
    save_action: QAction,
    on_new_task: Callable[[], None],
) -> None:
    toolbar = QToolBar("Main Toolbar")
    toolbar.setMovable(False)
    main_window.addToolBar(toolbar)
    toolbar.addAction(
        _action(
            main_window,
            "New Task",
            status_tip="Create a new task",
            triggered=_ignore_checked(on_new_task),
        )
    )
    toolbar.addSeparator()
    toolbar.addAction(save_action)


def setup_layout(
    main_window: QMainWindow,
    provider_manager: ProviderManager,
) -> tuple[QSplitter, QWidget, PromptEditor, ResultViewer]:
    main_splitter = QSplitter(Qt.Orientation.Horizontal)
    main_splitter.setHandleWidth(1)
    main_splitter.setObjectName("main_splitter")

    task_navigator = TaskNavigator()
    main_splitter.addWidget(task_navigator)

    prompt_editor = PromptEditor()
    main_splitter.addWidget(prompt_editor)

    result_viewer = ResultViewer(provider_manager)
    main_splitter.addWidget(result_viewer)

    main_splitter.setStretchFactor(0, 0)
    main_splitter.setStretchFactor(1, 1)
    main_splitter.setStretchFactor(2, 0)
    main_splitter.setSizes(
        [SPLITTER_SIZE_NAVIGATOR, SPLITTER_SIZE_EDITOR, SPLITTER_SIZE_VIEWER]
    )

    main_window.setCentralWidget(main_splitter)
    return main_splitter, task_navigator, prompt_editor, result_viewer


def open_provider_settings_dialog(
    parent: QMainWindow,
    provider_manager: ProviderManager,
    on_accepted: Callable[[], None],
) -> None:
    dialog = QDialog(parent)
    dialog.setWindowTitle("LLM Provider Settings")
    dialog.setMinimumSize(1100, 700)

    layout = QVBoxLayout()
    provider_management = ProviderManagementWidget(provider_manager)
    layout.addWidget(provider_management)
    dialog.setLayout(layout)

    provider_management.load_providers()

    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        on_accepted()
