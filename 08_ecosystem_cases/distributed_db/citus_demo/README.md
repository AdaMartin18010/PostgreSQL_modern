# Citus 分布式 PostgreSQL 演示

> Citus 12+ | PostgreSQL 17

## 📋 目标

演示如何使用 Citus 将 PostgreSQL 扩展为分布式数据库，包括：

- 多节点集群部署
- 分布式表和引用表
- 分布式查询和跨分片 JOIN
- 数据重平衡和故障恢复

---

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- 至少 4GB 可用内存
- PostgreSQL 客户端工具（psql）

### 步骤 1：启动 Citus 集群

```bash
# 启动3节点集群（1协调节点 + 2工作节点）
docker compose up -d

# 查看容器状态
docker compose ps

# 预期输出：
# coordinator  running  0.0.0.0:5432->5432/tcp
# worker1      running
# worker2      running
```

**等待集群就绪**（约 30 秒）：

```bash
# 查看日志，等待"Citus cluster ready"
docker compose logs -f coordinator
```

### 步骤 2：初始化数据

**方式 A：从容器内执行**:

```bash
docker compose exec -T coordinator psql -U postgres < init.sql
```

**方式 B：从宿主机执行**:

```bash
psql postgresql://postgres:postgres@localhost:5432/postgres -f init.sql
```

### 步骤 3：验证集群

```bash
# 连接到协调节点
psql postgresql://postgres:postgres@localhost:5432/postgres

# 查看工作节点
SELECT * FROM citus_get_active_worker_nodes();

# 预期输出：
#  node_name | node_port
# -----------+-----------
#  worker1   |      5432
#  worker2   |      5432
```

---

## 📊 核心概念演示

### 1. 分布式表（Distributed Table）

分布式表按分片键（distribution column）分布在多个工作节点上。

```sql
-- 创建分布式表
CREATE TABLE orders (
    order_id    BIGSERIAL,
    customer_id BIGINT NOT NULL,
    order_date  DATE NOT NULL,
    amount      DECIMAL(10,2),
    status      TEXT
);

-- 设置分片策略（按customer_id哈希分片）
SELECT create_distributed_table('orders', 'customer_id');

-- 查看分片分布
SELECT * FROM citus_shards WHERE table_name::text = 'orders';

-- 插入数据（自动路由到对应分片）
INSERT INTO orders (customer_id, order_date, amount, status)
VALUES
    (1, '2025-01-01', 100.00, 'completed'),
    (2, '2025-01-02', 200.00, 'pending'),
    (1, '2025-01-03', 150.00, 'completed');
```

### 2. 引用表（Reference Table）

引用表在所有工作节点上保存完整副本，适合小型维度表。

```sql
-- 创建引用表
CREATE TABLE customers (
    customer_id   BIGINT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email         TEXT,
    created_at    TIMESTAMP DEFAULT now()
);

-- 设置为引用表
SELECT create_reference_table('customers');

-- 插入数据（复制到所有节点）
INSERT INTO customers (customer_id, customer_name, email)
VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com');
```

### 3. 本地表（Local Table）

本地表只存在于协调节点，适合不需要分布的小表。

```sql
-- 普通表默认是本地表
CREATE TABLE system_config (
    config_key   TEXT PRIMARY KEY,
    config_value TEXT
);

-- 查看表类型
SELECT table_name, citus_table_type
FROM citus_tables
ORDER BY table_name;
```

---

## 🔍 查询模式分析

### 1. 单分片查询（最优）

```sql
-- 查询单个customer的订单（路由到单个分片）
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM orders
WHERE customer_id = 1;

-- 执行计划：Custom Scan (Citus Adaptive)
-- → Task Count: 1（只访问1个分片）
```

### 2. 跨分片 JOIN（协同定位）

```sql
-- 分布式表和引用表JOIN（本地JOIN）
EXPLAIN (ANALYZE, VERBOSE)
SELECT
    c.customer_name,
    COUNT(*) as order_count,
    SUM(o.amount) as total_amount
FROM orders o
JOIN customers c USING (customer_id)
GROUP BY c.customer_name
ORDER BY total_amount DESC
LIMIT 10;

-- 执行计划：每个worker本地执行JOIN，协调节点合并结果
```

