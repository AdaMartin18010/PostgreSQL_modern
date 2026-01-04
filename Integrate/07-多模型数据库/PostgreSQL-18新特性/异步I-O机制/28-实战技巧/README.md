# 28. 实战技巧与高级优化

> **章节编号**: 28
> **章节标题**: 实战技巧与高级优化
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 📑 目录

- [28. 实战技巧与高级优化](#28-实战技巧与高级优化)
  - [📑 目录](#-目录)
  - [28. 实战技巧与高级优化](#28-实战技巧与高级优化-1)
    - [28.1 高级配置技巧](#281-高级配置技巧)
      - [28.1.1 动态参数调整技巧](#2811-动态参数调整技巧)
      - [28.1.2 会话级参数优化技巧](#2812-会话级参数优化技巧)
    - [28.2 性能调优实战技巧](#282-性能调优实战技巧)
      - [28.2.1 I/O预热技巧](#2821-io预热技巧)
      - [28.2.2 批量操作优化技巧](#2822-批量操作优化技巧)
    - [28.3 故障排查高级技巧](#283-故障排查高级技巧)
      - [28.3.1 深度诊断技巧](#2831-深度诊断技巧)
      - [28.3.2 自动化诊断技巧](#2832-自动化诊断技巧)
    - [28.4 生产环境优化技巧](#284-生产环境优化技巧)
      - [28.4.1 高可用环境优化](#2841-高可用环境优化)
      - [28.4.2 云环境优化技巧](#2842-云环境优化技巧)
      - [28.4.3 混合工作负载优化](#2843-混合工作负载优化)

---

## 28. 实战技巧与高级优化

### 28.1 高级配置技巧

#### 28.1.1 动态参数调整技巧

**技巧1：基于工作负载的动态调整**

根据不同的工作负载动态调整异步I/O参数：

```sql
-- 创建动态调整函数
CREATE OR REPLACE FUNCTION adjust_io_concurrency()
RETURNS void AS $$
DECLARE
    current_time INTEGER;
    current_load NUMERIC;
    optimal_concurrency INTEGER;
BEGIN
    -- 获取当前时间（小时）
    current_time := EXTRACT(HOUR FROM NOW());

    -- 获取当前I/O负载
    SELECT AVG(reads + writes) INTO current_load
    FROM pg_stat_io
    WHERE context = 'normal';

    -- 根据时间和负载调整并发度
    IF current_time BETWEEN 9 AND 18 THEN
        -- 工作时间：高并发
        optimal_concurrency := 400;
    ELSIF current_time BETWEEN 19 AND 23 THEN
        -- 晚间：中等并发
        optimal_concurrency := 300;
    ELSE
        -- 夜间：低并发（维护任务）
        optimal_concurrency := 200;
    END IF;

    -- 根据负载微调
    IF current_load > 10000 THEN
        optimal_concurrency := optimal_concurrency + 50;
    ELSIF current_load < 1000 THEN
        optimal_concurrency := optimal_concurrency - 50;
    END IF;

    -- 应用配置
    EXECUTE format('ALTER SYSTEM SET effective_io_concurrency = %s', optimal_concurrency);
    PERFORM pg_reload_conf();

    RAISE NOTICE '已调整effective_io_concurrency为: %', optimal_concurrency;
END;
$$ LANGUAGE plpgsql;

-- 使用pg_cron定期执行（需要安装pg_cron扩展）
SELECT cron.schedule('adjust-io-concurrency', '*/30 * * * *',
    'SELECT adjust_io_concurrency();');
```

**技巧2：基于存储性能的自适应配置**

根据存储设备的实际性能自动调整配置：

```sql
-- 存储性能检测和配置函数
CREATE OR REPLACE FUNCTION auto_configure_io()
RETURNS void AS $$
DECLARE
    io_bandwidth_mbps NUMERIC;
    io_latency_ms NUMERIC;
    recommended_concurrency INTEGER;
    recommended_queue_depth INTEGER;
BEGIN
    -- 检测I/O带宽（简化示例，实际需要更复杂的检测逻辑）
    SELECT
        AVG(CASE WHEN reads > 0 THEN (reads * 8.0 / 1024 / 1024) / NULLIF(read_time / 1000.0, 0) ELSE 0 END)
    INTO io_bandwidth_mbps
    FROM pg_stat_io
    WHERE context = 'normal';

    -- 检测I/O延迟
    SELECT AVG(read_time) INTO io_latency_ms
    FROM pg_stat_io
    WHERE context = 'normal' AND reads > 0;

    -- 根据带宽和延迟推荐配置
    IF io_bandwidth_mbps > 2000 AND io_latency_ms < 1 THEN
        -- NVMe SSD
        recommended_concurrency := 400;
        recommended_queue_depth := 1024;
    ELSIF io_bandwidth_mbps > 500 AND io_latency_ms < 5 THEN
        -- SATA SSD
        recommended_concurrency := 200;
        recommended_queue_depth := 512;
    ELSE
        -- HDD或其他
        recommended_concurrency := 50;
        recommended_queue_depth := 128;
    END IF;

    -- 应用推荐配置
    EXECUTE format('ALTER SYSTEM SET effective_io_concurrency = %s', recommended_concurrency);
    EXECUTE format('ALTER SYSTEM SET io_uring_queue_depth = %s', recommended_queue_depth);
    PERFORM pg_reload_conf();

    RAISE NOTICE '检测到I/O带宽: % MB/s, 延迟: % ms', io_bandwidth_mbps, io_latency_ms;
    RAISE NOTICE '推荐配置: effective_io_concurrency=%s, io_uring_queue_depth=%s',
        recommended_concurrency, recommended_queue_depth;
END;
$$ LANGUAGE plpgsql;
```

#### 28.1.2 会话级参数优化技巧

**技巧3：查询级I/O优化**

针对特定查询优化I/O参数：

```sql
-- 大表扫描查询优化
SET effective_io_concurrency = 500;  -- 提高并发度
SET work_mem = '512MB';  -- 增加工作内存
SET max_parallel_workers_per_gather = 8;  -- 启用并行查询

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM large_table WHERE condition;

-- 恢复默认值
RESET effective_io_concurrency;
RESET work_mem;
RESET max_parallel_workers_per_gather;
```

**技巧4：事务级I/O优化**

针对特定事务优化I/O参数：

```sql
-- 批量导入事务优化
BEGIN;
SET LOCAL effective_io_concurrency = 400;
SET LOCAL maintenance_io_concurrency = 300;
SET LOCAL work_mem = '256MB';

-- 执行批量导入
COPY large_table FROM '/path/to/data.csv' WITH (FORMAT csv);

COMMIT;
-- 事务结束后自动恢复默认值
```

---

---

### 28.2 性能调优实战技巧

#### 28.2.1 I/O预热技巧

**技巧5：数据库启动后I/O预热**

数据库启动后预热I/O子系统，提高后续查询性能：

```sql
-- I/O预热函数
CREATE OR REPLACE FUNCTION warmup_io()
RETURNS void AS $$
DECLARE
    table_rec RECORD;
    warmup_query TEXT;
BEGIN
    RAISE NOTICE '开始I/O预热...';

    -- 预热主要表
    FOR table_rec IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10
    LOOP
        warmup_query := format('SELECT COUNT(*) FROM %I.%I',
            table_rec.schemaname, table_rec.tablename);

        BEGIN
            EXECUTE warmup_query;
            RAISE NOTICE '已预热表: %.%', table_rec.schemaname, table_rec.tablename;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '预热表 %.% 失败: %',
                    table_rec.schemaname, table_rec.tablename, SQLERRM;
        END;
    END LOOP;

    RAISE NOTICE 'I/O预热完成';
END;
$$ LANGUAGE plpgsql;

-- 数据库启动后执行预热
SELECT warmup_io();
```

**技巧6：索引预热技巧**

预热常用索引，提高查询性能：

```sql
-- 索引预热函数
CREATE OR REPLACE FUNCTION warmup_indexes()
RETURNS void AS $$
DECLARE
    index_rec RECORD;
BEGIN
    RAISE NOTICE '开始索引预热...';

    -- 预热常用索引
    FOR index_rec IN
        SELECT
            schemaname,
            tablename,
            indexname
        FROM pg_indexes
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY pg_relation_size(indexname::regclass) DESC
        LIMIT 20
    LOOP
        BEGIN
            -- 使用索引进行小范围扫描
            EXECUTE format('SELECT COUNT(*) FROM %I.%I WHERE ctid < ''(100,0)''',
                index_rec.schemaname, index_rec.tablename);
            RAISE NOTICE '已预热索引: %.%', index_rec.schemaname, index_rec.indexname;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '预热索引 %.% 失败: %',
                    index_rec.schemaname, index_rec.indexname, SQLERRM;
        END;
    END LOOP;

    RAISE NOTICE '索引预热完成';
END;
$$ LANGUAGE plpgsql;
```

#### 28.2.2 批量操作优化技巧

**技巧7：智能批量大小调整**

根据系统负载动态调整批量大小：

```python
#!/usr/bin/env python3
"""
智能批量大小调整工具
"""
import psycopg2
from psycopg2.extras import execute_values
import time
import statistics

class AdaptiveBatchInserter:
    def __init__(self, conn, table_name, columns):
        self.conn = conn
        self.table_name = table_name
        self.columns = columns
        self.batch_size = 1000
        self.min_batch_size = 100
        self.max_batch_size = 10000
        self.performance_history = []

    def insert_batch(self, data):
        """插入一批数据，记录性能"""
        cur = self.conn.cursor()

        start_time = time.time()
        try:
            execute_values(
                cur,
                f"INSERT INTO {self.table_name} ({','.join(self.columns)}) VALUES %s",
                data,
                page_size=self.batch_size
            )
            self.conn.commit()
            elapsed = time.time() - start_time
            throughput = len(data) / elapsed

            # 记录性能
            self.performance_history.append({
                'batch_size': self.batch_size,
                'throughput': throughput,
                'elapsed': elapsed
            })

            # 保持最近10次记录
            if len(self.performance_history) > 10:
                self.performance_history.pop(0)

            # 自适应调整批量大小
            self._adjust_batch_size()

            return True
        except Exception as e:
            self.conn.rollback()
            print(f"批量插入失败: {e}")
            # 失败时减少批量大小
            self.batch_size = max(self.batch_size // 2, self.min_batch_size)
            return False

    def _adjust_batch_size(self):
        """根据性能历史调整批量大小"""
        if len(self.performance_history) < 3:
            return

        # 计算平均吞吐量
        avg_throughput = statistics.mean([p['throughput'] for p in self.performance_history])

        # 如果吞吐量高且批量大小未达上限，增加批量大小
        if avg_throughput > 5000 and self.batch_size < self.max_batch_size:
            self.batch_size = min(self.batch_size * 2, self.max_batch_size)
        # 如果吞吐量低，减少批量大小
        elif avg_throughput < 1000 and self.batch_size > self.min_batch_size:
            self.batch_size = max(self.batch_size // 2, self.min_batch_size)

    def get_current_batch_size(self):
        return self.batch_size

# 使用示例
conn = psycopg2.connect(DATABASE_URL)
inserter = AdaptiveBatchInserter(conn, 'documents', ['content', 'metadata'])

data = [(f'content_{i}', f'metadata_{i}') for i in range(100000)]
for i in range(0, len(data), inserter.get_current_batch_size()):
    batch = data[i:i+inserter.get_current_batch_size()]
    inserter.insert_batch(batch)
    print(f"已插入批次，当前批量大小: {inserter.get_current_batch_size()}")
```

**技巧8：并行批量写入优化**

利用PostgreSQL的并行写入能力：

```sql
-- 并行批量写入函数
CREATE OR REPLACE FUNCTION parallel_batch_insert(
    target_table TEXT,
    source_table TEXT,
    batch_size INTEGER DEFAULT 10000,
    parallel_workers INTEGER DEFAULT 4
)
RETURNS void AS $$
DECLARE
    total_rows BIGINT;
    batches INTEGER;
    i INTEGER;
BEGIN
    -- 获取总行数
    EXECUTE format('SELECT COUNT(*) FROM %I', source_table) INTO total_rows;
    batches := CEIL(total_rows::NUMERIC / batch_size);

    RAISE NOTICE '总行数: %, 批量大小: %, 批次数: %', total_rows, batch_size, batches;

    -- 并行插入（使用多个会话）
    FOR i IN 0..batches-1 LOOP
        -- 这里需要外部工具（如pg_bulkload）或应用层实现真正的并行
        -- PostgreSQL本身不支持单个事务内的并行INSERT
        EXECUTE format('
            INSERT INTO %I
            SELECT * FROM %I
            ORDER BY ctid
            LIMIT %s OFFSET %s
        ', target_table, source_table, batch_size, i * batch_size);

        IF i % 10 = 0 THEN
            RAISE NOTICE '已完成批次: %/%', i, batches;
        END IF;
    END LOOP;

    RAISE NOTICE '并行批量插入完成';
END;
$$ LANGUAGE plpgsql;
```

---

### 28.3 故障排查高级技巧

#### 28.3.1 深度诊断技巧

**技巧9：I/O瓶颈深度分析**

深入分析I/O瓶颈，识别具体问题：

```sql
-- I/O瓶颈深度分析函数
CREATE OR REPLACE FUNCTION analyze_io_bottleneck()
RETURNS TABLE(
    bottleneck_type TEXT,
    severity TEXT,
    description TEXT,
    recommendation TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH io_stats AS (
        SELECT
            context,
            SUM(reads) as total_reads,
            SUM(writes) as total_writes,
            AVG(read_time) as avg_read_time,
            AVG(write_time) as avg_write_time,
            MAX(read_time) as max_read_time,
            MAX(write_time) as max_write_time
        FROM pg_stat_io
        GROUP BY context
    ),
    bottlenecks AS (
        SELECT
            '高延迟读取'::TEXT as bottleneck_type,
            CASE
                WHEN avg_read_time > 20 THEN '严重'
                WHEN avg_read_time > 10 THEN '中等'
                ELSE '轻微'
            END as severity,
            format('平均读取延迟: %s ms', ROUND(avg_read_time, 2)) as description,
            format('建议: 1) 检查存储性能 2) 提高effective_io_concurrency到300+ 3) 检查是否有I/O竞争') as recommendation
        FROM io_stats
        WHERE avg_read_time > 5

        UNION ALL

        SELECT
            '高延迟写入'::TEXT,
            CASE
                WHEN avg_write_time > 20 THEN '严重'
                WHEN avg_write_time > 10 THEN '中等'
                ELSE '轻微'
            END,
            format('平均写入延迟: %s ms', ROUND(avg_write_time, 2)),
            format('建议: 1) 检查WAL写入性能 2) 提高wal_io_concurrency到200+ 3) 优化WAL配置')
        FROM io_stats
        WHERE avg_write_time > 5

        UNION ALL

        SELECT
            'I/O竞争'::TEXT,
            CASE
                WHEN max_read_time > avg_read_time * 5 THEN '严重'
                WHEN max_read_time > avg_read_time * 3 THEN '中等'
                ELSE '轻微'
            END,
            format('最大读取延迟: %s ms, 平均: %s ms',
                ROUND(max_read_time, 2), ROUND(avg_read_time, 2)),
            format('建议: 1) 检查是否有其他进程竞争I/O 2) 使用I/O优先级 3) 分离数据文件和WAL文件')
        FROM io_stats
        WHERE max_read_time > avg_read_time * 2
    )
    SELECT * FROM bottlenecks
    ORDER BY
        CASE severity
            WHEN '严重' THEN 1
            WHEN '中等' THEN 2
            ELSE 3
        END;
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT * FROM analyze_io_bottleneck();
```

**技巧10：性能回归分析**

分析性能变化趋势，识别性能回归：

```sql
-- 性能回归分析函数
CREATE OR REPLACE FUNCTION analyze_performance_regression()
RETURNS TABLE(
    metric_name TEXT,
    current_value NUMERIC,
    baseline_value NUMERIC,
    change_percent NUMERIC,
    status TEXT
) AS $$
DECLARE
    baseline_date TIMESTAMP := NOW() - INTERVAL '7 days';
BEGIN
    RETURN QUERY
    WITH current_stats AS (
        SELECT
            'avg_read_time'::TEXT as metric_name,
            AVG(read_time)::NUMERIC as current_value
        FROM pg_stat_io
        WHERE context = 'normal'

        UNION ALL

        SELECT
            'avg_write_time'::TEXT,
            AVG(write_time)::NUMERIC
        FROM pg_stat_io
        WHERE context = 'normal'

        UNION ALL

        SELECT
            'throughput'::TEXT,
            (SUM(reads) + SUM(writes))::NUMERIC /
            NULLIF(EXTRACT(EPOCH FROM (NOW() - pg_postmaster_start_time())), 0)
        FROM pg_stat_io
    ),
    baseline_stats AS (
        -- 这里需要从历史数据中获取基线值
        -- 实际应用中需要使用pg_stat_statements或其他监控工具
        SELECT
            'avg_read_time'::TEXT as metric_name,
            5.0::NUMERIC as baseline_value  -- 示例基线值

        UNION ALL

        SELECT
            'avg_write_time'::TEXT,
            3.0::NUMERIC

        UNION ALL

        SELECT
            'throughput'::TEXT,
            10000.0::NUMERIC
    )
    SELECT
        c.metric_name,
        c.current_value,
        b.baseline_value,
        ROUND((c.current_value - b.baseline_value) / b.baseline_value * 100, 2) as change_percent,
        CASE
            WHEN (c.current_value - b.baseline_value) / b.baseline_value > 0.2 THEN '性能下降'
            WHEN (c.current_value - b.baseline_value) / b.baseline_value < -0.1 THEN '性能提升'
            ELSE '稳定'
        END as status
    FROM current_stats c
    JOIN baseline_stats b ON c.metric_name = b.metric_name;
END;
$$ LANGUAGE plpgsql;
```

#### 28.3.2 自动化诊断技巧

**技巧11：自动化健康检查**

定期自动执行健康检查，发现问题：

```sql
-- 自动化健康检查函数
CREATE OR REPLACE FUNCTION auto_health_check()
RETURNS TABLE(
    check_name TEXT,
    status TEXT,
    message TEXT,
    severity TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH checks AS (
        -- 检查1: 异步I/O是否启用
        SELECT
            '异步I/O配置'::TEXT as check_name,
            CASE
                WHEN (SELECT setting FROM pg_settings WHERE name = 'io_direct') = 'off'
                THEN '失败'::TEXT
                ELSE '通过'::TEXT
            END as status,
            CASE
                WHEN (SELECT setting FROM pg_settings WHERE name = 'io_direct') = 'off'
                THEN 'io_direct未启用，异步I/O可能未生效'
                ELSE '异步I/O配置正确'
            END as message,
            CASE
                WHEN (SELECT setting FROM pg_settings WHERE name = 'io_direct') = 'off'
                THEN '高'::TEXT
                ELSE '低'::TEXT
            END as severity

        UNION ALL

        -- 检查2: I/O延迟是否过高
        SELECT
            'I/O延迟检查'::TEXT,
            CASE
                WHEN (SELECT AVG(read_time) FROM pg_stat_io WHERE context = 'normal') > 10
                THEN '警告'::TEXT
                ELSE '通过'::TEXT
            END,
            CASE
                WHEN (SELECT AVG(read_time) FROM pg_stat_io WHERE context = 'normal') > 10
                THEN format('平均读取延迟: %s ms，超过10ms阈值',
                    ROUND((SELECT AVG(read_time) FROM pg_stat_io WHERE context = 'normal'), 2))
                ELSE 'I/O延迟正常'
            END,
            CASE
                WHEN (SELECT AVG(read_time) FROM pg_stat_io WHERE context = 'normal') > 10
                THEN '中'::TEXT
                ELSE '低'::TEXT
            END

        UNION ALL

        -- 检查3: 并发度配置是否合理
        SELECT
            '并发度配置'::TEXT,
            CASE
                WHEN (SELECT setting::INTEGER FROM pg_settings WHERE name = 'effective_io_concurrency') < 50
                THEN '警告'::TEXT
                ELSE '通过'::TEXT
            END,
            CASE
                WHEN (SELECT setting::INTEGER FROM pg_settings WHERE name = 'effective_io_concurrency') < 50
                THEN format('effective_io_concurrency=%s，可能过低，建议至少200',
                    (SELECT setting FROM pg_settings WHERE name = 'effective_io_concurrency'))
                ELSE '并发度配置合理'
            END,
            CASE
                WHEN (SELECT setting::INTEGER FROM pg_settings WHERE name = 'effective_io_concurrency') < 50
                THEN '中'::TEXT
                ELSE '低'::TEXT
            END
    )
    SELECT * FROM checks
    ORDER BY
        CASE severity
            WHEN '高' THEN 1
            WHEN '中' THEN 2
            ELSE 3
        END;
END;
$$ LANGUAGE plpgsql;

-- 定期执行健康检查（使用pg_cron）
SELECT cron.schedule('health-check', '*/15 * * * *',
    'SELECT * FROM auto_health_check();');
```

---

### 28.4 生产环境优化技巧

#### 28.4.1 高可用环境优化

**技巧12：主从复制环境优化**

在主从复制环境中优化异步I/O：

```sql
-- 主库配置（写入优化）
-- postgresql.conf (主库)
io_direct = 'data,wal'
effective_io_concurrency = 300
wal_io_concurrency = 200
synchronous_commit = 'on'  -- 保证一致性
wal_sync_method = 'fsync'

-- 从库配置（读取优化）
-- postgresql.conf (从库)
io_direct = 'data'
effective_io_concurrency = 400  -- 从库可以更高
max_parallel_workers_per_gather = 8
max_parallel_workers = 16

-- 从库查询优化
SET effective_io_concurrency = 400;
SET max_parallel_workers_per_gather = 8;
```

**技巧13：读写分离优化**

在读写分离环境中优化异步I/O：

```sql
-- 写库配置（主库）
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 300;
ALTER SYSTEM SET wal_io_concurrency = 200;

-- 读库配置（从库）
ALTER SYSTEM SET io_direct = 'data';
ALTER SYSTEM SET effective_io_concurrency = 500;  -- 读库可以更高
ALTER SYSTEM SET max_parallel_workers_per_gather = 16;
ALTER SYSTEM SET max_parallel_workers = 32;
```

#### 28.4.2 云环境优化技巧

**技巧14：云存储优化**

针对云存储（如AWS EBS、Azure Disk）优化：

```sql
-- 云存储优化配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 200;  -- 云存储适中配置
ALTER SYSTEM SET wal_io_concurrency = 150;
ALTER SYSTEM SET io_uring_queue_depth = 256;

-- 云存储特定优化
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD优化
ALTER SYSTEM SET effective_cache_size = '24GB';  -- 根据实例类型调整

-- 针对AWS EBS的优化
ALTER SYSTEM SET checkpoint_timeout = '15min';  -- 减少检查点频率
ALTER SYSTEM SET checkpoint_completion_target = 0.9;  -- 平滑检查点
```

**技巧15：容器环境优化**

在Docker/Kubernetes环境中优化：

```yaml
# Kubernetes StatefulSet配置优化
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:18
        env:
        - name: POSTGRES_INITDB_ARGS
          value: "--data-checksums"
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
          limits:
            memory: "16Gi"
            cpu: "8"
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        # 启用io_uring支持
        securityContext:
          capabilities:
            add: ["SYS_NICE"]
        # PostgreSQL配置
        command:
        - postgres
        - -c
        - "io_direct=data,wal"
        - -c
        - "effective_io_concurrency=200"
        - -c
        - "wal_io_concurrency=150"
```

#### 28.4.3 混合工作负载优化

**技巧16：OLTP和OLAP混合优化**

在混合工作负载环境中优化：

```sql
-- 混合负载配置
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET effective_io_concurrency = 300;  -- 平衡值
ALTER SYSTEM SET wal_io_concurrency = 150;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;  -- 适中并行度

-- 使用资源组隔离工作负载
CREATE RESOURCE GROUP oltp_group WITH (
    cpu_rate_limit = 60,
    memory_limit = 40
);

CREATE RESOURCE GROUP olap_group WITH (
    cpu_rate_limit = 40,
    memory_limit = 60
);

-- OLTP查询使用OLTP资源组
SET resource_group = 'oltp_group';
SELECT * FROM orders WHERE order_id = 12345;

-- OLAP查询使用OLAP资源组
SET resource_group = 'olap_group';
SELECT region, SUM(sales) FROM sales_fact GROUP BY region;
```

**技巧17：时间分片优化**

根据时间段优化配置：

```sql
-- 时间段优化函数
CREATE OR REPLACE FUNCTION time_based_optimization()
RETURNS void AS $$
DECLARE
    current_hour INTEGER;
    current_day_of_week INTEGER;
BEGIN
    current_hour := EXTRACT(HOUR FROM NOW());
    current_day_of_week := EXTRACT(DOW FROM NOW());

    -- 工作日工作时间（9-18点）：OLTP优化
    IF current_day_of_week BETWEEN 1 AND 5 AND current_hour BETWEEN 9 AND 18 THEN
        ALTER SYSTEM SET effective_io_concurrency = 300;
        ALTER SYSTEM SET max_parallel_workers_per_gather = 2;
        ALTER SYSTEM SET work_mem = '64MB';
        RAISE NOTICE '已切换到OLTP优化配置';

    -- 夜间和周末：OLAP优化
    ELSE
        ALTER SYSTEM SET effective_io_concurrency = 500;
        ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
        ALTER SYSTEM SET work_mem = '256MB';
        RAISE NOTICE '已切换到OLAP优化配置';
    END IF;

    PERFORM pg_reload_conf();
END;
$$ LANGUAGE plpgsql;

-- 每小时执行一次
SELECT cron.schedule('time-based-optimization', '0 * * * *',
    'SELECT time_based_optimization();');
```

---

---

**返回**: [文档首页](../README.md) | [上一章节](../27-性能模型理论/README.md) | [下一章节](../29-版本兼容性/README.md)
