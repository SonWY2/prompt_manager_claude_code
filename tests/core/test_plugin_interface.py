"""
[overview]
Plugin Interface 테스트

[description]
Plugin 인터페이스의 기능을 테스트합니다.
ABC abstractmethod, 플러그인 등록, 실행 훅 등을 검증합니다.
"""

import pytest

from src.core.plugin_interface import TaskPlugin


class MockTaskPlugin(TaskPlugin):
    """
    [overview]
    테스트용 Mock Plugin

    [description]
    TaskPlugin 인터페이스를 구현하는 테스트용 모의 클래스입니다.
    """

    def __init__(self, name: str):
        self.name = name

    def execute(self, task_id: str, context: dict) -> dict:
        """
        플러그인 실행

        Args:
            task_id: 태스크 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        context[f"{self.name}_executed"] = True
        return context

    def get_name(self) -> str:
        """
        플러그인 이름 반환

        Returns:
            플러그인 이름
        """
        return self.name


class TestTaskPlugin:
    """
    [overview]
    TaskPlugin 테스트

    [description]
    TaskPlugin 인터페이스 구현을 테스트합니다.
    """

    def test_plugin_execute(self):
        """플러그인 실행 테스트"""
        plugin = MockTaskPlugin("test_plugin")
        context = {"test": "value"}
        result = plugin.execute("task_123", context)

        assert result["test"] == "value"
        assert result["test_plugin_executed"] is True

    def test_plugin_get_name(self):
        """플러그인 이름 반환 테스트"""
        plugin = MockTaskPlugin("my_plugin")
        assert plugin.get_name() == "my_plugin"

    def test_plugin_cannot_instantiate_abstract(self):
        """추상 클래스 직접 인스턴스화 불가 테스트"""
        with pytest.raises(TypeError):
            TaskPlugin()

    def test_plugin_chain_execution(self):
        """여러 플러그인 연쇄 실행 테스트"""
        plugin1 = MockTaskPlugin("plugin1")
        plugin2 = MockTaskPlugin("plugin2")
        plugin3 = MockTaskPlugin("plugin3")

        context = {}
        context = plugin1.execute("task_123", context)
        context = plugin2.execute("task_123", context)
        context = plugin3.execute("task_123", context)

        assert context["plugin1_executed"] is True
        assert context["plugin2_executed"] is True
        assert context["plugin3_executed"] is True
