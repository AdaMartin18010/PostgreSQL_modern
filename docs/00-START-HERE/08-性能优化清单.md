# ✅ 性能优化完整检查清单：PostgreSQL 18 + AI

> **更新日期**: 2025年12月4日
> **适用场景**: 性能问题诊断、系统优化、上线前检查
> **使用方法**: 逐项检查，标记✅完成项

---

## 🎯 快速诊断（5分钟）

### 第一步：确定问题类型

- [ ] **查询慢**：单个查询执行时间长
- [ ] **吞吐低**：QPS/TPS低
- [ ] **响应慢**：用户感知延迟高
- [ ] **资源高**：CPU/内存/磁盘使用率高
- [ ] **稳定性**：偶发慢查询或崩溃

### 第二步：收集基础信息

```sql
-- 1. 检查当前活跃查询
SELECT pid, usename, state, query, now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC
LIMIT 10;

-- 2. 检查慢查询（Top 10）
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. 检查表膨胀
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- 4. 检查索引使用率
SELECT schemaname, tablename, indexname,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan
LIMIT 10;
```

---

## 📊 数据库级优化

### 1. 配置参数优化 ✅

#### 内存配置

- [ ] **shared_buffers**：设置为系统内存的25%

  ```sql
  -- 推荐：32GB内存 → 8GB
  ALTER SYSTEM SET shared_buffers = '8GB';
  ```

- [ ] **effective_cache_size**：设置为系统内存的50-75%

  ```sql
  -- 推荐：32GB内存 → 24GB
  ALTER SYSTEM SET effective_cache_size = '24GB';
  ```

- [ ] **work_mem**：根据并发数设置（总内存 / max_connections / 2）

  ```sql
  -- 推荐：32GB内存，100连接 → 160MB
  ALTER SYSTEM SET work_mem = '160MB';
  ```

- [ ] **maintenance_work_mem**：设置为1-2GB

  ```sql
  ALTER SYSTEM SET maintenance_work_mem = '2GB';
  ```

#### 连接配置

- [ ] **max_connections**：根据实际需求设置（通常100-200）

  ```sql
  ALTER SYSTEM SET max_connections = 200;
  ```

- [ ] 使用连接池（PgBouncer/Pgpool-II）

  ```bash
  # PgBouncer配置
  [databases]
  mydb = host=localhost port=5432 dbname=mydb

  [pgbouncer]
  pool_mode = transaction
  max_client_conn = 1000
  default_pool_size = 20
  ```

#### WAL配置

- [ ] **wal_buffers**：16MB（默认）

  ```sql
  ALTER SYSTEM SET wal_buffers = '16MB';
  ```

- [ ] **checkpoint_timeout**：5-15分钟

  ```sql
  ALTER SYSTEM SET checkpoint_timeout = '10min';
  ```

- [ ] **max_wal_size**：1-4GB

  ```sql
  ALTER SYSTEM SET max_wal_size = '2GB';
  ```

#### 查询规划器

- [ ] **random_page_cost**：SSD设置为1.1，HDD设置为4.0

  ```sql
  ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD
  ```

- [ ] **effective_io_concurrency**：SSD设置为200

  ```sql
  ALTER SYSTEM SET effective_io_concurrency = 200;
  ```

### 2. 统计信息 ✅

- [ ] **启用pg_stat_statements**

  ```sql
  CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
  ```

- [ ] **定期执行ANALYZE**

  ```sql
  -- 手动分析重要表
  ANALYZE VERBOSE table_name;

  -- 自动VACUUM配置
  ALTER SYSTEM SET autovacuum = on;
  ALTER SYSTEM SET autovacuum_naptime = '1min';
  ```

- [ ] **检查统计信息准确性**

  ```sql
  SELECT schemaname, tablename, last_analyze, last_autoanalyze
  FROM pg_stat_user_tables
  WHERE last_analyze < NOW() - INTERVAL '7 days';
  ```

---

## 🔍 查询级优化

### 1. 查询分析 ✅