### 3. 跨分片聚合

```sql
-- 全表聚合（并行执行）
EXPLAIN (ANALYZE, VERBOSE)
SELECT
    status,
    COUNT(*) as count,
    AVG(amount) as avg_amount
FROM orders
GROUP BY status;

-- 执行计划：
-- 1. 每个worker本地聚合
-- 2. 协调节点合并结果
```

### 4. 分布式 JOIN（重分布）

```sql
-- 两个分布式表按不同键JOIN（需要重分布）
CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    name       TEXT,
    price      DECIMAL(10,2)
);
SELECT create_distributed_table('products', 'product_id');

CREATE TABLE order_items (
    order_id   BIGINT,
    product_id BIGINT,
    quantity   INT
);
SELECT create_distributed_table('order_items', 'order_id');

-- 跨分片键JOIN（触发repartition）
EXPLAIN (ANALYZE, VERBOSE)
SELECT p.name, SUM(oi.quantity)
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.name;

-- 执行计划：包含 "Repartition" 节点
```

---

## 🛠️ 管理操作

### 1. 查看集群状态

```sql
-- 查看所有表的分布情况
SELECT * FROM citus_tables ORDER BY table_name;

-- 查看分片分布
SELECT
    table_name,
    COUNT(*) as shard_count,
    COUNT(DISTINCT node_name) as node_count
FROM citus_shards
GROUP BY table_name;

-- 查看分片详情
SELECT
    shardid,
    table_name,
    shard_size,
    node_name,
    node_port
FROM citus_shards
ORDER BY table_name, shardid;
```

### 2. 数据重平衡

```sql
-- 查看分片分布不均衡情况
SELECT
    node_name,
    COUNT(*) as shard_count,
    pg_size_pretty(SUM(shard_size)) as total_size
FROM citus_shards
GROUP BY node_name;

-- 重平衡分片（将分片均匀分布到所有节点）
SELECT rebalance_table_shards('orders');

-- 设置自动重平衡策略
ALTER TABLE orders SET (shard_replication_factor = 1);
```

### 3. 监控查询

```sql
-- 查看活动查询
SELECT * FROM citus_stat_activity;

-- 查看分布式查询统计
SELECT * FROM citus_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 查看worker节点健康状态
SELECT * FROM citus_check_cluster_node_health();
```

### 4. 添加/删除工作节点

```sql
-- 添加新的工作节点
SELECT citus_add_node('worker3', 5432);

-- 移除工作节点（先重平衡数据）
SELECT citus_drain_node('worker3', 5432);
SELECT citus_remove_node('worker3', 5432);

-- 临时禁用节点（不删除）
SELECT citus_disable_node('worker2', 5432);

-- 重新启用节点
SELECT citus_activate_node('worker2', 5432);
```

---

## 📈 性能优化

### 1. 选择合适的分片键

```sql
-- ✅ 好的分片键：
-- - 高基数（如user_id, customer_id）
-- - 查询常用的过滤条件
-- - 均匀分布

-- ❌ 不好的分片键：
-- - 低基数（如status, country）
-- - 时间戳（导致热点）
-- - 自增ID（不均匀）

-- 分析分片分布
SELECT
    hashtext(customer_id::text) % 32 as shard_id,
    COUNT(*) as row_count
FROM orders
GROUP BY 1
ORDER BY 2 DESC;
```

### 2. 协同定位（Co-location）

```sql
-- 确保相关表使用相同的分片键
CREATE TABLE order_items (
    order_id    BIGINT,
    customer_id BIGINT,  -- 与orders表相同的分片键
    product_id  BIGINT,
    quantity    INT
);

SELECT create_distributed_table('order_items', 'customer_id');

-- 验证协同定位
SELECT
    colocationid,
    table_name
FROM citus_tables
WHERE colocationid IS NOT NULL
ORDER BY colocationid, table_name;
```

