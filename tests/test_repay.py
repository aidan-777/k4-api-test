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
        """未知账户查询还款：不同部署可能返回 404 或返回 0 值的 success"""
        response = public_api_client.repay_quote({"address": test_address})
        assert response.status_code in (200, 400, 404)
        data = response.json()
        if response.status_code == 200:
            assert data["status"] == "success"
            assert "redeem_amount" in data
        else:
            assert data.get("status") == "error"
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
        """未知账户执行还款：不同部署可能返回 404 或直接入队成功"""
        payload = {"address": test_address}
        response = public_api_client.do_repay(payload)
        assert response.status_code in (200, 400, 404)
        data = response.json()
        assert "status" in data

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

    @pytest.mark.real_wallet
    def test_repay_quote_and_partial_repay_flow(
        self,
        public_api_client: PublicAPIClient,
        cm_wallet_address: str,
        cm_user_id: str,
        # cm_run_real_tx: bool,
    ):
        """
        赎回/还款：
        - repay_quote 返回应还本金+利息
        - do_repay 支持部分赎回请求（接口层面会接受并入队）

        该用例会先 do_loan 产生债务，需显式开启：
        `run_real_tx=true`（在 config.json/config.local.json 中设置）
        """
        # if not cm_run_real_tx:
        #     pytest.skip("Real-tx tests are disabled (set run_real_tx=true in config.json)")
        #
        # response = public_api_client.account_mode({"mode": "unified", "mainAddress": cm_wallet_address, "userId": cm_user_id})
        # assert response.status_code == 200
        #
        # quote_resp = public_api_client.loan_quote({"address": cm_wallet_address})
        # assert quote_resp.status_code == 200
        # # quote = quote_resp.json()
        # # max_borrowed = float(quote["max_borrowed_amount"])
        # # borrow_value = min(200.0, max_borrowed / 10.0)
        #
        # borrow_value = 5
        # loan_payload = {
        #     "user_id": cm_user_id,
        #     "address": cm_wallet_address,
        #     "intent_borrow_asset": "HyperliquidUSDC",
        #     "intent_borrow_value": str(borrow_value),
        #     "destination": "perps",
        # }
        #
        # loan_resp = public_api_client.do_loan(loan_payload)
        # assert loan_resp.status_code == 200

        repay_quote_resp = public_api_client.repay_quote({"address": cm_wallet_address})
        assert repay_quote_resp.status_code == 200
        repay_quote = repay_quote_resp.json()
        # assert repay_quote["status"] == "success"
        # assert repay_quote["redeem_amount"] >= 0.0

        # 部分赎回（接口层面接收并入队，实际结算由后端异步处理）
        do_repay_resp = public_api_client.do_repay({"address": cm_wallet_address, "usdc_to_repay": 3.0})
        assert do_repay_resp.status_code == 200
        data = do_repay_resp.json()
        assert data["status"] == "success"
