"""
[overview]
ProviderManagementWidget 테스트

[description]
Provider 설정 위젯의 연결 테스트/상태 갱신/버튼 상태 제어를 검증합니다.
"""

from datetime import datetime
from typing import Any, Callable
from unittest.mock import Mock

from src.core.provider_manager import ProviderManager
from src.data.models import Provider
from src.gui.widgets.provider_management_widget import ProviderManagementWidget


class _FakeSignal:
    def __init__(self) -> None:
        self._slots: list[Callable[..., None]] = []

    def connect(self, slot: Callable[..., None]) -> None:
        self._slots.append(slot)

    def emit(self, *args: Any, **kwargs: Any) -> None:
        for slot in self._slots:
            slot(*args, **kwargs)


class _FakeThread:
    def __init__(self) -> None:
        self.started = _FakeSignal()
        self.finished = _FakeSignal()
        self._running = False
        self.started_called = False

    def isRunning(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True
        self.started_called = True
        self.started.emit()

    def quit(self, *_args: object, **_kwargs: object) -> None:
        self._running = False
        self.finished.emit()

    def deleteLater(self) -> None:
        self.deleted = True


class _FakeWorker:
    def __init__(
        self,
        provider_manager: ProviderManager,
        provider_data: dict[str, Any],
        provider_id: str | None = None,
    ) -> None:
        self._provider_manager = provider_manager
        self._provider_data = provider_data
        self._provider_id = provider_id
        self.finished = _FakeSignal()
        self.moved = False
        self.run_calls: list[dict[str, Any]] = []

    def moveToThread(self, _thread: object) -> None:
        self.moved = True

    def run(self) -> None:
        self.run_calls.append(self._provider_data)
        if self._provider_id:
            result = self._provider_manager.test_connection(self._provider_id)
        else:
            result = self._provider_manager.test_connection_with_data(
                self._provider_data
            )

        target_provider_id = self._provider_id or str(self._provider_data.get("id", ""))
        self.finished.emit(result, target_provider_id)

    def deleteLater(self) -> None:
        self.deleted = True


def _build_provider_manager() -> ProviderManager:
    manager = Mock(spec=ProviderManager)
    provider = Provider(
        id="provider_1",
        name="OpenAI",
        description=None,
        api_url="https://api.openai.com/v1",
        api_key=None,
        model="gpt-4o",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    manager.get_all_providers.return_value = [provider]
    return manager


def test_test_connection_shows_warning_when_api_url_is_empty(qtbot):
    manager = _build_provider_manager()
    widget = ProviderManagementWidget(manager)
    qtbot.addWidget(widget)

    warning_mock = Mock()
    information_mock = Mock()

    widget._provider_list_panel.refresh_provider_list()
    widget._config_panel.name_edit.setText("OpenAI")
    widget._config_panel.api_url_edit.setText("")

    with (
        __import__("pytest").MonkeyPatch().context() as monkeypatch,
    ):
        monkeypatch.setattr(
            "src.gui.widgets.provider_management_widget.QMessageBox.warning",
            warning_mock,
        )
        monkeypatch.setattr(
            "src.gui.widgets.provider_management_widget.QMessageBox.information",
            information_mock,
        )

        widget._on_test_connection(
            {
                "id": "provider_1",
                "name": "OpenAI",
                "api_url": "",
            }
        )

    assert warning_mock.called
    assert information_mock.call_count == 0


def test_test_connection_prevents_concurrent_test(qtbot, monkeypatch):
    manager = _build_provider_manager()
    widget = ProviderManagementWidget(manager)
    qtbot.addWidget(widget)

    running_thread = Mock()
    running_thread.isRunning.return_value = True
    widget.test_thread = running_thread

    info_mock = Mock()
    warning_mock = Mock()

    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.information", info_mock
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.warning", warning_mock
    )

    widget._on_test_connection(
        {
            "id": "provider_1",
            "name": "OpenAI",
            "api_url": "https://api.openai.com/v1",
        }
    )

    info_mock.assert_called_once()
    assert warning_mock.call_count == 0


def test_test_connection_success_updates_button_and_status(qtbot, monkeypatch):
    manager = _build_provider_manager()
    manager.test_connection.return_value = {
        "success": True,
        "message": "Connection successful",
    }

    widget = ProviderManagementWidget(manager)
    qtbot.addWidget(widget)
    widget._provider_list_panel.refresh_provider_list()
    widget._config_panel.name_edit.setText("OpenAI")
    widget._config_panel.api_url_edit.setText("https://api.openai.com/v1")

    status_mock = Mock()
    monkeypatch.setattr(
        widget._provider_list_panel, "update_provider_status", status_mock
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.information", Mock()
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.warning", Mock()
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.ConnectionTestWorker", _FakeWorker
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QThread", _FakeThread
    )

    widget._on_test_connection(
        {
            "id": "provider_1",
            "name": "OpenAI",
            "api_url": "https://api.openai.com/v1",
        }
    )

    assert manager.test_connection.called
    assert status_mock.call_args == (("provider_1", "connected"),)
    assert widget._config_panel.test_button.text() == "Test Connection"
    assert widget._config_panel.test_button.isEnabled()
    assert widget.test_thread is None
    assert widget.test_worker is None


def test_test_connection_failure_updates_button_and_status(qtbot, monkeypatch):
    manager = _build_provider_manager()
    manager.test_connection.return_value = {
        "success": False,
        "message": "Connection failed",
    }

    widget = ProviderManagementWidget(manager)
    qtbot.addWidget(widget)
    widget._provider_list_panel.refresh_provider_list()
    widget._config_panel.name_edit.setText("OpenAI")
    widget._config_panel.api_url_edit.setText("https://api.openai.com/v1")

    status_mock = Mock()
    warning_mock = Mock()
    monkeypatch.setattr(
        widget._provider_list_panel, "update_provider_status", status_mock
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.warning", warning_mock
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QMessageBox.information", Mock()
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.ConnectionTestWorker", _FakeWorker
    )
    monkeypatch.setattr(
        "src.gui.widgets.provider_management_widget.QThread", _FakeThread
    )

    widget._on_test_connection(
        {
            "id": "provider_1",
            "name": "OpenAI",
            "api_url": "https://api.openai.com/v1",
        }
    )

    assert status_mock.call_args == (("provider_1", "error"),)
    assert warning_mock.called
    assert widget._config_panel.test_button.text() == "Test Connection"
    assert widget._config_panel.test_button.isEnabled()
    assert widget.test_thread is None
    assert widget.test_worker is None
