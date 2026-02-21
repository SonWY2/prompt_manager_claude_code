"""
[overview]
Version Manager 테스트

[description]
VersionManager의 버전 생성, 타임라인 조회, 복구, 첫 번째 버전 자동 생성,
Plugin hook 기능을 테스트합니다.
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.core.version_manager import VersionManager
from src.data.models import Prompt
from src.data.repository import PromptRepository
from src.core.plugin_interface import TaskPlugin


class MockVersionPlugin(TaskPlugin):
    """
    [overview]
    테스트용 Mock Version 플러그인

    [description]
    Plugin hook 호출을 검증하기 위한 Mock 플러그인입니다.
    """

    def __init__(self):
        self.execute_called = False
        self.last_context = {}

    def execute(self, task_id: str, context: dict) -> dict:
        """
        플러그인 실행

        Args:
            task_id: 태스크 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        self.execute_called = True
        self.last_context = context
        return context

    def get_name(self) -> str:
        """
        플러그인 이름 반환

        Returns:
            플러그인 이름
        """
        return "MockVersionPlugin"


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """
    임시 데이터베이스 경로 생성

    Args:
        tmp_path: pytest 임시 경로

    Returns:
        임시 데이터베이스 파일 경로
    """
    return tmp_path / "test_db.json"


@pytest.fixture
def version_manager(temp_db_path: Path) -> VersionManager:
    """
    VersionManager 인스턴스 생성

    Args:
        temp_db_path: 임시 데이터베이스 경로

    Returns:
        VersionManager 인스턴스
    """
    return VersionManager(db_path=temp_db_path)


@pytest.fixture
def sample_prompt(temp_db_path: Path) -> Prompt:
    """
    샘플 프롬프트 생성

    Args:
        temp_db_path: 임시 데이터베이스 경로

    Returns:
        샘플 프롬프트
    """
    prompt_repo = PromptRepository(db_path=temp_db_path)
    prompt = Prompt(
        id="prompt_001",
        task_id="task_001",
        current_version_id=None,
        system_prompt="",
        user_prompt="",
    )
    return prompt_repo.create(prompt)


class TestVersionManagerCreateVersion:
    """
    [overview]
    버전 생성 테스트

    [description]
    VersionManager의 버전 생성 기능을 테스트합니다.
    """

    def test_create_first_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        첫 번째 버전 생성 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        content = "첫 번째 프롬프트 내용"
        version = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content=content,
        )

        assert version.id is not None
        assert version.prompt_id == sample_prompt.id
        assert version.content == content
        assert version.version_number == 1
        assert isinstance(version.created_at, datetime)

    def test_create_second_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        두 번째 버전 생성 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        # 첫 번째 버전 생성
        version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="첫 번째 프롬프트 내용",
        )

        # 두 번째 버전 생성
        content = "두 번째 프롬프트 내용"
        version = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content=content,
        )

        assert version.version_number == 2
        assert version.content == content

    def test_create_version_with_custom_name(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        커스텀 버전 이름 생성 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        version = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
            version_name="Release Candidate",
        )

        assert version.version_name == "Release Candidate"
        assert version.version_number == 1

    def test_create_version_with_empty_name_becomes_none(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        빈 커스텀 이름은 None으로 정규화되는지 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        version = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
            version_name="   ",
        )

        assert version.version_name is None
        assert version.version_number == 1

    def test_create_version_with_plugin_hook(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        Plugin hook 호출 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        mock_plugin = MockVersionPlugin()
        version_manager.register_plugin(mock_plugin)

        version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
        )

        assert mock_plugin.execute_called
        assert "action" in mock_plugin.last_context
        assert mock_plugin.last_context["action"] == "create_version"
        assert "version" in mock_plugin.last_context

    def test_update_version_name(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        버전 이름 변경 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        created = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
            version_name="Initial",
        )

        updated = version_manager.update_version_name(
            version_id=created.id,
            version_name="Renamed",
        )

        assert updated is not None
        assert updated.version_name == "Renamed"
        assert updated.version_number == created.version_number

    def test_update_version_name_with_blank_raises_error(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        created = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
            version_name="Initial",
        )

        with pytest.raises(ValueError, match="Version name is required"):
            version_manager.update_version_name(
                version_id=created.id, version_name="   "
            )

    def test_update_version_name_with_duplicate_raises_error(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용 1",
            version_name="Alpha",
        )
        created = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용 2",
            version_name="Beta",
        )

        with pytest.raises(ValueError, match="Version name already exists"):
            version_manager.update_version_name(
                version_id=created.id,
                version_name="Alpha",
            )

    def test_update_version_name_nonexistent_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        존재하지 않는 버전 이름 변경 시 None 반환 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        updated = version_manager.update_version_name(
            version_id="missing-id", version_name="Renamed"
        )

        assert updated is None

    def test_auto_create_first_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        첫 번째 버전 자동 생성 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        # 첫 번째 버전 자동 생성
        version_manager.ensure_first_version(
            prompt_id=sample_prompt.id,
            content="초기 프롬프트 내용",
        )

        # 이미 첫 번째 버전이 있으면 자동 생성하지 않음
        version_manager.ensure_first_version(
            prompt_id=sample_prompt.id,
            content="다른 내용",
        )

        # 버전 목록 조회 (하나만 있어야 함)
        versions = version_manager.get_timeline(prompt_id=sample_prompt.id)
        assert len(versions) == 1
        assert versions[0].version_number == 1


