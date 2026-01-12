"""内部接口测试"""
import pytest
from src.api_client import InternalAPIClient

pytestmark = pytest.mark.skip(reason="internal API tests are not needed currently")


def _build_depth_payload() -> dict:
    """创建默认的深度请求"""
    return {
        "symbol": "BTC/USDC",
        "ask_price": [60100.0, 60200.0],
        "ask_volume": [1.5, 1.0],
        "bid_price": [60000.0, 59900.0],
        "bid_volume": [2.0, 1.5],
    }


@pytest.mark.internal
class TestInternalAPI:
    """内部接口测试类"""

    def test_add_mock_position_not_implemented(self, internal_api_client: InternalAPIClient):
        """当前实现返回 501"""
        payload = {
            "user_id": "test_user",
            "position_id": "test_pos",
            "borrowed_asset": "USDC",
            "borrowed_amount": 1000.0,
            "collateral_assets": {"BTC": 0.5},
        }
        response = internal_api_client.add_mock_position(payload)
        assert response.status_code == 501
        data = response.json()
        assert data["message"] == "Not implemented"

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
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["error"] == "invalid_price"

    def test_clear_mock_md_price_success(self, internal_api_client: InternalAPIClient):
        """测试清除 mock 价格 - 成功场景"""
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        response = internal_api_client.clear_mock_md_price("BTC")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["symbol"] == "BTC"

    def test_clear_all_mock_md_prices(self, internal_api_client: InternalAPIClient):
        """测试清除所有 mock 价格"""
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        response = internal_api_client.clear_all_mock_md_prices()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_set_mock_md_depth_success(self, internal_api_client: InternalAPIClient):
        """设置深度成功"""
        payload = _build_depth_payload()
        response = internal_api_client.set_mock_md_depth(payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["symbol"] == payload["symbol"]

    def test_set_mock_md_depth_invalid_spread(self, internal_api_client: InternalAPIClient):
        """买价大于等于卖价时返回错误"""
        payload = _build_depth_payload()
        payload["bid_price"][0] = 70000.0
        response = internal_api_client.set_mock_md_depth(payload)
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["error"] in ("invalid_spread", "invalid_depth")

    def test_clear_mock_md_depth_success(self, internal_api_client: InternalAPIClient):
        """清除指定交易对深度"""
        internal_api_client.set_mock_md_depth(_build_depth_payload())
        response = internal_api_client.clear_mock_md_depth({"symbol": "BTC/USDC"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_clear_all_mock_md_depths(self, internal_api_client: InternalAPIClient):
        """清除全部深度"""
        internal_api_client.set_mock_md_depth(_build_depth_payload())
        response = internal_api_client.clear_all_mock_md_depths()
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
