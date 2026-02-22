"""
[overview]
프롬프트 에디터 위젯

[description]
중앙 패널의 프롬프트 에디터 위젯입니다.
- System Prompt (QPlainTextEdit, ~150px 높이)
- User Prompt (QPlainTextEdit, 가변 높이)
- 변수 감지 ({{variable}})
- 버전 타임라인
"""

import re
from typing import List, Dict, Optional, cast, Any

from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtGui import QKeyEvent, QTextDocument
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QSplitter,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
    QMessageBox,
    QLineEdit,
)

from src.gui.theme import (
    COLOR_SIDEBAR,
    COLOR_ACCENT,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_BACKGROUND,
)
from src.gui.widgets.modal_dialog_factory import (
    MODAL_BUTTON_MIN_HEIGHT,
    MODAL_BUTTON_MIN_WIDTH,
    MODAL_BUTTON_SPACING,
    MODAL_INPUT_MIN_HEIGHT,
    MODAL_MIN_WIDTH,
    center_dialog_on_parent_or_screen,
    get_modal_button_size_style,
    get_modal_error_button_style,
    get_modal_line_edit_style,
    get_modal_primary_button_style,
    get_modal_secondary_button_style,
    get_modal_subtitle_style,
    get_modal_text_area_style,
    get_modal_title_style,
    setup_modal_dialog,
)
from src.gui.widgets.prompt_highlighter import VariableSyntaxHighlighter


