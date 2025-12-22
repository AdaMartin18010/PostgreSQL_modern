#!/usr/bin/env python3
"""
性能测试模板生成工具

功能:
1. 生成PostgreSQL异步I/O性能测试SQL脚本
2. 生成测试报告模板
3. 生成性能对比分析模板

使用方法:
    python generate_performance_test_template.py --output test_scripts/
"""

import os
from pathlib import Path
import argparse


def generate_aio_performance_test():
    """生成异步I/O性能测试SQL脚本"""

    script = """-- PostgreSQL 18 异步I/O性能测试脚本
-- 测试场景: 全表扫描、批量写入、并发连接

-- ============================================
-- 测试环境准备
-- ============================================

-- 1. 检查异步I/O是否启用
SHOW max_parallel_workers_per_gather;
SHOW maintenance_io_concurrency;
SHOW wal_io_concurrency;

-- 2. 创建测试表
DROP TABLE IF EXISTS test_aio_performance;
CREATE TABLE test_aio_performance (
    id BIGSERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 插入测试数据（1GB）
INSERT INTO test_aio_performance (data)
SELECT md5(random()::text) || repeat('x', 1000)
FROM generate_series(1, 1000000);

-- 4. 创建索引
CREATE INDEX idx_test_aio_created ON test_aio_performance(created_at);
CREATE INDEX idx_test_aio_updated ON test_aio_performance(updated_at);

-- ============================================
-- 测试1: 全表扫描性能测试
-- ============================================

-- 测试1.1: 同步I/O全表扫描
SET maintenance_io_concurrency = 0;  -- 禁用异步I/O
\\timing on
SELECT COUNT(*) FROM test_aio_performance;
\\timing off

-- 测试1.2: 异步I/O全表扫描
SET maintenance_io_concurrency = 10;  -- 启用异步I/O
\\timing on
SELECT COUNT(*) FROM test_aio_performance;
\\timing off

-- 测试1.3: 不同并发度测试
DO $$
DECLARE
    i INTEGER;
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration INTERVAL;
BEGIN
    FOR i IN 1..16 LOOP
        SET maintenance_io_concurrency = i;
        start_time := clock_timestamp();
        PERFORM COUNT(*) FROM test_aio_performance;
        end_time := clock_timestamp();
        duration := end_time - start_time;
        RAISE NOTICE '并发度: %, 耗时: %', i, duration;
    END LOOP;
END $$;

-- ============================================
-- 测试2: 批量写入性能测试
-- ============================================

-- 测试2.1: 同步I/O批量写入
SET maintenance_io_concurrency = 0;
\\timing on
INSERT INTO test_aio_performance (data)
SELECT md5(random()::text) || repeat('x', 1000)
FROM generate_series(1, 100000);
\\timing off

-- 测试2.2: 异步I/O批量写入
SET maintenance_io_concurrency = 10;
\\timing on
INSERT INTO test_aio_performance (data)
SELECT md5(random()::text) || repeat('x', 1000)
FROM generate_series(1, 100000);
\\timing off

-- 测试2.3: COPY性能测试
SET maintenance_io_concurrency = 0;
\\timing on
COPY test_aio_performance (data) FROM STDIN;
-- (需要准备CSV文件)
\\timing off

SET maintenance_io_concurrency = 10;
\\timing on
COPY test_aio_performance (data) FROM STDIN;
-- (需要准备CSV文件)
\\timing off

-- ============================================
-- 测试3: 并发连接性能测试
-- ============================================

-- 测试3.1: 单连接性能
SET maintenance_io_concurrency = 10;
\\timing on
SELECT * FROM test_aio_performance WHERE id BETWEEN 1 AND 10000;
\\timing off

-- 测试3.2: 多连接并发测试（需要在多个会话中执行）
-- 连接1
SET maintenance_io_concurrency = 10;
SELECT * FROM test_aio_performance WHERE id BETWEEN 1 AND 10000;

-- 连接2
SET maintenance_io_concurrency = 10;
SELECT * FROM test_aio_performance WHERE id BETWEEN 10001 AND 20000;

-- 连接3
SET maintenance_io_concurrency = 10;
SELECT * FROM test_aio_performance WHERE id BETWEEN 20001 AND 30000;

-- ============================================
-- 性能监控查询
-- ============================================

-- 1. 查看I/O统计
SELECT
    datname,
    blk_read_time,
    blk_write_time,
    stats_reset
FROM pg_stat_database
WHERE datname = current_database();

-- 2. 查看表I/O统计
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE tablename = 'test_aio_performance';

-- 3. 查看索引I/O统计
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'test_aio_performance';

-- ============================================
-- 清理测试数据
-- ============================================

DROP TABLE IF EXISTS test_aio_performance;
"""

    return script


def generate_test_report_template():
    """生成测试报告模板"""

    template = """# PostgreSQL 18 异步I/O性能测试报告

## 测试环境

- **PostgreSQL版本**: 18.x
- **操作系统**:
- **硬件配置**:
- **测试时间**:

## 测试配置

### 同步I/O配置
```sql
maintenance_io_concurrency = 0
wal_io_concurrency = 0
```

### 异步I/O配置
```sql
maintenance_io_concurrency = 10
wal_io_concurrency = 10
```

## 测试结果

### 1. 全表扫描性能测试

| 数据量 | 同步I/O耗时 | 异步I/O耗时 | 性能提升 | 提升百分比 |
|--------|------------|------------|---------|-----------|
| 1GB    |            |            |         |           |
| 10GB   |            |            |         |           |
| 100GB  |            |            |         |           |

### 2. 批量写入性能测试

| 操作类型 | 数据量 | 同步I/O耗时 | 异步I/O耗时 | 性能提升 | 提升百分比 |
|---------|--------|------------|------------|---------|-----------|
| INSERT  | 10万   |            |            |         |           |
| INSERT  | 100万  |            |            |         |           |
| COPY    | 10万   |            |            |         |           |
| COPY    | 100万  |            |            |         |           |

### 3. 并发连接性能测试

| 并发连接数 | 同步I/O吞吐量 | 异步I/O吞吐量 | 性能提升 | 提升百分比 |
|-----------|--------------|--------------|---------|-----------|
| 1         |              |              |         |           |
| 4         |              |              |         |           |
| 8         |              |              |         |           |
| 16        |              |              |         |           |

## 性能分析

### 关键发现

1.
2.
3.

### 优化建议

1.
2.
3.

## 结论

"""

    return template


def main():
    parser = argparse.ArgumentParser(description='性能测试模板生成工具')
    parser.add_argument('--output', type=str, default='test_scripts', help='输出目录')

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成测试SQL脚本
    test_script = generate_aio_performance_test()
    (output_dir / 'aio_performance_test.sql').write_text(test_script, encoding='utf-8')
    print(f"✅ 已生成测试SQL脚本: {output_dir / 'aio_performance_test.sql'}")

    # 生成测试报告模板
    report_template = generate_test_report_template()
    (output_dir / 'performance_test_report_template.md').write_text(report_template, encoding='utf-8')
    print(f"✅ 已生成测试报告模板: {output_dir / 'performance_test_report_template.md'}")

    print("\n✅ 所有模板已生成完成！")
    print(f"📁 输出目录: {output_dir}")


if __name__ == '__main__':
    main()
