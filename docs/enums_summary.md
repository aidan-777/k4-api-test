# 源码中定义的枚举总结

## 一、抵押资产枚举 (CollateralAsset)

**文件位置**: `crates/wallet-lib/src/cross_margin/enums.rs`

### 当前定义的枚举值

```rust
pub enum CollateralAsset {
    HypercoreSpotBTC,  // Hypercore Spot BTC
}
```

### 详细信息

| 枚举值 | JSON 序列化名称 | Symbol | 小数位数 | 说明 |
|--------|----------------|--------|---------|------|
| `HypercoreSpotBTC` | `"HypercoreSpotBTC"` | `"BTC"` | 10 | Hypercore 现货 BTC |

### 支持的字符串格式

- `"HypercoreSpotBTC"` ✅
- `"BTC"` ✅ (通过 FromStr 支持)

### 当前状态

**只支持 BTC，不支持 SOL、ETH 等其他资产**

---

## 二、借贷资产枚举 (BorrowedAsset)

**文件位置**: `crates/wallet-lib/src/cross_margin/enums.rs`

### 当前定义的枚举值

```rust
pub enum BorrowedAsset {
    HypercorePerpsUSDC,  // Hypercore Perps USDC
}
```

### 详细信息

| 枚举值 | JSON 序列化名称 | Symbol | 小数位数 | 说明 |
|--------|----------------|--------|---------|------|
| `HypercorePerpsUSDC` | `"HypercorePerpsUSDC"` | `"USDC"` | 8 | Hypercore 永续合约 USDC |

### 支持的字符串格式

- `"HypercorePerpsUSDC"` ✅

---

## 三、仓位状态枚举 (CrossMarginPositionStatus)

**文件位置**: `crates/wallet-lib/src/cross_margin/enums.rs`

### 枚举值

```rust
pub enum CrossMarginPositionStatus {
    Open,                // 仓位开启
    Closed,              // 仓位关闭
    PartiallyLiquidated, // 部分清算
    AllLiquidated,       // 全部清算
}
```

### JSON 序列化名称

- `"Open"`
- `"Closed"`
- `"PartiallyLiquidated"`
- `"AllLiquidated"`

---

## 四、操作类型枚举 (CrossMarginOperationType)

**文件位置**: `crates/wallet-lib/src/cross_margin/enums.rs`

### 枚举值

```rust
pub enum CrossMarginOperationType {
    Borrow,       // 开仓或增加仓位
    Repay,        // 减少仓位或完全平仓
    AddMargin,    // 增加保证金
    RemoveMargin, // 减少保证金
    Liquidation,  // 清算
}
```

---

## 五、其他相关枚举

### CollateralSymbol (简化符号枚举)

**文件位置**: `crates/wallet-lib/src/cross_margin/cross_margin/mod.rs`

```rust
pub enum CollateralSymbol {
    BTC,
}
```

### BorrowedSymbol (简化符号枚举)

**文件位置**: `crates/wallet-lib/src/cross_margin/cross_margin/mod.rs`

```rust
pub enum BorrowedSymbol {
    USDC,
}
```

### Network (网络枚举)

**文件位置**: `crates/wallet-lib/src/user/enums.rs` 或 `crates/wallet-lib/src/user/types.rs`

```rust
pub enum Network {
    Ethereum,
    Solana,
}
```

### AccountStatus (账户状态)

**文件位置**: `crates/wallet-lib/src/cross_margin/cross_margin/mod.rs`

```rust
pub enum AccountStatus {
    Active,       // 活跃
    Liquidating,  // 正在清算
    Closed,       // 已关闭
}
```

---

## 六、配置 vs 代码实现

### 配置文件支持 (`conf/loan.toml`)

```toml
allowed_collateral_assets = ["USDC", "USDT", "BTC", "ETH", "SOL", "HYPE"]
```

### 代码实现

**目前只实现了 BTC**，其他资产（ETH、SOL、USDC、USDT、HYPE）在配置文件中列出，但代码中还没有对应的枚举定义。

---

## 七、如果要添加 SOL 支持

需要在 `crates/wallet-lib/src/cross_margin/enums.rs` 中：

1. **添加枚举值**：
   ```rust
   pub enum CollateralAsset {
       HypercoreSpotBTC,
       HypercoreSpotSOL,  // 新增
   }
   ```

2. **更新所有 match 语句**：
   - `symbol()` 方法
   - `decimals()` 方法
   - `FromStr` 实现
   - `Display` 实现

3. **更新相关转换**：
   - `CollateralSymbol` enum
   - `convert_account_balances()` 函数
   - `has_enough_collateral()` 函数（需要确认 Hyperliquid 上 SOL 的符号）

---

## 八、当前可用的资产

### ✅ 已实现
- **抵押资产**: `HypercoreSpotBTC` (BTC)
- **借贷资产**: `HypercorePerpsUSDC` (USDC)

### ❌ 配置支持但代码未实现
- ETH
- SOL
- USDC (作为抵押物)
- USDT
- HYPE

---

## 九、测试用例中的使用

### 正确的用法

```python
# ✅ 正确 - 使用完整的枚举名称
collateral_assets = {"HypercoreSpotBTC": "0.25"}

# ✅ 正确 - 借贷资产
borrowed_asset = "HypercorePerpsUSDC"
```

### 错误的用法

```python
# ❌ 错误 - 使用简写（虽然 FromStr 支持，但 JSON 序列化需要完整名称）
collateral_assets = {"BTC": "0.25"}  # 在 JSON 请求中会失败

# ❌ 错误 - SOL 未定义
collateral_assets = {"HypercoreSpotSOL": "0.25"}  # 会返回 422 错误
```





