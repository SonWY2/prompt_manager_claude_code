"""
[overview]
main_window.py 모듈 테스트

[description]
MainWindow 클래스의 3단 QSplitter 레이아웃과 Modern Dark Mode 테마 테스트
"""

from typing import cast

from src.data.models import Task, Prompt, Version
from PySide6.QtWidgets import QDialog, QMainWindow, QSplitter, QWidget
from PySide6.QtCore import Qt

from src.gui.theme import COLOR_ACCENT, COLOR_TEXT_PRIMARY


def _main_splitter(window: QMainWindow) -> QSplitter:
    return cast(QSplitter, window.centralWidget())


class TestMainWindowLayout:
    """MainWindow 레이아웃 테스트"""

    def test_main_window_creation(self, qtbot):
        """MainWindow가 생성되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        assert window is not None
        assert window.windowTitle() == "Prompt Manager[*]"

    def test_main_splitter_exists(self, qtbot):
        """메인 QSplitter가 존재하는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        central_widget = window.centralWidget()
        assert central_widget is not None
        assert isinstance(central_widget, QSplitter)

    def test_three_column_layout(self, qtbot):
        """3단 컬럼 레이아웃이 구성되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = _main_splitter(window)
        assert isinstance(main_splitter, QSplitter)
        assert main_splitter.count() == 3

        # 각 패널 확인
        for i in range(3):
            widget = main_splitter.widget(i)
            assert widget is not None
            assert isinstance(widget, QWidget)

    def test_splitter_orientation_horizontal(self, qtbot):
        """QSplitter가 가로 방향인지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = _main_splitter(window)
        assert main_splitter.orientation() == Qt.Orientation.Horizontal

    def test_window_minimum_size(self, qtbot):
        """윈도우 최소 크기가 설정되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert window.minimumWidth() > 0
        assert window.minimumHeight() > 0


class TestMainWindowTheme:
    """MainWindow Modern Dark Mode 테마 테스트"""

    def test_main_window_background_color(self, qtbot):
        """메인 윈도우 배경색이 Modern Dark Mode인지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 스타일시트에서 배경색 확인
        stylesheet = window.styleSheet()
        assert "background-color" in stylesheet or "#1E1E1E" in stylesheet

    def test_accent_color_applied(self, qtbot):
        """Accent 색상이 적용되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        stylesheet = window.styleSheet()
        assert COLOR_ACCENT in stylesheet

    def test_text_colors_set(self, qtbot):
        """텍스트 색상이 설정되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        stylesheet = window.styleSheet()
        assert COLOR_TEXT_PRIMARY in stylesheet


