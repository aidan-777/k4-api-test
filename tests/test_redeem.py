"""赎回相关接口测试"""
import pytest
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.mark.redeem
class TestRedeemAPI:
    """赎回接口测试类"""

    def test_quest_redeem_amount_success(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient,
        test_user_id: str, test_position_id: str
    ):
        """测试查询应还本金+利息 - 成功场景"""
        # 先创建 mock 仓位
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.add_mock_position(
            user_id=test_user_id,
            position_id=test_position_id,
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5},
        )

        # 查询应还金额
        response = public_api_client.quest_redeem_amount(test_user_id, test_position_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "redeem_amount" in data
        assert "borrowed_value" in data
        assert "borrowed_interest_cost" in data

    def test_quest_redeem_amount_position_not_found(self, public_api_client: PublicAPIClient):
        """测试查询应还本金+利息 - 仓位不存在"""
        response = public_api_client.quest_redeem_amount("user_123", "non_existent_pos")
        assert response.status_code in [200, 404, 500]
        data = response.json()
        assert data.get("status") == "error" or "error" in data

    def test_quest_redeem_amount_invalid_user(self, public_api_client: PublicAPIClient):
        """测试查询应还本金+利息 - 用户不匹配"""
        response = public_api_client.quest_redeem_amount("wrong_user", "some_pos")
        assert response.status_code in [200, 400, 403, 500]
        data = response.json()
        assert data.get("status") == "error" or "error" in data

    def test_do_redeem_not_implemented(
        self, public_api_client: PublicAPIClient, test_user_id: str, test_position_id: str
    ):
        """测试执行赎回 - 未实现"""
        response = public_api_client.do_redeem(test_user_id, test_position_id)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Not implemented"

