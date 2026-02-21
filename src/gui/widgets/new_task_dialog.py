"""
[overview]
새 태스크 생성 다이얼로그

[description]
메인 화면에서 새 태스크 이름을 입력받는 모던 스타일 커스텀 다이얼로그입니다.
"""

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.gui.theme import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_PRESSED,
    COLOR_BORDER,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_SIDEBAR,
    COLOR_TEXT_ON_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)

POPUP_MIN_WIDTH: int = 420
POPUP_PADDING: int = 20
POPUP_SPACING: int = 12
POPUP_BUTTON_SPACING: int = 8
POPUP_OUTER_MARGIN: int = 12
POPUP_INPUT_MIN_HEIGHT: int = 40
POPUP_BUTTON_MIN_HEIGHT: int = 38
POPUP_BUTTON_MIN_WIDTH: int = 96
POPUP_CARD_RADIUS: int = 12
POPUP_SHADOW_BLUR: int = 28
POPUP_SHADOW_OFFSET_Y: int = 8
POPUP_SHADOW_ALPHA: int = 48


class NewTaskDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create New Task")
        self.setModal(True)
        self.setMinimumWidth(POPUP_MIN_WIDTH)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(
            POPUP_OUTER_MARGIN,
            POPUP_OUTER_MARGIN,
            POPUP_OUTER_MARGIN,
            POPUP_OUTER_MARGIN,
        )
        outer_layout.setSpacing(0)

        card = QWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(
            POPUP_PADDING,
            POPUP_PADDING,
            POPUP_PADDING,
            POPUP_PADDING,
        )
        card_layout.setSpacing(POPUP_SPACING)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(POPUP_SHADOW_BLUR)
        shadow.setOffset(0, POPUP_SHADOW_OFFSET_Y)
        shadow.setColor(QColor(15, 23, 42, POPUP_SHADOW_ALPHA))
        card.setGraphicsEffect(shadow)
        card.setObjectName("newTaskCard")

        title_label = QLabel("Create New Task")
        title_label.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 12pt; font-weight: 600;"
        )
        card_layout.addWidget(title_label)

        subtitle_label = QLabel("Enter a clear task name to organize prompts.")
        subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 9pt;")
        card_layout.addWidget(subtitle_label)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Task name")
        self._name_input.setMinimumHeight(POPUP_INPUT_MIN_HEIGHT)
        self._name_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 10px;
                padding: 0px 12px;
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_ACCENT};
            }}
            """
        )
        self._name_input.returnPressed.connect(self._accept_if_valid)
        self._name_input.textChanged.connect(self._update_create_button_state)
        card_layout.addWidget(self._name_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(POPUP_BUTTON_SPACING)
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setMinimumHeight(POPUP_BUTTON_MIN_HEIGHT)
        cancel_button.setMinimumWidth(POPUP_BUTTON_MIN_WIDTH)
        cancel_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                border-radius: 10px;
                padding: 0px 14px;
                font-size: 10pt;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            """
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._create_button = QPushButton("Create")
        self._create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._create_button.setMinimumHeight(POPUP_BUTTON_MIN_HEIGHT)
        self._create_button.setMinimumWidth(POPUP_BUTTON_MIN_WIDTH)
        self._create_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_ON_ACCENT};
                border: none;
                border-radius: 10px;
                padding: 0px 14px;
                font-size: 10pt;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ACCENT_PRESSED};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_SECONDARY};
            }}
            """
        )
        self._create_button.clicked.connect(self._accept_if_valid)
        button_layout.addWidget(self._create_button)

        card_layout.addLayout(button_layout)

        outer_layout.addWidget(card)

        self.setLayout(outer_layout)
        self.setStyleSheet(
            f"""
            QDialog {{
                background: transparent;
            }}
            QWidget {{
                background: transparent;
            }}
            QWidget#newTaskCard {{
                background-color: {COLOR_SIDEBAR};
                border: 1px solid {COLOR_BORDER};
                border-radius: {POPUP_CARD_RADIUS}px;
            }}
            """
        )

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
        self.adjustSize()

        parent_widget = self.parentWidget()
        if parent_widget is not None and parent_widget.isVisible():
            target_center = parent_widget.mapToGlobal(parent_widget.rect().center())
        else:
            screen = self.screen() or QApplication.primaryScreen()
            if screen is None:
                return
            target_center = screen.availableGeometry().center()

        target_x = int(target_center.x() - (self.width() / 2))
        target_y = int(target_center.y() - (self.height() / 2))
        self.move(target_x, target_y)
