"""
[overview]
Task Manager 구현

[description]
태스크 CRUD 작업, Task-Prompt 연결 관리, 플러그인 실행 훅을 제공합니다.
Repository를 통해 데이터베이스에 접근하며, 플러그인 패턴을 지원합니다.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from src.core.plugin_interface import TaskPlugin
from src.data.models import Task, Prompt
from src.data.repository import TaskRepository, PromptRepository
from src.utils.id_generator import generate_prompt_id, generate_task_id


class TaskManager:
    """
    [overview]
    Task Manager

    [description]
    태스크 CRUD 작업, Task-Prompt 연결 관리, 플러그인 실행을 담당합니다.
    Repository 패턴을 통해 데이터베이스에 접근합니다.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        TaskManager 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.task_repository = TaskRepository(db_path)
        self.prompt_repository = PromptRepository(db_path)
        self.plugins: List[TaskPlugin] = []

    def register_plugin(self, plugin: TaskPlugin) -> None:
        """
        플러그인 등록

        Args:
            plugin: 등록할 플러그인
        """
        self.plugins.append(plugin)

    def _execute_plugins(self, task_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        등록된 플러그인 실행

        Args:
            task_id: 태스크 ID
            context: 실행 컨텍스트

        Returns:
            수정된 컨텍스트
        """
        for plugin in self.plugins:
            context = plugin.execute(task_id, context)
        return context

    def create_task(self, name: str, description: Optional[str] = None) -> Task:
        """
        태스크 생성

        Args:
            name: 태스크 이름
            description: 태스크 설명

        Returns:
            생성된 태스크
        """
        task = Task(
            id=generate_task_id(),
            name=name,
            description=description,
            is_archived=False,
            archived_at=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # 플러그인 실행 (태스크 생성 훅)
        context = {"action": "create", "task": task}
        self._execute_plugins(task.id, context)

        return self.task_repository.create(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        태스크 조회

        Args:
            task_id: 태스크 ID

        Returns:
            조회된 태스크 또는 None
        """
        return self.task_repository.get(task_id)

    def get_all_tasks(self, include_archived: bool = False) -> List[Task]:
        """
        모든 태스크 조회

        Returns:
            태스크 목록
        """
        tasks = self.task_repository.get_all()
        if include_archived:
            return tasks
        return [t for t in tasks if not t.is_archived]

    def rename_task(self, task_id: str, new_name: str) -> Optional[Task]:
        name = new_name.strip()
        if not name:
            return None
        return self.update_task(task_id=task_id, name=name)

    def archive_task(self, task_id: str) -> bool:
        task = self.task_repository.get(task_id)
        if task is None:
            return False
        if task.is_archived:
            return True

        now = datetime.now()
        task.is_archived = True
        task.archived_at = now
        task.updated_at = now
        self.task_repository.update(task)
        return True

    def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Task]:
        """
        태스크 수정

        Args:
            task_id: 태스크 ID
            name: 새 태스크 이름
            description: 새 태스크 설명

        Returns:
            수정된 태스크 또는 None
        """
        task = self.task_repository.get(task_id)
        if task is None:
            return None

        if name is not None:
            task.name = name
        if description is not None:
            task.description = description
        task.updated_at = datetime.now()

        # 플러그인 실행 (태스크 수정 훅)
        context = {"action": "update", "task": task}
        self._execute_plugins(task_id, context)

        return self.task_repository.update(task)

    def delete_task(self, task_id: str) -> bool:
        """
        태스크 삭제

        Args:
            task_id: 태스크 ID

        Returns:
            삭제 성공 여부
        """
        # 플러그인 실행 (태스크 삭제 훅)
        context = {"action": "delete", "task_id": task_id}
        self._execute_plugins(task_id, context)

        return self.task_repository.delete(task_id)

    def get_task_prompts(self, task_id: str) -> List[Prompt]:
        """
        태스크별 프롬프트 조회

        Args:
            task_id: 태스크 ID

        Returns:
            프롬프트 목록
        """
        return self.prompt_repository.get_by_task(task_id)

    def get_latest_task_prompt(self, task_id: str) -> Optional[Prompt]:
        prompts = self.get_task_prompts(task_id)
        if not prompts:
            return None
        return max(prompts, key=lambda p: p.updated_at)

    def save_task_prompt(
        self,
        task_id: str,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[Prompt]:
        task = self.get_task(task_id)
        if task is None:
            return None

        now = datetime.now()
        prompt = self.get_latest_task_prompt(task_id)

        if prompt is None:
            prompt = Prompt(
                id=generate_prompt_id(),
                task_id=task_id,
                current_version_id=None,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                created_at=now,
                updated_at=now,
            )
            self.prompt_repository.create(prompt)
        else:
            updated_data = {
                **prompt.model_dump(),
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "updated_at": now,
            }
            prompt = Prompt.model_validate(updated_data)
            self.prompt_repository.update(prompt)

        task.updated_at = now
        self.task_repository.update(task)

        return prompt

    def set_prompt_current_version_id(
        self,
        prompt_id: str,
        current_version_id: str | None,
    ) -> Optional[Prompt]:
        prompt = self.prompt_repository.get(prompt_id)
        if prompt is None:
            return None

        now = datetime.now()
        updated_data = {
            **prompt.model_dump(),
            "current_version_id": current_version_id,
            "updated_at": now,
        }
        updated_prompt = Prompt.model_validate(updated_data)
        self.prompt_repository.update(updated_prompt)
        return updated_prompt