- [ ] **使用EXPLAIN ANALYZE**

  ```sql
  EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
  SELECT * FROM orders WHERE customer_id = 123;
  ```

- [ ] **识别瓶颈**
  - [ ] Seq Scan（全表扫描）→ 需要索引
  - [ ] Nested Loop（嵌套循环）→ 考虑Hash Join
  - [ ] Sort（排序）→ 考虑索引排序
  - [ ] Hash Join过大 → 增加work_mem

### 2. 索引优化 ✅

#### B-tree索引（通用）

- [ ] **单列索引**

  ```sql
  CREATE INDEX idx_orders_customer ON orders(customer_id);
  ```

- [ ] **复合索引**（注意列顺序）

  ```sql
  -- 选择性高的列在前
  CREATE INDEX idx_orders_status_date
  ON orders(status, created_at);
  ```

- [ ] **覆盖索引**（INCLUDE子句）

  ```sql
  CREATE INDEX idx_orders_covering
  ON orders(customer_id) INCLUDE (amount, status);
  ```

#### 向量索引（AI应用）

- [ ] **HNSW索引**（推荐，精度高）

  ```sql
  CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```

- [ ] **IVFFlat索引**（大数据量，性能好）

  ```sql
  CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
  ```

- [ ] **参数调优**

  ```sql
  -- HNSW查询参数
  SET hnsw.ef_search = 100;

  -- IVFFlat查询参数
  SET ivfflat.probes = 10;
  ```

#### 其他专用索引

- [ ] **GIN索引**（全文搜索、JSONB、数组）

  ```sql
  CREATE INDEX idx_documents_fts ON documents USING gin(to_tsvector('english', content));
  CREATE INDEX idx_data_jsonb ON data USING gin(metadata);
  ```

- [ ] **GiST索引**（空间数据、范围类型）

  ```sql
  CREATE INDEX idx_locations_geo ON locations USING gist(geom);
  ```

- [ ] **BRIN索引**（时序数据、线性相关数据）

  ```sql
  CREATE INDEX idx_events_time ON events USING brin(created_at);
  ```

### 3. 查询重写 ✅

- [ ] **避免SELECT \***

  ```sql
  -- ❌ 不好
  SELECT * FROM orders;

  -- ✅ 好
  SELECT id, customer_id, amount FROM orders;
  ```

- [ ] **使用EXISTS代替IN（子查询）**

  ```sql
  -- ❌ 慢
  SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE active = true);

  -- ✅ 快
  SELECT * FROM orders o WHERE EXISTS (SELECT 1 FROM customers c WHERE c.id = o.customer_id AND c.active = true);
  ```

- [ ] **使用JOIN代替子查询**

  ```sql
  -- ❌ 慢
  SELECT *, (SELECT name FROM customers WHERE id = orders.customer_id) FROM orders;

  -- ✅ 快
  SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id;
  ```

- [ ] **使用CTE优化复杂查询**

  ```sql
  WITH active_customers AS (
      SELECT id FROM customers WHERE active = true
  )
  SELECT o.* FROM orders o
  JOIN active_customers ac ON o.customer_id = ac.id;
  ```

---

## 🎯 向量搜索优化

### 1. 索引选择 ✅

| 数据量 | 推荐索引 | 参数建议 |
|--------|---------|---------|
| <10万 | 无索引（暴力搜索） | - |
| 10万-100万 | HNSW | m=16, ef_construction=64 |
| >100万 | IVFFlat | lists=sqrt(rows) |

### 2. HNSW调优 ✅

- [ ] **m参数**（连接数，越大精度越高但内存越大）

  ```sql
  -- 平衡：m=16（默认）
  -- 高精度：m=32
  -- 低内存：m=8
  CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16);
  ```

- [ ] **ef_construction**（构建质量，越大精度越高但构建越慢）

  ```sql
  -- 平衡：ef_construction=64（默认）
  -- 高精度：ef_construction=200
  -- 快速构建：ef_construction=32
  WITH (ef_construction = 64);
  ```

- [ ] **ef_search**（查询质量，运行时参数）

  ```sql
  -- 查询前设置
  SET hnsw.ef_search = 100;  -- 越大越精确但越慢
  ```

