---

> **📋 文档来源**: `MVCC-ACID-CAP\03-场景实践\分布式系统\Citus分布式PostgreSQL的CAP.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# Citus分布式PostgreSQL的CAP

> **文档编号**: CAP-PRACTICE-007
> **主题**: Citus分布式PostgreSQL的CAP
> **版本**: PostgreSQL 17 & 18
> **状态**: ✅ 已完成

---

## 📑 目录

- [Citus分布式PostgreSQL的CAP](#citus分布式postgresql的cap)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [📊 第一部分：Citus架构基础](#-第一部分citus架构基础)
    - [1.1 Citus架构定义](#11-citus架构定义)
    - [1.2 协调节点与工作节点](#12-协调节点与工作节点)
    - [1.3 分片机制](#13-分片机制)
  - [📊 第二部分：Citus的CAP定位](#-第二部分citus的cap定位)
    - [2.1 Citus CAP分析](#21-citus-cap分析)
    - [2.2 Citus一致性模型](#22-citus一致性模型)
    - [2.3 Citus可用性保证](#23-citus可用性保证)
  - [📊 第三部分：Citus的分区容错](#-第三部分citus的分区容错)
    - [3.1 分区容错机制](#31-分区容错机制)
    - [3.2 分片故障处理](#32-分片故障处理)
    - [3.3 分区恢复策略](#33-分区恢复策略)
  - [📊 第四部分：Citus分布式事务与CAP](#-第四部分citus分布式事务与cap)
    - [4.1 单分片事务](#41-单分片事务)
    - [4.2 跨分片事务](#42-跨分片事务)
    - [4.3 分布式事务CAP](#43-分布式事务cap)
  - [📊 第五部分：Citus CAP实践指南](#-第五部分citus-cap实践指南)
    - [5.1 Citus CAP配置](#51-citus-cap配置)
    - [5.2 Citus CAP优化](#52-citus-cap优化)
    - [5.3 Citus CAP监控](#53-citus-cap监控)
  - [📝 总结](#-总结)
    - [核心结论](#核心结论)
    - [实践建议](#实践建议)

---

## 📋 概述

Citus是PostgreSQL的分布式扩展，它将PostgreSQL扩展到多节点集群。理解Citus的CAP定位，有助于设计高可用的分布式PostgreSQL系统。

本文档从Citus架构、CAP定位、分区容错、分布式事务和实践指南五个维度，全面阐述Citus分布式PostgreSQL的CAP完整体系。

**核心观点**：

- **Citus CAP定位**：通常采用CP模式
- **Citus一致性模型**：强一致性（线性一致性）
- **Citus可用性**：分片故障不影响其他分片
- **Citus分区容错**：网络分区时继续运行

---

## 📊 第一部分：Citus架构基础

### 1.1 Citus架构定义

**Citus架构**：

Citus采用**协调节点（Coordinator）**和**工作节点（Worker）**的架构：

```text
协调节点 (Coordinator)
  │
  ├─ 工作节点1 (Worker) - 分片1
  ├─ 工作节点2 (Worker) - 分片2
  └─ 工作节点3 (Worker) - 分片3
```

**Citus组件**：

- **协调节点**：接收客户端请求，路由到工作节点
- **工作节点**：存储分片数据，执行查询
- **分片**：数据分片，分布在多个工作节点

### 1.2 协调节点与工作节点

**协调节点功能**：

- 接收客户端请求
- 解析SQL查询
- 路由查询到工作节点
- 聚合结果返回客户端

**工作节点功能**：

- 存储分片数据
- 执行查询
- 返回结果给协调节点

### 1.3 分片机制

**分片策略**：

| 分片策略 | 说明 | 适用场景 |
|---------|------|---------|
| **哈希分片** | 按哈希值分片 | 均匀分布数据 |
| **范围分片** | 按范围分片 | 时间序列数据 |
| **复制分片** | 复制分片到多个节点 | 高可用性 |

**分片示例**：

```sql
-- 创建分布式表
CREATE TABLE orders (
    id SERIAL,
    user_id INT,
    amount DECIMAL
);

-- 分片表
SELECT create_distributed_table('orders', 'user_id');
```

---

## 📊 第二部分：Citus的CAP定位

### 2.1 Citus CAP分析

**Citus CAP定位**：

| CAP属性 | Citus | 说明 |
|---------|-------|------|
| **C (一致性)** | ✅ 强 | 强一致性（线性一致性） |
| **A (可用性)** | ⚠️ 部分 | 分片故障不影响其他分片 |
| **P (分区容错)** | ✅ 高 | 网络分区时继续运行 |

**Citus CAP模式**：**CP模式**

### 2.2 Citus一致性模型

**Citus一致性模型**：

- ✅ **强一致性**：所有节点看到相同数据
- ✅ **线性一致性**：操作按全局顺序执行
- ✅ **ACID保证**：支持ACID事务

**Citus一致性实现**：

```sql
-- Citus强一致性配置
SET citus.shard_count = 32;
SET citus.replication_factor = 2;  -- 每个分片2个副本

