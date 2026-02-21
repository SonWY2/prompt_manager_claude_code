"""
[overview]
Provider Manager 테스트

[description]
ProviderManager의 Provider CRUD, 연결 테스트 기능을 테스트합니다.
unittest.mock을 사용하여 실제 API 연결을 모킹합니다.
"""

from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import requests

from src.core.provider_manager import ProviderManager
from src.data.repository import ProviderRepository


class TestProviderManagerInit:
    """ProviderManager 초기화 테스트"""

    def test_init_default_db_path(self):
        """기본 데이터베이스 경로로 초기화"""
        manager = ProviderManager()
        assert isinstance(manager.provider_repository, ProviderRepository)

    def test_init_custom_db_path(self):
        """사용자 지정 데이터베이스 경로로 초기화"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)
            assert manager.provider_repository is not None


class TestProviderManagerCreate:
    """Provider Manager 생성 테스트"""

    def test_create_provider(self):
        """Provider 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="test_key",
                model="llama2",
            )

            assert provider.name == "Test Provider"
            assert provider.api_url == "http://localhost:11434/v1"
            assert provider.api_key == "test_key"
            assert provider.model == "llama2"
            assert provider.id is not None

    def test_create_provider_without_api_key(self):
        """API Key 없이 Provider 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key=None,
                model="llama2",
            )

            assert provider.api_key is None

    def test_create_provider_multiple(self):
        """여러 Provider 생성"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider1 = manager.create_provider(
                name="Provider 1", api_url="http://localhost:11434/v1", model="llama2"
            )
            provider2 = manager.create_provider(
                name="Provider 2",
                api_url="http://localhost:8080/v1",
                model="gpt-3.5-turbo",
            )

            assert provider1.id != provider2.id
            assert provider1.name == "Provider 1"
            assert provider2.name == "Provider 2"


class TestProviderManagerRead:
    """Provider Manager 조회 테스트"""

    def test_get_provider(self):
        """ID로 Provider 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            created_provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                model="llama2",
            )

            retrieved_provider = manager.get_provider(created_provider.id)

            assert retrieved_provider is not None
            assert retrieved_provider.id == created_provider.id
            assert retrieved_provider.name == created_provider.name

    def test_get_provider_not_found(self):
        """존재하지 않는 Provider 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            retrieved_provider = manager.get_provider("non_existent_id")

            assert retrieved_provider is None

    def test_get_all_providers(self):
        """모든 Provider 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider1 = manager.create_provider(
                name="Provider 1", api_url="http://localhost:11434/v1", model="llama2"
            )
            provider2 = manager.create_provider(
                name="Provider 2",
                api_url="http://localhost:8080/v1",
                model="gpt-3.5-turbo",
            )

            all_providers = manager.get_all_providers()

            assert len(all_providers) == 2
            provider_ids = [p.id for p in all_providers]
            assert provider1.id in provider_ids
            assert provider2.id in provider_ids

    def test_get_all_providers_empty(self):
        """빈 목록 조회"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            all_providers = manager.get_all_providers()

            assert len(all_providers) == 0


class TestProviderManagerUpdate:
    """Provider Manager 수정 테스트"""

    def test_update_provider_name(self):
        """Provider 이름 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Original Name",
                api_url="http://localhost:11434/v1",
                model="llama2",
            )

            updated_provider = manager.update_provider(provider.id, name="Updated Name")

            assert updated_provider is not None
            assert updated_provider.name == "Updated Name"

    def test_update_provider_api_url(self):
        """Provider API URL 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                model="llama2",
            )

            updated_provider = manager.update_provider(
                provider.id, api_url="http://new-url.com/v1"
            )

            assert updated_provider is not None
            assert updated_provider.api_url == "http://new-url.com/v1"

    def test_update_provider_api_key(self):
        """Provider API Key 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="old_key",
                model="llama2",
            )

            updated_provider = manager.update_provider(provider.id, api_key="new_key")

            assert updated_provider is not None
            assert updated_provider.api_key == "new_key"

    def test_update_provider_model(self):
        """Provider 모델 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                model="llama2",
            )

            updated_provider = manager.update_provider(provider.id, model="gpt-4")

            assert updated_provider is not None
            assert updated_provider.model == "gpt-4"

    def test_update_provider_multiple_fields(self):
        """여러 필드 동시 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Original Name",
                api_url="http://localhost:11434/v1",
                api_key="old_key",
                model="llama2",
            )

            updated_provider = manager.update_provider(
                provider.id,
                name="Updated Name",
                api_url="http://new-url.com/v1",
                api_key="new_key",
                model="gpt-4",
            )

            assert updated_provider is not None
            assert updated_provider.name == "Updated Name"
            assert updated_provider.api_url == "http://new-url.com/v1"
            assert updated_provider.api_key == "new_key"
            assert updated_provider.model == "gpt-4"

    def test_update_provider_not_found(self):
        """존재하지 않는 Provider 수정"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            updated_provider = manager.update_provider(
                "non_existent_id", name="New Name"
            )

            assert updated_provider is None


