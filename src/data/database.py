"""
[overview]
TinyDB 데이터베이스 초기화

[description]
TinyDB를 사용하여 JSON 파일 기반 데이터베이스를 초기화하고 관리합니다.
"""

from pathlib import Path
from typing import Optional

from tinydb import TinyDB


class Database:
    """
    [overview]
    TinyDB 데이터베이스 관리자

    [description]
    TinyDB 데이터베이스를 초기화하고 테이블 관리를 제공합니다.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        데이터베이스 초기화

        Args:
            db_path: 데이터베이스 파일 경로 (기본값: data/prompts.json)
        """
        if db_path is None:
            # 기본 데이터 경로 설정
            from src.utils.config import DATA_DIR_NAME, DATABASE_FILENAME

            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / DATA_DIR_NAME / DATABASE_FILENAME

        self.db_path = db_path
        self._ensure_db_directory()
        self._db: Optional[TinyDB] = None

    def _ensure_db_directory(self) -> None:
        """데이터베이스 디렉토리가 존재하는지 확인하고 생성합니다."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def db(self) -> TinyDB:
        """TinyDB 인스턴스를 반환합니다 (lazy initialization)."""
        if self._db is None:
            self._db = TinyDB(self.db_path, indent=2)
        return self._db

    def get_table(self, table_name: str):
        """
        테이블을 가져옵니다.

        Args:
            table_name: 테이블 이름

        Returns:
            TinyDB 테이블 인스턴스
        """
        return self.db.table(table_name)

    def close(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self._db is not None:
            self._db.close()
            self._db = None

    def __enter__(self):
        """Context manager 진입."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료."""
        self.close()


# 전역 데이터베이스 인스턴스 (싱글톤 패턴)
_global_db: Optional[Database] = None


def get_database(db_path: Optional[Path] = None) -> Database:
    """
    전역 데이터베이스 인스턴스를 반환합니다.

    Args:
        db_path: 데이터베이스 파일 경로 (최초 호출 시만 유효)

    Returns:
        Database 인스턴스
    """
    global _global_db
    if _global_db is None:
        _global_db = Database(db_path)
    return _global_db


def close_database() -> None:
    """전역 데이터베이스 연결을 종료합니다."""
    global _global_db
    if _global_db is not None:
        _global_db.close()
        _global_db = None
