"""
[overview]
LLM Service 구현

[description]
OpenAI Compatible API 호출, 메트릭 수집, 플러그인 훅을 제공합니다.
requests 모듈을 사용하여 HTTP 요청을 수행합니다.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import requests  # type: ignore[import-untyped]

from src.data.models import Provider, ExecutionRecord
from src.utils.id_generator import generate_execution_record_id


class LLMPlugin(ABC):
    """
    [overview]
    LLM 플러그인 인터페이스

    [description]
    LLM 관련 확장 동작을 위한 플러그인 인터페이스입니다.
    모든 LLM 플러그인은 이 인터페이스를 구현해야 합니다.
    """

    @abstractmethod
    def execute(self, prompt_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        플러그인 실행

        Args:
            prompt_id: 프롬프트 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        pass

    def after_call(self, prompt_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        플러그인 후처리 실행 훅

        Args:
            prompt_id: 프롬프트 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        return context

    @abstractmethod
    def get_name(self) -> str:
        """
        플러그인 이름 반환

        Returns:
            플러그인 이름
        """
        pass


class LLMService:
    """
    [overview]
    LLM Service

    [description]
    OpenAI Compatible API 호출, 메트릭 수집, 플러그인 훅을 담당합니다.
    """

    OPENAI_CHAT_COMPLETIONS_PATH = "/chat/completions"
    DEFAULT_TIMEOUT = 30
    MILLISECONDS_IN_SECOND = 1000
    RESPONSE_TIME_KEY = "response_time_seconds"
    SUCCESS_STATUS_CODE = 200

    def __init__(self, provider: Provider):
        """
        LLMService 초기화

        Args:
            provider: LLM 프로바이더 정보
        """
        self.provider = provider
        self.plugins: List[LLMPlugin] = []

    def register_plugin(self, plugin: LLMPlugin) -> None:
        """
        플러그인 등록

        Args:
            plugin: 등록할 플러그인
        """
        self.plugins.append(plugin)

    def _execute_plugins(
        self, prompt_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        등록된 플러그인 실행

        Args:
            prompt_id: 프롬프트 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        for plugin in self.plugins:
            context = plugin.execute(prompt_id, context)
        return context

    def _execute_after_call_plugins(
        self, prompt_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        등록된 플러그인의 후처리 훅 실행

        Args:
            prompt_id: 프롬프트 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        for plugin in self.plugins:
            context = plugin.after_call(prompt_id, context)
        return context

    def _normalize_api_url(self) -> str:
        """
        API URL 정규화

        Returns:
            슬래시 정규화된 API URL
        """
        return self.provider.api_url.rstrip("/")

    def _build_chat_completion_url(self) -> str:
        """
        OpenAI Chat Completion URL 생성

        Returns:
            chat/completions 요청 URL
        """
        return f"{self._normalize_api_url()}{self.OPENAI_CHAT_COMPLETIONS_PATH}"

    def _render_prompt(self, prompt: str, variables: Dict[str, Any]) -> str:
        """
        프롬프트 렌더링

        Args:
            prompt: 원본 프롬프트
            variables: 변수 딕셔너리

        Returns:
            렌더링된 프롬프트
        """
        rendered = prompt
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def _build_headers(self) -> Dict[str, str]:
        """
        요청 헤더 생성

        Returns:
            HTTP 헤더
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.provider.api_key:
            headers["Authorization"] = f"Bearer {self.provider.api_key}"
        return headers

    def _build_request_body(
        self,
        prompt: str,
        variables: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        요청 바디 생성

        Args:
            prompt: 프롬프트
            variables: 변수 딕셔너리

        Returns:
            요청 바디
        """
        rendered_prompt = self._render_prompt(prompt, variables)
        return {
            "model": self.provider.model,
            "messages": [
                {
                    "role": "user",
                    "content": rendered_prompt,
                }
            ],
        }

    def _extract_usage_metrics(
        self, response_data: Dict[str, Any]
    ) -> Dict[str, Optional[int]]:
        """
        응답에서 사용량 메트릭 추출

        Args:
            response_data: API 응답 데이터

        Returns:
            토큰 사용량 메트릭
        """
        usage = response_data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    def _extract_tokens_used(self, response_data: Dict[str, Any]) -> Optional[int]:
        """
        응답에서 토큰 사용량 추출

        Args:
            response_data: API 응답 데이터

        Returns:
            총 토큰 사용량 또는 None
        """
        usage = response_data.get("usage", {})
        return usage.get("total_tokens")

    def _extract_output(self, response_data: Dict[str, Any]) -> str:
        """
        응답에서 출력 내용 추출

        Args:
            response_data: API 응답 데이터

        Returns:
            출력 내용
        """
        choices = response_data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            return message.get("content", "")
        return ""

    def _build_metrics(
        self, execution_time_ms: int, usage_metrics: Dict[str, Optional[int]]
    ) -> Dict[str, Any]:
        """
        메트릭 조합

        Args:
            execution_time_ms: 실행 시간(ms)
            usage_metrics: usage 메트릭

        Returns:
            메트릭 딕셔너리
        """
        return {
            "execution_time_ms": execution_time_ms,
            self.RESPONSE_TIME_KEY: execution_time_ms / self.MILLISECONDS_IN_SECOND,
            "tokens_used": usage_metrics.get("total_tokens"),
            "prompt_tokens": usage_metrics.get("prompt_tokens"),
            "completion_tokens": usage_metrics.get("completion_tokens"),
        }

    def _create_execution_record(
        self,
        prompt_id: str,
        version_id: str,
        input_variables: Dict[str, Any],
        output: str,
        execution_time_ms: int,
        tokens_used: Optional[int],
    ) -> ExecutionRecord:
        """
        ExecutionRecord 생성 헬퍼

        Returns:
            실행 기록 엔티티
        """
        return ExecutionRecord(
            id=generate_execution_record_id(),
            prompt_id=prompt_id,
            version_id=version_id,
            input_variables=input_variables,
            output=output,
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
        )

    def call_llm_with_metrics(
        self,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        prompt_id: str = "",
        version_id: str = "",
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        OpenAI 호환 API 호출 및 메트릭 수집

        Args:
            prompt: 프롬프트
            variables: 변수 딕셔너리
            prompt_id: 프롬프트 ID (선택)
            version_id: 버전 ID (선택)
            model: 모델 오버라이드(선택)
            timeout_seconds: 요청 타임아웃(초)

        Returns:
            호출 결과 및 메트릭
        """
        if variables is None:
            variables = {}

        before_call_context = self._execute_plugins(
            prompt_id,
            {
                "action": "before_call",
                "prompt": prompt,
                "variables": variables,
                "prompt_id": prompt_id,
                "version_id": version_id,
            },
        )

        prompt = before_call_context.get("prompt", prompt)
        variables = before_call_context.get("variables", variables)
        prompt_id = before_call_context.get("prompt_id", prompt_id)
        version_id = before_call_context.get("version_id", version_id)

        if not isinstance(variables, dict):
            variables = {}

        start_time = time.time()
        url = self._build_chat_completion_url()
        headers = self._build_headers()
        request_body = self._build_request_body(prompt, variables)
        if model is not None:
            request_body["model"] = model

        timeout_value: float = float(self.DEFAULT_TIMEOUT)
        if timeout_seconds is not None:
            timeout_value = timeout_seconds

        response = requests.post(
            url,
            json=request_body,
            headers=headers,
            timeout=timeout_value,
        )
        response.raise_for_status()
        if response.status_code != self.SUCCESS_STATUS_CODE:
            raise RuntimeError(
                f"Unexpected LLM response status: {response.status_code}"
            )

        response_data = response.json()
        execution_time_ms = int(
            (time.time() - start_time) * self.MILLISECONDS_IN_SECOND
        )

        output = self._extract_output(response_data)
        usage_metrics = self._extract_usage_metrics(response_data)
        metrics = self._build_metrics(execution_time_ms, usage_metrics)

        after_call_context = self._execute_after_call_plugins(
            prompt_id,
            {
                "action": "after_call",
                "prompt": prompt,
                "variables": variables,
                "prompt_id": prompt_id,
                "version_id": version_id,
                "output": output,
                "metrics": metrics,
            },
        )

        output = after_call_context.get("output", output)
        metrics = after_call_context.get("metrics", metrics)
        execution_time_ms = int(metrics.get("execution_time_ms", execution_time_ms))
        usage_metrics = {
            "total_tokens": metrics.get("tokens_used"),
            "prompt_tokens": metrics.get("prompt_tokens"),
            "completion_tokens": metrics.get("completion_tokens"),
        }
        tokens_used = self._extract_tokens_used({"usage": usage_metrics})

        execution_record = self._create_execution_record(
            prompt_id=prompt_id,
            version_id=version_id,
            input_variables=variables,
            output=output,
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used,
        )

        return {
            "output": output,
            "execution_time_ms": execution_time_ms,
            "tokens_used": tokens_used,
            self.RESPONSE_TIME_KEY: metrics.get(self.RESPONSE_TIME_KEY, 0.0),
            "prompt_tokens": usage_metrics.get("prompt_tokens"),
            "completion_tokens": usage_metrics.get("completion_tokens"),
            "execution_record": execution_record,
        }

    def call_llm(
        self,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        prompt_id: str = "",
        version_id: str = "",
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        LLM API 호출

        Args:
            prompt: 프롬프트
            variables: 변수 딕셔너리
            prompt_id: 프롬프트 ID (선택)
            version_id: 버전 ID (선택)
            model: 요청 모델 오버라이드(선택)
            timeout_seconds: 요청 타임아웃(초)

        Returns:
            결과 딕셔너리 (output, execution_time_ms, tokens_used, execution_record)
        """
        return self.call_llm_with_metrics(
            prompt=prompt,
            variables=variables,
            prompt_id=prompt_id,
            version_id=version_id,
            model=model,
            timeout_seconds=timeout_seconds,
        )

    async def call_llm_async(
        self,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        prompt_id: str = "",
        version_id: str = "",
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        비동기 LLM 호출 인터페이스

        Returns:
            동기 call_llm 결과
        """
        return await asyncio.to_thread(
            self.call_llm,
            prompt,
            variables,
            prompt_id,
            version_id,
            model,
            timeout_seconds,
        )
