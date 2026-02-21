"""
[overview]
Provider Manager 구현

[description]
Provider CRUD, 연결 테스트 기능을 제공합니다.
ProviderRepository를 통해 데이터베이스에 접근합니다.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional, List

import requests

from src.data.models import Provider
from src.data.repository import ProviderRepository
from src.utils.id_generator import generate_provider_id


class ProviderManager:
    """
    [overview]
    Provider Manager

    [description]
    Provider CRUD, 연결 테스트를 담당합니다.
    Repository 패턴을 통해 데이터베이스에 접근합니다.
    """

    DEFAULT_TIMEOUT = 10

    def __init__(self, db_path: Optional[Path] = None):
        """
        ProviderManager 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.provider_repository = ProviderRepository(db_path)

    def create_provider(
        self,
        name: str,
        api_url: str,
        api_key: Optional[str] = None,
        model: str = "llama2",
        description: Optional[str] = None,
    ) -> Provider:
        """
        Provider 생성

        Args:
            name: Provider 이름
            api_url: API 엔드포인트 URL
            api_key: API 키 (선택)
            model: 모델 이름
            description: Provider 설명 (선택)

        Returns:
            생성된 Provider
        """
        provider = Provider(
            id=generate_provider_id(),
            name=name,
            description=description,
            api_url=api_url,
            api_key=api_key,
            model=model,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return self.provider_repository.create(provider)

    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """
        ID로 Provider 조회

        Args:
            provider_id: Provider ID

        Returns:
            조회된 Provider 또는 None
        """
        return self.provider_repository.get(provider_id)

    def get_all_providers(self) -> List[Provider]:
        """
        모든 Provider 조회

        Returns:
            Provider 목록
        """
        return self.provider_repository.get_all()

    def update_provider(
        self,
        provider_id: str,
        name: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Optional[Provider]:
        """
        Provider 수정

        Args:
            provider_id: Provider ID
            name: 새 이름
            api_url: 새 API URL
            api_key: 새 API 키
            model: 새 모델 이름

        Returns:
            수정된 Provider 또는 None
        """
        provider = self.provider_repository.get(provider_id)
        if provider is None:
            return None

        if name is not None:
            provider.name = name
        if api_url is not None:
            provider.api_url = api_url
        if api_key is not None:
            provider.api_key = api_key
        if model is not None:
            provider.model = model

        provider.updated_at = datetime.now()

        return self.provider_repository.update(provider)

    def delete_provider(self, provider_id: str) -> bool:
        """
        Provider 삭제

        Args:
            provider_id: Provider ID

        Returns:
            삭제 성공 여부
        """
        return self.provider_repository.delete(provider_id)

    def test_connection(self, provider_id: str) -> dict[str, Any]:
        """
        Provider 연결 테스트

        Args:
            provider_id: Provider ID

        Returns:
            결과 딕셔너리 (success, message)
        """
        provider = self.provider_repository.get(provider_id)
        if provider is None:
            return {"success": False, "message": "Provider not found"}

        return self._test_connection_with_provider(provider)

    def test_connection_with_data(
        self, provider_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Provider 데이터로 직접 연결 테스트 (DB 저장 전)

        Args:
            provider_data: Provider 데이터 딕셔너리

        Returns:
            결과 딕셔너리 (success, message)
        """
        api_url = provider_data.get("api_url", "").strip()
        api_key = provider_data.get("api_key", "").strip()

        if not api_url:
            return {"success": False, "message": "API URL is required"}

        # 임시 Provider 객체 생성 (ID 검증을 위해 None 사용)
        provider = Provider(
            id=None,
            name=provider_data.get("name", "temp"),
            description=provider_data.get("description"),
            api_url=api_url,
            api_key=api_key if api_key else None,
            model=provider_data.get("model", "llama2"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        return self._test_connection_with_provider(provider)

    def _test_connection_with_provider(self, provider: Provider) -> dict[str, Any]:
        """
        Provider 객체로 연결 테스트 (내부 메서드)

        Args:
            provider: Provider 객체

        Returns:
            결과 딕셔너리 (success, message)
        """
        headers = {
            "Content-Type": "application/json",
        }
        if provider.api_key:
            headers["Authorization"] = f"Bearer {provider.api_key}"

        try:
            response = requests.get(
                provider.api_url, headers=headers, timeout=self.DEFAULT_TIMEOUT
            )

            if response.status_code == 200:
                return {"success": True, "message": "Connection successful"}
            else:
                return {
                    "success": False,
                    "message": f"Connection failed: {response.status_code}",
                }

        except requests.exceptions.Timeout:
            return {"success": False, "message": "Connection timeout"}
        except requests.exceptions.ConnectionError as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Connection error: {str(e)}"}
