"""Test configuration loader.

Prefer config files over environment variables to reduce setup friction.
Resolution order:
1) config.local.json (git-ignored)
2) config.json
3) environment variables (backward compatible)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must be a JSON object: {path}")
    return data


def _coalesce(*values):
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            continue
        return v
    return None


@dataclass(frozen=True)
class WalletConfig:
    address: Optional[str] = None
    user_id: Optional[str] = None
    authorization: Optional[str] = None
    spot_btc_asset: Optional[int] = None
    spot_buy_size: Optional[str] = None
    spot_buy_price: Optional[str] = None
    usdc_only_address: Optional[str] = None
    multi_collateral_address: Optional[str] = None


@dataclass(frozen=True)
class TestConfig:
    public_api_base_url: Optional[str] = None
    internal_api_base_url: Optional[str] = None
    enable_internal: bool = False
    run_real_tx: bool = False
    wallet: WalletConfig = WalletConfig()


_CACHED: Optional[TestConfig] = None


def load_test_config() -> TestConfig:
    global _CACHED
    if _CACHED is not None:
        return _CACHED

    root = _repo_root()
    raw: dict[str, Any] = {}
    for name in ("config.local.json", "config.json"):
        p = root / name
        if p.exists():
            raw = _read_json(p)
            break

    wallet_raw = raw.get("wallet") if isinstance(raw.get("wallet"), dict) else {}

    public_api_base_url = _coalesce(
        raw.get("public_api_base_url"),
        os.getenv("PUBLIC_API_BASE_URL"),
    )
    internal_api_base_url = _coalesce(
        raw.get("internal_api_base_url"),
        os.getenv("INTERNAL_API_BASE_URL"),
    )

    def _coerce_bool(value: Any, default: bool = False) -> bool:
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"1", "true", "yes", "y", "on"}:
                return True
            if v in {"0", "false", "no", "n", "off"}:
                return False
        return default

    enable_internal = _coerce_bool(raw.get("enable_internal"), default=False)
    run_real_tx = _coerce_bool(raw.get("run_real_tx"), default=False)

    def _wallet_get(key: str):
        return wallet_raw.get(key) if isinstance(wallet_raw, dict) else None

    wallet = WalletConfig(
        address=_coalesce(_wallet_get("address"), os.getenv("CM_WALLET_ADDRESS")),
        user_id=_coalesce(_wallet_get("user_id"), os.getenv("CM_USER_ID")),
        authorization=_coalesce(_wallet_get("authorization"), os.getenv("CM_AUTHORIZATION")),
        spot_btc_asset=_wallet_get("spot_btc_asset"),
        spot_buy_size=_coalesce(_wallet_get("spot_buy_size"), os.getenv("CM_SPOT_BUY_SIZE")),
        spot_buy_price=_coalesce(_wallet_get("spot_buy_price"), os.getenv("CM_SPOT_BUY_PRICE")),
        usdc_only_address=_coalesce(_wallet_get("usdc_only_address"), os.getenv("CM_USDC_ONLY_ADDRESS")),
        multi_collateral_address=_coalesce(
            _wallet_get("multi_collateral_address"),
            os.getenv("CM_MULTI_COLLATERAL_ADDRESS"),
        ),
    )

    _CACHED = TestConfig(
        public_api_base_url=public_api_base_url,
        internal_api_base_url=internal_api_base_url,
        enable_internal=enable_internal,
        run_real_tx=run_real_tx,
        wallet=wallet,
    )
    return _CACHED