### 3. IVFFlat调优 ✅

- [ ] **lists参数**（聚类数量）

  ```sql
  -- 推荐：sqrt(总行数)
  -- 100万行 → lists=1000
  CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 1000);
  ```

- [ ] **probes参数**（查询探测数）

  ```sql
  -- 运行时设置
  SET ivfflat.probes = 10;  -- 越大越精确但越慢
  ```

### 4. 混合检索 ✅

- [ ] **向量 + 关键词过滤**

  ```sql
  SELECT *, 1 - (embedding <=> query_vector) AS similarity
  FROM documents
  WHERE category = 'tech'  -- 先过滤
  ORDER BY embedding <=> query_vector
  LIMIT 10;
  ```

- [ ] **向量 + 全文搜索**

  ```sql
  SELECT *,
         1 - (embedding <=> query_vector) AS vec_sim,
         ts_rank(to_tsvector('english', content), query) AS text_rank
  FROM documents
  WHERE to_tsvector('english', content) @@ query
  ORDER BY (vec_sim * 0.7 + text_rank * 0.3) DESC
  LIMIT 10;
  ```

---

## 🗄️ 表结构优化

### 1. 分区表 ✅

- [ ] **按时间分区**（日志、订单等）

  ```sql
  CREATE TABLE orders (
      id BIGSERIAL,
      created_at TIMESTAMPTZ NOT NULL,
      ...
  ) PARTITION BY RANGE (created_at);

  -- 创建月度分区
  CREATE TABLE orders_2025_01 PARTITION OF orders
      FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
  ```

- [ ] **按列表分区**（区域、类型等）

  ```sql
  CREATE TABLE users (
      id BIGSERIAL,
      country VARCHAR(2),
      ...
  ) PARTITION BY LIST (country);

  CREATE TABLE users_us PARTITION OF users
      FOR VALUES IN ('US');
  ```

- [ ] **按哈希分区**（均匀分布）

  ```sql
  CREATE TABLE events (
      id BIGSERIAL,
      ...
  ) PARTITION BY HASH (id);

  CREATE TABLE events_0 PARTITION OF events
      FOR VALUES WITH (MODULUS 4, REMAINDER 0);
  ```

### 2. 数据类型优化 ✅

- [ ] **使用合适的数据类型**

  ```sql
  -- ❌ 不好
  amount VARCHAR(20)

  -- ✅ 好
  amount NUMERIC(10, 2)
  ```

- [ ] **使用ENUM代替VARCHAR**（固定选项）

  ```sql
  CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'delivered');
  ALTER TABLE orders ADD COLUMN status order_status;
  ```

- [ ] **使用JSONB代替TEXT**（半结构化数据）

  ```sql
  -- ✅ JSONB支持索引和查询
  metadata JSONB
  ```

### 3. 表维护 ✅

- [ ] **定期VACUUM**

  ```sql
  VACUUM ANALYZE table_name;
  ```

- [ ] **REINDEX重建索引**

  ```sql
  REINDEX TABLE table_name;
  ```

- [ ] **检查表膨胀**

  ```sql
  SELECT schemaname, tablename,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
         n_dead_tup
  FROM pg_stat_user_tables
  WHERE n_dead_tup > 10000
  ORDER BY n_dead_tup DESC;
  ```

---

## 🚀 应用层优化

### 1. 连接管理 ✅

- [ ] **使用连接池**（必需）

  ```python
  from psycopg2.pool import SimpleConnectionPool

  pool = SimpleConnectionPool(
      minconn=10,
      maxconn=100,
      dsn="postgresql://localhost/mydb"
  )
  ```

- [ ] **设置合理的超时**

  ```python
  conn = psycopg2.connect(
      "postgresql://localhost/mydb",
      connect_timeout=3,
      options="-c statement_timeout=30000"  # 30秒
  )
  ```

### 2. 批量操作 ✅

