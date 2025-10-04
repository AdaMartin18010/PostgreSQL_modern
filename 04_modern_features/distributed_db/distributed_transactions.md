# 分布式事务与幂等补偿

> 基于分布式系统理论，结合PostgreSQL生态实践

## 📋 目录

- [分布式事务与幂等补偿](#分布式事务与幂等补偿)
  - [📋 目录](#-目录)
  - [1. 分布式事务基础](#1-分布式事务基础)
    - [1.1 ACID在分布式环境的挑战](#11-acid在分布式环境的挑战)
    - [1.2 分布式事务的类型](#12-分布式事务的类型)
  - [2. 两阶段提交（2PC）](#2-两阶段提交2pc)
    - [2.1 协议流程](#21-协议流程)
    - [2.2 PostgreSQL中的2PC实现](#22-postgresql中的2pc实现)
    - [2.3 2PC的优势与局限](#23-2pc的优势与局限)
  - [3. 三阶段提交（3PC）](#3-三阶段提交3pc)
  - [4. 补偿事务与Saga模式](#4-补偿事务与saga模式)
    - [4.1 Saga模式原理](#41-saga模式原理)
    - [4.2 PostgreSQL实现示例](#42-postgresql实现示例)
  - [5. 幂等性设计](#5-幂等性设计)
    - [5.1 幂等键设计](#51-幂等键设计)
    - [5.2 去重表模式](#52-去重表模式)
  - [6. Outbox模式](#6-outbox模式)
    - [6.1 模式原理](#61-模式原理)
    - [6.2 PostgreSQL实现](#62-postgresql实现)
  - [7. 跨分片事务策略](#7-跨分片事务策略)
    - [7.1 单分片优先](#71-单分片优先)
    - [7.2 Citus分布式事务](#72-citus分布式事务)
  - [8. 隔离级别与一致性权衡](#8-隔离级别与一致性权衡)
  - [9. 故障恢复与补偿](#9-故障恢复与补偿)
  - [10. 工程实践建议](#10-工程实践建议)
  - [参考资源](#参考资源)

## 1. 分布式事务基础

### 1.1 ACID在分布式环境的挑战

**单机ACID vs 分布式ACID**:

- **原子性（Atomicity）**：跨节点的所有操作要么全部成功，要么全部失败
  - 挑战：部分节点失败，如何保证全局原子性
  - 解决：协调者协议（2PC/3PC）或补偿机制（Saga）

- **一致性（Consistency）**：分布式环境下维护业务规则
  - 挑战：跨分片的约束检查和外键关系
  - 解决：应用层验证或最终一致性

- **隔离性（Isolation）**：分布式锁和全局快照
  - 挑战：跨节点的并发控制和死锁检测
  - 解决：分布式锁管理器或乐观并发控制

- **持久性（Durability）**：多副本的持久化保证
  - 挑战：确保数据在多个节点持久化
  - 解决：仲裁写入或同步复制

### 1.2 分布式事务的类型

**强一致性事务**:

- 特点：保证严格的ACID属性
- 实现：2PC、3PC、Paxos Commit
- 适用：金融交易、库存管理
- 代价：高延迟、低可用性

**最终一致性事务**:

- 特点：允许短暂的不一致
- 实现：Saga、补偿事务、事件溯源
- 适用：订单处理、用户注册
- 优势：高可用性、低延迟

## 2. 两阶段提交（2PC）

### 2.1 协议流程

**准备阶段（Prepare Phase）**:

1. 协调者向所有参与者发送PREPARE请求
2. 参与者执行事务操作，写入重做和撤销日志
3. 参与者返回YES（准备就绪）或NO（中止）

**提交阶段（Commit Phase）**:

1. 如果所有参与者返回YES，协调者发送COMMIT
2. 如果任何参与者返回NO，协调者发送ROLLBACK
3. 参与者执行最终操作并返回确认

### 2.2 PostgreSQL中的2PC实现

```sql
-- 参与者节点1
BEGIN;
INSERT INTO orders (user_id, amount) VALUES (123, 100.00);
PREPARE TRANSACTION 'txn_order_123';

-- 参与者节点2
BEGIN;
UPDATE accounts SET balance = balance - 100.00 WHERE user_id = 123;
PREPARE TRANSACTION 'txn_payment_123';

-- 协调者决策：如果所有节点准备成功，提交
COMMIT PREPARED 'txn_order_123';
COMMIT PREPARED 'txn_payment_123';

-- 查看准备好的事务
SELECT * FROM pg_prepared_xacts;
```

### 2.3 2PC的优势与局限

**优势**:

- 保证强一致性和原子性
- 实现相对简单
- PostgreSQL原生支持

**局限**:

- 阻塞问题：参与者在准备后需要等待协调者决策
- 单点故障：协调者失败导致事务无法完成
- 性能开销：需要多次网络往返和持久化日志
- 锁持有时间长：影响并发性能

## 3. 三阶段提交（3PC）

3PC通过引入预提交阶段来减少阻塞：

1. **CanCommit阶段**：询问参与者是否可以提交
2. **PreCommit阶段**：参与者确认可以提交，但不提交
3. **DoCommit阶段**：最终提交或中止

**实际应用**：3PC在实践中应用较少，因为实现复杂且仍然无法完全避免阻塞。

## 4. 补偿事务与Saga模式

### 4.1 Saga模式原理

将长事务分解为多个本地事务，每个本地事务都有对应的补偿操作：

- **正向操作**：执行业务逻辑（Ti）
- **补偿操作**：撤销业务逻辑（Ci）

### 4.2 PostgreSQL实现示例

```sql
-- 创建Saga状态表
CREATE TABLE saga_state (
    saga_id UUID PRIMARY KEY,
    saga_type TEXT NOT NULL,
    current_step INTEGER NOT NULL,
    status TEXT NOT NULL, -- PENDING, COMPLETED, COMPENSATING, FAILED
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Saga执行函数
CREATE OR REPLACE FUNCTION execute_saga_step(
    p_saga_id UUID,
    p_step_number INTEGER,
    p_step_name TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    v_success BOOLEAN;
BEGIN
    -- 记录步骤开始
    INSERT INTO saga_steps (saga_id, step_number, step_name, status, executed_at)
    VALUES (p_saga_id, p_step_number, p_step_name, 'PENDING', NOW());
    
    -- 执行业务操作
    -- v_success := execute_business_logic();
    
    -- 更新步骤状态
    UPDATE saga_steps 
    SET status = CASE WHEN v_success THEN 'SUCCESS' ELSE 'FAILED' END
    WHERE saga_id = p_saga_id AND step_number = p_step_number;
    
    RETURN v_success;
END;
$$ LANGUAGE plpgsql;
```

## 5. 幂等性设计

### 5.1 幂等键设计

**原则**:

- 使用业务唯一标识作为幂等键
- 幂等键应该包含足够的上下文信息
- 避免使用自增ID或时间戳

### 5.2 去重表模式

```sql
-- 创建去重表
CREATE TABLE idempotency_keys (
    idempotency_key TEXT PRIMARY KEY,
    request_data JSONB NOT NULL,
    response_data JSONB,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- 幂等处理函数
CREATE OR REPLACE FUNCTION process_idempotent_request(
    p_key TEXT,
    p_request_data JSONB
) RETURNS JSONB AS $$
DECLARE
    v_existing RECORD;
BEGIN
    SELECT * INTO v_existing
    FROM idempotency_keys
    WHERE idempotency_key = p_key
    FOR UPDATE SKIP LOCKED;
    
    IF FOUND AND v_existing.status = 'COMPLETED' THEN
        RETURN v_existing.response_data;
    END IF;
    
    -- 执行业务逻辑
    -- ...
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

## 6. Outbox模式

### 6.1 模式原理

通过在同一个本地事务中写入业务数据和事件消息，保证数据一致性：

1. 在本地事务中同时写入业务表和outbox表
2. 独立进程读取outbox表并发送消息
3. 消息发送成功后标记或删除outbox记录

### 6.2 PostgreSQL实现

```sql
-- 创建Outbox表
CREATE TABLE outbox_events (
    event_id BIGSERIAL PRIMARY KEY,
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- 业务操作 + Outbox写入
CREATE OR REPLACE FUNCTION create_order_with_event(
    p_user_id BIGINT,
    p_amount NUMERIC
) RETURNS BIGINT AS $$
DECLARE
    v_order_id BIGINT;
BEGIN
    INSERT INTO orders (user_id, amount, status)
    VALUES (p_user_id, p_amount, 'CREATED')
    RETURNING id INTO v_order_id;
    
    INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload)
    VALUES ('Order', v_order_id::TEXT, 'OrderCreated',
            jsonb_build_object('order_id', v_order_id, 'amount', p_amount));
    
    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;
```

## 7. 跨分片事务策略

### 7.1 单分片优先

**设计原则**:

- 尽量将相关数据放在同一分片
- 选择合适的分片键保证数据局部性
- 大部分事务在单分片内完成

### 7.2 Citus分布式事务

```sql
-- Citus自动处理分布式事务
BEGIN;
UPDATE orders SET status = 'COMPLETED' WHERE order_id = 123;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 456;
COMMIT;
```

## 8. 隔离级别与一致性权衡

**Read Committed**（推荐）:

- 默认隔离级别
- 平衡一致性和性能
- 适用于大多数场景

**Repeatable Read**:

- 需要全局快照
- 适用于报表查询

**Serializable**:

- 性能开销大
- 仅用于关键业务

## 9. 故障恢复与补偿

```sql
-- 设置超时
SET statement_timeout = '30s';
SET idle_in_transaction_session_timeout = '60s';
SET lock_timeout = '10s';

-- 清理孤立的准备事务
SELECT gid FROM pg_prepared_xacts 
WHERE prepared < now() - interval '1 hour';
```

## 10. 工程实践建议

1. **优先使用单分片事务**：通过合理的分片键设计
2. **幂等性是必须的**：所有分布式操作都应该是幂等的
3. **超时机制**：设置合理的超时时间
4. **监控告警**：监控长事务和失败率
5. **补偿机制**：为每个操作设计补偿逻辑
6. **最终一致性**：在可能的情况下使用最终一致性
7. **避免分布式锁**：优先使用乐观并发控制
8. **定期清理**：清理孤立的准备事务和过期记录

## 参考资源

- [PostgreSQL Two-Phase Commit](<https://www.postgresql.org/docs/current/sql-prepare-transaction.htm>l)
- [Saga Pattern](<https://microservices.io/patterns/data/saga.htm>l)
- [Designing Data-Intensive Applications](<https://dataintensive.net>/)
- [Citus Distributed Transactions](<https://docs.citusdata.com>/)