-- 分布式事务
BEGIN;
INSERT INTO orders VALUES (1, 100, 1000);
COMMIT;  -- 保证所有分片一致提交
```

### 2.3 Citus可用性保证

**Citus可用性特征**：

- ✅ **分片隔离**：分片故障不影响其他分片
- ✅ **副本冗余**：每个分片有多个副本
- ⚠️ **部分可用性**：部分分片故障时，相关查询可能失败

**Citus可用性配置**：

```sql
-- 设置副本数
SET citus.replication_factor = 2;

-- 监控分片状态
SELECT * FROM citus_shards;
```

---

## 📊 第三部分：Citus的分区容错

### 3.1 分区容错机制

**Citus分区容错**：

1. **分片副本**
   - 每个分片有多个副本
   - 副本分布在不同节点
   - 节点故障时切换到副本

2. **协调节点冗余**
   - 多个协调节点
   - 协调节点故障时切换
   - 保证服务可用性

**Citus配置**：

```sql
-- 设置副本数
SET citus.replication_factor = 2;

-- 添加工作节点
SELECT citus_add_node('worker1', 5432);
SELECT citus_add_node('worker2', 5432);
```

### 3.2 分片故障处理

**分片故障处理**：

```text
1. 检测分片故障
   │
2. 切换到分片副本
   │
3. 恢复分片服务
   │
4. 同步数据差异
```

**Citus故障处理**：

```sql
-- 监控分片状态（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法监控分片状态';
            RETURN;
        END IF;
        RAISE NOTICE '开始监控Citus分片状态';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    shardid,
    shardstate,
    shardlength,
    nodename,
    nodeport
FROM citus_shards;

-- 处理分片故障（带错误处理）
DO $$
DECLARE
    v_result TEXT;
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法启动分片重平衡';
            RETURN;
        END IF;

        BEGIN
            SELECT citus_rebalance_start() INTO v_result;
            RAISE NOTICE '分片重平衡已启动: %', v_result;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '启动分片重平衡失败: %', SQLERRM;
                RAISE;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 3.3 分区恢复策略

**恢复策略**：

1. **自动恢复**：Citus自动切换到副本
2. **手动恢复**：手动处理分片故障
3. **数据恢复**：从副本恢复数据

---

## 📊 第四部分：Citus分布式事务与CAP

### 4.1 单分片事务

**单分片事务**：

- ✅ **强一致性**：单分片内强一致性
- ✅ **高性能**：无需跨节点协调
- ✅ **低延迟**：本地事务处理

**单分片事务示例**：

```sql
-- 单分片事务（user_id=100在同一分片，带错误处理和性能测试）
DO $$
DECLARE
    v_updated INTEGER;
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法执行分布式事务';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行单分片事务';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行单分片事务（user_id=100在同一分片）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;
        UPDATE orders SET amount = amount + 100 WHERE user_id = 100;
        GET DIAGNOSTICS v_updated = ROW_COUNT;

        IF v_updated = 0 THEN
            RAISE WARNING '未更新任何记录（user_id=100可能不存在）';
        ELSE
            RAISE NOTICE '单分片事务更新成功: 更新了 % 条记录', v_updated;
        END IF;

        COMMIT;
        RAISE NOTICE '单分片事务提交成功（强一致性）';
    EXCEPTION
        WHEN check_violation THEN
            ROLLBACK;
            RAISE WARNING '金额约束违反';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '单分片事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：单分片事务
EXPLAIN (ANALYZE, BUFFERS, TIMING)
UPDATE orders SET amount = amount + 100 WHERE user_id = 100;
```

### 4.2 跨分片事务

**跨分片事务**：

- ⚠️ **一致性复杂**：需要保证所有分片一致
- ❌ **低可用性**：任一分片故障导致事务失败
- ⚠️ **高延迟**：需要跨节点协调

**跨分片事务示例**：

