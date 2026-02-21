"""
[overview]
Provider Dialog 테스트

[description]
추가/편집 다이얼로그 위젯에 대한 pytest-qt 테스트입니다.
"""

from datetime import datetime

from PySide6.QtWidgets import QDialogButtonBox, QLineEdit

from src.data.models import Provider


class TestProviderDialog:
    """Provider Dialog 테스트 클래스"""

    def test_provider_dialog_creation_add_mode(self, qtbot):
        """다이얼로그 생성 (추가 모드) 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Add Provider"
        assert dialog.mode == "add"
        assert dialog.provider_id is None

    def test_provider_dialog_creation_edit_mode(self, qtbot):
        """다이얼로그 생성 (편집 모드) 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        provider = Provider(
            id="prov_1",
            name="Production GPT-4",
            api_url="https://api.openai.com/v1",
            api_key="sk-test-key-1",
            model="gpt-4",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        dialog = ProviderDialog(provider=provider)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Edit Provider"
        assert dialog.mode == "edit"
        assert dialog.provider_id == "prov_1"

    def test_provider_dialog_fields_exist(self, qtbot):
        """필드 존재 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "name_edit")
        assert hasattr(dialog, "description_edit")
        assert hasattr(dialog, "api_url_edit")
        assert hasattr(dialog, "api_key_edit")
        assert hasattr(dialog, "show_api_key_button")
        assert hasattr(dialog, "model_combo")
        assert hasattr(dialog, "temperature_slider")
        assert hasattr(dialog, "temperature_spinbox")
        assert hasattr(dialog, "max_tokens_spinbox")
        assert hasattr(dialog, "button_box")

    def test_provider_dialog_populate_provider_data(self, qtbot):
        """Provider 데이터 로드 테스트 (편집 모드)"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        provider = Provider(
            id="prov_1",
            name="Production GPT-4",
            api_url="https://api.openai.com/v1",
            api_key="sk-test-key-1",
            model="gpt-4",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        dialog = ProviderDialog(provider=provider)
        qtbot.addWidget(dialog)

        assert dialog.name_edit.text() == "Production GPT-4"
        assert dialog.api_url_edit.text() == "https://api.openai.com/v1"
        assert dialog.api_key_edit.text() == "sk-test-key-1"

    def test_provider_dialog_api_key_toggle_visibility(self, qtbot):
        """API Key 표시/숨김 토글 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.api_key_edit.setText("sk-test-key")

        assert dialog.api_key_edit.echoMode() == QLineEdit.EchoMode.Password

        dialog.show_api_key_button.click()

        assert dialog.api_key_edit.echoMode() == QLineEdit.EchoMode.Normal

        dialog.show_api_key_button.click()

        assert dialog.api_key_edit.echoMode() == QLineEdit.EchoMode.Password

    def test_provider_dialog_temperature_sync(self, qtbot):
        """Temperature 슬라이더/Spinbox 동기화 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.temperature_slider.setValue(12)

        assert dialog.temperature_spinbox.value() == 1.2

        dialog.temperature_spinbox.setValue(1.8)

        assert dialog.temperature_slider.value() == 18

    def test_provider_dialog_validation_required_fields(self, qtbot):
        """필수 필드 유효성 검사 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        ok_button = dialog.button_box.button(QDialogButtonBox.StandardButton.Ok)

        assert ok_button.isEnabled() is False

        dialog.name_edit.setText("Test Provider")

        assert ok_button.isEnabled() is False

        dialog.api_url_edit.setText("https://test.com/v1")

        assert ok_button.isEnabled() is True

    def test_provider_dialog_get_provider_data(self, qtbot):
        """Provider 데이터 조회 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.name_edit.setText("Test Provider")
        dialog.api_url_edit.setText("https://test.com/v1")
        dialog.api_key_edit.setText("sk-test-key")
        dialog.model_combo.setCurrentText("gpt-4")
        dialog.temperature_spinbox.setValue(0.7)
        dialog.max_tokens_spinbox.setValue(2048)

        provider_data = dialog.get_provider_data()

        assert provider_data["name"] == "Test Provider"
        assert provider_data["api_url"] == "https://test.com/v1"
        assert provider_data["api_key"] == "sk-test-key"
        assert provider_data["model"] == "gpt-4"
        assert provider_data["temperature"] == 0.7
        assert provider_data["max_tokens"] == 2048

    def test_provider_dialog_model_options(self, qtbot):
        """모델 옵션 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        model_count = dialog.model_combo.count()
        assert model_count > 0

        dialog.model_combo.setCurrentIndex(0)
        selected_model = dialog.model_combo.currentText()
        assert selected_model != ""

    def test_provider_dialog_accept(self, qtbot):
        """다이얼로그 accept 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.name_edit.setText("Test Provider")
        dialog.api_url_edit.setText("https://test.com/v1")

        assert dialog.result() == 0

        dialog.accept()

        assert dialog.result() == 1

    def test_provider_dialog_reject(self, qtbot):
        """다이얼로그 reject 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.reject()

        assert dialog.result() == 0

    def test_provider_dialog_url_validation(self, qtbot):
        """URL 유효성 검사 테스트"""
        from src.gui.widgets.provider_dialog import ProviderDialog

        dialog = ProviderDialog()
        qtbot.addWidget(dialog)

        dialog.name_edit.setText("Test Provider")

        # URL 비어있음 - 비활성화
        dialog.api_url_edit.setText("")

        ok_button = dialog.button_box.button(QDialogButtonBox.StandardButton.Ok)
        assert ok_button.isEnabled() is False

        # URL 입력 - 활성화
        dialog.api_url_edit.setText("https://test.com/v1")

        assert ok_button.isEnabled() is True
