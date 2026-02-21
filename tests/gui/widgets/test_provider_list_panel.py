"""
[overview]
Provider List Panel 테스트

[description]
좌측 Provider List Panel 위젯에 대한 pytest-qt 테스트입니다.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt

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
        updated_at=datetime.now()
    )
    provider2 = Provider(
        id="prov_2",
        name="Local Llama3",
        api_url="http://localhost:11434/v1",
        api_key=None,
        model="llama2",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    manager.get_all_providers.return_value = [provider1, provider2]
    manager.get_provider.side_effect = lambda pid: {
        "prov_1": provider1,
        "prov_2": provider2
    }.get(pid)

    return manager





class TestProviderListPanel:
    """Provider List Panel 테스트 클래스"""

    def test_provider_list_panel_creation(self, qtbot, mock_provider_manager):
        """Provider List Panel 생성 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        # 기본 컴포넌트 존재 확인
        assert panel.layout() is not None
        assert hasattr(panel, "provider_list")
        assert hasattr(panel, "add_button")

    def test_provider_list_panel_loads_providers(self, qtbot, mock_provider_manager):
        """Provider 목록 로드 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        # Provider 로드
        panel.load_providers()

        # 리스트 아이템 개수 확인
        assert panel.provider_list.count() == 2

    def test_provider_list_panel_item_content(self, qtbot, mock_provider_manager):
        """Provider 리스트 아이템 내용 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        panel.load_providers()

        first_item = panel.provider_list.item(0)
        assert "Production GPT-4" in first_item.text()
        assert first_item.data(Qt.ItemDataRole.UserRole) == "prov_1"

        second_item = panel.provider_list.item(1)
        assert "Local Llama3" in second_item.text()
        assert second_item.data(Qt.ItemDataRole.UserRole) == "prov_2"

    def test_provider_list_panel_selection_signal(self, qtbot, mock_provider_manager):
        """Provider 선택 시그널 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        panel.load_providers()

        panel.provider_list.setCurrentRow(0)
        panel._on_provider_selected(panel.provider_list.item(0))

        assert panel.current_provider_id == "prov_1"

    def test_provider_list_panel_add_button_signal(self, qtbot, mock_provider_manager):
        """Add 버튼 시그널 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        # 시그널 캡처
        with qtbot.waitSignal(panel.add_provider_requested, timeout=1000) as blocker:
            panel.add_button.click()

        # 시그널 발생 확인
        assert len(blocker.args) == 0

    def test_provider_list_panel_delete_action(self, qtbot, mock_provider_manager):
        """Provider 삭제 액션 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        panel.load_providers()

        # 삭제 시그널 캡처
        with qtbot.waitSignal(panel.provider_deleted, timeout=1000) as blocker:
            # 커스텀 delete_provider 메서드 호출 (우클릭 메뉴 대신)
            panel._delete_provider("prov_1")

        # 시그널 발생 확인
        assert len(blocker.args) > 0
        assert blocker.args[0] == "prov_1"

    def test_provider_list_panel_refresh(self, qtbot, mock_provider_manager):
        """Provider 목록 새로고침 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        panel.load_providers()
        assert panel.provider_list.count() == 2

        new_provider = Provider(
            id="prov_3",
            name="Test Provider",
            api_url="https://test.com/v1",
            api_key=None,
            model="test-model",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_provider_manager.get_all_providers.return_value = [
            mock_provider_manager.get_all_providers()[0],
            mock_provider_manager.get_all_providers()[1],
            new_provider
        ]

        panel.load_providers()
        assert panel.provider_list.count() == 3

    def test_provider_list_panel_select_provider(self, qtbot, mock_provider_manager):
        """특정 Provider 선택 테스트"""
        from src.gui.widgets.provider_list_panel import ProviderListPanel

        panel = ProviderListPanel(mock_provider_manager)
        qtbot.addWidget(panel)

        panel.load_providers()

        with qtbot.waitSignal(panel.provider_selected, timeout=1000) as blocker:
            panel.provider_list.itemClicked.emit(panel.provider_list.item(0))

        assert len(blocker.args) > 0
        assert blocker.args[0] == "prov_1"
