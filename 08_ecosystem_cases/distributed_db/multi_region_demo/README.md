# 跨区域多活演示骨架

本目录提供跨区域（多 AZ/Region）部署的演示骨架与延迟模拟思路，帮助理解一致性与延迟权衡。

## 思路

- 使用两个 compose 项目模拟两个 Region，Region A 暴露 5432，Region B 暴露 55432
- 通过 `tc`（linux traffic control）或 `toxiproxy` 注入网络延迟/丢包，模拟跨地域网络
- 在写入采用仲裁/同步策略时，观察 P95/P99 延迟的变化；在只读采用本地优先时，比较一致性与新鲜度

## 目录（建议）

- `region_a/`、`region_b/`：各自包含 coordinator 与 workers 的 compose
- `net_emulation/`：延迟注入脚本（tc/toxiproxy）
- `scenarios.md`：演示场景与指标采集（与 `10_benchmarks/` 对接）

## 脚本

- `tc_setup.sh` / `tc_teardown.sh`：基于 tc 的延迟/丢包注入与恢复
- `toxiproxy.json`：示例代理配置，可在 docker 中启动 `shopify/toxiproxy` 并加载

本仓库暂提供方法学与脚本骨架，具体实现可参考生产环境实际网络与参数策略。
