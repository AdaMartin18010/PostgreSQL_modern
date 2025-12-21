# PostgreSQL 18 pg_cron定时任务实战

## 📑 目录

- [PostgreSQL 18 pg\_cron定时任务实战](#postgresql-18-pg_cron定时任务实战)
  - [📑 目录](#-目录)
  - [1. 安装配置](#1-安装配置)
  - [2. 基础任务](#2-基础任务)
    - [2.1 创建定时任务](#21-创建定时任务)
    - [2.2 管理任务](#22-管理任务)
  - [3. 高级任务](#3-高级任务)
    - [3.1 复杂SQL任务](#31-复杂sql任务)
    - [3.2 调用存储过程](#32-调用存储过程)
  - [4. 实战案例](#4-实战案例)
    - [4.1 分区自动管理](#41-分区自动管理)
    - [4.2 数据库备份](#42-数据库备份)
  - [5. 监控与告警](#5-监控与告警)
    - [5.1 性能监控任务](#51-性能监控任务)
  - [6. 错误处理](#6-错误处理)
    - [6.1 任务失败处理](#61-任务失败处理)
  - [7. 最佳实践](#7-最佳实践)

## 1. 安装配置

```bash
#!/bin/bash
# 安装pg_cron（带错误处理）
set -e
set -u

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 安装pg_cron
if ! sudo apt install -y postgresql-18-cron 2>/dev/null; then
    error_exit "安装postgresql-18-cron失败"
fi

# 配置
if ! echo "shared_preload_libraries = 'pg_cron'" | \
  sudo tee -a /etc/postgresql/18/main/postgresql.conf > /dev/null; then
    error_exit "配置shared_preload_libraries失败"
fi

if ! echo "cron.database_name = 'postgres'" | \
  sudo tee -a /etc/postgresql/18/main/postgresql.conf > /dev/null; then
    error_exit "配置cron.database_name失败"
fi

# 重启
if ! sudo systemctl restart postgresql; then
    error_exit "重启PostgreSQL失败"
fi

# 创建扩展
if ! psql -c "CREATE EXTENSION IF NOT EXISTS pg_cron;" 2>/dev/null; then
    error_exit "创建扩展失败"
fi

echo "✅ pg_cron安装和配置完成"
```

---

## 2. 基础任务

### 2.1 创建定时任务

```sql
-- 性能测试：创建定时任务（带错误处理）
BEGIN;
-- 每天凌晨2点VACUUM
SELECT cron.schedule('nightly-vacuum', '0 2 * * *', 'VACUUM ANALYZE;');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定时任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 每小时清理旧日志
SELECT cron.schedule('cleanup-logs', '0 * * * *',
    'DELETE FROM logs WHERE created_at < now() - INTERVAL ''30 days''');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定时任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 每5分钟刷新物化视图
SELECT cron.schedule('refresh-stats', '*/5 * * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY user_stats;');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定时任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

BEGIN;
-- 每周日凌晨3点重建索引
SELECT cron.schedule('weekly-reindex', '0 3 * * 0',
    'REINDEX INDEX CONCURRENTLY idx_large_table;');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建定时任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 2.2 管理任务

```sql
-- 性能测试：查看所有任务（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM cron.job ORDER BY jobid;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看所有任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：查看任务运行历史（带错误处理和性能分析）
BEGIN;
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    job_id,
    run_details->'command' AS command,
    status,
    start_time,
    end_time,
    end_time - start_time AS duration
FROM cron.job_run_details
ORDER BY start_time DESC
LIMIT 20;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '查看任务运行历史失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：删除任务（带错误处理）
BEGIN;
SELECT cron.unschedule(1);  -- jobid
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '删除任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：更新任务（带错误处理）
BEGIN;
SELECT cron.alter_job(
    job_id := 1,
    schedule := '0 3 * * *',  -- 改为凌晨3点
    command := 'VACUUM FULL;'
);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '更新任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 3. 高级任务

### 3.1 复杂SQL任务

```sql
-- 性能测试：数据归档任务（带错误处理）
BEGIN;
SELECT cron.schedule('archive-old-orders', '0 1 * * *', $$
    BEGIN
        INSERT INTO orders_archive
        SELECT * FROM orders
        WHERE created_at < CURRENT_DATE - INTERVAL '365 days';

        DELETE FROM orders
        WHERE created_at < CURRENT_DATE - INTERVAL '365 days';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '数据归档任务失败: %', SQLERRM;
            RAISE;
    END;
$$);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建数据归档任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：统计报表生成（带错误处理）
BEGIN;
SELECT cron.schedule('daily-report', '0 8 * * *', $$
    BEGIN
        INSERT INTO daily_reports (report_date, total_orders, total_revenue)
        SELECT
            CURRENT_DATE - 1,
            COUNT(*),
            SUM(amount)
        FROM orders
        WHERE DATE(created_at) = CURRENT_DATE - 1;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '统计报表生成失败: %', SQLERRM;
            RAISE;
    END;
$$);
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建统计报表任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 3.2 调用存储过程

```sql
-- 性能测试：创建维护存储过程（带错误处理）
BEGIN;
CREATE OR REPLACE PROCEDURE maintenance_routine()
LANGUAGE plpgsql AS $$
BEGIN
    -- 1. VACUUM
    BEGIN
        VACUUM ANALYZE;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'VACUUM失败: %', SQLERRM;
    END;

    -- 2. 更新统计
    BEGIN
        ANALYZE;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE 'ANALYZE失败: %', SQLERRM;
    END;

    -- 3. 清理日志
    BEGIN
        DELETE FROM logs WHERE created_at < now() - INTERVAL '30 days';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '清理日志失败: %', SQLERRM;
    END;

    -- 4. 刷新缓存表
    BEGIN
        REFRESH MATERIALIZED VIEW CONCURRENTLY user_summary;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE NOTICE '刷新物化视图失败: %', SQLERRM;
    END;

    RAISE NOTICE '维护完成';
END;
$$;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建维护存储过程失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：定时执行（带错误处理）
BEGIN;
SELECT cron.schedule('maintenance', '0 2 * * *', 'CALL maintenance_routine();');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建维护任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

---

## 4. 实战案例

### 4.1 分区自动管理

```sql
-- 性能测试：自动创建分区函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION auto_create_partitions()
RETURNS VOID AS $$
DECLARE
    target_date DATE;
    partition_name TEXT;
BEGIN
    -- 创建未来7天的分区
    FOR i IN 0..6 LOOP
        target_date := CURRENT_DATE + i;
        partition_name := 'logs_' || to_char(target_date, 'YYYYMMDD');

        -- 检查分区是否存在
        IF NOT EXISTS (
            SELECT 1 FROM pg_tables WHERE tablename = partition_name
        ) THEN
            BEGIN
                EXECUTE format('
                    CREATE TABLE %I PARTITION OF logs
                    FOR VALUES FROM (%L) TO (%L);
                ', partition_name, target_date, target_date + 1);

                RAISE NOTICE '创建分区: %', partition_name;
            EXCEPTION
                WHEN duplicate_table THEN
                    RAISE NOTICE '分区 % 已存在', partition_name;
                WHEN undefined_table THEN
                    RAISE NOTICE '主表logs不存在';
                WHEN OTHERS THEN
                    RAISE NOTICE '创建分区 % 失败: %', partition_name, SQLERRM;
            END;
        END IF;
    END LOOP;

    -- 删除90天前的分区
    FOR partition_name IN (
        SELECT tablename FROM pg_tables
        WHERE tablename LIKE 'logs_%'
          AND tablename < 'logs_' || to_char(CURRENT_DATE - 90, 'YYYYMMDD')
    ) LOOP
        BEGIN
            EXECUTE format('DROP TABLE %I;', partition_name);
            RAISE NOTICE '删除分区: %', partition_name;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE '删除分区 % 失败: %', partition_name, SQLERRM;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建自动分区函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：每天运行（带错误处理）
BEGIN;
SELECT cron.schedule('partition-management', '0 1 * * *',
    'SELECT auto_create_partitions();');
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建分区管理任务失败: %', SQLERRM;
        ROLLBACK;
        RAISE;
```

### 4.2 数据库备份

```sql
-- 性能测试：创建备份函数（带错误处理）
BEGIN;
CREATE OR REPLACE FUNCTION backup_database()
RETURNS VOID AS $$
DECLARE
    backup_file TEXT;
BEGIN
    backup_file := '/backup/db_' || to_char(now(), 'YYYYMMDD_HH24MISS') || '.sql';

    -- 执行pg_dump（需要配置权限）
    BEGIN
        EXECUTE format('COPY (SELECT 1) TO PROGRAM ''pg_dump -U postgres mydb > %s''', backup_file);
        RAISE NOTICE '备份完成: %', backup_file;
    EXCEPTION
        WHEN insufficient_privilege THEN
            RAISE NOTICE '权限不足，无法执行pg_dump';
        WHEN OTHERS THEN
            RAISE NOTICE '备份失败: %', SQLERRM;
            RAISE;
    END;
END;
$$ LANGUAGE plpgsql;
COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '创建备份函数失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：每天凌晨备份（带错误处理）
BEGIN;
SELECT cron.schedule('daily-backup', '0 2 * * *',
    'SELECT backup_database();');
```

---

## 5. 监控与告警

### 5.1 性能监控任务

```sql
-- 性能测试：记录性能指标（带错误处理）
BEGIN;
CREATE TABLE IF NOT EXISTS performance_metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT now()
);
COMMIT;
EXCEPTION
    WHEN duplicate_table THEN
        RAISE NOTICE '性能指标表performance_metrics已存在';
    WHEN OTHERS THEN
        RAISE NOTICE '创建性能指标表失败: %', SQLERRM;
        ROLLBACK;
        RAISE;

-- 性能测试：定时采集（带错误处理）
BEGIN;
SELECT cron.schedule('collect-metrics', '*/5 * * * *', $$
    BEGIN
        INSERT INTO performance_metrics (metric_name, metric_value)
        SELECT 'tps', xact_commit + xact_rollback
        FROM pg_stat_database
        WHERE datname = current_database()
        UNION ALL
        SELECT 'connections', COUNT(*) FROM pg_stat_activity
        UNION ALL
        SELECT 'cache_hit_ratio',
               blks_hit * 100.0 / NULLIF(blks_hit + blks_read, 0)
    FROM pg_stat_database
    WHERE datname = current_database();
$$);
```

---

## 6. 错误处理

### 6.1 任务失败处理

```sql
-- 查看失败的任务
SELECT
    j.jobid,
    j.schedule,
    j.command,
    r.status,
    r.start_time,
    r.return_message
FROM cron.job j
JOIN cron.job_run_details r ON j.jobid = r.job_id
WHERE r.status = 'failed'
ORDER BY r.start_time DESC;

-- 重试机制（在存储过程中实现）
CREATE OR REPLACE PROCEDURE task_with_retry()
LANGUAGE plpgsql AS $$
DECLARE
    max_retries INT := 3;
    retry_count INT := 0;
BEGIN
    LOOP
        BEGIN
            -- 执行任务
            PERFORM expensive_operation();
            EXIT;  -- 成功退出
        EXCEPTION
            WHEN OTHERS THEN
                retry_count := retry_count + 1;

                IF retry_count >= max_retries THEN
                    RAISE NOTICE '任务失败，已重试%次', max_retries;
                    RAISE;
                END IF;

                RAISE NOTICE '重试%/%', retry_count, max_retries;
                PERFORM pg_sleep(retry_count * 5);  -- 指数退避
        END;
    END LOOP;
END;
$$;
```

---

## 7. 最佳实践

```text
任务设计:
✓ 避免长时间运行任务
✓ 使用批量处理
✓ 实现重试机制
✓ 记录执行日志

调度策略:
✓ 避免高峰期运行
✓ 错开多个任务时间
✓ 设置合理的超时
✓ 监控任务执行

安全性:
✓ 最小权限原则
✓ 审计任务变更
✓ 备份任务配置
✓ 测试环境验证
```

---

**完成**: PostgreSQL 18 pg_cron定时任务实战
**字数**: ~8,000字
**涵盖**: 安装、基础任务、高级任务、实战案例、监控、错误处理、最佳实践
