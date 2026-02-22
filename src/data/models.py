"""
[overview]
데이터 모델 정의

[description]
Prompt Manager의 핵심 데이터 모델들을 pydantic을 사용하여 정의합니다.
Task, Prompt, Version, ExecutionRecord, Provider 모델을 포함합니다.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator

from src.utils.config import (
    MAX_TASK_NAME_LENGTH,
    MAX_TASK_DESCRIPTION_LENGTH,
    MAX_VERSION_NUMBER,
    MAX_PROMPT_LENGTH,
    MAX_VERSION_NAME_LENGTH,
)


class Task(BaseModel):
    """
    [overview]
    태스크 모델

    [description]
    프롬프트를 그룹화하는 태스크 정보를 저장합니다.
    """

    id: str = Field(..., description="태스크 고유 ID")
    name: str = Field(..., max_length=MAX_TASK_NAME_LENGTH, description="태스크 이름")
    description: Optional[str] = Field(
        None, max_length=MAX_TASK_DESCRIPTION_LENGTH, description="태스크 설명"
    )
    is_archived: bool = Field(False, description="아카이브(숨김) 여부")
    archived_at: Optional[datetime] = Field(None, description="아카이브 일시")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 일시")


class Prompt(BaseModel):
    """
    [overview]
    프롬프트 모델

    [description]
    태스크에 속하는 프롬프트 정보를 저장합니다.
    """

    id: str = Field(..., description="프롬프트 고유 ID")
    task_id: str = Field(..., description="소속 태스크 ID")
    current_version_id: Optional[str] = Field(None, description="현재 버전 ID")
    system_prompt: str = Field(
        "", max_length=MAX_PROMPT_LENGTH, description="System Prompt 텍스트"
    )
    user_prompt: str = Field(
        "", max_length=MAX_PROMPT_LENGTH, description="User Prompt 텍스트"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 일시")


class Version(BaseModel):
    """
    [overview]
    버전 모델

    [description]
    프롬프트의 버전 정보를 저장합니다.
    """

    id: str = Field(..., description="버전 고유 ID")
    prompt_id: str = Field(..., description="소속 프롬프트 ID")
    content: str = Field(..., max_length=MAX_PROMPT_LENGTH, description="프롬프트 내용")
    version_number: int = Field(..., description="버전 번호")
    version_name: str | None = Field(
        None, max_length=MAX_VERSION_NAME_LENGTH, description="버전 표시 이름"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")

    @field_validator("version_name")
    @classmethod
    def normalize_version_name(cls, value: str | None) -> str | None:
        """버전 이름 정규화"""
        if value is None:
            return None
        normalized = value.strip()
        if normalized == "":
            return None
        return normalized

    @field_validator("version_number")
    @classmethod
    def validate_version_number(cls, v: int) -> int:
        """버전 번호 유효성 검사"""
        if v < 0:
            raise ValueError("version_number must be non-negative")
        if v > MAX_VERSION_NUMBER:
            raise ValueError(
                f"version_number must be less than or equal to {MAX_VERSION_NUMBER}"
            )
        return v


class ExecutionRecord(BaseModel):
    """
    [overview]
    실행 기록 모델

    [description]
    프롬프트 실행 결과를 저장합니다.
    """

    id: str = Field(..., description="실행 기록 고유 ID")
    prompt_id: str = Field(..., description="프롬프트 ID")
    version_id: str = Field(..., description="버전 ID")
    input_variables: Dict[str, Any] = Field(
        default_factory=dict, description="입력 변수"
    )
    output: str = Field(..., description="LLM 응답 결과")
    execution_time_ms: int = Field(..., description="실행 시간 (밀리초)")
    tokens_used: Optional[int] = Field(None, description="사용 토큰 수")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")

    @field_validator("execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: int) -> int:
        """실행 시간 유효성 검사"""
        if v < 0:
            raise ValueError("execution_time_ms must be non-negative")
        return v

    @field_validator("tokens_used")
    @classmethod
    def validate_tokens_used(cls, v: Optional[int]) -> Optional[int]:
        """사용 토큰 수 유효성 검사"""
        if v is not None and v < 0:
            raise ValueError("tokens_used must be non-negative")
        return v


class Provider(BaseModel):
    """
    [overview]
    LLM 프로바이더 모델

    [description]
    LLM API 프로바이더 설정 정보를 저장합니다.
    """

    id: Optional[str] = Field(None, description="프로바이더 고유 ID")
    name: str = Field(..., description="프로바이더 이름")
    description: Optional[str] = Field(None, description="프로바이더 설명")
    api_url: str = Field(..., description="API 엔드포인트 URL")
    api_key: Optional[str] = Field(None, description="API 키")
    model: str = Field(..., description="모델 이름")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 일시")
