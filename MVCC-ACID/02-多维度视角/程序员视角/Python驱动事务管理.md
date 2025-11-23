# Python驱动PostgreSQL事务管理最佳实践

> **文档编号**: DEV-PYTHON-001
> **语言**: Python
> **驱动**: psycopg2 / asyncpg
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [Python驱动PostgreSQL事务管理最佳实践](#python驱动postgresql事务管理最佳实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：psycopg2同步驱动](#-第一部分psycopg2同步驱动)
    - [1.1 连接管理](#11-连接管理)
      - [连接池配置](#连接池配置)
      - [连接参数优化](#连接参数优化)
    - [1.2 事务管理基础](#12-事务管理基础)
      - [基本事务操作](#基本事务操作)
      - [事务上下文管理器](#事务上下文管理器)
    - [1.3 隔离级别设置](#13-隔离级别设置)
      - [连接级隔离级别](#连接级隔离级别)
      - [事务级隔离级别](#事务级隔离级别)
    - [1.4 错误处理和重试](#14-错误处理和重试)
      - [死锁处理](#死锁处理)
      - [序列化错误处理](#序列化错误处理)
      - [重试机制实现](#重试机制实现)
  - [🚀 第二部分：asyncpg异步驱动](#-第二部分asyncpg异步驱动)
    - [2.1 异步连接管理](#21-异步连接管理)
      - [连接池配置](#连接池配置-1)
      - [异步连接参数](#异步连接参数)
    - [2.2 异步事务管理](#22-异步事务管理)
      - [异步事务上下文](#异步事务上下文)
      - [异步隔离级别](#异步隔离级别)
    - [2.3 异步错误处理](#23-异步错误处理)
      - [异步重试机制](#异步重试机制)
      - [异步死锁处理](#异步死锁处理)
  - [📊 第三部分：MVCC最佳实践](#-第三部分mvcc最佳实践)
    - [3.1 短事务原则](#31-短事务原则)
      - [避免长事务](#避免长事务)
      - [批量操作优化](#批量操作优化)
    - [3.2 并发控制](#32-并发控制)
      - [SELECT FOR UPDATE使用](#select-for-update使用)
      - [乐观锁实现](#乐观锁实现)
      - [悲观锁实现](#悲观锁实现)
    - [3.3 性能优化](#33-性能优化)
      - [连接池优化](#连接池优化)
      - [查询优化](#查询优化)
      - [批量操作](#批量操作)
  - [🔧 第四部分：实际场景案例](#-第四部分实际场景案例)
    - [4.1 电商库存扣减场景](#41-电商库存扣减场景)
    - [4.2 银行转账场景](#42-银行转账场景)
    - [4.3 日志写入场景](#43-日志写入场景)
  - [📝 第五部分：常见问题和解决方案](#-第五部分常见问题和解决方案)
    - [5.1 常见错误](#51-常见错误)
    - [5.2 性能问题](#52-性能问题)
    - [5.3 调试技巧](#53-调试技巧)
  - [🎯 总结](#-总结)

---

## 📋 概述

Python是PostgreSQL最常用的编程语言之一，主要有两个驱动：**psycopg2**（同步）和**asyncpg**（异步）。本文档深入分析Python驱动在PostgreSQL MVCC环境下的最佳实践，涵盖事务管理、并发控制、错误处理和性能优化。

---

## 🔍 第一部分：psycopg2同步驱动

### 1.1 连接管理

#### 连接池配置

```python
import psycopg2
from psycopg2 import pool

# 创建连接池
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="password",
    # MVCC相关参数
    connect_timeout=10,
    keepalives=1,
    keepalives_idle=30,
    keepalives_interval=10,
    keepalives_count=5
)

# 使用连接池
def get_connection():
    return connection_pool.getconn()

def return_connection(conn):
    connection_pool.putconn(conn)
```

#### 连接参数优化

```python
# PostgreSQL 17/18推荐连接参数
connection_params = {
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb',
    'user': 'postgres',
    'password': 'password',

    # 事务相关
    'isolation_level': psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED,  # 默认RC

    # 连接保持
    'keepalives': 1,
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5,

    # 超时设置
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000',  # 30秒语句超时

    # MVCC优化
    'application_name': 'myapp',  # 便于监控和调试
}
```

### 1.2 事务管理基础

#### 基本事务操作

```python
import psycopg2
from psycopg2 import sql

# 方式1：手动事务管理
conn = psycopg2.connect(**connection_params)
try:
    cur = conn.cursor()

    # BEGIN（自动）
    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

    # COMMIT
    conn.commit()
except psycopg2.Error as e:
    # ROLLBACK（自动）
    conn.rollback()
    print(f"Transaction failed: {e}")
finally:
    cur.close()
    conn.close()
```

#### 事务上下文管理器

```python
from contextlib import contextmanager

@contextmanager
def transaction(conn):
    """事务上下文管理器"""
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

# 使用示例
conn = get_connection()
try:
    with transaction(conn):
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
        cur.close()
finally:
    return_connection(conn)
```

### 1.3 隔离级别设置

#### 连接级隔离级别

```python
# 设置连接级隔离级别
conn = psycopg2.connect(**connection_params)

# READ COMMITTED（默认）
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED)

# REPEATABLE READ
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ)

# SERIALIZABLE
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)

# 查看当前隔离级别
print(conn.isolation_level)
```

#### 事务级隔离级别

```python
# 在事务内设置隔离级别
conn = psycopg2.connect(**connection_params)
cur = conn.cursor()

# 方式1：使用SET TRANSACTION
cur.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
cur.execute("SELECT balance FROM accounts WHERE id = 1")
# ... 其他操作
conn.commit()

# 方式2：使用BEGIN
cur.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
cur.execute("SELECT balance FROM accounts WHERE id = 1")
# ... 其他操作
conn.commit()
```

### 1.4 错误处理和重试

#### 死锁处理

```python
import time
import random
from psycopg2 import OperationalError

def execute_with_retry(conn, query, max_retries=3):
    """带重试的执行函数"""
    for attempt in range(max_retries):
        try:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            cur.close()
            return True
        except OperationalError as e:
            # 检查是否是死锁错误
            if 'deadlock' in str(e).lower():
                if attempt < max_retries - 1:
                    # 指数退避
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
                    conn.rollback()
                    continue
                else:
                    raise
            else:
                conn.rollback()
                raise
    return False

# 使用示例
conn = get_connection()
try:
    execute_with_retry(
        conn,
        "UPDATE accounts SET balance = balance - 100 WHERE id = 1"
    )
finally:
    return_connection(conn)
```

#### 序列化错误处理

```python
from psycopg2.extensions import TransactionRollbackError

def execute_serializable(conn, operations, max_retries=5):
    """可串行化事务执行，自动重试"""
    for attempt in range(max_retries):
        try:
            # 设置SERIALIZABLE隔离级别
            conn.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
            )

            cur = conn.cursor()
            for operation in operations:
                cur.execute(operation['query'], operation.get('params'))

            conn.commit()
            cur.close()
            return True

        except TransactionRollbackError as e:
            # 序列化冲突，重试
            if attempt < max_retries - 1:
                conn.rollback()
                time.sleep(random.uniform(0.01, 0.1))  # 短暂等待
                continue
            else:
                raise
        except Exception as e:
            conn.rollback()
            raise
    return False

# 使用示例
conn = get_connection()
try:
    operations = [
        {'query': "SELECT balance FROM accounts WHERE id = 1"},
        {'query': "UPDATE accounts SET balance = balance - 100 WHERE id = 1"},
        {'query': "UPDATE accounts SET balance = balance + 100 WHERE id = 2"},
    ]
    execute_serializable(conn, operations)
finally:
    return_connection(conn)
```

#### 重试机制实现

```python
from functools import wraps
import time
import random

def retry_on_deadlock(max_retries=3, base_delay=0.1):
    """死锁重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    if 'deadlock' in str(e).lower() and attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                        time.sleep(delay)
                        continue
                    raise
            return None
        return wrapper
    return decorator

# 使用示例
@retry_on_deadlock(max_retries=5)
def transfer_money(conn, from_id, to_id, amount):
    """转账操作，自动重试死锁"""
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE accounts SET balance = balance - %s WHERE id = %s",
            (amount, from_id)
        )
        cur.execute(
            "UPDATE accounts SET balance = balance + %s WHERE id = %s",
            (amount, to_id)
        )
        conn.commit()
    finally:
        cur.close()
```

---

## 🚀 第二部分：asyncpg异步驱动

### 2.1 异步连接管理

#### 连接池配置

```python
import asyncio
import asyncpg

# 创建异步连接池
async def create_pool():
    pool = await asyncpg.create_pool(
        host='localhost',
        port=5432,
        database='mydb',
        user='postgres',
        password='password',
        min_size=5,
        max_size=20,
        # MVCC相关参数
        command_timeout=30,
        server_settings={
            'application_name': 'myapp_async',
            'statement_timeout': '30000',  # 30秒
        }
    )
    return pool

# 使用连接池
async def execute_query(pool, query):
    async with pool.acquire() as conn:
        return await conn.fetch(query)
```

#### 异步连接参数

```python
# PostgreSQL 17/18推荐异步连接参数
async_pool_config = {
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb',
    'user': 'postgres',
    'password': 'password',

    # 连接池大小
    'min_size': 5,
    'max_size': 20,

    # 超时设置
    'command_timeout': 30,
    'server_settings': {
        'application_name': 'myapp_async',
        'statement_timeout': '30000',
        'idle_in_transaction_session_timeout': '300000',  # 5分钟，防止长事务
    },

    # 连接保持
    'max_queries': 50000,
    'max_inactive_connection_lifetime': 300,
}
```

### 2.2 异步事务管理

#### 异步事务上下文

```python
# 方式1：使用async with
async def transfer_money_async(pool, from_id, to_id, amount):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                amount, from_id
            )
            await conn.execute(
                "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                amount, to_id
            )
            # 自动提交或回滚
```

#### 异步隔离级别

```python
# 设置隔离级别
async def execute_rr_transaction(pool, operations):
    async with pool.acquire() as conn:
        # 设置REPEATABLE READ
        await conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")

        async with conn.transaction():
            for query, params in operations:
                await conn.execute(query, *params)
            # 自动提交

# 使用示例
async def main():
    pool = await create_pool()
    operations = [
        ("SELECT balance FROM accounts WHERE id = $1", (1,)),
        ("UPDATE accounts SET balance = balance - $1 WHERE id = $2", (100, 1)),
    ]
    await execute_rr_transaction(pool, operations)
    await pool.close()
```

### 2.3 异步错误处理

#### 异步重试机制

```python
import asyncio
from asyncpg import DeadlockDetectedError, SerializationError

async def execute_with_retry_async(
    pool,
    operations,
    max_retries=5,
    isolation_level='READ COMMITTED'
):
    """异步执行，自动重试死锁和序列化错误"""
    for attempt in range(max_retries):
        try:
            async with pool.acquire() as conn:
                # 设置隔离级别
                await conn.execute(
                    f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"
                )

                async with conn.transaction():
                    results = []
                    for query, params in operations:
                        result = await conn.fetch(query, *params)
                        results.append(result)
                    return results

        except (DeadlockDetectedError, SerializationError) as e:
            if attempt < max_retries - 1:
                # 指数退避
                delay = (2 ** attempt) * 0.1 + random.uniform(0, 0.1)
                await asyncio.sleep(delay)
                continue
            else:
                raise
        except Exception as e:
            raise
    return None
```

#### 异步死锁处理

```python
from functools import wraps

def async_retry_on_deadlock(max_retries=3):
    """异步死锁重试装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except DeadlockDetectedError as e:
                    if attempt < max_retries - 1:
                        delay = (2 ** attempt) * 0.1 + random.uniform(0, 0.1)
                        await asyncio.sleep(delay)
                        continue
                    raise
            return None
        return wrapper
    return decorator

# 使用示例
@async_retry_on_deadlock(max_retries=5)
async def update_inventory(pool, product_id, quantity):
    """更新库存，自动重试死锁"""
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE inventory SET stock = stock - $1 WHERE product_id = $2",
                quantity, product_id
            )
```

---

## 📊 第三部分：MVCC最佳实践

### 3.1 短事务原则

#### 避免长事务

```python
# ❌ 错误示例：长事务
def bad_example(conn):
    cur = conn.cursor()
    cur.execute("BEGIN")

    # 业务逻辑处理（耗时操作）
    time.sleep(10)  # 模拟耗时操作

    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    conn.commit()  # 事务持有时间过长，导致表膨胀

# ✅ 正确示例：短事务
def good_example(conn):
    # 先完成业务逻辑
    result = process_business_logic()  # 在事务外执行

    # 再执行数据库操作
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
    conn.commit()  # 事务时间短，不影响MVCC
```

#### 批量操作优化

```python
# ❌ 错误示例：逐条提交
def bad_batch_insert(conn, data_list):
    cur = conn.cursor()
    for item in data_list:
        cur.execute("INSERT INTO logs (message) VALUES (%s)", (item,))
        conn.commit()  # 每条都提交，事务开销大

# ✅ 正确示例：批量提交
def good_batch_insert(conn, data_list, batch_size=1000):
    cur = conn.cursor()
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i:i+batch_size]
        cur.executemany(
            "INSERT INTO logs (message) VALUES (%s)",
            [(item,) for item in batch]
        )
        conn.commit()  # 每1000条提交一次，平衡性能和MVCC
```

### 3.2 并发控制

#### SELECT FOR UPDATE使用

```python
# 场景：库存扣减，防止超卖
def deduct_inventory(conn, product_id, quantity):
    """扣减库存，使用SELECT FOR UPDATE防止并发问题"""
    cur = conn.cursor()

    try:
        # 当前读，加排他锁
        cur.execute(
            "SELECT stock FROM inventory WHERE product_id = %s FOR UPDATE",
            (product_id,)
        )
        row = cur.fetchone()

        if not row or row[0] < quantity:
            raise ValueError("Insufficient stock")

        # 更新库存
        cur.execute(
            "UPDATE inventory SET stock = stock - %s WHERE product_id = %s",
            (quantity, product_id)
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
```

#### 乐观锁实现

```python
# 乐观锁：使用版本号
def update_with_optimistic_lock(conn, account_id, new_balance, version):
    """使用版本号的乐观锁"""
    cur = conn.cursor()

    try:
        # 检查版本号
        cur.execute(
            "SELECT balance, version FROM accounts WHERE id = %s",
            (account_id,)
        )
        row = cur.fetchone()

        if not row or row[1] != version:
            raise ValueError("Version mismatch, please retry")

        # 更新（版本号+1）
        cur.execute(
            """
            UPDATE accounts
            SET balance = %s, version = version + 1
            WHERE id = %s AND version = %s
            """,
            (new_balance, account_id, version)
        )

        if cur.rowcount == 0:
            raise ValueError("Update failed, version changed")

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
```

#### 悲观锁实现

```python
# 悲观锁：使用SELECT FOR UPDATE
def update_with_pessimistic_lock(conn, account_id, new_balance):
    """使用SELECT FOR UPDATE的悲观锁"""
    cur = conn.cursor()

    try:
        # 加锁
        cur.execute(
            "SELECT balance FROM accounts WHERE id = %s FOR UPDATE",
            (account_id,)
        )
        row = cur.fetchone()

        if not row:
            raise ValueError("Account not found")

        # 更新
        cur.execute(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            (new_balance, account_id)
        )

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
```

### 3.3 性能优化

#### 连接池优化

```python
# 推荐连接池配置
def create_optimized_pool():
    """优化的连接池配置"""
    return psycopg2.pool.ThreadedConnectionPool(
        minconn=5,      # 最小连接数
        maxconn=20,     # 最大连接数（根据并发需求调整）
        host="localhost",
        port=5432,
        database="mydb",
        user="postgres",
        password="password",
        # MVCC优化参数
        connect_timeout=10,
        keepalives=1,
        keepalives_idle=30,
    )

# 连接池监控
def monitor_pool(pool):
    """监控连接池状态"""
    print(f"Pool size: {pool.maxconn}")
    print(f"Available connections: {pool.maxconn - len(pool._used)}")
```

#### 查询优化

```python
# 使用预编译语句
def create_prepared_statements(conn):
    """创建预编译语句，提高性能"""
    cur = conn.cursor()

    # 预编译常用查询
    cur.execute("""
        PREPARE get_account AS
        SELECT balance FROM accounts WHERE id = $1
    """)

    cur.execute("""
        PREPARE update_account AS
        UPDATE accounts SET balance = $1 WHERE id = $2
    """)

    conn.commit()
    cur.close()

# 使用预编译语句
def get_account_balance(conn, account_id):
    """使用预编译语句查询"""
    cur = conn.cursor()
    cur.execute("EXECUTE get_account (%s)", (account_id,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None
```

#### 批量操作

```python
# 使用executemany进行批量操作
def batch_update(conn, updates):
    """批量更新，减少事务开销"""
    cur = conn.cursor()

    try:
        cur.executemany(
            "UPDATE accounts SET balance = %s WHERE id = %s",
            updates
        )
        conn.commit()
        return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()

# 使用COPY进行大批量插入
def bulk_insert(conn, data):
    """使用COPY进行大批量插入，性能最优"""
    cur = conn.cursor()

    try:
        # 创建临时表
        cur.execute("CREATE TEMP TABLE temp_data (id INT, value TEXT)")

        # 使用COPY
        from io import StringIO
        f = StringIO()
        for row in data:
            f.write(f"{row[0]}\t{row[1]}\n")
        f.seek(0)

        cur.copy_from(f, 'temp_data', columns=('id', 'value'))

        # 插入到目标表
        cur.execute("""
            INSERT INTO target_table (id, value)
            SELECT id, value FROM temp_data
        """)

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cur.close()
```

---

## 🔧 第四部分：实际场景案例

### 4.1 电商库存扣减场景

```python
import psycopg2
from psycopg2 import pool
import time
import random

class InventoryManager:
    """库存管理器，处理并发扣减"""

    def __init__(self, pool):
        self.pool = pool

    def deduct_stock(self, product_id, quantity, max_retries=5):
        """扣减库存，自动重试死锁"""
        for attempt in range(max_retries):
            conn = self.pool.getconn()
            try:
                cur = conn.cursor()

                # 使用SELECT FOR UPDATE加锁
                cur.execute(
                    """
                    SELECT stock FROM inventory
                    WHERE product_id = %s FOR UPDATE
                    """,
                    (product_id,)
                )
                row = cur.fetchone()

                if not row:
                    raise ValueError(f"Product {product_id} not found")

                current_stock = row[0]
                if current_stock < quantity:
                    raise ValueError("Insufficient stock")

                # 更新库存
                cur.execute(
                    """
                    UPDATE inventory
                    SET stock = stock - %s
                    WHERE product_id = %s
                    """,
                    (quantity, product_id)
                )

                conn.commit()
                return True

            except psycopg2.OperationalError as e:
                if 'deadlock' in str(e).lower() and attempt < max_retries - 1:
                    conn.rollback()
                    time.sleep((2 ** attempt) * 0.1 + random.uniform(0, 0.1))
                    continue
                raise
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cur.close()
                self.pool.putconn(conn)

        return False

# 使用示例
pool = create_optimized_pool()
manager = InventoryManager(pool)

# 并发扣减
try:
    success = manager.deduct_stock(product_id=1, quantity=1)
    if success:
        print("Stock deducted successfully")
except ValueError as e:
    print(f"Error: {e}")
```

### 4.2 银行转账场景

```python
class BankTransfer:
    """银行转账，保证ACID"""

    def __init__(self, pool):
        self.pool = pool

    def transfer(self, from_account, to_account, amount, max_retries=5):
        """转账操作，自动重试序列化错误"""
        for attempt in range(max_retries):
            conn = self.pool.getconn()
            try:
                # 设置REPEATABLE READ隔离级别
                conn.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
                )

                cur = conn.cursor()

                # 检查余额
                cur.execute(
                    "SELECT balance FROM accounts WHERE id = %s",
                    (from_account,)
                )
                from_balance = cur.fetchone()[0]

                if from_balance < amount:
                    raise ValueError("Insufficient balance")

                # 扣减转出账户
                cur.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE id = %s",
                    (amount, from_account)
                )

                # 增加转入账户
                cur.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                    (amount, to_account)
                )

                conn.commit()
                return True

            except psycopg2.extensions.TransactionRollbackError as e:
                # 序列化错误，重试
                if attempt < max_retries - 1:
                    conn.rollback()
                    time.sleep(random.uniform(0.01, 0.1))
                    continue
                raise
            except Exception as e:
                conn.rollback()
                raise
            finally:
                cur.close()
                self.pool.putconn(conn)

        return False
```

### 4.3 日志写入场景

```python
class LogWriter:
    """日志写入，优化批量操作"""

    def __init__(self, pool):
        self.pool = pool
        self.buffer = []
        self.buffer_size = 1000

    def write_log(self, message, level='INFO'):
        """写入日志（缓冲）"""
        self.buffer.append((message, level))

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        """刷新缓冲区到数据库"""
        if not self.buffer:
            return

        conn = self.pool.getconn()
        try:
            cur = conn.cursor()

            # 批量插入
            cur.executemany(
                "INSERT INTO logs (message, level, created_at) VALUES (%s, %s, NOW())",
                self.buffer
            )

            conn.commit()
            self.buffer.clear()

        except Exception as e:
            conn.rollback()
            raise
        finally:
            cur.close()
            self.pool.putconn(conn)

    def __del__(self):
        """析构时刷新缓冲区"""
        if self.buffer:
            self.flush()
```

---

## 📝 第五部分：常见问题和解决方案

### 5.1 常见错误

#### 错误1：长事务导致表膨胀

```python
# ❌ 错误示例
def bad_example(conn):
    cur = conn.cursor()
    cur.execute("BEGIN")

    # 长时间处理
    process_large_dataset()  # 耗时10分钟

    cur.execute("UPDATE table SET ...")
    conn.commit()  # 事务持有10分钟，导致表膨胀

# ✅ 正确示例
def good_example(conn):
    # 先处理数据
    results = process_large_dataset()  # 在事务外

    # 再批量更新
    cur = conn.cursor()
    for batch in batch_process(results, batch_size=1000):
        cur.executemany("UPDATE table SET ...", batch)
        conn.commit()  # 短事务，每1000条提交
```

#### 错误2：忘记提交事务

```python
# ❌ 错误示例
def bad_example(conn):
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = 100 WHERE id = 1")
    # 忘记commit，事务一直持有

# ✅ 正确示例：使用上下文管理器
def good_example(conn):
    with transaction(conn):
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = 100 WHERE id = 1")
        # 自动提交
```

### 5.2 性能问题

#### 问题1：连接池耗尽

```python
# 监控连接池
def monitor_connection_pool(pool):
    """监控连接池状态"""
    used = len(pool._used)
    available = pool.maxconn - used

    if used > pool.maxconn * 0.8:
        print(f"WARNING: Pool usage high: {used}/{pool.maxconn}")

    return {
        'total': pool.maxconn,
        'used': used,
        'available': available,
        'usage_percent': (used / pool.maxconn) * 100
    }
```

#### 问题2：事务时间过长

```python
import time

def monitor_transaction_time(func):
    """监控事务执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time

            if elapsed > 5:  # 超过5秒警告
                print(f"WARNING: Transaction took {elapsed:.2f}s")

            return result
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"ERROR: Transaction failed after {elapsed:.2f}s")
            raise
    return wrapper
```

### 5.3 调试技巧

#### 查看当前事务状态

```python
def get_transaction_info(conn):
    """获取当前事务信息"""
    cur = conn.cursor()

    # 查看隔离级别
    cur.execute("SHOW transaction_isolation")
    isolation = cur.fetchone()[0]

    # 查看事务状态
    cur.execute("SELECT txid_current(), txid_current_if_assigned()")
    txid = cur.fetchone()

    # 查看长事务
    cur.execute("""
        SELECT pid, now() - xact_start as duration, query
        FROM pg_stat_activity
        WHERE state = 'active'
        AND now() - xact_start > interval '1 minute'
    """)
    long_transactions = cur.fetchall()

    cur.close()

    return {
        'isolation_level': isolation,
        'transaction_id': txid,
        'long_transactions': long_transactions
    }
```

---

## 🎯 总结

### 核心最佳实践

1. **短事务原则**：避免在事务内执行耗时操作
2. **批量操作**：使用executemany或COPY进行批量操作
3. **连接池管理**：合理配置连接池大小
4. **错误处理**：实现死锁和序列化错误的重试机制
5. **隔离级别**：根据业务需求选择合适的隔离级别

### 关键配置

- **连接池大小**：minconn=5, maxconn=20（根据并发调整）
- **事务超时**：statement_timeout=30秒
- **长事务限制**：idle_in_transaction_session_timeout=5分钟
- **隔离级别**：默认READ COMMITTED，必要时使用REPEATABLE READ

### MVCC影响

- ✅ 短事务减少表膨胀
- ✅ 批量操作提高性能
- ✅ 合理使用锁避免死锁
- ✅ 错误重试提高可靠性

PostgreSQL 17/18的MVCC机制在Python驱动下表现优异，通过合理的事务管理和并发控制，可以实现高性能、高可靠性的应用。
