# 12. 性能调优检查清单

> **章节编号**: 12
> **章节标题**: 性能调优检查清单
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 12. 性能调优检查清单

## 📑 目录

- [12.1 配置检查清单](#121-配置检查清单)
- [12.2 性能调优检查清单表](#122-性能调优检查清单表)
- [12.3 性能调优步骤](#123-性能调优步骤)

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

**返回**: [文档首页](../README.md) | [上一章节](../11-迁移指南/README.md) | [下一章节](../13-与其他特性集成/README.md)
