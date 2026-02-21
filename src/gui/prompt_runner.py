"""
[overview]
프롬프트 실행 플로우

[description]
PromptEditor의 내용을 TemplateEngine으로 렌더링하고 LLMService를 호출해 ResultViewer에 표시합니다.
MainWindow에서 실행 관련 로직을 분리하기 위한 모듈입니다.
"""

from __future__ import annotations

import requests  # type: ignore[import-untyped]

from src.core.llm_service import LLMService
from src.core.provider_manager import ProviderManager
from src.core.template_engine import TemplateEngine
from src.gui.widgets.prompt_editor import PromptEditor
from src.gui.widgets.result_viewer import ResultViewer


def run_prompt_with_viewer(
    provider_manager: ProviderManager,
    result_viewer: ResultViewer,
    prompt_editor: PromptEditor,
    model: str,
) -> None:
    system_prompt = prompt_editor.get_system_prompt()
    user_prompt = prompt_editor.get_user_prompt()
    template_variables = prompt_editor.get_variable_values()

    if not system_prompt and not user_prompt:
        result_viewer.display_error("Prompt is empty")
        return

    result_viewer.set_loading(True)
    try:
        provider_id = result_viewer.get_selected_provider_id()
        if provider_id is None:
            result_viewer.display_error(
                "No provider selected. Configure and select a provider first."
            )
            return

        provider = provider_manager.get_provider(provider_id)
        if provider is None:
            result_viewer.display_error("Selected provider not found")
            return

        llm_service = LLMService(provider)
        rendered_system_prompt = TemplateEngine(system_prompt).render(
            template_variables
        )
        rendered_user_prompt = TemplateEngine(user_prompt).render(template_variables)
        rendered_prompt = (
            f"System Prompt:\n{rendered_system_prompt}\n\n"
            f"User Prompt:\n{rendered_user_prompt}"
        )
        result = llm_service.call_llm(rendered_prompt)

        output = str(result.get("output", ""))
        execution_time_ms = int(result.get("execution_time_ms", 0))
        tokens_used = result.get("tokens_used")

        result_viewer.display_result(output)
        latency_seconds = execution_time_ms / 1000
        input_tokens = len(rendered_system_prompt.split()) + len(
            rendered_user_prompt.split()
        )
        output_tokens = int(tokens_used or 0)

        result_viewer.set_metrics(
            latency=latency_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=0.0,
        )
        result_viewer.add_to_history(
            output,
            model=model,
            latency=latency_seconds,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=0.0,
        )
    except requests.exceptions.RequestException as e:
        result_viewer.display_error(f"LLM request failed: {str(e)}")
    except ValueError as e:
        result_viewer.display_error(f"Invalid LLM response: {str(e)}")
    except RuntimeError as e:
        result_viewer.display_error(f"Execution failed: {str(e)}")
    except KeyError as e:
        result_viewer.display_error(f"Response missing field: {str(e)}")
    except TypeError as e:
        result_viewer.display_error(str(e))
    finally:
        result_viewer.set_loading(False)
