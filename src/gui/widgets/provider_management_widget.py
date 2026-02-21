"""
[overview]
LLM Provider Management 위젯

[description]
좌측 Provider List Panel과 우측 Configuration Detail Panel을 결합한 Split-View 레이아웃 위젯입니다.
"""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtWidgets import QMessageBox, QInputDialog, QSplitter, QVBoxLayout, QWidget

from src.core.provider_manager import ProviderManager
from src.gui.theme import COLOR_BORDER
from src.gui.widgets.provider_config_panel import ProviderConfigPanel
from src.gui.widgets.provider_list_panel import ProviderListPanel
from src.utils.logger import logger


class ConnectionTestWorker(QObject):
    """
    [overview]
    연결 테스트 비동기 워커

    [description]
    별도 스레드에서 연결 테스트를 수행하여 UI 응답성을 유지합니다.
    """

    finished = Signal(dict, str)

    def __init__(
        self,
        provider_manager: ProviderManager,
        provider_data: dict[str, Any],
        provider_id: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._provider_manager = provider_manager
        self._provider_data = provider_data
        self._provider_id = provider_id

    def run(self) -> None:
        if self._provider_id:
            result = self._provider_manager.test_connection(self._provider_id)
        else:
            result = self._provider_manager.test_connection_with_data(
                self._provider_data
            )

        target_provider_id = self._provider_id or str(self._provider_data.get("id", ""))
        self.finished.emit(result, target_provider_id)


class ProviderManagementWidget(QWidget):
    """
    [overview]
    LLM Provider Management 위젯

    [description]
    Provider List와 Configuration Detail Panel을 Split-View로 결합한 위젯입니다.
    """

    DEFAULT_MODEL = "llama2"

    provider_added = Signal(dict)
    provider_updated = Signal(dict)
    provider_deleted = Signal(str)

    def __init__(
        self, provider_manager: ProviderManager, parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)

        self.provider_manager = provider_manager
        self.test_thread: Optional[QThread] = None
        self.test_worker: Optional[ConnectionTestWorker] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(
            f"""
            QSplitter::handle:horizontal {{
                background-color: {COLOR_BORDER};
                width: 1px;
            }}
            """
        )

        self._provider_list_panel = ProviderListPanel(self.provider_manager)
        self._splitter.addWidget(self._provider_list_panel)

        self._config_panel = ProviderConfigPanel(self.provider_manager)
        self._splitter.addWidget(self._config_panel)

        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([300, 600])

        layout.addWidget(self._splitter)

    def _connect_signals(self) -> None:
        self._provider_list_panel.provider_selected.connect(self._on_provider_selected)
        self._provider_list_panel.add_provider_requested.connect(self._on_add_provider)
        self._provider_list_panel.provider_deleted.connect(self._on_provider_deleted)

        self._config_panel.save_requested.connect(self._on_provider_save)
        self._config_panel.test_connection_requested.connect(self._on_test_connection)

    def _on_provider_selected(self, provider_id: str) -> None:
        self._config_panel.load_provider(provider_id)

    def _on_add_provider(self) -> None:
        name, ok = QInputDialog.getText(self, "New Provider", "Provider name:")
        if not ok or not name.strip():
            return

        provider = self.provider_manager.create_provider(
            name=name.strip(),
            api_url="",
            api_key=None,
            model=self.DEFAULT_MODEL,
        )

        self._provider_list_panel.refresh_provider_list()
        self._provider_list_panel.select_provider(str(provider.id))
        self.provider_added.emit({"id": provider.id, "name": provider.name})

        logger.info(
            "Provider created",
            extra={
                "data": {
                    "provider_id": provider.id,
                    "name": provider.name,
                }
            },
        )

    def _on_provider_deleted(self, provider_id: str) -> None:
        deleted = self.provider_manager.delete_provider(provider_id)
        if not deleted:
            QMessageBox.warning(self, "Delete Provider", "Failed to delete provider.")
            return

        self.provider_deleted.emit(provider_id)
        self._provider_list_panel.refresh_provider_list()
        if self._config_panel.current_provider_id == provider_id:
            self._config_panel.clear_fields()

        logger.info("Provider deleted", extra={"data": {"provider_id": provider_id}})

    def _on_provider_save(self, provider_data: dict[str, Any]) -> None:
        provider_id = provider_data.get("id")

        provider_name = str(provider_data.get("name", ""))
        provider_description = str(provider_data.get("description", "")) or None
        provider_api_url = str(provider_data.get("api_url", ""))
        provider_api_key = str(provider_data.get("api_key", "")) or None
        provider_model = str(provider_data.get("model", self.DEFAULT_MODEL))

        if provider_id:
            updated_provider = self.provider_manager.update_provider(
                provider_id=str(provider_id),
                name=provider_name,
                api_url=provider_api_url,
                api_key=provider_api_key,
                model=provider_model,
            )
            if updated_provider is None:
                QMessageBox.warning(self, "Save Provider", "Provider not found.")
                return

            self.provider_updated.emit(provider_data)
            logger.info(
                "Provider updated",
                extra={
                    "data": {
                        "provider_id": provider_id,
                        "name": provider_data.get("name"),
                    }
                },
            )
        else:
            created_provider = self.provider_manager.create_provider(
                name=provider_name,
                description=provider_description,
                api_url=provider_api_url,
                api_key=provider_api_key,
                model=provider_model,
            )
            provider_data["id"] = created_provider.id
            self.provider_added.emit(provider_data)
            self._config_panel.load_provider(str(created_provider.id))
            logger.info(
                "Provider created",
                extra={
                    "data": {
                        "provider_id": created_provider.id,
                        "name": created_provider.name,
                    }
                },
            )

        self._provider_list_panel.refresh_provider_list()

    def _on_test_connection(self, provider_data: dict[str, Any]) -> None:
        api_url = str(provider_data.get("api_url", "")).strip()
        provider_id_raw = provider_data.get("id")
        provider_id = str(provider_id_raw) if provider_id_raw else None

        if not api_url:
            QMessageBox.warning(
                self,
                "Connection Test",
                "Please enter an API URL before testing the connection.",
            )
            return

        if self.test_thread and self.test_thread.isRunning():
            QMessageBox.information(
                self,
                "Connection Test",
                "A connection test is already in progress. Please wait.",
            )
            return

        self._config_panel.test_button.setEnabled(False)
        self._config_panel.test_button.setText("Testing...")

        self.test_thread = QThread()
        self.test_worker = ConnectionTestWorker(
            self.provider_manager,
            provider_data,
            provider_id,
        )
        self.test_worker.moveToThread(self.test_thread)

        self.test_thread.started.connect(self.test_worker.run)
        self.test_worker.finished.connect(self._on_test_finished)
        self.test_worker.finished.connect(self.test_thread.quit)
        self.test_thread.finished.connect(self._cleanup_test_thread)
        self.test_thread.start()

    def _on_test_finished(self, result: dict[str, Any], provider_id: str) -> None:
        success = bool(result.get("success", False))
        message = str(result.get("message", "Unknown error"))

        if success:
            QMessageBox.information(
                self, "Connection Test", f"Connection successful!\n\n{message}"
            )
            if provider_id:
                self._provider_list_panel.update_provider_status(
                    provider_id, "connected"
                )
        else:
            QMessageBox.warning(
                self, "Connection Test", f"Connection failed!\n\n{message}"
            )
            if provider_id:
                self._provider_list_panel.update_provider_status(provider_id, "error")

        self._config_panel.test_button.setEnabled(True)
        self._config_panel.test_button.setText("Test Connection")

    def _cleanup_test_thread(self) -> None:
        if self.test_worker is not None:
            self.test_worker.deleteLater()
        if self.test_thread is not None:
            self.test_thread.deleteLater()
        self.test_worker = None
        self.test_thread = None

    def load_providers(self) -> None:
        self._provider_list_panel.load_providers()
