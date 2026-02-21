"""
[overview]
Plugin 인터페이스 정의

[description]
Main Logic + Plugin 패턴을 위한 플러그인 인터페이스를 정의합니다.
TaskPlugin은 Task 관련 확장 동작을 위한 추상 기본 클래스입니다.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class TaskPlugin(ABC):
    """
    [overview]
    Task 플러그인 인터페이스

    [description]
    태스크 관련 확장 동작을 위한 플러그인 인터페이스입니다.
    모든 Task 플러그인은 이 인터페이스를 구현해야 합니다.
    """

    @abstractmethod
    def execute(self, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        플러그인 실행

        Args:
            task_id: 태스크 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        플러그인 이름 반환

        Returns:
            플러그인 이름
        """
        pass
