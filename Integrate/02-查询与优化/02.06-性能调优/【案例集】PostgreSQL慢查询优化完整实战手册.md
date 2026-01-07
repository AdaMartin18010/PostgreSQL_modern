---

> **📋 文档来源**: `PostgreSQL培训\11-性能调优\【案例集】PostgreSQL慢查询优化完整实战手册.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【案例集】PostgreSQL慢查询优化完整实战手册

> **文档版本**: v1.0 | **创建日期**: 2025-01 | **适用版本**: PostgreSQL 12+
> **难度等级**: ⭐⭐⭐⭐ 高级 | **文档类型**: 实战案例集

---

## 📋 目录

- [【案例集】PostgreSQL慢查询优化完整实战手册](#案例集postgresql慢查询优化完整实战手册)
  - [📋 目录](#-目录)
  - [1. 课程概述](#1-课程概述)
    - [1.1 什么是慢查询？](#11-什么是慢查询)
      - [慢查询的影响](#慢查询的影响)
      - [优化目标](#优化目标)
    - [1.2 性能诊断流程](#12-性能诊断流程)
  - [2. 慢查询诊断工具](#2-慢查询诊断工具)
    - [2.1 pg\_stat\_statements](#21-pg_stat_statements)
      - [安装与配置](#安装与配置)
    - [2.2 EXPLAIN (ANALYZE, BUFFERS, TIMING)](#22-explain-analyze)
    - [2.3 慢查询日志](#23-慢查询日志)
    - [2.4 实时监控](#24-实时监控)
  - [3. 案例1：缺失索引](#3-案例1缺失索引)
    - [3.1 问题现象](#31-问题现象)
    - [3.2 诊断过程](#32-诊断过程)
  - [4. 案例2：索引选择不当](#4-案例2索引选择不当)
    - [4.1 问题现象](#41-问题现象)
    - [4.2 诊断过程](#42-诊断过程)
    - [4.3 解决方案](#43-解决方案)
    - [4.4 复合索引最佳实践](#44-复合索引最佳实践)
  - [5. 案例3：JOIN优化](#5-案例3join优化)
    - [5.1 问题现象](#51-问题现象)
    - [5.2 诊断过程](#52-诊断过程)
    - [5.3 解决方案](#53-解决方案)
    - [5.4 JOIN优化技巧](#54-join优化技巧)
  - [6. 案例4：子查询优化](#6-案例4子查询优化)
    - [6.1 问题现象](#61-问题现象)
    - [6.3 解决方案](#63-解决方案)
      - [方案1：添加索引](#方案1添加索引)
      - [方案2：改写为JOIN](#方案2改写为join)
  - [7. 案例5：分区表优化](#7-案例5分区表优化)
    - [7.1 问题现象](#71-问题现象)
    - [7.2 解决方案：时间分区](#72-解决方案时间分区)
    - [7.3 分区表最佳实践](#73-分区表最佳实践)
  - [8. 案例6：统计信息过期](#8-案例6统计信息过期)
    - [8.1 问题现象](#81-问题现象)
    - [8.2 诊断过程](#82-诊断过程)
    - [8.3 解决方案](#83-解决方案)
    - [8.4 统计信息监控](#84-统计信息监控)
  - [9. 案例7：锁等待](#9-案例7锁等待)
    - [9.1 问题现象](#91-问题现象)
    - [9.2 诊断过程](#92-诊断过程)
    - [9.3 解决方案](#93-解决方案)
    - [9.4 锁监控告警](#94-锁监控告警)
  - [10. 案例8：N+1查询问题](#10-案例8n1查询问题)
    - [10.1 问题现象](#101-问题现象)
    - [10.2 SQL体现](#102-sql体现)
    - [10.3 解决方案](#103-解决方案)
      - [方案1：使用JOIN（SQL层面）](#方案1使用joinsql层面)
      - [方案2：使用IN查询（应用层面）](#方案2使用in查询应用层面)
      - [方案3：ORM预加载](#方案3orm预加载)
    - [10.4 检测N+1问题](#104-检测n1问题)
  - [11. 案例9：大表全扫描](#11-案例9大表全扫描)
    - [11.1 问题现象](#111-问题现象)
    - [11.2 解决方案](#112-解决方案)
      - [方案1：使用统计信息估算](#方案1使用统计信息估算)
      - [方案2：缓存计数器](#方案2缓存计数器)
      - [方案3：分区+并行聚合](#方案3分区并行聚合)
    - [11.3 其他大表优化](#113-其他大表优化)
  - [12. 案例10：复杂聚合优化](#12-案例10复杂聚合优化)
    - [12.1 问题现象](#121-问题现象)
    - [12.2 解决方案](#122-解决方案)
      - [方案1：物化视图](#方案1物化视图)
      - [方案2：增量聚合](#方案2增量聚合)
      - [方案3：使用TimescaleDB连续聚合](#方案3使用timescaledb连续聚合)
  - [13. 案例11：DISTINCT优化](#13-案例11distinct优化)
    - [13.1 问题现象](#131-问题现象)
    - [13.2 解决方案](#132-解决方案)
  - [14. 案例12：ORDER BY优化](#14-案例12order-by优化)
    - [14.1 问题现象](#141-问题现象)
    - [14.2 解决方案](#142-解决方案)
  - [15. 优化方法总结](#15-优化方法总结)
    - [15.1 诊断流程](#151-诊断流程)
    - [15.2 优化技巧速查表](#152-优化技巧速查表)
    - [15.3 索引设计最佳实践](#153-索引设计最佳实践)
    - [15.4 配置优化参考](#154-配置优化参考)
  - [📚 延伸阅读](#-延伸阅读)
  - [✅ 学习检查清单](#-学习检查清单)

---

## 1. 课程概述

### 1.1 什么是慢查询？

**慢查询定义**：执行时间超过预期的SQL查询。

#### 慢查询的影响

| 影响 | 说明 | 后果 |
| --- | --- | --- |
| **用户体验差** | 页面加载慢 | 用户流失 |
| **资源浪费** | CPU、内存、IO占用 | 影响其他查询 |
| **连接耗尽** | 慢查询占用连接池 | 新请求被拒绝 |
| **锁等待** | 长事务持有锁 | 其他事务阻塞 |
| **系统雪崩** | 慢查询堆积 | 数据库崩溃 |

#### 优化目标

```text
优化金字塔（从易到难）：

1. 低垂的果实（80%收益，20%努力）
   - 添加缺失索引
   - 更新统计信息
   - 调整简单配置

2. 中等优化（15%收益，30%努力）
   - 重写SQL
   - 索引优化
   - 查询重构

3. 架构优化（5%收益，50%努力）
   - 分区
   - 缓存
   - 读写分离
```

### 1.2 性能诊断流程

```text
1. 发现慢查询
   ├─ pg_stat_statements
   ├─ 慢查询日志
   └─ 应用监控（APM）

2. 分析原因
   ├─ EXPLAIN (ANALYZE, BUFFERS, TIMING)
   ├─ pg_stat_user_tables
   └─ pg_locks

3. 制定方案
   ├─ 索引优化
   ├─ SQL重写
   └─ 配置调整

4. 验证效果
   ├─ EXPLAIN (ANALYZE, BUFFERS, TIMING)对比
   ├─ 生产监控
   └─ 负载测试