class TestVersionManagerGetTimeline:
    """
    [overview]
    타임라인 조회 테스트

    [description]
    VersionManager의 타임라인 조회 기능을 테스트합니다.
    """

    def test_get_timeline_empty(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        빈 타임라인 조회 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        versions = version_manager.get_timeline(prompt_id=sample_prompt.id)
        assert versions == []

    def test_get_timeline_single_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        단일 버전 타임라인 조회 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="프롬프트 내용",
        )

        versions = version_manager.get_timeline(prompt_id=sample_prompt.id)
        assert len(versions) == 1
        assert versions[0].version_number == 1

    def test_get_timeline_multiple_versions(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        다중 버전 타임라인 조회 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        # 3개 버전 생성
        for i in range(3):
            version_manager.create_version(
                prompt_id=sample_prompt.id,
                content=f"버전 {i + 1} 내용",
            )

        versions = version_manager.get_timeline(prompt_id=sample_prompt.id)
        assert len(versions) == 3
        assert versions[0].version_number == 1
        assert versions[1].version_number == 2
        assert versions[2].version_number == 3

    def test_get_timeline_ordered_by_version_number(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        버전 번호 순서로 정렬된 타임라인 조회 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        # 버전 생성
        for i in range(5):
            version_manager.create_version(
                prompt_id=sample_prompt.id,
                content=f"버전 {i} 내용",
            )

        versions = version_manager.get_timeline(prompt_id=sample_prompt.id)
        assert len(versions) == 5

        # 버전 번호 순서 확인
        for i, version in enumerate(versions, start=1):
            assert version.version_number == i


class TestVersionManagerRestoreVersion:
    """
    [overview]
    버전 복구 테스트

    [description]
    VersionManager의 버전 복구 기능을 테스트합니다 (단순 스냅샷).
    """

    def test_restore_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        버전 복구 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        # 버전 1 생성
        original_content = "원본 프롬프트 내용"
        v1 = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content=original_content,
            version_name="Original",
        )

        # 버전 2 생성
        modified_content = "수정된 프롬프트 내용"
        version_manager.create_version(
            prompt_id=sample_prompt.id,
            content=modified_content,
        )

        # 버전 1 복구 (새 버전으로 생성)
        restored_version = version_manager.restore_version(
            prompt_id=sample_prompt.id,
            version_id=v1.id,
        )

        # 복구된 버전은 새로운 버전 번호를 가져야 함
        assert restored_version.version_number == 3
        assert restored_version.version_name == "Original"
        assert restored_version.content == original_content

    def test_restore_version_with_plugin_hook(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        복구 시 Plugin hook 호출 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        mock_plugin = MockVersionPlugin()
        version_manager.register_plugin(mock_plugin)

        # 버전 생성
        v1 = version_manager.create_version(
            prompt_id=sample_prompt.id,
            content="원본 내용",
        )

        # 버전 복구
        version_manager.restore_version(
            prompt_id=sample_prompt.id,
            version_id=v1.id,
        )

        # Plugin hook 호출 확인
        assert mock_plugin.execute_called
        assert "action" in mock_plugin.last_context
        assert mock_plugin.last_context["action"] == "restore_version"

    def test_restore_nonexistent_version(
        self, version_manager: VersionManager, sample_prompt: Prompt
    ):
        """
        존재하지 않는 버전 복구 시도 테스트

        Args:
            version_manager: VersionManager 인스턴스
            sample_prompt: 샘플 프롬프트
        """
        with pytest.raises(ValueError, match="Version not found"):
            version_manager.restore_version(
                prompt_id=sample_prompt.id,
                version_id="nonexistent_version_id",
            )
