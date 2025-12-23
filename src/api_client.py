"""API 客户端工具类"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    """API 客户端，封装 HTTP 请求"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        初始化 API 客户端

        Args:
            base_url: API 基础 URL，默认从环境变量读取
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url or os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8080")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get(self, path: str, **kwargs) -> requests.Response:
        """发送 GET 请求"""
        url = f"{self.base_url}{path}"
        return self.session.get(url, timeout=self.timeout, **kwargs)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送 POST 请求"""
        url = f"{self.base_url}{path}"
        return self.session.post(url, json=json, timeout=self.timeout, **kwargs)

    def put(self, path: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """发送 PUT 请求"""
        url = f"{self.base_url}{path}"
        return self.session.put(url, json=json, timeout=self.timeout, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        """发送 DELETE 请求"""
        url = f"{self.base_url}{path}"
        return self.session.delete(url, timeout=self.timeout, **kwargs)


class PublicAPIClient(APIClient):
    """公共 API 客户端"""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        base_url = base_url or os.getenv("PUBLIC_API_BASE_URL", "http://localhost:8080")
        super().__init__(base_url, timeout)

    def ping(self) -> requests.Response:
        """健康检查 - ping"""
        return self.get("/ping")

    def health_check(self) -> requests.Response:
        """健康检查 - hc"""
        return self.get("/hc")

    def get_status(self) -> requests.Response:
        """获取系统状态"""
        return self.get("/api/v1/status")

    def quest_loan_amount(self, collateral_assets: Dict[str, str]) -> requests.Response:
        """获取借款报价"""
        return self.post("/api/v1/quest_loan_amount", json={"collateral_assets": collateral_assets})

    def do_loan(self, payload: Dict[str, Any]) -> requests.Response:
        """执行借款"""
        return self.post("/api/v1/do_loan", json=payload)

    def quest_redeem_amount(self, user_id: str, position_id: str) -> requests.Response:
        """查询应还本金+利息"""
        return self.post("/api/v1/quest_redeem_amount", json={
            "user_id": user_id,
            "position_id": position_id,
        })

    def do_redeem(self, user_id: str, position_id: str) -> requests.Response:
        """执行赎回"""
        return self.post("/api/v1/do_redeem", json={
            "user_id": user_id,
            "position_id": position_id,
        })

    def user_close_position(self, user_id: str, position_id: str) -> requests.Response:
        """用户发起平仓"""
        return self.post("/api/v1/user_close_position", json={
            "user_id": user_id,
            "position_id": position_id,
        })

    def add_margin(self, payload: Dict[str, Any]) -> requests.Response:
        """增加保证金"""
        return self.post("/api/v1/add_margin", json=payload)


class InternalAPIClient(APIClient):
    """内部 API 客户端"""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        base_url = base_url or os.getenv("INTERNAL_API_BASE_URL", "http://localhost:8081")
        super().__init__(base_url, timeout)

    def ping(self) -> requests.Response:
        """健康检查 - ping"""
        return self.get("/ping")

    def health_check(self) -> requests.Response:
        """健康检查 - hc"""
        return self.get("/hc")

    def add_mock_position(
        self,
        user_id: str,
        position_id: str,
        borrowed_asset: str,
        borrowed_amount: float,
        collateral_assets: Dict[str, float],
    ) -> requests.Response:
        """添加测试持仓"""
        return self.post("/api/internal/add_mock_position", json={
            "user_id": user_id,
            "position_id": position_id,
            "borrowed_asset": borrowed_asset,
            "borrowed_amount": borrowed_amount,
            "collateral_assets": collateral_assets,
        })

    def set_mock_md_price(self, symbol: str, price: float) -> requests.Response:
        """设置模拟行情价格"""
        return self.post("/api/internal/mock_md_price", json={
            "symbol": symbol,
            "price": price,
        })

    def clear_mock_md_price(self, symbol: str) -> requests.Response:
        """清除指定模拟价格"""
        return self.post("/api/internal/clear_mock_md_price", json={
            "symbol": symbol,
        })

    def clear_all_mock_md_prices(self) -> requests.Response:
        """清除全部模拟价格"""
        return self.post("/api/internal/clear_all_mock_md_prices")

