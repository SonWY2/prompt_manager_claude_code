"""
[overview]
UUID 기반 고유 ID 생성기

[description]
uuid4를 사용하여 고유한 ID를 생성합니다.
모든 ID는 소문자 형식으로 반환됩니다.
"""

import uuid


def generate_id() -> str:
    """
    UUID4 기반 고유 ID 생성

    Returns:
        str: 하이픈이 포함된 소문자 UUID 문자열 (예: 123e4567-e89b-12d3-a456-426614174000)
    """
    return str(uuid.uuid4()).lower()


def generate_task_id() -> str:
    """
    태스크 고유 ID 생성

    Returns:
        str: task_ 접두사가 포함된 고유 ID (예: task_123e4567-e89b-12d3-a456-426614174000)
    """
    return f"task_{generate_id()}"


def generate_execution_record_id() -> str:
    """
    실행 기록 고유 ID 생성

    Returns:
        str: exec_ 접두사가 포함된 고유 ID (예: exec_123e4567-e89b-12d3-a456-426614174000)
    """
    return f"exec_{generate_id()}"


def generate_provider_id() -> str:
    """
    Provider 고유 ID 생성

    Returns:
        str: provider_ 접두사가 포함된 고유 ID (예: provider_123e4567-e89b-12d3-a456-426614174000)
    """
    return f"provider_{generate_id()}"


def generate_prompt_id() -> str:
    """
    Prompt 고유 ID 생성

    Returns:
        str: prompt_ 접두사가 포함된 고유 ID (예: prompt_123e4567-e89b-12d3-a456-426614174000)
    """
    return f"prompt_{generate_id()}"
