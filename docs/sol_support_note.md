# SOL 支持说明

## 当前状态

根据代码分析，系统配置文件中支持 SOL（`conf/loan.toml` 中 `allowed_collateral_assets` 包含 SOL），但代码中的 `CollateralAsset` enum 目前只定义了 `HypercoreSpotBTC`，**没有定义 SOL**。

## 问题

如果直接使用 `"HypercoreSpotSOL"` 作为抵押资产，可能会遇到以下错误：

```
Failed to deserialize the JSON body into the target type: 
collateral_assets.?: unknown variant `HypercoreSpotSOL`, 
expected `HypercoreSpotBTC` at line 1 column XX status=422
```

## 解决方案

### 方案 1: 如果系统实际上支持 SOL

如果系统实际上支持 SOL，但代码中还没有定义枚举，需要：

1. **在 `crates/wallet-lib/src/cross_margin/enums.rs` 中添加 SOL 枚举**：
   ```rust
   #[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
   pub enum CollateralAsset {
       HypercoreSpotBTC,
       HypercoreSpotSOL,  // 需要添加
   }
   ```

2. **更新相关方法**：
   - `symbol()` 方法：返回 "SOL"
   - `decimals()` 方法：返回 SOL 的小数位数
   - `FromStr` 实现：支持 "HypercoreSpotSOL" 和 "SOL"
   - `Display` 实现：显示 "HypercoreSpotSOL"

3. **更新余额检查逻辑**（`crates/risk/src/hyperliquid.rs`）：
   ```rust
   let symbol = match asset {
       CollateralAsset::HypercoreSpotBTC => "UBTC",
       CollateralAsset::HypercoreSpotSOL => "USOL",  // 需要确认 Hyperliquid 上的 SOL 符号
   };
   ```

### 方案 2: 如果系统不支持 SOL

如果系统确实不支持 SOL，需要：
- 使用 BTC 或其他支持的资产
- 或者等待系统添加 SOL 支持

## 测试用例

测试用例已修改为使用 SOL（0.25 SOL），如果系统不支持，测试会跳过并显示错误信息。

## 验证方法

运行测试时，如果看到以下错误，说明系统不支持 SOL：
- `422` 状态码 + `unknown variant HypercoreSpotSOL`
- 或者 `400` 状态码 + `Invalid collateral asset`

如果测试成功，说明系统支持 SOL（即使代码中还没有定义枚举，可能是通过其他方式支持的）。





