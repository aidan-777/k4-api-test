"""交易代理 /exchange 接口测试"""

import time
from typing import Optional

import pytest

from src.api_client import PublicAPIClient


def _spot_limit_order_action(*, asset: int, is_buy: bool, sz: str, px: str) -> dict:
    return {
        "type": "order",
        "orders": [
            {
                "asset": asset,
                "isBuy": is_buy,
                "limitPx": px,
                "sz": sz,
                "reduceOnly": False,
                "orderType": {"limit": {"tif": "Gtc"}},
            }
        ],
        "grouping": "na",
    }

def _send_asset_action(
    *,
    destination: str,
    source_dex: str,
    destination_dex: str,
    token: str,
    amount: str,
    nonce: Optional[int] = None,
) -> dict:
    """
    sendAsset 用于 spot/perp 之间的资产互转（服务侧可能会禁用 outbound transfer）。
    """
    nonce = int(nonce or (time.time() * 1000))
    return {
        "type": "sendAsset",
        # 0x66eee == 421614 (Arbitrum Sepolia)，示例里是 hex 字符串；服务实现通常按整数反序列化
        "signatureChainId": 421614,
        "hyperliquidChain": "Mainnet",
        "destination": destination,
        "sourceDex": source_dex,
        "destinationDex": destination_dex,
        "token": token,
        "amount": amount,
        "fromSubAccount": "",
        "nonce": nonce,
    }


