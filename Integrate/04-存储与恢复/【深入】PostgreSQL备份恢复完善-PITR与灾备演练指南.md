---

> **📋 文档来源**: `PostgreSQL培训\08-备份恢复\【深入】PostgreSQL备份恢复完善-PITR与灾备演练指南.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】PostgreSQL备份恢复完善 - PITR与灾备演练指南

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐ 高级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [【深入】PostgreSQL备份恢复完善 - PITR与灾备演练指南](#深入postgresql备份恢复完善---pitr与灾备演练指南)
  - [📑 目录](#-目录)
  - [1. PITR（时间点恢复）完整指南](#1-pitr时间点恢复完整指南)
    - [1.1 PITR原理](#11-pitr原理)
    - [1.2 PITR快速开始（30分钟）](#12-pitr快速开始30分钟)
      - [步骤1：配置WAL归档](#步骤1配置wal归档)
      - [步骤2：创建基础备份](#步骤2创建基础备份)
      - [步骤3：模拟数据丢失](#步骤3模拟数据丢失)
      - [步骤4：PITR恢复](#步骤4pitr恢复)
    - [1.3 PITR高级场景](#13-pitr高级场景)
      - [场景1：恢复到特定事务](#场景1恢复到特定事务)
      - [场景2：恢复到特定LSN](#场景2恢复到特定lsn)
      - [场景3：恢复到命名还原点](#场景3恢复到命名还原点)
      - [场景4：时间线恢复（多次PITR）](#场景4时间线恢复多次pitr)
  - [2. 灾备系统设计](#2-灾备系统设计)
    - [2.1 RPO和RTO目标](#21-rpo和rto目标)
    - [2.2 多层备份策略（3-2-1规则）](#22-多层备份策略3-2-1规则)
    - [1.3 PITR恢复详细步骤](#13-pitr恢复详细步骤)
      - [场景：恢复到误删除前](#场景恢复到误删除前)
    - [1.4 PITR恢复监控](#14-pitr恢复监控)
  - [3. 备份策略设计](#3-备份策略设计)
    - [3.1 完整的备份策略矩阵](#31-完整的备份策略矩阵)
    - [3.2 备份自动化完整方案](#32-备份自动化完整方案)
  - [4. 自动化备份脚本](#4-自动化备份脚本)
    - [4.1 备份目录（backup\_catalog）](#41-备份目录backup_catalog)
    - [4.2 增量备份脚本（PostgreSQL 18+）](#42-增量备份脚本postgresql-18)
    - [4.3 增量恢复脚本](#43-增量恢复脚本)
  - [5. 灾备演练SOP](#5-灾备演练sop)
    - [5.1 灾备演练计划](#51-灾备演练计划)
    - [5.2 全面演练SOP](#52-全面演练sop)
    - [5.3 灾备演练记录表](#53-灾备演练记录表)
  - [6. 恢复测试](#6-恢复测试)
    - [6.1 定期恢复测试（每月）](#61-定期恢复测试每月)
    - [6.2 数据一致性验证](#62-数据一致性验证)
  - [7. 完整实战案例](#7-完整实战案例)
    - [7.1 案例：电商平台灾备方案](#71-案例电商平台灾备方案)
    - [7.2 案例：灾难恢复实战](#72-案例灾难恢复实战)
  - [📊 备份恢复最佳实践清单](#-备份恢复最佳实践清单)
    - [✅ 必须做的](#-必须做的)
    - [❌ 不要做的](#-不要做的)
  - [📚 参考资源](#-参考资源)
    - [官方文档](#官方文档)
    - [备份工具](#备份工具)
    - [最佳实践](#最佳实践)

---

## 1. PITR（时间点恢复）完整指南

### 1.1 PITR原理

**什么是PITR**：

Point-In-Time Recovery（PITR）允许恢复数据库到过去任意时刻的状态，通过基础备份+WAL归档实现。

**适用场景**：

- 误操作恢复（删除了重要数据）
- 数据损坏恢复
- 审计和调查（查看历史状态）
- 灾难恢复（恢复到故障前）

### 1.2 PITR快速开始（30分钟）

#### 步骤1：配置WAL归档

**编辑`postgresql.conf`**：

```conf
# 启用WAL归档
wal_level = replica                # 或 logical
archive_mode = on
archive_command = 'cp %p /backup/wal_archive/%f'
# 或使用更可靠的方式
# archive_command = 'test ! -f /backup/wal_archive/%f && cp %p /backup/wal_archive/%f'

# WAL配置
max_wal_senders = 10
wal_keep_size = 1GB
archive_timeout = 300              # 5分钟归档一次

# PostgreSQL 18+ 增量备份支持
wal_summary_keep_time = 7d         # 保留7天的WAL摘要
```

**创建归档目录**：

```bash
sudo mkdir -p /backup/wal_archive
sudo chown postgres:postgres /backup/wal_archive
sudo chmod 700 /backup/wal_archive

# 重启PostgreSQL
sudo systemctl restart postgresql-17
```

**验证归档**：

```sql
-- 检查归档状态
SELECT * FROM pg_stat_archiver;

-- 强制归档当前WAL
SELECT pg_switch_wal();

-- 检查归档目录
SELECT pg_ls_waldir();
```

#### 步骤2：创建基础备份

```bash
# 方法1：使用pg_basebackup
pg_basebackup \
    -h localhost \
    -U postgres \
    -D /backup/base/$(date +%Y%m%d_%H%M%S) \
    -Ft \                          # tar格式
    -z \                           # 压缩
    -P \                           # 显示进度
    -X stream \                    # 包含WAL
    -c fast \                      # 快速检查点
    -l "base_backup_$(date +%Y%m%d)"

# 方法2：使用pg_backup_start/stop（更灵活）
psql -c "SELECT pg_backup_start('manual_backup', false)"

# 使用rsync或tar备份数据目录
tar -czf /backup/base/manual_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    -C /var/lib/postgresql/17/main .

psql -c "SELECT pg_backup_stop()"

# PostgreSQL 18+ 增量备份
pg_basebackup \
    -h localhost \
    -U postgres \
    -D /backup/incremental/$(date +%Y%m%d_%H%M%S) \
    -Ft -z -P \
    --incremental=/backup/base/previous_backup/backup_manifest
```

#### 步骤3：模拟数据丢失

```sql
-- 记录当前时间
SELECT now();  -- 假设：2025-01-01 10:00:00

-- 插入测试数据
INSERT INTO test_table VALUES (1, 'before disaster');

-- 等待5分钟，模拟正常使用
\! sleep 300

-- 灾难发生！误删除数据
DELETE FROM test_table WHERE id = 1;

-- 记录灾难时间
SELECT now();  -- 假设：2025-01-01 10:05:00

-- 继续插入数据（灾难后）
INSERT INTO test_table VALUES (2, 'after disaster');
```

#### 步骤4：PITR恢复

```bash
# 1. 停止PostgreSQL
sudo systemctl stop postgresql-17

