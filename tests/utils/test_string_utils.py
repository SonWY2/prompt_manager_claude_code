"""
[overview]
string_utils 모듈의 테스트 케이스

[description]
{{변수명}} 형식의 템플릿 변수 파싱 기능 테스트
"""


def test_extract_variables_no_variables() -> None:
    """
    변수가 없는 텍스트 처리 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "변수가 없는 일반 텍스트입니다."

    # 예상 결과
    expected: list[str] = []

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_single_variable() -> None:
    """
    단일 변수 추출 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "안녕하세요 {{name}}님"

    # 예상 결과
    expected: list[str] = ["name"]

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_multiple_variables() -> None:
    """
    여러 변수 추출 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "{{name}}님, {{age}}살 {{city}}에 오신 것을 환영합니다."

    # 예상 결과
    expected: list[str] = ["name", "age", "city"]

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_duplicate_variables() -> None:
    """
    중복 변수 추출 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "{{name}}님의 나이는 {{age}}살입니다. {{name}}님의 키는 {{height}}cm입니다."

    # 예상 결과 (중복 제거)
    expected: list[str] = ["name", "age", "height"]

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_korean_variable_name() -> None:
    """
    한글 변수명 추출 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "이름: {{이름}}, 나이: {{나이}}"

    # 예상 결과
    expected: list[str] = ["이름", "나이"]

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_empty_text() -> None:
    """
    빈 텍스트 처리 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = ""

    # 예상 결과
    expected: list[str] = []

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected


def test_extract_variables_incomplete_braces() -> None:
    """
    불완전한 괄호 처리 테스트
    """
    from src.utils.string_utils import extract_variables

    # 테스트 데이터
    text: str = "{{name}님} {{{age}}님"

    # 예상 결과 (완전한 형식만 추출)
    expected: list[str] = []

    # 테스트 실행 (예상 결과 반환)
    result: list[str] = extract_variables(text)
    assert result == expected
