"""
[overview]
LLM Service 초기화 및 플러그인 관리 테스트

[description]
LLMService의 초기화, 플러그인 등록 및 관리 기능을 테스트합니다.
unittest.mock을 사용하여 테스트를 수행합니다.
"""

import pytest
from typing import Dict, Any

from src.core.llm_service import LLMService, LLMPlugin
from src.data.models import Provider


class TestLLMPlugin:
    """LLMPlugin 인터페이스 테스트"""

    def test_llm_plugin_interface_cannot_instantiate(self):
        """LLMPlugin 인터페이스는 직접 인스턴스화할 수 없음"""
        with pytest.raises(TypeError):
            LLMPlugin()


class TestMockPlugin(LLMPlugin):
    """테스트용 Mock 플러그인 구현"""

    def __init__(self):
        self.execute_called = False
        self.context_passed = None

    def execute(self, prompt_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        self.execute_called = True
        self.context_passed = context
        return context

    def get_name(self) -> str:
        return "MockPlugin"


class TestLLMServiceInit:
    """LLMService 초기화 테스트"""

    def test_init_with_provider(self):
        """Provider로 초기화"""
        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="test_key",
            model="llama2"
        )
        service = LLMService(provider)
        assert service.provider == provider

    def test_init_creates_empty_plugins_list(self):
        """초기화 시 빈 플러그인 리스트 생성"""
        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="test_key",
            model="llama2"
        )
        service = LLMService(provider)
        assert service.plugins == []


class TestLLMServicePluginManagement:
    """LLMService 플러그인 관리 테스트"""

    def test_register_plugin(self):
        """플러그인 등록"""
        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="test_key",
            model="llama2"
        )
        service = LLMService(provider)
        plugin = TestMockPlugin()

        service.register_plugin(plugin)

        assert len(service.plugins) == 1
        assert service.plugins[0] == plugin

    def test_register_multiple_plugins(self):
        """여러 플러그인 등록"""
        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="test_key",
            model="llama2"
        )
        service = LLMService(provider)
        plugin1 = TestMockPlugin()
        plugin2 = TestMockPlugin()

        service.register_plugin(plugin1)
        service.register_plugin(plugin2)

        assert len(service.plugins) == 2
        assert service.plugins[0] == plugin1
        assert service.plugins[1] == plugin2