class TestMainWindowVersionBehavior:
    def test_version_selector_preserves_selected_data(self, qtbot, monkeypatch):
        from src.gui.main_window import (
            MainWindow,
            VERSION_SELECTOR_DATA_CURRENT,
            VERSION_SELECTOR_DATA_DB_PREFIX,
        )

        window = MainWindow()
        qtbot.addWidget(window)

        window._current_task_id = "task-1"

        prompt = Prompt(
            id="prompt-1",
            task_id="task-1",
            current_version_id=None,
            system_prompt="",
            user_prompt="",
        )
        versions = [
            Version(
                id="version-1",
                prompt_id="prompt-1",
                content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
                version_number=1,
                version_name=None,
            ),
            Version(
                id="version-2",
                prompt_id="prompt-1",
                content='{"schema_version": 1, "system_prompt": "new", "user_prompt": "new-user"}',
                version_number=2,
                version_name=None,
            ),
        ]

        monkeypatch.setattr(
            window._task_manager, "get_latest_task_prompt", lambda *_: prompt
        )
        monkeypatch.setattr(
            window._version_manager, "get_timeline", lambda *_: versions
        )

        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-2"
        window._refresh_version_selector()

        selector = window._prompt_editor._version_selector
        assert selector.currentData() == f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-2"

        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}missing"
        window._refresh_version_selector()
        assert selector.currentData() == VERSION_SELECTOR_DATA_CURRENT

    def test_selecting_version_does_not_auto_save(self, qtbot, monkeypatch):
        from src.gui.main_window import (
            MainWindow,
            VERSION_SELECTOR_DATA_DB_PREFIX,
        )

        window = MainWindow()
        qtbot.addWidget(window)

        save_calls = []
        monkeypatch.setattr(
            window,
            "_save_current_task_prompt",
            lambda: save_calls.append("saved"),
        )

        window._current_task_id = "task-1"
        version = Version(
            id="version-1",
            prompt_id="prompt-1",
            content='{"schema_version": 1, "system_prompt": "snap-system", "user_prompt": "snap-user"}',
            version_number=1,
            version_name=None,
        )
        monkeypatch.setattr(window._version_manager, "get_version", lambda _: version)

        window._on_version_changed(f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1")

        assert save_calls == []
        assert window.isWindowModified() is False
        assert window._save_action.isEnabled() is False
        assert window._prompt_editor.get_system_prompt() == "snap-system"
        assert window._prompt_editor.get_user_prompt() == "snap-user"

    def test_switching_to_current_clears_dirty_state(self, qtbot, monkeypatch):
        from src.gui.main_window import (
            MainWindow,
            VERSION_SELECTOR_DATA_CURRENT,
            VERSION_SELECTOR_DATA_DB_PREFIX,
        )

        window = MainWindow()
        qtbot.addWidget(window)

        window._current_task_id = "task-1"
        monkeypatch.setattr(
            window._task_manager,
            "get_latest_task_prompt",
            lambda *_: Prompt(
                id="prompt-1",
                task_id="task-1",
                current_version_id=None,
                system_prompt="base-system",
                user_prompt="base-user",
            ),
        )

        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"
        window.setWindowModified(True)
        window._set_save_enabled(True)

        window._on_version_changed(VERSION_SELECTOR_DATA_CURRENT)

        assert window.isWindowModified() is False
        assert window._save_action.isEnabled() is False
        assert window._prompt_editor.get_system_prompt() == "base-system"
        assert window._prompt_editor.get_user_prompt() == "base-user"
        assert window._selected_version_key == VERSION_SELECTOR_DATA_CURRENT

    def test_editing_version_does_not_switch_to_current(self, qtbot, monkeypatch):
        from src.gui.main_window import (
            MainWindow,
            VERSION_SELECTOR_DATA_CURRENT,
            VERSION_SELECTOR_DATA_DB_PREFIX,
        )

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"

        version = Version(
            id="version-1",
            prompt_id="prompt-1",
            content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
            version_number=1,
            version_name=None,
        )
        monkeypatch.setattr(window._version_manager, "get_version", lambda *_: version)

        selector = window._prompt_editor._version_selector
        selector.blockSignals(True)
        try:
            selector.clear()
            selector.addItem("Current", VERSION_SELECTOR_DATA_CURRENT)
            selector.addItem("v1", f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1")
        finally:
            selector.blockSignals(False)

        selector.setCurrentIndex(1)
        qtbot.wait(10)

        window._prompt_editor._user_prompt_edit.setPlainText("edited")
        qtbot.wait(10)

        assert selector.currentData() == f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"
        assert (
            window._selected_version_key
            == f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"
        )
        assert window._save_action.isEnabled() is True

    def test_new_version_created_with_empty_snapshot(self, qtbot, monkeypatch):
        from src.core.prompt_snapshot import serialize_prompt_snapshot
        from src.gui.main_window import (
            MainWindow,
            VERSION_SELECTOR_DATA_DB_PREFIX,
        )

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"

        prompt = Prompt(
            id="prompt-1",
            task_id="task-1",
            current_version_id=None,
            system_prompt="base-system",
            user_prompt="base-user",
        )
        monkeypatch.setattr(
            window._task_manager, "get_latest_task_prompt", lambda *_: prompt
        )

        captured: dict[str, str] = {}

        def fake_create_version(
            prompt_id: str, content: str, version_name: str | None = None
        ):
            captured["prompt_id"] = prompt_id
            captured["content"] = content
            captured["version_name"] = str(version_name)
            return Version(
                id="new-version",
                prompt_id=prompt_id,
                content=content,
                version_name=version_name,
                version_number=1,
            )

        monkeypatch.setattr(
            window._version_manager, "create_version", fake_create_version
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("", True),
        )
        monkeypatch.setattr(
            window._version_manager,
            "get_timeline",
            lambda *_: [
                Version(
                    id="new-version",
                    prompt_id="prompt-1",
                    content=serialize_prompt_snapshot("", ""),
                    version_number=1,
                    version_name=None,
                )
            ],
        )

        window._prompt_editor.set_prompts_silently("system", "user")
        window._on_new_version_clicked()

        assert captured["prompt_id"] == "prompt-1"
        assert captured["version_name"] == "None"
        assert captured["content"] == serialize_prompt_snapshot("", "")
        assert (
            window._selected_version_key
            == f"{VERSION_SELECTOR_DATA_DB_PREFIX}new-version"
        )
        assert window._prompt_editor.get_system_prompt() == ""
        assert window._prompt_editor.get_user_prompt() == ""

    def test_new_version_persists_custom_name(self, qtbot, monkeypatch):
        from src.core.prompt_snapshot import serialize_prompt_snapshot
        from src.gui.main_window import MainWindow, VERSION_SELECTOR_DATA_DB_PREFIX

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"

        prompt = Prompt(
            id="prompt-1",
            task_id="task-1",
            current_version_id=None,
            system_prompt="base-system",
            user_prompt="base-user",
        )
        monkeypatch.setattr(
            window._task_manager, "get_latest_task_prompt", lambda *_: prompt
        )

        captured: dict[str, str] = {}

        def fake_create_version(
            prompt_id: str, content: str, version_name: str | None = None
        ):
            captured["version_name"] = str(version_name)
            return Version(
                id="new-version",
                prompt_id=prompt_id,
                content=content,
                version_name=version_name,
                version_number=1,
            )

        monkeypatch.setattr(
            window._version_manager, "create_version", fake_create_version
        )
        monkeypatch.setattr(
            window._version_manager,
            "get_timeline",
            lambda *_: [
                Version(
                    id="new-version",
                    prompt_id="prompt-1",
                    content=serialize_prompt_snapshot("", ""),
                    version_number=1,
                    version_name="My Custom Name",
                )
            ],
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("My Custom Name", True),
        )

        window._on_new_version_clicked()

        assert captured["version_name"] == "My Custom Name"
        assert (
            window._selected_version_key
            == f"{VERSION_SELECTOR_DATA_DB_PREFIX}new-version"
        )

    def test_rename_version_updates_name(self, qtbot, monkeypatch):
        from src.gui.main_window import MainWindow, VERSION_SELECTOR_DATA_DB_PREFIX

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"
        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"

        original = Version(
            id="version-1",
            prompt_id="prompt-1",
            content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
            version_number=1,
            version_name="Old Name",
        )
        prompt = Prompt(
            id="prompt-1",
            task_id="task-1",
            current_version_id="version-1",
            system_prompt="old",
            user_prompt="old-user",
        )
        captured: dict[str, str | None] = {}

        def fake_update_version_name(version_id: str, version_name: str | None):
            captured["version_id"] = version_id
            captured["version_name"] = version_name
            return Version(
                id=version_id,
                prompt_id=original.prompt_id,
                content=original.content,
                version_number=original.version_number,
                version_name=version_name,
            )

        monkeypatch.setattr(window._version_manager, "get_version", lambda *_: original)
        monkeypatch.setattr(
            window._task_manager,
            "get_latest_task_prompt",
            lambda *_: prompt,
        )
        monkeypatch.setattr(
            window._version_manager,
            "update_version_name",
            fake_update_version_name,
        )
        monkeypatch.setattr(
            window._version_manager,
            "get_timeline",
            lambda *_: [
                Version(
                    id="version-1",
                    prompt_id="prompt-1",
                    content=original.content,
                    version_number=1,
                    version_name="Renamed",
                )
            ],
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("Renamed", True),
        )

        window._on_rename_version_clicked()

        assert captured["version_id"] == "version-1"
        assert captured["version_name"] == "Renamed"
        assert (
            window._selected_version_key
            == f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"
        )
        assert window.statusBar().currentMessage().startswith("Renamed to")

    def test_rename_version_requires_saved_selection(self, qtbot, monkeypatch):
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"
        window._selected_version_key = ""

        update_calls: list[str] = []
        monkeypatch.setattr(
            window._version_manager,
            "update_version_name",
            lambda *_: (
                update_calls.append("called")
                or Version(
                    id="version-1",
                    prompt_id="prompt-1",
                    content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
                    version_number=1,
                    version_name=None,
                )
            ),
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("Any", True),
        )

        window._on_rename_version_clicked()

        assert update_calls == []
        assert window.statusBar().currentMessage() == "Select a saved version to rename"

    def test_rename_version_rejects_blank_name(self, qtbot, monkeypatch):
        from src.gui.main_window import MainWindow, VERSION_SELECTOR_DATA_DB_PREFIX

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"
        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-1"

        monkeypatch.setattr(
            window._version_manager,
            "get_version",
            lambda *_: Version(
                id="version-1",
                prompt_id="prompt-1",
                content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
                version_number=1,
                version_name="Old Name",
            ),
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("   ", True),
        )
        monkeypatch.setattr(
            window._version_manager,
            "update_version_name",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                ValueError("Version name is required")
            ),
        )

        window._on_rename_version_clicked()

        assert window.statusBar().currentMessage() == "Version name is required"

    def test_rename_version_rejects_duplicate_name(self, qtbot, monkeypatch):
        from src.gui.main_window import MainWindow, VERSION_SELECTOR_DATA_DB_PREFIX

        window = MainWindow()
        qtbot.addWidget(window)
        window._current_task_id = "task-1"
        window._selected_version_key = f"{VERSION_SELECTOR_DATA_DB_PREFIX}version-2"

        monkeypatch.setattr(
            window._version_manager,
            "get_version",
            lambda *_: Version(
                id="version-2",
                prompt_id="prompt-1",
                content='{"schema_version": 1, "system_prompt": "old", "user_prompt": "old-user"}',
                version_number=2,
                version_name="Beta",
            ),
        )
        monkeypatch.setattr(
            window,
            "_ask_text_input",
            lambda *_, **__: ("Alpha", True),
        )
        monkeypatch.setattr(
            window._version_manager,
            "update_version_name",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                ValueError("Version name already exists")
            ),
        )

        window._on_rename_version_clicked()

        assert window.statusBar().currentMessage() == "Version name already exists"


