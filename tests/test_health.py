"""健康检查接口测试"""
import pytest
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.mark.health
class TestHealthCheck:
    """健康检查接口测试类"""

    def test_ping_public(self, public_api_client: PublicAPIClient):
        """测试公共 API ping 接口"""
        response = public_api_client.ping()
        assert response.status_code == 200
        assert response.text.strip() == "pong"

    def test_ping_internal(self, internal_api_client: InternalAPIClient):
        """测试内部 API ping 接口"""
        response = internal_api_client.ping()
        assert response.status_code == 200
        assert response.text.strip() == "pong"

    def test_health_check_public(self, public_api_client: PublicAPIClient):
        """测试公共 API 健康检查接口"""
        response = public_api_client.health_check()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "superstack-cross-margin"
        assert "timestamp" in data

    def test_health_check_internal(self, internal_api_client: InternalAPIClient):
        """测试内部 API 健康检查接口"""
        response = internal_api_client.health_check()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "superstack-cross-margin"
        assert "timestamp" in data

    def test_get_status(self, public_api_client: PublicAPIClient):
        """测试获取系统状态接口"""
        response = public_api_client.get_status()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["metrics_port"] == 9091
        assert data["http_port"] == 8080
        assert "version" in data
        assert "components" in data
        assert data["components"]["metrics_server"] == "running"
        assert data["components"]["http_server"] == "running"

