"""账户查询及模式切换接口测试"""
import pytest
from src.api_client import PublicAPIClient


@pytest.mark.accounts
class TestAccountAPIs:
    """账户相关接口测试"""

    def test_get_accounts_returns_snapshot(self, public_api_client: PublicAPIClient):
        """获取全部账户应返回标准结构"""
        response = public_api_client.get_accounts()
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "accounts" in data

    def test_get_account_by_ids_empty(self, public_api_client: PublicAPIClient):
        """空列表请求返回成功且数量为 0"""
        response = public_api_client.get_account_by_ids({"account_ids": []})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 0
        assert data["total_found"] == 0

    def test_get_assets_by_ids_empty(self, public_api_client: PublicAPIClient):
        """空列表资产查询返回成功"""
        response = public_api_client.get_assets_by_ids({"account_ids": []})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 0
        assert data["total_found"] == 0

    def test_operation_history_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 的请求应被拒绝"""
        response = public_api_client.operation_history({})
        assert response.status_code == 422

    def test_interest_history_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 的请求应被拒绝"""
        response = public_api_client.interest_history({})
        assert response.status_code == 422

    def test_account_mode_missing_auth(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """未携带 Authorization header 时返回 401"""
        payload = {
            "mode": "unified",
            "mainAddress": test_address,
        }
        response = public_api_client.account_mode(payload)
        assert response.status_code == 401
        data = response.json()
        assert "Missing Authorization header" in data["error"]
