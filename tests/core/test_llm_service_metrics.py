"""
[overview]
LLM Service ExecutionRecord 생성 테스트

[description]
LLMService의 ExecutionRecord 생성 및 메트릭 수집 기능을 테스트합니다.
unittest.mock을 사용하여 테스트를 수행합니다.
"""

from unittest.mock import Mock, patch
from datetime import datetime

from src.core.llm_service import LLMService
from src.data.models import Provider


class TestLLMServiceExecutionRecord:
    """LLMService ExecutionRecord 생성 테스트"""

    @patch('src.core.llm_service.requests.post')
    @patch('src.core.llm_service.generate_execution_record_id')
    def test_create_execution_record(
        self,
        mock_generate_id,
        mock_post
    ):
        """ExecutionRecord 생성"""
        mock_generate_id.return_value = "exec_123"
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

        result = service.call_llm(
            prompt="Test prompt",
            variables={"var1": "value1"},
            prompt_id="prompt_123",
            version_id="version_123"
        )

        assert result["execution_record"].id == "exec_123"
        assert result["execution_record"].prompt_id == "prompt_123"
        assert result["execution_record"].version_id == "version_123"
        assert result["execution_record"].input_variables == {"var1": "value1"}
        assert result["execution_record"].output == "Test response"
        assert result["execution_record"].execution_time_ms >= 0
        assert result["execution_record"].tokens_used == 30
        assert isinstance(result["execution_record"].created_at, datetime)

    @patch('src.core.llm_service.requests.post')
    @patch('src.core.llm_service.generate_execution_record_id')
    def test_create_execution_record_without_optional_fields(
        self,
        mock_generate_id,
        mock_post
    ):
        """선택적 필드 없이 ExecutionRecord 생성"""
        mock_generate_id.return_value = "exec_123"
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

        result = service.call_llm(prompt="Test prompt")

        # 선택적 필드 기본값 검증
        assert result["execution_record"].prompt_id == ""
        assert result["execution_record"].version_id == ""
        assert result["execution_record"].input_variables == {}
