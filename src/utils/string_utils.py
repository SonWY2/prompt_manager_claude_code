"""
[overview]
문자열 처리 유틸리티

[description]
{{변수명}} 형식의 템플릿 변수 파싱 기능을 제공합니다.
"""

import re

from src.utils.config import (
    TEMPLATE_START_DELIMITER,
    TEMPLATE_END_DELIMITER
)


def extract_variables(text: str) -> list[str]:
    """
    텍스트에서 {{변수명}} 형식의 변수명 추출

    Args:
        text: 변수가 포함된 텍스트

    Returns:
        list[str]: 추출된 변수명 리스트 (중복 제거됨, 순서 보존)
    """
    # 정규식 패턴: {{변수명}} 형식만 매칭
    # 후방 탐색(?<!{)과 전방 탐색(?!)을 사용하여 중첩된 괄호 방지
    pattern: re.Pattern[str] = re.compile(
        r'(?<!{)' + re.escape(TEMPLATE_START_DELIMITER) + r'(?!{' + r')([^}]+)' + re.escape(TEMPLATE_END_DELIMITER)
    )

    # 모든 매칭 찾기
    matches: list[str] = pattern.findall(text)

    # 중복 제거하면서 순서 보존
    seen: set[str] = set()
    result: list[str] = []
    for var in matches:
        if var not in seen:
            seen.add(var)
            result.append(var)

    return result