# 2. 移走当前数据目录
sudo mv /var/lib/postgresql/17/main /var/lib/postgresql/17/main.broken

# 3. 恢复基础备份
sudo mkdir /var/lib/postgresql/17/main
sudo tar -xzf /backup/base/base_backup_20250101.tar.gz \
    -C /var/lib/postgresql/17/main

# 4. 创建恢复配置
sudo tee /var/lib/postgresql/17/main/recovery.signal << EOF
# recovery.signal (空文件即可，配置在postgresql.conf)
EOF

# 5. 配置恢复参数（postgresql.conf或postgresql.auto.conf）
sudo tee -a /var/lib/postgresql/17/main/postgresql.auto.conf << EOF
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_time = '2025-01-01 10:04:59'  # 灾难前1秒
recovery_target_action = 'promote'              # 恢复后提升为主库
EOF

# 6. 设置权限
sudo chown -R postgres:postgres /var/lib/postgresql/17/main
sudo chmod 700 /var/lib/postgresql/17/main

# 7. 启动PostgreSQL（开始恢复）
sudo systemctl start postgresql-17

# 8. 监控恢复进度
tail -f /var/log/postgresql/postgresql-17-main.log

# 9. 验证恢复结果
psql -c "SELECT * FROM test_table"
# 应该只有id=1的记录，id=2的记录不存在（因为是灾难后插入的）
```

### 1.3 PITR高级场景

#### 场景1：恢复到特定事务

```sql
-- 记录当前事务ID
SELECT txid_current();  -- 假设：1000

-- 执行一些操作
INSERT INTO test VALUES (1);
INSERT INTO test VALUES (2);  -- txid: 1001
INSERT INTO test VALUES (3);  -- txid: 1002

-- 恢复到txid 1001（包含id=1和id=2，不包含id=3）
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_xid = '1001'
recovery_target_inclusive = true
```

#### 场景2：恢复到特定LSN

```sql
-- 记录当前LSN（带错误处理）
DO $$
DECLARE
    current_lsn TEXT;
BEGIN
    SELECT pg_current_wal_lsn()::TEXT INTO current_lsn;
    RAISE NOTICE '当前LSN: %', current_lsn;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '获取当前LSN失败: %', SQLERRM;
END $$;

-- 恢复到该LSN
-- 注意：以下配置需要在postgresql.auto.conf或recovery.conf中设置
-- restore_command = 'cp /backup/wal_archive/%f %p'
-- recovery_target_lsn = '0/1234ABCD'
```

<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
grep

#### 场景3：恢复到命名还原点

```sql
-- 创建还原点（带错误处理）
DO $$
DECLARE
    restore_point_lsn TEXT;
BEGIN
    SELECT pg_create_restore_point('before_major_update')::TEXT INTO restore_point_lsn;
    RAISE NOTICE '还原点已创建: before_major_update, LSN: %', restore_point_lsn;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建还原点失败: %', SQLERRM;
END $$;

-- 执行重大更新（带错误处理）
DO $$
DECLARE
    updated_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        RAISE EXCEPTION '表 users 不存在';
    END IF;

    UPDATE users SET salary = salary * 1.1;
    GET DIAGNOSTICS updated_count = ROW_COUNT;

    RAISE NOTICE '已更新 % 条记录', updated_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 users 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '更新失败: %', SQLERRM;
END $$;

-- 如果出错，恢复到还原点
-- 注意：以下配置需要在postgresql.auto.conf或recovery.conf中设置
-- restore_command = 'cp /backup/wal_archive/%f %p'
-- recovery_target_name = 'before_major_update'
```

#### 场景4：时间线恢复（多次PITR）

```bash
# 第一次恢复创建了timeline 2
# 再次恢复到timeline 1的某个时间点
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_time = '2025-01-01 09:00:00'
recovery_target_timeline = 1  # 指定时间线
```

---

## 2. 灾备系统设计

### 2.1 RPO和RTO目标

**定义**：

- **RPO（Recovery Point Objective）**：可接受的数据丢失时间
- **RTO（Recovery Time Objective）**：可接受的恢复时间

| 级别 | RPO | RTO | 备份策略 | 成本 |
|------|-----|-----|---------|------|
| **黄金级** | 0秒 | <5分钟 | 同步复制+自动故障切换 | ⭐⭐⭐⭐⭐ |
| **白银级** | <5分钟 | <30分钟 | 异步复制+快速恢复 | ⭐⭐⭐⭐ |
| **青铜级** | <1小时 | <4小时 | WAL归档+每日备份 | ⭐⭐⭐ |
| **经济级** | <24小时 | <8小时 | 每日全备 | ⭐⭐ |

### 2.2 多层备份策略（3-2-1规则）

**3-2-1规则**：

- **3份**数据副本
- **2种**不同存储介质
- **1份**异地备份

**实施方案**：

```bash
# 副本1：主数据库（生产）
/var/lib/postgresql/17/main

# 副本2：本地备份（同一数据中心）
/backup/local/
├── base/          # 基础备份（每周全备，每日增量）
├── wal_archive/   # WAL归档（实时）
└── logical/       # 逻辑备份（每日）

# 副本3：异地备份（不同数据中心）
s3://company-backups-us-west/postgresql/
├── base/
├── wal_archive/
└── logical/

# 介质1：本地磁盘（SSD/HDD）
# 介质2：对象存储（S3/OSS/Blob）
```

**备份脚本**（`/usr/local/bin/pg_full_backup.sh`）：

```bash
#!/bin/bash
# PostgreSQL完整备份脚本（带完整错误处理）

set -euo pipefail  # 严格错误处理

# 配置
BACKUP_DIR="/backup/local"
S3_BUCKET="s3://company-backups/postgresql"
RETENTION_DAYS=30
PGHOST="localhost"
PGUSER="postgres"
PGDATABASE="postgres"

# 日志
LOG_FILE="/var/log/postgresql/backup.log"
exec 1>> "$LOG_FILE" 2>&1

# 错误处理函数
error_exit() {
    echo "错误: $1" >&2
    echo "备份失败于: $(date)" >> "$LOG_FILE"
    exit 1
}

# 检查依赖
check_dependencies() {
    command -v pg_basebackup >/dev/null 2>&1 || error_exit "pg_basebackup 未安装"
    command -v pg_dumpall >/dev/null 2>&1 || error_exit "pg_dumpall 未安装"
    command -v aws >/dev/null 2>&1 || error_exit "aws CLI 未安装"
    command -v psql >/dev/null 2>&1 || error_exit "psql 未安装"
}

# 检查目录
check_directories() {
    [ -d "$BACKUP_DIR" ] || mkdir -p "$BACKUP_DIR" || error_exit "无法创建备份目录: $BACKUP_DIR"
    [ -d "$BACKUP_DIR/base" ] || mkdir -p "$BACKUP_DIR/base" || error_exit "无法创建基础备份目录"
    [ -d "$BACKUP_DIR/logical" ] || mkdir -p "$BACKUP_DIR/logical" || error_exit "无法创建逻辑备份目录"
}