@pytest.mark.exchange
class TestExchangeAPI:
    def test_exchange_requires_wallet_address(self, public_api_client: PublicAPIClient):
        response = public_api_client.exchange({"action": {"type": "cancel", "cancels": []}})
        assert response.status_code in (400, 422)

    def test_exchange_unauthorized_without_authorization(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_spot_btc_asset: int,
            cm_user_id: str,
            cm_account_mode_payload,
    ):
        """
        /exchange 会通过 wallet-service 解析 user_id；无 Authorization 时应拒绝。
        """
        # 先确保 account_mode 通过（接口需要 userId）
        resp = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert resp.status_code == 200

        payload = {
            "userId": cm_user_id,
            "walletAddress": cm_wallet_address,
            "action": _spot_limit_order_action(asset=cm_spot_btc_asset, is_buy=True, sz="0.0001", px="1"),
        }
        response = public_api_client.exchange(payload)
        assert response.status_code in (401, 403, 422, 502)

    @pytest.mark.real_wallet
    def test_exchange_spot_buy_collateral_asset_succeeds_guard_and_sign(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_authorization: str,
            cm_spot_btc_asset: int,
            cm_spot_buy_size: str,
            cm_spot_buy_price: str,
    ):
        """
        买入抵押物中的现货（例如 BTC）：
        - 风控 guard 通过
        - 返回签名后的 payload
        """
        # 先确保地址已被系统识别（会触发账户载入/写库/加入 ledger）
        response = public_api_client.account_mode({"mode": "unified", "mainAddress": cm_wallet_address})
        assert response.status_code == 200

        payload = {
            "walletAddress": cm_wallet_address,
            "action": _spot_limit_order_action(
                asset=cm_spot_btc_asset,
                is_buy=True,
                sz=cm_spot_buy_size,
                px=cm_spot_buy_price,
            ),
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)
        assert response.status_code == 200
        data = response.json()
        assert "payload" in data
        assert "action" in data["payload"]

    @pytest.mark.real_wallet
    def test_exchange_spot_buy_non_collateral_asset_rejected(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_authorization: str,
    ):
        """
        买入非抵押物中的现货：如果 spot symbol 不在允许列表，应被拒绝（或识别失败）。
        """
        response = public_api_client.account_mode({"mode": "unified", "mainAddress": cm_wallet_address})
        assert response.status_code == 200

        payload = {
            "walletAddress": cm_wallet_address,
            "action": _spot_limit_order_action(asset=10142, is_buy=True, sz="0.0001", px="95000"),
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)
        assert response.status_code in (400, 403)

    @pytest.mark.real_wallet
    def test_exchange_subaccount_transfer_outbound_disabled(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_authorization: str,
    ):
        """
        现货/合约互转资金（subAccountTransfer，出金方向）当前服务会直接禁用。
        """
        payload = {
            "walletAddress": cm_wallet_address,
            "action": {
                "type": "subAccountTransfer",
                "subAccountUser": cm_wallet_address,
                "isDeposit": False,
                "usd": 1,
            },
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)
        assert response.status_code == 403

    @pytest.mark.real_wallet
    @pytest.mark.parametrize(
        ("source_dex", "destination_dex"),
        [
            ("perp", "spot"),  # perps -> spot
            ("spot", "perp"),  # spot -> perps
        ],
    )
    def test_exchange_spot_perp_transfer_send_asset(
        self,
        public_api_client: PublicAPIClient,
        cm_wallet_address: str,
        cm_authorization: str,
        cm_user_id: str,
        cm_account_mode_payload,
        source_dex: str,
        destination_dex: str,
    ):
        """
        现货 <-> 合约互转（sendAsset）：
        - 若服务允许：返回 200 + signed payload
        - 若服务禁用 outbound transfer：返回 403 + outbound_transfer_disabled
        """
        resp = public_api_client.account_mode(
            cm_account_mode_payload(mode="unified", main_address=cm_wallet_address, user_id=cm_user_id)
        )
        assert resp.status_code == 200

        payload = {
            "userId": cm_user_id,
            "walletAddress": cm_wallet_address,
            "action": _send_asset_action(
                destination=cm_wallet_address,
                source_dex=source_dex,
                destination_dex=destination_dex,
                token="USDC:0x6d1e7cde53ba9467b783cb7c530ce054",
                amount="10",
            ),
            "isMainnet": True,
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)

        if response.status_code == 403:
            data = response.json()
            assert data.get("error") in ("outbound_transfer_disabled", "This action is not allowed by api")
            return

        assert response.status_code == 200, response.text
        data = response.json()
        assert "payload" in data
        assert data["payload"]["action"]["type"] == "sendAsset"
        assert data["payload"]["action"]["destinationDex"] == destination_dex

    @pytest.mark.real_wallet
    def test_exchange_perp_order_not_supported_by_api(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_authorization: str,
    ):
        """
        开合约仓位（永续 order）在当前 /exchange API 层面通常被禁用，仅允许现货订单。
        """
        payload = {
            "walletAddress": cm_wallet_address,
            "action": _spot_limit_order_action(asset=1, is_buy=True, sz="1", px="1"),
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)
        assert response.status_code == 403

    @pytest.mark.real_wallet
    def test_exchange_debug(
            self,
            public_api_client: PublicAPIClient,
            cm_wallet_address: str,
            cm_authorization: str,
            cm_user_id
    ):
        """
        debug
        """
        payload = {
            "userId": cm_user_id,
            "action": {
                "orders": [
                    {
                        "a": 10142,
                        "b": True,
                        "p": "89000",
                        "s": "0.00014",
                        "r": False,
                        "t": {
                            "limit": {
                                "tif": "GTC"
                            }
                        }
                    }
                ],
                "grouping": "na",
                "builder": {
                    "b": "0xcdb943570bcb48a6f1d3228d0175598fea19e87b",
                    "f": 17
                },
                "type": "order"
            },
            "isMainnet": True,
            "walletAddress": "0xdb2ca1bc72336b66d4c5889cc90d48723364efc5"
        }
        response = public_api_client.exchange(payload, authorization=cm_authorization)
        assert response.status_code == 403

        @pytest.mark.real_wallet
        def test_exchange_debug_transfer(
                self,
                public_api_client: PublicAPIClient,
                cm_wallet_address: str,
                cm_authorization: str,
                cm_user_id
        ):
            """
            debug
            """

            response = public_api_client.exchange(payload, authorization=cm_authorization)
            assert response.status_code == 403
