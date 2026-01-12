"""Pytest 配置和 fixtures"""
import os
import uuid
import secrets

import pytest
import requests

from src.api_client import InternalAPIClient, PublicAPIClient
from src.test_config import load_test_config


def _bootstrap_env_from_config() -> None:
    """
    将 config.local.json/config.json 中的配置同步到环境变量。

    目的：
    - 兼容 Tavern YAML 测试（常用 {tavern.env_vars.*} 读取变量，发生在 collection 阶段）
    - 兼容旧的 .env / 环境变量用法
    """
    cfg = load_test_config()
    os.environ.setdefault(
        "PUBLIC_API_BASE_URL",
        cfg.public_api_base_url or "http://localhost:8080",
    )
    os.environ.setdefault(
        "INTERNAL_API_BASE_URL",
        cfg.internal_api_base_url or "http://localhost:8081",
    )

    os.environ.setdefault("CM_WALLET_ADDRESS", cfg.wallet.address or "")
    os.environ.setdefault("CM_USER_ID", cfg.wallet.user_id or "")
    os.environ.setdefault("CM_AUTHORIZATION", cfg.wallet.authorization or "")

    os.environ.setdefault("CM_SPOT_BTC_ASSET", str(cfg.wallet.spot_btc_asset or 10142))
    os.environ.setdefault("CM_SPOT_BUY_SIZE", cfg.wallet.spot_buy_size or "")
    os.environ.setdefault("CM_SPOT_BUY_PRICE", cfg.wallet.spot_buy_price or "")
    os.environ.setdefault("CM_USDC_ONLY_ADDRESS", cfg.wallet.usdc_only_address or "")
    os.environ.setdefault("CM_MULTI_COLLATERAL_ADDRESS", cfg.wallet.multi_collateral_address or "")

    # run_real_tx：用 env var 也可控制（优先级低于 config 文件）
    os.environ.setdefault("CM_RUN_REAL_TX", "true" if cfg.run_real_tx else "false")


_bootstrap_env_from_config()


def _require_cfg(value, key: str) -> str:
    if not value:
        pytest.skip(f"Missing config value: {key} (set it in config.json/config.local.json)")
    return value


def _require_uuid_cfg(value, key: str) -> str:
    value = _require_cfg(value, key)
    try:
        uuid.UUID(value)
    except ValueError:
        pytest.skip(f"Config {key} must be a UUID, got: {value!r}")
    return value


@pytest.fixture(scope="session")
def public_api_client() -> PublicAPIClient:
    """公共 API 客户端 fixture"""
    cfg = load_test_config()
    base_url = cfg.public_api_base_url or os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8080")
    return PublicAPIClient(base_url=base_url)


@pytest.fixture(scope="session")
def internal_api_client() -> InternalAPIClient:
    """内部 API 客户端 fixture"""
    cfg = load_test_config()
    base_url = cfg.internal_api_base_url or os.getenv("INTERNAL_API_BASE_URL", "http://localhost:8081")
    return InternalAPIClient(base_url=base_url)


@pytest.fixture(scope="function")
def test_user_id():
    """测试用户 ID"""
    return "test_user_123"


@pytest.fixture(scope="function")
def test_position_id():
    """测试仓位 ID"""
    return "test_pos_456"


@pytest.fixture(scope="function")
def test_address():
    """默认测试地址（随机，避免依赖链上/缓存的特殊地址）"""
    return f"0x{secrets.token_hex(20)}"


@pytest.fixture(scope="function")
def test_user_uuid():
    """默认测试用户 UUID"""
    return str(uuid.uuid4())


@pytest.fixture(scope="function", autouse=True)
def cleanup_mock_data(
    request,
):
    """测试前后清理 mock 数据"""
    # internal API 已不再测试，这里保持空 fixture，避免历史用例依赖导致报错。
    yield

@pytest.fixture(scope="session")
def cm_wallet_address() -> str:
    """
    可选：真实钱包地址（用于集成测试）。

    在 `config.json/config.local.json` 中设置 `wallet.address` 后启用相关用例。
    """
    cfg = load_test_config()
    return _require_cfg(cfg.wallet.address, "wallet.address")


@pytest.fixture(scope="session")
def cm_user_id() -> str:
    """
    可选：测试用户 UUID（用于 do_loan 等需要 user_id 的接口）。
    """
    cfg = load_test_config()
    return _require_uuid_cfg(cfg.wallet.user_id, "wallet.user_id")


@pytest.fixture(scope="session")
def cm_authorization() -> str:
    """
    可选：wallet-service 的 Authorization（用于 /api/v1/exchange 等需要解析 user_id 的接口）。
    """
    cfg = load_test_config()
    return _require_cfg(cfg.wallet.authorization, "wallet.authorization")


@pytest.fixture(scope="session")
def cm_run_real_tx() -> bool:
    """
    是否允许运行会产生真实副作用的测试（如 do_loan / transfer 等）。

    在 `config.json/config.local.json` 中设置 `run_real_tx=true` 后启用。
    """
    cfg = load_test_config()
    return bool(cfg.run_real_tx)


@pytest.fixture(scope="session")
def cm_account_mode_payload():
    """
    生成 account_mode 标准 payload：接口需要传 userId。
    """
    def _build(*, mode: str, main_address: str, user_id: str):
        return {"mode": mode, "mainAddress": main_address, "userId": user_id}

    return _build


@pytest.fixture(scope="session")
def cm_spot_btc_asset() -> int:
    cfg = load_test_config()
    return int(cfg.wallet.spot_btc_asset or 10142)


@pytest.fixture(scope="session")
def cm_spot_buy_size() -> str:
    cfg = load_test_config()
    return cfg.wallet.spot_buy_size or "0.0001"


@pytest.fixture(scope="session")
def cm_spot_buy_price() -> str:
    cfg = load_test_config()
    return cfg.wallet.spot_buy_price or "1"


@pytest.fixture(scope="session")
def cm_usdc_only_address() -> str:
    cfg = load_test_config()
    return cfg.wallet.usdc_only_address or ""


@pytest.fixture(scope="session")
def cm_multi_collateral_address() -> str:
    cfg = load_test_config()
    return cfg.wallet.multi_collateral_address or ""


@pytest.fixture(scope="session")
def _public_api_reachable(public_api_client: PublicAPIClient) -> bool:
    try:
        resp = public_api_client.ping()
        return resp.status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(scope="session")
def _internal_api_reachable(internal_api_client: InternalAPIClient) -> bool:
    try:
        resp = internal_api_client.ping()
        return resp.status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(autouse=True)
def _skip_if_api_unreachable(
    request,
    _public_api_reachable: bool,
):
    """
    避免在未配置/未启动服务时把整套用例刷成 ConnectionRefusedError。

    - 绝大多数测试依赖 PUBLIC_API
    - 标记了 internal 的测试依赖 INTERNAL_API
    """
    needs_internal = (
        request.node.get_closest_marker("internal") is not None
        or request.node.get_closest_marker("market") is not None
    )
    if needs_internal:
        pytest.skip("Internal API tests are disabled (not needed)")
    if not needs_internal and not _public_api_reachable:
        pytest.skip(
            "Public API is unreachable. Set public_api_base_url in config.json/config.local.json."
        )

    yield
