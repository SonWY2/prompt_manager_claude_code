"""
[overview]
run_prompt_with_viewer 테스트

[description]
PromptEditor와 ResultViewer를 사용하지 않는 순수 의존성 대체 객체로
run_prompt_with_viewer의 경로 분기와 결과 처리를 검증합니다.
"""

from typing import Any, Dict, List

import requests

from src.gui import prompt_runner


class _FakePromptEditor:
    def __init__(self, system_prompt: str, user_prompt: str, variables: Dict[str, str]):
        self._system_prompt = system_prompt
        self._user_prompt = user_prompt
        self._variables = variables

    def get_system_prompt(self) -> str:
        return self._system_prompt

    def get_user_prompt(self) -> str:
        return self._user_prompt

    def get_variable_values(self) -> Dict[str, str]:
        return self._variables


class _FakeResultViewer:
    def __init__(self, provider_id: str | None = None):
        self.provider_id = provider_id
        self.loading_states: List[bool] = []
        self.errors: List[str] = []
        self.results: List[str] = []
        self.metrics: List[Dict[str, Any]] = []
        self.histories: List[tuple[str, Dict[str, Any]]] = []

    def set_loading(self, loading: bool) -> None:
        self.loading_states.append(loading)

    def get_selected_provider_id(self) -> str | None:
        return self.provider_id

    def display_error(self, error: str) -> None:
        self.errors.append(error)

    def display_result(self, result: str) -> None:
        self.results.append(result)

    def set_metrics(
        self,
        latency: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        self.metrics.append(
            {
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            }
        )

    def add_to_history(self, result: str, **kwargs: Any) -> None:
        self.histories.append((result, kwargs))


class _FakeProvider:
    def __init__(self, model: str = "llama2") -> None:
        self.model = model


class _FakeProviderManager:
    def __init__(self, provider: _FakeProvider | None) -> None:
        self._provider = provider
        self.get_provider_calls: List[str] = []

    def get_provider(self, provider_id: str) -> _FakeProvider | None:
        self.get_provider_calls.append(provider_id)
        return self._provider


class _FakeLLMService:
    def __init__(self, provider: _FakeProvider):
        self.provider = provider
        self.call_prompts: List[str] = []

    def call_llm(self, prompt: str):
        self.call_prompts.append(prompt)
        return {
            "output": "done",
            "execution_time_ms": 500,
            "tokens_used": 12,
        }


def test_run_prompt_with_viewer_shows_error_when_prompt_is_empty() -> None:
    provider_manager = _FakeProviderManager(_FakeProvider())
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("", "", {})

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="Test Model",
    )

    assert result_viewer.errors == ["Prompt is empty"]
    assert result_viewer.loading_states == []
    assert len(provider_manager.get_provider_calls) == 0


def test_run_prompt_with_viewer_shows_error_when_provider_missing(monkeypatch) -> None:
    provider_manager = _FakeProviderManager(None)
    result_viewer = _FakeResultViewer(provider_id=None)
    prompt_editor = _FakePromptEditor("system", "user", {})

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="Test Model",
    )

    assert result_viewer.errors == [
        "No provider selected. Configure and select a provider first."
    ]
    assert result_viewer.loading_states == [True, False]
    assert len(provider_manager.get_provider_calls) == 0


def test_run_prompt_with_viewer_shows_error_when_provider_not_found(
    monkeypatch,
) -> None:
    provider_manager = _FakeProviderManager(None)
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="Test Model",
    )

    assert result_viewer.errors == ["Selected provider not found"]
    assert result_viewer.loading_states == [True, False]
    assert provider_manager.get_provider_calls == ["provider_1"]
    assert result_viewer.results == []


def test_run_prompt_with_viewer_success_calls_llm_and_records_result(
    monkeypatch,
) -> None:
    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor(
        "Hello {{name}}",
        "Ask {{target}}",
        {"name": "Alice", "target": "world"},
    )

    monkeypatch.setattr(prompt_runner, "LLMService", _FakeLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert result_viewer.results == ["done"]
    assert len(result_viewer.metrics) == 1
    assert result_viewer.metrics[0]["latency"] == 0.5
    assert result_viewer.metrics[0]["input_tokens"] == 4
    assert result_viewer.metrics[0]["output_tokens"] == 12
    assert len(result_viewer.histories) == 1
    assert result_viewer.histories[0][0] == "done"
    assert result_viewer.histories[0][1]["model"] == "gpt-4o"
    assert result_viewer.loading_states == [True, False]
    assert result_viewer.errors == []


def test_run_prompt_with_viewer_shows_request_error(monkeypatch) -> None:
    class _ErrorLLMService(_FakeLLMService):
        def call_llm(self, prompt: str):
            raise requests.exceptions.RequestException("network failed")

    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    monkeypatch.setattr(prompt_runner, "LLMService", _ErrorLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert len(result_viewer.errors) == 1
    assert result_viewer.errors[0] == "LLM request failed: network failed"
    assert result_viewer.loading_states == [True, False]
    assert result_viewer.results == []


def test_run_prompt_with_viewer_shows_invalid_llm_response_error(monkeypatch) -> None:
    class _ErrorLLMService(_FakeLLMService):
        def call_llm(self, prompt: str):
            raise ValueError("invalid response")

    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    monkeypatch.setattr(prompt_runner, "LLMService", _ErrorLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert result_viewer.errors == ["Invalid LLM response: invalid response"]
    assert result_viewer.loading_states == [True, False]


def test_run_prompt_with_viewer_shows_execution_error(monkeypatch) -> None:
    class _ErrorLLMService(_FakeLLMService):
        def call_llm(self, prompt: str):
            raise RuntimeError("unexpected runtime")

    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    monkeypatch.setattr(prompt_runner, "LLMService", _ErrorLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert result_viewer.errors == ["Execution failed: unexpected runtime"]
    assert result_viewer.loading_states == [True, False]
    assert result_viewer.results == []


def test_run_prompt_with_viewer_shows_missing_field_error(monkeypatch) -> None:
    class _ErrorLLMService(_FakeLLMService):
        def call_llm(self, prompt: str):
            raise KeyError("missing_field")

    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    monkeypatch.setattr(prompt_runner, "LLMService", _ErrorLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert result_viewer.errors == ["Response missing field: 'missing_field'"]
    assert result_viewer.loading_states == [True, False]
    assert result_viewer.results == []


def test_run_prompt_with_viewer_shows_type_error(monkeypatch) -> None:
    class _ErrorLLMService(_FakeLLMService):
        def call_llm(self, prompt: str):
            raise TypeError("bad type")

    provider_manager = _FakeProviderManager(_FakeProvider("gpt-4o"))
    result_viewer = _FakeResultViewer(provider_id="provider_1")
    prompt_editor = _FakePromptEditor("system", "user", {})

    monkeypatch.setattr(prompt_runner, "LLMService", _ErrorLLMService)

    prompt_runner.run_prompt_with_viewer(
        provider_manager=provider_manager,
        result_viewer=result_viewer,
        prompt_editor=prompt_editor,
        model="gpt-4o",
    )

    assert result_viewer.errors == ["bad type"]
    assert result_viewer.loading_states == [True, False]
    assert result_viewer.results == []
