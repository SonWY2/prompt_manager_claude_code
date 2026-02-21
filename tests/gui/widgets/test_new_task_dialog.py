"""
[overview]
NewTaskDialog 위젯 테스트

[description]
새 태스크 생성 다이얼로그의 입력/버튼 동작을 검증합니다.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QWidget

from src.gui.widgets.new_task_dialog import NewTaskDialog


class TestNewTaskDialog:
    def test_dialog_uses_frameless_window(self, qtbot):
        dialog = NewTaskDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        assert bool(dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)

    def test_create_button_disabled_when_input_empty(self, qtbot):
        dialog = NewTaskDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        assert not dialog._create_button.isEnabled()

    def test_accept_when_valid_task_name_entered(self, qtbot):
        dialog = NewTaskDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        dialog._name_input.setText("New Task Name")
        dialog._accept_if_valid()

        assert dialog.result() == QDialog.DialogCode.Accepted

    def test_task_name_is_trimmed(self, qtbot):
        dialog = NewTaskDialog()
        qtbot.addWidget(dialog)
        dialog.show()

        dialog._name_input.setText("  Task Name  ")

        assert dialog.task_name == "Task Name"

    def test_dialog_is_centered_on_parent(self, qtbot):
        parent = QWidget()
        parent.setGeometry(120, 120, 640, 480)
        qtbot.addWidget(parent)
        parent.show()

        dialog = NewTaskDialog(parent)
        qtbot.addWidget(dialog)
        dialog.resize(420, 220)
        dialog.show()
        qtbot.wait(30)

        parent_center = parent.mapToGlobal(parent.rect().center())
        dialog_center = dialog.mapToGlobal(dialog.rect().center())

        assert abs(parent_center.x() - dialog_center.x()) <= 140
        assert abs(parent_center.y() - dialog_center.y()) <= 180
