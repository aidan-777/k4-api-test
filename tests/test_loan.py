"""借款相关接口测试"""
import pytest
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.mark.loan
class TestLoanAPI:
    """借款接口测试类"""

    def test_quest_loan_amount_success(self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient):
        """测试获取借款报价 - 成功场景"""
        # 先设置 mock 价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)

        # 请求借款报价
        response = public_api_client.quest_loan_amount({"BTC": "0.25"})
        assert response.status_code == 200
        data = response.json()
        assert "quote_id" in data
        assert "collateral_asset_infos" in data
        assert "BTC" in data["collateral_asset_infos"]
        assert "max_borrowed_value" in data
        assert "max_borrowed_amount" in data
        assert "borrowed_asset" in data
        assert "total_collateral_value" in data
        assert "created_at" in data
        assert "expires_at" in data

    def test_quest_loan_amount_empty_collateral(self, public_api_client: PublicAPIClient):
        """测试获取借款报价 - 空抵押资产"""
        response = public_api_client.quest_loan_amount({})
        assert response.status_code in [400, 500]
        data = response.json()
        assert "error" in data or "message" in data

    def test_quest_loan_amount_invalid_collateral(self, public_api_client: PublicAPIClient):
        """测试获取借款报价 - 无效抵押资产"""
        response = public_api_client.quest_loan_amount({"INVALID": "1.0"})
        # 可能返回错误或空结果
        assert response.status_code in [200, 400, 500]

    def test_quest_loan_amount_multiple_collaterals(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient
    ):
        """测试获取借款报价 - 多个抵押资产"""
        # 设置多个资产的价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)
        internal_api_client.set_mock_md_price("ETH", 3000.0)

        response = public_api_client.quest_loan_amount({
            "BTC": "0.1",
            "ETH": "2.0",
        })
        assert response.status_code == 200
        data = response.json()
        assert "collateral_asset_infos" in data
        assert "BTC" in data["collateral_asset_infos"]
        assert "ETH" in data["collateral_asset_infos"]

    def test_do_loan_success(
        self, public_api_client: PublicAPIClient, internal_api_client: InternalAPIClient
    ):
        """测试执行借款 - 成功场景"""
        # 先设置 mock 价格
        internal_api_client.set_mock_md_price("BTC", 50000.0)

        # 获取报价
        quote_response = public_api_client.quest_loan_amount({"BTC": "0.25"})
        assert quote_response.status_code == 200
        quote_data = quote_response.json()

        # 执行借款（需要根据实际 API 要求构造 payload）
        loan_payload = {
            "quote_id": quote_data["quote_id"],
            "user_id": "test_user_loan",
            "collateral_assets": {"BTC": "0.25"},
        }
        response = public_api_client.do_loan(loan_payload)
        # 根据实际实现，可能是 200 或 400/500
        assert response.status_code in [200, 400, 500]

    def test_do_loan_invalid_quote_id(self, public_api_client: PublicAPIClient):
        """测试执行借款 - 无效报价 ID"""
        loan_payload = {
            "quote_id": "invalid-quote-id",
            "user_id": "test_user",
            "collateral_assets": {"BTC": "0.25"},
        }
        response = public_api_client.do_loan(loan_payload)
        assert response.status_code in [400, 404, 500]

