# 真实钱包地址测试指南

## 测试用例

已创建测试用例 `test_do_loan_with_real_wallet`，使用真实钱包地址 `0x44D609d8A2d26882d099f1ef8F8bea1A60121C09` 进行借贷测试。

## 前置条件

1. **钱包地址必须在 Hyperliquid 上注册**
   - 地址需要在 Hyperliquid 上有账户记录
   - 如果未注册，余额检查会失败

2. **钱包需要有足够的抵押资产**
   - 测试使用 0.25 BTC 作为抵押
   - 钱包中需要有足够的 UBTC（Hyperliquid 上的 BTC）余额
   - 余额必须 ≥ 0.25 UBTC

3. **系统需要有足够的 USDC**
   - 系统账户需要有足够的 USDC 可以借出

4. **用户不能已有活跃账户**
   - 一个用户只能有一个活跃的 cross margin 账户

## 运行测试

### 运行单个测试用例

```bash
# 进入测试目录
cd /Users/meng/workspace/k4-api-test

# 运行真实钱包测试
pytest tests/test_loan.py::TestLoanAPI::test_do_loan_with_real_wallet -v

# 或者使用标记运行所有 loan 测试
pytest -m loan -v
```

### 使用真实价格（不设置 mock）

测试会自动使用真实价格，因为：
- 使用了 `wait_for_real_price` fixture，等待 WebSocket 连接建立
- 没有调用 `set_mock_md_price`，系统会使用真实市场数据

## 测试流程

1. **获取报价**
   - 使用真实价格计算可借额度
   - 抵押资产：0.25 HypercoreSpotBTC
   - 返回 `quote_id` 和 `max_borrowed_amount`

2. **执行借款**
   - 使用真实钱包地址：`0x44D609d8A2d26882d099f1ef8F8bea1A60121C09`
   - 验证钱包余额（调用 Hyperliquid API）
   - 验证系统 USDC 余额
   - 重新计算可借额度（使用最新价格）
   - 验证报价有效期（滑点检查）
   - 创建账户并记录到账本

3. **验证结果**
   - 成功：返回 `account_id`、`borrowed_amount`、`current_ltv` 等
   - 失败：返回错误代码和消息

## 可能的错误情况

### 1. 余额不足 (`insufficient_collateral_balance`)
- **原因**：钱包地址未注册或余额不足
- **解决**：确保钱包在 Hyperliquid 注册并有足够的 UBTC 余额

### 2. 报价过期 (`quote_outdated`)
- **原因**：报价有效期（20秒）已过或价格波动太大
- **解决**：重新获取报价并立即执行

### 3. 已有活跃账户 (`duplicate_account`)
- **原因**：用户已有一个活跃的 cross margin 账户
- **解决**：先关闭或清算现有账户

### 4. 系统 USDC 不足 (`insufficient_usdc_balance`)
- **原因**：系统账户 USDC 余额不足
- **解决**：联系管理员充值系统账户

## 测试输出示例

### 成功情况
```
✅ 成功创建账户: account_id=550e8400-e29b-41d4-a716-446655440000
   借款金额: 1000.0
   抵押价值: 12500.0
   当前 LTV: 0.08
```

### 失败情况
```
⚠️  借款失败: insufficient_collateral_balance
   错误信息: Collateral wallet balance is insufficient
   提示: 钱包地址可能余额不足或未在 Hyperliquid 注册
```

## 注意事项

1. **真实交易**：此测试会创建真实的账户和借贷记录
2. **成本**：可能会产生实际的交易费用
3. **数据持久化**：创建的账户会保存在系统中
4. **价格波动**：使用真实价格，报价可能因价格波动而失效

## 环境变量

推荐使用 `config.local.json` 配置（无需导出环境变量）：

```bash
cp /Users/meng/workspace/k4-api-test/config.example.json /Users/meng/workspace/k4-api-test/config.local.json
```

然后在 `config.local.json` 中设置：
- `public_api_base_url`
- `internal_api_base_url`
- `wallet.address` / `wallet.user_id`
- `run_real_tx=true`

## 调试技巧

如果测试失败，可以：

1. **检查钱包余额**
   ```bash
   # 可以通过 Hyperliquid API 直接查询
   curl -X POST https://api.hyperliquid.xyz/info \
     -H "Content-Type: application/json" \
     -d '{"type": "spotClearinghouseState", "user": "0x44D609d8A2d26882d099f1ef8F8bea1A60121C09"}'
   ```

2. **查看详细日志**
   ```bash
   pytest tests/test_loan.py::TestLoanAPI::test_do_loan_with_real_wallet -v -s
   ```

3. **单独测试报价接口**
   ```bash
   pytest tests/test_loan.py::TestLoanAPI::test_quest_loan_amount_success -v
   ```




