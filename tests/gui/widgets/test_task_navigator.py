"""
[overview]
TaskNavigator 위젯 테스트

[description]
태스크 네비게이터 위젯의 기능을 테스트합니다.
- 태스크 리스트 표시
- 검색 기능
- New Task 버튼
- 태스크 선택 강조
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget
from PySide6.QtTest import QTest

from src.gui.widgets.task_navigator import (
    TASK_ITEM_SEARCH_TEXT_ROLE,
    TASK_ITEM_META_TEXT_ROLE,
    TaskNavigator,
)


class TestTaskNavigator:
    """TaskNavigator 위젯 테스트"""

    def test_initialization(self, qtbot):
        """위젯 초기화 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 검색바 존재 확인
        assert widget._search_bar is not None
        assert widget._search_bar.placeholderText() == "Search tasks..."

        # New Task 버튼 존재 확인
        assert widget._new_task_button is not None
        assert "New Task" in widget._new_task_button.text()

        # 태스크 리스트 존재 확인
        assert widget._task_list is not None
        assert isinstance(widget._task_list, QListWidget)

    def test_add_task(self, qtbot):
        """태스크 추가 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 태스크 추가
        widget.add_task("Test Task", "1.0")

        # 태스크가 리스트에 추가되었는지 확인
        assert widget._task_list.count() == 1

        item = widget._task_list.item(0)
        assert item.text() == "Test Task"
        assert "Test Task" in str(item.data(TASK_ITEM_SEARCH_TEXT_ROLE))
        assert "1.0" in str(item.data(TASK_ITEM_SEARCH_TEXT_ROLE))

        assert item.data(TASK_ITEM_META_TEXT_ROLE) == "v1.0"

        assert widget._task_list.itemWidget(item) is None

    def test_task_title_and_meta_have_visual_variation(self, qtbot):
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        widget.add_task("Customer Support Bot", "1.0", "desc")
        item = widget._task_list.item(0)
        assert widget._task_list.itemWidget(item) is None
        assert item.text() == "Customer Support Bot"
        assert item.data(TASK_ITEM_META_TEXT_ROLE) == "v1.0 • desc"

    def test_search_functionality(self, qtbot):
        """검색 기능 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 여러 태스크 추가
        widget.add_task("Customer Support Bot", "1.0")
        widget.add_task("Python Code Refactor", "2.1")
        widget.add_task("Blog Post Generator", "1.0")

        # 검색어 입력
        QTest.keyClicks(widget._search_bar, "Python")

        # 검색바에 텍스트가 입력되었는지 확인
        assert widget._search_bar.text() == "Python"

    def test_task_selection_highlight(self, qtbot):
        """태스크 선택 강조 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 태스크 추가
        widget.add_task("Test Task", "1.0")

        # 첫 번째 아이템 선택
        item = widget._task_list.item(0)
        widget._task_list.setCurrentItem(item)

        # 선택된 아이템 확인
        assert widget._task_list.currentItem() == item
        assert widget._task_list.currentRow() == 0

    def test_clear_tasks(self, qtbot):
        """태스크 전체 삭제 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 태스크 추가
        widget.add_task("Task 1", "1.0")
        widget.add_task("Task 2", "1.0")
        assert widget._task_list.count() == 2

        # 전체 삭제
        widget.clear_tasks()
        assert widget._task_list.count() == 0

    def test_new_task_button_signal(self, qtbot):
        """New Task 버튼 시그널 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 시그널 캡처 준비
        signal_emitted = False

        def on_new_task():
            nonlocal signal_emitted
            signal_emitted = True

        widget.new_task_clicked.connect(on_new_task)

        # 버튼 클릭
        QTest.mouseClick(widget._new_task_button, Qt.MouseButton.LeftButton)

        # 시그널 발생 확인
        assert signal_emitted

    def test_task_selected_signal(self, qtbot):
        """태스크 선택 시그널 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 시그널 캡처 준비
        selected_task_id = None

        def on_task_selected(task_id: str):
            nonlocal selected_task_id
            selected_task_id = task_id

        widget.task_selected.connect(on_task_selected)

        # 태스크 추가
        task_id = widget.add_task("Test Task", "1.0")

        # 태스크 선택
        item = widget._task_list.item(0)
        widget._task_list.setCurrentItem(item)

        # 시그널 발생 확인
        assert selected_task_id == task_id

    def test_search_clear(self, qtbot):
        """검색창 초기화 테스트"""
        widget = TaskNavigator()
        qtbot.addWidget(widget)
        widget.show()

        # 검색어 입력
        QTest.keyClicks(widget._search_bar, "test")
        assert widget._search_bar.text() == "test"

        # 검색창 초기화
        widget._search_bar.clear()
        assert widget._search_bar.text() == ""
