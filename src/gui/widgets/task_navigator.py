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

from typing import Any, Optional

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QMenu,
    QPushButton,
    QStyle,
    QStyleOptionViewItem,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
)

from src.gui.theme import (
    COLOR_SIDEBAR,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_PRESSED,
    COLOR_ACCENT_SOFT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_ON_ACCENT,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_SURFACE_HOVER,
)

TASK_ITEM_SEARCH_TEXT_ROLE: int = int(Qt.ItemDataRole.UserRole) + 1
TASK_ITEM_META_TEXT_ROLE: int = int(Qt.ItemDataRole.UserRole) + 2
TASK_ITEM_VERSION_ROLE: int = int(Qt.ItemDataRole.UserRole) + 3
TASK_ITEM_DESCRIPTION_ROLE: int = int(Qt.ItemDataRole.UserRole) + 4
TASK_ITEM_TITLE_FONT_SIZE_PT: int = 10
TASK_ITEM_META_FONT_SIZE_PT: int = 9
TASK_ITEM_TEXT_LINE_GAP_PX: int = 2
TASK_ITEM_LIST_PADDING_X_PX: int = 12
TASK_ITEM_LIST_PADDING_Y_PX: int = 8
TASK_ITEM_TITLE_FONT_WEIGHT: QFont.Weight = QFont.Weight.DemiBold
TASK_ITEM_META_FONT_WEIGHT: QFont.Weight = QFont.Weight.Normal

ACTION_BUTTON_BORDER_STYLE_NONE: str = "none"
ACTION_BUTTON_DISABLED_BORDER_COLOR: str = COLOR_INPUT_BORDER


class _TaskItemDelegate(QStyledItemDelegate):
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        style = opt.widget.style() if opt.widget is not None else QApplication.style()
        selected = bool(opt.state & QStyle.StateFlag.State_Selected)

        opt.text = ""
        style.drawControl(
            QStyle.ControlElement.CE_ItemViewItem, opt, painter, opt.widget
        )

        title_text = str(index.data(Qt.ItemDataRole.DisplayRole) or "")
        meta_text = str(index.data(TASK_ITEM_META_TEXT_ROLE) or "")

        title_color = COLOR_ACCENT if selected else COLOR_TEXT_PRIMARY
        meta_color = COLOR_TEXT_PRIMARY if selected else COLOR_TEXT_SECONDARY

        title_font = QFont(opt.font)
        title_font.setPointSize(TASK_ITEM_TITLE_FONT_SIZE_PT)
        title_font.setWeight(TASK_ITEM_TITLE_FONT_WEIGHT)
        meta_font = QFont(opt.font)
        meta_font.setPointSize(TASK_ITEM_META_FONT_SIZE_PT)
        meta_font.setWeight(TASK_ITEM_META_FONT_WEIGHT)

        title_metrics = QFontMetrics(title_font)
        meta_metrics = QFontMetrics(meta_font)

        text_rect = style.subElementRect(
            QStyle.SubElement.SE_ItemViewItemText,
            opt,
            opt.widget,
        )

        total_text_height = (
            title_metrics.height() + TASK_ITEM_TEXT_LINE_GAP_PX + meta_metrics.height()
        )
        start_y = text_rect.top()
        if text_rect.height() > total_text_height:
            start_y = text_rect.top() + int(
                (text_rect.height() - total_text_height) / 2
            )

        title_rect = text_rect.adjusted(0, 0, 0, 0)
        title_rect.setTop(start_y)
        title_rect.setHeight(title_metrics.height())
        meta_rect = text_rect.adjusted(0, 0, 0, 0)
        meta_rect.setTop(start_y + title_metrics.height() + TASK_ITEM_TEXT_LINE_GAP_PX)
        meta_rect.setHeight(meta_metrics.height())

        painter.save()

        painter.setFont(title_font)
        painter.setPen(QColor(title_color))
        title_draw_text = title_metrics.elidedText(
            title_text, Qt.TextElideMode.ElideRight, title_rect.width()
        )
        painter.drawText(
            title_rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title_draw_text,
        )

        painter.setFont(meta_font)
        painter.setPen(QColor(meta_color))
        meta_draw_text = meta_metrics.elidedText(
            meta_text, Qt.TextElideMode.ElideRight, meta_rect.width()
        )
        painter.drawText(
            meta_rect,
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            meta_draw_text,
        )

        painter.restore()

    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> QSize:
        base_font = option.font
        title_font = QFont(base_font)
        title_font.setPointSize(TASK_ITEM_TITLE_FONT_SIZE_PT)
        title_font.setWeight(TASK_ITEM_TITLE_FONT_WEIGHT)
        meta_font = QFont(base_font)
        meta_font.setPointSize(TASK_ITEM_META_FONT_SIZE_PT)
        meta_font.setWeight(TASK_ITEM_META_FONT_WEIGHT)

        title_height = QFontMetrics(title_font).height()
        meta_height = QFontMetrics(meta_font).height()
        height = (
            (TASK_ITEM_LIST_PADDING_Y_PX * 2)
            + title_height
            + TASK_ITEM_TEXT_LINE_GAP_PX
            + meta_height
        )
        return QSize(0, height)


