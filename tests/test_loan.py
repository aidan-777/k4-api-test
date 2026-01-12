"""借款相关接口测试"""

import pytest
from src.api_client import PublicAPIClient
from src.api_client import InternalAPIClient


def _loan_payload(*, user_id: str, address: str, borrow_value: str, destination: str = "spot") -> dict:
    return {
        "user_id": user_id,
        "address": address,
        "intent_borrow_asset": "HyperliquidUSDC",
        "intent_borrow_value": borrow_value,
        "destination": destination,
    }


@pytest.mark.loan
class TestLoanAPI:
    """借款接口测试类"""

    def test_loan_quote_success_with_wallet_address(
        self,
        public_api_client: PublicAPIClient,
        cm_wallet_address: str,
        cm_user_id: str,
        cm_account_mode_payload,
    ):
        """
        正向用例：对一个“已存在且有资产余额”的地址，loan_quote 应返回可借额度信息。

        说明：
        - 当前测试仓库没有可用的“创建 mock 账户/余额”的 internal API（add_mock_position 未实现），
          所以正向用例需要你提供一个真实/已注册的地址。
        - 该用例不会执行 do_loan，不会触发转账等强副作用。
        """
        # 触发账户加载/写库/加入 ledger（服务侧不依赖 wallet-service）
        resp = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert resp.status_code == 200

        response = public_api_client.loan_quote({"address": cm_wallet_address})
        assert response.status_code == 200
        data = response.json()
        assert "borrowed_asset" in data
        assert "max_borrowed_amount" in data
        assert "created_at" in data
        assert "expires_at" in data

    def test_loan_quote_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
    ):
        """请求未知地址的借款报价：通常应返回错误（或根据实现返回可借额度）"""
        response = public_api_client.loan_quote({"address": test_address})
        assert response.status_code in (200, 400, 404, 503)
        data = response.json()
        if response.status_code == 200:
            assert "max_borrowed_amount" in data
        else:
            # 不同版本可能是 {status,error,message} 或 {error,message}
            assert "message" in data or "error" in data

    def test_loan_quote_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 address 时返回 422"""
        response = public_api_client.loan_quote({})
        assert response.status_code == 422

    def test_do_loan_validation_error(self, public_api_client: PublicAPIClient):
        """缺少 body 字段时返回 422"""
        response = public_api_client.do_loan({})
        assert response.status_code == 422

    def test_do_loan_account_not_found(
        self,
        public_api_client: PublicAPIClient,
        test_address: str,
        test_user_uuid: str,
    ):
        """未知账户发起借款应失败"""
        payload = _loan_payload(user_id=test_user_uuid, address=test_address, borrow_value="100")
        response = public_api_client.do_loan(payload)
        assert response.status_code in (400, 404, 503)
        data = response.json()
        assert data.get("status") == "error" or "error" in data

    @pytest.mark.real_wallet
    def test_do_loan_with_real_wallet(
        self,
        public_api_client: PublicAPIClient,
        cm_wallet_address: str,
        cm_user_id: str,
        cm_account_mode_payload,
    ):
        """
        持有抵押物（当前环境通常是 BTC）借 USDC。

        该用例会触发真实转账/记账副作用，需显式开启：
        `run_real_tx=true`（在 config.json/config.local.json 中设置）
        """
        response = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert response.status_code == 200

        quote_resp = public_api_client.loan_quote({"address": cm_wallet_address})
        assert quote_resp.status_code == 200
        # quote = quote_resp.json()
        # max_borrowed = float(quote["max_borrowed_amount"])
        # borrow_value = min(15.0, 200.0, max_borrowed / 10.0) if max_borrowed > 0 else 15.0
        borrow_value = 2
        payload = _loan_payload(
            user_id=cm_user_id,
            address=cm_wallet_address,
            borrow_value=str(borrow_value),
            destination="spot",
        )
        response = public_api_client.do_loan(payload)
        assert response.status_code == 200
        data = response.json()
        assert data["address"] == cm_wallet_address.lower()
        assert data["borrowed_asset"] == "HyperliquidUSDC"

    @pytest.mark.real_wallet
    def test_do_loan_quote_outdated_when_price_drops(
        self,
        public_api_client: PublicAPIClient,
        internal_api_client: InternalAPIClient,
        cm_wallet_address: str,
        cm_user_id: str,
        cm_run_real_tx: bool,
    ):
        """
        报价后长时间未确认/行情剧烈波动：通过 mock 下调 BTC 价格来模拟“报价失效”。

        注意：该用例会尝试发起 do_loan（可能触发真实转账），需显式开启：
        `run_real_tx=true`（在 config.json/config.local.json 中设置）
        """
        if not cm_run_real_tx:
            pytest.skip("Real-tx tests are disabled (set run_real_tx=true in config.json)")

        # 价格拉高，获取一个更大的 max_borrowed_amount
        response = internal_api_client.set_mock_md_price("BTC", 50_000.0)
        assert response.status_code == 200

        response = public_api_client.account_mode({"mode": "unified", "mainAddress": cm_wallet_address})
        assert response.status_code == 200

        quote_resp = public_api_client.loan_quote({"address": cm_wallet_address})
        assert quote_resp.status_code == 200
        quote = quote_resp.json()
        desired = str(quote["max_borrowed_amount"])

        # 价格大幅下调，导致 allowance 大幅下降，do_loan 应返回 quote_outdated/insufficient_collateral
        response = internal_api_client.set_mock_md_price("BTC", 1_000.0)
        assert response.status_code == 200

        payload = _loan_payload(user_id=cm_user_id, address=cm_wallet_address, borrow_value=desired)
        resp = public_api_client.do_loan(payload)
        assert resp.status_code in (400, 404)
        data = resp.json()
        assert data.get("status") == "error"
        assert data.get("error") in ("quote_outdated", "insufficient_collateral", "loan_amount_too_small")

    @pytest.mark.real_wallet
    def test_do_loan_with_usdc_collateral_if_supported(
        self,
        public_api_client: PublicAPIClient,
        cm_user_id: str,
        cm_usdc_only_address: str,
        cm_run_real_tx: bool,
    ):
        """
        持 USDC 借 USDC（仅当服务支持 USDC 作为抵押物时运行）。
        通过配置 `wallet.usdc_only_address` 指定“仅持有 USDC/或主要为 USDC”的地址。
        """
        if not cm_run_real_tx:
            pytest.skip("Real-tx tests are disabled (set run_real_tx=true in config.json)")

        if not cm_usdc_only_address:
            pytest.skip("Missing config: wallet.usdc_only_address")
        address = cm_usdc_only_address

        info = public_api_client.get_general_info().json()
        if "USDC" not in info.get("assets", {}):
            pytest.skip("USDC collateral not supported in this deployment")

        response = public_api_client.account_mode({"mode": "unified", "mainAddress": address})
        assert response.status_code == 200

        quote_resp = public_api_client.loan_quote({"address": address})
        assert quote_resp.status_code == 200
        quote = quote_resp.json()
        max_borrowed = float(quote["max_borrowed_amount"])
        borrow_value = min(200.0, max_borrowed / 10.0)

        payload = _loan_payload(user_id=cm_user_id, address=address, borrow_value=str(borrow_value))
        resp = public_api_client.do_loan(payload)
        assert resp.status_code == 200

    @pytest.mark.real_wallet
    def test_do_loan_with_multi_collateral_if_supported(
        self,
        public_api_client: PublicAPIClient,
        cm_user_id: str,
        cm_multi_collateral_address: str,
        cm_run_real_tx: bool,
    ):
        """
        持多种抵押物借 USDC（仅当服务提供 >=2 种抵押物资产并且地址确实持有时运行）。
        通过配置 `wallet.multi_collateral_address` 指定多资产地址。
        """
        if not cm_run_real_tx:
            pytest.skip("Real-tx tests are disabled (set run_real_tx=true in config.json)")

        if not cm_multi_collateral_address:
            pytest.skip("Missing config: wallet.multi_collateral_address")
        address = cm_multi_collateral_address

        info = public_api_client.get_general_info().json()
        assets = list(info.get("assets", {}).keys())
        if len(assets) < 2:
            pytest.skip("Multi-collateral not supported in this deployment")

        response = public_api_client.account_mode({"mode": "unified", "mainAddress": address})
        assert response.status_code == 200

        quote_resp = public_api_client.loan_quote({"address": address})
        assert quote_resp.status_code == 200
        quote = quote_resp.json()
        max_borrowed = float(quote["max_borrowed_amount"])
        borrow_value = min(200.0, max_borrowed / 10.0)

        payload = _loan_payload(user_id=cm_user_id, address=address, borrow_value=str(borrow_value))
        resp = public_api_client.do_loan(payload)
        assert resp.status_code == 200
