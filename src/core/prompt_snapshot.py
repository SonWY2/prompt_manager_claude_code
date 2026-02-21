"""
[overview]
프롬프트 스냅샷 직렬화

[description]
System/User 프롬프트를 버전 저장용 단일 문자열로 직렬화/역직렬화합니다.
Version.content에 저장되는 포맷을 한 곳에서 관리합니다.
"""

from __future__ import annotations

import json
from typing import Final


PROMPT_SNAPSHOT_SCHEMA_VERSION: Final[int] = 1


def serialize_prompt_snapshot(system_prompt: str, user_prompt: str) -> str:
    payload = {
        "schema_version": PROMPT_SNAPSHOT_SCHEMA_VERSION,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }
    return json.dumps(payload, ensure_ascii=False)


def deserialize_prompt_snapshot(snapshot: str) -> tuple[str, str]:
    try:
        payload = json.loads(snapshot)
    except json.JSONDecodeError:
        return "", snapshot

    if not isinstance(payload, dict):
        return "", snapshot

    system_prompt = payload.get("system_prompt", "")
    user_prompt = payload.get("user_prompt", "")

    if not isinstance(system_prompt, str) or not isinstance(user_prompt, str):
        return "", snapshot

    return system_prompt, user_prompt
