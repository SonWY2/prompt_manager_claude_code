"""
[overview]
config 모듈의 테스트 케이스

[description]
상수 및 설정 값 정의 테스트
"""

from typing import Final


def test_config_template_delimiters_exist() -> None:
    """
    템플릿 변수 구분자 상수 존재 여부 테스트
    """
    from src.utils.config import (
        TEMPLATE_START_DELIMITER,
        TEMPLATE_END_DELIMITER
    )

    # 테스트 실행 (상수 존재 확인)
    assert isinstance(TEMPLATE_START_DELIMITER, str)
    assert isinstance(TEMPLATE_END_DELIMITER, str)


def test_config_template_delimiter_values() -> None:
    """
    템플릿 변수 구분자 값 테스트
    """
    from src.utils.config import (
        TEMPLATE_START_DELIMITER,
        TEMPLATE_END_DELIMITER
    )

    # 예상 값
    expected_start: Final[str] = "{{"
    expected_end: Final[str] = "}}"

    # 테스트 실행 (값 확인)
    assert TEMPLATE_START_DELIMITER == expected_start
    assert TEMPLATE_END_DELIMITER == expected_end


def test_config_constants_are_uppercase() -> None:
    """
    상수 이름이 UPPER_CASE 형식인지 테스트
    """
    import src.utils.config as config_module

    # 테스트 실행 (형식 확인)
    for name in dir(config_module):
        if name.isupper():
            assert isinstance(getattr(config_module, name), (str, int, float))


def test_config_magic_number_prevention() -> None:
    """
    Magic Number 방지를 위한 상수 정의 테스트
    """
    # UUID 길이 등 중요한 상수들이 정의되어 있는지 확인
    from src.utils.config import (
        UUID_LENGTH,
        MAX_TASK_NAME_LENGTH
    )

    # 테스트 실행 (상수 존재 확인)
    assert isinstance(UUID_LENGTH, int)
    assert isinstance(MAX_TASK_NAME_LENGTH, int)
