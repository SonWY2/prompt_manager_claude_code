"""
[overview]
Template Engine 테스트

[description]
TemplateEngine의 {{변수명}} 형식 파싱 및 렌더링 기능을 테스트합니다.
Python string.Template 확장 기능을 테스트합니다.
"""


from src.core.template_engine import TemplateEngine


class TestTemplateEngineRender:
    """
    [overview]
    템플릿 렌더링 테스트

    [description]
    TemplateEngine의 렌더링 기능을 테스트합니다.
    """

    def test_render_single_variable(self):
        """
        단일 변수 렌더링 테스트
        """
        template = "안녕하세요, {{name}}님"
        engine = TemplateEngine(template)
        result = engine.render({"name": "홍길동"})
        assert result == "안녕하세요, 홍길동님"

    def test_render_multiple_variables(self):
        """
        다중 변수 렌더링 테스트
        """
        template = "{{name}}님은 {{age}}살입니다."
        engine = TemplateEngine(template)
        result = engine.render({"name": "철수", "age": "25"})
        assert result == "철수님은 25살입니다."

    def test_render_no_variables(self):
        """
        변수 없는 템플릿 렌더링 테스트
        """
        template = "변수가 없는 템플릿입니다."
        engine = TemplateEngine(template)
        result = engine.render({})
        assert result == "변수가 없는 템플릿입니다."

    def test_render_empty_variable_value(self):
        """
        빈 변수 값 렌더링 테스트
        """
        template = "안녕하세요, {{name}}님"
        engine = TemplateEngine(template)
        result = engine.render({"name": ""})
        assert result == "안녕하세요, 님"

    def test_render_duplicate_variables(self):
        """
        중복 변수 렌더링 테스트
        """
        template = "{{name}}님과 {{name}}님은 친구입니다."
        engine = TemplateEngine(template)
        result = engine.render({"name": "영희"})
        assert result == "영희님과 영희님은 친구입니다."

    def test_render_variable_with_special_chars(self):
        """
        특수 문자 포함 변수 값 렌더링 테스트
        """
        template = "이메일: {{email}}"
        engine = TemplateEngine(template)
        result = engine.render({"email": "test@example.com"})
        assert result == "이메일: test@example.com"

    def test_render_variable_with_numbers(self):
        """
        숫자 포함 변수 값 렌더링 테스트
        """
        template = "가격은 {{price}}원입니다."
        engine = TemplateEngine(template)
        result = engine.render({"price": "1000"})
        assert result == "가격은 1000원입니다."

    def test_render_missing_variable(self):
        """
        누락된 변수 렌더링 테스트

        기본 string.Template 동작: 변수가 없으면 그대로 유지
        """
        template = "안녕하세요, {{name}}님"
        engine = TemplateEngine(template)
        result = engine.render({})
        assert "{{name}}" in result or "$name" in result or "${name}" in result

    def test_render_multiline_template(self):
        """
        멀티라인 템플릿 렌더링 테스트
        """
        template = """안녕하세요, {{name}}님.
직업은 {{job}}입니다.
만나서 반갑습니다."""
        engine = TemplateEngine(template)
        result = engine.render({"name": "민수", "job": "개발자"})
        expected = """안녕하세요, 민수님.
직업은 개발자입니다.
만나서 반갑습니다."""
        assert result == expected

    def test_render_variable_with_korean(self):
        """
        한글 변수 값 렌더링 테스트
        """
        template = "이름: {{name}}"
        engine = TemplateEngine(template)
        result = engine.render({"name": "김철수"})
        assert result == "이름: 김철수"


class TestTemplateEngineParse:
    """
    [overview]
    템플릿 파싱 테스트

    [description]
    TemplateEngine의 변수 추출 기능을 테스트합니다.
    """

    def test_parse_single_variable(self):
        """
        단일 변수 추출 테스트
        """
        template = "안녕하세요, {{name}}님"
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert variables == ["name"]

    def test_parse_multiple_variables(self):
        """
        다중 변수 추출 테스트
        """
        template = "{{name}}님은 {{age}}살이고 {{city}}에 살고 있습니다."
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert set(variables) == {"name", "age", "city"}

    def test_parse_no_variables(self):
        """
        변수 없는 템플릿 추출 테스트
        """
        template = "변수가 없는 템플릿입니다."
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert variables == []

    def test_parse_duplicate_variables(self):
        """
        중복 변수 추출 테스트 (중복 제거)
        """
        template = "{{name}}님과 {{name}}님은 친구입니다."
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert variables == ["name"]

    def test_parse_variable_with_numbers(self):
        """
        숫자 포함 변수 추출 테스트
        """
        template = "{{var1}}과 {{var2}}는 다릅니다."
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert set(variables) == {"var1", "var2"}

    def test_parse_variable_with_underscores(self):
        """
        언더스코어 포함 변수 추출 테스트
        """
        template = "{{first_name}} {{last_name}}"
        engine = TemplateEngine(template)
        variables = engine.parse_variables()
        assert set(variables) == {"first_name", "last_name"}


class TestTemplateEngineStringTemplateExtension:
    """
    [overview]
    Python string.Template 확장 테스트

    [description]
    Python string.Template 기본 기능과 확장 기능을 테스트합니다.
    """

    def test_standard_dollar_syntax(self):
        """
        기본 $var 형식 렌더링 테스트
        """
        template = "안녕하세요, $name님"
        engine = TemplateEngine(template)
        result = engine.render({"name": "길동"})
        assert result == "안녕하세요, 길동님"

    def test_standard_brace_syntax(self):
        """
        기본 ${var} 형식 렌더링 테스트
        """
        template = "안녕하세요, ${name}님"
        engine = TemplateEngine(template)
        result = engine.render({"name": "순이"})
        assert result == "안녕하세요, 순이님"

    def test_mixed_syntax(self):
        """
        혼합 구문 렌더링 테스트 ({{var}}, $var, ${var})
        """
        template = "{{name}}님은 $age살이고, ${city}에 삽니다."
        engine = TemplateEngine(template)
        result = engine.render({"name": "철수", "age": "30", "city": "서울"})
        assert result == "철수님은 30살이고, 서울에 삽니다."

    def test_escape_dollar(self):
        """
        $ 이스케이프 처리 테스트
        """
        template = "가격은 $$100입니다."
        engine = TemplateEngine(template)
        result = engine.render({})
        assert result == "가격은 $100입니다."

    def test_complex_template(self):
        """
        복잡한 템플릿 렌더링 테스트
        """
        template = """
        시스템: {{system}}
        사용자: {{user}}
        프롬프트: {{prompt}}
        """
        engine = TemplateEngine(template)
        result = engine.render({
            "system": "You are a helpful assistant.",
            "user": "John",
            "prompt": "Hello, how are you?"
        })
        expected = """
        시스템: You are a helpful assistant.
        사용자: John
        프롬프트: Hello, how are you?
        """
        assert result == expected

    def test_whitespace_preservation(self):
        """
        공백 보존 테스트
        """
        template = "  {{name}}  "
        engine = TemplateEngine(template)
        result = engine.render({"name": "테스트"})
        assert result == "  테스트  "