class TaskNavigator(QWidget):
    """태스크 네비게이터 위젯"""

    # 시그널 정의
    new_task_clicked = Signal()
    task_selected = Signal(str)
    task_rename_requested = Signal(str)
    task_delete_requested = Signal(str)

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

        def build_action_button_stylesheet(
            *,
            background_color: str,
            hover_color: str,
            pressed_color: str,
            text_color: str,
            border_style: str = ACTION_BUTTON_BORDER_STYLE_NONE,
        ) -> str:
            return f"""
                QPushButton {{
                    background-color: {background_color};
                    color: {text_color};
                    border: {border_style};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 10pt;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                    color: {COLOR_TEXT_ON_ACCENT};
                }}
                QPushButton:disabled {{
                    background-color: {COLOR_BUTTON_BG};
                    color: {COLOR_TEXT_SECONDARY};
                    border: 1px solid {ACTION_BUTTON_DISABLED_BORDER_COLOR};
                }}
            """

        new_task_button_stylesheet = build_action_button_stylesheet(
            background_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            pressed_color=COLOR_ACCENT_PRESSED,
            text_color=COLOR_TEXT_ON_ACCENT,
        )
        rename_task_button_stylesheet = build_action_button_stylesheet(
            background_color=COLOR_BUTTON_BG,
            hover_color=COLOR_BUTTON_HOVER,
            pressed_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_PRIMARY,
            border_style=f"1px solid {COLOR_INPUT_BORDER}",
        )
        delete_task_button_stylesheet = build_action_button_stylesheet(
            background_color=COLOR_BUTTON_BG,
            hover_color=COLOR_BUTTON_HOVER,
            pressed_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_PRIMARY,
            border_style=f"1px solid {COLOR_INPUT_BORDER}",
        )

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)

        self._new_task_button = QPushButton("New Task")
        self._new_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._new_task_button.setStyleSheet(new_task_button_stylesheet)
        action_row.addWidget(self._new_task_button, 1)

        self._rename_task_button = QPushButton("Rename")
        self._rename_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rename_task_button.setStyleSheet(rename_task_button_stylesheet)
        self._rename_task_button.setEnabled(False)
        action_row.addWidget(self._rename_task_button)

        self._delete_task_button = QPushButton("Delete")
        self._delete_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._delete_task_button.setStyleSheet(delete_task_button_stylesheet)
        self._delete_task_button.setEnabled(False)
        action_row.addWidget(self._delete_task_button)

        header_layout.addLayout(action_row)

        layout.addLayout(header_layout)

        # 태스크 리스트
        self._task_list = QListWidget()
        self._task_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._task_list.setItemDelegate(_TaskItemDelegate(self._task_list))
        self._task_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLOR_SIDEBAR};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: {TASK_ITEM_LIST_PADDING_Y_PX}px {TASK_ITEM_LIST_PADDING_X_PX}px;
                margin: 2px 8px;
                border-radius: 6px;
                border: none;
            }}
            QListWidget::item:selected {{
                background-color: {COLOR_ACCENT_SOFT};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLOR_SURFACE_HOVER};
            }}
        """)
        layout.addWidget(self._task_list)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """시그널 연결"""
        self._new_task_button.clicked.connect(self.new_task_clicked.emit)
        self._rename_task_button.clicked.connect(self._request_rename_selected)
        self._delete_task_button.clicked.connect(self._request_delete_selected)
        self._task_list.currentRowChanged.connect(self._on_row_changed)
        self._task_list.customContextMenuRequested.connect(self._on_context_menu)
        self._search_bar.textChanged.connect(self._on_search_changed)

    def _request_rename_selected(self) -> None:
        self._request_action_for_selected(self.task_rename_requested)

    def _request_delete_selected(self) -> None:
        self._request_action_for_selected(self.task_delete_requested)

    def _request_action_for_selected(self, signal: Any) -> None:
        task_id = self.get_selected_task_id()
        if task_id is None:
            return
        signal.emit(task_id)

    def _on_context_menu(self, pos: QPoint) -> None:
        item = self._task_list.itemAt(pos)
        if item is None:
            return

        self._task_list.setCurrentItem(item)
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(task_id, str) or not task_id:
            return

        menu = QMenu(self)
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        selected = menu.exec(self._task_list.mapToGlobal(pos))
        if selected == rename_action:
            self._emit_task_action(task_id, self.task_rename_requested)
        elif selected == delete_action:
            self._emit_task_action(task_id, self.task_delete_requested)

    def _emit_task_action(self, task_id: str, signal: Any) -> None:
        signal.emit(task_id)

    def _on_row_changed(self, row: int) -> None:
        """행 변경 핸들러"""
        has_selection = row >= 0
        self._rename_task_button.setEnabled(has_selection)
        self._delete_task_button.setEnabled(has_selection)
        if row >= 0:
            item = self._task_list.item(row)
            if item:
                task_id = item.data(Qt.ItemDataRole.UserRole)
                if task_id:
                    self.task_selected.emit(task_id)

    def _on_search_changed(self, text: str) -> None:
        """검색어 변경 핸들러"""
        search_text = text.lower()
        for i in range(self._task_list.count()):
            item = self._task_list.item(i)
            searchable_text = str(item.data(TASK_ITEM_SEARCH_TEXT_ROLE) or "").lower()
            item.setHidden(search_text not in searchable_text)

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

        meta_text = f"v{version}" if not description else f"v{version} • {description}"
        searchable_text = " ".join([name, version, description or ""]).strip()

        item.setText(name)
        item.setData(Qt.ItemDataRole.UserRole, task_id)
        item.setData(TASK_ITEM_SEARCH_TEXT_ROLE, searchable_text)
        item.setData(TASK_ITEM_META_TEXT_ROLE, meta_text)
        item.setData(TASK_ITEM_VERSION_ROLE, version)
        item.setData(TASK_ITEM_DESCRIPTION_ROLE, description)
        self._task_list.addItem(item)

        return task_id

    def clear_tasks(self) -> None:
        """모든 태스크 삭제"""
        self._task_list.clear()
        self._rename_task_button.setEnabled(False)
        self._delete_task_button.setEnabled(False)

    def update_task_name(self, task_id: str, new_name: str) -> bool:
        for i in range(self._task_list.count()):
            item = self._task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) != task_id:
                continue

            version = str(item.data(TASK_ITEM_VERSION_ROLE) or "")
            description = item.data(TASK_ITEM_DESCRIPTION_ROLE)
            description_text = "" if description is None else str(description)

            searchable_text = " ".join([new_name, version, description_text]).strip()
            item.setText(new_name)
            item.setData(TASK_ITEM_SEARCH_TEXT_ROLE, searchable_text)
            return True
        return False

    def remove_task(self, task_id: str) -> bool:
        for i in range(self._task_list.count()):
            item = self._task_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                self._task_list.takeItem(i)
                return True
        return False

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
