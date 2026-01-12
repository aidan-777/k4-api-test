# 增加保证金流程完整分析

## 一、接口入口

```
POST /api/v1/add_margin
Headers:
  X-User-Id: <UUID>  # 必需，必须是 UUID 格式
Body:
  {
    "account_id": "<UUID>",  # 账户ID，必须是 UUID 格式
    "is_add_margin": true,   # 必须为 true（目前只支持增加）
    "collateral_assets": {
      "HypercoreSpotBTC": "0.1"  # 使用完整枚举名称，金额为字符串
    }
  }
```

## 二、完整流程步骤

### 步骤 1: 提取用户ID (`extract_user_id`)
```rust
let user_id = extract_user_id(&headers)?;
// 从 X-User-Id header 提取 UUID
// 如果缺失或格式错误，返回 401/400
```

### 步骤 2: 验证操作类型
```rust
if !payload.is_add_margin {
    return Err("Only add margin is supported");
}
// 目前只支持增加保证金，不支持减少
// 如果 is_add_margin 为 false，返回 400
```

### 步骤 3: 验证抵押资产非空
```rust
if payload.collateral_assets.is_empty() {
    return Err("collateral_assets cannot be empty");
}
// 如果为空，返回 400
```

### 步骤 4: 金额精度处理
```rust
for (asset, amount) in payload.collateral_assets.iter_mut() {
    *amount = amount.round(asset.decimals() as i64);
}
// 将金额四舍五入到资产对应的小数位数
// 例如：BTC 是 10 位小数
```

### 步骤 5: 查找账户
```rust
let account = state.ledger.get_account(&account_key)?;
// 根据 account_id 从内存账本中查找账户
// 如果不存在，返回 404 Not Found
```

### 步骤 6: 验证账户归属（关键！）
```rust
if account.user_id != user_id.to_string() {
    return Err("Account does not belong to the user");
}
// 验证 X-User-Id 必须与账户的 user_id 完全匹配
// 如果不匹配，返回 403 Forbidden
// 这是安全验证，防止用户操作他人的账户
```

### 步骤 7: 转换抵押资产格式
```rust
let added_collaterals = convert_collaterals_map(payload.collateral_assets)?;
// 将 CollateralAsset enum -> String symbol 映射
// HypercoreSpotBTC -> "BTC"
// 同时验证金额必须 > 0
```

### 步骤 8: 更新账本余额（核心逻辑）
```rust
update_ledger_balances(&state.ledger, &account_key, &added_collaterals)?;

// 内部实现：
ledger.update_account(account_id, |account| {
    for (symbol, added_amount) in additions {
        // 获取或创建余额记录
        let balance = account.balances.entry(symbol.clone())
            .or_insert_with(|| Balance {
                asset_id: symbol.clone(),
                amount: Decimal::ZERO,
            });
        
        // 累加金额（不是替换！）
        balance.amount += Decimal::from_str(&added_amount.to_string());
    }
    account.updated_at = Utc::now();  // 更新修改时间
});
```

### 步骤 9: 返回成功响应
```rust
CrossMarginAdjustMarginResponse {
    account_id: payload.account_id
}
```

## 三、关键数据结构

### 请求结构
```rust
CrossMarginAdjustMarginRequest {
    account_id: Uuid,  // UUID 格式
    is_add_margin: bool,  // 必须为 true
    collateral_assets: HashMap<CollateralAsset, BigDecimal>,  // 枚举 -> 金额
}
```

### 余额更新逻辑
- **累加模式**：余额是累加的，不是替换的
- **自动创建**：如果资产不存在，自动创建余额记录
- **时间戳更新**：自动更新 `updated_at` 字段

## 四、错误情况汇总

| 错误情况 | 状态码 | 错误代码 | 说明 |
|---------|--------|---------|------|
| 缺少 X-User-Id | 401 | unauthorized | Missing X-User-Id header |
| X-User-Id 格式错误 | 400 | invalid_user_id | 必须是 UUID 格式 |
| is_add_margin 为 false | 400 | unsupported_operation | 只支持增加保证金 |
| collateral_assets 为空 | 400 | invalid_request | 不能为空 |
| account_id 不存在 | 404 | account_not_found | 账户不存在 |
| user_id 不匹配 | 403 | unauthorized | 账户不属于该用户 |
| 金额转换失败 | 500 | conversion_failed | 内部错误 |

## 五、测试要点

### 1. 必须使用 UUID 格式的 user_id
```python
# ❌ 错误
test_user_id = "test_user_123"  # 不是 UUID

# ✅ 正确
test_user_id = str(uuid.uuid4())  # UUID 格式
```

### 2. account_id 必须存在
```python
# 必须先创建账户（通过 add_mock_position 或 do_loan）
account_id = add_mock_position(...)["data"]["account_id"]
```

### 3. X-User-Id 必须与账户的 user_id 匹配
```python
# 创建账户时使用的 user_id
create_user_id = str(uuid.uuid4())

# 增加保证金时使用的 X-User-Id 必须一致
response = add_margin(..., headers={"X-User-Id": create_user_id})
```

### 4. collateral_assets 使用完整枚举名称
```python
# ❌ 错误
{"BTC": "0.1"}

# ✅ 正确
{"HypercoreSpotBTC": "0.1"}
```

## 六、余额更新示例

假设账户当前余额：
```json
{
  "BTC": {
    "asset_id": "BTC",
    "amount": "0.5"
  }
}
```

增加 0.1 BTC 后：
```json
{
  "BTC": {
    "asset_id": "BTC",
    "amount": "0.6"  // 0.5 + 0.1 = 0.6（累加）
  }
}
```

## 七、完整测试示例

```python
def test_add_margin_complete_flow(
    public_api_client, internal_api_client
):
    # 1. 生成 UUID 格式的 user_id
    test_user_id = str(uuid.uuid4())
    test_position_id = f"test_pos_{uuid.uuid4().hex[:8]}"
    
    # 2. 创建账户
    internal_api_client.set_mock_md_price("BTC", 50000.0)
    add_response = internal_api_client.add_mock_position(
        user_id=test_user_id,  # UUID 格式
        position_id=test_position_id,
        borrowed_asset="USDC",
        borrowed_amount=10000.0,
        collateral_assets={"BTC": 0.5},
    )
    account_id = add_response.json()["data"]["account_id"]
    
    # 3. 增加保证金
    margin_payload = {
        "account_id": account_id,  # UUID 格式
        "is_add_margin": True,
        "collateral_assets": {"HypercoreSpotBTC": "0.1"},
    }
    
    response = public_api_client.add_margin(margin_payload, headers={
        "X-User-Id": test_user_id  # 必须与创建账户时的 user_id 一致
    })
    
    # 4. 验证成功
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == account_id
```

## 八、常见问题

### Q1: 为什么测试失败，返回 403？
**A**: `X-User-Id` 与账户的 `user_id` 不匹配。确保创建账户和增加保证金时使用相同的 `user_id`。

### Q2: 为什么返回 400，说 user_id 格式错误？
**A**: `X-User-Id` 必须是 UUID 格式，不能是普通字符串。

### Q3: 余额是累加还是替换？
**A**: 累加。每次调用 `add_margin` 都会在现有余额基础上增加。

### Q4: 如何获取 account_id？
**A**: 
- 通过 `add_mock_position` 返回的 `data.account_id`
- 通过 `do_loan` 返回的 `account_id`
- 通过 `get_accounts` 或 `get_account_by_ids` 查询





