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

    def get_metrics(self) -> requests.Response:
        """获取 metrics 重定向"""
        return self.get("/api/v1/metrics", allow_redirects=False)

    def get_general_info(self) -> requests.Response:
        """获取利率和抵押品信息"""
        return self.get("/api/v1/general_info")

    def exchange(self, payload: Dict[str, Any], authorization: Optional[str] = None) -> requests.Response:
        """发送交易代理请求"""
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        return self.post("/api/v1/exchange", json=payload, headers=headers or None)

    def loan_quote(self, payload: Dict[str, Any]) -> requests.Response:
        """获取借款报价"""
        return self.post("/api/v1/loan_quote", json=payload)

    def do_loan(
        self,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """执行借款"""
        merged_headers = dict(headers) if headers else {}
        if user_id:
            merged_headers["X-User-Id"] = user_id
        return self.post("/api/v1/do_loan", json=payload, headers=merged_headers or None)

    def repay_quote(self, payload: Dict[str, Any]) -> requests.Response:
        """获取还款报价"""
        return self.post("/api/v1/repay_quote", json=payload)

    def do_repay(self, payload: Dict[str, Any]) -> requests.Response:
        """执行还款"""
        return self.post("/api/v1/do_repay", json=payload)

    def account_mode(
        self,
        payload: Dict[str, Any],
        authorization: Optional[str] = None,
    ) -> requests.Response:
        """切换账户模式"""
        headers = {}
        if authorization:
            headers["Authorization"] = authorization
        return self.post("/api/v1/account_mode", json=payload, headers=headers or None)

    def do_param_update(self, payload: Optional[Dict[str, Any]] = None) -> requests.Response:
        """参数更新占位接口"""
        return self.post("/api/v1/do_param_update", json=payload)

    def get_account_by_ids(self, payload: Dict[str, Any]) -> requests.Response:
        """批量查询账户"""
        return self.post("/api/v1/get_account_by_ids", json=payload)

    def get_assets_by_ids(self, payload: Dict[str, Any]) -> requests.Response:
        """批量查询资产"""
        return self.post("/api/v1/get_assets_by_ids", json=payload)

    def get_accounts(self) -> requests.Response:
        """查询全部账户"""
        return self.post("/api/v1/get_accounts")

    def operation_history(self, payload: Dict[str, Any]) -> requests.Response:
        """查询操作历史"""
        return self.post("/api/v1/operation_history", json=payload)

    def interest_history(self, payload: Dict[str, Any]) -> requests.Response:
        """查询利息历史"""
        return self.post("/api/v1/interest_history", json=payload)


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

    def add_mock_position(self, payload: Dict[str, Any]) -> requests.Response:
        """添加测试持仓（当前未实现）"""
        return self.post("/api/internal/add_mock_position", json=payload)

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

    def set_mock_md_depth(self, payload: Dict[str, Any]) -> requests.Response:
        """设置模拟深度"""
        return self.post("/api/internal/mock_md_depth", json=payload)

    def clear_mock_md_depth(self, payload: Dict[str, Any]) -> requests.Response:
        """清除指定交易对的模拟深度"""
        return self.post("/api/internal/clear_mock_md_depth", json=payload)

    def clear_all_mock_md_depths(self) -> requests.Response:
        """清除全部模拟深度"""
        return self.post("/api/internal/clear_all_mock_md_depths")