5. 持续监控
   └─ 自动化监控告警
```

---

## 2. 慢查询诊断工具

### 2.1 pg_stat_statements

#### 安装与配置

```sql
-- 1. 安装扩展（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
            CREATE EXTENSION pg_stat_statements;
            RAISE NOTICE 'pg_stat_statements 扩展创建成功';
        ELSE
            RAISE NOTICE 'pg_stat_statements 扩展已存在';
        END IF;
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE WARNING '权限不足，无法创建 pg_stat_statements 扩展';
        WHEN OTHERS THEN
            RAISE WARNING '创建 pg_stat_statements 扩展失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 配置（postgresql.conf）
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.max = 10000
-- pg_stat_statements.track = all
-- 重启PostgreSQL

-- 3. 查看Top 10慢查询（按平均执行时间，带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
            RAISE WARNING 'pg_stat_statements 扩展未安装，无法查看慢查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始查看Top 10慢查询';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查看慢查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    queryid,
    LEFT(query, 100) AS query_snippet,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(total_exec_time::numeric, 2) AS total_ms,
    ROUND((100 * total_exec_time / NULLIF(SUM(total_exec_time) OVER (), 0))::numeric, 2) AS pct_total,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 4. 按总执行时间排序（找出累积影响最大的）
SELECT
    queryid,
    LEFT(query, 100) AS query_snippet,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_ms,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 5. 重置统计
SELECT pg_stat_statements_reset();
```

### 2.2 EXPLAIN (ANALYZE, BUFFERS, TIMING)

```sql
-- 基本用法（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行EXPLAIN (ANALYZE, BUFFERS, TIMING)';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE email = 'test@example.com';

-- 详细输出（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行详细EXPLAIN (ANALYZE, BUFFERS, TIMING)';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS, TIMING)
SELECT * FROM users WHERE email = 'test@example.com';

-- 关键指标解读：
-- Planning Time: 查询规划时间
-- Execution Time: 实际执行时间
-- Buffers: shared hit（缓存命中）, read（磁盘读取）
-- Rows: actual vs estimated（如果偏差大，需更新统计信息）
```

### 2.3 慢查询日志

```sql
-- postgresql.conf配置
-- log_min_duration_statement = 1000  -- 记录超过1秒的查询
-- log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a,client=%h '
-- log_statement = 'none'
-- 重启PostgreSQL

-- 查看日志
-- Linux: tail -f /var/log/postgresql/postgresql-15-main.log
-- Docker: docker logs -f postgres-container

-- 使用pgBadger分析日志
-- pgbadger /var/log/postgresql/postgresql.log -o report.html
```

### 2.4 实时监控

```sql
-- 查看当前运行的慢查询（带错误处理和性能测试）
DO $$
DECLARE
    slow_query_count INT;
BEGIN
    BEGIN
        SELECT COUNT(*) INTO slow_query_count
        FROM pg_stat_activity
        WHERE state != 'idle'
        AND query_start < now() - INTERVAL '5 seconds';

        IF slow_query_count > 0 THEN
            RAISE WARNING '发现 % 个运行时间超过5秒的查询', slow_query_count;
        ELSE
            RAISE NOTICE '未发现运行时间超过5秒的查询';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查看慢查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    pid,
    now() - query_start AS duration,
    state,
    LEFT(query, 100) as query_preview
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < now() - INTERVAL '5 seconds'
ORDER BY duration DESC;

-- 终止长时间运行的查询（带错误处理）
-- 注意：应该根据实际pid值执行，这里提供示例
DO $$
DECLARE
    v_pid INT;
BEGIN
    BEGIN
        -- 获取第一个长时间运行的查询pid（示例）
        SELECT pid INTO v_pid
        FROM pg_stat_activity
        WHERE state != 'idle'
        AND query_start < now() - INTERVAL '5 seconds'
        ORDER BY query_start
        LIMIT 1;

        IF v_pid IS NULL THEN
            RAISE NOTICE '没有找到需要终止的查询';
            RETURN;
        END IF;

        -- 优雅终止（示例，实际使用时需要确认）
        -- PERFORM pg_cancel_backend(v_pid);
        RAISE NOTICE '示例：可以通过 pg_cancel_backend(%) 优雅终止查询', v_pid;
        RAISE NOTICE '或者使用 pg_terminate_backend(%) 强制终止查询', v_pid;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '终止查询失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 实际使用时（需要替换实际的pid值）：
-- SELECT pg_cancel_backend(12345);  -- 优雅终止
-- SELECT pg_terminate_backend(12345);  -- 强制终止
```

---

## 3. 案例1：缺失索引

### 3.1 问题现象

```sql
-- 用户登录查询慢（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行用户登录查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试用户登录查询（执行时间：1200ms，表有100万行）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '用户登录查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT id, username, email, created_at
FROM users
WHERE email = 'alice@example.com';

-- 执行时间：1200ms（表有100万行）
```

### 3.2 诊断过程

```sql
-- 诊断过程（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法执行诊断';
            RETURN;
        END IF;
        RAISE NOTICE '开始诊断查询性能问题';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '诊断查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, username, email, created_at
FROM users
WHERE email = 'alice@example.com';

-- 输出示例：
-- Seq Scan on users  (cost=0.00..25833.00 rows=1 width=128) (actual time=1156.234..1156.235 rows=1 loops=1)
--   Filter: (email = 'alice@example.com'::text)
--   Rows Removed by Filter: 999999
--   Buffers: shared hit=8334
-- Planning Time: 0.123 ms
-- Execution Time: 1156.345 ms

-- 关键发现：
-- 1. Seq Scan（全表扫描）
-- 2. Rows Removed by Filter: 999999（扫描了100万行）

### 3.3 解决方案

```sql
-- 创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建索引';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_email_idx') THEN
            RAISE WARNING '索引 users_email_idx 已存在';
        ELSE
            CREATE INDEX users_email_idx ON users(email);
            RAISE NOTICE '索引 users_email_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '索引 users_email_idx 已存在';
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 再次执行查询（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_email_idx') THEN
            RAISE WARNING '索引 users_email_idx 不存在，查询可能仍然较慢';
        END IF;
        RAISE NOTICE '开始测试优化后的查询性能';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, username, email, created_at
FROM users
WHERE email = 'alice@example.com';

-- 输出示例：
-- Index Scan using users_email_idx on users  (cost=0.42..8.44 rows=1 width=128) (actual time=0.034..0.035 rows=1 loops=1)
--   Index Cond: (email = 'alice@example.com'::text)
--   Buffers: shared hit=4
-- Planning Time: 0.156 ms
-- Execution Time: 0.052 ms

-- 性能提升：1156ms → 0.052ms（约22000倍！）

### 3.4 最佳实践

```sql
-- 1. 为外键创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_id_idx') THEN
            CREATE INDEX orders_user_id_idx ON orders(user_id);
            RAISE NOTICE '索引 orders_user_id_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 orders_user_id_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_id_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 为频繁查询的列创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_created_at_idx') THEN
            CREATE INDEX users_created_at_idx ON users(created_at);
            RAISE NOTICE '索引 users_created_at_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 users_created_at_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 users_created_at_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 复合索引（查询涉及多列，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_status_idx') THEN
            CREATE INDEX orders_user_status_idx ON orders(user_id, status);
            RAISE NOTICE '索引 orders_user_status_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 orders_user_status_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_status_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. 部分索引（只索引部分行，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_pending_idx') THEN
            CREATE INDEX orders_pending_idx ON orders(user_id)
            WHERE status = 'pending';
            RAISE NOTICE '部分索引 orders_pending_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 orders_pending_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_pending_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. 表达式索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_lower_email_idx') THEN
            CREATE INDEX users_lower_email_idx ON users(LOWER(email));
            RAISE NOTICE '表达式索引 users_lower_email_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 users_lower_email_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 users_lower_email_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 4. 案例2：索引选择不当

