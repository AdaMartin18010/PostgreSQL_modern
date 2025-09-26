# Citus 最小可运行演示

## 快速开始

1) 启动集群：

    ```bash
    docker compose up -d
    ```

2) 等待 `manager` 输出 `Citus cluster ready` 后，执行初始化：

    ```bash
    docker compose exec -T coordinator psql -U postgres -f /docker-entrypoint-initdb.d/init.sql < init.sql
    ```

    或在宿主机：

    ```bash
    psql postgresql://postgres:postgres@localhost:5432/postgres -f init.sql
    ```

3) 观察执行计划（路由 vs 重分布）：

```sql
EXPLAIN (ANALYZE, VERBOSE) SELECT count(*) FROM orders WHERE customer_id = 42;
EXPLAIN (ANALYZE, VERBOSE) SELECT c.customer_name, sum(o.amount) FROM orders o JOIN customers c USING (customer_id) GROUP BY c.customer_name ORDER BY sum(o.amount) DESC LIMIT 10;
```

## 目录

- `docker-compose.yml`：3 节点（1 协调 + 2 工作）
- `init.sql`：创建扩展/表/分布策略与示例数据

## 注意

- 示例仅用于本地教学与演示，请根据生产环境修改参数与安全配置。
