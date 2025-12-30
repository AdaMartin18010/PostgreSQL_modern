# 12. 性能调优检查清单

> **章节编号**: 12
> **章节标题**: 性能调优检查清单
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 12. 性能调优检查清单

## 📑 目录

- [12. 性能调优检查清单](#12-性能调优检查清单)
  - [12. 性能调优检查清单](#12-性能调优检查清单-1)
  - [📑 目录](#-目录)
    - [12.1 配置检查清单](#121-配置检查清单)
    - [12.2 性能调优检查清单表](#122-性能调优检查清单表)
    - [12.3 性能调优步骤](#123-性能调优步骤)
    - [12.4 性能问题诊断](#124-性能问题诊断)
    - [12.5 性能优化建议](#125-性能优化建议)
    - [12.6 性能监控仪表板](#126-性能监控仪表板)

---

### 12.1 配置检查清单

**基础配置检查**:

- [ ] PostgreSQL版本为18或更高
- [ ] Linux内核版本5.1+（支持io_uring）
- [ ] io_direct参数已启用
- [ ] effective_io_concurrency已配置
- [ ] wal_io_concurrency已配置
- [ ] io_uring_queue_depth已配置

**系统配置检查**:

- [ ] 文件描述符限制足够（推荐65536+）
- [ ] 内存配置合理（shared_buffers等）
- [ ] 存储设备性能良好（NVMe SSD推荐）
- [ ] CPU核心数充足

**验证脚本**:

```sql
-- 配置检查脚本
SELECT
    name,
    setting,
    unit,
    CASE
        WHEN name = 'io_direct' AND setting != 'off' THEN '✅'
        WHEN name = 'effective_io_concurrency' AND setting::int >= 200 THEN '✅'
        WHEN name = 'wal_io_concurrency' AND setting::int >= 200 THEN '✅'
        ELSE '❌'
    END AS status
FROM pg_settings
WHERE name IN (
    'io_direct',
    'effective_io_concurrency',
    'wal_io_concurrency',
    'io_uring_queue_depth'
);
```

### 12.2 性能调优检查清单表

**性能指标检查**:

| 指标 | 目标值 | 检查方法 |
|------|--------|---------|
| **I/O等待时间** | <10% | `SELECT * FROM pg_stat_io` |
| **CPU利用率** | 60-80% | 系统监控工具 |
| **查询P99延迟** | <100ms | `pg_stat_statements` |
| **连接数使用率** | <80% | `SELECT count(*) FROM pg_stat_activity` |
| **缓存命中率** | >95% | `pg_stat_database` |

**性能调优检查项**:

- [ ] I/O性能监控正常
- [ ] CPU利用率在合理范围
- [ ] 查询性能达到预期
- [ ] 连接池配置合理
- [ ] 索引使用率良好
- [ ] 锁竞争在可接受范围

### 12.3 性能调优步骤

**步骤1: 基线测试**:

```sql
-- 记录当前性能基线
CREATE TABLE performance_baseline AS
SELECT
    NOW() AS test_time,
    (SELECT setting FROM pg_settings WHERE name = 'effective_io_concurrency) AS io_concurrency,
    (SELECT count(*) FROM pg_stat_activity) AS active_connections,
    (SELECT sum(blks_read) FROM pg_stat_database) AS total_reads;
```

**步骤2: 逐步调优**:

1. **调整I/O并发数**: 从200开始，逐步增加到300-500
2. **监控性能变化**: 观察性能指标变化
3. **优化内存配置**: 调整shared_buffers等参数
4. **优化查询**: 分析慢查询并优化

**步骤3: 验证优化效果**:

```sql
-- 对比优化前后性能
SELECT
    test_time,
    io_concurrency,
    active_connections,
    total_reads,
    total_reads - LAG(total_reads) OVER (ORDER BY test_time) AS reads_increase
FROM performance_baseline
ORDER BY test_time DESC;
```

**调优最佳实践**:

- **渐进式调优**: 每次只调整一个参数
- **持续监控**: 调优后持续监控一段时间
- **记录变更**: 记录所有配置变更和性能变化
- **回滚准备**: 准备回滚方案以防性能下降

### 12.4 性能问题诊断

**常见性能问题**：

| 问题 | 症状 | 可能原因 | 解决方案 |
|------|------|---------|---------|
| **I/O等待高** | I/O等待时间>20% | io_uring配置不当 | 增加io_uring_queue_depth |
| **CPU利用率低** | CPU利用率<30% | I/O并发数不足 | 增加effective_io_concurrency |
| **查询延迟高** | P99延迟>200ms | 索引缺失或配置不当 | 优化查询和索引 |
| **连接数不足** | 连接数使用率>90% | max_connections设置过小 | 增加max_connections或使用连接池 |

**诊断脚本**：

```sql
-- 综合性能诊断
WITH performance_check AS (
    SELECT
        'I/O等待时间' AS metric,
        CASE
            WHEN (
                SELECT SUM(io_wait_time)
                FROM pg_stat_io
                WHERE context = 'async'
            ) / NULLIF(
                SELECT SUM(io_wait_time + io_read_time + io_write_time)
                FROM pg_stat_io
                WHERE context = 'async'
            , 1) * 100 > 20 THEN '❌ 过高'
            ELSE '✅ 正常'
        END AS status
    UNION ALL
    SELECT
        'I/O并发数' AS metric,
        CASE
            WHEN (SELECT setting::int FROM pg_settings WHERE name = 'effective_io_concurrency') < 200 THEN '⚠️ 偏低'
            WHEN (SELECT setting::int FROM pg_settings WHERE name = 'effective_io_concurrency') > 500 THEN '⚠️ 偏高'
            ELSE '✅ 正常'
        END AS status
    UNION ALL
    SELECT
        '连接数使用率' AS metric,
        CASE
            WHEN (
                SELECT COUNT(*) FROM pg_stat_activity
            )::float / NULLIF(
                (SELECT setting::int FROM pg_settings WHERE name = 'max_connections')
            , 1) * 100 > 80 THEN '❌ 过高'
            ELSE '✅ 正常'
        END AS status
)
SELECT * FROM performance_check;
```

### 12.5 性能优化建议

**优化优先级**：

1. **P0 - 关键优化**（立即执行）
   - [ ] 启用异步I/O（io_direct）
   - [ ] 配置合理的I/O并发数
   - [ ] 优化慢查询

2. **P1 - 重要优化**（近期执行）
   - [ ] 调整内存配置
   - [ ] 优化索引策略
   - [ ] 配置连接池

3. **P2 - 可选优化**（长期规划）
   - [ ] 升级硬件
   - [ ] 优化应用层代码
   - [ ] 实施读写分离

**优化效果评估**：

```sql
-- 创建性能优化记录表
CREATE TABLE IF NOT EXISTS performance_optimization_log (
    id SERIAL PRIMARY KEY,
    optimization_date TIMESTAMPTZ DEFAULT NOW(),
    optimization_type TEXT,
    before_value TEXT,
    after_value TEXT,
    performance_improvement NUMERIC,
    notes TEXT
);

-- 记录优化效果
INSERT INTO performance_optimization_log
(optimization_type, before_value, after_value, performance_improvement, notes)
VALUES
('io_concurrency', '100', '300', 50.0, 'I/O并发数从100增加到300，性能提升50%');

-- 查询优化历史
SELECT
    optimization_date,
    optimization_type,
    before_value,
    after_value,
    performance_improvement || '%' AS improvement,
    notes
FROM performance_optimization_log
ORDER BY optimization_date DESC;
```

### 12.6 性能监控仪表板

**监控指标查询**：

```sql
-- 创建性能监控视图
CREATE OR REPLACE VIEW performance_dashboard AS
SELECT
    'I/O性能' AS category,
    jsonb_build_object(
        'io_wait_pct', ROUND(
            (SELECT SUM(io_wait_time) FROM pg_stat_io WHERE context = 'async')::numeric /
            NULLIF((SELECT SUM(io_wait_time + io_read_time + io_write_time)
                    FROM pg_stat_io WHERE context = 'async'), 0) * 100, 2
        ),
        'io_reads', (SELECT SUM(reads) FROM pg_stat_io WHERE context = 'async'),
        'io_writes', (SELECT SUM(writes) FROM pg_stat_io WHERE context = 'async')
    ) AS metrics
UNION ALL
SELECT
    '查询性能' AS category,
    jsonb_build_object(
        'avg_query_time', (
            SELECT ROUND(AVG(mean_exec_time), 2)
            FROM pg_stat_statements
            WHERE calls > 100
        ),
        'slow_queries', (
            SELECT COUNT(*)
            FROM pg_stat_statements
            WHERE mean_exec_time > 1000
        )
    ) AS metrics
UNION ALL
SELECT
    '连接状态' AS category,
    jsonb_build_object(
        'active_connections', (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active'),
        'idle_connections', (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'idle'),
        'max_connections', (SELECT setting FROM pg_settings WHERE name = 'max_connections')
    ) AS metrics;

-- 查询监控仪表板
SELECT * FROM performance_dashboard;
```

**返回**: [文档首页](../README.md) | [上一章节](../11-迁移指南/README.md) | [下一章节](../13-与其他特性集成/README.md)