class TestMainWindowTaskActions:
    def test_task_rename_dialog_is_centered_by_shared_path(self, qtbot, monkeypatch):
        from src.data.models import Task
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        get_task_calls: list[str] = []
        rename_calls: list[tuple[str, str]] = []
        position_calls: list[str] = []

        task = Task(
            id="task-1",
            name="old",
            description=None,
            is_archived=False,
            archived_at=None,
        )

        monkeypatch.setattr(
            window._task_manager,
            "get_task",
            lambda *_: get_task_calls.append("get_task") or task,
        )
        monkeypatch.setattr(
            window._task_manager,
            "rename_task",
            lambda task_id, new_name: (
                rename_calls.append((task_id, new_name))
                or Task(
                    id=task_id,
                    name=new_name,
                    description=None,
                    is_archived=False,
                    archived_at=None,
                )
            ),
        )

        class FakeInputDialog:
            def __init__(self, *_args, **_kwargs) -> None:
                self._text = ""

            def setWindowTitle(self, _title: str) -> None:
                return None

            def setLabelText(self, _label: str) -> None:
                return None

            def setTextValue(self, text: str) -> None:
                self._text = text

            def adjustSize(self) -> None:
                return None

            def width(self) -> int:
                return 120

            def height(self) -> int:
                return 90

            def move(self, _x: int, _y: int) -> None:
                position_calls.append("moved")

            def exec(self) -> QDialog.DialogCode:
                return QDialog.DialogCode.Accepted

            def textValue(self) -> str:
                return "renamed"

        monkeypatch.setattr("src.gui.main_window.QInputDialog", FakeInputDialog)

        window._on_task_rename_requested("task-1")

        assert get_task_calls == ["get_task"]
        assert rename_calls == [("task-1", "renamed")]
        assert position_calls == ["moved"]


