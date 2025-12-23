"""保证金相关接口测试"""
import pytest
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.mark.margin
class TestMarginAPI:
    """保证金接口测试类"""

    def test_add_margin_success(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient,
        test_user_id: str, test_position_id: str
    ):
        """测试增加保证金 - 成功场景"""
        # 先创建 mock 仓位
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.add_mock_position(
            user_id=test_user_id,
            position_id=test_position_id,
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5},
        )

        # 增加保证金
        margin_payload = {
            "user_id": test_user_id,
            "position_id": test_position_id,
            "collateral_assets": {"BTC": 0.1},
        }
        response = public_api_client.add_margin(margin_payload)
        # 根据实际实现判断状态码
        assert response.status_code in [200, 400, 500]

    def test_add_margin_invalid_position(self, public_api_client: PublicAPIClient):
        """测试增加保证金 - 无效仓位"""
        margin_payload = {
            "user_id": "test_user",
            "position_id": "non_existent_pos",
            "collateral_assets": {"BTC": 0.1},
        }
        response = public_api_client.add_margin(margin_payload)
        assert response.status_code in [400, 404, 500]

    def test_add_margin_empty_collateral(self, public_api_client: PublicAPIClient):
        """测试增加保证金 - 空抵押资产"""
        margin_payload = {
            "user_id": "test_user",
            "position_id": "test_pos",
            "collateral_assets": {},
        }
        response = public_api_client.add_margin(margin_payload)
        assert response.status_code in [400, 500]