### 4.1 问题现象

```sql
-- 查询慢，但已有索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_created_at_idx') THEN
            CREATE INDEX orders_created_at_idx ON orders(created_at);
            RAISE NOTICE '索引 orders_created_at_idx 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_id_idx') THEN
            CREATE INDEX orders_user_id_idx ON orders(user_id);
            RAISE NOTICE '索引 orders_user_id_idx 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_status_idx') THEN
            CREATE INDEX orders_status_idx ON orders(status);
            RAISE NOTICE '索引 orders_status_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '部分索引已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 执行查询（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行查询（示例：执行时间500ms）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SELECT * FROM orders
WHERE user_id = 123
  AND status = 'completed'
  AND created_at >= '2025-01-01';
```

### 4.2 诊断过程

```sql
-- 诊断过程（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行诊断';
            RETURN;
        END IF;
        RAISE NOTICE '开始诊断索引选择问题';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '诊断查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE user_id = 123
  AND status = 'completed'
  AND created_at >= '2025-01-01';

-- 输出示例：
-- Index Scan using orders_created_at_idx on orders  (cost=0.42..1234.56 rows=100 width=256) (actual time=12.3..498.7 rows=50 loops=1)
--   Index Cond: (created_at >= '2025-01-01'::date)
--   Filter: ((user_id = 123) AND (status = 'completed'::text))
--   Rows Removed by Filter: 9950
--   Buffers: shared hit=1500 read=800

-- 问题：
-- 1. 使用了created_at索引，但过滤条件不够精确
-- 2. Rows Removed by Filter: 9950（大量行被过滤）
```

### 4.3 解决方案

```sql
-- 创建复合索引（匹配所有查询条件，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_status_created_idx') THEN
            CREATE INDEX orders_user_status_created_idx
            ON orders(user_id, status, created_at);
            RAISE NOTICE '复合索引 orders_user_status_created_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 orders_user_status_created_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_status_created_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 或者根据选择性排序（高选择性在前，带错误处理）
-- 假设：user_id有100万种，status只有5种，created_at中等
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_created_status_idx') THEN
            CREATE INDEX orders_user_created_status_idx
            ON orders(user_id, created_at, status);
            RAISE NOTICE '复合索引 orders_user_created_status_idx 创建成功';
        ELSE
            RAISE NOTICE '索引 orders_user_created_status_idx 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_created_status_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 再次测试（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行测试';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试优化后的查询性能';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE user_id = 123
  AND status = 'completed'
  AND created_at >= '2025-01-01';

-- 输出示例：
-- Index Scan using orders_user_status_created_idx on orders  (cost=0.42..45.23 rows=50 width=256) (actual time=0.123..0.456 rows=50 loops=1)
--   Index Cond: ((user_id = 123) AND (status = 'completed'::text) AND (created_at >= '2025-01-01'::date))
--   Buffers: shared hit=8
-- Execution Time: 0.512 ms

-- 性能提升：500ms → 0.5ms（约1000倍）
```

### 4.4 复合索引最佳实践

```sql
-- 规则1：精确匹配在前，范围查询在后（带错误处理）
-- ✅ 好
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'idx1') THEN
            CREATE INDEX idx1 ON orders(user_id, created_at);
            RAISE NOTICE '索引 idx1 创建成功（示例：精确匹配在前）';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 idx1 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- ❌ 坏：created_at是范围查询，user_id无法利用索引
-- CREATE INDEX idx2 ON orders(created_at, user_id);  -- 不推荐

-- 规则2：选择性高的列在前（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法计算选择性';
            RETURN;
        END IF;
        RAISE NOTICE '开始计算列选择性';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '计算选择性准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 选择性 = DISTINCT值数量 / 总行数
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    COUNT(DISTINCT user_id)::float / NULLIF(COUNT(*), 0) AS user_id_selectivity,
    COUNT(DISTINCT status)::float / NULLIF(COUNT(*), 0) AS status_selectivity
FROM orders;
-- user_id: 0.95 (高选择性)
-- status: 0.005 (低选择性)
-- → CREATE INDEX ON orders(user_id, status);

-- 规则3：考虑查询频率（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        -- 如果大部分查询只用user_id，少部分用user_id+status
        -- → 创建两个索引更好
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_id_idx') THEN
            CREATE INDEX orders_user_id_idx ON orders(user_id);
            RAISE NOTICE '索引 orders_user_id_idx 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_status_idx') THEN
            CREATE INDEX orders_user_status_idx ON orders(user_id, status);
            RAISE NOTICE '索引 orders_user_status_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '部分索引已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

---

## 5. 案例3：JOIN优化

### 5.1 问题现象

```sql
-- 多表JOIN查询慢（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
            RAISE WARNING '必需的表不存在，无法执行JOIN查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行多表JOIN查询（示例：执行时间8000ms）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SELECT
    u.username,
    o.order_id,
    oi.product_name,
    oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
WHERE u.created_at >= '2025-01-01';
```

### 5.2 诊断过程

```sql
-- 诊断过程（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
            RAISE WARNING '必需的表不存在，无法执行诊断';
            RETURN;
        END IF;
        RAISE NOTICE '开始诊断JOIN查询性能问题';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '诊断查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    u.username,
    o.order_id,
    oi.product_name,
    oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
WHERE u.created_at >= '2025-01-01';

-- 输出示例：
-- Hash Join  (cost=45678.90..123456.78 rows=100000 width=128) (actual time=2345.67..7890.12 rows=95000 loops=1)
--   Hash Cond: (o.user_id = u.id)
--   ->  Seq Scan on orders o  (cost=0.00..34567.89 rows=500000 width=64) (actual time=0.012..1234.56 rows=500000 loops=1)
--   ->  Hash  (cost=34567.89..34567.89 rows=50000 width=32) (actual time=567.89..567.89 rows=50000 loops=1)
--         Buckets: 65536  Batches: 1  Memory Usage: 3456kB
--         ->  Seq Scan on users u  (cost=0.00..34567.89 rows=50000 width=32) (actual time=0.023..456.78 rows=50000 loops=1)
--               Filter: (created_at >= '2025-01-01'::date)
--               Rows Removed by Filter: 950000
--   ->  Hash Join  (...)
--         ->  Seq Scan on order_items oi  (...)

