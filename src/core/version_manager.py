"""
[overview]
버전 관리자

[description]
프롬프트의 버전을 관리하는 코어 로직입니다.
버전 생성, 타임라인 조회, 복구(단순 스냅샷) 기능을 제공합니다.
Plugin hook을 통해 확장 가능합니다.
"""

from pathlib import Path
from typing import Any

from src.data.models import Version
from src.data.repository import VersionRepository
from src.core.plugin_interface import TaskPlugin
from src.utils.id_generator import generate_id


class VersionManager:
    """
    [overview]
    버전 관리자 클래스

    [description]
    프롬프트의 버전 관리를 위한 핵심 비즈니스 로직을 구현합니다.
    단순 스냅샷 방식으로 버전을 저장하고 관리합니다.
    Plugin hook을 통해 새 버전 생성 및 복구 시 확장 동작을 제공합니다.
    """

    def __init__(self, db_path: Path | None = None):
        """
        VersionManager 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.version_repo: VersionRepository = VersionRepository(db_path=db_path)
        self.plugins: list[TaskPlugin] = []

    def register_plugin(self, plugin: TaskPlugin) -> None:
        """
        플러그인 등록

        Args:
            plugin: 등록할 플러그인
        """
        self.plugins.append(plugin)

    def _execute_plugins(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        등록된 플러그인 실행

        Args:
            action: 액션 타입 (create_version, restore_version)
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        context["action"] = action
        for plugin in self.plugins:
            context = plugin.execute(task_id="", context=context)
        return context

    def _get_next_version_number(self, prompt_id: str) -> int:
        """
        다음 버전 번호 계산

        Args:
            prompt_id: 프롬프트 ID

        Returns:
            다음 버전 번호
        """
        versions = self.version_repo.get_by_prompt(prompt_id)
        if not versions:
            return 1
        max_version = max(v.version_number for v in versions)
        return max_version + 1

    def create_version(self, prompt_id: str, content: str) -> Version:
        """
        새 버전 생성

        Args:
            prompt_id: 프롬프트 ID
            content: 프롬프트 내용

        Returns:
            생성된 버전
        """
        version_number = self._get_next_version_number(prompt_id)
        version = Version(
            id=generate_id(),
            prompt_id=prompt_id,
            content=content,
            version_number=version_number,
        )

        self.version_repo.create(version)

        # Plugin hook 실행
        self._execute_plugins(
            action="create_version",
            context={"version": version.model_dump(), "prompt_id": prompt_id},
        )

        return version

    def get_timeline(self, prompt_id: str) -> list[Version]:
        """
        버전 타임라인 조회

        Args:
            prompt_id: 프롬프트 ID

        Returns:
            버전 목록 (버전 번호 순서로 정렬)
        """
        versions = self.version_repo.get_by_prompt(prompt_id)
        return sorted(versions, key=lambda v: v.version_number)

    def restore_version(self, prompt_id: str, version_id: str) -> Version:
        """
        버전 복구 (단순 스냅샷 방식)

        Args:
            prompt_id: 프롬프트 ID
            version_id: 복구할 버전 ID

        Returns:
            새로 생성된 복구 버전

        Raises:
            ValueError: 버전을 찾을 수 없는 경우
        """
        target_version = self.version_repo.get(version_id)
        if target_version is None:
            raise ValueError(f"Version not found: {version_id}")

        # 복구된 버전으로 새 버전 생성
        restored_version = self.create_version(
            prompt_id=prompt_id,
            content=target_version.content,
        )

        # Plugin hook 실행
        self._execute_plugins(
            action="restore_version",
            context={
                "restored_version": restored_version.model_dump(),
                "original_version": target_version.model_dump(),
                "prompt_id": prompt_id,
            },
        )

        return restored_version

    def ensure_first_version(
        self, prompt_id: str, content: str
    ) -> Version | None:
        """
        첫 번째 버전 자동 생성

        프롬프트에 버전이 없는 경우 첫 번째 버전을 생성합니다.
        이미 버전이 있는 경우 아무 동작도 하지 않습니다.

        Args:
            prompt_id: 프롬프트 ID
            content: 프롬프트 내용

        Returns:
            생성된 버전 또는 None (이미 버전이 있는 경우)
        """
        versions = self.version_repo.get_by_prompt(prompt_id)
        if versions:
            return None

        return self.create_version(prompt_id=prompt_id, content=content)
