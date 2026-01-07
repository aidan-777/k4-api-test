"""借款相关接口测试"""
import pytest
from src.api_client import PublicAPIClient


def _default_loan_payload(test_address: str) -> dict:
    """构造默认借款请求"""
    return {
        "network": "Ethereum",
        "address": test_address,
        "intent_borrow_asset": "HypercorePerpsUSDC",
        "intent_borrow_value": "1000.0",
    }


@pytest.mark.loan
class TestLoanAPI:
    """借款接口测试类"""

    def test_loan_quote_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """请求未知地址的借款报价应返回错误"""
        response = public_api_client.loan_quote({"address": test_address})
        assert response.status_code in (400, 404, 503)
        data = response.json()
        assert data["status"] == "error"
        assert "message" in data

    def test_loan_quote_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 时返回 422"""
        response = public_api_client.loan_quote({})
        assert response.status_code == 422

    def test_do_loan_missing_user_header(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """缺少用户 header 时返回未授权"""
        payload = _default_loan_payload(test_address)
        response = public_api_client.do_loan(payload)
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "unauthorized"
        assert data["message"] == "Missing X-User-Id header"

    def test_do_loan_invalid_user_header(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """非法 UUID header 应返回 400"""
        payload = _default_loan_payload(test_address)
        response = public_api_client.do_loan(payload, user_id="not-a-uuid")
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "invalid_user_id"

    def test_do_loan_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
        test_user_uuid: str,
    ):
        """未知账户发起借款应失败"""
        payload = _default_loan_payload(test_address)
        response = public_api_client.do_loan(payload, user_id=test_user_uuid)
        assert response.status_code in (400, 404, 500)
        data = response.json()
        assert data.get("status") == "error" or "error" in data