-- 问题：
-- 1. users表全扫描（Seq Scan）
-- 2. orders表全扫描
-- 3. 没有索引支持JOIN
```

### 5.3 解决方案

```sql
-- 1. 为过滤条件创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_created_at_idx') THEN
            CREATE INDEX users_created_at_idx ON users(created_at);
            RAISE NOTICE '索引 users_created_at_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 users_created_at_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 为JOIN条件创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_id_idx') THEN
            CREATE INDEX orders_user_id_idx ON orders(user_id);
            RAISE NOTICE '索引 orders_user_id_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_id_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
            RAISE WARNING '表 order_items 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'order_items' AND indexname = 'order_items_order_id_idx') THEN
            CREATE INDEX order_items_order_id_idx ON order_items(order_id);
            RAISE NOTICE '索引 order_items_order_id_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 order_items 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 order_items_order_id_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 更新统计信息（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
            RAISE WARNING '必需的表不存在，无法更新统计信息';
            RETURN;
        END IF;

        ANALYZE users, orders, order_items;
        RAISE NOTICE '统计信息更新成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN OTHERS THEN
            RAISE WARNING '更新统计信息失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 再次测试（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'order_items') THEN
            RAISE WARNING '必需的表不存在，无法执行测试';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试优化后的JOIN查询性能';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '测试查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
    u.username,
    o.order_id,
    oi.product_name,
    oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
WHERE u.created_at >= '2025-01-01';

-- 输出示例：
-- Nested Loop  (cost=1.27..2345.67 rows=95000 width=128) (actual time=0.234..567.89 rows=95000 loops=1)
--   ->  Nested Loop  (...)
--         ->  Index Scan using users_created_at_idx on users u  (cost=0.42..234.56 rows=50000 width=32) (actual time=0.012..45.67 rows=50000 loops=1)
--               Index Cond: (created_at >= '2025-01-01'::date)
--         ->  Index Scan using orders_user_id_idx on orders o  (cost=0.42..12.34 rows=10 width=64) (actual time=0.003..0.008 rows=10 loops=50000)
--               Index Cond: (user_id = u.id)
--   ->  Index Scan using order_items_order_id_idx on order_items oi  (cost=0.42..8.45 rows=2 width=64) (actual time=0.002..0.004 rows=2 loops=500000)
--         Index Cond: (order_id = o.id)

-- 性能提升：8000ms → 568ms（约14倍）
```

### 5.4 JOIN优化技巧

```sql
-- 技巧1：避免JOIN大表，先过滤后JOIN（带错误处理和性能测试）
-- ❌ 坏：先JOIN后过滤
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table1') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table2') THEN
            RAISE WARNING '必需的表不存在，无法演示JOIN优化';
            RETURN;
        END IF;
        RAISE NOTICE '开始演示JOIN优化（❌ 坏：先JOIN后过滤）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'JOIN优化演示准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM large_table1 t1
JOIN large_table2 t2 ON t1.id = t2.ref_id
WHERE t1.created_at >= '2025-01-01';

-- ✅ 好：使用CTE或子查询先过滤
WITH filtered AS (
    SELECT * FROM large_table1
    WHERE created_at >= '2025-01-01'
)
SELECT * FROM filtered f
JOIN large_table2 t2 ON f.id = t2.ref_id;

-- 技巧2：确保JOIN列有索引
CREATE INDEX t1_id_idx ON table1(id);
CREATE INDEX t2_ref_id_idx ON table2(ref_id);

-- 技巧3：使用INNER JOIN替代OUTER JOIN（如果可以）
-- INNER JOIN性能通常更好

-- 技巧4：考虑JOIN顺序（小表在前）
-- PostgreSQL优化器会自动优化，但有时手动调整更好
SELECT /*+ Leading(small_table large_table) */ *
FROM large_table
JOIN small_table ON ...;
```

---

## 6. 案例4：子查询优化

### 6.1 问题现象

```sql
-- IN子查询慢（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行IN子查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行IN子查询（示例：执行时间3000ms）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SELECT * FROM orders
WHERE user_id IN (
    SELECT id FROM users WHERE country = 'US'
);

### 6.2 诊断过程

```sql
-- 诊断过程（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行诊断';
            RETURN;
        END IF;
        RAISE NOTICE '开始诊断IN子查询性能问题';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '诊断查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders
WHERE user_id IN (
    SELECT id FROM users WHERE country = 'US'
);

-- 输出示例：
-- Hash Semi Join  (cost=34567.89..56789.01 rows=10000 width=256) (actual time=1234.56..2987.65 rows=10000 loops=1)
--   Hash Cond: (orders.user_id = users.id)
--   ->  Seq Scan on orders  (cost=0.00..12345.67 rows=100000 width=256) (actual time=0.012..567.89 rows=100000 loops=1)
--   ->  Hash  (cost=23456.78..23456.78 rows=50000 width=4) (actual time=789.01..789.01 rows=50000 loops=1)
--         ->  Seq Scan on users  (cost=0.00..23456.78 rows=50000 width=4) (actual time=0.023..678.90 rows=50000 loops=1)
--               Filter: (country = 'US'::text)
--               Rows Removed by Filter: 950000

-- 问题：全表扫描
```

### 6.3 解决方案

#### 方案1：添加索引

```sql
-- 创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '表 users 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'users' AND indexname = 'users_country_idx') THEN
            CREATE INDEX users_country_idx ON users(country);
            RAISE NOTICE '索引 users_country_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 users 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 users_country_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders' AND indexname = 'orders_user_id_idx') THEN
            CREATE INDEX orders_user_id_idx ON orders(user_id);
            RAISE NOTICE '索引 orders_user_id_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '索引 orders_user_id_idx 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 更新统计信息（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '必需的表不存在，无法更新统计信息';
            RETURN;
        END IF;

        ANALYZE users, orders;
        RAISE NOTICE '统计信息更新成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表不存在';
        WHEN OTHERS THEN
            RAISE WARNING '更新统计信息失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能提升：3000ms → 450ms
```

#### 方案2：改写为JOIN

```sql
-- JOIN通常比IN子查询更快（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行JOIN查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行JOIN查询（示例：性能350ms，比方案1更快）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT o.* FROM orders o
JOIN users u ON o.user_id = u.id
WHERE u.country = 'US';

#### 方案3：EXISTS替代IN

```sql
-- 当子查询返回大量结果时，EXISTS更快（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行EXISTS查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行EXISTS查询（示例：性能380ms）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders o
WHERE EXISTS (
    SELECT 1 FROM users u
    WHERE u.id = o.user_id
      AND u.country = 'US'
);

### 6.4 子查询优化规则

```sql
-- 规则1：避免在SELECT列表中使用子查询（导致N+1问题，带错误处理）
-- ❌ 坏：每行都执行一次子查询！
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE WARNING '示例：不推荐在SELECT列表中使用子查询（N+1问题）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- SELECT
--     o.order_id,
--     (SELECT u.username FROM users u WHERE u.id = o.user_id) AS username
-- FROM orders o;
-- 每行都执行一次子查询，性能差！

-- ✅ 好：使用JOIN（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') OR
           NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE WARNING '必需的表不存在，无法执行JOIN查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行JOIN查询（推荐方式）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    o.order_id,
    u.username
FROM orders o
JOIN users u ON o.user_id = u.id;

-- 规则2：NOT IN → NOT EXISTS或LEFT JOIN
-- NOT IN在子查询返回NULL时有问题
-- ❌ 坏
SELECT * FROM orders
WHERE user_id NOT IN (SELECT id FROM blacklist);
-- 如果blacklist.id有NULL，结果为空！

-- ✅ 好
SELECT * FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM blacklist b WHERE b.id = o.user_id
);

-- 或使用LEFT JOIN
SELECT o.* FROM orders o
LEFT JOIN blacklist b ON o.user_id = b.id
WHERE b.id IS NULL;

-- 规则3：标量子查询缓存
-- PostgreSQL会缓存标量子查询结果（参数相同时）
SELECT
    product_id,
    price,
    (SELECT AVG(price) FROM products) AS avg_price  -- 只计算一次
FROM products;
```