echo "===== Backup started at $(date) ====="

# 检查依赖和目录
check_dependencies
check_directories

# 创建时间戳目录
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/base/$TIMESTAMP"
mkdir -p "$BACKUP_PATH" || error_exit "无法创建备份路径: $BACKUP_PATH"

# 1. 基础备份（带错误处理）
echo "Creating base backup..."
if ! pg_basebackup \
    -h "$PGHOST" \
    -U "$PGUSER" \
    -D "$BACKUP_PATH" \
    -Ft -z -P \
    -X stream \
    -c fast \
    -l "base_backup_$TIMESTAMP"; then
    error_exit "基础备份失败"
fi
echo "基础备份完成"

# 2. 逻辑备份（补充，带错误处理）
echo "Creating logical backup..."
LOGICAL_BACKUP_FILE="$BACKUP_DIR/logical/dump_$TIMESTAMP.sql.gz"
if ! pg_dumpall \
    -h "$PGHOST" \
    -U "$PGUSER" \
    --clean --if-exists \
    | gzip > "$LOGICAL_BACKUP_FILE"; then
    error_exit "逻辑备份失败"
fi
echo "逻辑备份完成: $LOGICAL_BACKUP_FILE"

# 3. 备份元数据（带错误处理）
echo "Backing up metadata..."
METADATA_FILE="$BACKUP_PATH/backup_metadata.json"
if ! cat > "$METADATA_FILE" <<EOF
{
    "timestamp": "$TIMESTAMP",
    "type": "full",
    "postgresql_version": "$(psql -h "$PGHOST" -U "$PGUSER" -t -c 'SELECT version()' | tr -d ' ')",
    "database_size": "$(psql -h "$PGHOST" -U "$PGUSER" -t -c 'SELECT pg_size_pretty(pg_database_size(current_database()))' | tr -d ' ')",
    "wal_location": "$(psql -h "$PGHOST" -U "$PGUSER" -t -c 'SELECT pg_current_wal_lsn()' | tr -d ' ')",
    "backup_size": "$(du -sh "$BACKUP_PATH" | cut -f1)"
}
EOF
then
    error_exit "创建备份元数据失败"
fi
echo "备份元数据已创建"

# 4. 上传到S3（带错误处理）
echo "Uploading to S3..."
if ! aws s3 sync "$BACKUP_PATH" "$S3_BUCKET/base/$TIMESTAMP" \
    --storage-class STANDARD_IA; then
    error_exit "S3上传基础备份失败"
fi

if ! aws s3 cp "$LOGICAL_BACKUP_FILE" \
    "$S3_BUCKET/logical/"; then
    error_exit "S3上传逻辑备份失败"
fi
echo "S3上传完成"

# 5. 清理旧备份（带错误处理）
echo "Cleaning old backups..."
if ! find "$BACKUP_DIR/base" -mindepth 1 -maxdepth 1 -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null; then
    echo "警告: 清理旧基础备份时出现问题" >&2
fi

if ! find "$BACKUP_DIR/logical" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null; then
    echo "警告: 清理旧逻辑备份时出现问题" >&2
fi
echo "旧备份清理完成"

# 6. 验证备份（带错误处理）
echo "Verifying backup..."
if [ -f "$BACKUP_PATH/base.tar.gz" ]; then
    if tar -tzf "$BACKUP_PATH/base.tar.gz" > /dev/null 2>&1; then
        echo "备份验证: 成功"
    else
        error_exit "备份验证失败: 备份文件可能损坏"
    fi
else
    echo "警告: 未找到基础备份文件" >&2
fi

echo "===== Backup completed at $(date) ====="
echo "备份成功完成"
```

**定时任务**（`/etc/cron.d/postgresql-backup`）：

```cron
# 每天凌晨2点全备
0 2 * * * postgres /usr/local/bin/pg_full_backup.sh

# 每小时增量备份（WAL归档已自动）
# 0 * * * * postgres /usr/local/bin/pg_incremental_backup.sh
```

### 1.3 PITR恢复详细步骤

#### 场景：恢复到误删除前

**背景**：

- 误删除时间：2025-01-01 15:30:45
- 最新全备：2025-01-01 02:00:00
- WAL归档：持续到当前

**恢复步骤**：

```bash
#!/bin/bash
# PITR恢复脚本（带完整错误处理）

set -euo pipefail  # 严格错误处理

# 错误处理函数
error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 1. 确认恢复目标时间
RECOVERY_TARGET="2025-01-01 15:30:44"  # 误删除前1秒
BACKUP_DIR="/backup/base/20250101_020000"
WAL_ARCHIVE="/backup/wal_archive"
PGDATA="/var/lib/postgresql/17/main"

# 检查备份和目录
[ -d "$BACKUP_DIR" ] || error_exit "备份目录不存在: $BACKUP_DIR"
[ -f "$BACKUP_DIR/base.tar.gz" ] || error_exit "基础备份文件不存在"
[ -d "$WAL_ARCHIVE" ] || error_exit "WAL归档目录不存在: $WAL_ARCHIVE"

# 2. 停止当前数据库（带错误处理）
echo "停止PostgreSQL..."
if ! sudo systemctl stop postgresql-17; then
    error_exit "停止PostgreSQL失败"
fi

# 3. 备份当前数据目录（预防，带错误处理）
if [ -d "$PGDATA" ]; then
    BACKUP_BROKEN="$PGDATA.broken.$(date +%s)"
    echo "备份当前数据目录到: $BACKUP_BROKEN"
    if ! sudo mv "$PGDATA" "$BACKUP_BROKEN"; then
        error_exit "备份当前数据目录失败"
    fi
fi

# 4. 恢复基础备份（带错误处理）
echo "恢复基础备份..."
if ! sudo mkdir -p "$PGDATA"; then
    error_exit "创建数据目录失败"
fi

if ! sudo tar -xzf "$BACKUP_DIR/base.tar.gz" -C "$PGDATA"; then
    error_exit "恢复基础备份失败"
fi

# 5. 恢复WAL归档目录访问（带错误处理）
echo "准备WAL归档..."
if ! sudo mkdir -p "$PGDATA/pg_wal_restore"; then
    error_exit "创建WAL恢复目录失败"
fi

