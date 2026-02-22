"""
[overview]
공통 모달 다이얼로그 유틸리티

[description]
새 작업 다이얼로그와 변수 편집 다이얼로그에서 사용하는
프레임리스 카드형 모달의 공통 레이아웃 및 스타일을 제공합니다.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPoint, QSize, Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QGraphicsDropShadowEffect,
    QMessageBox,
    QInputDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
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


def center_dialog_on_parent_or_screen(
    dialog: QDialog, parent_widget: QWidget | None = None
) -> None:
    dialog.adjustSize()

    target_widget = parent_widget
    if target_widget is None:
        target_widget = dialog.parentWidget()

    target_center = None
    if (
        target_widget is not None
        and target_widget.width() > 0
        and target_widget.height() > 0
    ):
        mapped_center = target_widget.mapToGlobal(target_widget.rect().center())
        if target_widget.isWindow():
            frame_center = target_widget.frameGeometry().center()
            if mapped_center == QPoint(0, 0) and frame_center != QPoint(0, 0):
                target_center = frame_center
            elif frame_center != QPoint(0, 0):
                target_center = frame_center
            else:
                target_center = mapped_center
        else:
            target_center = mapped_center
    else:
        screen = dialog.screen() or QApplication.primaryScreen()
        if screen is None:
            return
        target_center = screen.availableGeometry().center()

    if target_center is None:
        return

    if hasattr(dialog, "size"):
        dialog_size = dialog.size()
    elif hasattr(dialog, "width") and hasattr(dialog, "height"):
        dialog_size = QSize(dialog.width(), dialog.height())
    else:
        dialog_size = QSize()

    dialog_x = int(target_center.x() - (dialog_size.width() / 2))
    dialog_y = int(target_center.y() - (dialog_size.height() / 2))
    dialog.move(dialog_x, dialog_y)


class CenteredDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        anchor: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._center_anchor = anchor

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        center_dialog_on_parent_or_screen(self, self._center_anchor)
        QTimer.singleShot(
            0, lambda: center_dialog_on_parent_or_screen(self, self._center_anchor)
        )


class CenteredMessageBox(QMessageBox):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        anchor: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._center_anchor = anchor

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        center_dialog_on_parent_or_screen(self, self._center_anchor)
        QTimer.singleShot(
            0, lambda: center_dialog_on_parent_or_screen(self, self._center_anchor)
        )


class CenteredInputDialog(QInputDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        anchor: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._center_anchor = anchor

    def showEvent(self, event: Any) -> None:
        super().showEvent(event)
        center_dialog_on_parent_or_screen(self, self._center_anchor)
        QTimer.singleShot(
            0, lambda: center_dialog_on_parent_or_screen(self, self._center_anchor)
        )


# ============================================================================
# Simple Dialog Pattern - 테스트 가능한 Static Method
# ============================================================================

from typing import Any, Callable, Optional


class SimpleDialog:
    """
    [overview]
    단순 message/input dialog를 위한 테스트 가능한 static factory

    [description]
    커스텀 스타일링과 중앙 정렬이 적용된 message/input dialog를 제공합니다.
    static method는 테스트에서 patch 가능합니다.

    Usage:
        # Message dialog
        result = SimpleDialog.show_message("Title", "Message content")

        # Input dialog
        result = SimpleDialog.show_input("Title", "Enter value:", default="default")
        if result is not None:
            print(f"Input: {result}")
    """

    @staticmethod
    def show_message(
        title: str,
        message: str,
        parent: QWidget | None = None,
        *,
        button_text: str = "OK",
        is_error: bool = False,
    ) -> bool:
        """
        메시지 다이얼로그를 표시하고 닫힐 때까지 대기합니다.

        Args:
            title: 다이얼로그 제목
            message: 표시할 메시지
            parent: 부모 위젯
            button_text: 버튼 텍스트
            is_error: 에러 스타일 적용 여부

        Returns:
            사용자가 OK를 누르면 True, 그렇지 않으면 False

        Test mocking:
            with patch.object(SimpleDialog, 'show_message', return_value=True):
                # 테스트 코드
                ...
        """
        dialog = _SimpleStyledMessageDialog(
            title, message, parent, button_text, is_error
        )
        return dialog.exec() == QDialog.DialogCode.Accepted

    @staticmethod
    def show_input(
        title: str,
        label: str,
        parent: QWidget | None = None,
        *,
        default: str = "",
        placeholder: str = "",
        is_password: bool = False,
        validator: Optional[Callable[[str], bool]] = None,
    ) -> Optional[str]:
        """
        입력 다이얼로그를 표시하고 닫힐 때까지 대기합니다.

        Args:
            title: 다이얼로그 제목
            label: 입력 필드 라벨
            parent: 부모 위젯
            default: 기본값
            placeholder: 플레이스홀더 텍스트
            is_password: 비밀번호 입력 여부
            validator: 입력 유효성 검사 함수 (return True if valid)

        Returns:
            사용자가 입력한 값, 취소 시 None

        Test mocking:
            with patch.object(SimpleDialog, 'show_input', return_value='test'):
                # 테스트 코드
                ...
        """
        dialog = _SimpleStyledInputDialog(
            title, label, parent, default, placeholder, is_password, validator
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_input_value()
        return None


class _SimpleStyledDialogBase(QDialog):
    """
    [overview]
    단순 다이얼로그 베이스 클래스

    [description]
    중앙 정렬과 커스텀 스타일링이 적용된 다이얼로그 베이스
    """

    def __init__(self, title: str, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self) -> None:
        """UI 기본 구조 설정"""
        self._layout = setup_modal_dialog(self, object_name="simpleDialogCard")

    def _setup_content(self) -> None:
        """서브클래스에서 컨텐츠 구현"""
        raise NotImplementedError

    def showEvent(self, event: Any) -> None:
        """다이얼로그 표시 시 중앙 정렬"""
        super().showEvent(event)
        center_dialog_on_parent_or_screen(self)


class _SimpleStyledMessageDialog(_SimpleStyledDialogBase):
    """
    [overview]
    단순 메시지 다이얼로그

    [description]
    텍스트 메시지와 OK 버튼이 있는 다이얼로그
    """

    def __init__(
        self,
        title: str,
        message: str,
        parent: QWidget | None,
        button_text: str,
        is_error: bool,
    ) -> None:
        self._message = message
        self._button_text = button_text
        self._is_error = is_error
        super().__init__(title, parent)

    def _setup_content(self) -> None:
        """메시지 다이얼로그 컨텐츠 구성"""
        message_label = QLabel(self._message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(get_modal_subtitle_style())
        self._layout.addWidget(message_label)

        button_style = (
            get_modal_error_button_style()
            if self._is_error
            else get_modal_primary_button_style()
        )

        ok_button = QPushButton(self._button_text)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setMinimumHeight(MODAL_BUTTON_MIN_HEIGHT)
        ok_button.setMinimumWidth(MODAL_BUTTON_MIN_WIDTH)
        ok_button.setStyleSheet(f"{button_style}\n{get_modal_button_size_style()}")
        ok_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(MODAL_BUTTON_SPACING)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)

        self._layout.addLayout(button_layout)


class _SimpleStyledInputDialog(_SimpleStyledDialogBase):
    """
    [overview]
    단순 입력 다이얼로그

    [description]
    라벨과 입력 필드가 있는 다이얼로그
    """

    def __init__(
        self,
        title: str,
        label: str,
        parent: QWidget | None,
        default: str,
        placeholder: str,
        is_password: bool,
        validator: Optional[Callable[[str], bool]],
    ) -> None:
        self._label_text = label
        self._default_value = default
        self._placeholder = placeholder
        self._is_password = is_password
        self._validator = validator
        super().__init__(title, parent)

    def _setup_content(self) -> None:
        """입력 다이얼로그 컨텐츠 구성"""
        label_widget = QLabel(self._label_text)
        label_widget.setStyleSheet(get_modal_title_style())
        self._layout.addWidget(label_widget)

        self._input = QLineEdit()
        self._input.setText(self._default_value)
        self._input.setPlaceholderText(self._placeholder)
        self._input.setMinimumHeight(MODAL_INPUT_MIN_HEIGHT)
        self._input.setStyleSheet(get_modal_line_edit_style())

        if self._is_password:
            self._input.setEchoMode(QLineEdit.EchoMode.Password)

        self._input.textChanged.connect(self._update_button_state)
        self._input.returnPressed.connect(self._accept_if_valid)

        self._layout.addWidget(self._input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(MODAL_BUTTON_SPACING)
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setMinimumHeight(MODAL_BUTTON_MIN_HEIGHT)
        cancel_button.setMinimumWidth(MODAL_BUTTON_MIN_WIDTH)
        cancel_button.setStyleSheet(
            f"{get_modal_secondary_button_style()}\n{get_modal_button_size_style()}"
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._ok_button = QPushButton("OK")
        self._ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ok_button.setMinimumHeight(MODAL_BUTTON_MIN_HEIGHT)
        self._ok_button.setMinimumWidth(MODAL_BUTTON_MIN_WIDTH)
        self._ok_button.setStyleSheet(
            f"{get_modal_primary_button_style()}\n{get_modal_button_size_style()}"
        )
        self._ok_button.clicked.connect(self._accept_if_valid)
        button_layout.addWidget(self._ok_button)

        self._layout.addLayout(button_layout)

        self._update_button_state()
        self._input.setFocus()

    def _update_button_state(self) -> None:
        """OK 버튼 상태 업데이트"""
        if self._validator:
            self._ok_button.setEnabled(self._validator(self._input.text()))
        else:
            self._ok_button.setEnabled(bool(self._input.text().strip()))

    def _accept_if_valid(self) -> None:
        """유효성 검사 후 수락"""
        if self._validator:
            if self._validator(self._input.text()):
                self.accept()
        elif self._input.text().strip():
            self.accept()

    def get_input_value(self) -> str:
        """입력 값 반환"""
        return self._input.text().strip()
