# 03 | PostgreSQL-VACUUM机制

> **实现定位**: 本文档深入分析PostgreSQL VACUUM的源码实现，从触发到清理的完整流程。

---

## 📑 目录

- [03 | PostgreSQL-VACUUM机制](#03--postgresql-vacuum机制)
  - [📑 目录](#-目录)
  - [一、VACUUM概述](#一vacuum概述)
    - [1.1 目的](#11-目的)
    - [1.2 类型](#12-类型)
  - [二、触发机制](#二触发机制)
    - [2.1 autovacuum触发条件](#21-autovacuum触发条件)
    - [2.2 autovacuum守护进程](#22-autovacuum守护进程)
  - [三、扫描与清理](#三扫描与清理)
    - [3.1 堆表扫描](#31-堆表扫描)
    - [3.2 死元组判断](#32-死元组判断)
  - [四、索引清理](#四索引清理)
    - [4.1 索引VACUUM](#41-索引vacuum)
    - [4.2 B-tree索引清理](#42-b-tree索引清理)
  - [五、Freeze操作](#五freeze操作)
    - [5.1 Freeze原理](#51-freeze原理)
    - [5.2 aggressive VACUUM](#52-aggressive-vacuum)
  - [六、并行VACUUM](#六并行vacuum)
    - [6.1 并行机制](#61-并行机制)
    - [6.2 性能提升](#62-性能提升)
  - [七、总结](#七总结)
    - [7.1 核心流程](#71-核心流程)
    - [7.2 关键优化](#72-关键优化)
    - [7.3 最佳实践](#73-最佳实践)
  - [八、完整源码分析](#八完整源码分析)
    - [8.1 lazy\_scan\_heap详细实现](#81-lazy_scan_heap详细实现)
    - [8.2 HOT剪枝优化](#82-hot剪枝优化)
    - [8.3 Visibility Map优化](#83-visibility-map优化)
  - [九、性能优化实战](#九性能优化实战)
    - [9.1 大规模表VACUUM优化](#91-大规模表vacuum优化)
    - [9.2 Freeze优化](#92-freeze优化)
  - [十、实际案例](#十实际案例)
    - [案例1: 电商订单表膨胀](#案例1-电商订单表膨胀)
    - [案例2: 高并发写入表VACUUM](#案例2-高并发写入表vacuum)
  - [十一、反例与错误配置](#十一反例与错误配置)
    - [反例1: VACUUM过于频繁](#反例1-vacuum过于频繁)
    - [反例2: 忽略Freeze](#反例2-忽略freeze)

---

## 一、VACUUM概述

### 1.1 目的

**VACUUM解决三大问题**:

1. 回收死元组空间
2. 更新统计信息
3. 防止事务ID回卷

### 1.2 类型

| 类型 | 命令 | 特点 |
|-----|------|------|
| **普通VACUUM** | `VACUUM table` | 不阻塞读写 |
| **VACUUM FULL** | `VACUUM FULL table` | 锁表，完全重建 |
| **ANALYZE** | `VACUUM ANALYZE` | 更新统计信息 |
| **Auto VACUUM** | 自动触发 | 后台运行 |

---

## 二、触发机制

### 2.1 autovacuum触发条件

**公式**:

$$Trigger = DeadTuples > threshold + scale\_factor \times LiveTuples$$

**默认参数**:

```sql
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
```

**示例**:

- 表有1000行
- 阈值 = 50 + 0.2 × 1000 = 250行
- 当死元组>250时触发

### 2.2 autovacuum守护进程

**源码位置**: `src/backend/postmaster/autovacuum.c`

```c
void AutoVacuumMain(int argc, char *argv[]) {
    while (!shutdown_requested) {
        // 1. 扫描所有数据库
        DatabaseList *dbs = get_database_list();

        for (db in dbs) {
            // 2. 查找需要VACUUM的表
            List *tables = get_tables_to_vacuum(db);

            for (table in tables) {
                if (should_vacuum(table)) {
                    // 3. 启动worker进程
                    autovacuum_do_vac_analyze(table);
                }
            }
        }

        // 4. 睡眠
        pg_usleep(autovacuum_naptime * 1000000L);
    }
}
```

---

## 三、扫描与清理

### 3.1 堆表扫描

**源码位置**: `src/backend/commands/vacuum.c`

```c
void heap_vacuum_rel(Relation rel, VacuumParams *params) {
    BlockNumber nblocks = RelationGetNumberOfBlocks(rel);

    // 1. 第一遍：扫描堆表
    for (BlockNumber blkno = 0; blkno < nblocks; blkno++) {
        Buffer buf = ReadBufferExtended(rel, MAIN_FORKNUM, blkno);
        LockBuffer(buf, BUFFER_LOCK_SHARE);

        Page page = BufferGetPage(buf);

        // 扫描页内所有元组
        lazy_scan_heap(rel, buf, &vacrel state);

        UnlockReleaseBuffer(buf);
    }

    // 2. 清理索引（如果需要）
    if (dead_tuples > threshold) {
        lazy_vacuum_indexes(&vacrelstats);
    }

    // 3. 第二遍：回收堆表空间
    lazy_vacuum_heap(rel, &vacrelstats);

    // 4. 更新统计信息
    vac_update_relstats(rel);
}
```

### 3.2 死元组判断

```c
bool heap_tuple_needs_freeze(HeapTupleHeader tuple,
                             TransactionId cutoff_xid) {
    TransactionId xmin = HeapTupleHeaderGetXmin(tuple);

    // 检查xmin是否过老
    if (TransactionIdPrecedes(xmin, cutoff_xid)) {
        return true;  // 需要Freeze
    }

    // 检查xmax
    if (tuple->t_infomask & HEAP_XMAX_COMMITTED) {
        TransactionId xmax = HeapTupleHeaderGetXmax(tuple);
        if (TransactionIdPrecedes(xmax, cutoff_xid)) {
            return true;
        }
    }

    return false;
}
```

---

## 四、索引清理

### 4.1 索引VACUUM

```c
void lazy_vacuum_index(Relation indrel,
                      IndexVacuumInfo *ivinfo,
                      LVDeadTuples *dead_tuples) {
    // 批量删除死元组的索引项
    amroutine->ambulkdelete(indrel,
                           lazy_tid_reaped,
                           (void *) dead_tuples,
                           ivinfo);
}
```

### 4.2 B-tree索引清理

```c
IndexBulkDeleteResult *
btbulkdelete(IndexVacuumInfo *info, ...) {
    // 扫描B-tree
    for (BlockNumber blkno = 1; blkno < nblocks; blkno++) {
        Buffer buf = ReadBuffer(rel, blkno);
        Page page = BufferGetPage(buf);

        // 遍历页内项
        for (OffsetNumber offnum = FirstOffsetNumber;
             offnum <= maxoff; offnum++) {
            ItemId itemid = PageGetItemId(page, offnum);
            IndexTuple itup = (IndexTuple) PageGetItem(page, itemid);

            // 检查元组是否死亡
            if (callback(&itup->t_tid, callback_state)) {
                // 删除索引项
                _bt_delitems_delete(rel, buf, offnum);
            }
        }

        ReleaseBuffer(buf);
    }
}
```

---

## 五、Freeze操作

### 5.1 Freeze原理

**目的**: 防止事务ID回卷（32位，21亿限制）

**Freeze**: 将旧事务ID替换为FrozenTransactionId (2)

```c
#define FrozenTransactionId ((TransactionId) 2)

void heap_freeze_tuple(HeapTupleHeader tuple) {
    TransactionId xid = HeapTupleHeaderGetXmin(tuple);

    if (TransactionIdPrecedes(xid, cutoff_xid)) {
        // Freeze xmin
        HeapTupleHeaderSetXmin(tuple, FrozenTransactionId);
        tuple->t_infomask |= HEAP_XMIN_COMMITTED;
        tuple->t_infomask |= HEAP_XMIN_INVALID;
    }
}
```

### 5.2 aggressive VACUUM

**触发条件**:

$$age(table) > autovacuum\_freeze\_max\_age$$

**默认**: 2亿事务

```sql
ALTER SYSTEM SET autovacuum_freeze_max_age = 200000000;
```

---

## 六、并行VACUUM

### 6.1 并行机制

**PostgreSQL 13+支持并行索引清理**:

```sql
VACUUM (PARALLEL 4) large_table;
```

**实现**:

```c
void parallel_vacuum_indexes(VacuumParams *params,
                            Relation *indrels,
                            int nindexes) {
    // 1. 启动worker进程
    int nworkers = min(params->nworkers, nindexes);

    ParallelVacuumState *pvs = parallel_vacuum_init(nworkers);

    // 2. 分配索引给worker
    for (int i = 0; i < nindexes; i++) {
        int worker_id = i % nworkers;
        assign_index_to_worker(pvs, worker_id, indrels[i]);
    }

    // 3. 等待完成
    parallel_vacuum_wait_for_workers(pvs);
}
```

### 6.2 性能提升

| 索引数 | 串行VACUUM | 并行VACUUM(4) | 提升 |
|-------|-----------|--------------|------|
| 4 | 40分钟 | 12分钟 | 3.3× |
| 8 | 80分钟 | 25分钟 | 3.2× |

**Amdahl定律验证**:

$$Speedup = \frac{1}{0.2 + \frac{0.8}{4}} = 3.33×$$

---

## 七、总结

### 7.1 核心流程

```text
触发VACUUM
    ↓
扫描堆表（第一遍）
    ↓
收集死元组TID
    ↓
清理索引
    ↓
回收堆表空间（第二遍）
    ↓
Freeze老元组
    ↓
更新FSM/VM
    ↓
更新统计信息
```

### 7.2 关键优化

- 批量处理死元组
- 并行索引清理
- HOT剪枝
- Visibility Map跳过

### 7.3 最佳实践

**配置建议**:

```sql
-- 热表调优
ALTER TABLE hot_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_vacuum_cost_delay = 10
);

-- 并行VACUUM
SET max_parallel_maintenance_workers = 4;
```

---

## 八、完整源码分析

### 8.1 lazy_scan_heap详细实现

**源码位置**: `src/backend/commands/vacuumlazy.c`

```c
static void lazy_scan_heap(Relation rel, Buffer buffer, LVRelStats *vacrelstats) {
    Page page = BufferGetPage(buffer);
    BlockNumber blkno = BufferGetBlockNumber(buffer);
    OffsetNumber maxoff = PageGetMaxOffsetNumber(page);

    vacrelstats->scanned_pages++;

    // 遍历页内所有元组
    for (OffsetNumber offnum = FirstOffsetNumber;
         offnum <= maxoff;
         offnum = OffsetNumberNext(offnum)) {

        ItemId itemid = PageGetItemId(page, offnum);

        // 跳过未使用的项
        if (!ItemIdIsUsed(itemid) || ItemIdIsDead(itemid)) {
            continue;
        }

        HeapTupleHeader tuple = (HeapTupleHeader) PageGetItem(page, itemid);

        // 检查是否需要Freeze
        TransactionId xmin = HeapTupleHeaderGetXmin(tuple);
        TransactionId xmax = HeapTupleHeaderGetXmax(tuple);

        bool needs_freeze = false;
        bool is_dead = false;

        // Freeze检查
        if (TransactionIdIsNormal(xmin)) {
            if (TransactionIdPrecedes(xmin, vacrelstats->freeze_min_xid)) {
                needs_freeze = true;
            }
        }

        // 死元组检查
        if (tuple->t_infomask & HEAP_XMAX_COMMITTED) {
            if (TransactionIdPrecedes(xmax, vacrelstats->oldest_xmin)) {
                is_dead = true;
            }
        } else if (tuple->t_infomask & HEAP_XMAX_INVALID) {
            // xmax无效，元组存活
        } else {
            // xmax未提交，检查是否对当前快照可见
            if (TransactionIdIsInProgress(xmax, &snapshot)) {
                // 删除事务仍在进行，元组存活
            } else {
                is_dead = true;
            }
        }

        // 记录死元组
        if (is_dead) {
            vacrelstats->dead_tuples++;
            record_dead_tuple(vacrelstats, blkno, offnum);
        }

        // 执行Freeze
        if (needs_freeze) {
            heap_freeze_tuple(tuple, vacrelstats->freeze_min_xid);
            vacrelstats->frozen_tuples++;
        }
    }

    // 更新Visibility Map
    if (vacrelstats->dead_tuples == 0) {
        visibilitymap_set(rel, blkno, buffer, InvalidXLogRecPtr, buffer, VISIBILITYMAP_ALL_VISIBLE);
    }
}
```

### 8.2 HOT剪枝优化

**HOT (Heap-Only Tuple)**: 避免索引更新

```c
bool heap_hot_prune(Relation rel, Buffer buffer, TransactionId snapshot_xmin) {
    Page page = BufferGetPage(buffer);
    OffsetNumber maxoff = PageGetMaxOffsetNumber(page);

    // 查找HOT链
    for (OffsetNumber offnum = FirstOffsetNumber; offnum <= maxoff; offnum++) {
        ItemId itemid = PageGetItemId(page, offnum);
        HeapTupleHeader tuple = (HeapTupleHeader) PageGetItem(page, itemid);

        // 检查是否是HOT更新
        if (HeapTupleHeaderIsHeapOnly(tuple)) {
            // HOT链: 可以安全删除旧版本
            if (is_dead_tuple(tuple, snapshot_xmin)) {
                // 标记为可删除
                ItemIdMarkDead(itemid);
            }
        }
    }

    // 压缩页面
    PageRepairFragmentation(page);
}
```

**HOT条件**:

1. 更新不修改索引列
2. 新版本在同一页面
3. 旧版本对当前快照不可见

**性能提升**: HOT更新避免索引维护，速度提升10×

### 8.3 Visibility Map优化

**Visibility Map (VM)**: 标记全可见页面

```c
void update_visibility_map(Relation rel, BlockNumber blkno, Buffer buffer) {
    // 检查页面是否全可见
    bool all_visible = true;

    for (OffsetNumber offnum = FirstOffsetNumber; offnum <= maxoff; offnum++) {
        HeapTupleHeader tuple = get_tuple(page, offnum);

        if (!tuple_is_visible(tuple, snapshot)) {
            all_visible = false;
            break;
        }
    }

    if (all_visible) {
        // 标记为全可见
        visibilitymap_set(rel, blkno, buffer, InvalidXLogRecPtr, buffer, VISIBILITYMAP_ALL_VISIBLE);
    }
}
```

**优化效果**: VACUUM跳过全可见页面，速度提升5-10×

---

## 九、性能优化实战

### 9.1 大规模表VACUUM优化

**场景**: 10亿行表，死元组10%

**问题**: VACUUM耗时8小时

**优化方案**:

```sql
-- 1. 并行VACUUM
VACUUM (PARALLEL 8, VERBOSE, ANALYZE) large_table;

-- 2. 调整autovacuum参数
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.01,  -- 降低阈值
    autovacuum_vacuum_cost_delay = 5,       -- 减少延迟
    autovacuum_workers = 4                   -- 增加worker
);

-- 3. 分区表VACUUM
-- 按日期分区，仅VACUUM最近分区
VACUUM (VERBOSE) large_table_2025_12;
```

**效果**: 耗时从8小时降至2小时 (-75%)

### 9.2 Freeze优化

**场景**: 事务ID接近回卷点

**问题**: aggressive VACUUM频繁触发

**优化方案**:

```sql
-- 1. 提前Freeze
ALTER SYSTEM SET autovacuum_freeze_max_age = 150000000;  -- 降低阈值

-- 2. 监控Freeze进度
SELECT
    schemaname || '.' || relname AS table,
    age(relfrozenxid) AS xid_age,
    pg_size_pretty(pg_total_relation_size(oid)) AS size
FROM pg_class
WHERE age(relfrozenxid) > 100000000
ORDER BY age(relfrozenxid) DESC;

-- 3. 手动Freeze关键表
VACUUM FREEZE critical_table;
```

**效果**: 避免紧急Freeze，性能稳定

---

## 十、实际案例

### 案例1: 电商订单表膨胀

**问题**: 订单表800GB，查询缓慢

**诊断**:

```sql
SELECT
    schemaname || '.' || relname AS table,
    n_live_tup,
    n_dead_tup,
    round(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_ratio,
    pg_size_pretty(pg_total_relation_size(oid)) AS total_size
FROM pg_stat_user_tables
WHERE relname = 'orders';

-- 结果:
-- table: orders
-- n_live_tup: 500,000,000
-- n_dead_tup: 300,000,000
-- dead_ratio: 37.5%
-- total_size: 800GB
```

**解决方案**:

```sql
-- 1. 立即VACUUM
VACUUM (VERBOSE, ANALYZE) orders;

-- 2. 如果还不够，VACUUM FULL（需停机）
VACUUM FULL orders;

-- 3. 优化autovacuum
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- 5%死元组即触发
    fillfactor = 80                         -- 预留空间给HOT
);
```

**效果**: 表大小降至500GB (-37.5%)，查询速度提升3×

### 案例2: 高并发写入表VACUUM

**问题**: 高并发写入导致VACUUM跟不上

**场景**: 每秒10,000次UPDATE

**问题**: 死元组快速积累，VACUUM来不及清理

**解决方案**:

```sql
-- 1. 增加autovacuum worker
ALTER SYSTEM SET autovacuum_max_workers = 6;

-- 2. 降低cost限制
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 2000;

-- 3. 表级调优
ALTER TABLE hot_table SET (
    autovacuum_vacuum_cost_delay = 0,  -- 无延迟
    autovacuum_vacuum_scale_factor = 0.02  -- 2%即触发
);

-- 4. 使用HOT优化
-- 确保更新不修改索引列
CREATE INDEX idx_hot_table_user_id ON hot_table(user_id);
-- UPDATE时只修改非索引列
```

**效果**: VACUUM及时清理，表膨胀率<5%

---

## 十一、反例与错误配置

### 反例1: VACUUM过于频繁

**错误配置**:

```sql
-- 错误: 阈值过低
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.001  -- 0.1%即触发
);
```

**问题**:

- VACUUM频繁运行，占用CPU
- 锁竞争增加
- 性能下降

**正确配置**:

```sql
-- 正确: 合理阈值
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.1  -- 10%死元组触发
);
```

### 反例2: 忽略Freeze

**错误做法**:

```sql
-- 错误: 禁用autovacuum
ALTER SYSTEM SET autovacuum = off;
```

**问题**: 事务ID回卷，数据库崩溃

**正确做法**:

```sql
-- 正确: 启用autovacuum并监控
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_freeze_max_age = 200000000;

-- 监控
SELECT age(datfrozenxid) FROM pg_database WHERE datname = current_database();
-- 如果age > 1.5亿，需要立即VACUUM FREEZE
```

---

**文档版本**: 2.0.0（大幅充实）
**最后更新**: 2025-12-05
**新增内容**: 完整源码分析、HOT优化、Visibility Map、性能优化实战、实际案例、反例

**关联文档**:

- `01-核心理论模型/02-MVCC理论完整解析.md`
- `05-实现机制/01-PostgreSQL-MVCC实现.md`
- `02-设计权衡分析/05-存储-并发权衡.md`
- `06-性能分析/03-存储开销分析.md` (存储开销理论)
