# Superstack Cross Margin API 测试项目

基于 pytest 的 API 接口测试项目，用于测试 superstack-cross-margin 服务的 HTTP API。

## 项目结构

```
api_tests/
├── src/                    # 源代码目录
│   ├── __init__.py
│   └── api_client.py      # API 客户端工具类
├── tests/                  # 测试用例目录
│   ├── __init__.py
│   ├── test_health.py     # 健康检查接口测试
│   ├── test_loan.py       # 借款相关接口测试
│   ├── test_redeem.py     # 赎回相关接口测试
│   ├── test_position.py   # 仓位相关接口测试
│   ├── test_margin.py     # 保证金相关接口测试
│   └── test_internal.py   # 内部接口测试
├── conftest.py            # Pytest 配置和 fixtures
├── pytest.ini             # Pytest 配置文件
├── requirements.txt       # Python 依赖
├── env.example            # 环境变量示例
├── Makefile              # Make 命令快捷方式
└── run_tests.sh          # 测试运行脚本
└── README.md              # 项目说明文档
```

## 安装和配置

### 1. 安装依赖

```bash
cd api_tests
pip install -r requirements.txt
```

或者使用虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

编辑 `.env` 文件：

```env
PUBLIC_API_BASE_URL=http://localhost:8080
INTERNAL_API_BASE_URL=http://localhost:8081
TIMEOUT=30
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_health.py
```

### 运行特定测试类

```bash
pytest tests/test_loan.py::TestLoanAPI
```

### 运行特定测试方法

```bash
pytest tests/test_health.py::TestHealthCheck::test_ping_public
```

### 按标记运行测试

```bash
# 只运行健康检查测试
pytest -m health

# 只运行借款相关测试
pytest -m loan

# 只运行内部接口测试
pytest -m internal

# 排除内部接口测试
pytest -m "not internal"
```

### 生成测试报告

```bash
# 生成 HTML 报告
pytest --html=reports/report.html --self-contained-html

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 详细输出

```bash
# 显示详细输出
pytest -v

# 显示最详细的输出
pytest -vv

# 显示 print 输出
pytest -s
```

## 测试分类

测试用例使用 pytest markers 进行分类：

- `@pytest.mark.health`: 健康检查相关测试
- `@pytest.mark.loan`: 借款相关测试
- `@pytest.mark.redeem`: 赎回相关测试
- `@pytest.mark.margin`: 保证金相关测试
- `@pytest.mark.position`: 仓位相关测试
- `@pytest.mark.internal`: 内部接口测试
- `@pytest.mark.mock`: Mock 数据相关测试

## API 接口覆盖

### 公共接口 (端口 8080)

- ✅ GET `/ping` - 服务连通性检查
- ✅ GET `/hc` - 运行健康状态
- ✅ GET `/api/v1/status` - 组件运行概览
- ✅ POST `/api/v1/quest_loan_amount` - 获取借款报价
- ✅ POST `/api/v1/do_loan` - 执行借款
- ✅ POST `/api/v1/quest_redeem_amount` - 查询应还本金+利息
- ✅ POST `/api/v1/do_redeem` - 赎回操作
- ✅ POST `/api/v1/user_close_position` - 用户发起平仓
- ✅ POST `/api/v1/add_margin` - 增加保证金

### 内部接口 (端口 8081)

- ✅ GET `/ping` - 服务连通性检查
- ✅ GET `/hc` - 运行健康状态
- ✅ POST `/api/internal/add_mock_position` - 添加测试持仓
- ✅ POST `/api/internal/mock_md_price` - 设置模拟行情价格
- ✅ POST `/api/internal/clear_mock_md_price` - 清除指定模拟价格
- ✅ POST `/api/internal/clear_all_mock_md_prices` - 清除全部模拟价格

## 使用说明

### API 客户端

项目提供了两个 API 客户端类：

1. **PublicAPIClient**: 用于访问公共 API（端口 8080）
2. **InternalAPIClient**: 用于访问内部 API（端口 8081）

在测试中使用 fixtures：

```python
def test_example(public_api_client: PublicAPIClient):
    response = public_api_client.ping()
    assert response.status_code == 200
```

### Fixtures

- `public_api_client`: 公共 API 客户端实例
- `internal_api_client`: 内部 API 客户端实例
- `test_user_id`: 测试用户 ID
- `test_position_id`: 测试仓位 ID
- `cleanup_mock_data`: 自动清理 mock 数据（每个测试前后）

## 注意事项

1. **服务运行**: 运行测试前确保 superstack-cross-margin 服务已启动
2. **端口配置**: 确保 `.env` 中的端口配置与服务实际端口一致
3. **Mock 数据**: 测试会自动清理 mock 数据，但建议在测试环境运行
4. **依赖顺序**: 某些测试需要先创建 mock 数据（如价格、仓位），测试会自动处理

## 持续集成

可以在 CI/CD 流程中使用：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest --html=reports/report.html --self-contained-html

# 检查退出码
echo $?
```

## 贡献

添加新测试时：

1. 在对应的测试文件中添加测试方法
2. 使用适当的 pytest marker 标记测试
3. 确保测试独立，不依赖其他测试的执行顺序
4. 使用 fixtures 管理测试数据和清理

## 许可证

与主项目保持一致。

