"""
[overview]
Python logging 유틸리티 모듈

[description]
구조화된 JSON 형식 로깅을 위한 유틸리티 모듈입니다.
- timestamp, level, service, request_id, message, data 필드 포함
- DEBUG, INFO, WARNING, ERROR 로그 레벨 지원
- 로그 파일로 출력 (파일/표준출력 선택 가능)
"""

from __future__ import annotations

import logging

LOGGER_NAME = "prompt_manager"
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _create_logger() -> logging.Logger:
    logger_instance = logging.getLogger(LOGGER_NAME)

    if logger_instance.handlers:
        return logger_instance

    logger_instance.setLevel(DEFAULT_LOG_LEVEL)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
    logger_instance.addHandler(stream_handler)

    return logger_instance


logger = _create_logger()
