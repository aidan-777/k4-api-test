"""参数相关接口测试"""
import pytest
from src.api_client import PublicAPIClient


@pytest.mark.params
class TestParamAPI:
    """参数更新占位接口测试"""

    def test_do_param_update_returns_placeholder(self, public_api_client: PublicAPIClient):
        """接口应返回 unimplemented 占位信息"""
        response = public_api_client.do_param_update({"foo": "bar"})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "unimplemented"

    def test_do_param_update_empty_payload(self, public_api_client: PublicAPIClient):
        """空 payload 也应返回占位信息"""
        response = public_api_client.do_param_update()
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "unimplemented"