class PromptEditor(QWidget):
    """프롬프트 에디터 위젯"""

    _COL_VARIABLE = 0
    _COL_VALUE = 1
    _COL_SOURCE = 2
    _VARIABLE_NAME_PATTERN = r"[a-zA-Z0-9_-]+"
    _VALUE_PREVIEW_MAX_LENGTH = 80
    POPUP_MIN_WIDTH: int = MODAL_MIN_WIDTH
    POPUP_INPUT_MIN_HEIGHT: int = MODAL_INPUT_MIN_HEIGHT
    POPUP_BUTTON_MIN_HEIGHT: int = MODAL_BUTTON_MIN_HEIGHT
    POPUP_BUTTON_MIN_WIDTH: int = MODAL_BUTTON_MIN_WIDTH
    POPUP_BUTTON_SPACING: int = MODAL_BUTTON_SPACING

    # 시그널 정의
    prompt_changed = Signal(str)
    version_changed = Signal(str)
    save_clicked = Signal()
    new_version_clicked = Signal()
    rename_version_clicked = Signal()

    def __init__(self) -> None:
        """PromptEditor 초기화"""
        super().__init__()

        self._versions: List[Dict[str, str]] = []
        self._variable_values: Dict[str, str] = {}
        self._manual_variable_keys: set[str] = set()
        self._deleted_variable_keys: set[str] = set()
        self._highlighters: List[VariableSyntaxHighlighter] = []
        self._save_button: Optional[QPushButton] = None
        self._new_version_button: Optional[QPushButton] = None
        self._rename_version_button: Optional[QPushButton] = None
        self._add_variable_button: Optional[QPushButton] = None
        self._delete_variable_button: Optional[QPushButton] = None
        self._edit_variable_button: Optional[QPushButton] = None

        self._setup_ui()
        self._setup_variable_highlighting()
        self._connect_signals()

    def _setup_variable_highlighting(self) -> None:
        documents: List[QTextDocument] = [
            self._system_prompt_edit.document(),
            self._user_prompt_edit.document(),
        ]
        self._highlighters = [
            VariableSyntaxHighlighter(document) for document in documents
        ]

    def _setup_ui(self) -> None:
        """UI 설정"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 탭 위젯 (Editor, Variables)
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {COLOR_BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                padding: 10px 16px;
                margin-right: 4px;
                font-size: 10pt;
                font-weight: 500;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_ACCENT};
                border-bottom: 2px solid {COLOR_ACCENT};
            }}
            QTabBar::tab:hover {{
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

        # Editor 탭
        editor_widget = self._create_editor_tab()
        self._tab_widget.addTab(editor_widget, "Editor")

        variables_widget = self._create_variables_tab()
        self._tab_widget.addTab(variables_widget, "Variables")

        layout.addWidget(self._tab_widget)

        self.setLayout(layout)

    def _create_editor_tab(self) -> QWidget:
        """에디터 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 버전 타임라인 드롭다운
        version_toolbar = self._create_version_toolbar()
        layout.addWidget(version_toolbar)

        # 스플리터를 사용하여 System/User Prompt 영역 분할
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: {COLOR_BORDER};
                height: 1px;
            }}
        """)

        # System Prompt 섹션
        system_section = self._create_prompt_section(
            "SYSTEM PROMPT",
            "Instructions for the AI persona",
        )
        self._system_prompt_edit = cast(Any, getattr(system_section, "edit"))
        splitter.addWidget(system_section)

        # User Prompt 섹션
        user_section = self._create_prompt_section(
            "USER PROMPT",
            "The task to execute",
        )
        self._user_prompt_edit = cast(Any, getattr(user_section, "edit"))
        splitter.addWidget(user_section)

        # 스플리터 비율 설정 (System: 150px, User: 가변)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([150, 400])

        layout.addWidget(splitter)

        widget.setLayout(layout)
        return widget

    def _create_variables_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("Detected Variables")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 10pt; font-weight: bold;"
        )
        layout.addWidget(title)

        button_bar = QHBoxLayout()
        self._add_variable_button = QPushButton("변수 추가")
        self._delete_variable_button = QPushButton("변수 삭제")
        self._edit_variable_button = QPushButton("값 편집")
        for button in (
            self._add_variable_button,
            self._delete_variable_button,
            self._edit_variable_button,
        ):
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {COLOR_BUTTON_BG};
                    color: {COLOR_TEXT_PRIMARY};
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 10pt;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_BUTTON_HOVER};
                }}
                QPushButton:pressed {{
                    background-color: {COLOR_ACCENT};
                    color: white;
                }}
                """
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_variable_button.setEnabled(False)
        self._edit_variable_button.setEnabled(False)
        self._add_variable_button.clicked.connect(self._add_variable_row)
        self._delete_variable_button.clicked.connect(self._delete_selected_variable)
        self._edit_variable_button.clicked.connect(self._edit_selected_variable)

        button_bar.addWidget(self._add_variable_button)
        button_bar.addWidget(self._delete_variable_button)
        button_bar.addWidget(self._edit_variable_button)
        button_bar.addStretch()
        layout.addLayout(button_bar)

        self._variables_table = QTableWidget(0, 3)
        self._variables_table.setHorizontalHeaderLabels(["Variable", "Value", "Type"])
        self._variables_table.horizontalHeader().setSectionResizeMode(
            self._COL_VARIABLE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._variables_table.horizontalHeader().setSectionResizeMode(
            self._COL_VALUE,
            QHeaderView.ResizeMode.Stretch,
        )
        self._variables_table.horizontalHeader().setSectionResizeMode(
            self._COL_SOURCE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._variables_table.verticalHeader().setVisible(False)
        self._variables_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._variables_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self._variables_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._variables_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLOR_SIDEBAR};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                gridline-color: {COLOR_BORDER};
                font-size: 10pt;
            }}
            QHeaderView::section {{
                background-color: {COLOR_BORDER};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                padding: 6px;
            }}
            """
        )
        self._variables_table.itemChanged.connect(self._on_variable_item_changed)
        self._variables_table.itemSelectionChanged.connect(
            self._on_variable_selection_changed
        )
        self._variables_table.itemDoubleClicked.connect(
            self._on_variable_item_double_clicked
        )
        self._variables_table.installEventFilter(self)
        layout.addWidget(self._variables_table)

        widget.setLayout(layout)
        return widget

    def _on_variable_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != self._COL_VALUE:
            return
        key_item = self._variables_table.item(item.row(), self._COL_VARIABLE)
        if key_item is None:
            return
        self._variable_values[key_item.text()] = item.text()

    def _on_variable_selection_changed(self) -> None:
        selected_key = self._get_selected_variable_key()
        has_selection = selected_key is not None
        if self._delete_variable_button is not None:
            self._delete_variable_button.setEnabled(has_selection)
        if self._edit_variable_button is not None:
            self._edit_variable_button.setEnabled(has_selection)

    def _on_variable_item_double_clicked(self, item: QTableWidgetItem) -> None:
        if item.column() != self._COL_VALUE:
            return
        variable_key = self._get_item_variable_key(item.row())
        if variable_key is None:
            return
        self._open_variable_editor(variable_key)

    def _get_item_variable_key(self, row: int) -> Optional[str]:
        key_item = self._variables_table.item(row, self._COL_VARIABLE)
        if key_item is None:
            return None
        return key_item.text()

    def _get_selected_variable_key(self) -> Optional[str]:
        selected_items = self._variables_table.selectedItems()
        if not selected_items:
            return None
        return self._get_item_variable_key(selected_items[0].row())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self._variables_table and isinstance(event, QKeyEvent):
            if event.type() == QEvent.Type.KeyPress and event.key() in {
                Qt.Key.Key_Delete,
                Qt.Key.Key_Backspace,
            }:
                self._delete_selected_variable()
                return True

        return super().eventFilter(watched, event)

    def _select_variable_row(self, variable_key: str) -> None:
        for row in range(self._variables_table.rowCount()):
            if self._get_item_variable_key(row) == variable_key:
                self._variables_table.selectRow(row)
                return

    def _value_preview(self, value: str) -> str:
        sanitized_value = value.replace("\n", "\\n")
        if len(sanitized_value) <= self._VALUE_PREVIEW_MAX_LENGTH:
            return sanitized_value
        return sanitized_value[: self._VALUE_PREVIEW_MAX_LENGTH - 3] + "..."

    def _refresh_variables_panel(self) -> None:
        detected_variables = self.detect_variables()
        for variable in detected_variables:
            self._variable_values.setdefault(variable, "")

        detected_set = set(detected_variables)
        all_stored_keys = {
            variable
            for variable in self._variable_values
            if variable not in self._deleted_variable_keys
        }
        sorted_detected_variables = sorted(
            variable
            for variable in detected_variables
            if variable not in self._deleted_variable_keys
        )
        sorted_manual_variables = sorted(
            variable
            for variable in self._manual_variable_keys
            if variable not in detected_set
            and variable not in self._deleted_variable_keys
        )
        sorted_unused_variables = sorted(
            variable
            for variable in all_stored_keys
            if variable not in detected_set
            and variable not in self._manual_variable_keys
        )
        visible_variables = (
            sorted_detected_variables
            + sorted_manual_variables
            + sorted_unused_variables
        )
        current_selection = self._get_selected_variable_key()

        self._variables_table.blockSignals(True)
        self._variables_table.setRowCount(len(visible_variables))

        for row, variable in enumerate(visible_variables):
            key_item = QTableWidgetItem(variable)
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            value = self._variable_values.get(variable, "")
            value_item = QTableWidgetItem(self._value_preview(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setToolTip(value)

            source = "Detected"
            if variable in self._manual_variable_keys:
                source = "Manual"
            elif variable not in detected_set:
                source = "Unused"
            source_item = QTableWidgetItem(source)
            source_item.setFlags(source_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            self._variables_table.setItem(row, self._COL_VARIABLE, key_item)
            self._variables_table.setItem(row, self._COL_VALUE, value_item)
            self._variables_table.setItem(row, self._COL_SOURCE, source_item)

        self._variables_table.blockSignals(False)
        self._on_variable_selection_changed()
        if current_selection is not None:
            self._select_variable_row(current_selection)

    def _create_variable_popup(
        self,
        title: str,
        subtitle: str,
    ) -> tuple[QDialog, QVBoxLayout]:
        dialog = QDialog(self)
        card_layout = setup_modal_dialog(
            dialog,
            object_name="promptEditorPopup",
            min_width=self.POPUP_MIN_WIDTH,
        )

        title_label = QLabel(title)
        title_label.setStyleSheet(get_modal_title_style())
        card_layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(get_modal_subtitle_style())
        card_layout.addWidget(subtitle_label)
        return dialog, card_layout

    def _center_variable_popup(self, dialog: QDialog) -> None:
        QTimer.singleShot(
            0,
            lambda: center_dialog_on_parent_or_screen(dialog, self.window()),
        )

    def _add_dialog_buttons(
        self,
        layout: QVBoxLayout,
        on_cancel: Any,
        on_accept: Any,
        accept_label: str,
    ) -> None:
        button_bar = QHBoxLayout()
        button_bar.setSpacing(self.POPUP_BUTTON_SPACING)
        button_bar.addStretch()

        cancel_button = QPushButton("취소")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet(
            f"{get_modal_secondary_button_style()}\n{get_modal_button_size_style()}"
        )
        cancel_button.setMinimumHeight(self.POPUP_BUTTON_MIN_HEIGHT)
        cancel_button.setMinimumWidth(self.POPUP_BUTTON_MIN_WIDTH)
        cancel_button.clicked.connect(on_cancel)
        button_bar.addWidget(cancel_button)

        accept_button = QPushButton(accept_label)
        accept_button.setCursor(Qt.CursorShape.PointingHandCursor)
        accept_button.setStyleSheet(
            f"{get_modal_primary_button_style()}\n{get_modal_button_size_style()}"
        )
        accept_button.setMinimumHeight(self.POPUP_BUTTON_MIN_HEIGHT)
        accept_button.setMinimumWidth(self.POPUP_BUTTON_MIN_WIDTH)
        accept_button.clicked.connect(on_accept)
        button_bar.addWidget(accept_button)

        layout.addLayout(button_bar)

    def _prompt_variable_name(self) -> Optional[str]:
        dialog, layout = self._create_variable_popup(
            title="변수 추가",
            subtitle="영문, 숫자, 밑줄(_), 하이픈(-)만 허용됩니다.",
        )

        name_input = QLineEdit()
        name_input.setPlaceholderText("변수명(영문/숫자/_/-)")
        name_input.setMinimumHeight(self.POPUP_INPUT_MIN_HEIGHT)
        name_input.setFocus()
        name_input.setStyleSheet(get_modal_line_edit_style())
        layout.addWidget(name_input)

        confirm: Dict[str, object] = {}

        def accept_with_value() -> None:
            confirm["value"] = name_input.text().strip()
            dialog.accept()

        name_input.returnPressed.connect(accept_with_value)

        self._add_dialog_buttons(
            layout,
            on_cancel=dialog.reject,
            on_accept=accept_with_value,
            accept_label="추가",
        )

        self._center_variable_popup(dialog)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        value = confirm.get("value")
        if not isinstance(value, str) or not value.strip():
            return None
        return value.strip()

    def _confirm_delete_variable(self, variable_key: str) -> bool:
        dialog, layout = self._create_variable_popup(
            title="변수 삭제",
            subtitle=f"변수 '{variable_key}'를 삭제하시겠어요?\n삭제된 값은 복구할 수 없습니다.",
        )

        confirm: Dict[str, bool] = {"value": False}

        def on_cancel() -> None:
            confirm["value"] = False
            dialog.reject()

        def on_delete() -> None:
            confirm["value"] = True
            dialog.accept()

        button_bar = QHBoxLayout()
        button_bar.setSpacing(self.POPUP_BUTTON_SPACING)
        button_bar.addStretch()

        cancel_button = QPushButton("취소")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.setStyleSheet(
            f"{get_modal_secondary_button_style()}\n{get_modal_button_size_style()}"
        )
        cancel_button.setMinimumHeight(self.POPUP_BUTTON_MIN_HEIGHT)
        cancel_button.setMinimumWidth(self.POPUP_BUTTON_MIN_WIDTH)
        cancel_button.clicked.connect(on_cancel)
        button_bar.addWidget(cancel_button)

        delete_button = QPushButton("삭제")
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.setStyleSheet(
            f"{get_modal_error_button_style()}\n{get_modal_button_size_style()}"
        )
        delete_button.setMinimumHeight(self.POPUP_BUTTON_MIN_HEIGHT)
        delete_button.setMinimumWidth(self.POPUP_BUTTON_MIN_WIDTH)
        delete_button.clicked.connect(on_delete)
        button_bar.addWidget(delete_button)

        layout.addLayout(button_bar)

        self._center_variable_popup(dialog)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        return bool(confirm.get("value"))

    def _add_variable_row(self) -> None:
        variable_name = self._prompt_variable_name()
        if variable_name is None:
            return
        if not re.fullmatch(self._VARIABLE_NAME_PATTERN, variable_name):
            QMessageBox.warning(
                self,
                "입력 확인",
                "변수명은 영문, 숫자, 밑줄(_), 하이픈(-)만 허용합니다.",
            )
            return
        self._deleted_variable_keys.discard(variable_name)
        self._manual_variable_keys.add(variable_name)
        self._variable_values.setdefault(variable_name, "")
        self._refresh_variables_panel()
        self._select_variable_row(variable_name)
        self._open_variable_editor(variable_name)

    def _delete_selected_variable(self) -> None:
        selected_key = self._get_selected_variable_key()
        if selected_key is None:
            return
        if not self._confirm_delete_variable(selected_key):
            return
        self._deleted_variable_keys.add(selected_key)
        self._manual_variable_keys.discard(selected_key)
        self._refresh_variables_panel()

    def _edit_selected_variable(self) -> None:
        selected_key = self._get_selected_variable_key()
        if selected_key is None:
            return
        self._open_variable_editor(selected_key)

    def _open_variable_editor(self, variable_key: str) -> None:
        dialog, layout = self._create_variable_popup(
            title=f"변수 값 편집 - {variable_key}",
            subtitle="값을 입력한 뒤 저장을 눌러 반영하세요.",
        )

        editor = QPlainTextEdit()
        editor.setMinimumHeight(180)
        editor.setPlainText(self._variable_values.get(variable_key, ""))
        editor.setStyleSheet(get_modal_text_area_style())

        layout.addWidget(editor)

        def on_accept() -> None:
            dialog.accept()

        self._add_dialog_buttons(
            layout,
            on_cancel=dialog.reject,
            on_accept=on_accept,
            accept_label="저장",
        )

        self._center_variable_popup(dialog)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        self._variable_values[variable_key] = editor.toPlainText()
        self._manual_variable_keys.add(variable_key)
        self._deleted_variable_keys.discard(variable_key)
        self._refresh_variables_panel()

    def set_variable_value(self, variable_key: str, value: str) -> None:
        self._variable_values[variable_key] = value
        self._manual_variable_keys.add(variable_key)
        self._deleted_variable_keys.discard(variable_key)
        self._refresh_variables_panel()

    def get_variable_values(self) -> Dict[str, str]:
        self._refresh_variables_panel()
        return {
            key: value
            for key, value in self._variable_values.items()
            if key not in self._deleted_variable_keys
        }

    def _create_version_toolbar(self) -> QWidget:
        """버전 타임라인 툴바 생성

        Returns:
            QWidget: 버전 툴바 위젯
        """
        widget = QWidget()
        widget.setStyleSheet(
            f"background-color: {COLOR_SIDEBAR}; border-bottom: 1px solid {COLOR_BORDER};"
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        version_label = QLabel("Version")
        version_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10pt;")
        layout.addWidget(version_label)

        self._version_selector = QComboBox()
        self._version_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10pt;
                min-width: 140px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLOR_SIDEBAR};
                selection-background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        layout.addWidget(self._version_selector)

        button_stylesheet = f"""
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10pt;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ACCENT};
                color: white;
            }}
        """

        self._save_button = QPushButton("Save")
        self._save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_button.setStyleSheet(button_stylesheet)
        self._save_button.clicked.connect(self.save_clicked.emit)
        layout.addWidget(self._save_button)

        self._new_version_button = QPushButton("New Version")
        self._new_version_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_version_button.setStyleSheet(button_stylesheet)
        self._new_version_button.clicked.connect(self.new_version_clicked.emit)
        layout.addWidget(self._new_version_button)

        self._rename_version_button = QPushButton("Rename Version")
        self._rename_version_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rename_version_button.setStyleSheet(button_stylesheet)
        self._rename_version_button.clicked.connect(self.rename_version_clicked.emit)
        layout.addWidget(self._rename_version_button)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_prompt_section(self, title: str, subtitle: str) -> QWidget:
        """프롬프트 섹션 생성

        Args:
            title: 섹션 제목
            subtitle: 섹션 부제목

        Returns:
            QWidget: 프롬프트 섹션 컨테이너 (내부에 edit 속성 포함)
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더
        header = QLabel(f"{title}")
        header.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                padding: 12px 16px 8px 16px;
                font-size: 9pt;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
        """)
        layout.addWidget(header)

        # 에디터
        edit = QPlainTextEdit()
        edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                padding: 0px 16px 16px 16px;
                font-family: 'Consolas', 'Menlo', 'Monaco', monospace;
                font-size: 11pt;
                line-height: 1.5;
            }}
            QPlainTextEdit:focus {{
                background-color: transparent;
            }}
        """)
        edit.setPlaceholderText(subtitle)

        layout.addWidget(edit)

        container.setLayout(layout)
        setattr(container, "edit", edit)
        return container

    def _on_version_changed(self, _text: str) -> None:
        data = self._version_selector.currentData()
        if data is None:
            self.version_changed.emit("")
            return
        if not isinstance(data, str):
            return

        self.version_changed.emit(data)

    def _connect_signals(self) -> None:
        """시그널 연결"""
        self._system_prompt_edit.textChanged.connect(
            lambda: self.prompt_changed.emit("system")
        )
        self._system_prompt_edit.textChanged.connect(self._refresh_variables_panel)
        self._user_prompt_edit.textChanged.connect(
            lambda: self.prompt_changed.emit("user")
        )
        self._user_prompt_edit.textChanged.connect(self._refresh_variables_panel)
        self._version_selector.currentTextChanged.connect(self._on_version_changed)
        self._refresh_variables_panel()

    def set_prompts_silently(self, system_prompt: str, user_prompt: str) -> None:
        self._system_prompt_edit.blockSignals(True)
        self._user_prompt_edit.blockSignals(True)
        try:
            self._system_prompt_edit.setPlainText(system_prompt)
            self._user_prompt_edit.setPlainText(user_prompt)
        finally:
            self._system_prompt_edit.blockSignals(False)
            self._user_prompt_edit.blockSignals(False)
        self._refresh_variables_panel()

    def clear_prompts_silently(self) -> None:
        self.set_prompts_silently("", "")

    def set_editors_read_only(self, read_only: bool) -> None:
        self._system_prompt_edit.setReadOnly(read_only)
        self._user_prompt_edit.setReadOnly(read_only)

    def set_toolbar_buttons_enabled(
        self,
        save_enabled: bool,
        new_version_enabled: bool,
        rename_version_enabled: bool,
    ) -> None:
        if self._save_button is not None:
            self._save_button.setEnabled(save_enabled)
        if self._new_version_button is not None:
            self._new_version_button.setEnabled(new_version_enabled)
        if self._rename_version_button is not None:
            self._rename_version_button.setEnabled(rename_version_enabled)

    def detect_variables(self) -> List[str]:
        source_text = "\n".join(
            [
                self._system_prompt_edit.toPlainText(),
                self._user_prompt_edit.toPlainText(),
            ]
        )

        # {{variable}} 패턴 매칭 (중첩 제외)
        pattern = r"\{\{([a-zA-Z0-9_-]+)\}\}"
        matches = re.findall(pattern, source_text)

        # 중복 제거
        unique_variables = list(set(matches))

        return unique_variables

    def get_system_prompt(self) -> str:
        return self._system_prompt_edit.toPlainText()

    def get_user_prompt(self) -> str:
        return self._user_prompt_edit.toPlainText()

    def set_system_prompt(self, text: str) -> None:
        self._system_prompt_edit.setPlainText(text)

    def set_user_prompt(self, text: str) -> None:
        self._user_prompt_edit.setPlainText(text)

    def clear_prompts(self) -> None:
        self._system_prompt_edit.clear()
        self._user_prompt_edit.clear()
        self._variable_values.clear()
        self._refresh_variables_panel()

    def add_version(self, version: str, description: str) -> None:
        self._versions.append(
            {
                "version": version,
                "description": description,
                "system_prompt": self.get_system_prompt(),
                "user_prompt": self.get_user_prompt(),
            }
        )

        # 버전 드롭다운에 추가
        self._version_selector.addItem(f"v{version}", version)

    def get_versions(self) -> List[Dict[str, str]]:
        return self._versions

    def load_version(self, version: str) -> bool:
        for v in self._versions:
            if v["version"] == version:
                self.set_system_prompt(v["system_prompt"])
                self.set_user_prompt(v["user_prompt"])
                return True
        return False
