# 分片策略与复制拓扑

> 分布式PostgreSQL的数据分片、复制策略与查询执行

## 📋 目录

- [分片策略与复制拓扑](#分片策略与复制拓扑)
  - [📋 目录](#-目录)
  - [1. 分片策略](#1-分片策略)
    - [1.1 哈希分片](#11-哈希分片)
    - [1.2 范围分片](#12-范围分片)
    - [1.3 目录分片](#13-目录分片)
    - [1.4 混合分片](#14-混合分片)
  - [2. 分片键选择](#2-分片键选择)
    - [2.1 选择原则](#21-选择原则)
    - [2.2 倾斜评估](#22-倾斜评估)
    - [2.3 常见陷阱](#23-常见陷阱)
  - [3. 特殊表类型](#3-特殊表类型)
    - [3.1 分布式表](#31-分布式表)
    - [3.2 引用表](#32-引用表)
    - [3.3 本地表](#33-本地表)
  - [4. 复制拓扑](#4-复制拓扑)
    - [4.1 主备复制](#41-主备复制)
    - [4.2 级联复制](#42-级联复制)
    - [4.3 多主复制](#43-多主复制)
  - [5. 复制模式](#5-复制模式)
    - [5.1 同步复制](#51-同步复制)
    - [5.2 异步复制](#52-异步复制)
    - [5.3 半同步复制](#53-半同步复制)
  - [6. 副本放置策略](#6-副本放置策略)
    - [6.1 跨可用区部署](#61-跨可用区部署)
    - [6.2 跨区域部署](#62-跨区域部署)
  - [7. 故障域与仲裁](#7-故障域与仲裁)
    - [7.1 仲裁机制](#71-仲裁机制)
    - [7.2 见证节点](#72-见证节点)
  - [8. 查询执行](#8-查询执行)
    - [8.1 查询路由](#81-查询路由)
    - [8.2 并行执行](#82-并行执行)
    - [8.3 跨分片连接](#83-跨分片连接)
  - [9. 数据重分布](#9-数据重分布)
  - [10. 工程实践](#10-工程实践)
  - [参考资源](#参考资源)

## 1. 分片策略

### 1.1 哈希分片

**原理**：基于分片键的哈希值分配数据到不同分片

**PostgreSQL + Citus实现**:

```sql
-- 创建哈希分片表
CREATE TABLE orders (
    order_id BIGSERIAL,
    user_id BIGINT NOT NULL,
    order_date TIMESTAMPTZ DEFAULT NOW(),
    amount NUMERIC,
    status TEXT,
    PRIMARY KEY (order_id, user_id)
);

-- 分布表到8个分片
SELECT create_distributed_table('orders', 'user_id');

-- 查看分片分布
SELECT 
    shardid,
    nodename,
    nodeport,
    shardstate
FROM citus_shards
WHERE table_name = 'orders'::regclass;
```

**优势**:

- 数据分布均匀
- 负载均衡好
- 扩展性强

**局限**:

- 范围查询需要扫描所有分片
- 重分片复杂（需要数据迁移）

**适用场景**:

- 高并发OLTP系统
- 按用户ID分片的多租户应用
- 数据分布均匀的场景

### 1.2 范围分片

**原理**：基于数据范围分配到不同分片

**PostgreSQL分区表实现**:

```sql
-- 创建范围分区表
CREATE TABLE events (
    event_id BIGSERIAL,
    event_time TIMESTAMPTZ NOT NULL,
    event_type TEXT,
    data JSONB,
    PRIMARY KEY (event_id, event_time)
) PARTITION BY RANGE (event_time);

-- 创建分区
CREATE TABLE events_2025_01 PARTITION OF events
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE events_2025_02 PARTITION OF events
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE events_2025_03 PARTITION OF events
FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- 创建索引
CREATE INDEX idx_events_2025_01_time ON events_2025_01 (event_time);
CREATE INDEX idx_events_2025_02_time ON events_2025_02 (event_time);
CREATE INDEX idx_events_2025_03_time ON events_2025_03 (event_time);
```

**优势**:

- 范围查询高效（分区裁剪）
- 易于归档历史数据
- 数据局部性好

**局限**:

- 可能出现数据倾斜
- 热点分区问题
- 需要合理规划分区边界

**适用场景**:

- 时序数据（按时间分片）
- 有序数据（按ID范围分片）
- 需要定期归档的场景

### 1.3 目录分片

**原理**：维护分片键到分片的映射表

**实现示例**:

```sql
-- 创建分片映射表
CREATE TABLE shard_map (
    tenant_id BIGINT PRIMARY KEY,
    shard_id INTEGER NOT NULL,
    node_name TEXT NOT NULL
);

-- 插入映射关系
INSERT INTO shard_map (tenant_id, shard_id, node_name) VALUES
(1, 1, 'node1'),
(2, 1, 'node1'),
(3, 2, 'node2'),
(4, 2, 'node2');

-- 应用层路由函数
CREATE OR REPLACE FUNCTION get_shard_for_tenant(p_tenant_id BIGINT)
RETURNS TEXT AS $$
    SELECT node_name FROM shard_map WHERE tenant_id = p_tenant_id;
$$ LANGUAGE sql STABLE;
```

**优势**:

- 灵活性最高
- 支持复杂的分片规则
- 易于调整分片策略

**局限**:

- 需要维护映射表
- 映射表可能成为性能瓶颈
- 实现复杂度高

**适用场景**:

- 多租户SaaS系统
- 需要灵活调整分片的场景
- VIP用户独立分片

### 1.4 混合分片

**原理**：结合多种分片策略

```sql
-- 先按区域哈希分片，再按时间范围分区
CREATE TABLE user_events (
    event_id BIGSERIAL,
    user_id BIGINT NOT NULL,
    region TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    data JSONB,
    PRIMARY KEY (event_id, user_id, event_time)
) PARTITION BY LIST (region);

-- 每个区域分区
CREATE TABLE user_events_us PARTITION OF user_events
FOR VALUES IN ('us-east', 'us-west');

CREATE TABLE user_events_eu PARTITION OF user_events
FOR VALUES IN ('eu-central', 'eu-west');

-- 区域内再按用户ID分片
SELECT create_distributed_table('user_events_us', 'user_id');
SELECT create_distributed_table('user_events_eu', 'user_id');
```

## 2. 分片键选择

### 2.1 选择原则

**高基数（High Cardinality）**:

- 分片键值的唯一性要高
- 避免使用布尔值、性别等低基数字段
- 推荐：user_id、order_id、device_id

**查询模式对齐**:

- 大部分查询都包含分片键
- 避免频繁的跨分片查询
- 示例：按user_id分片，查询条件包含user_id

**数据分布均匀**:

- 避免热点数据集中在少数分片
- 考虑业务增长趋势
- 定期评估分片分布

### 2.2 倾斜评估

**检测数据倾斜**:

```sql
-- 查看分片大小分布
SELECT 
    shardid,
    pg_size_pretty(shard_size) as size,
    estimated_rows,
    ROUND(100.0 * shard_size / SUM(shard_size) OVER (), 2) as pct
FROM citus_shards
WHERE table_name = 'orders'::regclass
ORDER BY shard_size DESC;

-- 倾斜度分析
WITH shard_stats AS (
    SELECT 
        AVG(shard_size) as avg_size,
        STDDEV(shard_size) as stddev_size
    FROM citus_shards
    WHERE table_name = 'orders'::regclass
)
SELECT 
    s.shardid,
    s.shard_size,
    ROUND((s.shard_size - ss.avg_size) / NULLIF(ss.stddev_size, 0), 2) as z_score
FROM citus_shards s, shard_stats ss
WHERE s.table_name = 'orders'::regclass
HAVING ABS((s.shard_size - ss.avg_size) / NULLIF(ss.stddev_size, 0)) > 2;
```

**处理数据倾斜**:

- 重新选择分片键
- 增加分片数量
- 使用复合分片键
- 拆分热点数据

### 2.3 常见陷阱

**陷阱1：使用自增ID作为分片键**:

```sql
-- 错误示例：自增ID导致新数据集中在最后的分片
CREATE TABLE bad_example (
    id SERIAL PRIMARY KEY,
    data TEXT
);
SELECT create_distributed_table('bad_example', 'id');
-- 问题：所有新插入都路由到同一分片

-- 正确做法：使用业务相关的稳定ID
CREATE TABLE good_example (
    id SERIAL,
    user_id BIGINT NOT NULL,
    data TEXT,
    PRIMARY KEY (id, user_id)
);
SELECT create_distributed_table('good_example', 'user_id');
```

**陷阱2：频繁跨分片查询**:

```sql
-- 低效查询：需要扫描所有分片
SELECT * FROM orders WHERE status = 'pending';

-- 高效查询：包含分片键
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';
```

## 3. 特殊表类型

### 3.1 分布式表

```sql
-- 标准分布式表
SELECT create_distributed_table('orders', 'user_id');

-- 指定分片数量
SELECT create_distributed_table('orders', 'user_id', shard_count := 16);

-- 指定副本数量
SELECT create_distributed_table('orders', 'user_id', 
                               shard_count := 16, 
                               replication_factor := 2);
```

### 3.2 引用表

**用途**：小型维度表，在所有节点复制

```sql
-- 创建引用表（广播表）
CREATE TABLE products (
    product_id BIGINT PRIMARY KEY,
    name TEXT,
    price NUMERIC
);

SELECT create_reference_table('products');

-- 优势：与分布式表JOIN时无需跨节点通信
SELECT o.*, p.name, p.price
FROM orders o
JOIN products p ON o.product_id = p.product_id
WHERE o.user_id = 123;
```

### 3.3 本地表

**用途**：仅在协调节点存在的表

```sql
-- 本地表（不分布）
CREATE TABLE system_config (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- 用于存储系统配置、元数据等
INSERT INTO system_config (key, value) 
VALUES ('version', '1.0.0');
```

## 4. 复制拓扑

### 4.1 主备复制

**配置主库**:

```sql
-- postgresql.conf (主库)
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
hot_standby = on

-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secret';

-- pg_hba.conf
host replication replicator 0.0.0.0/0 md5
```

**配置备库**:

```bash
# 创建备库
pg_basebackup -h primary_host -D /var/lib/postgresql/data \
  -U replicator -R -P --wal-method=stream

# standby.signal 文件自动创建（PostgreSQL 12+）
```

### 4.2 级联复制

**拓扑结构**:

```text
Primary → Standby1 → Standby2
             ↓
          Standby3
```

**配置级联备库**:

```sql
-- Standby1 配置
-- postgresql.conf
hot_standby = on
max_wal_senders = 5  -- 允许下级备库连接

-- Standby2 从 Standby1 复制
primary_conninfo = 'host=standby1 port=5432 user=replicator password=secret'
```

### 4.3 多主复制

**使用逻辑复制实现**:

```sql
-- Node1 配置
CREATE PUBLICATION pub_orders FOR TABLE orders;

-- Node2 配置
CREATE SUBSCRIPTION sub_from_node1
CONNECTION 'host=node1 dbname=mydb user=repl'
PUBLICATION pub_orders;

-- Node2 也发布
CREATE PUBLICATION pub_orders FOR TABLE orders;

-- Node1 订阅 Node2
CREATE SUBSCRIPTION sub_from_node2
CONNECTION 'host=node2 dbname=mydb user=repl'
PUBLICATION pub_orders;
```

## 5. 复制模式

### 5.1 同步复制

**配置**:

```sql
-- 主库配置
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby1, standby2)';
SELECT pg_reload_conf();

-- 检查同步状态
SELECT application_name, state, sync_state
FROM pg_stat_replication;
```

**优势与代价**:

- 优势：零数据丢失（RPO=0）
- 代价：写入延迟增加、可用性降低

### 5.2 异步复制

**配置**:

```sql
-- 默认模式，无需特殊配置
synchronous_commit = off

-- 检查复制延迟
SELECT 
    application_name,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn)) as lag
FROM pg_stat_replication;
```

### 5.3 半同步复制

**配置**:

```sql
-- 至少1个备库确认
synchronous_standby_names = 'ANY 1 (standby1, standby2, standby3)';

-- 仲裁复制：任意2个确认
synchronous_standby_names = 'ANY 2 (standby1, standby2, standby3)';
```

## 6. 副本放置策略

### 6.1 跨可用区部署

```sql
-- Citus节点标签
SELECT * FROM citus_add_node('worker1.az1', 5432, nodecluster := 'az1');
SELECT * FROM citus_add_node('worker2.az2', 5432, nodecluster := 'az2');
SELECT * FROM citus_add_node('worker3.az3', 5432, nodecluster := 'az3');

-- 配置副本放置
ALTER TABLE orders SET (citus.shard_replication_factor = 3);
```

### 6.2 跨区域部署

**使用逻辑复制**:

```sql
-- 主区域（us-east）发布
CREATE PUBLICATION pub_cross_region FOR ALL TABLES;

-- 从区域（eu-west）订阅
CREATE SUBSCRIPTION sub_from_us
CONNECTION 'host=primary-us.example.com dbname=mydb'
PUBLICATION pub_cross_region
WITH (copy_data = false);  -- 避免初始全量复制
```

## 7. 故障域与仲裁

### 7.1 仲裁机制

**奇数投票原则**:

- 3节点集群：允许1个节点失败
- 5节点集群：允许2个节点失败
- 避免脑裂：需要 (N/2)+1 个节点

### 7.2 见证节点

```sql
-- 配置见证节点（轻量级，不存储数据）
-- 仅用于仲裁投票
CREATE EXTENSION IF NOT EXISTS pg_witness;

-- 见证节点配置
witness = on
witness_sync_timeout = 1000  -- 1秒超时
```

## 8. 查询执行

### 8.1 查询路由

**单分片路由**（最优）:

```sql
-- 查询包含分片键，直接路由到对应分片
SELECT * FROM orders WHERE user_id = 123;

-- 执行计划
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM orders WHERE user_id = 123;
-- Result: Custom Scan (Citus Adaptive)
--   Task Count: 1  -- 只查询1个分片
```

**多分片路由**:

```sql
-- 不包含分片键，需要查询所有分片
SELECT COUNT(*) FROM orders WHERE status = 'pending';

-- 执行计划
-- Task Count: 32  -- 查询所有32个分片
```

### 8.2 并行执行

```sql
-- 启用并行查询
SET max_parallel_workers_per_gather = 4;
SET citus.max_adaptive_executor_pool_size = 16;

-- 分片内并行 + 跨分片并行
SELECT 
    DATE(order_date) as date,
    COUNT(*),
    SUM(amount)
FROM orders
WHERE order_date > '2025-01-01'
GROUP BY DATE(order_date);
```

### 8.3 跨分片连接

**重分布策略**:

```sql
-- 跨分片JOIN（自动重分布）
SELECT o.*, u.name
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.amount > 1000;

-- Citus自动选择重分布策略：
-- 1. 广播小表
-- 2. 重分片大表
-- 3. 协调节点合并结果
```

## 9. 数据重分布

**重新平衡分片**:

```sql
-- 增加工作节点
SELECT * FROM citus_add_node('worker4', 5432);

-- 重新平衡
SELECT citus_rebalance_start();

-- 监控重平衡进度
SELECT * FROM citus_rebalance_status();
```

## 10. 工程实践

**分片键选择检查清单**:

- ✅ 高基数字段
- ✅ 大部分查询包含此字段
- ✅ 数据分布均匀
- ✅ 不会随时间变化（避免重分片）

**复制配置建议**:

- 生产环境：至少3个节点（1主2备）
- 关键业务：同步复制 + 异步备份
- 跨区域：逻辑复制 + 定期快照

**监控指标**:

- 分片大小分布（检测倾斜）
- 复制延迟
- 跨分片查询比例
- 重分布任务进度

## 参考资源

- [Wikipedia: Database Shard](https://en.wikipedia.org/wiki/Shard_(database))
- [Citus Distributed Tables](https://docs.citusdata.com/en/stable/develop/reference_sql.html)
- [PostgreSQL Replication](https://www.postgresql.org/docs/current/high-availability.html)
- [Citus Shard Rebalancing](https://docs.citusdata.com/en/stable/admin_guide/cluster_management.html)