if ! sudo cp "$WAL_ARCHIVE"/* "$PGDATA/pg_wal_restore/" 2>/dev/null; then
    echo "警告: 复制WAL归档文件失败，将使用原归档目录" >&2
fi

# 6. 创建recovery配置（带错误处理）
echo "创建恢复配置..."
if ! sudo tee "$PGDATA/recovery.signal" > /dev/null << EOF
# recovery.signal - 标记数据库处于恢复模式
EOF
then
    error_exit "创建recovery.signal失败"
fi

if ! sudo tee "$PGDATA/postgresql.auto.conf" > /dev/null << EOF
# 恢复配置
restore_command = 'cp $WAL_ARCHIVE/%f %p'
recovery_target_time = '$RECOVERY_TARGET'
recovery_target_action = 'promote'

# 可选：恢复到特定事务、LSN或还原点
# recovery_target_xid = '1234567'
# recovery_target_lsn = '0/12345678'
# recovery_target_name = 'before_major_update'

# 恢复行为
recovery_target_inclusive = true          # 包含目标事务
recovery_target_timeline = 'latest'       # 恢复到最新时间线
EOF
then
    error_exit "创建恢复配置文件失败"
fi

# 7. 设置权限（带错误处理）
echo "设置权限..."
if ! sudo chown -R postgres:postgres "$PGDATA"; then
    error_exit "设置所有者失败"
fi

if ! sudo chmod 700 "$PGDATA"; then
    error_exit "设置权限失败"
fi

# 8. 启动恢复（带错误处理）
echo "启动PostgreSQL恢复..."
if ! sudo systemctl start postgresql-17; then
    error_exit "启动PostgreSQL失败"
fi

# 9. 监控恢复进度（带超时）
echo "监控恢复进度..."
for i in {1..60}; do
    if sudo systemctl is-active --quiet postgresql-17; then
        if psql -c "SELECT pg_is_in_recovery();" 2>/dev/null | grep -q "f"; then
            echo "恢复完成"
            break
        fi
    fi
    if [ $i -eq 60 ]; then
        error_exit "恢复超时（60分钟）"
    fi
    echo "恢复进行中... ($i/60)"
    sleep 60
done

# 10. 验证恢复（带错误处理）
echo "验证恢复..."
if ! psql -c "SELECT * FROM test_table WHERE id = 1;" > /dev/null 2>&1; then
    echo "警告: 验证查询失败" >&2
fi

# 11. 检查数据库状态（带错误处理）
echo "检查数据库状态..."
psql -c "SELECT pg_is_in_recovery() AS in_recovery;" || echo "警告: 检查恢复状态失败" >&2
psql -c "SELECT pg_last_wal_replay_lsn() AS replay_lsn;" || echo "警告: 检查重放LSN失败" >&2
psql -c "SELECT pg_current_wal_lsn() AS current_lsn;" || echo "警告: 检查当前LSN失败" >&2

echo "PITR恢复流程完成"
```

### 1.4 PITR恢复监控

**恢复进度监控脚本**：

```bash
#!/bin/bash
# monitor_recovery.sh

while true; do
    # 检查是否还在恢复
    IS_RECOVERY=$(psql -t -c "SELECT pg_is_in_recovery()")

    if [ "$IS_RECOVERY" = " f" ]; then
        echo "Recovery completed!"
        break
    fi

    # 获取恢复进度
    REPLAY_LSN=$(psql -t -c "SELECT pg_last_wal_replay_lsn()")
    RECEIVE_LSN=$(psql -t -c "SELECT pg_last_wal_receive_lsn()")
    TARGET=$(grep recovery_target_time /var/lib/postgresql/17/main/postgresql.auto.conf | cut -d\' -f2)

    echo "$(date): Recovery in progress..."
    echo "  Replay LSN: $REPLAY_LSN"
    echo "  Receive LSN: $RECEIVE_LSN"
    echo "  Target: $TARGET"
    echo ""

    sleep 5
done
```

---

## 3. 备份策略设计

### 3.1 完整的备份策略矩阵

| 备份类型 | 频率 | 保留期 | 存储位置 | 成本 | RPO | RTO |
|---------|------|--------|---------|------|-----|-----|
| **全量备份** | 每周日 | 12周 | 本地+S3 | 高 | 1周 | 2-4小时 |
| **增量备份** | 每天 | 30天 | 本地+S3 | 中 | 1天 | 1-2小时 |
| **WAL归档** | 持续 | 30天 | 本地+S3 | 中 | 5分钟 | 30分钟 |
| **逻辑备份** | 每天 | 7天 | 本地 | 低 | 1天 | 4-8小时 |
| **快照** | 每4小时 | 48小时 | 存储系统 | 中 | 4小时 | 10分钟 |

### 3.2 备份自动化完整方案

**主控脚本**（`/usr/local/bin/pg_backup_master.sh`）：

```bash
#!/bin/bash

set -euo pipefail

# 配置文件
source /etc/postgresql/backup.conf

# 函数：发送告警
alert() {
    local level=$1
    local message=$2

    # 发送到监控系统
    curl -X POST https://monitoring.example.com/api/alerts \
        -H "Content-Type: application/json" \
        -d "{\"level\": \"$level\", \"message\": \"$message\", \"service\": \"postgresql-backup\"}"

    # 发送邮件
    echo "$message" | mail -s "PostgreSQL Backup Alert [$level]" admin@example.com
}

# 函数：记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# 主逻辑
main() {
    local backup_type=$(get_backup_type)

    log "Starting $backup_type backup..."

    case $backup_type in
        full)
            run_full_backup || { alert "ERROR" "Full backup failed"; exit 1; }
            ;;
        incremental)
            run_incremental_backup || { alert "ERROR" "Incremental backup failed"; exit 1; }
            ;;
        logical)
            run_logical_backup || { alert "ERROR" "Logical backup failed"; exit 1; }
            ;;
    esac

    # 验证备份
    verify_backup || { alert "WARNING" "Backup verification failed"; }

    # 上传到云存储
    upload_to_cloud || { alert "WARNING" "Cloud upload failed"; }

    # 清理旧备份
    cleanup_old_backups

    # 生成报告
    generate_backup_report

    log "$backup_type backup completed successfully"
    alert "INFO" "$backup_type backup completed"
}

# 确定备份类型
get_backup_type() {
    local day_of_week=$(date +%u)
    local hour=$(date +%H)

    if [ "$day_of_week" = "7" ] && [ "$hour" = "02" ]; then
        echo "full"
    elif [ "$hour" = "02" ]; then
        echo "incremental"
    else
        echo "wal_archive"  # 持续归档，不需要手动触发
    fi
}

# 全量备份
run_full_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$BACKUP_BASE_DIR/full/$timestamp"

    mkdir -p "$backup_dir"

    pg_basebackup \
        -h $PGHOST \
        -U $PGUSER \
        -D "$backup_dir" \
        -Ft -z -P \
        -X stream \
        -c fast \
        -l "full_backup_$timestamp"

    # 记录备份信息
    psql -h $PGHOST -U $PGUSER -c \
        "INSERT INTO backup_catalog (backup_type, backup_path, backup_size)
         VALUES ('full', '$backup_dir', $(du -sb $backup_dir | cut -f1))"
}

# 增量备份（PostgreSQL 18+）
run_incremental_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$BACKUP_BASE_DIR/incremental/$timestamp"
    local last_full=$(find "$BACKUP_BASE_DIR/full" -mindepth 1 -maxdepth 1 -type d | sort -r | head -1)

    mkdir -p "$backup_dir"

    pg_basebackup \
        -h $PGHOST \
        -U $PGUSER \
        -D "$backup_dir" \
        -Ft -z -P \
        -X stream \
        --incremental="$last_full/backup_manifest"

    psql -h $PGHOST -U $PGUSER -c \
        "INSERT INTO backup_catalog (backup_type, backup_path, backup_size)
         VALUES ('incremental', '$backup_dir', $(du -sb $backup_dir | cut -f1))"
}

# 逻辑备份
run_logical_backup() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$BACKUP_BASE_DIR/logical/dump_$timestamp.sql.gz"

    pg_dumpall \
        -h $PGHOST \
        -U $PGUSER \
        --clean --if-exists \
        | gzip > "$backup_file"
}

# 验证备份
verify_backup() {
    local latest_backup=$(find "$BACKUP_BASE_DIR/full" -name "base.tar.gz" | sort -r | head -1)

    if [ -z "$latest_backup" ]; then
        return 1
    fi

    # 检查tar文件完整性
    tar -tzf "$latest_backup" > /dev/null 2>&1
}

# 上传到云存储
upload_to_cloud() {
    # 同步到S3（增量上传）
    aws s3 sync "$BACKUP_BASE_DIR" "$S3_BUCKET" \
        --storage-class STANDARD_IA \
        --exclude "*/pg_wal_restore/*"
}

# 清理旧备份
cleanup_old_backups() {
    # 本地保留30天
    find "$BACKUP_BASE_DIR/full" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
    find "$BACKUP_BASE_DIR/incremental" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
    find "$BACKUP_BASE_DIR/logical" -name "*.sql.gz" -mtime +7 -delete

    # S3保留90天（使用生命周期策略）
}

# 生成备份报告
generate_backup_report() {
    psql -h $PGHOST -U $PGUSER -c "
        SELECT
            backup_type,
            COUNT(*) AS count,
            pg_size_pretty(SUM(backup_size)) AS total_size,
            MAX(backup_time) AS latest_backup
        FROM backup_catalog
        WHERE backup_time >= now() - interval '7 days'
        GROUP BY backup_type
        ORDER BY backup_type;
    "
}

# 执行
main "$@"
```

---

## 4. 自动化备份脚本

### 4.1 备份目录（backup_catalog）

```sql
-- 创建备份目录表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_catalog') THEN
        DROP TABLE backup_catalog;
        RAISE NOTICE '已删除现有表: backup_catalog';
    END IF;

    CREATE TABLE backup_catalog (
        backup_id serial PRIMARY KEY,
        backup_type text CHECK (backup_type IN ('full', 'incremental', 'logical', 'wal_archive')),
        backup_path text NOT NULL,
        backup_size bigint,
        backup_time timestamptz DEFAULT now(),
        wal_start_lsn pg_lsn,
        wal_end_lsn pg_lsn,
        postgresql_version text,
        is_verified boolean DEFAULT false,
        is_uploaded boolean DEFAULT false,
        retention_until timestamptz,
        notes text
    );

    RAISE NOTICE '备份目录表创建成功: backup_catalog';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 backup_catalog 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建备份目录表失败: %', SQLERRM;
END $$;

-- 创建索引（带错误处理）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_catalog') THEN
        RAISE EXCEPTION '表 backup_catalog 不存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_backup_catalog_time') THEN
        CREATE INDEX idx_backup_catalog_time ON backup_catalog(backup_time);
        RAISE NOTICE '索引创建成功: idx_backup_catalog_time';
    ELSE
        RAISE WARNING '索引 idx_backup_catalog_time 已存在';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_backup_catalog_type') THEN
        CREATE INDEX idx_backup_catalog_type ON backup_catalog(backup_type);
        RAISE NOTICE '索引创建成功: idx_backup_catalog_type';
    ELSE
        RAISE WARNING '索引 idx_backup_catalog_type 已存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 backup_catalog 不存在';
    WHEN duplicate_table THEN
        RAISE WARNING '索引已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建索引失败: %', SQLERRM;
END $$;
```

### 4.2 增量备份脚本（PostgreSQL 18+）

```bash
#!/bin/bash
# pg_incremental_backup.sh - 增量备份脚本（带完整错误处理）

set -euo pipefail  # 严格错误处理

# 错误处理函数
error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 配置
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_BASE="/backup/incremental"
BACKUP_DIR="$BACKUP_BASE/$TIMESTAMP"

# 检查命令
command -v psql >/dev/null 2>&1 || error_exit "psql 命令未找到"
command -v pg_basebackup >/dev/null 2>&1 || error_exit "pg_basebackup 命令未找到"
command -v du >/dev/null 2>&1 || error_exit "du 命令未找到"

# 检查目录
[ -d "$BACKUP_BASE" ] || mkdir -p "$BACKUP_BASE" || error_exit "无法创建备份目录: $BACKUP_BASE"

# 查找最新的全备（带错误处理）
echo "查找最新的全备..."
LAST_FULL=$(psql -t -A -c "
    SELECT backup_path
    FROM backup_catalog
    WHERE backup_type = 'full'
      AND is_verified = true
    ORDER BY backup_time DESC
    LIMIT 1
" 2>/dev/null || error_exit "查询备份目录失败")

if [ -z "$LAST_FULL" ]; then
    error_exit "未找到全备，请先运行全备"
fi

if [ ! -d "$LAST_FULL" ]; then
    error_exit "全备目录不存在: $LAST_FULL"
fi

if [ ! -f "$LAST_FULL/backup_manifest" ]; then
    error_exit "全备清单文件不存在: $LAST_FULL/backup_manifest"
fi

echo "找到最新全备: $LAST_FULL"

# 创建增量备份（带错误处理）
echo "创建增量备份..."
[ -d "$BACKUP_DIR" ] || mkdir -p "$BACKUP_DIR" || error_exit "无法创建备份目录: $BACKUP_DIR"

if ! pg_basebackup \
    -h localhost \
    -U postgres \
    -D "$BACKUP_DIR" \
    -Ft -z -P \
    --incremental="$LAST_FULL/backup_manifest" \
    -l "incremental_backup_$TIMESTAMP"; then
    error_exit "创建增量备份失败"
fi

echo "增量备份创建成功: $BACKUP_DIR"

# 记录到catalog（带错误处理）
echo "记录备份到目录..."
BACKUP_SIZE=$(du -sb "$BACKUP_DIR" | cut -f1)
[ -n "$BACKUP_SIZE" ] || error_exit "无法获取备份大小"

if ! psql -c "
    INSERT INTO backup_catalog (
        backup_type, backup_path, backup_size,
        wal_start_lsn, wal_end_lsn
    ) VALUES (
        'incremental',
        '$BACKUP_DIR',
        $BACKUP_SIZE,
        (SELECT pg_current_wal_lsn()),
        (SELECT pg_current_wal_lsn())
    )
"; then
    error_exit "记录备份到目录失败"
fi

echo "增量备份完成: $BACKUP_DIR"
```

### 4.3 增量恢复脚本

```bash
#!/bin/bash
# pg_incremental_restore.sh - 增量恢复脚本（带完整错误处理）

set -euo pipefail  # 严格错误处理

# 错误处理函数
error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 参数检查
RECOVERY_TARGET_TIME=$1

if [ -z "$RECOVERY_TARGET_TIME" ]; then
    echo "用法: $0 'YYYY-MM-DD HH:MM:SS'"
    exit 1
fi

# 配置
PGDATA="/var/lib/postgresql/17/main"

# 检查命令
command -v psql >/dev/null 2>&1 || error_exit "psql 命令未找到"
command -v pg_combinebackup >/dev/null 2>&1 || error_exit "pg_combinebackup 命令未找到（PostgreSQL 18+）"

# 1. 查找需要的备份链（带错误处理）
echo "查找备份链..."
BACKUP_CHAIN=$(psql -t -A -F, -c "
WITH RECURSIVE backup_chain AS (
    SELECT backup_id, backup_type, backup_path, backup_time, 1 AS level
    FROM backup_catalog
    WHERE backup_type = 'full'
      AND backup_time <= '$RECOVERY_TARGET_TIME'::timestamptz
    ORDER BY backup_time DESC
    LIMIT 1

    UNION ALL

    SELECT b.backup_id, b.backup_type, b.backup_path, b.backup_time, bc.level + 1
    FROM backup_catalog b
    JOIN backup_chain bc ON b.backup_time > bc.backup_time
    WHERE b.backup_type = 'incremental'
      AND b.backup_time <= '$RECOVERY_TARGET_TIME'::timestamptz
)
SELECT backup_id || ',' || backup_type || ',' || backup_path || ',' || backup_time || ',' || level
FROM backup_chain ORDER BY level;
" 2>/dev/null)

if [ -z "$BACKUP_CHAIN" ]; then
    error_exit "未找到备份链"
fi

# 2. 恢复备份链（带错误处理）
echo "$BACKUP_CHAIN" | while IFS=, read -r backup_id type path time level; do
    echo "恢复 $type 备份 (级别 $level) 从 $time..."

    [ -n "$path" ] || error_exit "备份路径为空"
    [ -f "$path/base.tar.gz" ] || error_exit "备份文件不存在: $path/base.tar.gz"

    if [ "$type" = "full" ]; then
        # 恢复全备
        echo "恢复全量备份..."
        if [ -d "$PGDATA" ]; then
            rm -rf "$PGDATA" || error_exit "删除旧数据目录失败"
        fi
        mkdir -p "$PGDATA" || error_exit "创建数据目录失败"

        if ! tar -xzf "$path/base.tar.gz" -C "$PGDATA"; then
            error_exit "恢复全量备份失败"
        fi
    else
        # 应用增量备份
        echo "应用增量备份..."
        if ! pg_combinebackup \
            "$PGDATA" \
            "$path" \
            -o "$PGDATA"; then
            error_exit "应用增量备份失败"
        fi
    fi
done

echo "备份链恢复完成。请配置恢复参数并启动PostgreSQL。"
```

---

## 5. 灾备演练SOP

### 5.1 灾备演练计划

**演练频率**：

- **全面演练**：每季度1次（4小时）
- **部分演练**：每月1次（1小时）
- **桌面演练**：每周1次（30分钟）

**演练类型**：

| 演练类型 | 场景 | 目标 | 人员 |
|---------|------|------|------|
| **桌面演练** | 讨论恢复步骤 | 熟悉流程 | DBA团队 |
| **部分演练** | 恢复单个数据库 | 验证步骤 | DBA+开发 |
| **全面演练** | 完整灾难恢复 | 验证RTO/RPO | 全团队 |

### 5.2 全面演练SOP

**演练准备清单**（提前1周）：

```markdown
- [ ] 选择演练时间（非业务高峰）
- [ ] 通知相关人员
- [ ] 准备演练环境（隔离网络）
- [ ] 检查最新备份可用性
- [ ] 准备监控工具
- [ ] 准备通信工具（钉钉、Slack等）
- [ ] 打印恢复SOP
- [ ] 准备计时器
```

**演练脚本**（`disaster_recovery_drill.sh`）：

```bash
#!/bin/bash

# 灾备演练自动化脚本
set -euo pipefail

DRILL_LOG="/var/log/postgresql/drill_$(date +%Y%m%d_%H%M%S).log"
exec 1>> "$DRILL_LOG" 2>&1

echo "====== 灾备演练开始 ======"
echo "演练时间: $(date)"
echo "演练场景: 数据中心完全故障"
echo ""

# 阶段1：模拟灾难（5分钟）
echo "=== 阶段1：模拟灾难 ==="
DISASTER_TIME=$(date '+%Y-%m-%d %H:%M:%S')
echo "灾难发生时间: $DISASTER_TIME"

# 停止主数据库
echo "停止主数据库..."
systemctl stop postgresql-17

# 损坏数据目录（模拟）
echo "模拟数据目录损坏..."
mv /var/lib/postgresql/17/main /var/lib/postgresql/17/main.disaster

START_TIME=$(date +%s)

# 阶段2：启动恢复（10分钟目标）
echo ""
echo "=== 阶段2：启动恢复 ==="

# 2.1 查找最新备份
echo "查找最新备份..."
LATEST_BACKUP=$(find /backup/base -name "base.tar.gz" | sort -r | head -1)
echo "最新备份: $LATEST_BACKUP"

# 2.2 恢复基础备份
echo "恢复基础备份..."
mkdir -p /var/lib/postgresql/17/main
tar -xzf "$LATEST_BACKUP" -C /var/lib/postgresql/17/main

# 2.3 配置PITR
echo "配置PITR..."
cat > /var/lib/postgresql/17/main/recovery.signal << EOF
EOF

cat > /var/lib/postgresql/17/main/postgresql.auto.conf << EOF
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_time = '$DISASTER_TIME'
recovery_target_action = 'promote'
EOF

# 2.4 启动恢复
echo "启动数据库恢复..."
chown -R postgres:postgres /var/lib/postgresql/17/main
chmod 700 /var/lib/postgresql/17/main
systemctl start postgresql-17

# 2.5 等待恢复完成
echo "等待恢复完成..."
while true; do
    if psql -c "SELECT pg_is_in_recovery()" | grep -q "f"; then
        break
    fi
    sleep 5
done

RECOVERY_TIME=$(date +%s)
RECOVERY_DURATION=$((RECOVERY_TIME - START_TIME))

echo "恢复完成，耗时: ${RECOVERY_DURATION}秒"

# 阶段3：验证恢复（5分钟）
echo ""
echo "=== 阶段3：验证恢复 ==="

# 3.1 数据完整性检查
echo "检查数据完整性..."
psql -c "SELECT COUNT(*) FROM pg_class"

# 3.2 业务数据验证
echo "验证业务数据..."
psql -c "
    SELECT
        'users' AS table_name, COUNT(*) AS row_count FROM users
    UNION ALL
    SELECT 'orders', COUNT(*) FROM orders
    UNION ALL
    SELECT 'products', COUNT(*) FROM products;
"

# 3.3 检查数据库状态
echo "检查数据库状态..."
psql -c "SELECT pg_is_in_recovery(), pg_current_wal_lsn()"

# 阶段4：性能测试（5分钟）
echo ""
echo "=== 阶段4：性能测试 ==="

echo "运行pgbench..."
pgbench -i -s 10 testdb
pgbench -c 10 -j 2 -t 1000 testdb

# 阶段5：清理（5分钟）
echo ""
echo "=== 阶段5：清理和总结 ==="

# 计算总时间
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

echo ""
echo "====== 演练总结 ======"
echo "总耗时: ${TOTAL_DURATION}秒 ($(($TOTAL_DURATION / 60))分钟)"
echo "恢复耗时: ${RECOVERY_DURATION}秒"
echo "RTO目标: 30分钟"
echo "RTO达成: $(if [ $TOTAL_DURATION -lt 1800 ]; then echo '是'; else echo '否'; fi)"
echo ""

# 生成演练报告
psql -c "
    INSERT INTO dr_drill_log (
        drill_date,
        drill_scenario,
        recovery_duration_seconds,
        total_duration_seconds,
        rto_achieved,
        notes
    ) VALUES (
        '$DISASTER_TIME',
        '数据中心完全故障',
        $RECOVERY_DURATION,
        $TOTAL_DURATION,
        $(if [ $TOTAL_DURATION -lt 1800 ]; then echo 'true'; else echo 'false'; fi),
        'Automated drill'
    )
"

echo "演练日志: $DRILL_LOG"
echo "====== 演练完成 ======"
```

### 5.3 灾备演练记录表

```sql
-- 创建灾备演练记录表（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dr_drill_log') THEN
        DROP TABLE dr_drill_log;
        RAISE NOTICE '已删除现有表: dr_drill_log';
    END IF;

    CREATE TABLE dr_drill_log (
        drill_id serial PRIMARY KEY,
        drill_date timestamptz NOT NULL,
        drill_scenario text NOT NULL,
        recovery_duration_seconds int,
        total_duration_seconds int,
        rto_target_seconds int DEFAULT 1800,  -- 30分钟
        rto_achieved boolean,
        participants text[],
        issues_found text[],
        action_items text[],
        notes text,
        created_at timestamptz DEFAULT now()
    );

    RAISE NOTICE '灾备演练记录表创建成功: dr_drill_log';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 dr_drill_log 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建灾备演练记录表失败: %', SQLERRM;
END $$;

-- 查询演练历史（带性能测试和错误处理）
DO $$
DECLARE
    drill_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'dr_drill_log') THEN
        RAISE EXCEPTION '表 dr_drill_log 不存在';
    END IF;

    SELECT COUNT(*) INTO drill_count FROM dr_drill_log;

    IF drill_count = 0 THEN
        RAISE WARNING '演练记录表为空';
    ELSE
        RAISE NOTICE '找到 % 条演练记录', drill_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 dr_drill_log 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查询演练历史失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    drill_date,
    drill_scenario,
    total_duration_seconds / 60 AS duration_minutes,
    rto_target_seconds / 60 AS target_minutes,
    rto_achieved,
    CASE
        WHEN rto_achieved THEN '✅ 达标'
        ELSE '❌ 超时'
    END AS status
FROM dr_drill_log
ORDER BY drill_date DESC;
```

---

## 6. 恢复测试

### 6.1 定期恢复测试（每月）

**测试脚本**（`test_recovery.sh`）：

```bash
#!/bin/bash

# 在隔离环境测试恢复
TEST_ENV="/var/lib/postgresql/test_recovery"
TEST_PORT=5433

# 1. 准备测试环境
mkdir -p $TEST_ENV
rm -rf $TEST_ENV/*

# 2. 恢复最新备份
LATEST_BACKUP=$(find /backup/base -name "base.tar.gz" | sort -r | head -1)
tar -xzf "$LATEST_BACKUP" -C $TEST_ENV

# 3. 修改配置（使用不同端口）
cat >> $TEST_ENV/postgresql.conf << EOF
port = $TEST_PORT
shared_buffers = 256MB
EOF

# 4. 启动测试实例
pg_ctl -D $TEST_ENV -l $TEST_ENV/logfile start

# 等待启动
sleep 5

# 5. 验证数据
psql -p $TEST_PORT -c "SELECT COUNT(*) FROM pg_database"
psql -p $TEST_PORT -c "SELECT pg_size_pretty(pg_database_size(current_database()))"

# 6. 清理
pg_ctl -D $TEST_ENV stop
rm -rf $TEST_ENV

echo "Recovery test completed successfully"
```

### 6.2 数据一致性验证

```sql
-- 创建校验和表（备份时，带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_checksums') THEN
        DROP TABLE backup_checksums;
        RAISE NOTICE '已删除现有表: backup_checksums';
    END IF;

    CREATE TABLE backup_checksums (
        table_name text PRIMARY KEY,
        row_count bigint,
        data_checksum text,
        backup_time timestamptz DEFAULT now()
    );

    RAISE NOTICE '校验和表创建成功: backup_checksums';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表 backup_checksums 已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建校验和表失败: %', SQLERRM;
END $$;

-- 生成校验和（带错误处理）
DO $$
DECLARE
    inserted_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_checksums') THEN
        RAISE EXCEPTION '表 backup_checksums 不存在';
    END IF;

    INSERT INTO backup_checksums (table_name, row_count, data_checksum)
    SELECT
        tablename,
        n_live_tup AS row_count,
        md5(string_agg(ctid::text, '' ORDER BY ctid)) AS data_checksum
    FROM pg_stat_user_tables
    GROUP BY tablename, n_live_tup;

    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RAISE NOTICE '已插入 % 条校验和记录', inserted_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 backup_checksums 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '生成校验和失败: %', SQLERRM;
END $$;

-- 恢复后验证（带性能测试和错误处理）
DO $$
DECLARE
    match_count INT;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'backup_checksums') THEN
        RAISE EXCEPTION '表 backup_checksums 不存在';
    END IF;

    SELECT COUNT(*) INTO match_count
    FROM (
        SELECT
            current.table_name,
            current.row_count AS current_rows,
            backup.row_count AS backup_rows,
            current.row_count = backup.row_count AS row_count_match,
            current.data_checksum = backup.data_checksum AS checksum_match
        FROM (
            SELECT
                tablename AS table_name,
                n_live_tup AS row_count,
                md5(string_agg(ctid::text, '' ORDER BY ctid)) AS data_checksum
            FROM pg_stat_user_tables
            GROUP BY tablename, n_live_tup
        ) current
        FULL OUTER JOIN backup_checksums backup USING (table_name)
        WHERE current.row_count != backup.row_count
           OR current.data_checksum != backup.data_checksum
    ) mismatches;

    IF match_count = 0 THEN
        RAISE NOTICE '所有表的校验和匹配，数据完整性验证通过';
    ELSE
        RAISE WARNING '发现 % 个表的校验和不匹配，数据可能已损坏', match_count;
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表 backup_checksums 不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '恢复后验证失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    current.table_name,
    current.row_count AS current_rows,
    backup.row_count AS backup_rows,
    current.row_count = backup.row_count AS row_count_match,
    current.data_checksum = backup.data_checksum AS checksum_match
FROM (
    SELECT
        tablename AS table_name,
        n_live_tup AS row_count,
        md5(string_agg(ctid::text, '' ORDER BY ctid)) AS data_checksum
    FROM pg_stat_user_tables
    GROUP BY tablename, n_live_tup
) current
FULL OUTER JOIN backup_checksums backup USING (table_name)
WHERE current.row_count != backup.row_count
   OR current.data_checksum != backup.data_checksum;
-- 执行时间: 取决于表数量和大小
-- 计划: Hash Join + Seq Scan
```

---

## 7. 完整实战案例

### 7.1 案例：电商平台灾备方案

**业务需求**：

- 数据库大小：500GB
- 日增长：5GB
- RPO：5分钟
- RTO：30分钟
- 合规：3年数据保留

**方案设计**：

```text
架构：主-从-备
├── 主库（生产）：北京机房
├── 从库（热备）：上海机房
│   └── 实时流复制，延迟<1秒
├── 灾备库（冷备）：深圳机房
│   └── WAL归档恢复，延迟<5分钟
└── 云备份：AWS S3
    ├── 每周全备
    ├── 每日增量
    └── 持续WAL归档

备份计划：
├── 全量备份：每周日 02:00（约2小时）
├── 增量备份：每天 02:00（约30分钟）
├── WAL归档：持续（实时）
├── 逻辑备份：每天 03:00（约1小时）
└── 快照：每4小时（EC2 snapshot，5分钟）
```

**实施配置**：

**主库配置**（`postgresql.conf`）：

```conf
# WAL配置
wal_level = replica
wal_log_hints = on
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 10GB

# 归档配置
archive_mode = on
archive_command = 'aws s3 cp %p s3://company-wal-archive/%f'
archive_timeout = 300

# 检查点配置
checkpoint_timeout = 15min
max_wal_size = 10GB
min_wal_size = 2GB

# PostgreSQL 18+
wal_summary_keep_time = 7d
```

**从库配置**（上海机房）：

```conf
# 复制配置
hot_standby = on
max_standby_streaming_delay = 30s
hot_standby_feedback = on

# primary_conninfo在recovery.conf或postgresql.auto.conf
primary_conninfo = 'host=beijing-primary port=5432 user=replication password=xxx'
primary_slot_name = 'shanghai_replica'
```

**备份脚本部署**：

```bash
# 在主库上部署备份cron
# /etc/cron.d/postgresql-backup
0 2 * * 0 postgres /usr/local/bin/pg_full_backup.sh
0 2 * * 1-6 postgres /usr/local/bin/pg_incremental_backup.sh
0 */4 * * * postgres /usr/local/bin/pg_wal_archive_check.sh
```

### 7.2 案例：灾难恢复实战

**灾难场景**：主库所在机房火灾，主库和从库（北京）全部不可用

**恢复步骤**：

```bash
# T+0分钟：发现灾难
echo "$(date): 发现主库和从库不可达"

