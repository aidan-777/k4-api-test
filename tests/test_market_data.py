"""行情/价格相关接口测试"""

import pytest

from src.api_client import InternalAPIClient, PublicAPIClient

pytestmark = pytest.mark.skip(reason="market data tests depend on internal API; not needed currently")


@pytest.mark.market
class TestMarketData:
    def test_general_info_has_btc_price(self, public_api_client: PublicAPIClient):
        response = public_api_client.get_general_info()
        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "BTC" in data["assets"]
        assert "price" in data["assets"]["BTC"]

    def test_mock_price_updates_general_info(
        self,
        public_api_client: PublicAPIClient,
        internal_api_client: InternalAPIClient,
    ):
        """
        通过内部接口注入 mock 价格后，general_info 应返回一致的价格。
        """
        mock_price = 50_000.0
        response = internal_api_client.set_mock_md_price("BTC", mock_price)
        assert response.status_code == 200

        response = public_api_client.get_general_info()
        assert response.status_code == 200
        data = response.json()
        price = data["assets"]["BTC"]["price"]
        assert abs(price - mock_price) < 1e-9
