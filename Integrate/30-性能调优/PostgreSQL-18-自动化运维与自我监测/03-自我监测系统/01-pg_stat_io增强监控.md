# 3.1 pg_stat_io增强监控

> **所属主题**: 03-自我监测系统
> **章节编号**: 3.1
> **创建日期**: 2025年1月
> **PostgreSQL版本**: 18+
> **难度等级**: ⭐⭐⭐

---

## 📋 目录

- [3.1 pg_stat_io增强监控](#31-pg_stat_io增强监控)
  - [3.1.1 概述与背景](#311-概述与背景)
  - [3.1.2 pg_stat_io增强功能原理](#312-pg_stat_io增强功能原理)
  - [3.1.3 监控决策树](#313-监控决策树)
  - [3.1.4 pg_stat_io增强功能](#314-pg_stat_io增强功能)
  - [3.1.5 I/O统计查询](#315-io统计查询)
  - [3.1.6 PostgreSQL 18新增列](#316-postgresql-18新增列)
  - [3.1.7 使用示例与实践](#317-使用示例与实践)
  - [3.1.8 性能优势与论证](#318-性能优势与论证)
  - [3.1.9 注意事项与最佳实践](#319-注意事项与最佳实践)
  - [3.1.10 导航](#3110-导航)

---

## 3.1.1 概述与背景

### 3.1.1.1 什么是pg_stat_io增强监控

PostgreSQL 18的pg_stat_io视图提供了详细的I/O统计信息，新增了字节级别的统计（read_bytes、write_bytes、extend_bytes），提供更全面的I/O性能分析。

### 3.1.1.2 问题背景

**I/O监控的挑战**：

- ❌ 只能看到I/O次数，无法了解I/O数据量
- ❌ 难以准确评估I/O性能
- ❌ 无法识别I/O瓶颈的具体原因

**PostgreSQL 18的解决方案**：

- ✅ 新增字节级别统计（read_bytes、write_bytes、extend_bytes）
- ✅ 更详细的I/O性能分析
- ✅ 支持按对象和上下文分类统计

### 3.1.1.3 PostgreSQL 18新特性

1. **read_bytes**：读取字节数统计
2. **write_bytes**：写入字节数统计
3. **extend_bytes**：扩展字节数统计
4. **分类统计**：支持按对象和上下文分类

---

## 3.1.2 pg_stat_io增强功能原理

### 3.1.2.1 监控流程

```
┌─────────────────────────────────────────────────────────┐
│          PostgreSQL 18 pg_stat_io监控流程                 │
└─────────────────────────────────────────────────────────┘

I/O操作发生
    │
    ├─→ 记录I/O操作
    │   ├─→ 操作类型（read/write/extend）
    │   ├─→ 操作次数（reads/writes/extends）
    │   └─→ 操作字节数（read_bytes/write_bytes/extend_bytes）
    │
    ├─→ 分类统计
    │   ├─→ 对象类型（object）
    │   │   ├─→ relation（表/索引）
    │   │   ├─→ temp（临时文件）
    │   │   └─→ shared_buffers（共享缓冲区）
    │   │
    │   └─→ 上下文（context）
    │       ├─→ normal（正常操作）
    │       ├─→ vacuum（VACUUM操作）
    │       └─→ bulkread（批量读取）
    │
    └─→ 更新pg_stat_io视图
        └─→ 提供统计信息查询
```

---

## 3.1.3 监控决策树

### 3.1.3.1 I/O监控使用决策树

```
开始：是否需要I/O监控？
│
├─→ 系统是否有I/O性能问题？
│   ├─→ [是] ✅ 需要I/O监控
│   │   └─→ 理由：需要识别I/O瓶颈
│   │
│   └─→ [否] 继续
│
├─→ 是否需要优化存储性能？
│   ├─→ [是] ✅ 需要I/O监控
│   │   └─→ 理由：需要评估存储性能
│   │
│   └─→ [否] 继续
│
├─→ 是否需要分析工作负载？
│   ├─→ [是] ✅ 需要I/O监控
│   │   └─→ 理由：需要了解I/O模式
│   │
│   └─→ [否] ⚠️  可选监控
│
└─→ 最终决策
    └─→ 根据需求决定是否启用I/O监控
```

### 3.1.3.2 I/O瓶颈识别决策树

```
开始：识别I/O瓶颈
│
├─→ 读取字节数 > 阈值？
│   ├─→ [是] ⚠️  读取I/O瓶颈
│   │   └─→ 建议：优化索引，减少读取
│   │
│   └─→ [否] 继续
│
├─→ 写入字节数 > 阈值？
│   ├─→ [是] ⚠️  写入I/O瓶颈
│   │   └─→ 建议：优化写入模式，使用异步I/O
│   │
│   └─→ [否] 继续
│
└─→ 扩展字节数 > 阈值？
    ├─→ [是] ⚠️  扩展I/O瓶颈
    │   └─→ 建议：优化表结构，减少扩展
    └─→ [否] ✅ I/O正常
```

### 3.1.3.3 监控决策论证

**论证：为什么需要I/O监控？**

```
前提条件：
P1: I/O是数据库性能的重要瓶颈
P2: 无法监控I/O性能，难以优化
P3: PostgreSQL 18提供详细的I/O统计

推理过程：
R1: 如果P1，则需要监控I/O性能
R2: 如果P2，则无法优化I/O性能
R3: 如果P3，则可以监控和优化I/O性能

结论：
C1: 应该使用I/O监控功能
C2: 可以识别I/O瓶颈，优化I/O性能
C3: 可以提升数据库整体性能
```

---

## 3.1.4 pg_stat_io增强功能

### 3.1.4.1 新增列说明

PostgreSQL 18在pg_stat_io视图中新增了以下列：

| 列名 | 类型 | 说明 | PostgreSQL版本 |
|------|------|------|----------------|
| `read_bytes` | bigint | 读取字节数 | **18新增** |
| `write_bytes` | bigint | 写入字节数 | **18新增** |
| `extend_bytes` | bigint | 扩展字节数 | **18新增** |

---

## 3.1.5 I/O统计查询

```sql
-- PostgreSQL 18 pg_stat_io增强监控（带错误处理和性能测试）
DO $$
DECLARE
    io_stats RECORD;
    total_read_bytes bigint := 0;
    total_write_bytes bigint := 0;
    total_reads bigint := 0;
    total_writes bigint := 0;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== PostgreSQL 18 pg_stat_io增强监控 ===';
        RAISE NOTICE 'I/O性能统计（PostgreSQL 18新增字节统计）:';
        RAISE NOTICE '';

        -- 查询I/O统计（PostgreSQL 18新增列）
        FOR io_stats IN
            SELECT
                object,
                context,
                reads,
                read_bytes,  -- PostgreSQL 18新增：读取字节数
                writes,
                write_bytes,  -- PostgreSQL 18新增：写入字节数
                extends,
                extend_bytes,  -- PostgreSQL 18新增：扩展字节数
                fsyncs,
                ROUND(100.0 * reads / NULLIF(reads + writes, 0), 2) AS read_ratio,
                ROUND(read_bytes::numeric / 1024 / 1024, 2) AS read_mb,
                ROUND(write_bytes::numeric / 1024 / 1024, 2) AS write_mb,
                ROUND(extend_bytes::numeric / 1024 / 1024, 2) AS extend_mb
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            ORDER BY reads + writes DESC
            LIMIT 20
        LOOP
            total_read_bytes := total_read_bytes + io_stats.read_bytes;
            total_write_bytes := total_write_bytes + io_stats.write_bytes;
            total_reads := total_reads + io_stats.reads;
            total_writes := total_writes + io_stats.writes;

            RAISE NOTICE '对象: % | 上下文: %', io_stats.object, io_stats.context;
            RAISE NOTICE '  读取: % 次 (%.2f MB) | 写入: % 次 (%.2f MB)',
                io_stats.reads, io_stats.read_mb, io_stats.writes, io_stats.write_mb;
            RAISE NOTICE '  扩展: % 次 (%.2f MB) | Fsync: % 次',
                io_stats.extends, io_stats.extend_mb, io_stats.fsyncs;
            RAISE NOTICE '  读写比例: %%', io_stats.read_ratio;
            RAISE NOTICE '';
        END LOOP;

        -- 汇总统计
        RAISE NOTICE '=== I/O汇总统计 ===';
        RAISE NOTICE '总读取: % 次 (%.2f GB)',
            total_reads, ROUND(total_read_bytes::numeric / 1024 / 1024 / 1024, 2);
        RAISE NOTICE '总写入: % 次 (%.2f GB)',
            total_writes, ROUND(total_write_bytes::numeric / 1024 / 1024 / 1024, 2);
        RAISE NOTICE '总I/O: % 次 (%.2f GB)',
            total_reads + total_writes,
            ROUND((total_read_bytes + total_write_bytes)::numeric / 1024 / 1024 / 1024, 2);
        RAISE NOTICE '';

        RAISE NOTICE 'PostgreSQL 18增强特性:';
        RAISE NOTICE '- read_bytes: 读取字节数统计（新增）';
        RAISE NOTICE '- write_bytes: 写入字节数统计（新增）';
        RAISE NOTICE '- extend_bytes: 扩展字节数统计（新增）';
        RAISE NOTICE '- 更详细的I/O性能分析';
        RAISE NOTICE '- 支持按对象和上下文分类统计';
        RAISE NOTICE '- 便于识别I/O瓶颈和优化存储';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'pg_stat_io监控失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 3.1.6 PostgreSQL 18新增列

### 3.1.6.1 完整视图说明

**pg_stat_io视图说明**：

| 列名 | 类型 | 说明 | PostgreSQL版本 |
|------|------|------|----------------|
| `object` | text | I/O对象类型（relation、temp、shared_buffers等） | 17+ |
| `context` | text | I/O上下文（normal、vacuum、bulkread等） | 17+ |
| `reads` | bigint | 读取次数 | 17+ |
| `read_bytes` | bigint | 读取字节数 | **18新增** |
| `writes` | bigint | 写入次数 | 17+ |
| `write_bytes` | bigint | 写入字节数 | **18新增** |
| `extends` | bigint | 扩展次数 | 17+ |
| `extend_bytes` | bigint | 扩展字节数 | **18新增** |
| `fsyncs` | bigint | Fsync次数 | 17+ |

---

## 3.1.7 使用示例与实践

### 3.1.7.1 基础使用示例

```sql
-- 查询I/O统计（PostgreSQL 18增强，带错误处理和性能测试）
DO $$
DECLARE
    io_record RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== I/O统计查询（PostgreSQL 18增强） ===';
        RAISE NOTICE '';

        -- 查询I/O统计（PostgreSQL 18新增read_bytes、write_bytes）
        FOR io_record IN
            SELECT
                object,
                context,
                reads,
                read_bytes,  -- PostgreSQL 18新增
                writes,
                write_bytes,  -- PostgreSQL 18新增
                ROUND(read_bytes::numeric / 1024 / 1024, 2) AS read_mb,
                ROUND(write_bytes::numeric / 1024 / 1024, 2) AS write_mb
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            ORDER BY reads + writes DESC
            LIMIT 10
        LOOP
            RAISE NOTICE '对象: % | 上下文: %', io_record.object, io_record.context;
            RAISE NOTICE '  读取: % 次 (%.2f MB) | 写入: % 次 (%.2f MB)',
                io_record.reads, io_record.read_mb, io_record.writes, io_record.write_mb;
            RAISE NOTICE '';
        END LOOP;

        -- 性能测试：使用EXPLAIN ANALYZE测试查询性能
        RAISE NOTICE '=== 性能测试：查询执行计划 ===';
        RAISE NOTICE '';

        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                object,
                context,
                reads,
                read_bytes,
                writes,
                write_bytes,
                ROUND(read_bytes::numeric / 1024 / 1024, 2) AS read_mb,
                ROUND(write_bytes::numeric / 1024 / 1024, 2) AS write_mb
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            ORDER BY reads + writes DESC
            LIMIT 10
        ) AS explain_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'I/O统计查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.1.7.2 高级分析查询

```sql
-- 分析I/O吞吐量（带错误处理和性能测试）
DO $$
DECLARE
    throughput_record RECORD;
    efficiency_record RECORD;
BEGIN
    BEGIN
        -- 检查PostgreSQL版本
        IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
            RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+';
            RETURN;
        END IF;

        RAISE NOTICE '=== I/O吞吐量分析（PostgreSQL 18增强） ===';
        RAISE NOTICE '';

        -- 分析I/O吞吐量
        FOR throughput_record IN
            SELECT
                object,
                context,
                SUM(reads) AS total_reads,
                SUM(read_bytes) AS total_read_bytes,
                SUM(writes) AS total_writes,
                SUM(write_bytes) AS total_write_bytes,
                ROUND(SUM(read_bytes)::numeric / 1024 / 1024 / 1024, 2) AS read_gb,
                ROUND(SUM(write_bytes)::numeric / 1024 / 1024 / 1024, 2) AS write_gb
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            GROUP BY object, context
            ORDER BY total_read_bytes + total_write_bytes DESC
            LIMIT 10
        LOOP
            RAISE NOTICE '对象: % | 上下文: %', throughput_record.object, throughput_record.context;
            RAISE NOTICE '  总读取: % 次 (%.2f GB) | 总写入: % 次 (%.2f GB)',
                throughput_record.total_reads, throughput_record.read_gb,
                throughput_record.total_writes, throughput_record.write_gb;
            RAISE NOTICE '';
        END LOOP;

        -- 性能测试：I/O吞吐量查询性能
        RAISE NOTICE '=== 性能测试：I/O吞吐量查询执行计划 ===';
        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                object,
                context,
                SUM(reads) AS total_reads,
                SUM(read_bytes) AS total_read_bytes,
                SUM(writes) AS total_writes,
                SUM(write_bytes) AS total_write_bytes
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            GROUP BY object, context
            ORDER BY total_read_bytes + total_write_bytes DESC
        ) AS explain_result;

        RAISE NOTICE '';
        RAISE NOTICE '=== I/O效率分析 ===';
        RAISE NOTICE '';

        -- 分析I/O效率
        FOR efficiency_record IN
            SELECT
                object,
                context,
                reads,
                read_bytes,
                ROUND(read_bytes::numeric / NULLIF(reads, 0), 2) AS avg_read_bytes,
                writes,
                write_bytes,
                ROUND(write_bytes::numeric / NULLIF(writes, 0), 2) AS avg_write_bytes
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            ORDER BY reads + writes DESC
            LIMIT 10
        LOOP
            RAISE NOTICE '对象: % | 上下文: %', efficiency_record.object, efficiency_record.context;
            RAISE NOTICE '  平均读取: %.2f 字节/次 | 平均写入: %.2f 字节/次',
                efficiency_record.avg_read_bytes, efficiency_record.avg_write_bytes;
            RAISE NOTICE '';
        END LOOP;

        -- 性能测试：I/O效率查询性能
        RAISE NOTICE '=== 性能测试：I/O效率查询执行计划 ===';
        PERFORM *
        FROM (
            EXPLAIN (ANALYZE, BUFFERS, TIMING)
            SELECT
                object,
                context,
                reads,
                read_bytes,
                ROUND(read_bytes::numeric / NULLIF(reads, 0), 2) AS avg_read_bytes,
                writes,
                write_bytes,
                ROUND(write_bytes::numeric / NULLIF(writes, 0), 2) AS avg_write_bytes
            FROM pg_stat_io
            WHERE reads > 0 OR writes > 0
            ORDER BY reads + writes DESC
        ) AS explain_result;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'I/O高级分析查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 3.1.8 性能优势与论证

### 3.1.8.1 性能优势分析

| 优势项 | 说明 | 价值 |
|--------|------|------|
| **字节级别统计** | 新增read_bytes、write_bytes、extend_bytes | 准确评估I/O数据量 |
| **详细分类** | 支持按对象和上下文分类 | 深入分析I/O模式 |
| **性能分析** | 便于识别I/O瓶颈 | 优化I/O性能 |
| **存储优化** | 便于优化存储配置 | 提升存储性能 |

### 3.1.8.2 性能优势论证

**论证：字节级别统计的价值**

```
前提条件：
P1: I/O次数统计无法准确反映I/O数据量
P2: 大块I/O和小块I/O的性能影响不同
P3: PostgreSQL 18提供字节级别统计

推理过程：
R1: 如果P1，则需要字节级别统计
R2: 如果P2，则字节级别统计更有价值
R3: 如果P3，则可以准确评估I/O数据量

结论：
C1: 字节级别统计可以准确评估I/O数据量
C2: 可以识别I/O瓶颈的具体原因
C3: 可以优化I/O性能
```

---

## 3.1.9 注意事项与最佳实践

### 3.1.9.1 注意事项

⚠️ **重要提醒**：

1. **版本要求**：需要PostgreSQL 18+

   ```sql
   -- 检查PostgreSQL版本（带错误处理）
   DO $$
   BEGIN
       BEGIN
           IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
               RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+，当前版本: %',
                   current_setting('server_version');
               RETURN;
           END IF;
           RAISE NOTICE 'PostgreSQL版本检查通过: %', current_setting('server_version');
       EXCEPTION
           WHEN OTHERS THEN
               RAISE WARNING '版本检查失败: %', SQLERRM;
               RAISE;
       END;
   END $$;
   ```

2. **统计重置**：统计信息在服务器重启或重置后会清零

3. **性能开销**：I/O统计本身性能开销很小

### 3.1.9.2 最佳实践

✅ **推荐做法**：

1. **定期监控**：设置定时任务，定期查询I/O统计

   ```sql
   -- 定期监控I/O统计（带错误处理）
   DO $$
   DECLARE
       io_summary RECORD;
   BEGIN
       BEGIN
           -- 检查PostgreSQL版本
           IF (SELECT current_setting('server_version_num')::int) < 180000 THEN
               RAISE WARNING 'pg_stat_io视图需要PostgreSQL 18+';
               RETURN;
           END IF;

           -- 查询I/O汇总统计
           SELECT
               SUM(reads) AS total_reads,
               SUM(read_bytes) AS total_read_bytes,
               SUM(writes) AS total_writes,
               SUM(write_bytes) AS total_write_bytes,
               ROUND(SUM(read_bytes)::numeric / 1024 / 1024 / 1024, 2) AS read_gb,
               ROUND(SUM(write_bytes)::numeric / 1024 / 1024 / 1024, 2) AS write_gb
           INTO io_summary
           FROM pg_stat_io
           WHERE reads > 0 OR writes > 0;

           RAISE NOTICE 'I/O统计汇总 - 读取: %.2f GB | 写入: %.2f GB',
               io_summary.read_gb, io_summary.write_gb;
       EXCEPTION
           WHEN OTHERS THEN
               RAISE WARNING 'I/O统计监控失败: %', SQLERRM;
               RAISE;
       END;
   END $$;
   ```

2. **趋势分析**：记录历史数据，分析I/O趋势

3. **阈值告警**：设置I/O阈值，超过阈值时告警

### 3.1.9.3 故障排查

🔧 **常见问题**：

1. **统计信息为空**
   - 检查PostgreSQL版本（需要18+）
   - 检查是否有I/O操作
   - 检查统计信息是否被重置

2. **I/O统计不准确**
   - 注意统计信息重置的影响
   - 考虑在稳定运行一段时间后查询

---

## 3.1.10 导航

### 3.1.10.1 章节导航

- **上一节**：无（本章为03-自我监测系统的第一节）
- **下一节**：[3.2 后端I/O追踪](./02-后端I-O追踪.md)
- **返回主题目录**：[03-自我监测系统](./README.md)
- **返回主文档**：[PostgreSQL-18-自动化运维与自我监测](../README.md)

### 3.1.10.2 相关章节

- [3.2 后端I/O追踪](./02-后端I-O追踪.md) - 后端级别I/O追踪
- [4.3 自动资源瓶颈检测](../04-自动化诊断/03-自动资源瓶颈检测.md) - I/O瓶颈检测
- [2.1 异步I/O支持](../02-自动化性能调优/01-异步I-O支持.md) - I/O性能优化

---

## 📚 参考资料

- [PostgreSQL 18 pg_stat_io文档](https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-IO-VIEW)
- [PostgreSQL性能调优指南](../PostgreSQL性能调优完整指南.md)

---

**最后更新**: 2025年1月
**文档版本**: v2.0（已添加决策树、推理论证、完整目录）
