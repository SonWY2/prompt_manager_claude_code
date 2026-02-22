"""
[overview]
새 태스크 생성 다이얼로그

[description]
메인 화면에서 새 태스크 이름을 입력받는 모던 스타일 커스텀 다이얼로그입니다.
"""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QLineEdit, QWidget, QPushButton

from src.gui.widgets.modal_dialog_factory import (
    center_dialog_on_parent_or_screen,
    get_modal_primary_button_style,
    get_modal_secondary_button_style,
    get_modal_title_style,
    get_modal_subtitle_style,
    get_modal_line_edit_style,
    MODAL_BUTTON_MIN_HEIGHT,
    MODAL_BUTTON_MIN_WIDTH,
    MODAL_INPUT_MIN_HEIGHT,
    MODAL_MIN_WIDTH,
    MODAL_BUTTON_SPACING,
    setup_modal_dialog,
)


class NewTaskDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create New Task")
        self.setMinimumWidth(MODAL_MIN_WIDTH)

        layout = setup_modal_dialog(self, object_name="newTaskCard")

        title_label = QLabel("Create New Task")
        title_label.setStyleSheet(get_modal_title_style())
        layout.addWidget(title_label)

        subtitle_label = QLabel("Enter a clear task name to organize prompts.")
        subtitle_label.setStyleSheet(get_modal_subtitle_style())
        layout.addWidget(subtitle_label)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Task name")
        self._name_input.setMinimumHeight(MODAL_INPUT_MIN_HEIGHT)
        self._name_input.setStyleSheet(get_modal_line_edit_style())
        self._name_input.returnPressed.connect(self._accept_if_valid)
        self._name_input.textChanged.connect(self._update_create_button_state)
        layout.addWidget(self._name_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(MODAL_BUTTON_SPACING)
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setMinimumHeight(MODAL_BUTTON_MIN_HEIGHT)
        cancel_button.setMinimumWidth(MODAL_BUTTON_MIN_WIDTH)
        cancel_button.setStyleSheet(get_modal_secondary_button_style())
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._create_button = QPushButton("Create")
        self._create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_button.setMinimumHeight(MODAL_BUTTON_MIN_HEIGHT)
        self._create_button.setMinimumWidth(MODAL_BUTTON_MIN_WIDTH)
        self._create_button.setStyleSheet(get_modal_primary_button_style())
        self._create_button.clicked.connect(self._accept_if_valid)
        button_layout.addWidget(self._create_button)

        layout.addLayout(button_layout)

        self._update_create_button_state()
        self._name_input.setFocus()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        QTimer.singleShot(0, self.center_on_parent_or_screen)

    @property
    def task_name(self) -> str:
        return self._name_input.text().strip()

    def _update_create_button_state(self) -> None:
        self._create_button.setEnabled(bool(self.task_name))

    def _accept_if_valid(self) -> None:
        if self.task_name:
            self.accept()

    def center_on_parent_or_screen(self) -> None:
        center_dialog_on_parent_or_screen(self)
