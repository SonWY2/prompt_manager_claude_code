"""
[overview]
Provider Configuration Detail Panel 구현

[description]
우측 Configuration Detail Panel 위젯입니다. Provider 설정을 표시하고 수정합니다.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
)

from src.core.provider_manager import ProviderManager
from src.gui.theme import (
    COLOR_BACKGROUND,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_BUTTON_BG,
    COLOR_BUTTON_HOVER,
    COLOR_ACCENT,
)

PROVIDER_PRESETS = {
    "OpenAI": {
        "api_url": "https://api.openai.com/v1",
    },
    "Ollama": {
        "api_url": "http://localhost:11434/v1",
    },
    "vLLM": {
        "api_url": "http://localhost:8343/v1",
    },
    "Anthropic": {
        "api_url": "https://api.anthropic.com/v1",
    },
    "OpenRouter": {
        "api_url": "https://openrouter.ai/api/v1",
    },
    "Custom": {
        "api_url": "",
    },
}

DEFAULT_MODEL_OPTIONS = [
    "gpt-4o",
    "gpt-4",
    "claude-3-opus",
    "llama2",
    "llama3",
]


class ProviderConfigPanel(QWidget):
    """
    [overview]
    Provider Configuration Detail Panel 위젯

    [description]
    선택된 Provider의 상세 설정을 표시하고 수정합니다.
    General Info, Connection Settings, Default Model Parameters 섹션을 제공합니다.
    """

    save_requested = Signal(dict)
    test_connection_requested = Signal(dict)

    def __init__(
        self, provider_manager: ProviderManager, parent: Optional[QWidget] = None
    ):
        """
        ProviderConfigPanel 초기화

        Args:
            provider_manager: ProviderManager 인스턴스
            parent: 부모 위젯
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

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_BACKGROUND};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {COLOR_INPUT_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_INPUT_BORDER};
                border-radius: 6px;
                padding: 8px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border: 1px solid {COLOR_ACCENT};
            }}
            QPushButton {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUTTON_HOVER};
            }}
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: 10pt;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Provider Name")
        form_layout.addRow("Name", self.name_edit)

        self.description_edit = QPlainTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Description (optional)")
        form_layout.addRow("Description", self.description_edit)

        scroll_layout.addLayout(form_layout)

        general_label = QLabel("General Info")
        general_label.setStyleSheet(f"font-size: 12pt; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; margin-top: 10px;")
        scroll_layout.addWidget(general_label)

        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(10)

        preset_label = QLabel("Provider Preset")
        preset_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        preset_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PROVIDER_PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        scroll_layout.addLayout(preset_layout)

        connection_layout = QFormLayout()
        connection_layout.setSpacing(10)
        connection_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://api.openai.com/v1")
        connection_layout.addRow("API Base URL", self.api_url_edit)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_edit.setPlaceholderText("API Key (optional)")

        self.show_api_key_button = QPushButton("Show")
        self.show_api_key_button.setCheckable(True)
        self.show_api_key_button.setFixedWidth(60)

        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(self.api_key_edit)
        api_key_layout.addWidget(self.show_api_key_button)
        connection_layout.addRow("API Key", api_key_layout)

        connection_label = QLabel("Connection Settings")
        connection_label.setStyleSheet(f"font-size: 12pt; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; margin-top: 10px;")
        scroll_layout.addWidget(connection_label)

        scroll_layout.addLayout(connection_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.test_button = QPushButton("Test Connection")
        self.test_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.test_button)

        scroll_layout.addLayout(button_layout)

        parameters_label = QLabel("Default Model Parameters")
        parameters_label.setStyleSheet(f"font-size: 12pt; font-weight: 600; color: {COLOR_TEXT_PRIMARY}; margin-top: 10px;")
        scroll_layout.addWidget(parameters_label)

        parameters_layout = QFormLayout()
        parameters_layout.setSpacing(10)
        parameters_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems(DEFAULT_MODEL_OPTIONS)
        self.model_combo.setCurrentText("llama2")
        parameters_layout.addRow("Default Model", self.model_combo)

        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 20)
        self.temperature_slider.setValue(7)

        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.0, 2.0)
        self.temperature_spinbox.setSingleStep(0.1)
        self.temperature_spinbox.setValue(0.7)

        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_spinbox)
        parameters_layout.addRow("Temperature", temp_layout)

        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(1, 128000)
        self.max_tokens_spinbox.setValue(4096)
        parameters_layout.addRow("Max Tokens", self.max_tokens_spinbox)

        scroll_layout.addLayout(parameters_layout)

        scroll_layout.addStretch()

        save_button_layout = QHBoxLayout()
        save_button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setEnabled(False)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                font-weight: 600;
                padding: 10px 24px;
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BUTTON_BG};
                color: {COLOR_TEXT_SECONDARY};
            }}
        """)
        save_button_layout.addWidget(self.save_button)

        scroll_layout.addLayout(save_button_layout)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def _connect_signals(self):
        """시그널 연결"""
        self.name_edit.textChanged.connect(self._validate_inputs)
        self.api_url_edit.textChanged.connect(self._validate_inputs)
        self.model_combo.currentTextChanged.connect(self._validate_inputs)
        self.temperature_slider.valueChanged.connect(
            self._on_temperature_slider_changed
        )
        self.temperature_spinbox.valueChanged.connect(
            self._on_temperature_spinbox_changed
        )
        self.save_button.clicked.connect(self._on_save_clicked)
        self.test_button.clicked.connect(self._on_test_connection_clicked)
        self.show_api_key_button.toggled.connect(self._toggle_api_key_visibility)

    def _validate_inputs(self):
        """입력 필드 유효성 검사"""
        name = self.name_edit.text().strip()
        api_url = self.api_url_edit.text().strip()

        self.save_button.setEnabled(bool(name and api_url))

    def _on_preset_changed(self, preset_name: str):
        """프리셋 변경 핸들러

        Args:
            preset_name: 선택된 프리셋 이름
        """
        preset_data = PROVIDER_PRESETS.get(preset_name)
        if preset_data:
            api_url = preset_data.get("api_url", "")
            self.api_url_edit.setText(api_url)

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

    def _on_save_clicked(self):
        """저장 버튼 클릭 이벤트 핸들러"""
        provider_data = self._get_provider_data()
        self.save_requested.emit(provider_data)

    def _on_test_connection_clicked(self):
        """연결 테스트 버튼 클릭 이벤트 핸들러"""
        provider_data = self._get_provider_data()
        self.test_connection_requested.emit(provider_data)

    def _get_provider_data(self) -> dict[str, object]:
        """
        현재 입력 필드의 데이터 조회

        Returns:
            Provider 데이터 딕셔너리
        """
        return {
            "id": self.current_provider_id,
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "api_url": self.api_url_edit.text().strip(),
            "api_key": self.api_key_edit.text().strip(),
            "model": self.model_combo.currentText().strip(),
            "temperature": self.temperature_spinbox.value(),
            "max_tokens": self.max_tokens_spinbox.value(),
        }

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

    def load_provider(self, provider_id: str):
        """
        Provider 데이터 로드

        Args:
            provider_id: Provider ID
        """
        provider = self.provider_manager.get_provider(provider_id)
        if provider is None:
            return

        self.current_provider_id = provider_id
        self.name_edit.setText(provider.name)
        self.api_url_edit.setText(provider.api_url)
        self.api_key_edit.setText(provider.api_key or "")
        self.model_combo.setCurrentText(provider.model)
        self._validate_inputs()

        # API Key 버튼 상태 초기화
        self.show_api_key_button.setChecked(False)

    def clear_fields(self):
        """입력 필드 초기화"""
        self.current_provider_id = None
        self.name_edit.clear()
        self.description_edit.clear()
        self.api_url_edit.clear()
        self.api_key_edit.clear()
        self.model_combo.setCurrentText("")
        self.preset_combo.setCurrentIndex(0)
        self.temperature_slider.setValue(7)
        self.temperature_spinbox.setValue(0.7)
        self.max_tokens_spinbox.setValue(4096)
        self.save_button.setEnabled(False)
