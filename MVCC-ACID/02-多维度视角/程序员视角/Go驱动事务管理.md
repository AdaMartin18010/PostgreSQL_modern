# Go驱动PostgreSQL事务管理最佳实践

> **文档编号**: DEV-GO-001
> **语言**: Go
> **驱动**: pgx
> **版本**: PostgreSQL 17 & 18

---

## 📑 目录

- [Go驱动PostgreSQL事务管理最佳实践](#go驱动postgresql事务管理最佳实践)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔍 第一部分：pgx基础事务管理](#-第一部分pgx基础事务管理)
    - [1.1 连接管理](#11-连接管理)
      - [连接池配置](#连接池配置)
      - [连接参数优化](#连接参数优化)
    - [1.2 事务管理基础](#12-事务管理基础)
      - [基本事务操作](#基本事务操作)
      - [事务上下文管理](#事务上下文管理)
    - [1.3 隔离级别设置](#13-隔离级别设置)
      - [连接级隔离级别](#连接级隔离级别)
      - [事务级隔离级别](#事务级隔离级别)
    - [1.4 错误处理和重试](#14-错误处理和重试)
      - [死锁处理](#死锁处理)
      - [序列化错误处理](#序列化错误处理)
      - [重试机制实现](#重试机制实现)
  - [🚀 第二部分：连接池管理](#-第二部分连接池管理)
    - [2.1 pgxpool配置](#21-pgxpool配置)
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
      - [错误1：上下文取消导致事务未提交](#错误1上下文取消导致事务未提交)
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

Go语言在PostgreSQL生态系统中越来越受欢迎，主要通过**pgx**驱动与PostgreSQL交互。pgx是Go语言中性能最好的PostgreSQL驱动，支持连接池、预编译语句和批量操作。本文档深入分析Go驱动在PostgreSQL MVCC环境下的最佳实践。

---

## 🔍 第一部分：pgx基础事务管理

### 1.1 连接管理

#### 连接池配置

```go
package main

import (
    "context"
    "time"
    "github.com/jackc/pgx/v5/pgxpool"
)

// PostgreSQL 17/18推荐连接配置
func createPool(ctx context.Context) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig("postgres://postgres:password@localhost:5432/mydb")
    if err != nil {
        return nil, err
    }

    // 连接池大小
    config.MinConns = 5
    config.MaxConns = 20

    // 连接超时
    config.ConnConfig.ConnectTimeout = 10 * time.Second
    config.MaxConnLifetime = 30 * time.Minute
    config.MaxConnIdleTime = 10 * time.Minute

    // MVCC优化参数
    config.ConnConfig.Config.RuntimeParams = map[string]string{
        "application_name": "myapp",
        "statement_timeout": "30000",  // 30秒
    }

    // 连接健康检查
    config.HealthCheckPeriod = 1 * time.Minute

    return pgxpool.NewWithConfig(ctx, config)
}
```

#### 连接参数优化

```go
// PostgreSQL 17/18推荐连接参数
func getConnectionString() string {
    return "postgres://postgres:password@localhost:5432/mydb?" +
        "application_name=myapp&" +
        "connect_timeout=10&" +
        "statement_timeout=30000&" +
        "idle_in_transaction_session_timeout=300000"  // 5分钟，防止长事务
}
```

### 1.2 事务管理基础

#### 基本事务操作

```go
package main

import (
    "context"
    "fmt"
    "github.com/jackc/pgx/v5"
)

func transferMoney(ctx context.Context, conn *pgxpool.Pool,
                   fromID, toID int, amount float64) error {
    // 开始事务
    tx, err := conn.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)  // 确保回滚

    // 扣减转出账户
    _, err = tx.Exec(ctx,
        "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
        amount, fromID)
    if err != nil {
        return err
    }

    // 增加转入账户
    _, err = tx.Exec(ctx,
        "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
        amount, toID)
    if err != nil {
        return err
    }

    // 提交事务
    return tx.Commit(ctx)
}
```

#### 事务上下文管理

```go
// 事务上下文管理器
func WithTransaction(ctx context.Context, pool *pgxpool.Pool,
                   fn func(context.Context, pgx.Tx) error) error {
    tx, err := pool.Begin(ctx)
    if err != nil {
        return err
    }

    defer func() {
        if p := recover(); p != nil {
            tx.Rollback(ctx)
            panic(p)
        } else if err != nil {
            tx.Rollback(ctx)
        } else {
            err = tx.Commit(ctx)
        }
    }()

    return fn(ctx, tx)
}

// 使用示例
func example(ctx context.Context, pool *pgxpool.Pool) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        _, err := tx.Exec(ctx, "UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        return err
    })
}
```

### 1.3 隔离级别设置

#### 连接级隔离级别

```go
func setIsolationLevel(ctx context.Context, conn *pgxpool.Pool,
                       level string) error {
    _, err := conn.Exec(ctx, fmt.Sprintf("SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL %s", level))
    return err
}

// 使用示例
func example(ctx context.Context, pool *pgxpool.Pool) error {
    // 设置REPEATABLE READ
    if err := setIsolationLevel(ctx, pool, "REPEATABLE READ"); err != nil {
        return err
    }

    // 执行操作
    _, err := pool.Exec(ctx, "SELECT * FROM accounts")
    return err
}
```

#### 事务级隔离级别

```go
func executeWithIsolation(ctx context.Context, pool *pgxpool.Pool,
                           isolationLevel string, fn func(context.Context, pgx.Tx) error) error {
    tx, err := pool.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    // 设置事务隔离级别
    _, err = tx.Exec(ctx, fmt.Sprintf("SET TRANSACTION ISOLATION LEVEL %s", isolationLevel))
    if err != nil {
        return err
    }

    // 执行操作
    if err := fn(ctx, tx); err != nil {
        return err
    }

    return tx.Commit(ctx)
}

// 使用示例
func example(ctx context.Context, pool *pgxpool.Pool) error {
    return executeWithIsolation(ctx, pool, "REPEATABLE READ",
        func(ctx context.Context, tx pgx.Tx) error {
            _, err := tx.Exec(ctx, "UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            return err
        })
}
```

### 1.4 错误处理和重试

#### 死锁处理

```go
import (
    "errors"
    "time"
    "math/rand"
    "github.com/jackc/pgx/v5/pgconn"
)

func isDeadlock(err error) bool {
    var pgErr *pgconn.PgError
    if errors.As(err, &pgErr) {
        return pgErr.Code == "40001" ||
               pgErr.Code == "40P01" ||  // deadlock_detected
               pgErr.Message == "deadlock detected"
    }
    return false
}

func executeWithRetry(ctx context.Context, pool *pgxpool.Pool,
                     fn func(context.Context, pgx.Tx) error, maxRetries int) error {
    var lastErr error

    for attempt := 0; attempt < maxRetries; attempt++ {
        err := WithTransaction(ctx, pool, fn)
        if err == nil {
            return nil
        }

        if isDeadlock(err) && attempt < maxRetries-1 {
            // 指数退避
            delay := time.Duration(1<<uint(attempt))*100*time.Millisecond +
                time.Duration(rand.Intn(100))*time.Millisecond
            time.Sleep(delay)
            lastErr = err
            continue
        }

        return err
    }

    return lastErr
}
```

#### 序列化错误处理

```go
func isSerializationError(err error) bool {
    var pgErr *pgconn.PgError
    if errors.As(err, &pgErr) {
        return pgErr.Code == "40001" ||  // serialization_failure
               pgErr.Message == "could not serialize access"
    }
    return false
}

func executeSerializable(ctx context.Context, pool *pgxpool.Pool,
                        fn func(context.Context, pgx.Tx) error, maxRetries int) error {
    return executeWithRetry(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 设置SERIALIZABLE隔离级别
        if _, err := tx.Exec(ctx, "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"); err != nil {
            return err
        }
        return fn(ctx, tx)
    }, maxRetries)
}
```

#### 重试机制实现

```go
import "github.com/cenkalti/backoff/v4"

func executeWithBackoff(ctx context.Context, pool *pgxpool.Pool,
                       fn func(context.Context, pgx.Tx) error) error {
    operation := func() error {
        return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
            // 设置SERIALIZABLE隔离级别
            if _, err := tx.Exec(ctx, "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"); err != nil {
                return err
            }
            return fn(ctx, tx)
        })
    }

    // 指数退避重试
    backoffConfig := backoff.NewExponentialBackOff()
    backoffConfig.MaxElapsedTime = 5 * time.Second

    return backoff.Retry(operation, backoffConfig)
}
```

---

## 🚀 第二部分：连接池管理

### 2.1 pgxpool配置

#### 基本配置

```go
func createOptimizedPool(ctx context.Context) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig("postgres://postgres:password@localhost:5432/mydb")
    if err != nil {
        return nil, err
    }

    // 连接池大小（根据CPU核心数）
    cores := runtime.NumCPU()
    config.MinConns = cores
    config.MaxConns = cores * 2

    // 连接生命周期
    config.MaxConnLifetime = 30 * time.Minute
    config.MaxConnIdleTime = 10 * time.Minute

    // 连接超时
    config.ConnConfig.ConnectTimeout = 10 * time.Second

    // 健康检查
    config.HealthCheckPeriod = 1 * time.Minute

    return pgxpool.NewWithConfig(ctx, config)
}
```

#### MVCC优化配置

```go
func createMVCCOptimizedPool(ctx context.Context) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig("postgres://postgres:password@localhost:5432/mydb")
    if err != nil {
        return nil, err
    }

    // PostgreSQL 17/18优化参数
    config.ConnConfig.Config.RuntimeParams = map[string]string{
        "application_name": "myapp",
        "statement_timeout": "30000",                    // 30秒语句超时
        "idle_in_transaction_session_timeout": "300000", // 5分钟，防止长事务
    }

    // 连接池大小
    config.MinConns = 5
    config.MaxConns = 20

    // 连接泄漏检测（通过健康检查）
    config.HealthCheckPeriod = 1 * time.Minute

    return pgxpool.NewWithConfig(ctx, config)
}
```

### 2.2 连接池监控

#### 连接池统计

```go
func monitorPool(pool *pgxpool.Pool) {
    stats := pool.Stat()

    fmt.Printf("=== pgxpool Statistics ===\n")
    fmt.Printf("Max connections: %d\n", stats.MaxConns())
    fmt.Printf("Acquired connections: %d\n", stats.AcquiredConns())
    fmt.Printf("Idle connections: %d\n", stats.IdleConns())
    fmt.Printf("Constructing connections: %d\n", stats.ConstructingConns())

    // 连接池使用率
    usageRate := float64(stats.AcquiredConns()) / float64(stats.MaxConns()) * 100
    fmt.Printf("Pool usage: %.2f%%\n", usageRate)

    if usageRate > 80 {
        fmt.Println("WARNING: Pool usage exceeds 80%")
    }
}
```

#### 健康检查

```go
func healthCheck(ctx context.Context, pool *pgxpool.Pool) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    var result int
    err := pool.QueryRow(ctx, "SELECT 1").Scan(&result)
    if err != nil {
        return fmt.Errorf("health check failed: %w", err)
    }

    return nil
}

// 定期健康检查
func startHealthCheck(ctx context.Context, pool *pgxpool.Pool, interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            if err := healthCheck(ctx, pool); err != nil {
                log.Printf("Health check failed: %v", err)
            }
        }
    }
}
```

### 2.3 连接池最佳实践

#### 连接池大小设置

```go
func calculateOptimalPoolSize() (minConns, maxConns int) {
    cores := runtime.NumCPU()

    // 基本公式：cores * 2
    baseSize := cores * 2

    // 根据PostgreSQL MVCC特性调整
    // MVCC读不阻塞写，可以适当增加
    adjustedSize := int(float64(baseSize) * 1.2)

    // 限制最大连接数
    maxConns = min(adjustedSize, 50)
    minConns = cores

    return minConns, maxConns
}
```

#### 连接生命周期管理

```go
func createPoolWithLifecycle(ctx context.Context) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig("postgres://postgres:password@localhost:5432/mydb")
    if err != nil {
        return nil, err
    }

    // 连接最大生命周期（30分钟）
    config.MaxConnLifetime = 30 * time.Minute

    // 空闲连接最大时间（10分钟）
    config.MaxConnIdleTime = 10 * time.Minute

    // 健康检查周期（1分钟）
    config.HealthCheckPeriod = 1 * time.Minute

    return pgxpool.NewWithConfig(ctx, config)
}
```

---

## 📊 第三部分：MVCC最佳实践

### 3.1 短事务原则

#### 避免长事务

```go
// ❌ 错误示例：长事务
func badExample(ctx context.Context, pool *pgxpool.Pool) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 耗时操作在事务内
        time.Sleep(10 * time.Minute)  // 模拟耗时操作

        _, err := tx.Exec(ctx, "UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        return err
    })
}

// ✅ 正确示例：短事务
func goodExample(ctx context.Context, pool *pgxpool.Pool) error {
    // 先完成业务逻辑（事务外）
    result := processBusinessLogic()

    // 再执行数据库操作（短事务）
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        _, err := tx.Exec(ctx, "UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        return err
    })
}
```

#### 批量操作优化

```go
func batchInsert(ctx context.Context, pool *pgxpool.Pool, data []Entity) error {
    batchSize := 1000

    for i := 0; i < len(data); i += batchSize {
        end := min(i+batchSize, len(data))
        batch := data[i:end]

        err := WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
            // 批量插入
            _, err := tx.CopyFrom(ctx, pgx.Identifier{"table"},
                []string{"col1", "col2"}, pgx.CopyFromSlice(len(batch),
                func(i int) ([]interface{}, error) {
                    return []interface{}{batch[i].Col1, batch[i].Col2}, nil
                }))
            return err
        })

        if err != nil {
            return err
        }
    }

    return nil
}
```

### 3.2 并发控制

#### SELECT FOR UPDATE使用

```go
func deductInventory(ctx context.Context, pool *pgxpool.Pool,
                     productID, quantity int) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 使用SELECT FOR UPDATE加锁
        var stock int
        err := tx.QueryRow(ctx,
            "SELECT stock FROM inventory WHERE product_id = $1 FOR UPDATE",
            productID).Scan(&stock)
        if err != nil {
            return err
        }

        if stock < quantity {
            return fmt.Errorf("insufficient stock")
        }

        // 更新库存
        _, err = tx.Exec(ctx,
            "UPDATE inventory SET stock = stock - $1 WHERE product_id = $2",
            quantity, productID)
        return err
    })
}
```

#### 乐观锁实现

```go
type Account struct {
    ID      int
    Balance float64
    Version int  // 版本号
}

func updateWithOptimisticLock(ctx context.Context, pool *pgxpool.Pool,
                              accountID int, newBalance float64, version int) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 检查版本号
        var currentVersion int
        err := tx.QueryRow(ctx,
            "SELECT version FROM accounts WHERE id = $1",
            accountID).Scan(&currentVersion)
        if err != nil {
            return err
        }

        if currentVersion != version {
            return fmt.Errorf("version mismatch")
        }

        // 更新（版本号+1）
        result, err := tx.Exec(ctx,
            "UPDATE accounts SET balance = $1, version = version + 1 WHERE id = $2 AND version = $3",
            newBalance, accountID, version)
        if err != nil {
            return err
        }

        if result.RowsAffected() == 0 {
            return fmt.Errorf("update failed, version changed")
        }

        return nil
    })
}
```

#### 悲观锁实现

```go
func updateWithPessimisticLock(ctx context.Context, pool *pgxpool.Pool,
                                accountID int, newBalance float64) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 加锁
        var balance float64
        err := tx.QueryRow(ctx,
            "SELECT balance FROM accounts WHERE id = $1 FOR UPDATE",
            accountID).Scan(&balance)
        if err != nil {
            return err
        }

        // 更新
        _, err = tx.Exec(ctx,
            "UPDATE accounts SET balance = $1 WHERE id = $2",
            newBalance, accountID)
        return err
    })
}
```

### 3.3 性能优化

#### 预编译语句

```go
func usePreparedStatement(ctx context.Context, pool *pgxpool.Pool) error {
    // 创建预编译语句
    stmt, err := pool.Prepare(ctx, "get_account",
        "SELECT balance FROM accounts WHERE id = $1")
    if err != nil {
        return err
    }
    defer stmt.Close()

    // 使用预编译语句
    var balance float64
    err = pool.QueryRow(ctx, "get_account", 1).Scan(&balance)
    return err
}
```

#### 批量操作

```go
func batchUpdate(ctx context.Context, pool *pgxpool.Pool, updates []Update) error {
    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        batch := &pgx.Batch{}

        for _, update := range updates {
            batch.Queue("UPDATE accounts SET balance = $1 WHERE id = $2",
                update.Balance, update.ID)
        }

        results := tx.SendBatch(ctx, batch)
        defer results.Close()

        for i := 0; i < len(updates); i++ {
            _, err := results.Exec()
            if err != nil {
                return err
            }
        }

        return nil
    })
}
```

#### 连接池优化

```go
func createOptimizedPool(ctx context.Context) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig("postgres://postgres:password@localhost:5432/mydb")
    if err != nil {
        return nil, err
    }

    // 根据系统资源调整
    cores := runtime.NumCPU()
    config.MinConns = cores
    config.MaxConns = cores * 2

    // MVCC优化
    config.ConnConfig.Config.RuntimeParams = map[string]string{
        "application_name": "myapp",
        "statement_timeout": "30000",
        "idle_in_transaction_session_timeout": "300000",
    }

    return pgxpool.NewWithConfig(ctx, config)
}
```

---

## 🔧 第四部分：实际场景案例

### 4.1 电商库存扣减场景

```go
type InventoryService struct {
    pool *pgxpool.Pool
}

func (s *InventoryService) DeductStock(ctx context.Context,
                                       productID, quantity int) error {
    return executeWithRetry(ctx, s.pool,
        func(ctx context.Context, tx pgx.Tx) error {
            var stock int
            err := tx.QueryRow(ctx,
                "SELECT stock FROM inventory WHERE product_id = $1 FOR UPDATE",
                productID).Scan(&stock)
            if err != nil {
                return err
            }

            if stock < quantity {
                return fmt.Errorf("insufficient stock")
            }

            _, err = tx.Exec(ctx,
                "UPDATE inventory SET stock = stock - $1 WHERE product_id = $2",
                quantity, productID)
            return err
        }, 5)
}
```

### 4.2 银行转账场景

```go
type TransferService struct {
    pool *pgxpool.Pool
}

func (s *TransferService) Transfer(ctx context.Context,
                                   fromID, toID int, amount float64) error {
    return executeWithIsolation(ctx, s.pool, "REPEATABLE READ",
        func(ctx context.Context, tx pgx.Tx) error {
            // 检查余额
            var balance float64
            err := tx.QueryRow(ctx,
                "SELECT balance FROM accounts WHERE id = $1",
                fromID).Scan(&balance)
            if err != nil {
                return err
            }

            if balance < amount {
                return fmt.Errorf("insufficient balance")
            }

            // 扣减转出账户
            _, err = tx.Exec(ctx,
                "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
                amount, fromID)
            if err != nil {
                return err
            }

            // 增加转入账户
            _, err = tx.Exec(ctx,
                "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
                amount, toID)
            return err
        })
}
```

### 4.3 日志写入场景

```go
type LogWriter struct {
    pool   *pgxpool.Pool
    buffer []Log
    mu     sync.Mutex
}

func (w *LogWriter) WriteLog(ctx context.Context, message, level string) {
    w.mu.Lock()
    defer w.mu.Unlock()

    w.buffer = append(w.buffer, Log{Message: message, Level: level})

    if len(w.buffer) >= 1000 {
        w.flush(ctx)
    }
}

func (w *LogWriter) flush(ctx context.Context) error {
    w.mu.Lock()
    defer w.mu.Unlock()

    if len(w.buffer) == 0 {
        return nil
    }

    return WithTransaction(ctx, w.pool, func(ctx context.Context, tx pgx.Tx) error {
        _, err := tx.CopyFrom(ctx, pgx.Identifier{"logs"},
            []string{"message", "level", "created_at"},
            pgx.CopyFromSlice(len(w.buffer), func(i int) ([]interface{}, error) {
                return []interface{}{w.buffer[i].Message, w.buffer[i].Level, time.Now()}, nil
            }))
        if err == nil {
            w.buffer = w.buffer[:0]
        }
        return err
    })
}
```

---

## 📝 第五部分：常见问题和解决方案

### 5.1 常见错误

#### 错误1：上下文取消导致事务未提交

```go
// ❌ 错误示例：上下文取消
func badExample(ctx context.Context, pool *pgxpool.Pool) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 如果操作超过5秒，上下文取消，事务回滚
        time.Sleep(10 * time.Second)
        return nil
    })
}

// ✅ 正确示例：合理设置超时
func goodExample(ctx context.Context, pool *pgxpool.Pool) error {
    // 设置足够的超时时间
    ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
    defer cancel()

    return WithTransaction(ctx, pool, func(ctx context.Context, tx pgx.Tx) error {
        // 快速操作
        _, err := tx.Exec(ctx, "UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        return err
    })
}
```

### 5.2 性能问题

#### 问题1：连接池耗尽

```go
func monitorPoolUsage(pool *pgxpool.Pool) {
    stats := pool.Stat()
    usageRate := float64(stats.AcquiredConns()) / float64(stats.MaxConns()) * 100

    if usageRate > 80 {
        log.Printf("WARNING: Pool usage: %.2f%%", usageRate)
    }
}
```

### 5.3 调试技巧

#### 查看事务信息

```go
func getTransactionInfo(ctx context.Context, pool *pgxpool.Pool) error {
    var txID, isolationLevel string

    err := pool.QueryRow(ctx,
        "SELECT txid_current(), current_setting('transaction_isolation')").
        Scan(&txID, &isolationLevel)
    if err != nil {
        return err
    }

    log.Printf("Transaction ID: %s, Isolation Level: %s", txID, isolationLevel)
    return nil
}
```

---

## 🎯 总结

### 核心最佳实践

1. **使用pgxpool连接池**：高性能、低延迟
2. **短事务原则**：避免在事务内执行耗时操作
3. **批量操作**：使用CopyFrom进行批量操作
4. **错误重试**：实现死锁和序列化错误的重试机制
5. **上下文管理**：合理使用context控制超时

### 关键配置

- **连接池大小**：MinConns=5, MaxConns=20
- **连接生命周期**：MaxConnLifetime=30分钟
- **事务超时**：statement_timeout=30秒
- **长事务限制**：idle_in_transaction_session_timeout=5分钟

### MVCC影响

- ✅ 短事务减少表膨胀
- ✅ 批量操作提高性能
- ✅ 合理使用锁避免死锁
- ✅ 上下文管理控制事务时间

PostgreSQL 17/18的MVCC机制在Go驱动下表现优异，通过pgxpool连接池和合理的事务管理，可以实现高性能、高可靠性的Go应用。
