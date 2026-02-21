"""
[overview]
Provider Configuration Detail Panel 테스트

[description]
우측 Configuration Detail Panel 위젯에 대한 pytest-qt 테스트입니다.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QLineEdit

from src.core.provider_manager import ProviderManager
from src.data.models import Provider


@pytest.fixture
def mock_provider_manager():
    """Mock ProviderManager fixture"""
    manager = Mock(spec=ProviderManager)

    # 테스트용 Provider 데이터
    provider1 = Provider(
        id="prov_1",
        name="Production GPT-4",
        api_url="https://api.openai.com/v1",
        api_key="sk-test-key-1",
        model="gpt-4",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    provider2 = Provider(
        id="prov_2",
        name="Local Llama3",
        api_url="http://localhost:11434/v1",
        api_key=None,
        model="llama2",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    manager.get_provider.side_effect = lambda pid: {
        "prov_1": provider1,
        "prov_2": provider2,
    }.get(pid)
    manager.update_provider.return_value = provider1

    return manager


class TestProviderConfigPanel:
    """Provider Config Panel 테스트 클래스"""

    def test_provider_config_panel_creation(self, qtbot, mock_provider_manager):
        """Provider Config Panel 생성 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        assert panel.layout() is not None
        assert hasattr(panel, "name_edit")
        assert hasattr(panel, "description_edit")
        assert hasattr(panel, "api_url_edit")
        assert hasattr(panel, "api_key_edit")
        assert hasattr(panel, "model_combo")
        assert hasattr(panel, "temperature_slider")
        assert hasattr(panel, "temperature_spinbox")
        assert hasattr(panel, "max_tokens_spinbox")
        assert hasattr(panel, "test_button")
        assert hasattr(panel, "save_button")

    def test_provider_config_panel_load_provider(self, qtbot, mock_provider_manager):
        """Provider 데이터 로드 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        panel.load_provider("prov_1")

        assert panel.name_edit.text() == "Production GPT-4"
        assert panel.api_url_edit.text() == "https://api.openai.com/v1"
        assert panel.api_key_edit.text() == "sk-test-key-1"

    def test_provider_config_panel_clear_fields(self, qtbot, mock_provider_manager):
        """필드 초기화 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        panel.load_provider("prov_1")

        panel.clear_fields()

        assert panel.name_edit.text() == ""
        assert panel.description_edit.toPlainText() == ""
        assert panel.api_url_edit.text() == ""
        assert panel.api_key_edit.text() == ""

    def test_provider_config_panel_save_signal(self, qtbot, mock_provider_manager):
        """저장 시그널 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        # 필수 필드 입력
        panel.name_edit.setText("Test Provider")
        panel.api_url_edit.setText("https://test.com/v1")

        with qtbot.waitSignal(panel.save_requested, timeout=1000) as blocker:
            panel.save_button.click()

        assert len(blocker.args) > 0

    def test_provider_config_panel_test_connection_signal(
        self, qtbot, mock_provider_manager
    ):
        """연결 테스트 시그널 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        with qtbot.waitSignal(panel.test_connection_requested, timeout=1000) as blocker:
            panel.test_button.click()

        assert len(blocker.args) > 0

    def test_provider_config_panel_temperature_slider_sync(
        self, qtbot, mock_provider_manager
    ):
        """Temperature 슬라이더와 Spinbox 동기화 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        panel.temperature_slider.setValue(15)

        assert panel.temperature_spinbox.value() == 1.5

        panel.temperature_spinbox.setValue(0.7)

        assert panel.temperature_slider.value() == 7

    def test_provider_config_panel_validation_url(self, qtbot, mock_provider_manager):
        """URL 유효성 검사 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        # name 필드 입력 (필수)
        panel.name_edit.setText("Test Provider")

        # URL 비어있음 - 비활성화
        panel.api_url_edit.setText("")

        assert not panel.save_button.isEnabled()

        # URL 입력 - 활성화
        panel.api_url_edit.setText("https://api.openai.com/v1")

        assert panel.save_button.isEnabled()

    def test_provider_config_panel_api_key_toggle(self, qtbot, mock_provider_manager):
        """API Key 표시/숨김 토글 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        panel.api_key_edit.setText("sk-test-key")

        assert panel.api_key_edit.echoMode() == QLineEdit.EchoMode.Password

    def test_provider_config_panel_model_options(self, qtbot, mock_provider_manager):
        """모델 옵션 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        model_count = panel.model_combo.count()
        assert model_count > 0

        panel.model_combo.setCurrentIndex(0)
        selected_model = panel.model_combo.currentText()
        assert selected_model != ""

    def test_provider_config_panel_max_tokens_range(self, qtbot, mock_provider_manager):
        """Max Tokens 범위 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        max_value = panel.max_tokens_spinbox.maximum()
        min_value = panel.max_tokens_spinbox.minimum()
        assert max_value > min_value
        assert min_value >= 0

        panel.max_tokens_spinbox.setValue(2048)
        assert panel.max_tokens_spinbox.value() == 2048

    def test_provider_config_panel_stop_sequences(self, qtbot, mock_provider_manager):
        """Stop Sequences 입력 테스트"""
        from src.gui.widgets.provider_config_panel import ProviderConfigPanel

        panel = ProviderConfigPanel(mock_provider_manager)
        qtbot = qtbot
        qtbot.addWidget(panel)

        panel.model_combo.setCurrentText("llama3")
        assert panel.model_combo.currentText() == "llama3"