class TestMainWindowPanels:
    """MainWindow 패널 구성 테스트"""

    def test_left_panel_attributes(self, qtbot):
        """좌측 패널(Task Navigator) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = _main_splitter(window)
        left_panel = main_splitter.widget(0)

        assert left_panel is not None
        assert isinstance(left_panel, QWidget)

    def test_center_panel_attributes(self, qtbot):
        """중앙 패널(Prompt Editor) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = _main_splitter(window)
        center_panel = main_splitter.widget(1)

        assert center_panel is not None
        assert isinstance(center_panel, QWidget)

    def test_right_panel_attributes(self, qtbot):
        """우측 패널(Result Viewer) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = _main_splitter(window)
        right_panel = main_splitter.widget(2)

        assert right_panel is not None
        assert isinstance(right_panel, QWidget)

    def test_panels_are_resizable(self, qtbot):
        """패널 크기 조절이 가능한지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        main_splitter = _main_splitter(window)

        # QSplitter의 크기 조절 기능 확인
        assert main_splitter.handle(1).isEnabled()
        assert main_splitter.handle(2).isEnabled()

    def test_new_task_creation_uses_dialog_value(self, qtbot, monkeypatch):
        from src.gui.main_window import MainWindow

        class FakeDialog:
            def __init__(self, *_args, **_kwargs):
                self.task_name = "Dialog Task"

            def center_on_parent_or_screen(self):
                return None

            def exec(self):
                return QDialog.DialogCode.Accepted

        window = MainWindow()
        qtbot.addWidget(window)

        monkeypatch.setattr("src.gui.main_window.NewTaskDialog", FakeDialog)

        created_names: list[str] = []

        def fake_create_task(name: str, description=None):
            created_names.append(name)
            return Task(
                id="task-test",
                name=name,
                description=description,
                is_archived=False,
                archived_at=None,
            )

        monkeypatch.setattr(window._task_manager, "create_task", fake_create_task)

        window._on_new_task()

        assert created_names == ["Dialog Task"]
