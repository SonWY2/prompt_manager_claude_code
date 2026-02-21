"""
[overview]
태스크 네비게이터 위젯

[description]
왼쪽 패널의 태스크 네비게이터 위젯입니다.
- 태스크 리스트 표시 (QListWidget)
- 검색 기능
- New Task 버튼
- 태스크 선택 강조
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
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
)


class TaskNavigator(QWidget):
    """태스크 네비게이터 위젯"""

    # 시그널 정의
    new_task_clicked = Signal()
    task_selected = Signal(str)

    def __init__(self) -> None:
        """TaskNavigator 초기화"""
        super().__init__()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """UI 설정"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 헤더 영역 (Search Bar + New Task Button)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(12, 12, 12, 8)
        header_layout.setSpacing(8)

        # 검색바
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search tasks...")
        self._search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {COLOR_ACCENT};
                background-color: {COLOR_INPUT_BG};
            }}
        """)
        header_layout.addWidget(self._search_bar)

        # New Task 버튼
        self._new_task_button = QPushButton()
        self._new_task_button.setText("New Task")
        self._new_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_task_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
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
        header_layout.addWidget(self._new_task_button)

        layout.addLayout(header_layout)

        # 태스크 리스트
        self._task_list = QListWidget()
        self._task_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._task_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLOR_SIDEBAR};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 10px 14px;
                margin: 2px 8px;
                border-radius: 6px;
                border: none;
                color: {COLOR_TEXT_SECONDARY};
            }}
            QListWidget::item:selected {{
                background-color: rgba(10, 132, 255, 0.15); /* Translucent Blue */
                color: {COLOR_ACCENT};
            }}
            QListWidget::item:hover:!selected {{
                background-color: rgba(255, 255, 255, 0.05);
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        layout.addWidget(self._task_list)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """시그널 연결"""
        self._new_task_button.clicked.connect(self.new_task_clicked.emit)
        self._task_list.itemClicked.connect(self._on_task_clicked)
        self._task_list.currentRowChanged.connect(self._on_row_changed)
        self._search_bar.textChanged.connect(self._on_search_changed)

    def _on_row_changed(self, row: int) -> None:
        """행 변경 핸들러"""
        if row >= 0:
            item = self._task_list.item(row)
            if item:
                task_id = item.data(Qt.ItemDataRole.UserRole)
                if task_id:
                    self.task_selected.emit(task_id)

    def _on_task_clicked(self, item: QListWidgetItem) -> None:
        """태스크 클릭 핸들러"""
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if task_id:
            self.task_selected.emit(task_id)

    def _on_search_changed(self, text: str) -> None:
        """검색어 변경 핸들러"""
        search_text = text.lower()
        for i in range(self._task_list.count()):
            item = self._task_list.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)

    def add_task(
        self,
        name: str,
        version: str,
        description: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> str:
        """태스크 추가

        Args:
            name: 태스크 이름
            version: 버전
            description: 설명 (선택 사항)

        Returns:
            str: 태스크 ID
        """
        if task_id is None:
            import uuid

            task_id = str(uuid.uuid4())

        item = QListWidgetItem()

        # 태스크 이름과 버전 표시
        item_text = f"{name}\nv{version}"
        if description:
            item_text += f" • {description}"

        item.setText(item_text)
        item.setData(Qt.ItemDataRole.UserRole, task_id)

        self._task_list.addItem(item)

        return task_id

    def clear_tasks(self) -> None:
        """모든 태스크 삭제"""
        self._task_list.clear()

    def get_selected_task_id(self) -> Optional[str]:
        """선택된 태스크 ID 반환

        Returns:
            Optional[str]: 선택된 태스크 ID, 없으면 None
        """
        current_item = self._task_list.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None

    def select_task(self, task_id: str) -> bool:
        """특정 태스크 선택

        Args:
            task_id: 선택할 태스크 ID

        Returns:
            bool: 선택 성공 여부
        """
        for i in range(self._task_list.count()):
            item = self._task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                self._task_list.setCurrentItem(item)
                return True
        return False

    def get_search_text(self) -> str:
        """검색바 텍스트 반환

        Returns:
            str: 검색바 텍스트
        """
        return self._search_bar.text()
