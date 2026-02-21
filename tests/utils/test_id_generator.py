"""
[overview]
id_generator 모듈의 테스트 케이스

[description]
UUID 기반 ID 생성 기능 테스트
"""

import re


def test_generate_id_format() -> None:
    """
    ID 형식 유효성 테스트
    """
    from src.utils.id_generator import generate_id

    # UUID 형식 정규식 (예: 123e4567-e89b-12d3-a456-426614174000)
    uuid_pattern: re.Pattern[str] = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )

    # 테스트 실행 (유효한 UUID 생성)
    generated_id: str = generate_id()
    assert uuid_pattern.match(generated_id) is not None


def test_generate_id_uniqueness() -> None:
    """
    ID 중복 확인 테스트
    """
    from src.utils.id_generator import generate_id

    # 테스트 실행 (다른 ID 생성)
    id1: str = generate_id()
    id2: str = generate_id()
    assert id1 != id2


def test_generate_id_length() -> None:
    """
    ID 길이 테스트
    """
    from src.utils.id_generator import generate_id

    # UUID4 표준 길이 (하이픈 포함)
    expected_length: int = 36

    # 테스트 실행 (길이 확인)
    generated_id: str = generate_id()
    assert len(generated_id) == expected_length


def test_generate_id_consistency() -> None:
    """
    여러 ID 생성 시 일관성 테스트
    """
    from src.utils.id_generator import generate_id

    # 테스트 실행 (여러 ID 생성)
    ids: list[str] = [generate_id() for _ in range(10)]
    assert len(ids) == 10
    assert len(set(ids)) == 10  # 모두 유일해야 함


def test_generate_id_lowercase() -> None:
    """
    ID 소문자 여부 테스트
    """
    from src.utils.id_generator import generate_id

    # 테스트 실행 (소문자 확인)
    generated_id: str = generate_id()
    assert generated_id == generated_id.lower()
