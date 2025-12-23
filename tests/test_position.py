"""仓位相关接口测试"""
import pytest
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.mark.position
class TestPositionAPI:
    """仓位接口测试类"""

    def test_user_close_position_success(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient,
        test_user_id: str, test_position_id: str
    ):
        """测试用户发起平仓 - 成功场景"""
        # 先创建 mock 仓位
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.add_mock_position(
            user_id=test_user_id,
            position_id=test_position_id,
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5},
        )

        # 发起平仓
        response = public_api_client.user_close_position(test_user_id, test_position_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_user_close_position_not_found(self, public_api_client: PublicAPIClient):
        """测试用户发起平仓 - 仓位不存在"""
        response = public_api_client.user_close_position("user_123", "non_existent_pos")
        assert response.status_code in [200, 404, 500]
        data = response.json()
        assert data.get("status") == "error" or "error" in data

    def test_user_close_position_wrong_user(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient,
        test_position_id: str
    ):
        """测试用户发起平仓 - 用户不匹配"""
        # 创建仓位
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.add_mock_position(
            user_id="owner_user",
            position_id=test_position_id,
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5},
        )

        # 用错误的用户 ID 尝试平仓
        response = public_api_client.user_close_position("wrong_user", test_position_id)
        assert response.status_code in [200, 400, 403, 500]
        data = response.json()
        assert data.get("status") == "error" or "error" in data