class TestProviderManagerDelete:
    """Provider Manager 삭제 테스트"""

    def test_delete_provider(self):
        """Provider 삭제"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                model="llama2",
            )

            deleted = manager.delete_provider(provider.id)

            assert deleted is True

            # 삭제 후 조회 시 None 반환
            retrieved_provider = manager.get_provider(provider.id)
            assert retrieved_provider is None

    def test_delete_provider_not_found(self):
        """존재하지 않는 Provider 삭제"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            deleted = manager.delete_provider("non_existent_id")

            assert deleted is False


class TestProviderManagerConnectionTest:
    """Provider Manager 연결 테스트 테스트"""

    @patch("src.core.provider_manager.requests.get")
    def test_connection_success(self, mock_get):
        """연결 테스트 성공"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="test_key",
                model="llama2",
            )

            result = manager.test_connection(provider.id)

            assert result["success"] is True
            assert result["message"] == "Connection successful"
            assert mock_get.called

    @patch("src.core.provider_manager.requests.get")
    def test_connection_failure_404(self, mock_get):
        """연결 테스트 실패 (404)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="test_key",
                model="llama2",
            )

            result = manager.test_connection(provider.id)

            assert result["success"] is False
            assert "Connection failed" in result["message"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_failure_timeout(self, mock_get):
        """연결 테스트 실패 (타임아웃)"""
        mock_get.side_effect = Exception("Timeout")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="test_key",
                model="llama2",
            )

            result = manager.test_connection(provider.id)

            assert result["success"] is False
            assert "Connection error" in result["message"]

    def test_connection_provider_not_found(self):
        """존재하지 않는 Provider 연결 테스트"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            result = manager.test_connection("non_existent_id")

            assert result["success"] is False
            assert "Provider not found" in result["message"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_api_key(self, mock_get):
        """API Key 포함 연결 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key="secret_key",
                model="llama2",
            )

            manager.test_connection(provider.id)

            # Authorization 헤더 검증
            call_kwargs = mock_get.call_args[1]
            assert "Authorization" in call_kwargs["headers"]
            assert "Bearer secret_key" in call_kwargs["headers"]["Authorization"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_without_api_key(self, mock_get):
        """API Key 없이 연결 테스트"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider = manager.create_provider(
                name="Test Provider",
                api_url="http://localhost:11434/v1",
                api_key=None,
                model="llama2",
            )

            manager.test_connection(provider.id)

            # Authorization 헤더 없음 검증
            call_kwargs = mock_get.call_args[1]
            assert "Authorization" not in call_kwargs["headers"]


class TestProviderManagerConnectionTestWithData:
    """Provider Manager 연결 테스트 (데이터 기반) 테스트"""

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_success(self, mock_get):
        """데이터 기반 연결 테스트 성공"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "test_key",
                "model": "llama2",
            }

            result = manager.test_connection_with_data(provider_data)

            assert result["success"] is True
            assert result["message"] == "Connection successful"
            assert mock_get.called

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_failure_404(self, mock_get):
        """데이터 기반 연결 테스트 실패 (404)"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "test_key",
                "model": "llama2",
            }

            result = manager.test_connection_with_data(provider_data)

            assert result["success"] is False
            assert "Connection failed" in result["message"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_timeout(self, mock_get):
        """데이터 기반 연결 테스트 타임아웃"""
        mock_get.side_effect = requests.exceptions.Timeout("Connection timeout")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "test_key",
                "model": "llama2",
            }

            result = manager.test_connection_with_data(provider_data)

            assert result["success"] is False
            assert "Connection timeout" in result["message"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_connection_error(self, mock_get):
        """데이터 기반 연결 테스트 연결 에러"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "test_key",
                "model": "llama2",
            }

            result = manager.test_connection_with_data(provider_data)

            assert result["success"] is False
            assert "Connection error" in result["message"]

    def test_connection_with_data_missing_url(self):
        """데이터 기반 연결 테스트 (URL 누락)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "",
                "api_key": "test_key",
                "model": "llama2",
            }

            result = manager.test_connection_with_data(provider_data)

            assert result["success"] is False
            assert "API URL is required" in result["message"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_with_api_key(self, mock_get):
        """데이터 기반 연결 테스트 (API Key 포함)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "secret_key",
                "model": "llama2",
            }

            manager.test_connection_with_data(provider_data)

            # Authorization 헤더 검증
            call_kwargs = mock_get.call_args[1]
            assert "Authorization" in call_kwargs["headers"]
            assert "Bearer secret_key" in call_kwargs["headers"]["Authorization"]

    @patch("src.core.provider_manager.requests.get")
    def test_connection_with_data_without_api_key(self, mock_get):
        """데이터 기반 연결 테스트 (API Key 미포함)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_db.json"
            manager = ProviderManager(db_path)

            provider_data = {
                "id": "test_id",
                "name": "Test Provider",
                "api_url": "http://localhost:11434/v1",
                "api_key": "",
                "model": "llama2",
            }

            manager.test_connection_with_data(provider_data)

            # Authorization 헤더 없음 검증
            call_kwargs = mock_get.call_args[1]
            assert "Authorization" not in call_kwargs["headers"]