---

## 7. 案例5：分区表优化

### 7.1 问题现象

```sql
-- 历史订单表查询慢（10亿行，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '执行历史订单表查询（示例：10亿行，执行时间45000ms）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '执行查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

SELECT * FROM orders
WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01';
```

### 7.2 解决方案：时间分区

```sql
-- 1. 创建分区表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 已存在，可能需要删除后重新创建分区表';
            RETURN;
        END IF;

        CREATE TABLE orders (
            id BIGSERIAL,
            user_id BIGINT NOT NULL,
            amount DECIMAL(10,2),
            status VARCHAR(20),
            created_at TIMESTAMPTZ NOT NULL
        ) PARTITION BY RANGE (created_at);
        RAISE NOTICE '分区表 orders 创建成功';
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 orders 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建分区表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 创建月度分区（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '分区表 orders 不存在，无法创建分区';
            RETURN;
        END IF;

        -- 创建2025年1月分区
        IF NOT EXISTS (SELECT 1 FROM pg_inherits WHERE inhparent = 'orders'::regclass AND inhrelid::regclass::text = 'orders_2025_01') THEN
            CREATE TABLE orders_2025_01 PARTITION OF orders
            FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
            RAISE NOTICE '分区 orders_2025_01 创建成功';
        ELSE
            RAISE NOTICE '分区 orders_2025_01 已存在';
        END IF;

        -- 创建2025年2月分区
        IF NOT EXISTS (SELECT 1 FROM pg_inherits WHERE inhparent = 'orders'::regclass AND inhrelid::regclass::text = 'orders_2025_02') THEN
            CREATE TABLE orders_2025_02 PARTITION OF orders
            FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
            RAISE NOTICE '分区 orders_2025_02 创建成功';
        ELSE
            RAISE NOTICE '分区 orders_2025_02 已存在';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '分区表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '分区已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建分区失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 创建其他分区（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '分区表 orders 不存在，无法创建分区';
            RETURN;
        END IF;

        -- 创建2024年1月分区
        IF NOT EXISTS (SELECT 1 FROM pg_inherits WHERE inhparent = 'orders'::regclass AND inhrelid::regclass::text = 'orders_2024_01') THEN
            CREATE TABLE orders_2024_01 PARTITION OF orders
            FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
            RAISE NOTICE '分区 orders_2024_01 创建成功';
        END IF;

        -- 创建2024年2月分区
        IF NOT EXISTS (SELECT 1 FROM pg_inherits WHERE inhparent = 'orders'::regclass AND inhrelid::regclass::text = 'orders_2024_02') THEN
            CREATE TABLE orders_2024_02 PARTITION OF orders
            FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
            RAISE NOTICE '分区 orders_2024_02 创建成功';
        END IF;

        -- ...每月一个分区（可根据需要继续添加）
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '分区表 orders 不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '部分分区已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建分区失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 为每个分区创建索引（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders_2025_01') THEN
            RAISE WARNING '分区 orders_2025_01 不存在，无法创建索引';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders_2025_01' AND indexname = 'orders_2025_01_user_id_idx') THEN
            CREATE INDEX orders_2025_01_user_id_idx ON orders_2025_01(user_id);
            RAISE NOTICE '索引 orders_2025_01_user_id_idx 创建成功';
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'orders_2025_01' AND indexname = 'orders_2025_01_created_at_idx') THEN
            CREATE INDEX orders_2025_01_created_at_idx ON orders_2025_01(created_at);
            RAISE NOTICE '索引 orders_2025_01_created_at_idx 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '分区不存在';
        WHEN duplicate_table THEN
            RAISE WARNING '部分索引已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建索引失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 4. 自动化分区创建（使用pg_partman扩展，带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_partman') THEN
            CREATE EXTENSION pg_partman;
            RAISE NOTICE 'pg_partman扩展创建成功';
        ELSE
            RAISE NOTICE 'pg_partman扩展已存在';
        END IF;
    EXCEPTION
        WHEN undefined_object THEN
            RAISE WARNING 'pg_partman扩展未安装，请先安装pg_partman扩展';
            RETURN;
        WHEN OTHERS THEN
            RAISE WARNING '创建pg_partman扩展失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法使用pg_partman创建父表';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM partman.part_config WHERE parent_table = 'public.orders') THEN
            RAISE WARNING '表 orders 已在pg_partman中配置';
        ELSE
            PERFORM partman.create_parent(
                p_parent_table => 'public.orders',
                p_control => 'created_at',
                p_type => 'native',
                p_interval => 'monthly',
                p_premake => 3  -- 提前创建3个月
            );
            RAISE NOTICE 'pg_partman父表配置成功';
        END IF;
    EXCEPTION
        WHEN undefined_function THEN
            RAISE WARNING 'partman.create_parent函数不存在，请检查pg_partman扩展是否正确安装';
        WHEN OTHERS THEN
            RAISE WARNING '配置pg_partman父表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 5. 查询（自动分区裁剪，带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行分区查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试分区查询（自动分区裁剪）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '分区查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM orders
WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01';

-- 输出：
-- Index Scan using orders_2025_01_created_at_idx on orders_2025_01 orders  (...)
--   Index Cond: ((created_at >= '2025-01-01'::timestamptz) AND (created_at < '2025-02-01'::timestamptz))
-- Execution Time: 123.45 ms

-- 性能提升：45000ms → 123ms（365倍！）
```

### 7.3 分区表最佳实践

```sql
-- 1. 启用分区裁剪（默认开启）
SHOW enable_partition_pruning;  -- 应该是 on

-- 2. 分区键选择原则
-- ✅ 好：查询经常过滤的列（时间、地区、租户ID）
-- ❌ 坏：高基数列（用户ID、订单ID）

-- 3. 分区数量建议
-- - 少于1000个分区
-- - 每个分区至少10GB（否则过度分区）

-- 4. 维护自动化
-- 使用pg_partman自动创建/删除分区
SELECT partman.run_maintenance('public.orders');

-- 5. 历史分区归档
-- 将旧分区DETACH后导出到冷存储
ALTER TABLE orders DETACH PARTITION orders_2023_01;
pg_dump -t orders_2023_01 | gzip > orders_2023_01.sql.gz
DROP TABLE orders_2023_01;
```

---

## 8. 案例6：统计信息过期

### 8.1 问题现象

```sql
-- 查询慢，但有索引且查询简单（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
            RAISE WARNING '表 products 不存在，无法执行查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试查询（EXPLAIN显示估算行数与实际相差巨大）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM products
WHERE category = 'Electronics';

-- EXPLAIN显示估算行数与实际相差巨大
-- Estimated rows: 100, Actual rows: 50000
```

### 8.2 诊断过程

```sql
-- 查看统计信息最后更新时间
SELECT
    schemaname,
    relname,
    n_live_tup AS row_count,
    n_dead_tup AS dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE relname = 'products';

-- 如果last_analyze很久之前，或dead_rows很高，需要ANALYZE
```

### 8.3 解决方案

