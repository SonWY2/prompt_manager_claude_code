"""
[overview]
Task Manager 테스트

[description]
TaskManager의 기능을 테스트합니다.
Task CRUD, Task-Prompt 연결, 플러그인 등록 및 실행을 검증합니다.
"""

import pytest
from pathlib import Path

from src.core.task_manager import TaskManager
from src.core.plugin_interface import TaskPlugin
from src.data.models import Prompt
from src.data.repository import PromptRepository


class MockTaskPlugin(TaskPlugin):
    """
    [overview]
    테스트용 Mock Plugin

    [description]
    TaskPlugin 인터페이스를 구현하는 테스트용 모의 클래스입니다.
    """

    def __init__(self, name: str):
        self.name = name
        self.execute_count = 0

    def execute(self, task_id: str, context: dict) -> dict:
        """
        플러그인 실행

        Args:
            task_id: 태스크 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        self.execute_count += 1
        context[f"{self.name}_executed"] = True
        return context

    def get_name(self) -> str:
        """
        플러그인 이름 반환

        Returns:
            플러그인 이름
        """
        return self.name


class TestTaskManager:
    """
    [overview]
    TaskManager 테스트

    [description]
    TaskManager의 CRUD 작업, Task-Prompt 연결, 플러그인 기능을 테스트합니다.
    """

    @pytest.fixture
    def temp_db_path(self, tmp_path: Path) -> Path:
        """
        임시 데이터베이스 경로 fixture

        Args:
            tmp_path: pytest tmp_path fixture

        Returns:
            임시 데이터베이스 파일 경로
        """
        return tmp_path / "test_db.json"

    @pytest.fixture
    def task_manager(self, temp_db_path: Path) -> TaskManager:
        """
        TaskManager fixture

        Args:
            temp_db_path: 임시 데이터베이스 경로

        Returns:
            TaskManager 인스턴스
        """
        return TaskManager(db_path=temp_db_path)

    def test_create_task(self, task_manager: TaskManager):
        """태스크 생성 테스트"""
        task = task_manager.create_task("테스트 태스크", "테스트 설명")

        assert task.name == "테스트 태스크"
        assert task.description == "테스트 설명"
        assert task.id is not None
        assert len(task.id) > 0

    def test_get_task(self, task_manager: TaskManager):
        """태스크 조회 테스트"""
        created_task = task_manager.create_task("조회 태스크", "조회 설명")
        retrieved_task = task_manager.get_task(created_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.name == created_task.name

    def test_get_task_not_found(self, task_manager: TaskManager):
        """존재하지 않는 태스크 조회 테스트"""
        task = task_manager.get_task("non_existent_id")
        assert task is None

    def test_get_all_tasks(self, task_manager: TaskManager):
        """모든 태스크 조회 테스트"""
        task_manager.create_task("태스크 1", "설명 1")
        task_manager.create_task("태스크 2", "설명 2")
        task_manager.create_task("태스크 3", "설명 3")

        tasks = task_manager.get_all_tasks()

        assert len(tasks) == 3

    def test_update_task(self, task_manager: TaskManager):
        """태스크 수정 테스트"""
        task = task_manager.create_task("원본 태스크", "원본 설명")

        updated_task = task_manager.update_task(
            task.id,
            name="수정된 태스크",
            description="수정된 설명"
        )

        assert updated_task is not None
        assert updated_task.name == "수정된 태스크"
        assert updated_task.description == "수정된 설명"
        assert updated_task.id == task.id

    def test_update_task_not_found(self, task_manager: TaskManager):
        """존재하지 않는 태스크 수정 테스트"""
        result = task_manager.update_task(
            "non_existent_id",
            name="이름",
            description="설명"
        )
        assert result is None

    def test_delete_task(self, task_manager: TaskManager):
        """태스크 삭제 테스트"""
        task = task_manager.create_task("삭제 태스크", "삭제 설명")

        success = task_manager.delete_task(task.id)

        assert success is True
        assert task_manager.get_task(task.id) is None

    def test_delete_task_not_found(self, task_manager: TaskManager):
        """존재하지 않는 태스크 삭제 테스트"""
        success = task_manager.delete_task("non_existent_id")
        assert success is False

    def test_register_plugin(self, task_manager: TaskManager):
        """플러그인 등록 테스트"""
        plugin = MockTaskPlugin("test_plugin")

        task_manager.register_plugin(plugin)

        assert len(task_manager.plugins) == 1
        assert task_manager.plugins[0].get_name() == "test_plugin"

    def test_execute_plugins_on_task(self, task_manager: TaskManager):
        """태스크에서 플러그인 실행 테스트"""
        task = task_manager.create_task("플러그인 태스크", "설명")
        plugin1 = MockTaskPlugin("plugin1")
        plugin2 = MockTaskPlugin("plugin2")

        task_manager.register_plugin(plugin1)
        task_manager.register_plugin(plugin2)

        context = {"initial": "value"}
        result = task_manager._execute_plugins(task.id, context)

        assert result["initial"] == "value"
        assert result["plugin1_executed"] is True
        assert result["plugin2_executed"] is True
        assert plugin1.execute_count == 1
        assert plugin2.execute_count == 1

    def test_get_task_prompts(self, task_manager: TaskManager, temp_db_path: Path):
        """태스크별 프롬프트 조회 테스트"""
        task = task_manager.create_task("프롬프트 태스크", "설명")

        # 직접 PromptRepository를 사용하여 프롬프트 생성
        prompt_repo = PromptRepository(temp_db_path)
        prompt1 = Prompt(
            id="prompt_1",
            task_id=task.id,
            current_version_id=None
        )
        prompt2 = Prompt(
            id="prompt_2",
            task_id=task.id,
            current_version_id=None
        )
        prompt_repo.create(prompt1)
        prompt_repo.create(prompt2)

        # 다른 태스크의 프롬프트 생성
        other_task = task_manager.create_task("다른 태스크", "설명")
        other_prompt = Prompt(
            id="prompt_3",
            task_id=other_task.id,
            current_version_id=None
        )
        prompt_repo.create(other_prompt)

        prompts = task_manager.get_task_prompts(task.id)

        assert len(prompts) == 2
        assert any(p.id == "prompt_1" for p in prompts)
        assert any(p.id == "prompt_2" for p in prompts)

    def test_get_task_prompts_empty(self, task_manager: TaskManager):
        """프롬프트가 없는 태스크 조회 테스트"""
        task = task_manager.create_task("빈 태스크", "설명")
        prompts = task_manager.get_task_prompts(task.id)

        assert len(prompts) == 0