```sql
-- 跨分片事务（user_id=100和200在不同分片，带错误处理和性能测试）
DO $$
DECLARE
    v_updated1 INTEGER;
    v_updated2 INTEGER;
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法执行分布式事务';
            RETURN;
        END IF;

        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE WARNING '表 orders 不存在，无法执行跨分片事务';
            RETURN;
        END IF;
        RAISE NOTICE '开始执行跨分片事务（user_id=100和200在不同分片）';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '操作准备失败: %', SQLERRM;
            RAISE;
    END;

    BEGIN
        BEGIN;
        -- 第一个分片更新
        UPDATE orders SET amount = amount + 100 WHERE user_id = 100;
        GET DIAGNOSTICS v_updated1 = ROW_COUNT;

        IF v_updated1 = 0 THEN
            RAISE WARNING '第一个分片未更新任何记录（user_id=100可能不存在）';
        ELSE
            RAISE NOTICE '第一个分片更新成功: 更新了 % 条记录', v_updated1;
        END IF;

        -- 第二个分片更新
        UPDATE orders SET amount = amount - 100 WHERE user_id = 200;
        GET DIAGNOSTICS v_updated2 = ROW_COUNT;

        IF v_updated2 = 0 THEN
            RAISE WARNING '第二个分片未更新任何记录（user_id=200可能不存在）';
        ELSE
            RAISE NOTICE '第二个分片更新成功: 更新了 % 条记录', v_updated2;
        END IF;

        COMMIT;
        RAISE NOTICE '跨分片事务提交成功（需要两阶段提交，强一致性）';
    EXCEPTION
        WHEN check_violation THEN
            ROLLBACK;
            RAISE WARNING '金额约束违反';
            RAISE;
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE WARNING '跨分片事务失败: %', SQLERRM;
            RAISE;
    END;
END $$;

-- 性能测试：跨分片事务
EXPLAIN (ANALYZE, BUFFERS, TIMING)
UPDATE orders SET amount = amount + 100 WHERE user_id = 100;
```

### 4.3 分布式事务CAP

**分布式事务CAP分析**：

| 事务类型 | CAP模式 | 说明 |
|---------|---------|------|
| **单分片事务** | CP | 强一致性，高性能 |
| **跨分片事务** | CP | 强一致性，低可用性 |

---

## 📊 第五部分：Citus CAP实践指南

### 5.1 Citus CAP配置

**Citus CAP配置**：

```sql
-- CP模式配置（带错误处理）
DO $$
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法配置Citus参数';
            RETURN;
        END IF;

        BEGIN
            SET LOCAL citus.replication_factor = 2;  -- 副本数
            RAISE NOTICE 'Citus副本数已设置为2';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置Citus副本数失败: %', SQLERRM;
        END;

        BEGIN
            SET LOCAL citus.shard_count = 32;  -- 分片数
            RAISE NOTICE 'Citus分片数已设置为32';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置Citus分片数失败: %', SQLERRM;
        END;

        BEGIN
            SET LOCAL default_transaction_isolation = 'serializable';
            RAISE NOTICE '默认事务隔离级别已设置为可串行化（强一致性）';
        EXCEPTION
            WHEN OTHERS THEN
                RAISE WARNING '设置事务隔离级别失败: %', SQLERRM;
        END;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '配置失败: %', SQLERRM;
            RAISE;
    END;
END $$;
```

### 5.2 Citus CAP优化

**优化策略**：

1. **避免跨分片事务**：尽量在单分片内完成事务
2. **合理分片设计**：根据查询模式设计分片
3. **副本配置**：设置合理的副本数

### 5.3 Citus CAP监控

**监控指标**：

```sql
-- 监控分片状态（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法监控分片状态';
            RETURN;
        END IF;
        RAISE NOTICE '开始监控Citus分片状态';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    shardid,
    shardstate,
    nodename,
    nodeport
FROM citus_shards;

-- 监控分布式事务（带错误处理和性能测试）
DO $$
BEGIN
    BEGIN
        -- 检查Citus扩展是否已安装
        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'citus') THEN
            RAISE WARNING 'Citus扩展未安装，无法监控分布式事务';
            RETURN;
        END IF;
        RAISE NOTICE '开始监控Citus分布式事务';
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '监控准备失败: %', SQLERRM;
            RAISE;
    END;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM citus_distributed_transactions;
```

---

## 📝 总结

### 核心结论

1. **Citus CAP定位**：通常采用CP模式
2. **Citus一致性模型**：强一致性（线性一致性）
3. **Citus可用性**：分片故障不影响其他分片
4. **Citus分区容错**：网络分区时继续运行

### 实践建议

1. **理解Citus CAP定位**：Citus采用CP模式
2. **优化分片设计**：避免跨分片事务
3. **配置副本数**：设置合理的副本数保证可用性
4. **监控Citus状态**：实时监控分片和事务状态

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
