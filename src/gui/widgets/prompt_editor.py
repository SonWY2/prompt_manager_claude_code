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
from typing import List, Dict, cast, Any

from PySide6.QtCore import Qt, Signal
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
)

from src.gui.theme import (
    COLOR_SIDEBAR,
    COLOR_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BORDER,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_BACKGROUND,
)


class PromptEditor(QWidget):
    """프롬프트 에디터 위젯"""

    # 시그널 정의
    prompt_changed = Signal(str)
    version_changed = Signal(str)
    new_version_clicked = Signal()

    def __init__(self) -> None:
        """PromptEditor 초기화"""
        super().__init__()

        self._versions: List[Dict[str, str]] = []
        self._variable_values: Dict[str, str] = {}

        self._setup_ui()
        self._connect_signals()

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

        self._variables_table = QTableWidget(0, 2)
        self._variables_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self._variables_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self._variables_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )
        self._variables_table.verticalHeader().setVisible(False)
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
        layout.addWidget(self._variables_table)

        widget.setLayout(layout)
        return widget

    def _on_variable_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != 1:
            return
        key_item = self._variables_table.item(item.row(), 0)
        if key_item is None:
            return
        self._variable_values[key_item.text()] = item.text()

    def _refresh_variables_panel(self) -> None:
        variables = sorted(self.detect_variables())
        valid_keys = set(variables)
        self._variable_values = {
            key: value
            for key, value in self._variable_values.items()
            if key in valid_keys
        }

        self._variables_table.blockSignals(True)
        self._variables_table.setRowCount(len(variables))

        for row, variable in enumerate(variables):
            key_item = QTableWidgetItem(variable)
            key_item.setFlags(key_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item = QTableWidgetItem(self._variable_values.get(variable, ""))
            self._variables_table.setItem(row, 0, key_item)
            self._variables_table.setItem(row, 1, value_item)

        self._variables_table.blockSignals(False)

    def get_variable_values(self) -> Dict[str, str]:
        self._refresh_variables_panel()
        return dict(self._variable_values)

    def _create_version_toolbar(self) -> QWidget:
        """버전 타임라인 툴바 생성

        Returns:
            QWidget: 버전 툴바 위젯
        """
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; border-bottom: 1px solid {COLOR_BORDER};")

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

        new_version_button = QPushButton("New Version")
        new_version_button.setCursor(Qt.CursorShape.PointingHandCursor)
        new_version_button.setStyleSheet(f"""
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
        """)
        new_version_button.clicked.connect(self.new_version_clicked.emit)
        layout.addWidget(new_version_button)

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

    def _on_version_changed(self, version: str) -> None:
        """버전 변경 핸들러

        Args:
            version: 선택된 버전
        """
        if version and version != "Current":
            self.load_version(version)
            self.version_changed.emit(version)

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

    def detect_variables(self) -> List[str]:
        """프롬프트에서 변수 감지

        Returns:
            List[str]: 감지된 변수 이름 목록
        """
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
        """System Prompt 반환

        Returns:
            str: System Prompt 텍스트
        """
        return self._system_prompt_edit.toPlainText()

    def get_user_prompt(self) -> str:
        """User Prompt 반환

        Returns:
            str: User Prompt 텍스트
        """
        return self._user_prompt_edit.toPlainText()

    def set_system_prompt(self, text: str) -> None:
        """System Prompt 설정

        Args:
            text: 설정할 System Prompt 텍스트
        """
        self._system_prompt_edit.setPlainText(text)

    def set_user_prompt(self, text: str) -> None:
        """User Prompt 설정

        Args:
            text: 설정할 User Prompt 텍스트
        """
        self._user_prompt_edit.setPlainText(text)

    def clear_prompts(self) -> None:
        """모든 프롬프트 초기화"""
        self._system_prompt_edit.clear()
        self._user_prompt_edit.clear()
        self._variable_values.clear()
        self._refresh_variables_panel()

    def add_version(self, version: str, description: str) -> None:
        """버전 추가

        Args:
            version: 버전 번호 (예: "1.0")
            description: 버전 설명
        """
        self._versions.append(
            {
                "version": version,
                "description": description,
                "system_prompt": self.get_system_prompt(),
                "user_prompt": self.get_user_prompt(),
            }
        )

        # 버전 드롭다운에 추가
        self._version_selector.addItem(f"v{version}")

    def get_versions(self) -> List[Dict[str, str]]:
        """버전 목록 반환

        Returns:
            List[Dict[str, str]]: 버전 목록
        """
        return self._versions

    def load_version(self, version: str) -> bool:
        """특정 버전 로드

        Args:
            version: 로드할 버전 번호

        Returns:
            bool: 로드 성공 여부
        """
        for v in self._versions:
            if v["version"] == version:
                self.set_system_prompt(v["system_prompt"])
                self.set_user_prompt(v["user_prompt"])
                return True
        return False
