"""Pytest 配置和 fixtures"""
import pytest
import os
from src.api_client import PublicAPIClient, InternalAPIClient


@pytest.fixture(scope="session")
def public_api_client() -> PublicAPIClient:
    """公共 API 客户端 fixture"""
    base_url = os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8080")
    return PublicAPIClient(base_url=base_url)


@pytest.fixture(scope="session")
def internal_api_client() -> InternalAPIClient:
    """内部 API 客户端 fixture"""
    base_url = os.getenv("INTERNAL_API_BASE_URL", "http://localhost:8081")
    return InternalAPIClient(base_url=base_url)


@pytest.fixture(scope="function")
def test_user_id():
    """测试用户 ID"""
    return "test_user_123"


@pytest.fixture(scope="function")
def test_position_id():
    """测试仓位 ID"""
    return "test_pos_456"


@pytest.fixture(scope="function", autouse=True)
def cleanup_mock_data(internal_api_client: InternalAPIClient):
    """测试前后清理 mock 数据"""
    # 测试前清理
    try:
        internal_api_client.clear_all_mock_md_prices()
    except Exception:
        pass

    yield

    # 测试后清理
    try:
        internal_api_client.clear_all_mock_md_prices()
    except Exception:
        pass