# T+5分钟：决策切换到灾备库
echo "$(date): 决策：使用深圳灾备库"

# T+10分钟：提升灾备库为主库
ssh shenzhen-dr << 'EOF'
    # 停止恢复，提升为主库
    sudo -u postgres psql -c "SELECT pg_promote()"

    # 或者（旧版本）
    # sudo -u postgres pg_ctl promote -D /var/lib/postgresql/17/main
EOF

# T+15分钟：验证数据完整性
ssh shenzhen-dr << 'EOF'
    psql -c "SELECT pg_is_in_recovery()"  # 应该返回false
    psql -c "SELECT COUNT(*) FROM orders WHERE created_at >= now() - interval '1 hour'"
    psql -c "SELECT pg_current_wal_lsn()"
EOF

# T+20分钟：更新DNS/负载均衡
# 指向深圳机房IP
# ...

# T+25分钟：通知业务恢复
echo "$(date): 数据库已恢复，业务可以访问"

# T+30分钟：评估数据丢失
ssh shenzhen-dr << 'EOF'
    psql -c "
        SELECT
            MAX(created_at) AS last_order_time,
            now() - MAX(created_at) AS data_loss
        FROM orders;
    "
EOF

echo "$(date): 恢复完成，RTO: 30分钟，RPO: $(获取数据丢失时间)"
```

**恢复后检查清单**：

```markdown
- [ ] 验证数据库可连接
- [ ] 验证数据完整性（行数、校验和）
- [ ] 验证业务功能（下单、支付等）
- [ ] 检查复制延迟（如果有从库）
- [ ] 验证监控恢复
- [ ] 验证备份恢复（新主库开始备份）
- [ ] 更新文档和配置
- [ ] 通知相关方恢复完成
- [ ] 开始故障分析
```

---

## 📊 备份恢复最佳实践清单

### ✅ 必须做的

1. **定期备份**
   - 每周全备
   - 每天增量
   - 持续WAL归档

2. **异地备份**
   - 至少2个地理位置
   - 使用对象存储（S3等）

3. **定期演练**
   - 每季度全面演练
   - 每月恢复测试

4. **监控告警**
   - 备份失败告警
   - WAL归档延迟告警
   - 磁盘空间告警

5. **文档维护**
   - 恢复SOP
   - 联系人清单
   - 配置文档

### ❌ 不要做的

1. **不要**只依赖单一备份方式
2. **不要**从不测试恢复
3. **不要**将备份放在同一物理位置
4. **不要**忽略WAL归档
5. **不要**使用未验证的备份

---

## 📚 参考资源

### 官方文档

1. [Continuous Archiving and Point-in-Time Recovery (PITR)](https://www.postgresql.org/docs/current/continuous-archiving.html)
2. [pg_basebackup](https://www.postgresql.org/docs/current/app-pgbasebackup.html)
3. [pg_combinebackup (PG18+)](https://www.postgresql.org/docs/18/app-pgcombinebackup.html)

### 备份工具

1. [pgBackRest](https://pgbackrest.org/) - 企业级备份工具
2. [Barman](https://pgbarman.org/) - 备份和恢复管理
3. [WAL-G](https://github.com/wal-g/wal-g) - WAL归档工具

### 最佳实践

1. [PostgreSQL Backup Best Practices](https://www.postgresql.org/docs/current/backup.html)
2. [Disaster Recovery Planning](https://wiki.postgresql.org/wiki/Disaster_recovery_planning)

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐ 高级

💾 **永远不要失去数据！定期备份，定期演练！**