- [ ] **批量插入**

  ```python
  # ❌ 慢：逐条插入
  for row in data:
      cur.execute("INSERT INTO table VALUES (%s, %s)", row)

  # ✅ 快：批量插入
  cur.executemany("INSERT INTO table VALUES (%s, %s)", data)

  # ✅ 更快：COPY
  from io import StringIO
  f = StringIO('\n'.join(','.join(map(str, row)) for row in data))
  cur.copy_from(f, 'table', sep=',')
  ```

- [ ] **批量更新**

  ```sql
  -- 使用临时表 + JOIN
  CREATE TEMP TABLE tmp_updates (id INT, new_value TEXT);
  COPY tmp_updates FROM ...;

  UPDATE main_table m
  SET value = t.new_value
  FROM tmp_updates t
  WHERE m.id = t.id;
  ```

### 3. 缓存策略 ✅

- [ ] **查询结果缓存**（Redis/Memcached）

  ```python
  def get_data(key):
      # 先查缓存
      data = cache.get(key)
      if data:
          return data

      # 缓存未命中，查数据库
      data = db.query(...)
      cache.set(key, data, timeout=300)
      return data
  ```

- [ ] **PostgreSQL prepared statements**

  ```python
  # 预编译语句，减少解析开销
  cur.execute("PREPARE myplan AS SELECT * FROM table WHERE id = $1")
  cur.execute("EXECUTE myplan(123)")
  ```

---

## 📊 监控与诊断

### 1. 实时监控 ✅

- [ ] **慢查询日志**

  ```sql
  ALTER SYSTEM SET log_min_duration_statement = '1000';  -- 记录>1秒的查询
  ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
  ```

- [ ] **pg_stat_statements监控**

  ```sql
  -- Top 10慢查询
  SELECT query, calls, mean_exec_time, total_exec_time,
         stddev_exec_time, min_exec_time, max_exec_time
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
  ```

- [ ] **活跃会话监控**

  ```sql
  SELECT pid, usename, application_name, client_addr,
         state, query, now() - query_start AS duration
  FROM pg_stat_activity
  WHERE state != 'idle' AND query_start < NOW() - INTERVAL '1 minute';
  ```

### 2. 资源监控 ✅

- [ ] **表和索引大小**

  ```sql
  SELECT schemaname, tablename,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
         pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) -
                       pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
  FROM pg_tables
  WHERE schemaname = 'public'
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
  ```

- [ ] **缓存命中率**

  ```sql
  SELECT SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit + heap_blks_read), 0) AS cache_hit_ratio
  FROM pg_statio_user_tables;
  -- 目标：>99%
  ```

- [ ] **连接数监控**

  ```sql
  SELECT count(*) AS total_connections,
         count(*) FILTER (WHERE state = 'active') AS active,
         count(*) FILTER (WHERE state = 'idle') AS idle
  FROM pg_stat_activity;
  ```

---

## ✅ 上线前检查清单

### 数据库配置 ✅

- [ ] 内存参数已调优
- [ ] 连接池已配置
- [ ] WAL参数已设置
- [ ] 统计信息已收集
- [ ] 慢查询日志已启用

### 索引检查 ✅

- [ ] 所有WHERE列有索引
- [ ] 所有JOIN列有索引
- [ ] 向量列有HNSW/IVFFlat索引
- [ ] 全文搜索有GIN索引
- [ ] 无冗余索引

### 查询检查 ✅

- [ ] 所有查询已EXPLAIN分析
- [ ] 无全表扫描（关键查询）
- [ ] 无子查询嵌套过深
- [ ] 批量操作已优化

### 监控检查 ✅

- [ ] Prometheus + Grafana已部署
- [ ] 慢查询告警已配置
- [ ] 资源使用告警已配置
- [ ] 连接数告警已配置

### 备份检查 ✅

- [ ] 全量备份策略已制定
- [ ] 增量备份已配置
- [ ] PITR已启用
- [ ] 恢复流程已测试

---

**使用本清单，系统性优化你的PostgreSQL！** 🚀

---

**最后更新**: 2025年12月4日
**维护者**: PostgreSQL Modern Team
**文档编号**: CHECKLIST-2025-12
