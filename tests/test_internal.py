"""内部接口测试"""
import pytest
from src.api_client import InternalAPIClient


@pytest.mark.internal
class TestInternalAPI:
    """内部接口测试类"""

    def test_add_mock_position_success(self, internal_api_client: InternalAPIClient):
        """测试添加 mock 仓位 - 成功场景"""
        # 先设置价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.set_mock_md_price("ETH", 3000.0)

        # 添加仓位
        response = internal_api_client.add_mock_position(
            user_id="test_user_1",
            position_id="test_pos_1",
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5, "ETH": 5.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["position_id"] == "test_pos_1"
        assert data["data"]["user_id"] == "test_user_1"

    def test_add_mock_position_empty_collateral(self, internal_api_client: InternalAPIClient):
        """测试添加 mock 仓位 - 空抵押资产"""
        response = internal_api_client.add_mock_position(
            user_id="test_user",
            position_id="test_pos",
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={},
        )
        assert response.status_code in [400, 500]
        data = response.json()
        assert "error" in data or data.get("status") == "error"

    def test_add_mock_position_no_price(self, internal_api_client: InternalAPIClient):
        """测试添加 mock 仓位 - 缺少价格数据"""
        # 不设置价格，直接添加仓位
        response = internal_api_client.add_mock_position(
            user_id="test_user",
            position_id="test_pos",
            borrowed_asset="USDC",
            borrowed_amount=10000.0,
            collateral_assets={"BTC": 0.5},
        )
        # 应该返回错误，因为缺少价格
        assert response.status_code in [400, 500]

    def test_set_mock_md_price_success(self, internal_api_client: InternalAPIClient):
        """测试设置 mock 价格 - 成功场景"""
        response = internal_api_client.set_mock_md_price("BTC", 50000.0)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["symbol"] == "BTC"
        assert data["price"] == 50000.0

    def test_set_mock_md_price_invalid(self, internal_api_client: InternalAPIClient):
        """测试设置 mock 价格 - 无效价格"""
        response = internal_api_client.set_mock_md_price("BTC", -100.0)
        assert response.status_code in [200, 400, 500]
        data = response.json()
        assert data.get("status") == "error" or "error" in data

    def test_clear_mock_md_price_success(self, internal_api_client: InternalAPIClient):
        """测试清除 mock 价格 - 成功场景"""
        # 先设置价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)

        # 清除价格
        response = internal_api_client.clear_mock_md_price("BTC")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["symbol"] == "BTC"

    def test_clear_all_mock_md_prices(self, internal_api_client: InternalAPIClient):
        """测试清除所有 mock 价格"""
        # 先设置一些价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.set_mock_md_price("ETH", 3000.0)

        # 清除所有价格
        response = internal_api_client.clear_all_mock_md_prices()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

