"""可选端点测试：不同部署版本可能未实现"""

import pytest

from src.api_client import PublicAPIClient


@pytest.mark.margin
class TestMarginOptional:
    def test_add_margin_endpoint_exists_or_skipped(self, public_api_client: PublicAPIClient):
        """
        保证金相关接口在不同版本可能不存在。
        - 若返回 404：跳过
        - 若存在：至少应对非法 payload 做出明确响应
        """
        resp = public_api_client.add_margin({})
        if resp.status_code == 404:
            pytest.skip("add_margin endpoint not available in this deployment")
        assert resp.status_code in (400, 401, 403, 422)


@pytest.mark.position
class TestPositionOptional:
    def test_user_close_position_endpoint_exists_or_skipped(self, public_api_client: PublicAPIClient):
        resp = public_api_client.user_close_position({})
        if resp.status_code == 404:
            pytest.skip("user_close_position endpoint not available in this deployment")
        assert resp.status_code in (400, 401, 403, 422)

