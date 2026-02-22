"""
[overview]
Repository 패턴 구현

[description]
데이터베이스 CRUD 작업을 위한 Repository 인터페이스와 구현체들을 제공합니다.
TaskRepository, PromptRepository, VersionRepository, ExecutionRecordRepository,
ProviderRepository를 포함합니다.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, Optional, List

from pydantic import BaseModel

from src.data.database import Database
from src.data.models import (
    Task,
    Prompt,
    Version,
    ExecutionRecord,
    Provider,
)

# Generic TypeVar for Repository
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType], ABC):
    """
    [overview]
    기본 Repository 인터페이스

    [description]
    모든 Repository가 구현해야 할 기본 CRUD 인터페이스를 정의합니다.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Repository 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.database = Database(db_path)
        self.table_name = self._get_table_name()

    @abstractmethod
    def _get_table_name(self) -> str:
        """테이블 이름을 반환합니다."""
        pass

    @abstractmethod
    def _model_class(self) -> type[ModelType]:
        """모델 클래스를 반환합니다."""
        pass

    def create(self, entity: ModelType) -> ModelType:
        """
        엔티티 생성

        Args:
            entity: 생성할 엔티티

        Returns:
            생성된 엔티티
        """
        table = self.database.get_table(self.table_name)
        table.insert(entity.model_dump(mode='json'))
        return entity

    def get(self, entity_id: str) -> Optional[ModelType]:
        """
        ID로 엔티티 조회

        Args:
            entity_id: 엔티티 ID

        Returns:
            조회된 엔티티 또는 None
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        result = table.get(query.id == entity_id)
        if result:
            return self._model_class()(**result)
        return None

    def get_all(self) -> List[ModelType]:
        """
        모든 엔티티 조회

        Returns:
            엔티티 목록
        """
        table = self.database.get_table(self.table_name)
        return [self._model_class()(**item) for item in table.all()]

    def update(self, entity: ModelType) -> Optional[ModelType]:
        """
        엔티티 수정

        Args:
            entity: 수정할 엔티티

        Returns:
            수정된 엔티티 또는 None (존재하지 않을 경우)
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        entity_dict = entity.model_dump(mode='json')
        table.update(entity_dict, query.id == entity_dict.get('id', ''))
        return entity

    def delete(self, entity_id: str) -> bool:
        """
        엔티티 삭제

        Args:
            entity_id: 삭제할 엔티티 ID

        Returns:
            삭제 성공 여부
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        result = table.remove(query.id == entity_id)
        return len(result) > 0


class TaskRepository(BaseRepository[Task]):
    """
    [overview]
    Task Repository

    [description]
    Task 모델의 CRUD 작업을 수행합니다.
    """

    def _get_table_name(self) -> str:
        return "tasks"

    def _model_class(self) -> type[Task]:
        return Task


class PromptRepository(BaseRepository[Prompt]):
    """
    [overview]
    Prompt Repository

    [description]
    Prompt 모델의 CRUD 작업을 수행합니다.
    """

    def _get_table_name(self) -> str:
        return "prompts"

    def _model_class(self) -> type[Prompt]:
        return Prompt

    def get_by_task(self, task_id: str) -> List[Prompt]:
        """
        태스크별 프롬프트 조회

        Args:
            task_id: 태스크 ID

        Returns:
            프롬프트 목록
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        results = table.search(query.task_id == task_id)
        return [Prompt(**item) for item in results]


class VersionRepository(BaseRepository[Version]):
    """
    [overview]
    Version Repository

    [description]
    Version 모델의 CRUD 작업을 수행합니다.
    """

    def _get_table_name(self) -> str:
        return "versions"

    def _model_class(self) -> type[Version]:
        return Version

    def get_by_prompt(self, prompt_id: str) -> List[Version]:
        """
        프롬프트별 버전 조회

        Args:
            prompt_id: 프롬프트 ID

        Returns:
            버전 목록
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        results = table.search(query.prompt_id == prompt_id)
        return [Version(**item) for item in results]

    def get_latest(self, prompt_id: str) -> Optional[Version]:
        """
        최신 버전 조회

        Args:
            prompt_id: 프롬프트 ID

        Returns:
            최신 버전 또는 None
        """
        versions = self.get_by_prompt(prompt_id)
        if not versions:
            return None
        return max(versions, key=lambda v: v.version_number)


class ExecutionRecordRepository(BaseRepository[ExecutionRecord]):
    """
    [overview]
    ExecutionRecord Repository

    [description]
    ExecutionRecord 모델의 CRUD 작업을 수행합니다.
    """

    def _get_table_name(self) -> str:
        return "execution_records"

    def _model_class(self) -> type[ExecutionRecord]:
        return ExecutionRecord

    def get_by_prompt(self, prompt_id: str) -> List[ExecutionRecord]:
        """
        프롬프트별 실행 기록 조회

        Args:
            prompt_id: 프롬프트 ID

        Returns:
            실행 기록 목록
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        results = table.search(query.prompt_id == prompt_id)
        return [ExecutionRecord(**item) for item in results]

    def get_by_version(self, version_id: str) -> List[ExecutionRecord]:
        """
        버전별 실행 기록 조회

        Args:
            version_id: 버전 ID

        Returns:
            실행 기록 목록
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        results = table.search(query.version_id == version_id)
        return [ExecutionRecord(**item) for item in results]


class ProviderRepository(BaseRepository[Provider]):
    """
    [overview]
    Provider Repository

    [description]
    Provider 모델의 CRUD 작업을 수행합니다.
    """

    def _get_table_name(self) -> str:
        return "providers"

    def _model_class(self) -> type[Provider]:
        return Provider

    def get_by_name(self, name: str) -> Optional[Provider]:
        """
        이름으로 프로바이더 조회

        Args:
            name: 프로바이더 이름

        Returns:
            조회된 프로바이더 또는 None
        """
        from tinydb import Query

        table = self.database.get_table(self.table_name)
        query = Query()
        result = table.get(query.name == name)
        if result:
            return Provider(**result)
        return None
