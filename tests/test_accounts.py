"""账户查询及模式切换接口测试"""
import pytest
from src.api_client import PublicAPIClient


@pytest.mark.accounts
class TestAccountAPIs:
    """账户相关接口测试"""

    def test_get_accounts_returns_snapshot(self, public_api_client: PublicAPIClient):
        """获取全部账户应返回标准结构"""
        response = public_api_client.get_accounts()
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "count" in data
        assert "accounts" in data

    def test_get_account_by_ids_empty(self, public_api_client: PublicAPIClient):
        """空列表请求返回成功且数量为 0"""
        response = public_api_client.get_account_by_ids({"account_ids": []})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 0
        assert data["total_found"] == 0

    def test_get_account_by_ids(self, public_api_client: PublicAPIClient, cm_wallet_address: str):
        """请求 1 个 account_id：total_requested 应为 1，found 取决于后端是否已缓存/入库"""
        response = public_api_client.get_account_by_ids({"account_ids": [cm_wallet_address]})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 1
        assert data["total_found"] in (0, 1)

    def test_get_assets_by_ids_empty(self, public_api_client: PublicAPIClient):
        """空列表资产查询返回成功"""
        response = public_api_client.get_assets_by_ids({"account_ids": []})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 0
        assert data["total_found"] == 0

    def test_get_assets_by_ids(self, public_api_client: PublicAPIClient, cm_wallet_address: str):
        """空列表资产查询返回成功"""
        response = public_api_client.get_assets_by_ids({"account_ids": [cm_wallet_address]})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_requested"] == 0
        assert data["total_found"] == 0

    def test_operation_history_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 的请求应被拒绝"""
        response = public_api_client.operation_history({})
        assert response.status_code == 422

    def test_interest_history_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 的请求应被拒绝"""
        response = public_api_client.interest_history({})
        assert response.status_code == 422

    def test_switch_to_unified_mode(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_user_id: str,
            cm_account_mode_payload,
    ):
        response = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "unified"

    def test_switch_to_basic_mode_no_debt(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_user_id: str,
            cm_account_mode_payload,
    ):
        """
        切换到 basic mode：要求无未偿债务。
        """
        response = public_api_client.account_mode(
            cm_account_mode_payload(mode="basic", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "basic"

    @pytest.mark.real_wallet
    def test_reject_basic_mode_when_unpaid_debt(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_user_id: str,
            cm_account_mode_payload,
    ):
        """
        有未偿债务时，拒绝切换回 basic mode。

        该用例需要先成功 do_loan 产生债务，属于真实副作用测试，需显式开启：
        `run_real_tx=true`（在 config.json/config.local.json 中设置）
        """
        response = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert response.status_code == 200

        quote_resp = public_api_client.loan_quote({"address": cm_wallet_address})
        assert quote_resp.status_code == 200
        quote = quote_resp.json()
        max_borrowed = float(quote["max_borrowed_amount"])
        borrow_value = min(200.0, max_borrowed / 10.0)

        loan_payload = {
            "user_id": cm_user_id,
            "address": cm_wallet_address,
            "intent_borrow_asset": "HypercorePerpsUSDC",
            "intent_borrow_value": str(borrow_value),
            "destination": "spot",
        }
        loan_resp = public_api_client.do_loan(loan_payload)
        assert loan_resp.status_code == 200

        resp = public_api_client.account_mode({"mode": "basic", "mainAddress": cm_wallet_address})
        assert resp.status_code == 400
        data = resp.json()
        assert "Account has outstanding debt" in data.get("error", "") or "debt" in data.get(
            "error", ""
        )
