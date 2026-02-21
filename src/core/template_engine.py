"""
[overview]
템플릿 엔진

[description]
{{변수명}} 형식의 템플릿 변수를 파싱하고 렌더링합니다.
Python string.Template을 확장하여 {{variable}} 형식을 지원합니다.
"""

import re
from string import Template
from typing import Dict, List


class TemplateEngine:
    """
    [overview]
    템플릿 엔진 클래스

    [description]
    {{variable}} 형식의 템플릿 변수를 지원하는 템플릿 엔진입니다.
    Python string.Template을 확장하여 구현했습니다.
    $variable, ${variable}, {{variable}} 형식을 모두 지원합니다.
    """

    def __init__(self, template: str):
        """
        TemplateEngine 초기화

        Args:
            template: 템플릿 문자열
        """
        self.template: str = template

    def _convert_to_python_template(self) -> str:
        """
        {{variable}} 형식을 ${variable} 형식으로 변환

        Returns:
            Python string.Template 호환 템플릿
        """
        # {{var}}을 ${var}로 변환
        # 정규 표현식: {{\s*([^}]+)\s*}}
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        python_template = re.sub(pattern, r'${\1}', self.template)
        return python_template

    def render(self, variables: Dict[str, str]) -> str:
        """
        템플릿 렌더링

        Args:
            variables: 변수 딕셔너리

        Returns:
            렌더링된 문자열
        """
        python_template = self._convert_to_python_template()
        template = Template(python_template)
        return template.safe_substitute(variables)

    def parse_variables(self) -> List[str]:
        """
        템플릿에서 변수 추출

        Returns:
            변수 이름 목록 (중복 제거)
        """
        # {{var}} 형식 변수 추출
        pattern = r'\{\{\s*([^}]+)\s*\}\}'
        variables = re.findall(pattern, self.template)

        # 중복 제거
        unique_variables = list(dict.fromkeys(variables))

        return unique_variables