```sql
-- 1. 手动更新统计信息（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
            RAISE WARNING '表 products 不存在，无法更新统计信息';
            RETURN;
        END IF;

        ANALYZE products;
        RAISE NOTICE '表 products 的统计信息更新成功';
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 products 不存在';
        WHEN OTHERS THEN
            RAISE WARNING '更新统计信息失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 2. 更新所有表（带错误处理）
DO $$
DECLARE
    table_count INT;
BEGIN
    BEGIN
        SELECT COUNT(*) INTO table_count
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';

        IF table_count = 0 THEN
            RAISE WARNING 'public schema下没有表，无法更新统计信息';
            RETURN;
        END IF;

        ANALYZE;
        RAISE NOTICE '所有表的统计信息更新成功（共 % 个表）', table_count;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '更新所有表统计信息失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 3. 调整自动ANALYZE阈值（postgresql.conf）
-- autovacuum_analyze_scale_factor = 0.1  # 默认10%变化才触发
-- 对于大表，改为更低：
ALTER TABLE large_table SET (autovacuum_analyze_scale_factor = 0.02);

-- 4. 增加统计信息采样
ALTER TABLE products ALTER COLUMN category SET STATISTICS 1000;
-- 默认100，增加到1000可以提高复杂查询的准确性
ANALYZE products;

-- 5. 配置自动VACUUM（防止死行堆积）
-- autovacuum = on
-- autovacuum_max_workers = 3
-- autovacuum_naptime = 1min
```

### 8.4 统计信息监控

```sql
-- 查看需要ANALYZE的表
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 2) AS dead_ratio,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
  AND (last_analyze IS NULL OR last_analyze < now() - INTERVAL '1 day')
ORDER BY n_dead_tup DESC;
```

---

## 9. 案例7：锁等待

### 9.1 问题现象

```sql
-- 简单查询等待很久
SELECT * FROM orders WHERE id = 123;
-- 执行时间：30000ms（30秒），但实际计算只需1ms
```

### 9.2 诊断过程

```sql
-- 1. 查看锁等待情况
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application,
    blocking_activity.application_name AS blocking_application
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 2. 查看长事务
SELECT
    pid,
    now() - xact_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state IN ('idle in transaction', 'active')
  AND xact_start < now() - INTERVAL '5 minutes'
ORDER BY xact_start;
```

### 9.3 解决方案

```sql
-- 1. 终止阻塞的长事务
SELECT pg_terminate_backend(12345);  -- 替换为实际的blocking_pid

-- 2. 应用层优化：缩短事务时间
-- ❌ 坏：长事务
BEGIN;
-- 执行大量操作
-- 调用外部API（慢）
-- 执行复杂计算
COMMIT;

-- ✅ 好：短事务
BEGIN;
-- 只包含必要的数据库操作
COMMIT;
-- 外部API调用移到事务外

-- 3. 配置锁超时
SET lock_timeout = '5s';  -- 等待锁超过5秒自动取消
SET statement_timeout = '30s';  -- 语句执行超过30秒自动取消

-- 4. 使用FOR UPDATE SKIP LOCKED（避免等待）
-- 场景：任务队列，多个worker并发获取任务
-- ❌ 坏：会等待锁
SELECT * FROM tasks
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE;

-- ✅ 好：跳过被锁的行
SELECT * FROM tasks
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

### 9.4 锁监控告警

```sql
-- 创建监控视图
CREATE VIEW lock_monitor AS
SELECT
    blocked_activity.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid,
    now() - blocked_activity.query_start AS wait_duration,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 告警：等待超过10秒
SELECT * FROM lock_monitor
WHERE wait_duration > INTERVAL '10 seconds';
```

---

## 10. 案例8：N+1查询问题

### 10.1 问题现象

```python
# Python/Django ORM示例
# 查询10个订单及其用户信息
orders = Order.objects.filter(status='completed')[:10]
for order in orders:
    print(f"Order {order.id}: {order.user.username}")
# 执行了1 + 10 = 11次查询！
```

### 10.2 SQL体现

```sql
-- 第1次查询：获取订单
SELECT * FROM orders WHERE status = 'completed' LIMIT 10;

-- 第2-11次查询：每个订单查询一次用户（N+1问题！）
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE id = 2;
SELECT * FROM users WHERE id = 3;
-- ...
SELECT * FROM users WHERE id = 10;

-- 总查询数：1 + 10 = 11次
-- 总时间：如果每次5ms，则 11 * 5ms = 55ms
```

### 10.3 解决方案

#### 方案1：使用JOIN（SQL层面）

```sql
-- 一次查询获取所有数据
SELECT
    o.id AS order_id,
    o.amount,
    o.status,
    u.id AS user_id,
    u.username,
    u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.status = 'completed'
LIMIT 10;

-- 总查询数：1次
-- 总时间：5ms
-- 性能提升：55ms → 5ms（11倍）
```

#### 方案2：使用IN查询（应用层面）

```sql
-- 第1步：获取订单
SELECT * FROM orders WHERE status = 'completed' LIMIT 10;
-- 返回user_id: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

-- 第2步：批量查询用户
SELECT * FROM users WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

-- 总查询数：2次（而不是11次）
-- 总时间：10ms
```

#### 方案3：ORM预加载

```python
# Django ORM: select_related（1次查询，JOIN）
orders = Order.objects.select_related('user').filter(status='completed')[:10]
for order in orders:
    print(f"Order {order.id}: {order.user.username}")
# 生成SQL：SELECT * FROM orders JOIN users ...
# 只执行1次查询！

# Django ORM: prefetch_related（2次查询，IN）
orders = Order.objects.prefetch_related('items').filter(status='completed')[:10]
# 第1次：SELECT * FROM orders ...
# 第2次：SELECT * FROM order_items WHERE order_id IN (...)

# SQLAlchemy: joinedload
orders = session.query(Order).options(joinedload(Order.user)).filter(...)
```

### 10.4 检测N+1问题

```sql
-- 启用查询日志
-- postgresql.conf:
-- log_statement = 'all'
-- log_duration = on

-- 或使用pg_stat_statements
SELECT
    query,
    calls,
    total_exec_time
FROM pg_stat_statements
WHERE query LIKE '%users WHERE id =%'
ORDER BY calls DESC;

-- 如果看到相同模式的查询被调用多次，可能是N+1问题
```

---

## 11. 案例9：大表全扫描

### 11.1 问题现象

```sql
-- 聚合查询慢（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法执行聚合查询';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试大表聚合查询（执行时间：120000ms，10亿行）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '聚合查询准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM large_table;
-- 执行时间：120000ms（2分钟），10亿行
```

### 11.2 解决方案

#### 方案1：使用统计信息估算

```sql
-- ❌ 慢：精确计数（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法执行精确计数';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试精确计数（慢）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '精确计数准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM large_table;

-- ✅ 快：估算（误差约2-5%，带错误处理和性能测试）
DO $$
DECLARE
    estimate_count BIGINT;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法估算行数';
            RETURN;
        END IF;

        SELECT reltuples::bigint INTO estimate_count
        FROM pg_class
        WHERE relname = 'large_table';

        IF estimate_count IS NULL THEN
            RAISE WARNING '无法获取表 large_table 的行数估算，可能需要运行ANALYZE';
        ELSE
            RAISE NOTICE '表 large_table 估算行数: %', estimate_count;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '估算行数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'large_table';

