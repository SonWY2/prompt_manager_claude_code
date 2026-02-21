"""
[overview]
Provider List Panel 구현

[description]
좌측 Provider List Panel 위젯입니다. Provider 목록을 표시하고 관리합니다.
"""

from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMenu,
    QFrame,
)

from src.core.provider_manager import ProviderManager
from src.data.models import Provider
from src.gui.theme import (
    COLOR_SIDEBAR,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_ACCENT,
    COLOR_ACCENT_SOFT,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_SURFACE_HOVER,
    COLOR_STATUS_CONNECTED,
    COLOR_STATUS_ERROR,
    COLOR_STATUS_UNKNOWN,
)


class ProviderListPanel(QWidget):
    """
    [overview]
    Provider List Panel 위젯

    [description]
    등록된 Provider 목록을 표시하고 선택, 추가, 삭제 기능을 제공합니다.
    상태 표시등(연결 상태)을 시각적으로 표시합니다.
    """

    STATUS_COLOR_CONNECTED = COLOR_STATUS_CONNECTED
    STATUS_COLOR_ERROR = COLOR_STATUS_ERROR
    STATUS_COLOR_UNKNOWN = COLOR_STATUS_UNKNOWN

    provider_selected = Signal(str)
    add_provider_requested = Signal()
    provider_deleted = Signal(str)

    def __init__(
        self, provider_manager: ProviderManager, parent: Optional[QWidget] = None
    ):
        """
        ProviderListPanel 초기화

        Args:
            provider_manager: ProviderManager 인스턴스
            parent: 부분 위젯
        """
        super().__init__(parent)

        self.provider_manager = provider_manager
        self.current_provider_id: Optional[str] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(8)

        title_label = QLabel("Providers")
        title_label.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {COLOR_TEXT_PRIMARY};"
        )

        self.add_button = QPushButton("Add")
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setFixedWidth(60)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)

        layout.addLayout(header_layout)

        self.provider_list = QListWidget()
        self.provider_list.setFrameShape(QFrame.Shape.NoFrame)
        self.provider_list.setStyleSheet(f"""
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
                background-color: {COLOR_ACCENT_SOFT};
                color: {COLOR_ACCENT};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLOR_SURFACE_HOVER};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)

        layout.addWidget(self.provider_list)

    def _connect_signals(self):
        """시그널 연결"""
        self.provider_list.itemClicked.connect(self._on_provider_selected)
        self.add_button.clicked.connect(lambda: self.add_provider_requested.emit())
        self.provider_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.provider_list.customContextMenuRequested.connect(self._show_context_menu)

    def load_providers(self):
        """Provider 목록 로드"""
        self.provider_list.clear()

        providers = self.provider_manager.get_all_providers()

        for provider in providers:
            item = self._create_provider_item(provider)
            self.provider_list.addItem(item)

    def _create_provider_item(self, provider: Provider) -> QListWidgetItem:
        """
        Provider 아이템 생성

        Args:
            provider: Provider 데이터

        Returns:
            QListWidgetItem
        """
        item = QListWidgetItem()
        item.setText(provider.name)
        item.setData(Qt.ItemDataRole.UserRole, provider.id)
        item.setData(Qt.ItemDataRole.UserRole + 1, provider)
        item.setData(Qt.ItemDataRole.UserRole + 2, "unknown")

        return item

    def update_provider_status(self, provider_id: str, status: str):
        """
        Provider 연결 상태 업데이트

        Args:
            provider_id: Provider ID
            status: 연결 상태 ("connected", "error", "unknown")
        """
        for i in range(self.provider_list.count()):
            item = self.provider_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == provider_id:
                item.setData(Qt.ItemDataRole.UserRole + 2, status)

                # 아이템 텍스트에 상태 아이콘 추가
                status_icon = ""
                if status == "connected":
                    status_icon = "● "
                elif status == "error":
                    status_icon = "● "
                elif status == "unknown":
                    status_icon = "○ "

                provider_data = item.data(Qt.ItemDataRole.UserRole + 1)
                if provider_data:
                    item.setText(f"{status_icon}{provider_data.name}")
                break

    def _on_provider_selected(self, item: QListWidgetItem):
        """
        Provider 선택 이벤트 핸들러

        Args:
            item: 선택된 아이템
        """
        provider_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_provider_id = provider_id
        self.provider_selected.emit(provider_id)

    def _show_context_menu(self, position):
        """
        컨텍스트 메뉴 표시

        Args:
            position: 마우스 위치
        """
        item = self.provider_list.itemAt(position)
        if item is None:
            return

        provider_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)
        delete_action = menu.addAction("Delete")

        action = menu.exec_(self.provider_list.mapToGlobal(position))

        if action == delete_action:
            self._delete_provider(provider_id)

    def _delete_provider(self, provider_id: str):
        """
        Provider 삭제

        Args:
            provider_id: 삭제할 Provider ID
        """
        self.provider_deleted.emit(provider_id)

    def refresh_provider_list(self):
        """Provider 목록 새로고침"""
        self.load_providers()

    def select_provider(self, provider_id: str):
        """
        특정 Provider 선택

        Args:
            provider_id: 선택할 Provider ID
        """
        for i in range(self.provider_list.count()):
            item = self.provider_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == provider_id:
                self.provider_list.setCurrentItem(item)
                break
