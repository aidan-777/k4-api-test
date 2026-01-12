# 增加保证金流程分析

## 完整流程

### 1. 接口入口 (`server/http.rs`)
```
POST /api/v1/add_margin
```

### 2. 请求验证层 (`server/margin.rs` - `adjust_margin`)

#### 步骤 1: 提取用户ID
```rust
let user_id = extract_user_id(&headers)?;
// 从 X-User-Id header 提取 UUID 格式的用户ID
```

#### 步骤 2: 验证操作类型
```rust
if !payload.is_add_margin {
    return Err("Only add margin is supported");
}
// 目前只支持增加保证金，不支持减少
```

#### 步骤 3: 验证抵押资产
```rust
if payload.collateral_assets.is_empty() {
    return Err("collateral_assets cannot be empty");
}
```

#### 步骤 4: 金额精度处理
```rust
for (asset, amount) in payload.collateral_assets.iter_mut() {
    *amount = amount.round(asset.decimals() as i64);
}
// 将金额四舍五入到资产对应的小数位数
```

#### 步骤 5: 查找账户
```rust
let account = state.ledger.get_account(&account_key)?;
// 根据 account_id 从账本中查找账户
// 如果不存在，返回 404
```

#### 步骤 6: 验证账户归属
```rust
if account.user_id != user_id.to_string() {
    return Err("Account does not belong to the user");
}
// 验证 X-User-Id 必须与账户的 user_id 匹配
// 如果不匹配，返回 403 Forbidden
```

#### 步骤 7: 转换抵押资产格式
```rust
let added_collaterals = convert_collaterals_map(payload.collateral_assets)?;
// 将 CollateralAsset enum -> String symbol 映射
// 例如: HypercoreSpotBTC -> "BTC"
```

#### 步骤 8: 更新账本余额
```rust
update_ledger_balances(&state.ledger, &account_key, &added_collaterals)?;
// 在账户的 balances 中增加对应的资产数量
// 如果资产不存在，创建新的余额记录
// 如果资产已存在，累加到现有余额
```

#### 步骤 9: 返回成功响应
```rust
CrossMarginAdjustMarginResponse { account_id: payload.account_id }
```

## 关键数据结构

### 请求结构 (`CrossMarginAdjustMarginRequest`)
```rust
{
    account_id: Uuid,  // 账户ID（UUID格式）
    is_add_margin: bool,  // 必须为 true
    collateral_assets: HashMap<CollateralAsset, BigDecimal>,  // 抵押资产，key 必须是完整枚举名称
}
```

### 响应结构 (`CrossMarginAdjustMarginResponse`)
```rust
{
    account_id: Uuid  // 返回账户ID
}
```

## 余额更新逻辑

```rust
fn update_ledger_balances(
    ledger: &Ledger,
    account_id: &str,
    additions: &HashMap<String, f64>,
) {
    ledger.update_account(account_id, |account| {
        for (symbol, added_amount) in additions {
            // 获取或创建余额记录
            let balance = account.balances.entry(symbol.clone())
                .or_insert_with(|| Balance {
                    asset_id: symbol.clone(),
                    amount: Decimal::ZERO,
                });
            
            // 累加金额
            balance.amount += Decimal::from_str(&added_amount.to_string());
        }
        account.updated_at = Utc::now();
    });
}
```

## 错误情况

1. **缺少 X-User-Id header**: 401 Unauthorized
2. **X-User-Id 格式错误**: 400 Bad Request
3. **is_add_margin 为 false**: 400 Bad Request ("unsupported_operation")
4. **collateral_assets 为空**: 400 Bad Request ("invalid_request")
5. **account_id 不存在**: 404 Not Found ("account_not_found")
6. **user_id 不匹配**: 403 Forbidden ("unauthorized")
7. **金额转换失败**: 500 Internal Server Error

## 注意事项

1. **account_id 必须是 UUID 格式**
2. **X-User-Id 必须是 UUID 格式，且必须与账户的 user_id 匹配**
3. **collateral_assets 的 key 必须使用完整枚举名称**（如 "HypercoreSpotBTC"）
4. **金额会自动四舍五入到资产对应的小数位数**
5. **余额是累加的**，不是替换的





