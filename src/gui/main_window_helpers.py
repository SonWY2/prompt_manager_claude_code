"""\
[overview]
메인 윈도우 헬퍼

[description]
MainWindow에서 사용되는 다이얼로그/버전 셀렉터 관련 보조 함수들을 분리합니다.
main_window.py의 라인 수를 줄이되, 런타임 동작은 동일하게 유지합니다.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QComboBox, QDialog, QInputDialog, QMainWindow

from src.core.task_manager import TaskManager
from src.core.version_manager import VersionManager
from src.gui.widgets.modal_dialog_factory import center_dialog_on_parent_or_screen


def get_version_display_text(
    version_number: int, version_name: str | None = None
) -> str:
    if version_name:
        return version_name
    return f"v{version_number}"


def position_dialog_at_parent_center(parent: QMainWindow, dialog: QDialog) -> None:
    center_dialog_on_parent_or_screen(dialog, parent)


def ask_text_input(
    parent: QMainWindow,
    title: str,
    label: str,
    default_text: str = "",
    *,
    dialog_class: type[QInputDialog] = QInputDialog,
) -> tuple[str, bool]:
    input_dialog = dialog_class(parent)
    input_dialog.setWindowTitle(title)
    input_dialog.setLabelText(label)
    input_dialog.setTextValue(default_text)
    position_dialog_at_parent_center(parent, input_dialog)
    result = input_dialog.exec()
    return input_dialog.textValue(), result == QDialog.DialogCode.Accepted


def refresh_version_selector(
    *,
    selector: QComboBox,
    task_manager: TaskManager,
    version_manager: VersionManager,
    current_task_id: str | None,
    selected_version_key: str,
    version_selector_data_current: str,
    version_selector_data_db_prefix: str,
    display_text: Callable[[int, str | None], str] = get_version_display_text,
) -> str:
    selected_data = selected_version_key

    selector.blockSignals(True)
    try:
        selector.clear()
        selector.addItem("Current", version_selector_data_current)

        if current_task_id is not None:
            prompt = task_manager.get_latest_task_prompt(current_task_id)
            if prompt is not None:
                for version in version_manager.get_timeline(prompt.id):
                    selector.addItem(
                        display_text(version.version_number, version.version_name),
                        f"{version_selector_data_db_prefix}{version.id}",
                    )

        selected_index = selector.findData(selected_data)
        if selected_index < 0:
            selected_data = version_selector_data_current
            selected_index = selector.findData(selected_data)
        if selected_index < 0:
            selected_index = 0
            selected_data = version_selector_data_current

        selector.setCurrentIndex(selected_index)
        return str(selected_data)
    finally:
        selector.blockSignals(False)
