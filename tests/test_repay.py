"""还款相关接口测试"""
import pytest
from src.api_client import PublicAPIClient


@pytest.mark.repay
class TestRepayAPI:
    """还款接口测试"""

    def test_repay_quote_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """未知账户查询还款应返回错误"""
        response = public_api_client.repay_quote({"address": test_address})
        assert response.status_code in (400, 404)
        data = response.json()
        assert data["status"] == "error"
        assert "message" in data

    def test_repay_quote_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 时返回 422"""
        response = public_api_client.repay_quote({})
        assert response.status_code == 422

    def test_repay_quote_empty_address(self, public_api_client: PublicAPIClient):
        """address 为空字符串应返回 400"""
        response = public_api_client.repay_quote({"address": ""})
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Invalid address: cannot be empty"

    def test_do_repay_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """未知账户执行还款应失败"""
        payload = {"address": test_address}
        response = public_api_client.do_repay(payload)
        assert response.status_code in (400, 404)
        data = response.json()
        assert data["status"] == "error"

    def test_do_repay_invalid_payload(self, public_api_client: PublicAPIClient):
        """缺少 body 字段时返回 422"""
        response = public_api_client.do_repay({})
        assert response.status_code == 422

    def test_do_repay_empty_address(self, public_api_client: PublicAPIClient):
        """address 为空字符串应返回 400"""
        response = public_api_client.do_repay({"address": ""})
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Invalid address: cannot be empty"
