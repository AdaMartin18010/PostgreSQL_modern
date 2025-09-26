# pgbench 示例（简单）

## 初始化与运行

```bash
# 初始化 10 倍扩展（表数据规模）
pgbench -i -s 10
# 基准 60s，16 并发，1 线程
pgbench -T 60 -c 16 -j 1
```

## 自定义脚本（只读示例）

```sql
-- select_only.sql
SELECT sum(1) FROM pgbench_accounts WHERE aid BETWEEN 1 AND 1000;
```

```bash
pgbench -T 60 -c 16 -j 1 -f select_only.sql
```
