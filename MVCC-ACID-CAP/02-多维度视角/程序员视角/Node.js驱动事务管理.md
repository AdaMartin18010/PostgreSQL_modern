# Node.js驱动PostgreSQL事务管理最佳实践

> **文档编号**: DEV-NODEJS-001
> **语言**: Node.js / TypeScript
> **驱动**: pg (node-postgres)
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [Node.js驱动PostgreSQL事务管理最佳实践](#nodejs驱动postgresql事务管理最佳实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：pg基础事务管理](#-第一部分pg基础事务管理)
    - [1.1 连接管理](#11-连接管理)
      - [连接池配置](#连接池配置)
      - [连接参数优化](#连接参数优化)
    - [1.2 事务管理基础](#12-事务管理基础)
      - [基本事务操作](#基本事务操作)
      - [事务回调模式](#事务回调模式)
      - [Promise模式](#promise模式)
    - [1.3 隔离级别设置](#13-隔离级别设置)
      - [连接级隔离级别](#连接级隔离级别)
      - [事务级隔离级别](#事务级隔离级别)
    - [1.4 错误处理和重试](#14-错误处理和重试)
      - [死锁处理](#死锁处理)
      - [序列化错误处理](#序列化错误处理)
      - [重试机制实现](#重试机制实现)
  - [🚀 第二部分：连接池管理](#-第二部分连接池管理)
    - [2.1 pg.Pool配置](#21-pgpool配置)
      - [基本配置](#基本配置)
      - [MVCC优化配置](#mvcc优化配置)
    - [2.2 连接池监控](#22-连接池监控)
      - [连接池统计](#连接池统计)
      - [健康检查](#健康检查)
    - [2.3 连接池最佳实践](#23-连接池最佳实践)
      - [连接池大小设置](#连接池大小设置)
      - [连接生命周期管理](#连接生命周期管理)
  - [📊 第三部分：MVCC最佳实践](#-第三部分mvcc最佳实践)
    - [3.1 短事务原则](#31-短事务原则)
      - [避免长事务](#避免长事务)
      - [批量操作优化](#批量操作优化)
    - [3.2 并发控制](#32-并发控制)
      - [SELECT FOR UPDATE使用](#select-for-update使用)
      - [乐观锁实现](#乐观锁实现)
      - [悲观锁实现](#悲观锁实现)
    - [3.3 性能优化](#33-性能优化)
      - [预编译语句](#预编译语句)
      - [批量操作](#批量操作)
      - [连接池优化](#连接池优化)
  - [🔧 第四部分：实际场景案例](#-第四部分实际场景案例)
    - [4.1 电商库存扣减场景](#41-电商库存扣减场景)
    - [4.2 银行转账场景](#42-银行转账场景)
    - [4.3 日志写入场景](#43-日志写入场景)
  - [📝 第五部分：常见问题和解决方案](#-第五部分常见问题和解决方案)
    - [5.1 常见错误](#51-常见错误)
      - [错误1：忘记释放连接](#错误1忘记释放连接)
    - [5.2 性能问题](#52-性能问题)
      - [问题1：连接池耗尽](#问题1连接池耗尽)
    - [5.3 调试技巧](#53-调试技巧)
      - [查看事务信息](#查看事务信息)
  - [🎯 总结](#-总结)
    - [核心最佳实践](#核心最佳实践)
    - [关键配置](#关键配置)
    - [MVCC影响](#mvcc影响)

---

## 📋 概述

Node.js是PostgreSQL Web应用的主要编程语言之一，主要通过**pg**（node-postgres）驱动与PostgreSQL交互。
pg是Node.js中功能最完善的PostgreSQL驱动，支持连接池、预编译语句和批量操作。
本文档深入分析Node.js驱动在PostgreSQL MVCC环境下的最佳实践。

---

## 🔍 第一部分：pg基础事务管理

### 1.1 连接管理

#### 连接池配置

```typescript
import { Pool, PoolConfig } from 'pg';

// PostgreSQL 17/18推荐连接配置
const poolConfig: PoolConfig = {
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    user: 'postgres',
    password: 'password',

    // 连接池大小
    min: 5,
    max: 20,

    // 连接超时
    connectionTimeoutMillis: 10000,  // 10秒
    idleTimeoutMillis: 600000,       // 10分钟
    maxLifetimeMillis: 1800000,       // 30分钟

    // MVCC优化参数
    application_name: 'myapp',
    statement_timeout: 30000,         // 30秒
    idle_in_transaction_session_timeout: 300000,  // 5分钟，防止长事务
};

const pool = new Pool(poolConfig);
```

#### 连接参数优化

```typescript
// PostgreSQL 17/18推荐连接参数
const optimizedConfig: PoolConfig = {
    host: 'localhost',
    port: 5432,
    database: 'mydb',
    user: 'postgres',
    password: 'password',

    // 连接池大小（根据CPU核心数）
    min: 5,
    max: 20,

    // MVCC优化
    application_name: 'myapp',
    statement_timeout: 30000,
    idle_in_transaction_session_timeout: 300000,

    // 连接保持
    keepAlive: true,
    keepAliveInitialDelayMillis: 10000,
};
```

### 1.2 事务管理基础

#### 基本事务操作

```typescript
import { PoolClient } from 'pg';

async function transferMoney(
    pool: Pool,
    fromId: number,
    toId: number,
    amount: number
): Promise<void> {
    const client = await pool.connect();

    try {
        await client.query('BEGIN');

        // 扣减转出账户
        await client.query(
            'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
            [amount, fromId]
        );

        // 增加转入账户
        await client.query(
            'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
            [amount, toId]
        );

        await client.query('COMMIT');
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
}
```

#### 事务回调模式

```typescript
async function withTransaction<T>(
    pool: Pool,
    callback: (client: PoolClient) => Promise<T>
): Promise<T> {
    const client = await pool.connect();

    try {
        await client.query('BEGIN');
        const result = await callback(client);
        await client.query('COMMIT');
        return result;
    } catch (error) {
        await client.query('ROLLBACK');
        throw error;
    } finally {
        client.release();
    }
}

// 使用示例
async function example(pool: Pool) {
    await withTransaction(pool, async (client) => {
        await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
        await client.query('UPDATE accounts SET balance = balance + 100 WHERE id = 2');
    });
}
```

#### Promise模式

```typescript
class TransactionManager {
    constructor(private pool: Pool) {}

    async execute<T>(
        callback: (client: PoolClient) => Promise<T>
    ): Promise<T> {
        const client = await this.pool.connect();

        try {
            await client.query('BEGIN');
            const result = await callback(client);
            await client.query('COMMIT');
            return result;
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }
}

// 使用示例
const manager = new TransactionManager(pool);
await manager.execute(async (client) => {
    await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
});
```

### 1.3 隔离级别设置

#### 连接级隔离级别

```typescript
async function setIsolationLevel(
    pool: Pool,
    level: 'READ COMMITTED' | 'REPEATABLE READ' | 'SERIALIZABLE'
): Promise<void> {
    await pool.query(`SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL ${level}`);
}

// 使用示例
await setIsolationLevel(pool, 'REPEATABLE READ');
```

#### 事务级隔离级别

```typescript
async function executeWithIsolation<T>(
    pool: Pool,
    isolationLevel: string,
    callback: (client: PoolClient) => Promise<T>
): Promise<T> {
    return withTransaction(pool, async (client) => {
        await client.query(`SET TRANSACTION ISOLATION LEVEL ${isolationLevel}`);
        return await callback(client);
    });
}

// 使用示例
await executeWithIsolation(pool, 'REPEATABLE READ', async (client) => {
    await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
});
```

### 1.4 错误处理和重试

#### 死锁处理

```typescript
function isDeadlock(error: any): boolean {
    const code = error?.code;
    const message = error?.message?.toLowerCase() || '';
    return code === '40001' || code === '40P01' || message.includes('deadlock');
}

async function executeWithRetry<T>(
    pool: Pool,
    callback: (client: PoolClient) => Promise<T>,
    maxRetries: number = 5
): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await withTransaction(pool, callback);
        } catch (error) {
            if (isDeadlock(error) && attempt < maxRetries - 1) {
                // 指数退避
                const delay = Math.pow(2, attempt) * 100 + Math.random() * 100;
                await new Promise(resolve => setTimeout(resolve, delay));
                lastError = error;
                continue;
            }
            throw error;
        }
    }

    throw lastError;
}
```

#### 序列化错误处理

```typescript
function isSerializationError(error: any): boolean {
    const code = error?.code;
    const message = error?.message?.toLowerCase() || '';
    return code === '40001' || message.includes('serialization');
}

async function executeSerializable<T>(
    pool: Pool,
    callback: (client: PoolClient) => Promise<T>,
    maxRetries: number = 5
): Promise<T> {
    return executeWithRetry(pool, async (client) => {
        await client.query('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE');
        return await callback(client);
    }, maxRetries);
}
```

#### 重试机制实现

```typescript
import * as retry from 'retry';

async function executeWithBackoff<T>(
    pool: Pool,
    callback: (client: PoolClient) => Promise<T>
): Promise<T> {
    const operation = retry.operation({
        retries: 5,
        factor: 2,
        minTimeout: 100,
        maxTimeout: 1000,
    });

    return new Promise((resolve, reject) => {
        operation.attempt(async () => {
            try {
                const result = await withTransaction(pool, async (client) => {
                    await client.query('SET TRANSACTION ISOLATION LEVEL SERIALIZABLE');
                    return await callback(client);
                });
                resolve(result);
            } catch (error) {
                if (isSerializationError(error) && operation.retry(error)) {
                    return;
                }
                reject(operation.mainError());
            }
        });
    });
}
```

---

## 🚀 第二部分：连接池管理

### 2.1 pg.Pool配置

#### 基本配置

```typescript
import { Pool } from 'pg';
import os from 'os';

function createPool(): Pool {
    const cores = os.cpus().length;

    return new Pool({
        host: 'localhost',
        port: 5432,
        database: 'mydb',
        user: 'postgres',
        password: 'password',

        // 连接池大小（根据CPU核心数）
        min: cores,
        max: cores * 2,

        // 连接生命周期
        maxLifetimeMillis: 30 * 60 * 1000,  // 30分钟
        idleTimeoutMillis: 10 * 60 * 1000,   // 10分钟

        // 连接超时
        connectionTimeoutMillis: 10000,  // 10秒
    });
}
```

#### MVCC优化配置

```typescript
function createMVCCOptimizedPool(): Pool {
    return new Pool({
        host: 'localhost',
        port: 5432,
        database: 'mydb',
        user: 'postgres',
        password: 'password',

        // PostgreSQL 17/18优化参数
        application_name: 'myapp',
        statement_timeout: 30000,                    // 30秒
        idle_in_transaction_session_timeout: 300000, // 5分钟，防止长事务

        // 连接池大小
        min: 5,
        max: 20,

        // 连接保持
        keepAlive: true,
        keepAliveInitialDelayMillis: 10000,
    });
}
```

### 2.2 连接池监控

#### 连接池统计

```typescript
function monitorPool(pool: Pool): void {
    const totalCount = pool.totalCount;
    const idleCount = pool.idleCount;
    const waitingCount = pool.waitingCount;

    console.log('=== pg Pool Statistics ===');
    console.log(`Total connections: ${totalCount}`);
    console.log(`Idle connections: ${idleCount}`);
    console.log(`Waiting clients: ${waitingCount}`);

    // 连接池使用率
    const usageRate = (totalCount - idleCount) / pool.options.max * 100;
    console.log(`Pool usage: ${usageRate.toFixed(2)}%`);

    if (usageRate > 80) {
        console.warn('WARNING: Pool usage exceeds 80%');
    }
}
```

#### 健康检查

```typescript
async function healthCheck(pool: Pool): Promise<boolean> {
    try {
        const result = await pool.query('SELECT 1');
        return result.rows[0]['?column?'] === 1;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

// 定期健康检查
function startHealthCheck(pool: Pool, interval: number = 60000): void {
    setInterval(async () => {
        const healthy = await healthCheck(pool);
        if (!healthy) {
            console.error('Pool health check failed');
        }
    }, interval);
}
```

### 2.3 连接池最佳实践

#### 连接池大小设置

```typescript
function calculateOptimalPoolSize(): { min: number; max: number } {
    const cores = os.cpus().length;

    // 基本公式：cores * 2
    const baseSize = cores * 2;

    // 根据PostgreSQL MVCC特性调整
    const adjustedSize = Math.floor(baseSize * 1.2);

    // 限制最大连接数
    const max = Math.min(adjustedSize, 50);
    const min = cores;

    return { min, max };
}
```

#### 连接生命周期管理

```typescript
function createPoolWithLifecycle(): Pool {
    return new Pool({
        host: 'localhost',
        port: 5432,
        database: 'mydb',
        user: 'postgres',
        password: 'password',

        // 连接最大生命周期（30分钟）
        maxLifetimeMillis: 30 * 60 * 1000,

        // 空闲连接最大时间（10分钟）
        idleTimeoutMillis: 10 * 60 * 1000,

        min: 5,
        max: 20,
    });
}
```

---

## 📊 第三部分：MVCC最佳实践

### 3.1 短事务原则

#### 避免长事务

```typescript
// ❌ 错误示例：长事务
async function badExample(pool: Pool): Promise<void> {
    await withTransaction(pool, async (client) => {
        // 耗时操作在事务内
        await new Promise(resolve => setTimeout(resolve, 10 * 60 * 1000));  // 10分钟

        await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
    });
}

// ✅ 正确示例：短事务
async function goodExample(pool: Pool): Promise<void> {
    // 先完成业务逻辑（事务外）
    const result = await processBusinessLogic();

    // 再执行数据库操作（短事务）
    await withTransaction(pool, async (client) => {
        await client.query('UPDATE accounts SET balance = balance - 100 WHERE id = 1');
    });
}
```

#### 批量操作优化

```typescript
async function batchInsert(pool: Pool, data: Entity[]): Promise<void> {
    const batchSize = 1000;

    for (let i = 0; i < data.length; i += batchSize) {
        const batch = data.slice(i, i + batchSize);

        await withTransaction(pool, async (client) => {
            const values = batch.map((item, index) =>
                `($${index * 2 + 1}, $${index * 2 + 2})`
            ).join(', ');

            const params = batch.flatMap(item => [item.col1, item.col2]);

            await client.query(
                `INSERT INTO table (col1, col2) VALUES ${values}`,
                params
            );
        });
    }
}
```

### 3.2 并发控制

#### SELECT FOR UPDATE使用

```typescript
async function deductInventory(
    pool: Pool,
    productId: number,
    quantity: number
): Promise<boolean> {
    return withTransaction(pool, async (client) => {
        // 使用SELECT FOR UPDATE加锁
        const result = await client.query(
            'SELECT stock FROM inventory WHERE product_id = $1 FOR UPDATE',
            [productId]
        );

        if (result.rows.length === 0) {
            throw new Error('Product not found');
        }

        const stock = result.rows[0].stock;
        if (stock < quantity) {
            throw new Error('Insufficient stock');
        }

        // 更新库存
        await client.query(
            'UPDATE inventory SET stock = stock - $1 WHERE product_id = $2',
            [quantity, productId]
        );

        return true;
    });
}
```

#### 乐观锁实现

```typescript
interface Account {
    id: number;
    balance: number;
    version: number;
}

async function updateWithOptimisticLock(
    pool: Pool,
    accountId: number,
    newBalance: number,
    version: number
): Promise<void> {
    return withTransaction(pool, async (client) => {
        // 检查版本号
        const result = await client.query(
            'SELECT version FROM accounts WHERE id = $1',
            [accountId]
        );

        if (result.rows.length === 0) {
            throw new Error('Account not found');
        }

        if (result.rows[0].version !== version) {
            throw new Error('Version mismatch');
        }

        // 更新（版本号+1）
        const updateResult = await client.query(
            'UPDATE accounts SET balance = $1, version = version + 1 WHERE id = $2 AND version = $3',
            [newBalance, accountId, version]
        );

        if (updateResult.rowCount === 0) {
            throw new Error('Update failed, version changed');
        }
    });
}
```

#### 悲观锁实现

```typescript
async function updateWithPessimisticLock(
    pool: Pool,
    accountId: number,
    newBalance: number
): Promise<void> {
    return withTransaction(pool, async (client) => {
        // 加锁
        const result = await client.query(
            'SELECT balance FROM accounts WHERE id = $1 FOR UPDATE',
            [accountId]
        );

        if (result.rows.length === 0) {
            throw new Error('Account not found');
        }

        // 更新
        await client.query(
            'UPDATE accounts SET balance = $1 WHERE id = $2',
            [newBalance, accountId]
        );
    });
}
```

### 3.3 性能优化

#### 预编译语句

```typescript
async function usePreparedStatement(pool: Pool): Promise<void> {
    // 创建预编译语句
    const stmt = {
        name: 'get_account',
        text: 'SELECT balance FROM accounts WHERE id = $1',
    };

    // 使用预编译语句
    const result = await pool.query(stmt, [1]);
    console.log(result.rows[0].balance);
}
```

#### 批量操作

```typescript
async function batchUpdate(pool: Pool, updates: Update[]): Promise<void> {
    return withTransaction(pool, async (client) => {
        const queries = updates.map(update => ({
            text: 'UPDATE accounts SET balance = $1 WHERE id = $2',
            values: [update.balance, update.id],
        }));

        // 批量执行
        await Promise.all(queries.map(query => client.query(query)));
    });
}
```

#### 连接池优化

```typescript
function createOptimizedPool(): Pool {
    const cores = os.cpus().length;

    return new Pool({
        host: 'localhost',
        port: 5432,
        database: 'mydb',
        user: 'postgres',
        password: 'password',

        // 根据系统资源调整
        min: cores,
        max: cores * 2,

        // MVCC优化
        application_name: 'myapp',
        statement_timeout: 30000,
        idle_in_transaction_session_timeout: 300000,
    });
}
```

---

## 🔧 第四部分：实际场景案例

### 4.1 电商库存扣减场景

```typescript
class InventoryService {
    constructor(private pool: Pool) {}

    async deductStock(productId: number, quantity: number): Promise<boolean> {
        return executeWithRetry(this.pool, async (client) => {
            const result = await client.query(
                'SELECT stock FROM inventory WHERE product_id = $1 FOR UPDATE',
                [productId]
            );

            if (result.rows.length === 0) {
                throw new Error('Product not found');
            }

            const stock = result.rows[0].stock;
            if (stock < quantity) {
                throw new Error('Insufficient stock');
            }

            await client.query(
                'UPDATE inventory SET stock = stock - $1 WHERE product_id = $2',
                [quantity, productId]
            );

            return true;
        });
    }
}
```

### 4.2 银行转账场景

```typescript
class TransferService {
    constructor(private pool: Pool) {}

    async transfer(fromId: number, toId: number, amount: number): Promise<void> {
        return executeWithIsolation(this.pool, 'REPEATABLE READ', async (client) => {
            // 检查余额
            const result = await client.query(
                'SELECT balance FROM accounts WHERE id = $1',
                [fromId]
            );

            if (result.rows.length === 0) {
                throw new Error('Account not found');
            }

            const balance = result.rows[0].balance;
            if (balance < amount) {
                throw new Error('Insufficient balance');
            }

            // 扣减转出账户
            await client.query(
                'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
                [amount, fromId]
            );

            // 增加转入账户
            await client.query(
                'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
                [amount, toId]
            );
        });
    }
}
```

### 4.3 日志写入场景

```typescript
class LogWriter {
    private buffer: Log[] = [];
    private readonly bufferSize = 1000;

    constructor(private pool: Pool) {}

    async writeLog(message: string, level: string): Promise<void> {
        this.buffer.push({ message, level });

        if (this.buffer.length >= this.bufferSize) {
            await this.flush();
        }
    }

    async flush(): Promise<void> {
        if (this.buffer.length === 0) {
            return;
        }

        const logs = this.buffer.splice(0);

        await withTransaction(this.pool, async (client) => {
            const values = logs.map((_, index) =>
                `($${index * 2 + 1}, $${index * 2 + 2}, NOW())`
            ).join(', ');

            const params = logs.flatMap(log => [log.message, log.level]);

            await client.query(
                `INSERT INTO logs (message, level, created_at) VALUES ${values}`,
                params
            );
        });
    }
}
```

---

## 📝 第五部分：常见问题和解决方案

### 5.1 常见错误

#### 错误1：忘记释放连接

```typescript
// ❌ 错误示例：忘记释放连接
async function badExample(pool: Pool): Promise<void> {
    const client = await pool.connect();
    await client.query('SELECT * FROM table');
    // 忘记client.release()，导致连接泄漏
}

// ✅ 正确示例：使用try-finally
async function goodExample(pool: Pool): Promise<void> {
    const client = await pool.connect();
    try {
        await client.query('SELECT * FROM table');
    } finally {
        client.release();
    }
}
```

### 5.2 性能问题

#### 问题1：连接池耗尽

```typescript
function monitorPoolUsage(pool: Pool): void {
    const usageRate = (pool.totalCount - pool.idleCount) / pool.options.max * 100;

    if (usageRate > 80) {
        console.warn(`WARNING: Pool usage: ${usageRate.toFixed(2)}%`);
    }
}
```

### 5.3 调试技巧

#### 查看事务信息

```typescript
async function getTransactionInfo(pool: Pool): Promise<void> {
    const result = await pool.query(
        "SELECT txid_current(), current_setting('transaction_isolation')"
    );

    console.log('Transaction ID:', result.rows[0].txid_current);
    console.log('Isolation Level:', result.rows[0].current_setting);
}
```

---

## 🎯 总结

### 核心最佳实践

1. **使用pg.Pool连接池**：高性能、低延迟
2. **短事务原则**：避免在事务内执行耗时操作
3. **批量操作**：使用批量插入提高性能
4. **错误重试**：实现死锁和序列化错误的重试机制
5. **Promise模式**：使用async/await简化异步代码

### 关键配置

- **连接池大小**：min=5, max=20
- **连接生命周期**：maxLifetimeMillis=30分钟
- **事务超时**：statement_timeout=30秒
- **长事务限制**：idle_in_transaction_session_timeout=5分钟

### MVCC影响

- ✅ 短事务减少表膨胀
- ✅ 批量操作提高性能
- ✅ 合理使用锁避免死锁
- ✅ Promise模式简化异步事务管理

PostgreSQL 17/18的MVCC机制在Node.js驱动下表现优异，通过pg.Pool连接池和合理的事务管理，可以实现高性能、高可靠性的Node.js应用。
