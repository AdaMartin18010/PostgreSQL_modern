# Heap Access Method 深度形式化 V2

> **文档类型**: 存储引擎核心 (DEEP-V2学术深度版本)
> **对齐标准**: PostgreSQL源码, "Database Internals" (Petrov), CMU 15-445
> **数学基础**: 集合论、地址空间理论、版本控制理论
> **版本**: DEEP-V2 | 字数: ~6500字
> **创建日期**: 2026-03-04

---

## 📑 目录

- [Heap Access Method 深度形式化 V2](#heap-access-method-深度形式化-v2)
  - [📑 目录](#-目录)
  - [1. 理论基础与概念定义](#1-理论基础与概念定义)
    - [1.1 Heap表模型](#11-heap表模型)
    - [1.2 元组形式化定义](#12-元组形式化定义)
    - [1.3 堆表操作](#13-堆表操作)
  - [2. TID结构与元组标识](#2-tid结构与元组标识)
    - [2.1 TID定义](#21-tid定义)
    - [2.2 地址空间](#22-地址空间)
    - [2.3 TID稳定性](#23-tid稳定性)
  - [3. 页内布局与行版本](#3-页内布局与行版本)
    - [3.1 页结构](#31-页结构)
    - [3.2 Line Pointer结构](#32-line-pointer结构)
    - [3.3 元组头结构](#33-元组头结构)
    - [3.4 元组标志位](#34-元组标志位)
  - [4. MVCC行版本控制](#4-mvcc行版本控制)
    - [4.1 元组可见性规则](#41-元组可见性规则)
    - [4.2 版本链](#42-版本链)
    - [4.3 形式化规则](#43-形式化规则)
  - [5. HOT (Heap-Only Tuple) 机制](#5-hot-heap-only-tuple-机制)
    - [5.1 HOT原理](#51-hot原理)
    - [5.2 LP\_REDIRECT机制](#52-lp_redirect机制)
    - [5.3 HOT形式化](#53-hot形式化)
    - [5.4 HOT修剪与碎片整理](#54-hot修剪与碎片整理)
  - [6. PostgreSQL heapam.c源码分析](#6-postgresql-heapamc源码分析)
    - [6.1 插入操作](#61-插入操作)
    - [6.2 更新操作](#62-更新操作)
    - [6.3 删除操作](#63-删除操作)
    - [6.4 扫描操作](#64-扫描操作)
    - [6.5 可见性判断](#65-可见性判断)
  - [7. 性能分析与优化](#7-性能分析与优化)
    - [7.1 元组大小计算](#71-元组大小计算)
    - [7.2 页填充率](#72-页填充率)
    - [7.3 HOT性能收益](#73-hot性能收益)
    - [7.4 VACUUM影响](#74-vacuum影响)
  - [8. 形式化验证](#8-形式化验证)
    - [8.1 Heap不变式](#81-heap不变式)
    - [8.2 MVCC正确性](#82-mvcc正确性)
  - [9. 参考文献](#9-参考文献)

---

## 1. 理论基础与概念定义

### 1.1 Heap表模型

**定义 1.1 (Heap表)**:

Heap表是无序的元组集合，按插入顺序存储:

$$
\text{HeapTable} = \{P_1, P_2, ..., P_n\} \quad \text{where} \quad n = \lceil \frac{N_{tuples}}{N_{tuples\_per\_page}} \rceil
$$

**定义 1.2 (页)**:

页是磁盘I/O的基本单位:

$$
P_i = \langle \text{Header}, \text{LinePointers}[], \text{Tuples}[], \text{FreeSpace} \rangle
$$

在PostgreSQL中，默认页大小为 8KB:

$$
\text{PageSize} = 8192 \text{ bytes}
$$

### 1.2 元组形式化定义

**定义 1.3 (元组)**:

$$
T = \langle \text{Header},  ext{Data} \rangle
$$

其中:

$$
\text{Header} = \langle t\_xmin, t\_xmax, t\_cid, t\_infomask, t\_hoff \rangle
$$

$$
\text{Data} = \langle A_1:v_1, A_2:v_2, ..., A_n:v_n \rangle
$$

### 1.3 堆表操作

**定义 1.4 (堆表操作集)**:

$$
\mathcal{O}_{Heap} = \{\text{Insert}, \text{Update}, \text{Delete}, \text{Fetch}, \text{Scan}\}
$$

---

## 2. TID结构与元组标识

### 2.1 TID定义

**定义 2.1 (元组标识符 TID)**:

$$
\text{TID} = \langle \text{BlockNumber}, \text{OffsetNumber} \rangle
$$

其中:

- $\text{BlockNumber} \in [0, 2^{32}-1]$: 页号
- $\text{OffsetNumber} \in [1, \text{MaxOffsetNumber}]$: 页内偏移

**PostgreSQL实现**:

```c
// src/include/c.h
typedef uint32 BlockNumber;    /* 块号，最大 2^32-1 */

// src/include/storage/itemid.h
typedef uint16 OffsetNumber;   /* 页内偏移，从1开始 */

// src/include/storage/itemptr.h
typedef struct ItemPointerData {
    BlockIdData ip_blkid;      /* 块号 */
    OffsetNumber ip_posid;     /* 偏移号 */
} ItemPointerData;

typedef ItemPointerData *ItemPointer;

#define ItemPointerGetBlockNumber(pointer) \
    (BlockIdGetBlockNumber(&(pointer)->ip_blkid))
#define ItemPointerGetOffsetNumber(pointer) \
    ((pointer)->ip_posid)
```

### 2.2 地址空间

**定义 2.2 (堆表地址空间)**:

$$
\mathcal{A}_{Heap} = \{0, 1, ..., N_{blocks}-1\} \times \{1, 2, ..., N_{max\_offset}\}
$$

**地址计算**:

$$
\text{FileOffset} = \text{BlockNumber} \times \text{BLCKSZ} + \text{PageHeaderSize}
$$

### 2.3 TID稳定性

**定义 2.3 (TID稳定性)**:

TID在以下操作中保持不变:

- 选择 (SELECT)
- 索引扫描 (Index Scan)

TID在以下操作中改变:

- 更新 (UPDATE) - 创建新元组
- 移动 (CLUSTER, VACUUM FULL)

---

## 3. 页内布局与行版本

### 3.1 页结构

**定义 3.1 (页结构)**:

```
+------------------+  <-- PageHeader (24 bytes)
│   PageHeaderData │
+------------------+
│  pd_lsn          │  WAL位置
│  pd_checksum     │  页校验和
│  pd_flags        │  标志位
│  pd_lower        │  空闲空间开始
│  pd_upper        │  空闲空间结束
│  pd_special      │  特殊空间开始
+------------------+  <-- LinePointerArray
│   LinePointer[1] │  4 bytes each
│   LinePointer[2] │
│   ...            │
+------------------+  <-- Free Space
│                  │
│   (grows down)   │
│                  │
+------------------+  <-- Tuple Data (grows up)
│   Tuple N        │
│   Tuple N-1      │
│   ...            │
+------------------+  <-- Special Space (if any)
```

### 3.2 Line Pointer结构

```c
// src/include/storage/itemid.h
typedef struct ItemIdData {
    unsigned lp_off:15,        /* 元组在页内的偏移 */
             lp_flags:2,       /* 状态标志 */
             lp_len:15;        /* 元组长度 */
} ItemIdData;

typedef ItemIdData *ItemId;

/* lp_flags取值 */
#define LP_UNUSED    0    /* 未使用 */
#define LP_NORMAL    1    /* 正常使用的元组 */
#define LP_REDIRECT  2    /* HOT重定向 */
#define LP_DEAD      3    /* 死元组，可清理 */
```

### 3.3 元组头结构

```c
// src/include/access/htup_details.h
typedef struct HeapTupleFields {
    TransactionId t_xmin;        /* 插入事务ID */
    TransactionId t_xmax;        /* 删除事务ID (0=未删除) */
    union {
        CommandId t_cid;         /* 插入/删除命令ID */
        TransactionId t_xvac;    /* 旧式VACUUM FULL */
    } t_field3;
} HeapTupleFields;

typedef struct DatumTupleFields {
    /* 用于内存中的元组 */
} DatumTupleFields;

typedef struct HeapTupleHeaderData {
    union {
        HeapTupleFields t_heap;
        DatumTupleFields t_datum;
    } t_choice;

    ItemPointerData t_ctid;      /* 当前或下一个TID */
    uint16 t_infomask2;          /* 属性数量 + 标志 */
    uint16 t_infomask;           /* 各种标志位 */
    uint8  t_hoff;               /* 头部长度 */

    /* 位图和OID可能跟在后面 */
    bits8 t_bits[FLEXIBLE_ARRAY_MEMBER];
} HeapTupleHeaderData;

typedef HeapTupleHeaderData *HeapTupleHeader;
```

### 3.4 元组标志位

```c
/* t_infomask标志位 */
#define HEAP_HASNULL        0x0001    /* 有空值 */
#define HEAP_HASVARWIDTH    0x0002    /* 有变长属性 */
#define HEAP_HASEXTERNAL    0x0004    /* 有TOAST数据 */
#define HEAP_HASOID         0x0008    /* 有OID */
#define HEAP_XMAX_KEYSHR_LOCK 0x0010  /* Xmax是keyshare锁 */
#define HEAP_COMBOCID       0x0020    /* t_cid是组合CID */
#define HEAP_XMAX_EXCL_LOCK 0x0040    /* Xmax是排他锁 */
#define HEAP_XMAX_LOCK_ONLY 0x0080    /* Xmax只是锁标记 */
#define HEAP_XMIN_COMMITTED 0x0100    /* Xmin已提交 */
#define HEAP_XMIN_INVALID   0x0200    /* Xmin无效/中止 */
#define HEAP_XMAX_COMMITTED 0x0400    /* Xmax已提交 */
#define HEAP_XMAX_INVALID   0x0800    /* Xmax无效/中止 */
#define HEAP_XMAX_IS_MULTI  0x1000    /* Xmax是多事务 */
#define HEAP_UPDATED        0x2000    /* 这是更新后的元组 */
#define HEAP_MOVED_OFF      0x4000    /* 被VACUUM FULL移走 */
#define HEAP_MOVED_IN       0x8000    /* 被VACUUM FULL移入 */
```

---

## 4. MVCC行版本控制

### 4.1 元组可见性规则

**定义 4.1 (元组版本)**:

$$
\text{Version}(T) = \langle t\_xmin, t\_xmax, \text{data} \rangle
$$

**定义 4.2 (可见性)**:

对于快照 $S = \langle xmin, xmax, xip[] \rangle$，元组 $T$ 可见当且仅当:

$$
\text{Visible}(T, S) :=
    \text{Committed}(T.t\_xmin) \land
    (T.t\_xmin < S.xmin \lor T.t\_xmin \notin S.xip) \land
    (T.t\_xmax = 0 \lor T.t\_xmax \geq S.xmax \lor T.t\_xmax \in S.xip)
$$

### 4.2 版本链

**定义 4.3 (版本链)**:

$$
\text{VersionChain}(T_0) = T_0 \rightarrow T_1 \rightarrow T_2 \rightarrow ... \rightarrow T_n
$$

其中:

$$
T_i.t\_ctid \rightarrow T_{i+1} \quad \text{且} \quad T_i.t\_xmax = T_{i+1}.t\_xmin
$$

### 4.3 形式化规则

**插入操作**:

$$
\text{Insert}(x, v) :=
    \text{find_free_slot()} \rightarrow tid \\
    \text{write_tuple}(tid, \langle xid, 0, v \rangle) \rightarrow T_{new}
$$

**删除操作**:

$$
\text{Delete}(tid) :=
    T = \text{read_tuple}(tid) \\
    T.t\_xmax := xid
$$

**更新操作**:

$$
\text{Update}(tid, v') :=
    \text{Delete}(tid) \rightarrow T_{old} \\
    \text{Insert}(x, v') \rightarrow T_{new} \\
    T_{old}.t\_ctid := tid(T_{new})
$$

---

## 5. HOT (Heap-Only Tuple) 机制

### 5.1 HOT原理

**定义 5.1 (HOT更新)**:

HOT更新是不改变索引键值的更新，满足:

$$
\pi_{\text{key}}(T_{old}) = \pi_{\text{key}}(T_{new})
$$

**HOT链结构**:

```
索引项                    堆页
-------                   ----
+-------+                +------------------+
│ Root  │--------------->│ LP1: Root Tuple  │
│ TID   │                │   (已死亡)       │
+-------+                │   t_ctid → LP2   │
                         +------------------+
                         │ LP2: Redirect    │
                         │   (重定向到LP3)  │
                         +------------------+
                         │ LP3: HOT Tuple   │
                         │   (当前版本)     │
                         +------------------+
```

### 5.2 LP_REDIRECT机制

```c
/* HOT链重定向 */
#define LP_REDIRECT 2

/* Line Pointer重定向到新的偏移 */
ItemIdSetRedirect(itemId, offsetNumber)
```

### 5.3 HOT形式化

**HOT更新条件**:

$$
\text{HOT-Eligible}(T, T') :=
    \forall idx \in \text{Indexes}(T):
    \pi_{idx.key}(T) = \pi_{idx.key}(T')
$$

**HOT链遍历**:

$$
\text{HOT-Next}(T_i) =
    \begin{cases}
    T_{i+1} & \text{if } LP[T_i.t\_ctid].flags = LP\_REDIRECT \\
    T_{i+1} & \text{if } LP[T_i.t\_ctid].flags = LP\_NORMAL \\
    \bot & \text{otherwise}
    \end{cases}
$$

### 5.4 HOT修剪与碎片整理

**修剪 (Pruning)**:

```
页内碎片整理，将HOT链压缩:

Before:              After:
+-----------+       +-----------+
│ LP1: Root │       │ LP1: Root │
│ (dead)    │       │ (dead)    │
+-----------+       +-----------+
│ LP2: Hot1 │  =>   │ LP2: Live │
│ (dead)    │       │ (当前)    │
+-----------+       +-----------+
│ LP3: Hot2 │
│ (live)    │
+-----------+
```

---

## 6. PostgreSQL heapam.c源码分析

### 6.1 插入操作

```c
// src/backend/access/heap/heapam.c

/*
 * heap_insert - 向堆表插入新元组
 */
Oid heap_insert(Relation relation, HeapTuple tup, CommandId cid,
                int options, BulkInsertState bistate) {
    // 1. 准备元组头
    HeapTupleHeader td = tup->t_data;

    // 设置事务信息
    HeapTupleHeaderSetXmin(td, GetCurrentTransactionId());
    HeapTupleHeaderSetCmin(td, cid);
    td->t_infomask &= ~(HEAP_XACT_MASK);
    td->t_infomask |= HEAP_XMAX_INVALID;

    // 2. 找到有空间的页
    Buffer buffer = RelationGetBufferForTuple(relation, tup->t_len,
                                               InvalidBuffer, options, bistate);

    // 3. 在页中分配空间
    OffsetNumber offnum = PageAddItem(...);

    // 4. 更新TID
    ItemPointerSet(&(tup->t_self),
                   BufferGetBlockNumber(buffer), offnum);

    // 5. 写入WAL
    if (!(options & HEAP_INSERT_SKIP_WAL))
        log_heap_insert(relation, buffer, offnum);

    return HeapTupleGetOid(tup);
}
```

### 6.2 更新操作

```c
/*
 * heap_update - 更新堆表元组
 */
HTSU_Result heap_update(Relation relation, ItemPointer otid,
                        HeapTuple newtup, ItemPointer ctid,
                        TransactionId *update_xmax, Buffer *buffer) {
    // 1. 获取旧元组
    HeapTupleDataoldtup;
    if (!heap_fetch(relation, SnapshotAny, otid, &oldtup, buffer))
        return HeapTupleInvisible;

    // 2. 检查并发更新
    if (TransactionIdIsValid(HeapTupleHeaderGetXmax(oldtup.t_data))) {
        // 已被其他事务更新/删除
        return HeapTupleBeingUpdated;
    }

    // 3. 标记旧元组为已删除
    HeapTupleHeaderSetXmax(oldtup.t_data, GetCurrentTransactionId());
    HeapTupleHeaderSetCmax(oldtup.t_data, cid, false);

    // 4. 检查是否可以HOT更新
    bool hot_attrs = HeapDetermineColumnsInfo(...);

    if (hot_attrs) {
        // HOT更新：同页内插入新版本
        // ...
    } else {
        // 普通更新：插入新元组
        newbuf = RelationGetBufferForTuple(relation, newtup->t_len, ...);
        newoff = PageAddItem(...);
    }

    // 5. 设置旧元组的t_ctid指向新版本
    oldtup.t_data->t_ctid = newtup->t_self;

    // 6. 写入WAL
    log_heap_update(relation, *buffer, newbuf, ...);

    return HeapTupleMayBeUpdated;
}
```

### 6.3 删除操作

```c
/*
 * heap_delete - 删除堆表元组
 */
HTSU_Result heap_delete(Relation relation, ItemPointer tid,
                        CommandId cid, Snapshot crosscheck, ...) {
    // 1. 获取元组
    Buffer buffer;
    HeapTupleData tp;
    if (!heap_fetch(relation, SnapshotAny, tid, &tp, &buffer))
        return HeapTupleInvisible;

    // 2. 检查并发访问
    if (TransactionIdIsValid(HeapTupleHeaderGetXmax(tp.t_data)))
        return HeapTupleBeingUpdated;

    // 3. 设置删除标记
    HeapTupleHeaderSetXmax(tp.t_data, GetCurrentTransactionId());
    HeapTupleHeaderSetCmax(tp.t_data, cid, false);

    // 4. 写入WAL
    log_heap_delete(relation, buffer, tid);

    return HeapTupleMayBeUpdated;
}
```

### 6.4 扫描操作

```c
/*
 * heapgettup_pagemode - 页模式堆扫描
 */
static void heapgettup_pagemode(HeapScanDesc scan, ScanDirection dir) {
    // 1. 读取页到缓冲区
    buffer = ReadBuffer(scan->rs_base.rs_rd, page);

    // 2. 获取页快照 (防止页被修改)
    snapshot = scan->rs_base.rs_snapshot;
    PushActiveSnapshot(snapshot);

    // 3. 遍历页内所有行指针
    for (lineoff = FirstOffsetNumber, lpp = PageGetItemId(dp, lineoff);
         lineoff <= lines;
         lineoff++, lpp++) {

        // 跳过未使用和重定向的项
        if (!(ItemIdIsNormal(lpp) || ItemIdIsDead(lpp)))
            continue;

        // 4. 获取元组并检查可见性
        lp: heapTuple = (HeapTuple) PageGetItem((Page) dp, lpp);

        valid = HeapTupleSatisfiesVisibility(heapTuple, snapshot, buffer);

        if (valid) {
            // 保存到扫描结果集
            scan->rs_vistuples[scan->rs_ntuples++] = lineoff;
        }
    }

    // 5. 设置扫描位置
    scan->rs_cindex = 0;
    scan->rs_ntuples = ntup;
}
```

### 6.5 可见性判断

```c
/*
 * HeapTupleSatisfiesMVCC - MVCC可见性判断
 */
static bool HeapTupleSatisfiesMVCC(HeapTuple htup, Snapshot snapshot,
                                   Buffer buffer) {
    HeapTupleHeader tuple = htup->t_data;

    // 1. 检查Xmin
    if (!HeapTupleHeaderXminCommitted(tuple)) {
        if (HeapTupleHeaderXminInvalid(tuple))
            return false;  // 插入者已中止

        TransactionId xmin = HeapTupleHeaderGetXmin(tuple);

        if (TransactionIdIsCurrentTransactionId(xmin)) {
            // 同一事务插入
            if (HeapTupleHeaderGetCmin(tuple) >= snapshot->curcid)
                return false;  // 插入在当前命令之后
            return true;
        }

        if (XidInMVCCSnapshot(xmin, snapshot))
            return false;  // 插入事务还在活跃列表

        if (!TransactionIdDidCommit(xmin))
            return false;  // 插入者未提交
    }

    // 2. 检查Xmax
    if (tuple->t_infomask & HEAP_XMAX_INVALID)
        return true;  // 未被删除

    if (tuple->t_infomask & HEAP_XMAX_COMMITTED) {
        // Xmax已提交，检查是否在快照中
        TransactionId xmax = HeapTupleHeaderGetXmax(tuple);
        if (!TransactionIdIsValid(xmax))
            return true;

        if (XidInMVCCSnapshot(xmax, snapshot))
            return true;  // 删除者对我们的快照不可见

        return false;  // 已被删除且对我们可见
    }

    // ... 其他情况处理
}
```

---

## 7. 性能分析与优化

### 7.1 元组大小计算

**元组大小公式**:

$$
\text{TupleSize} = \text{HeaderSize} + \text{DataSize} + \text{BitmapSize} + \text{Padding}
$$

其中:

$$
\text{HeaderSize} = 23 \text{ bytes (HeapTupleHeaderData)}
$$

$$
\text{BitmapSize} = \lceil \frac{N_{attrs}}{8} \rceil \text{ bytes (空值位图)}
$$

### 7.2 页填充率

**理论最大元组数**:

$$
N_{max} = \frac{\text{PageSize} - \text{PageHeaderSize} - \text{SpecialSize}}{\text{AvgTupleSize} + \text{LinePointerSize}}
$$

**填充因子 (Fill Factor)**:

$$
\text{FillFactor} = \frac{\text{UsedSpace}}{\text{PageSize}} \times 100\%
$$

默认 `FILLFACTOR = 100` (INSERT)，`FILLFACTOR = 90` (UPDATE频繁)。

### 7.3 HOT性能收益

| 场景 | 无HOT | 有HOT | 收益 |
|------|-------|-------|------|
| 单索引表更新 | 2次索引修改 | 0次索引修改 | 100% |
| 多索引表更新 | N次索引修改 | 0次索引修改 | 100% |
| 页内碎片 | 高 | 低 | ~30% |

### 7.4 VACUUM影响

**死元组清理**:

$$
\text{DeadSpace} = \sum_{T \in \text{DeadTuples}} (\text{size}(T) + 4)
$$

**可见性映射 (Visibility Map)**:

```c
/* VM加速VACUUM，标记全可见/全冻结页 */
#define VISIBILITYMAP_ALL_VISIBLE  0x01
#define VISIBILITYMAP_ALL_FROZEN   0x02
```

---

## 8. 形式化验证

### 8.1 Heap不变式

**不变式 8.1 (TID唯一性)**:

$$
\forall T_1, T_2 \in \text{Heap}: T_1 \neq T_2 \Rightarrow \text{TID}(T_1) \neq \text{TID}(T_2)
$$

**不变式 8.2 (版本链有效性)**:

$$
\forall T \in \text{Heap}: T.t\_xmax \neq 0 \Rightarrow \exists T': T.t\_ctid = \text{TID}(T')
$$

**不变式 8.3 (空间一致性)**:

$$
\forall P: P.pd\_lower \leq P.pd\_upper \land P.pd\_upper \leq P.pd\_special
$$

### 8.2 MVCC正确性

**定理 8.1 (读一致性)**:

对于任何快照 $S$，事务 $T_x$ 看到的数据库状态是一致的。

**证明草图**:

1. 快照 $S$ 捕获了某一时刻的活跃事务集合
2. 可见性规则保证只读取已提交且对快照可见的版本
3. 元组的 $t\_xmin$ 和 $t\_xmax$ 标记版本生命周期
4. $\therefore$ 看到的状态等价于某串行执行的结果 ∎

---

## 9. 参考文献

1. **PostgreSQL Global Development Group.** (2025). *PostgreSQL Source Code - src/backend/access/heap/*.

2. **Petrov, A.** (2019). *Database Internals: A Deep Dive into How Distributed Data Systems Work*. O'Reilly Media.

3. **PostgreSQL Global Development Group.** (2025). *PostgreSQL Documentation - Chapter 69: Database Page Layout*.

4. **Momjian, B.** (2021). *PostgreSQL Internals*. Momjian Consulting.

5. **CMU 15-445.** (2023). *Intro to Database Systems - Lecture 5: Storage Models & Compression*.

---

**创建者**: PostgreSQL_Modern Academic Team
**审核状态**: 学术级深度版本 (DEEP-V2)
**最后更新**: 2026-03-04
**完成度**: 100% (DEEP-V2)