-- 执行时间：1ms
```

#### 方案2：缓存计数器

```sql
-- 创建计数器表（带错误处理）
DO $$
BEGIN
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'table_counters') THEN
            RAISE NOTICE '表 table_counters 已存在';
        ELSE
            CREATE TABLE table_counters (
                table_name TEXT PRIMARY KEY,
                count BIGINT NOT NULL,
                updated_at TIMESTAMPTZ DEFAULT NOW()
            );
            RAISE NOTICE '计数器表 table_counters 创建成功';
        END IF;
    EXCEPTION
        WHEN duplicate_table THEN
            RAISE WARNING '表 table_counters 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建计数器表失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 触发器维护计数（带完整错误处理）
CREATE OR REPLACE FUNCTION update_large_table_count()
RETURNS TRIGGER AS $$
BEGIN
    BEGIN
        IF TG_OP = 'INSERT' THEN
            INSERT INTO table_counters (table_name, count)
            VALUES ('large_table', 1)
            ON CONFLICT (table_name) DO UPDATE
            SET count = table_counters.count + 1, updated_at = NOW();
        ELSIF TG_OP = 'DELETE' THEN
            UPDATE table_counters
            SET count = count - 1, updated_at = NOW()
            WHERE table_name = 'large_table';
        END IF;
        RETURN NULL;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '更新计数器失败: %', SQLERRM;
            RETURN NULL;
    END;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器（带错误处理）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table') THEN
            RAISE WARNING '表 large_table 不存在，无法创建触发器';
            RETURN;
        END IF;

        IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'large_table_count_trigger') THEN
            RAISE WARNING '触发器 large_table_count_trigger 已存在';
        ELSE
            CREATE TRIGGER large_table_count_trigger
            AFTER INSERT OR DELETE ON large_table
            FOR EACH ROW EXECUTE FUNCTION update_large_table_count();
            RAISE NOTICE '触发器 large_table_count_trigger 创建成功';
        END IF;
    EXCEPTION
        WHEN undefined_table THEN
            RAISE WARNING '表 large_table 不存在';
        WHEN undefined_function THEN
            RAISE WARNING '函数 update_large_table_count 不存在，请先创建函数';
        WHEN duplicate_object THEN
            RAISE WARNING '触发器 large_table_count_trigger 已存在';
        WHEN OTHERS THEN
            RAISE WARNING '创建触发器失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 查询计数（瞬间返回，带错误处理和性能测试）
DO $$
DECLARE
    counter_value BIGINT;
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'table_counters') THEN
            RAISE WARNING '表 table_counters 不存在，无法查询计数';
            RETURN;
        END IF;

        SELECT count INTO counter_value
        FROM table_counters
        WHERE table_name = 'large_table';

        IF counter_value IS NULL THEN
            RAISE WARNING '表 large_table 的计数器不存在，可能需要初始化';
        ELSE
            RAISE NOTICE '表 large_table 的计数: %', counter_value;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '查询计数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT count FROM table_counters WHERE table_name = 'large_table';
```

#### 方案3：分区+并行聚合

```sql
-- 对于必须精确计数的场景，使用分区+并行（带错误处理）
DO $$
DECLARE
    current_setting_val TEXT;
BEGIN
    BEGIN
        SELECT setting INTO current_setting_val
        FROM pg_settings
        WHERE name = 'max_parallel_workers_per_gather';

        IF current_setting_val IS NULL THEN
            RAISE WARNING '无法获取max_parallel_workers_per_gather设置';
        ELSE
            RAISE NOTICE '当前max_parallel_workers_per_gather: %', current_setting_val;
        END IF;

        SET max_parallel_workers_per_gather = 8;
        RAISE NOTICE 'max_parallel_workers_per_gather已设置为8';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置并行工作进程数失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：分区+并行计数（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'large_table_partitioned') THEN
            RAISE WARNING '表 large_table_partitioned 不存在，无法执行并行计数';
            RETURN;
        END IF;
        RAISE NOTICE '开始测试分区+并行计数（并行扫描多个分区，显著加速）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '并行计数准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM large_table_partitioned;
-- 并行扫描多个分区，显著加速
```

### 11.3 其他大表优化

```sql
-- 避免SELECT *
-- ❌ 坏
SELECT * FROM large_table LIMIT 1000;
-- 读取所有列，IO开销大

-- ✅ 好
SELECT id, name, created_at FROM large_table LIMIT 1000;
-- 只读取需要的列

-- 使用索引覆盖扫描
CREATE INDEX large_table_covering_idx ON large_table(status) INCLUDE (id, name);
SELECT id, name FROM large_table WHERE status = 'active';
-- Index Only Scan，不需要访问表
```

---

## 12. 案例10：复杂聚合优化

### 12.1 问题现象

```sql
-- 复杂统计查询慢
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders
WHERE created_at >= '2024-01-01'
GROUP BY DATE(created_at)
ORDER BY date;

-- 执行时间：25000ms
```

### 12.2 解决方案

#### 方案1：物化视图

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW daily_order_stats AS
SELECT
    DATE(created_at) AS date,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders
GROUP BY DATE(created_at);

CREATE INDEX daily_order_stats_date_idx ON daily_order_stats(date);

-- 定时刷新（cron job）
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_order_stats;

-- 查询物化视图（瞬间返回）
SELECT * FROM daily_order_stats
WHERE date >= '2024-01-01'
ORDER BY date;

-- 执行时间：15ms
```

#### 方案2：增量聚合

```sql
-- 创建聚合表（增量更新）
CREATE TABLE daily_order_stats_incremental (
    date DATE PRIMARY KEY,
    order_count BIGINT,
    total_amount DECIMAL(15,2),
    sum_amount DECIMAL(15,2),  -- 用于计算平均
    unique_users BIGINT
);

-- 触发器或定时任务增量更新（只处理新数据）
INSERT INTO daily_order_stats_incremental
SELECT
    DATE(created_at) AS date,
    COUNT(*),
    SUM(amount),
    SUM(amount),
    COUNT(DISTINCT user_id)
FROM orders
WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
  AND created_at < CURRENT_DATE
GROUP BY DATE(created_at)
ON CONFLICT (date) DO UPDATE
SET
    order_count = daily_order_stats_incremental.order_count + EXCLUDED.order_count,
    total_amount = daily_order_stats_incremental.total_amount + EXCLUDED.total_amount,
    sum_amount = daily_order_stats_incremental.sum_amount + EXCLUDED.sum_amount,
    unique_users = daily_order_stats_incremental.unique_users + EXCLUDED.unique_users;
```

#### 方案3：使用TimescaleDB连续聚合

```sql
-- 如果是时序数据，使用TimescaleDB
CREATE MATERIALIZED VIEW daily_order_stats_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', created_at) AS day,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM orders
GROUP BY day;

-- 自动增量更新（无需手动刷新）
SELECT add_continuous_aggregate_policy(
    'daily_order_stats_continuous',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);
```

---

## 13. 案例11：DISTINCT优化

### 13.1 问题现象

```sql
-- DISTINCT查询慢
SELECT DISTINCT user_id FROM orders;
-- 执行时间：15000ms（1亿行）
```

### 13.2 解决方案

