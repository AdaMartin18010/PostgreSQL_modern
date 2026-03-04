# DCA 快速开始指南

> **目标**: 30分钟内掌握数据库中心架构(DCA)的核心概念和实践
> **前置要求**: PostgreSQL 14+ 基础
> **预计时间**: 30分钟

---

## 🎯 本指南目标

完成本指南后，您将能够：

- ✅ 理解DCA与传统架构的核心区别
- ✅ 创建第一个数据库存储过程
- ✅ 实现读写分离路由
- ✅ 配置数据库事件通知
- ✅ 了解分布式架构基础

---

## 📚 目录

- [DCA 快速开始指南](#dca-快速开始指南)
  - [🎯 本指南目标](#-本指南目标)
  - [📚 目录](#-目录)
  - [1. 什么是DCA？](#1-什么是dca)
    - [1.1 传统架构 vs DCA](#11-传统架构-vs-dca)
    - [1.2 DCA的核心优势](#12-dca的核心优势)
  - [2. 环境准备](#2-环境准备)
    - [2.1 数据库环境](#21-数据库环境)
    - [2.2 扩展安装](#22-扩展安装)
  - [3. 5分钟入门](#3-5分钟入门)
    - [3.1 创建第一个存储过程](#31-创建第一个存储过程)
    - [3.2 快速验证](#32-快速验证)
  - [4. 15分钟实践](#4-15分钟实践)
    - [4.1 电商订单场景](#41-电商订单场景)
    - [4.2 添加事件通知](#42-添加事件通知)
    - [4.3 Python客户端示例](#43-python客户端示例)
  - [5. 30分钟进阶](#5-30分钟进阶)
    - [5.1 读写分离路由](#51-读写分离路由)
    - [5.2 分布式ID生成（PG 18 UUIDv7）](#52-分布式id生成pg-18-uuidv7)
    - [5.3 缓存失效通知](#53-缓存失效通知)
  - [6. 下一步](#6-下一步)
    - [6.1 继续学习](#61-继续学习)
    - [6.2 实践项目](#62-实践项目)
    - [6.3 资源索引](#63-资源索引)
  - [🎉 总结](#-总结)

---

## 1. 什么是DCA？

### 1.1 传统架构 vs DCA

```text
┌─────────────────────────────────────────────────────────────────┐
│                    传统三层架构                                  │
├─────────────────────────────────────────────────────────────────┤
│  UI Layer                                                       │
│      │                                                          │
│      ▼  SQL/JDBC                                                │
│  Business Logic Layer  ◄──────►  多次往返数据库                  │
│      │                                                          │
│      ▼ 简单的CRUD                                               │
│  Data Access Layer                                              │
│      │                                                          │
│      ▼                                                          │
│  Database (仅存储)                                               │
└─────────────────────────────────────────────────────────────────┘

                          vs

┌─────────────────────────────────────────────────────────────────┐
│                    数据库中心架构 (DCA)                          │
├─────────────────────────────────────────────────────────────────┤
│  UI Layer                                                       │
│      │                                                          │
│      ▼ 存储过程调用                                              │
│  Thin API Layer  ◄────────────►  单次往返数据库                  │
│                                  业务逻辑在数据库中执行           │
│  Database (存储 + 业务逻辑)                                      │
│      ├── 存储过程 (业务规则)                                     │
│      ├── 触发器 (自动化)                                         │
│      ├── 函数 (计算逻辑)                                         │
│      └── 视图 (数据封装)                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 DCA的核心优势

| 优势 | 说明 | 量化指标 |
|-----|------|---------|
| **性能** | 减少网络往返 | 延迟降低50-80% |
| **一致性** | ACID原生保证 | 100%数据一致性 |
| **安全** | SQL注入消除 | 漏洞减少95% |
| **可维护** | 业务逻辑集中 | 维护成本降低60% |

---

## 2. 环境准备

### 2.1 数据库环境

```bash
# 检查PostgreSQL版本
psql --version
# 要求: PostgreSQL 14+ (推荐18)

# 创建测试数据库
CREATE DATABASE dca_quickstart;
\c dca_quickstart
```

### 2.2 扩展安装

```sql
-- 安装常用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- PG 18用户安装UUIDv7
-- CREATE EXTENSION IF NOT EXISTS "uuidv7";  -- PG 18+
```

---

## 3. 5分钟入门

### 3.1 创建第一个存储过程

```sql
-- ============================================
-- 步骤1: 创建测试表
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- 步骤2: 创建存储过程 - 创建用户
-- ============================================
CREATE OR REPLACE PROCEDURE sp_user_create(
    IN p_username VARCHAR,
    IN p_email VARCHAR,
    OUT p_user_id UUID,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 输入验证
    IF p_username IS NULL OR LENGTH(TRIM(p_username)) < 3 THEN
        p_success := false;
        p_message := 'Username must be at least 3 characters';
        RETURN;
    END IF;

    -- 检查邮箱格式
    IF p_email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        p_success := false;
        p_message := 'Invalid email format';
        RETURN;
    END IF;

    -- 插入用户
    INSERT INTO users (username, email)
    VALUES (p_username, p_email)
    RETURNING id INTO p_user_id;

    p_success := true;
    p_message := 'User created successfully';

EXCEPTION
    WHEN unique_violation THEN
        p_success := false;
        p_message := 'Username or email already exists';
END;
$$;

-- ============================================
-- 步骤3: 调用存储过程
-- ============================================
CALL sp_user_create('john_doe', 'john@example.com', NULL, NULL, NULL);

-- 查看结果
SELECT * FROM users;
```

### 3.2 快速验证

```sql
-- 验证错误处理
CALL sp_user_create('ab', 'invalid-email', NULL, NULL, NULL);
-- 预期: success=false, message='Username must be at least 3 characters'

-- 验证唯一性
CALL sp_user_create('john_doe', 'john2@example.com', NULL, NULL, NULL);
-- 预期: success=false, message='Username or email already exists'
```

**✅ 恭喜！您已创建了第一个DCA风格的存储过程。**

---

## 4. 15分钟实践

### 4.1 电商订单场景

```sql
-- ============================================
-- 步骤1: 创建订单相关表
-- ============================================
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    total DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL
);

-- 插入测试数据
INSERT INTO products (name, stock, price) VALUES
    ('Laptop', 10, 999.99),
    ('Mouse', 50, 29.99),
    ('Keyboard', 30, 79.99);

-- ============================================
-- 步骤2: 创建带事务的存储过程
-- ============================================
CREATE OR REPLACE PROCEDURE sp_create_order(
    IN p_user_id UUID,
    IN p_items JSONB,  -- [{"product_id": 1, "qty": 2}, ...]
    OUT p_order_id UUID,
    OUT p_total DECIMAL,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_item JSONB;
    v_product RECORD;
    v_subtotal DECIMAL := 0;
BEGIN
    -- 参数验证
    IF jsonb_array_length(p_items) = 0 THEN
        p_success := false;
        p_message := 'Order must contain at least one item';
        RETURN;
    END IF;

    -- 验证库存
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        SELECT * INTO v_product
        FROM products WHERE id = (v_item->>'product_id')::INT;

        IF NOT FOUND THEN
            p_success := false;
            p_message := format('Product %s not found', v_item->>'product_id');
            RETURN;
        END IF;

        IF v_product.stock < (v_item->>'qty')::INT THEN
            p_success := false;
            p_message := format('Insufficient stock for product %s', v_product.name);
            RETURN;
        END IF;

        v_subtotal := v_subtotal + (v_item->>'qty')::INT * v_product.price;
    END LOOP;

    -- 创建订单
    INSERT INTO orders (user_id, total, status)
    VALUES (p_user_id, v_subtotal, 'confirmed')
    RETURNING id INTO p_order_id;

    -- 创建订单项并扣减库存
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        -- 插入订单项
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        SELECT
            p_order_id,
            id,
            (v_item->>'qty')::INT,
            price
        FROM products WHERE id = (v_item->>'product_id')::INT;

        -- 扣减库存
        UPDATE products
        SET stock = stock - (v_item->>'qty')::INT
        WHERE id = (v_item->>'product_id')::INT;
    END LOOP;

    p_total := v_subtotal;
    p_success := true;
    p_message := 'Order created successfully';

EXCEPTION
    WHEN OTHERS THEN
        p_success := false;
        p_message := format('Error: %s', SQLERRM);
        RAISE;
END;
$$;

-- ============================================
-- 步骤3: 测试订单创建
-- ============================================
-- 创建测试用户
INSERT INTO users (id, username, email)
VALUES (uuid_generate_v4(), 'test_user', 'test@example.com')
RETURNING id;

-- 假设用户ID是: <复制上面的UUID>
-- 创建订单
CALL sp_create_order(
    '<用户UUID>',
    '[{"product_id": 1, "qty": 1}, {"product_id": 2, "qty": 2}]'::JSONB,
    NULL, NULL, NULL, NULL
);

-- 验证结果
SELECT * FROM orders;
SELECT * FROM order_items;
SELECT * FROM products;  -- 查看库存变化
```

### 4.2 添加事件通知

```sql
-- ============================================
-- 步骤4: 订单创建后发送通知
-- ============================================
CREATE OR REPLACE PROCEDURE sp_create_order_with_notify(
    IN p_user_id UUID,
    IN p_items JSONB,
    OUT p_order_id UUID,
    OUT p_total DECIMAL,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 调用基础订单创建
    CALL sp_create_order(p_user_id, p_items, p_order_id, p_total, p_success, p_message);

    -- 如果成功，发送通知
    IF p_success THEN
        PERFORM pg_notify('order_created', jsonb_build_object(
            'order_id', p_order_id,
            'user_id', p_user_id,
            'total', p_total,
            'timestamp', NOW()
        )::TEXT);
    END IF;
END;
$$;

-- 在另一个会话中监听
-- LISTEN order_created;
```

### 4.3 Python客户端示例

```python
# ============================================
# Python调用存储过程
# ============================================

import psycopg2
import json
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(
        host="localhost",
        database="dca_quickstart",
        user="postgres",
        password="your_password"
    )
    try:
        yield conn
    finally:
        conn.close()

class OrderService:
    """订单服务 - DCA风格"""

    def create_order(self, user_id: str, items: list):
        """
        创建订单
        所有业务逻辑在数据库中执行
        """
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 调用存储过程
                cur.execute("""
                    CALL sp_create_order(%s, %s, NULL, NULL, NULL, NULL)
                """, (user_id, json.dumps(items)))

                # 获取输出参数
                cur.execute("FETCH ALL IN \"\"" )
                result = cur.fetchone()

                conn.commit()

                return {
                    'order_id': result[0],
                    'total': result[1],
                    'success': result[2],
                    'message': result[3]
                }

# 使用示例
if __name__ == "__main__":
    service = OrderService()

    result = service.create_order(
        user_id="用户UUID",
        items=[
            {"product_id": 1, "qty": 1},
            {"product_id": 2, "qty": 2}
        ]
    )

    print(f"Order created: {result}")
```

**✅ 恭喜！您已实现了一个完整的DCA订单流程。**

---

## 5. 30分钟进阶

### 5.1 读写分离路由

```sql
-- ============================================
-- 存储过程读写路由标记
-- ============================================

-- 读操作函数（可路由到从库）
CREATE OR REPLACE FUNCTION fn_get_user_orders(
    p_user_id UUID,
    p_page INT DEFAULT 1
)
RETURNS TABLE (
    order_id UUID,
    total DECIMAL,
    status VARCHAR,
    created_at TIMESTAMP
)
LANGUAGE plpgsql
STABLE  -- 标记为稳定函数，允许从库读取
AS $$
BEGIN
    RETURN QUERY
    SELECT o.id, o.total, o.status, o.created_at
    FROM orders o
    WHERE o.user_id = p_user_id
    ORDER BY o.created_at DESC
    LIMIT 20 OFFSET (p_page - 1) * 20;
END;
$$;

COMMENT ON FUNCTION fn_get_user_orders IS '@read_operation:true';

-- 写操作存储过程（强制主库）
CREATE OR REPLACE PROCEDURE sp_cancel_order(
    IN p_order_id UUID,
    IN p_reason TEXT,
    OUT p_success BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE orders
    SET status = 'cancelled',
        cancelled_reason = p_reason,
        cancelled_at = NOW()
    WHERE id = p_order_id
      AND status IN ('pending', 'confirmed');

    GET DIAGNOSTICS p_success = ROW_COUNT;
END;
$$;

COMMENT ON PROCEDURE sp_cancel_order IS '@write_operation:true';
```

### 5.2 分布式ID生成（PG 18 UUIDv7）

```sql
-- ============================================
-- 使用UUIDv7（时间有序UUID）
-- ============================================

-- PG 18+ 原生支持
CREATE TABLE distributed_orders (
    id UUID PRIMARY KEY DEFAULT uuidv7(),  -- PG 18+
    user_id BIGINT NOT NULL,
    total DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ID提取时间戳
CREATE OR REPLACE FUNCTION fn_uuid_to_timestamp(p_uuid UUID)
RETURNS TIMESTAMP
LANGUAGE plpgsql
AS $$
DECLARE
    v_hex TEXT;
    v_unix_ms BIGINT;
BEGIN
    -- UUIDv7: tttttttt-tttt-7xxx-8xxx-xxxxxxxxxxxx
    v_hex := REPLACE(SUBSTRING(p_uuid::TEXT, 1, 8) ||
                     SUBSTRING(p_uuid::TEXT, 10, 4), '-', '');
    v_unix_ms := ('x' || v_hex)::BIT(48)::BIGINT;
    RETURN TO_TIMESTAMP(v_unix_ms / 1000.0);
END;
$$;
```

### 5.3 缓存失效通知

```sql
-- ============================================
-- 数据变更时通知缓存层
-- ============================================

CREATE OR REPLACE FUNCTION fn_cache_invalidation_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- 发布缓存失效事件
    PERFORM pg_notify('cache_invalidation', jsonb_build_object(
        'table', TG_TABLE_NAME,
        'operation', TG_OP,
        'key', CASE
            WHEN TG_OP = 'DELETE' THEN OLD.id::TEXT
            ELSE NEW.id::TEXT
        END
    )::TEXT);

    RETURN COALESCE(NEW, OLD);
END;
$$;

-- 应用到产品表
CREATE TRIGGER trg_products_cache_invalidation
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION fn_cache_invalidation_trigger();
```

---

## 6. 下一步

### 6.1 继续学习

| 主题 | 推荐文档 | 预计时间 |
|-----|---------|---------|
| 存储过程模式 | 02-Stored-Procedure-Patterns-DEEP-V2.md | 2小时 |
| 性能优化 | 05-Performance-Optimization-DEEP-V2.md | 3小时 |
| PG 18新特性 | 13-PostgreSQL18-New-Features-DEEP-V2.md | 4小时 |
| 分布式架构 | 14-Distributed-Architecture-DEEP-V2.md | 6小时 |
| 事件驱动 | 15-Database-Notifications-DEEP-V2.md | 4小时 |

### 6.2 实践项目

**练习1**: 扩展订单系统

- 添加库存预占机制
- 实现订单超时取消
- 添加订单状态历史

**练习2**: 实现用户认证

- 密码加密存储
- JWT令牌管理
- 登录审计日志

**练习3**: 添加报表功能

- 销售统计存储过程
- 缓存策略
- 定时任务

### 6.3 资源索引

```text
📚 完整文档索引
├── INDEX.md                          # 文档总索引
├── 00-ROADMAP-AND-ACTION-PLAN-v2.md  # 完整路线图
├── 01-Theory-and-Principles          # 理论基础
├── 02-Stored-Procedure-Patterns      # 设计模式
├── 04-API-Design                     # API设计
├── 05-Performance-Optimization       # 性能优化
├── 13-PostgreSQL18-New-Features      # PG 18新特性 ⭐
├── 14-Distributed-Architecture       # 分布式架构 ⭐
├── 15-Database-Notifications         # 事件驱动 ⭐
└── 16-ReadWrite-SyncAsync            # 读写分离 ⭐
```

---

## 🎉 总结

通过本快速开始指南，您已经：

1. ✅ 理解了DCA的核心价值
2. ✅ 创建了第一个存储过程
3. ✅ 实现了电商订单流程
4. ✅ 了解了读写分离基础
5. ✅ 体验了事件通知机制

**DCA不是银弹，但它是构建高性能、高一致性系统的强大工具。**

继续探索完整文档，构建您的数据库中心架构！

---

**快速反馈**

如在实践过程中遇到问题，请检查：

1. PostgreSQL版本是否14+
2. 扩展是否正确安装
3. 代码示例是否完整复制

**版本信息**: v2.0
**最后更新**: 2026-03-04
