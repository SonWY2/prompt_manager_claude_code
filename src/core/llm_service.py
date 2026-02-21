"""
[overview]
LLM Service 구현

[description]
OpenAI Compatible API 호출, 메트릭 수집, 플러그인 훅을 제공합니다.
requests 모듈을 사용하여 HTTP 요청을 수행합니다.
"""

import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import requests

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

    DEFAULT_TIMEOUT = 30

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

    def _execute_plugins(self, prompt_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
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
        variables: Dict[str, Any]
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
                    "content": rendered_prompt
                }
            ]
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

    def call_llm(
        self,
        prompt: str,
        variables: Optional[Dict[str, Any]] = None,
        prompt_id: str = "",
        version_id: str = ""
    ) -> Dict[str, Any]:
        """
        LLM API 호출

        Args:
            prompt: 프롬프트
            variables: 변수 딕셔너리
            prompt_id: 프롬프트 ID (선택)
            version_id: 버전 ID (선택)

        Returns:
            결과 딕셔너리 (output, execution_time_ms, tokens_used, execution_record)
        """
        if variables is None:
            variables = {}

        # 플러그인 실행 (API 호출 전)
        context = {
            "action": "before_call",
            "prompt": prompt,
            "variables": variables,
        }
        self._execute_plugins(prompt_id, context)

        # API 호출
        start_time = time.time()
        url = f"{self.provider.api_url}/chat/completions"
        headers = self._build_headers()
        request_body = self._build_request_body(prompt, variables)

        response = requests.post(
            url,
            json=request_body,
            headers=headers,
            timeout=self.DEFAULT_TIMEOUT
        )
        response.raise_for_status()

        response_data = response.json()
        execution_time_ms = int((time.time() - start_time) * 1000)

        # 메트릭 추출
        output = self._extract_output(response_data)
        tokens_used = self._extract_tokens_used(response_data)

        # ExecutionRecord 생성
        execution_record = ExecutionRecord(
            id=generate_execution_record_id(),
            prompt_id=prompt_id,
            version_id=version_id,
            input_variables=variables,
            output=output,
            execution_time_ms=execution_time_ms,
            tokens_used=tokens_used
        )

        return {
            "output": output,
            "execution_time_ms": execution_time_ms,
            "tokens_used": tokens_used,
            "execution_record": execution_record
        }
