"""
[overview]
공통 모달 다이얼로그 유틸리티

[description]
새 작업 다이얼로그와 변수 편집 다이얼로그에서 사용하는
프레임리스 카드형 모달의 공통 레이아웃 및 스타일을 제공합니다.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QDialog, QGraphicsDropShadowEffect, QVBoxLayout, QWidget

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
    COLOR_ERROR,
)

MODAL_MIN_WIDTH: int = 420
MODAL_PADDING: int = 20
MODAL_SPACING: int = 12
MODAL_BUTTON_SPACING: int = 8
MODAL_OUTER_MARGIN: int = 12
MODAL_INPUT_MIN_HEIGHT: int = 40
MODAL_BUTTON_MIN_HEIGHT: int = 38
MODAL_BUTTON_MIN_WIDTH: int = 96
MODAL_CARD_RADIUS: int = 12
MODAL_SHADOW_BLUR: int = 28
MODAL_SHADOW_OFFSET_Y: int = 8
MODAL_SHADOW_ALPHA: int = 48
MODAL_TITLE_FONT_SIZE: str = "12pt"
MODAL_SUBTITLE_FONT_SIZE: str = "9pt"


def setup_modal_dialog(
    dialog: QDialog,
    *,
    object_name: str,
    min_width: int = MODAL_MIN_WIDTH,
) -> QVBoxLayout:
    """프레임리스 카드형 모달 다이얼로그 기본 구조를 구성해 반환한다."""
    dialog.setModal(True)
    dialog.setMinimumWidth(min_width)
    dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
    dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    dialog.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

    outer_layout = QVBoxLayout()
    outer_layout.setContentsMargins(
        MODAL_OUTER_MARGIN,
        MODAL_OUTER_MARGIN,
        MODAL_OUTER_MARGIN,
        MODAL_OUTER_MARGIN,
    )
    outer_layout.setSpacing(0)

    card = QWidget(dialog)
    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(
        MODAL_PADDING,
        MODAL_PADDING,
        MODAL_PADDING,
        MODAL_PADDING,
    )
    card_layout.setSpacing(MODAL_SPACING)

    shadow = QGraphicsDropShadowEffect(dialog)
    shadow.setBlurRadius(MODAL_SHADOW_BLUR)
    shadow.setOffset(0, MODAL_SHADOW_OFFSET_Y)
    shadow.setColor(QColor(15, 23, 42, MODAL_SHADOW_ALPHA))
    card.setGraphicsEffect(shadow)
    card.setObjectName(object_name)

    outer_layout.addWidget(card)
    dialog.setLayout(outer_layout)
    dialog.setStyleSheet(_build_modal_dialog_stylesheet(object_name))

    return card_layout


def _build_modal_dialog_stylesheet(object_name: str) -> str:
    return f"""
    QDialog {{
        background: transparent;
    }}
    QWidget {{
        background: transparent;
    }}
    QWidget#{object_name} {{
        background-color: {COLOR_SIDEBAR};
        border: 1px solid {COLOR_BORDER};
        border-radius: {MODAL_CARD_RADIUS}px;
    }}
    """


def get_modal_title_style() -> str:
    return f"color: {COLOR_TEXT_PRIMARY}; font-size: {MODAL_TITLE_FONT_SIZE}; font-weight: 600;"


def get_modal_subtitle_style() -> str:
    return f"color: {COLOR_TEXT_SECONDARY}; font-size: {MODAL_SUBTITLE_FONT_SIZE};"


def get_modal_line_edit_style() -> str:
    return f"""
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


def get_modal_text_area_style() -> str:
    return f"""
    QPlainTextEdit {{
        background-color: {COLOR_INPUT_BG};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_INPUT_BORDER};
        border-radius: 10px;
        padding: 10px;
        font-size: 10pt;
    }}
    QPlainTextEdit:focus {{
        border: 1px solid {COLOR_ACCENT};
    }}
    """


def get_modal_primary_button_style() -> str:
    return f"""
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
    """


def get_modal_secondary_button_style() -> str:
    return f"""
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


def get_modal_error_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {COLOR_ERROR};
        color: {COLOR_TEXT_ON_ACCENT};
        border: none;
        border-radius: 10px;
        padding: 0px 14px;
        font-size: 10pt;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background-color: #E64545;
    }}
    QPushButton:pressed {{
        background-color: #D93636;
    }}
    """


def get_modal_button_size_style() -> str:
    return f"min-height: {MODAL_BUTTON_MIN_HEIGHT}px; min-width: {MODAL_BUTTON_MIN_WIDTH}px;"


def center_dialog_on_parent_or_screen(dialog: QDialog, parent_widget: QWidget | None = None) -> None:
    dialog.adjustSize()

    target_widget = parent_widget
    if target_widget is None:
        target_widget = dialog.parentWidget()

    if target_widget is not None and target_widget.isVisible():
        target_center = target_widget.mapToGlobal(target_widget.rect().center())
    else:
        screen = dialog.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        target_center = screen.availableGeometry().center()

    dialog_x = int(target_center.x() - (dialog.width() / 2))
    dialog_y = int(target_center.y() - (dialog.height() / 2))
    dialog.move(dialog_x, dialog_y)