### 3. 并行度调优

```sql
-- 设置并行度
SET citus.max_adaptive_executor_pool_size = 16;
SET citus.executor_slow_start_interval = 10;

-- 调整分片数量（在create_distributed_table时）
SELECT create_distributed_table(
    'large_table',
    'user_id',
    shard_count := 64  -- 增加分片数以提高并行度
);
```

### 4. 索引优化

```sql
-- 在分片键上创建索引
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- 在常用查询列上创建索引
CREATE INDEX idx_orders_date ON orders(order_date);

-- 索引会自动分布到所有分片
```

---

## 🧪 测试场景

### 场景 1：高并发写入

```sql
-- 使用pgbench测试分布式写入
-- 创建测试脚本 insert_orders.sql：
\set customer_id random(1, 10000)
INSERT INTO orders (customer_id, order_date, amount, status)
VALUES (:customer_id, CURRENT_DATE, random() * 1000, 'pending');

-- 执行测试
-- pgbench -h localhost -p 5432 -U postgres -f insert_orders.sql -c 32 -j 4 -T 60
```

### 场景 2：分析查询

```sql
-- 客户订单汇总
SELECT
    c.customer_name,
    COUNT(DISTINCT o.order_id) as order_count,
    SUM(o.amount) as total_spent,
    AVG(o.amount) as avg_order
FROM orders o
JOIN customers c USING (customer_id)
WHERE o.order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY c.customer_name
HAVING COUNT(*) >= 5
ORDER BY total_spent DESC
LIMIT 100;
```

### 场景 3：实时仪表板

```sql
-- 创建实时统计视图
CREATE MATERIALIZED VIEW daily_stats AS
SELECT
    order_date,
    status,
    COUNT(*) as order_count,
    SUM(amount) as total_amount
FROM orders
GROUP BY order_date, status;

-- 定期刷新
REFRESH MATERIALIZED VIEW daily_stats;
```

---

## 🔧 故障处理

### 节点故障恢复

```bash
# 模拟worker节点故障
docker compose stop worker1

# 查看集群状态（会显示worker1不可用）
psql -c "SELECT * FROM citus_check_cluster_node_health();"

# 重启worker节点
docker compose start worker1

# 等待节点恢复（自动重新加入集群）
```

### 数据一致性检查

```sql
-- 检查分片复制状态
SELECT * FROM citus_shard_placement
WHERE shardstate != 1;  -- 1表示健康

-- 修复不一致的分片
SELECT citus_copy_shard_placement(
    12345,  -- shard_id
    'worker1', 5432,  -- source
    'worker2', 5432   -- target
);
```

---

## 📚 目录说明

- `docker-compose.yml` - 3 节点集群配置
- `init.sql` - 初始化脚本（创建表、分布策略、示例数据）
- `run.ps1` - Windows 启动脚本

---

## ⚠️ 生产环境建议

1. **高可用配置**：

   - 使用分片复制（shard_replication_factor >= 2）
   - 配置故障转移机制
   - 跨可用区部署工作节点

2. **安全配置**：

   - 启用 SSL/TLS
   - 配置防火墙规则
   - 使用强密码和证书认证

3. **监控告警**：

   - 监控节点健康状态
   - 跟踪分片分布和数据倾斜
   - 设置查询延迟告警

4. **容量规划**：
   - 根据数据增长预留空间
   - 定期重平衡分片
   - 监控磁盘和内存使用

---

## 📖 参考资源

- **Citus 文档**: <https://docs.citusdata.com/>
- **GitHub**: <https://github.com/citusdata/citus>
- **相关章节**: `../../04_modern_features/distributed_db/`
- **性能基准**: `../../../10_benchmarks/`

---

**最后更新**: 2025-10  
**适用版本**: Citus 12+ | PostgreSQL 15-17

---

## 🎯 下一步

- 尝试修改分片数量和复制因子
- 测试不同的分片键对性能的影响
- 实现跨区域部署和灾难恢复
- 集成应用程序连接池
