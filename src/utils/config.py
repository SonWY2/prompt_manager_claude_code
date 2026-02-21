"""
[overview]
프로젝트 전반에서 사용하는 상수 및 설정 값

[description]
Magic Number 방지를 위해 모든 상수를 중앙 관리합니다.
템플릿 변수 구분자, UUID 길이, 최대값 등 중요한 상수를 정의합니다.
"""

from typing import Final

# 템플릿 변수 구분자
TEMPLATE_START_DELIMITER: Final[str] = "{{"
TEMPLATE_END_DELIMITER: Final[str] = "}}"

# UUID 관련 상수
UUID_LENGTH: Final[int] = 36  # 표준 UUID4 길이 (하이픈 포함)

# 태스크 관련 상수
MAX_TASK_NAME_LENGTH: Final[int] = 100
MAX_TASK_DESCRIPTION_LENGTH: Final[int] = 500

# 버전 관련 상수
MAX_VERSION_NUMBER: Final[int] = 9999

# 프롬프트 관련 상수
MAX_PROMPT_LENGTH: Final[int] = 10000

# API 관련 상수
API_TIMEOUT_SECONDS: Final[int] = 60
MAX_RETRY_COUNT: Final[int] = 3

# 파일 경로 상수
DATABASE_FILENAME: Final[str] = "prompts.json"
DATA_DIR_NAME: Final[str] = "data"
