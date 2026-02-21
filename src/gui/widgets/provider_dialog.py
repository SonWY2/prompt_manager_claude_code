"""
[overview]
Provider Dialog 구현

[description]
추가/편집 다이얼로그 위젯입니다. Provider 추가 및 편집 다이얼로그를 제공합니다.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit,
    QComboBox, QSlider, QDoubleSpinBox, QSpinBox, QDialogButtonBox,
    QPushButton, QHBoxLayout
)

from src.data.models import Provider


DEFAULT_MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "llama2",
    "llama3",
    "mistral",
    "mixtral",
]


class ProviderDialog(QDialog):
    """
    [overview]
    Provider 다이얼로그 위젯

    [description]
    Provider 추가 및 편집 다이얼로그를 제공합니다.
    추가 모드와 편집 모드를 지원합니다.
    """

    def __init__(self, provider: Optional[Provider] = None, parent=None):
        """
        ProviderDialog 초기화

        Args:
            provider: 편집할 Provider 데이터 (추가 모드일 경우 None)
            parent: 부모 위젯
        """
        super().__init__(parent)

        self.provider = provider
        self.mode = "add" if provider is None else "edit"
        self.provider_id = provider.id if provider else None

        self._setup_ui()
        self._connect_signals()

        if provider is not None:
            self._populate_fields(provider)

    def _setup_ui(self):
        """UI 초기화"""
        if self.mode == "add":
            self.setWindowTitle("Add Provider")
        else:
            self.setWindowTitle("Edit Provider")

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Provider Name")
        form_layout.addRow("Name:", self.name_edit)

        self.description_edit = QPlainTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description (optional)")
        form_layout.addRow("Description:", self.description_edit)

        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://api.openai.com/v1")
        form_layout.addRow("API Base URL:", self.api_url_edit)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("API Key (optional)")

        self.show_api_key_button = QPushButton("Show")
        self.show_api_key_button.setCheckable(True)
        self.show_api_key_button.setMaximumWidth(60)

        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_edit)
        api_key_layout.addWidget(self.show_api_key_button)
        form_layout.addRow("API Key:", api_key_layout)

        self.model_combo = QComboBox()
        self.model_combo.addItems(DEFAULT_MODELS)
        form_layout.addRow("Default Model:", self.model_combo)

        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 20)
        self.temperature_slider.setValue(7)

        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.0, 2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        self.temperature_spinbox.setValue(0.7)

        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_spinbox)
        form_layout.addRow("Temperature:", temp_layout)

        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(1, 128000)
        self.max_tokens_spinbox.setValue(4096)
        form_layout.addRow("Max Tokens:", self.max_tokens_spinbox)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        layout.addWidget(self.button_box)

    def _connect_signals(self):
        """시그널 연결"""
        self.name_edit.textChanged.connect(self._validate_inputs)
        self.api_url_edit.textChanged.connect(self._validate_inputs)
        self.temperature_slider.valueChanged.connect(self._on_temperature_slider_changed)
        self.temperature_spinbox.valueChanged.connect(self._on_temperature_spinbox_changed)
        self.show_api_key_button.toggled.connect(self._toggle_api_key_visibility)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def _validate_inputs(self):
        """입력 필드 유효성 검사"""
        name = self.name_edit.text().strip()
        api_url = self.api_url_edit.text().strip()

        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(bool(name and api_url))

    def _on_temperature_slider_changed(self, value: int):
        """
        Temperature 슬라이더 변경 이벤트 핸들러

        Args:
            value: 슬라이더 값 (0-20)
        """
        self.temperature_spinbox.blockSignals(True)
        self.temperature_spinbox.setValue(value / 10.0)
        self.temperature_spinbox.blockSignals(False)

    def _on_temperature_spinbox_changed(self, value: float):
        """
        Temperature Spinbox 변경 이벤트 핸들러

        Args:
            value: Spinbox 값 (0.0-2.0)
        """
        self.temperature_slider.blockSignals(True)
        self.temperature_slider.setValue(int(value * 10))
        self.temperature_slider.blockSignals(False)

    def _toggle_api_key_visibility(self, visible: bool):
        """
        API Key 표시/숨김 토글

        Args:
            visible: 표시 여부
        """
        if visible:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_button.setText("Hide")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_key_button.setText("Show")

    def _populate_fields(self, provider: Provider):
        """
        필드에 Provider 데이터 로드 (편집 모드)

        Args:
            provider: Provider 데이터
        """
        self.name_edit.setText(provider.name)
        self.api_url_edit.setText(provider.api_url)
        self.api_key_edit.setText(provider.api_key or "")

        model_index = self.model_combo.findText(provider.model)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)

    def get_provider_data(self) -> dict:
        """
        입력 필드의 Provider 데이터 조회

        Returns:
            Provider 데이터 딕셔너리
        """
        return {
            "id": self.provider_id,
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "api_url": self.api_url_edit.text().strip(),
            "api_key": self.api_key_edit.text().strip(),
            "model": self.model_combo.currentText(),
            "temperature": self.temperature_spinbox.value(),
            "max_tokens": self.max_tokens_spinbox.value(),
        }
