# 评测结果模板

## CSV 列定义（示例）

- scenario, tps, p50_ms, p95_ms, p99_ms, error_rate, retries, start_ts, end_ts, notes

## Markdown 报告骨架

```markdown
## 场景与配置
- 场景：单分片路由写 / 跨分片读取 / 扩缩容期间
- 配置：节点数、副本策略、分片键与倾斜比例

## 指标结果
- TPS：
- 延迟（P50/P95/P99）：
- 错误率/重试：

## 观察与结论
- 热点与倾斜：
- 路由与重分布：
- 建议：
```

## 使用

- 在评测脚本中输出 CSV；完成后基于骨架整理成 Markdown 报告。
