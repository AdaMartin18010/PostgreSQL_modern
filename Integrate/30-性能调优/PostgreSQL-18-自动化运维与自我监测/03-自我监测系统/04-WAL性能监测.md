# 3.4 WAL性能监测

> **所属主题**: 03-自我监测系统
> **章节编号**: 3.4
> **PostgreSQL版本**: 18+
> **难度等级**: ⭐⭐⭐
> **相关章节**: [3.3 连接性能监测](./03-连接性能监测.md) | [4.1 自动慢查询检测](../04-自动化诊断/01-自动慢查询检测.md)

---

## 📋 目录

- [3.4 WAL性能监测](#34-wal性能监测)
  - [3.4.1 概述与背景](#341-概述与背景)
  - [3.4.2 WAL性能监测原理](#342-wal性能监测原理)
  - [3.4.3 监测决策树](#343-监测决策树)
  - [3.4.4 WAL性能监测系统](#344-wal性能监测系统)
  - [3.4.5 pg_stat_checkpointer视图说明](#345-pg_stat_checkpointer视图说明)
  - [3.4.6 WAL性能分析](#346-wal性能分析)
  - [3.4.7 WAL性能问题诊断](#347-wal性能问题诊断)
  - [3.4.8 性能优势与论证](#348-性能优势与论证)
  - [3.4.9 注意事项与最佳实践](#349-注意事项与最佳实践)
  - [3.4.10 导航](#3410-导航)

---

## 3.4.1 概述与背景

### 3.4.1.1 什么是WAL性能监测

PostgreSQL 18提供了更详细的WAL统计信息，包括pg_stat_checkpointer的新增列。新的WAL监测功能可以更好地分析写入性能和检查点配置。

### 3.4.1.2 问题背景

**WAL性能监控的挑战**：

- ❌ 无法了解检查点完成情况
- ❌ 难以分析写入性能
- ❌ 无法优化检查点配置

**PostgreSQL 18的解决方案**：

- ✅ 新增num_done列：完成的检查点数量
- ✅ 更详细的WAL统计信息
- ✅ 便于优化写入性能和检查点配置

### 3.4.1.3 PostgreSQL 18特性

1. **num_done列**：新增完成的检查点数量统计
2. **详细统计**：更详细的WAL统计信息
3. **性能分析**：便于优化写入性能和检查点配置

---

## 3.4.2 WAL性能监测原理

### 3.4.2.1 监测流程

```
┌─────────────────────────────────────────────────────────┐
│          PostgreSQL 18 WAL性能监测流程                    │
└─────────────────────────────────────────────────────────┘

WAL写入操作
    │
    ├─→ 记录WAL统计
    │   ├─→ WAL位置（LSN）
    │   ├─→ WAL大小
    │   └─→ WAL缓冲区使用
    │
检查点操作
    │
    ├─→ 记录检查点统计
    │   ├─→ 检查点类型（定时/请求）
    │   ├─→ 检查点耗时
    │   ├─→ 检查点缓冲区
    │   └─→ 完成的检查点数量（PostgreSQL 18新增）
    │
统计信息更新
    │
    └─→ 更新pg_stat_checkpointer视图
        └─→ 提供统计信息查询
```

---

## 3.4.3 监测决策树

### 3.4.3.1 WAL监测启用决策树

```
开始：是否需要WAL监测？
│
├─→ 是否有写入性能问题？
│   ├─→ [是] ✅ 需要WAL监测
│   │   └─→ 理由：需要分析写入性能
│   │
│   └─→ [否] 继续
│
├─→ 是否需要优化检查点配置？
│   ├─→ [是] ✅ 需要WAL监测
│   │   └─→ 理由：需要分析检查点性能
│   │
│   └─→ [否] ⚠️  可选监测
│
└─→ 最终决策
    └─→ 根据需求决定是否启用WAL监测
```

### 3.4.3.2 监测决策论证

**论证：为什么需要WAL性能监测？**

```
前提条件：
P1: WAL性能影响写入性能
P2: 检查点配置影响系统性能
P3: WAL监测可以分析写入和检查点性能

推理过程：
R1: 如果P1，则需要监控WAL性能
R2: 如果P2，则需要优化检查点配置
R3: 如果P3，则可以分析和优化性能

结论：
C1: 应该启用WAL性能监测
C2: 可以分析写入性能，优化检查点配置
C3: 可以提升系统整体性能
```

---

## 3.4.4 WAL性能监测系统

### 3.4.4.1 WAL统计查询

```sql
-- PostgreSQL 18 WAL性能监测（带错误处理和性能测试）
DO $$
DECLARE
    wal_stats RECORD;
    checkpoint_stats RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'WAL性能监测增强需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== PostgreSQL 18 WAL性能监测 ===';
        RAISE NOTICE 'WAL性能统计:';
        RAISE NOTICE '';

        -- 查询WAL统计
        SELECT
            pg_current_wal_lsn() AS current_wal_lsn,
            pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS total_wal_bytes,
            ROUND(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')::numeric / 1024 / 1024, 2) AS total_wal_mb,
            (SELECT setting FROM pg_settings WHERE name = 'wal_buffers') AS wal_buffers,
            (SELECT setting FROM pg_settings WHERE name = 'max_wal_size') AS max_wal_size,
            (SELECT setting FROM pg_settings WHERE name = 'min_wal_size') AS min_wal_size
        INTO wal_stats
        FROM pg_stat_database
        WHERE datname = current_database();

        RAISE NOTICE '当前WAL位置: %', wal_stats.current_wal_lsn;
        RAISE NOTICE '总WAL大小: %.2f MB', wal_stats.total_wal_mb;
        RAISE NOTICE 'WAL缓冲区: %', wal_stats.wal_buffers;
        RAISE NOTICE '最小WAL大小: %', wal_stats.min_wal_size;
        RAISE NOTICE '最大WAL大小: %', wal_stats.max_wal_size;
        RAISE NOTICE '';

        -- 查询检查点统计（PostgreSQL 18新增num_done列）
        SELECT
            checkpoints_timed,
            checkpoints_req,
            checkpoint_write_time,
            checkpoint_sync_time,
            buffers_checkpoint,
            buffers_clean,
            max_write_time,
            max_sync_time,
            num_done  -- PostgreSQL 18新增：完成的检查点数量
        INTO checkpoint_stats
        FROM pg_stat_checkpointer;

        RAISE NOTICE '=== 检查点统计（PostgreSQL 18增强） ===';
        RAISE NOTICE '定时检查点: %', checkpoint_stats.checkpoints_timed;
        RAISE NOTICE '请求检查点: %', checkpoint_stats.checkpoints_req;
        RAISE NOTICE '完成的检查点: %', checkpoint_stats.num_done;  -- PostgreSQL 18新增
        RAISE NOTICE '检查点写入时间: %.2f ms', checkpoint_stats.checkpoint_write_time;
        RAISE NOTICE '检查点同步时间: %.2f ms', checkpoint_stats.checkpoint_sync_time;
        RAISE NOTICE '检查点缓冲区: %', checkpoint_stats.buffers_checkpoint;
        RAISE NOTICE '清理缓冲区: %', checkpoint_stats.buffers_clean;
        RAISE NOTICE '最大写入时间: %.2f ms', checkpoint_stats.max_write_time;
        RAISE NOTICE '最大同步时间: %.2f ms', checkpoint_stats.max_sync_time;
        RAISE NOTICE '';

        -- PostgreSQL 18增强：更详细的WAL统计
        RAISE NOTICE 'PostgreSQL 18增强特性:';
        RAISE NOTICE '- pg_stat_checkpointer新增num_done列：完成的检查点数量';
        RAISE NOTICE '- WAL缓冲区生成的日志数量统计';
        RAISE NOTICE '- WAL缓冲区数据量统计';
        RAISE NOTICE '- 缓冲区被写满的次数统计';
        RAISE NOTICE '- 便于优化写入性能和检查点配置';

        -- 检查WAL性能问题
        IF wal_stats.total_wal_mb > (wal_stats.max_wal_size::numeric / 1024) * 0.8 THEN
            RAISE WARNING 'WAL使用率超过80%%，建议检查写入负载或增加max_wal_size';
        END IF;

        IF checkpoint_stats.checkpoint_write_time > 1000 THEN
            RAISE WARNING '检查点写入时间过长（%.2f ms），建议优化I/O性能或调整检查点参数',
                checkpoint_stats.checkpoint_write_time;
        END IF;

        IF checkpoint_stats.checkpoint_sync_time > 1000 THEN
            RAISE WARNING '检查点同步时间过长（%.2f ms），建议优化存储性能',
                checkpoint_stats.checkpoint_sync_time;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'WAL性能监测失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 3.4.5 pg_stat_checkpointer视图说明

### 3.4.5.1 视图列说明

| 列名 | 类型 | 说明 | PostgreSQL版本 |
|------|------|------|----------------|
| `checkpoints_timed` | bigint | 定时检查点数量 | 17+ |
| `checkpoints_req` | bigint | 请求检查点数量 | 17+ |
| `checkpoint_write_time` | double precision | 检查点写入时间（毫秒） | 17+ |
| `checkpoint_sync_time` | double precision | 检查点同步时间（毫秒） | 17+ |
| `buffers_checkpoint` | bigint | 检查点缓冲区数量 | 17+ |
| `buffers_clean` | bigint | 清理缓冲区数量 | 17+ |
| `max_write_time` | double precision | 最大写入时间（毫秒） | 17+ |
| `max_sync_time` | double precision | 最大同步时间（毫秒） | 17+ |
| `num_done` | bigint | 完成的检查点数量 | **18新增** |

---

## 3.4.6 WAL性能分析

### 3.4.6.1 查询检查点统计

```sql
-- 查询检查点统计（带错误处理和性能测试）
DO $$
DECLARE
    checkpoint_record RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_checkpointer视图的num_done列需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== 检查点统计查询（PostgreSQL 18增强） ===';
        RAISE NOTICE '';

        -- 查询检查点统计
        SELECT
            checkpoints_timed,
            checkpoints_req,
            num_done,  -- PostgreSQL 18新增
            checkpoint_write_time,
            checkpoint_sync_time,
            buffers_checkpoint,
            buffers_clean,
            max_write_time,
            max_sync_time
        INTO checkpoint_record
        FROM pg_stat_checkpointer;

        RAISE NOTICE '定时检查点: %', checkpoint_record.checkpoints_timed;
        RAISE NOTICE '请求检查点: %', checkpoint_record.checkpoints_req;
        RAISE NOTICE '完成的检查点: %', checkpoint_record.num_done;  -- PostgreSQL 18新增
        RAISE NOTICE '检查点写入时间: %.2f ms', checkpoint_record.checkpoint_write_time;
        RAISE NOTICE '检查点同步时间: %.2f ms', checkpoint_record.checkpoint_sync_time;
        RAISE NOTICE '检查点缓冲区: %', checkpoint_record.buffers_checkpoint;
        RAISE NOTICE '清理缓冲区: %', checkpoint_record.buffers_clean;
        RAISE NOTICE '最大写入时间: %.2f ms', checkpoint_record.max_write_time;
        RAISE NOTICE '最大同步时间: %.2f ms', checkpoint_record.max_sync_time;
        RAISE NOTICE '';

        -- 性能测试：查询执行计划
        RAISE NOTICE '=== 性能测试：查询执行计划 ===';
        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                checkpoints_timed,
                checkpoints_req,
                num_done,
                checkpoint_write_time,
                checkpoint_sync_time,
                buffers_checkpoint,
                buffers_clean,
                max_write_time,
                max_sync_time
            FROM pg_stat_checkpointer
        ) AS explain_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查点统计查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.4.6.2 查询WAL使用情况

```sql
-- 查询WAL使用情况（带错误处理和性能测试）
DO $$
DECLARE
    wal_usage RECORD;
    current_lsn pg_lsn;
    total_wal_bytes bigint;
    total_wal_mb numeric;
    max_wal_size numeric;
    wal_usage_percent numeric;
BEGIN
    BEGIN
        RAISE NOTICE '=== WAL使用情况查询 ===';
        RAISE NOTICE '';

        -- 获取当前WAL LSN
        current_lsn := pg_current_wal_lsn();

        -- 计算总WAL字节数
        total_wal_bytes := pg_wal_lsn_diff(current_lsn, '0/0');
        total_wal_mb := ROUND(total_wal_bytes::numeric / 1024 / 1024, 2);

        -- 获取max_wal_size配置
        SELECT setting::numeric INTO max_wal_size
        FROM pg_settings
        WHERE name = 'max_wal_size';

        -- 计算WAL使用率
        wal_usage_percent := ROUND(100.0 * total_wal_bytes::numeric /
            NULLIF(max_wal_size * 1024 * 1024, 0), 2);

        RAISE NOTICE '当前WAL位置: %', current_lsn;
        RAISE NOTICE '总WAL大小: %.2f MB', total_wal_mb;
        RAISE NOTICE '最大WAL大小: %.2f MB', ROUND(max_wal_size::numeric / 1024, 2);
        RAISE NOTICE 'WAL使用率: %%', wal_usage_percent;
        RAISE NOTICE '';

        -- 检查WAL使用率警告
        IF wal_usage_percent > 80 THEN
            RAISE WARNING 'WAL使用率超过80%%，建议检查写入负载或增加max_wal_size';
        END IF;

        -- 性能测试：查询执行计划
        RAISE NOTICE '=== 性能测试：查询执行计划 ===';
        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                pg_current_wal_lsn() AS current_wal_lsn,
                pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS total_wal_bytes,
                ROUND(pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0')::numeric / 1024 / 1024, 2) AS total_wal_mb
        ) AS explain_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'WAL使用情况查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.4.6.3 分析检查点性能

```sql
-- 分析检查点性能（带错误处理和性能测试）
DO $$
DECLARE
    checkpoint_perf RECORD;
    total_checkpoints bigint;
    completion_rate numeric;
    avg_write_time_ms numeric;
    avg_sync_time_ms numeric;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_checkpointer视图的num_done列需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== 检查点性能分析（PostgreSQL 18增强） ===';
        RAISE NOTICE '';

        -- 分析检查点性能
        SELECT
            checkpoints_timed + checkpoints_req AS total_checkpoints,
            num_done AS completed_checkpoints,  -- PostgreSQL 18新增
            ROUND(100.0 * num_done / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS completion_rate,
            ROUND(checkpoint_write_time / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS avg_write_time_ms,
            ROUND(checkpoint_sync_time / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS avg_sync_time_ms
        INTO checkpoint_perf
        FROM pg_stat_checkpointer;

        total_checkpoints := checkpoint_perf.total_checkpoints;
        completion_rate := checkpoint_perf.completion_rate;
        avg_write_time_ms := checkpoint_perf.avg_write_time_ms;
        avg_sync_time_ms := checkpoint_perf.avg_sync_time_ms;

        RAISE NOTICE '总检查点数: %', total_checkpoints;
        RAISE NOTICE '完成的检查点: %', checkpoint_perf.completed_checkpoints;
        RAISE NOTICE '完成率: %%', completion_rate;
        RAISE NOTICE '平均写入时间: %.2f ms', avg_write_time_ms;
        RAISE NOTICE '平均同步时间: %.2f ms', avg_sync_time_ms;
        RAISE NOTICE '';

        -- 性能问题检查
        IF avg_write_time_ms > 1000 THEN
            RAISE WARNING '平均写入时间过长（%.2f ms），建议优化I/O性能', avg_write_time_ms;
        END IF;

        IF avg_sync_time_ms > 1000 THEN
            RAISE WARNING '平均同步时间过长（%.2f ms），建议优化存储性能', avg_sync_time_ms;
        END IF;

        IF completion_rate < 95 AND total_checkpoints > 0 THEN
            RAISE WARNING '检查点完成率较低（%%），建议检查检查点配置', completion_rate;
        END IF;

        -- 性能测试：查询执行计划
        RAISE NOTICE '=== 性能测试：查询执行计划 ===';
        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                checkpoints_timed + checkpoints_req AS total_checkpoints,
                num_done AS completed_checkpoints,
                ROUND(100.0 * num_done / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS completion_rate,
                ROUND(checkpoint_write_time / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS avg_write_time_ms,
                ROUND(checkpoint_sync_time / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) AS avg_sync_time_ms
            FROM pg_stat_checkpointer
        ) AS explain_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '检查点性能分析失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 3.4.7 WAL性能问题诊断

### 3.4.7.1 问题诊断表

| 问题 | 症状 | 解决方案 |
|------|------|---------|
| **WAL使用率过高** | WAL使用率 > 80% | 检查写入负载，增加max_wal_size，优化检查点频率 |
| **检查点写入时间过长** | 写入时间 > 1000ms | 优化I/O性能，调整检查点参数，检查存储性能 |
| **检查点同步时间过长** | 同步时间 > 1000ms | 优化存储性能，检查磁盘I/O，考虑更快存储 |

### 3.4.7.2 问题诊断决策树

```
开始：诊断WAL性能问题
│
├─→ WAL使用率 > 80%？
│   ├─→ [是] ⚠️  WAL使用率过高
│   │   └─→ 解决方案：增加max_wal_size，优化检查点频率
│   │
│   └─→ [否] 继续
│
├─→ 检查点写入时间 > 1000ms？
│   ├─→ [是] ⚠️  写入时间过长
│   │   └─→ 解决方案：优化I/O性能，调整检查点参数
│   │
│   └─→ [否] 继续
│
└─→ 检查点同步时间 > 1000ms？
    ├─→ [是] ⚠️  同步时间过长
    │   └─→ 解决方案：优化存储性能，检查磁盘I/O
    └─→ [否] ✅ WAL性能正常
```

---

## 3.4.8 性能优势与论证

### 3.4.8.1 PostgreSQL 18增强特性

| 特性 | 说明 | 价值 |
|------|------|------|
| **num_done列** | 新增完成的检查点数量统计 | 了解检查点完成情况 |
| **详细统计** | 更详细的WAL统计信息 | 深入分析WAL性能 |
| **性能分析** | 便于优化写入性能和检查点配置 | 优化系统性能 |

### 3.4.8.2 性能优势论证

**论证：WAL监测的价值**

```
前提条件：
P1: WAL性能影响写入性能
P2: 检查点配置影响系统性能
P3: WAL监测可以分析写入和检查点性能

推理过程：
R1: 如果P1，则需要监控WAL性能
R2: 如果P2，则需要优化检查点配置
R3: 如果P3，则可以分析和优化性能

结论：
C1: WAL监测可以分析写入性能
C2: 可以优化检查点配置，提升系统性能
C3: 可以快速定位问题，减少诊断时间
```

---

## 3.4.9 注意事项与最佳实践

### 3.4.9.1 注意事项

⚠️ **重要提醒**：

1. **版本要求**：需要PostgreSQL 18+

   ```sql
   SELECT current_setting('server_version_num')::int >= 180000;
   ```

2. **性能影响**：WAL监测本身性能开销很小（< 0.1%）

3. **配置优化**：根据监测结果调整WAL和检查点配置

### 3.4.9.2 最佳实践

✅ **推荐做法**：

1. **定期监控**：设置定时任务，定期查询WAL统计

   ```sql
   -- 每小时查询一次WAL统计
   ```

2. **趋势分析**：记录历史数据，分析WAL趋势

3. **告警设置**：设置WAL使用率和检查点耗时告警阈值

### 3.4.9.3 故障排查

🔧 **常见问题**：

1. **WAL使用率过高**
   - 检查写入负载
   - 增加max_wal_size配置
   - 优化检查点频率

2. **检查点耗时过长**
   - 检查I/O性能
   - 调整检查点参数
   - 检查存储性能

---

## 3.4.10 导航

### 3.4.10.1 章节导航

- **上一节**：[3.3 连接性能监测](./03-连接性能监测.md)
- **返回主题目录**：[03-自我监测系统](./README.md)
- **返回主文档**：[PostgreSQL-18-自动化运维与自我监测](../README.md)

### 3.4.10.2 相关章节

- [3.3 连接性能监测](./03-连接性能监测.md) - 连接监测
- [6.2 Autovacuum配置](../06-综合方案/02-Autovacuum配置.md) - 检查点配置
- [4.3 自动资源瓶颈检测](../04-自动化诊断/03-自动资源瓶颈检测.md) - I/O瓶颈检测

---

## 📚 参考资料

- [PostgreSQL 18 WAL文档](https://www.postgresql.org/docs/18/wal.html)
- [PostgreSQL 18 检查点文档](https://www.postgresql.org/docs/18/runtime-config-wal.html#RUNTIME-CONFIG-WAL-CHECKPOINTS)
- [PostgreSQL 18 pg_stat_checkpointer文档](https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-CHECKPOINTER-VIEW)

---

**最后更新**: 2025年1月
**文档版本**: v2.0（已添加决策树、推理论证、完整目录）