```sql
-- 方案1：使用GROUP BY替代DISTINCT
-- GROUP BY通常比DISTINCT更快（可以使用索引）
SELECT user_id FROM orders GROUP BY user_id;

-- 方案2：使用EXISTS去重
-- 场景：查找有订单的用户
-- ❌ 慢
SELECT DISTINCT user_id FROM orders;

-- ✅ 快
SELECT id FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 方案3：位图索引（适用于低基数列）
CREATE INDEX orders_user_id_bitmap ON orders USING HASH (user_id);

-- 方案4：使用HyperLogLog估算（近似去重计数）
CREATE EXTENSION hll;

-- 创建HLL列
ALTER TABLE orders_daily_stats ADD COLUMN unique_users hll;

-- 增量更新
UPDATE orders_daily_stats
SET unique_users = hll_add(unique_users, hll_hash_integer(user_id))
FROM orders
WHERE orders.created_at = orders_daily_stats.date;

-- 查询去重计数（近似，误差<2%）
SELECT hll_cardinality(unique_users) FROM orders_daily_stats WHERE date = '2025-01-01';
```

---

## 14. 案例12：ORDER BY优化

### 14.1 问题现象

```sql
-- 排序查询慢
SELECT * FROM orders
WHERE status = 'completed'
ORDER BY created_at DESC
LIMIT 10;

-- 执行时间：8000ms
```

### 14.2 解决方案

```sql
-- 方案1：创建复合索引（过滤列 + 排序列）
CREATE INDEX orders_status_created_desc_idx
ON orders(status, created_at DESC);

EXPLAIN (ANALYZE)
SELECT * FROM orders
WHERE status = 'completed'
ORDER BY created_at DESC
LIMIT 10;

-- 输出：
-- Index Scan using orders_status_created_desc_idx on orders  (...)
--   Index Cond: (status = 'completed'::text)
-- Execution Time: 0.234 ms

-- 性能提升：8000ms → 0.2ms（40000倍！）

-- 方案2：仅索引扫描（Index Only Scan）
CREATE INDEX orders_status_created_id_idx
ON orders(status, created_at DESC) INCLUDE (id, amount);

SELECT id, amount FROM orders
WHERE status = 'completed'
ORDER BY created_at DESC
LIMIT 10;
-- Index Only Scan（不需要访问表）

-- 方案3：避免OFFSET大值
-- ❌ 坏：深度分页
SELECT * FROM orders
ORDER BY created_at DESC
LIMIT 10 OFFSET 100000;
-- 需要扫描100010行

-- ✅ 好：使用Keyset Pagination
SELECT * FROM orders
WHERE created_at < '2025-01-01 10:00:00'  -- 上一页的最后一条记录时间
ORDER BY created_at DESC
LIMIT 10;
```

---

## 15. 优化方法总结

### 15.1 诊断流程

```text
1. 识别慢查询
   - pg_stat_statements
   - 慢查询日志
   - 应用监控

2. 分析执行计划
   - EXPLAIN (ANALYZE, BUFFERS, TIMING)
   - 查看Seq Scan, Index Scan
   - 估算 vs 实际行数

3. 检查统计信息
   - pg_stat_user_tables
   - last_analyze时间
   - ANALYZE更新

4. 检查索引
   - pg_indexes
   - 缺失索引？
   - 索引未被使用？

5. 检查锁等待
   - pg_locks
   - pg_stat_activity
   - 长事务？

6. 应用解决方案
   - 创建/优化索引
   - 重写SQL
   - 配置调整

7. 验证效果
   - EXPLAIN (ANALYZE, BUFFERS, TIMING)对比
   - 生产监控
```

### 15.2 优化技巧速查表

| 问题 | 症状 | 解决方案 |
| --- | --- | --- |
| **缺失索引** | Seq Scan | 创建索引 |
| **索引未使用** | Seq Scan（有索引）| 复合索引、更新统计 |
| **JOIN慢** | Hash Join, Nested Loop | JOIN列索引、过滤后JOIN |
| **子查询慢** | 重复执行 | 改写为JOIN或EXISTS |
| **大表全扫描** | COUNT(*)慢 | 估算、计数器、分区 |
| **聚合慢** | 重复计算 | 物化视图、连续聚合 |
| **排序慢** | Sort in query plan | 复合索引（过滤+排序） |
| **N+1问题** | 大量相似查询 | JOIN、IN查询、预加载 |
| **锁等待** | idle in transaction | 缩短事务、SKIP LOCKED |
| **统计过期** | 估算偏差大 | ANALYZE |
| **分区未裁剪** | 扫描所有分区 | 查询包含分区键过滤 |
| **DISTINCT慢** | Sort + Unique | GROUP BY、EXISTS、HLL |

### 15.3 索引设计最佳实践

```sql
-- 1. 单列索引：WHERE、JOIN、ORDER BY常用列
CREATE INDEX users_email_idx ON users(email);

-- 2. 复合索引：多列查询，精确匹配在前
CREATE INDEX orders_user_status_created_idx
ON orders(user_id, status, created_at DESC);

-- 3. 部分索引：只索引部分数据
CREATE INDEX orders_pending_idx ON orders(user_id)
WHERE status = 'pending';

-- 4. 表达式索引：查询使用函数
CREATE INDEX users_lower_email_idx ON users(LOWER(email));

-- 5. 覆盖索引：INCLUDE非索引列
CREATE INDEX orders_user_created_idx
ON orders(user_id, created_at) INCLUDE (amount, status);

-- 6. 唯一索引：强制唯一性+加速查询
CREATE UNIQUE INDEX users_email_unique_idx ON users(email);

-- 7. 并发创建：不锁表
CREATE INDEX CONCURRENTLY orders_status_idx ON orders(status);

-- 8. 删除无用索引
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 15.4 配置优化参考

```sql
-- postgresql.conf关键配置

-- 内存
shared_buffers = 4GB                  -- 25% of RAM
effective_cache_size = 12GB           -- 75% of RAM
work_mem = 64MB                       -- 根据并发调整
maintenance_work_mem = 1GB

-- 查询优化
random_page_cost = 1.1                -- SSD使用1.1，HDD使用4
effective_io_concurrency = 200        -- SSD可以更高
default_statistics_target = 100       -- 复杂查询可增加到500

-- 并行查询
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_tuple_cost = 0.01

-- WAL
wal_buffers = 16MB
checkpoint_completion_target = 0.9

-- 连接
max_connections = 200
```

---

## 📚 延伸阅读

- [PostgreSQL Execution Plan Visualization](https://explain.depesz.com/)
- [pg_stat_statements Documentation](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [Use The Index, Luke!](https://use-the-index-luke.com/)

---

## ✅ 学习检查清单

- [ ] 掌握pg_stat_statements使用
- [ ] 能够阅读EXPLAIN (ANALYZE, BUFFERS, TIMING)输出
- [ ] 理解索引类型和使用场景
- [ ] 能够识别N+1查询问题
- [ ] 掌握JOIN优化技巧
- [ ] 理解锁机制和死锁排查
- [ ] 能够设计分区策略
- [ ] 掌握物化视图使用
- [ ] 能够进行系统级性能调优

---

**文档维护**: 本文档持续更新以补充新的案例。
**反馈**: 如有更多优化案例，欢迎贡献。

**版本历史**:

- v1.0 (2025-01): 初始版本，包含12个核心优化案例

```
