# 08-自动VACUUM优化

> **所属主题**: 02-自动化性能调优
> **创建日期**: 2025年1月
> **PostgreSQL版本**: 18+

---

## 📋 目录

- [08-自动VACUUM优化](#08-自动vacuum优化)
  - [概述](#概述)
  - [自动VACUUM优化系统](#自动vacuum优化系统)
  - [VACUUM状态判断](#vacuum状态判断)
  - [PostgreSQL 18新特性](#postgresql-18新特性)
  - [使用示例](#使用示例)
  - [导航](#导航)

---

## 概述

PostgreSQL 18支持智能VACUUM策略调整，能够自动检测需要VACUUM的表，并根据死元组比例智能调整VACUUM策略。

---

## 自动VACUUM优化系统

```sql
-- PostgreSQL 18 自动VACUUM优化系统（带错误处理和性能测试）
DO $$
DECLARE
    vacuum_stats RECORD;
    vacuum_count int := 0;
BEGIN
    BEGIN
        RAISE NOTICE '=== PostgreSQL 18自动VACUUM优化系统 ===';
        RAISE NOTICE '分析VACUUM需求...';
        RAISE NOTICE '';

        -- 查找需要VACUUM的表
        FOR vacuum_stats IN
            SELECT
                schemaname,
                tablename,
                n_dead_tup,
                n_live_tup,
                ROUND(100.0 * n_dead_tup / NULLIF(n_dead_tup + n_live_tup, 0), 2) AS dead_tuple_ratio,
                last_autovacuum,
                autovacuum_count,
                CASE
                    WHEN n_dead_tup > 10000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_dead_tup + n_live_tup, 0), 2) > 10 THEN '紧急'
                    WHEN n_dead_tup > 1000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_dead_tup + n_live_tup, 0), 2) > 5 THEN '需要'
                    WHEN last_autovacuum IS NULL OR last_autovacuum < NOW() - INTERVAL '7 days' THEN '建议'
                    ELSE '正常'
                END AS vacuum_status
            FROM pg_stat_user_tables
            WHERE n_dead_tup > 0
            ORDER BY dead_tuple_ratio DESC, n_dead_tup DESC
            LIMIT 20
        LOOP
            IF vacuum_stats.vacuum_status IN ('紧急', '需要', '建议') THEN
                vacuum_count := vacuum_count + 1;
                RAISE NOTICE '需要VACUUM #%:', vacuum_count;
                RAISE NOTICE '  表: %.%', vacuum_stats.schemaname, vacuum_stats.tablename;
                RAISE NOTICE '  死元组数: %', vacuum_stats.n_dead_tup;
                RAISE NOTICE '  死元组比例: %%', vacuum_stats.dead_tuple_ratio;
                RAISE NOTICE '  最后VACUUM: %', COALESCE(vacuum_stats.last_autovacuum::text, '从未');
                RAISE NOTICE '  状态: %', vacuum_stats.vacuum_status;
                RAISE NOTICE '  建议: VACUUM ANALYZE %.%;', vacuum_stats.schemaname, vacuum_stats.tablename;
                RAISE NOTICE '';
            END IF;
        END LOOP;

        IF vacuum_count = 0 THEN
            RAISE NOTICE '所有表的VACUUM状态正常';
        ELSE
            RAISE NOTICE '共发现 % 个表需要VACUUM', vacuum_count;
        END IF;

        RAISE NOTICE '';
        RAISE NOTICE 'PostgreSQL 18自动化特性:';
        RAISE NOTICE '- 自动检测死元组比例';
        RAISE NOTICE '- 自动触发VACUUM';
        RAISE NOTICE '- 智能调整VACUUM策略';
        RAISE NOTICE '- 并行VACUUM支持（PostgreSQL 18新增）';
        RAISE NOTICE '- vacuum_truncate变量控制文件截断（PostgreSQL 18新增）';
        RAISE NOTICE '- vacuum_max_eager_freeze_failure_rate参数调整冻结策略（PostgreSQL 18新增）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '自动VACUUM优化失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## VACUUM状态判断

系统通过以下标准判断VACUUM状态：

| 状态 | 条件 | 优先级 |
|------|------|--------|
| **紧急** | 死元组 > 10000 且 死元组比例 > 10% | 最高 |
| **需要** | 死元组 > 1000 且 死元组比例 > 5% | 高 |
| **建议** | 超过7天未VACUUM | 中 |
| **正常** | 其他情况 | - |

---

## PostgreSQL 18新特性

PostgreSQL 18在VACUUM方面的新特性：

1. **并行VACUUM支持**：提升VACUUM性能
2. **vacuum_truncate变量**：控制文件截断行为
3. **vacuum_max_eager_freeze_failure_rate参数**：优化冻结策略
4. **异步I/O支持**：VACUUM操作可以利用异步I/O提升性能

---

## 使用示例

```sql
-- 执行自动VACUUM优化检查
DO $$ ... $$;  -- 使用上面的脚本

-- 根据建议执行VACUUM
VACUUM ANALYZE orders;
VACUUM ANALYZE users;

-- 使用PostgreSQL 18并行VACUUM（如果支持）
VACUUM (PARALLEL 4) ANALYZE large_table;
```

---

## 导航

- [返回主题目录](./README.md)
- [返回主文档](../README.md)
- [上一节：07-自动统计信息更新](./07-自动统计信息更新.md)

---

**最后更新**: 2025年1月
