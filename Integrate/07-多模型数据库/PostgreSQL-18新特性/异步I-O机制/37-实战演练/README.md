# 31. 实战演练教程

> **章节编号**: 37
> **章节标题**: 实战演练教程
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 37. 实战演练教程

## 📑 目录

- [37.2 从零开始配置异步I/O](#372-从零开始配置异步io)
- [37.3 完整性能测试演练](#373-完整性能测试演练)
- [37.4 实际应用场景演练](#374-实际应用场景演练)
- [37.5 问题排查演练](#375-问题排查演练)

---

---

### 37.2 从零开始配置异步I/O

#### 31.2.1 第一步：备份当前配置

**备份配置文件**:

```bash
# 找到PostgreSQL配置文件位置
psql -U postgres -c "SHOW config_file;"

# 备份配置文件（假设配置文件在/etc/postgresql/18/main/postgresql.conf）
sudo cp /etc/postgresql/18/main/postgresql.conf \
        /etc/postgresql/18/main/postgresql.conf.backup.$(date +%Y%m%d_%H%M%S)
```

#### 31.2.2 第二步：配置异步I/O参数

**编辑配置文件**:

```bash
# 编辑PostgreSQL配置文件
sudo nano /etc/postgresql/18/main/postgresql.conf
```

**添加或修改以下参数**:

```ini
# ============================================
# PostgreSQL 18异步I/O配置
# ============================================

# 启用直接I/O（绕过OS缓存，直接访问存储设备）
io_direct = 'data,wal'

# I/O并发度配置（根据存储类型调整）
# SSD/NVMe: 200-400
# SATA SSD: 100-200
# HDD: 50-100
effective_io_concurrency = 200

# WAL I/O并发度
wal_io_concurrency = 150

# io_uring队列深度（可选，默认256）
io_uring_queue_depth = 512

# 维护操作I/O并发度
maintenance_io_concurrency = 200
```

**保存并重新加载配置**:

```bash
# 重新加载配置（无需重启）
sudo systemctl reload postgresql

# 或使用PostgreSQL命令
psql -U postgres -c "SELECT pg_reload_conf();"
```

#### 31.2.3 第三步：验证配置

**验证脚本** (`verify_config.sh`):

```bash
#!/bin/bash
# 验证异步I/O配置脚本

echo "=== 验证异步I/O配置 ==="
echo ""

psql -U postgres -c "
SELECT
    name,
    setting,
    unit,
    source
FROM pg_settings
WHERE name IN (
    'io_direct',
    'effective_io_concurrency',
    'wal_io_concurrency',
    'io_uring_queue_depth',
    'maintenance_io_concurrency'
)
ORDER BY name;
"

echo ""
echo "=== 验证结果 ==="
IO_DIRECT=$(psql -t -c "SELECT setting FROM pg_settings WHERE name = 'io_direct';" | xargs)
if [ "$IO_DIRECT" == "data,wal" ] || [ "$IO_DIRECT" == "on" ]; then
    echo "✓ io_direct已启用: $IO_DIRECT"
else
    echo "✗ io_direct未正确配置: $IO_DIRECT"
fi

EFFECTIVE_IO=$(psql -t -c "SELECT setting FROM pg_settings WHERE name = 'effective_io_concurrency';" | xargs)
if [ "$EFFECTIVE_IO" -ge 50 ]; then
    echo "✓ effective_io_concurrency已配置: $EFFECTIVE_IO"
else
    echo "⚠ effective_io_concurrency可能过低: $EFFECTIVE_IO"
fi
```

**运行验证**:

```bash
chmod +x verify_config.sh
./verify_config.sh
```

---

### 37.3 完整性能测试演练

#### 31.3.1 测试准备

**创建测试数据库和表**:

```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建测试数据库
CREATE DATABASE aio_test;
\c aio_test

-- 创建测试表
CREATE TABLE test_table (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入测试数据（100万行）
INSERT INTO test_table (data)
SELECT 'Test data ' || generate_series(1, 1000000);

-- 创建索引
CREATE INDEX idx_test_table_created_at ON test_table(created_at);

-- 更新统计信息
ANALYZE test_table;
```

#### 31.3.2 性能测试脚本

**完整性能测试脚本** (`performance_test.sh`):

```bash
#!/bin/bash
# PostgreSQL 18异步I/O性能测试脚本

DB_NAME="aio_test"
TEST_ROWS=1000000

echo "=== PostgreSQL 18异步I/O性能测试 ==="
echo ""

# 1. 全表扫描测试
echo "[1/4] 全表扫描测试..."
echo "执行: SELECT COUNT(*) FROM test_table;"
time psql -U postgres -d $DB_NAME -c "SELECT COUNT(*) FROM test_table;" > /dev/null

# 2. 批量插入测试
echo ""
echo "[2/4] 批量插入测试..."
echo "执行: INSERT INTO test_table (data) SELECT 'New data ' || generate_series(1, 10000);"
time psql -U postgres -d $DB_NAME -c "
INSERT INTO test_table (data)
SELECT 'New data ' || generate_series(1, 10000);
" > /dev/null

# 3. 索引扫描测试
echo ""
echo "[3/4] 索引扫描测试..."
echo "执行: SELECT * FROM test_table WHERE created_at > NOW() - INTERVAL '1 day' LIMIT 1000;"
time psql -U postgres -d $DB_NAME -c "
SELECT * FROM test_table
WHERE created_at > NOW() - INTERVAL '1 day'
LIMIT 1000;
" > /dev/null

# 4. 并发查询测试
echo ""
echo "[4/4] 并发查询测试..."
echo "执行: 10个并发查询"
for i in {1..10}; do
    psql -U postgres -d $DB_NAME -c "SELECT COUNT(*) FROM test_table WHERE id < 100000;" > /dev/null &
done
wait

echo ""
echo "=== 性能测试完成 ==="
```

**运行测试**:

```bash
chmod +x performance_test.sh
./performance_test.sh
```

#### 31.3.3 性能对比测试

**对比同步I/O和异步I/O性能** (`compare_performance.sh`):

```bash
#!/bin/bash
# 对比同步I/O和异步I/O性能

DB_NAME="aio_test"

echo "=== 性能对比测试 ==="
echo ""

# 测试1: 同步I/O
echo "[测试1] 同步I/O配置..."
psql -U postgres -c "ALTER SYSTEM SET io_direct = 'off';"
psql -U postgres -c "ALTER SYSTEM SET effective_io_concurrency = 1;"
psql -U postgres -c "SELECT pg_reload_conf();"
sleep 2

echo "执行全表扫描..."
SYNC_TIME=$(time (psql -U postgres -d $DB_NAME -c "SELECT COUNT(*) FROM test_table;" > /dev/null) 2>&1 | grep real | awk '{print $2}')

# 测试2: 异步I/O
echo ""
echo "[测试2] 异步I/O配置..."
psql -U postgres -c "ALTER SYSTEM SET io_direct = 'data,wal';"
psql -U postgres -c "ALTER SYSTEM SET effective_io_concurrency = 200;"
psql -U postgres -c "SELECT pg_reload_conf();"
sleep 2

echo "执行全表扫描..."
ASYNC_TIME=$(time (psql -U postgres -d $DB_NAME -c "SELECT COUNT(*) FROM test_table;" > /dev/null) 2>&1 | grep real | awk '{print $2}')

# 显示结果
echo ""
echo "=== 性能对比结果 ==="
echo "同步I/O时间: $SYNC_TIME"
echo "异步I/O时间: $ASYNC_TIME"
echo ""
echo "性能提升: 请手动计算提升百分比"
```

---

### 37.4 实际应用场景演练

#### 31.4.1 场景1：RAG应用优化

**步骤1：创建向量表**

```sql
-- 安装pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建文档表
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建向量索引
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
```

**步骤2：批量插入文档**

```python
#!/usr/bin/env python3
# RAG应用批量插入脚本

import psycopg2
import numpy as np
from pgvector.psycopg2 import register_vector

# 连接数据库
conn = psycopg2.connect(
    host="localhost",
    database="aio_test",
    user="postgres"
)
register_vector(conn)

cur = conn.cursor()

# 批量插入文档（利用异步I/O）
batch_size = 1000
total_docs = 10000

for i in range(0, total_docs, batch_size):
    batch = []
    for j in range(batch_size):
        doc_id = i + j
        content = f"Document {doc_id} content"
        embedding = np.random.rand(1536).tolist()
        metadata = {"doc_id": doc_id, "category": "test"}
        batch.append((content, embedding, metadata))

    # 批量插入
    cur.executemany(
        "INSERT INTO documents (content, embedding, metadata) VALUES (%s, %s::vector, %s)",
        batch
    )
    conn.commit()
    print(f"已插入 {i + batch_size} 个文档")

cur.close()
conn.close()
print("批量插入完成")
```

**步骤3：向量搜索测试**

```sql
-- 向量相似度搜索
SELECT
    id,
    content,
    metadata,
    1 - (embedding <=> '[0.1,0.2,...]'::vector) AS similarity
FROM documents
ORDER BY embedding <=> '[0.1,0.2,...]'::vector
LIMIT 10;
```

#### 31.4.2 场景2：IoT数据写入优化

**步骤1：创建时序表**

```sql
-- 创建IoT设备数据表
CREATE TABLE iot_sensors (
    device_id VARCHAR(50),
    sensor_type VARCHAR(50),
    value DOUBLE PRECISION,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- 创建分区表（按月分区）
CREATE TABLE iot_sensors_2025_01 PARTITION OF iot_sensors
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- 创建索引
CREATE INDEX ON iot_sensors (device_id, timestamp);
CREATE INDEX ON iot_sensors USING GIN (metadata);
```

**步骤2：批量写入脚本**

```python
#!/usr/bin/env python3
# IoT数据批量写入脚本

import psycopg2
import random
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host="localhost",
    database="aio_test",
    user="postgres"
)

cur = conn.cursor()

# 批量写入IoT数据
batch_size = 5000
devices = ['device_001', 'device_002', 'device_003']
sensor_types = ['temperature', 'humidity', 'pressure']

for batch_num in range(10):
    batch = []
    base_time = datetime.now() - timedelta(hours=batch_num)

    for i in range(batch_size):
        device_id = random.choice(devices)
        sensor_type = random.choice(sensor_types)
        value = random.uniform(0, 100)
        timestamp = base_time + timedelta(seconds=i)
        metadata = {
            "location": f"room_{random.randint(1, 10)}",
            "status": "active"
        }
        batch.append((device_id, sensor_type, value, timestamp, metadata))

    # 批量插入
    cur.executemany(
        """INSERT INTO iot_sensors
           (device_id, sensor_type, value, timestamp, metadata)
           VALUES (%s, %s, %s, %s, %s)""",
        batch
    )
    conn.commit()
    print(f"批次 {batch_num + 1}/10 完成")

cur.close()
conn.close()
print("IoT数据写入完成")
```

---

### 37.5 问题排查演练

#### 31.5.1 问题1：异步I/O未生效

**症状**:

- 配置了`io_direct = 'data,wal'`，但性能没有提升

**排查步骤**:

```bash
# 步骤1：检查配置是否生效
psql -U postgres -c "SHOW io_direct;"
psql -U postgres -c "SHOW effective_io_concurrency;"

# 步骤2：检查I/O统计
psql -U postgres -c "
SELECT
    context,
    reads,
    writes,
    read_time,
    write_time
FROM pg_stat_io
WHERE context = 'normal';

"

# 步骤3：检查系统I/O
iostat -x 1 5

# 步骤4：检查PostgreSQL日志
sudo tail -n 100 /var/log/postgresql/postgresql-18-main.log | grep -i "io\|uring"
```

**解决方案**:

```sql
-- 如果io_direct未生效，检查是否有权限问题
-- 确保PostgreSQL进程有直接I/O权限

-- 重新加载配置
SELECT pg_reload_conf();

-- 验证配置
SELECT name, setting, source
FROM pg_settings
WHERE name LIKE '%io%'
ORDER BY name;
```

#### 31.5.2 问题2：性能反而下降

**症状**:

- 启用异步I/O后，查询性能反而变慢

**排查步骤**:

```bash
# 步骤1：检查I/O并发度是否过高
psql -U postgres -c "SHOW effective_io_concurrency;"

# 步骤2：检查系统资源使用情况
top
iostat -x 1 5
vmstat 1 5

# 步骤3：检查是否有I/O竞争
psql -U postgres -c "
SELECT
    pid,
    wait_event_type,
    wait_event,

    state
FROM pg_stat_activity
WHERE wait_event_type = 'IO';
"
```

**解决方案**:

```sql
-- 降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();

-- 或根据存储类型调整
-- SSD: 200-400
-- HDD: 50-100
```

#### 31.5.3 问题3：系统资源耗尽

**症状**:

- 启用异步I/O后，系统CPU或内存使用率过高

**排查步骤**:

```bash
# 步骤1：检查CPU使用率
top -p $(pgrep -f postgres | head -1)

# 步骤2：检查内存使用
ps aux | grep postgres

# 步骤3：检查文件描述符
lsof -p $(pgrep -f postgres | head -1) | wc -l

# 步骤4：检查io_uring队列深度
psql -U postgres -c "SHOW io_uring_queue_depth;"
```

**解决方案**:

```sql
-- 降低io_uring队列深度
ALTER SYSTEM SET io_uring_queue_depth = 256;
SELECT pg_reload_conf();

-- 降低I/O并发度
ALTER SYSTEM SET effective_io_concurrency = 100;
SELECT pg_reload_conf();
```

---

---

**返回**: [文档首页](../README.md) | [上一章节](../31-实用工具/README.md) | [下一章节](../32-错误解决方案/README.md)
