"""
[overview]
LLM Service API 호출 테스트

[description]
LLMService의 OpenAI Compatible API 호출 및 플러그인 실행 기능을 테스트합니다.
unittest.mock을 사용하여 실제 API 호출을 모킹합니다.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.core.llm_service import LLMService, LLMPlugin
from src.data.models import Provider


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


class TestLLMServiceAPICall:
    """LLMService API 호출 테스트"""

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_success(self, mock_post):
        """LLM API 호출 성공"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="test_key",
            model="llama2"
        )
        service = LLMService(provider)

        result = service.call_llm(
            prompt="Test prompt",
            variables={"var1": "value1"}
        )

        # 결과 검증
        assert result["output"] == "Test response"
        assert result["execution_time_ms"] >= 0
        assert result["tokens_used"] == 30

        # API 호출 검증
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "http://localhost:11434/v1/chat/completions" in str(call_args[0][0])

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_with_api_key(self, mock_post):
        """API Key 포함하여 호출"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key="secret_key",
            model="llama2"
        )
        service = LLMService(provider)

        service.call_llm("Test prompt")

        # 헤더 검증
        call_kwargs = mock_post.call_args[1]
        assert "Authorization" in call_kwargs["headers"]
        assert "Bearer secret_key" in call_kwargs["headers"]["Authorization"]

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_without_api_key(self, mock_post):
        """API Key 없이 호출"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="llama2"
        )
        service = LLMService(provider)

        service.call_llm("Test prompt")

        # 헤더 검증 (Authorization 헤더 없음)
        call_kwargs = mock_post.call_args[1]
        assert "Authorization" not in call_kwargs["headers"]

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_request_body(self, mock_post):
        """요청 바디 검증"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="test_model"
        )
        service = LLMService(provider)

        service.call_llm(
            "Test prompt {{var1}}",
            variables={"var1": "value1"}
        )

        # 요청 바디 검증
        call_kwargs = mock_post.call_args[1]
        request_data = call_kwargs["json"]
        assert request_data["model"] == "test_model"
        assert request_data["messages"][0]["content"] == "Test prompt value1"

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_api_error(self, mock_post):
        """API 에러 응답 처리"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="llama2"
        )
        service = LLMService(provider)

        with pytest.raises(Exception, match="API Error"):
            service.call_llm("Test prompt")

    @patch('src.core.llm_service.requests.post')
    def test_call_llm_missing_usage_field(self, mock_post):
        """usage 필드가 없는 응답 처리"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ]
            # usage 필드 없음
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="llama2"
        )
        service = LLMService(provider)

        result = service.call_llm("Test prompt")

        assert result["output"] == "Test response"
        assert result["tokens_used"] is None


class TestLLMServicePluginExecution:
    """LLMService 플러그인 실행 테스트"""

    @patch('src.core.llm_service.requests.post')
    def test_execute_plugins_before_api_call(self, mock_post):
        """API 호출 전 플러그인 실행"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="llama2"
        )
        service = LLMService(provider)
        plugin = TestMockPlugin()

        service.register_plugin(plugin)
        service.call_llm("Test prompt", variables={"test": "value"})

        # 플러그인 실행 검증
        assert plugin.execute_called is True
        assert plugin.context_passed["action"] == "before_call"
        assert plugin.context_passed["prompt"] == "Test prompt"
        assert plugin.context_passed["variables"] == {"test": "value"}

    @patch('src.core.llm_service.requests.post')
    def test_execute_multiple_plugins(self, mock_post):
        """여러 플러그인 순차적 실행"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test response"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_post.return_value = mock_response

        provider = Provider(
            id="test_provider",
            name="Test Provider",
            api_url="http://localhost:11434/v1",
            api_key=None,
            model="llama2"
        )
        service = LLMService(provider)
        plugin1 = TestMockPlugin()
        plugin2 = TestMockPlugin()

        service.register_plugin(plugin1)
        service.register_plugin(plugin2)
        service.call_llm("Test prompt")

        # 모든 플러그인 실행 검증
        assert plugin1.execute_called is True
        assert plugin2.execute_called is True
