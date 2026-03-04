# DCA端到端完整实现示例

> **文档类型**: 完整项目实现
> **业务场景**: 电商订单系统
> **技术栈**: PostgreSQL 18 + Python + PgBouncer
> **状态**: 生产就绪代码

---

## 目录

- [DCA端到端完整实现示例](#dca端到端完整实现示例)
  - [目录](#目录)
  - [1. 项目结构](#1-项目结构)
  - [2. 数据库Schema](#2-数据库schema)
  - [3. 核心存储过程](#3-核心存储过程)
  - [4. Python后端实现](#4-python后端实现)
  - [5. 部署配置](#5-部署配置)

---

## 1. 项目结构

```
dca-ecommerce/
├── database/
│   ├── 01_schema.sql           # 数据库Schema
│   ├── 02_procedures.sql       # 存储过程
│   ├── 03_triggers.sql         # 触发器
│   ├── 04_seed_data.sql        # 种子数据
│   └── 05_rls_policies.sql     # 行级安全策略
├── backend/
│   ├── app.py                  # Flask/FastAPI应用
│   ├── database.py             # 数据库连接池
│   ├── services/
│   │   ├── order_service.py    # 订单服务
│   │   └── user_service.py     # 用户服务
│   └── config.py               # 配置文件
├── docker/
│   ├── docker-compose.yml      # Docker编排
│   └── Dockerfile
├── tests/
│   ├── test_procedures.sql     # 存储过程测试
│   └── test_integration.py     # 集成测试
└── docs/
    └── api.md                  # API文档
```

---

## 2. 数据库Schema

```sql
-- ============================================
-- 01_schema.sql - 完整数据库Schema
-- ============================================

-- 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);

-- 产品表
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'paid', 'shipped', 'delivered', 'cancelled')),
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    shipping_address JSONB NOT NULL,
    payment_method VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    paid_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ
);

-- 订单项表
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 库存预占表（防止超卖）
CREATE TABLE inventory_reservations (
    id BIGSERIAL PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    reserved_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    is_committed BOOLEAN DEFAULT false
);

-- 审计日志表
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id TEXT NOT NULL,
    operation VARCHAR(10) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET
);

-- 索引
CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status) WHERE status IN ('pending', 'confirmed');
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_inventory_reservations_order ON inventory_reservations(order_id);
CREATE INDEX idx_inventory_reservations_expires ON inventory_reservations(expires_at)
    WHERE is_committed = false;
CREATE INDEX idx_audit_logs_table ON audit_logs(table_name, changed_at DESC);

-- 分区（按时间分区订单表）
CREATE TABLE orders_2026_01 PARTITION OF orders
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE orders_2026_02 PARTITION OF orders
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE orders_2026_03 PARTITION OF orders
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
```

---

## 3. 核心存储过程

```sql
-- ============================================
-- 02_procedures.sql - 核心业务存储过程
-- ============================================

-- 1. 用户注册
CREATE OR REPLACE PROCEDURE sp_user_register(
    IN p_username VARCHAR,
    IN p_email VARCHAR,
    IN p_password VARCHAR,
    OUT p_user_id UUID,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_password_hash VARCHAR;
BEGIN
    -- 验证输入
    IF p_username IS NULL OR LENGTH(TRIM(p_username)) < 3 THEN
        p_success := false;
        p_message := 'Username must be at least 3 characters';
        RETURN;
    END IF;

    IF p_email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        p_success := false;
        p_message := 'Invalid email format';
        RETURN;
    END IF;

    IF LENGTH(p_password) < 8 THEN
        p_success := false;
        p_message := 'Password must be at least 8 characters';
        RETURN;
    END IF;

    -- 密码哈希
    v_password_hash := crypt(p_password, gen_salt('bf', 10));

    -- 插入用户
    BEGIN
        INSERT INTO users (username, email, password_hash)
        VALUES (p_username, p_email, v_password_hash)
        RETURNING id INTO p_user_id;

        p_success := true;
        p_message := 'User registered successfully';

    EXCEPTION WHEN unique_violation THEN
        p_success := false;
        p_message := 'Username or email already exists';
    END;
END;
$$;

-- 2. 创建订单（带库存预占）
CREATE OR REPLACE PROCEDURE sp_order_create(
    IN p_user_id UUID,
    IN p_items JSONB,  -- [{"product_id": 1, "quantity": 2}, ...]
    IN p_shipping_address JSONB,
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
    v_total DECIMAL := 0;
    v_reservation_id BIGINT;
BEGIN
    -- 验证输入
    IF jsonb_array_length(p_items) = 0 THEN
        p_success := false;
        p_message := 'Order must contain at least one item';
        RETURN;
    END IF;

    -- 检查库存并预占
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        SELECT * INTO v_product
        FROM products
        WHERE id = (v_item->>'product_id')::BIGINT
        FOR UPDATE;  -- 锁定库存行

        IF NOT FOUND THEN
            p_success := false;
            p_message := format('Product %s not found', v_item->>'product_id');
            RETURN;
        END IF;

        IF v_product.stock_quantity < (v_item->>'quantity')::INT THEN
            p_success := false;
            p_message := format('Insufficient stock for %s (available: %s, requested: %s)',
                v_product.name, v_product.stock_quantity, v_item->>'quantity');
            RETURN;
        END IF;

        -- 预减库存
        UPDATE products
        SET stock_quantity = stock_quantity - (v_item->>'quantity')::INT
        WHERE id = v_product.id;

        v_total := v_total + ((v_item->>'quantity')::INT * v_product.price);
    END LOOP;

    -- 创建订单
    p_order_id := uuid_generate_v4();

    INSERT INTO orders (id, user_id, total_amount, shipping_address)
    VALUES (p_order_id, p_user_id, v_total, p_shipping_address);

    -- 创建订单项和库存预占
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        -- 插入订单项
        INSERT INTO order_items (order_id, product_id, quantity, unit_price)
        SELECT
            p_order_id,
            id,
            (v_item->>'quantity')::INT,
            price
        FROM products WHERE id = (v_item->>'product_id')::BIGINT;

        -- 记录库存预占
        INSERT INTO inventory_reservations (order_id, product_id, quantity, expires_at)
        VALUES (p_order_id, (v_item->>'product_id')::BIGINT, (v_item->>'quantity')::INT, NOW() + INTERVAL '30 minutes');
    END LOOP;

    p_total := v_total;
    p_success := true;
    p_message := 'Order created successfully';

    -- 发送通知
    PERFORM pg_notify('order_created', jsonb_build_object(
        'order_id', p_order_id,
        'user_id', p_user_id,
        'total', v_total
    )::TEXT);

EXCEPTION WHEN OTHERS THEN
    p_success := false;
    p_message := format('Error: %s', SQLERRM);
    RAISE;
END;
$$;

-- 3. 确认支付
CREATE OR REPLACE PROCEDURE sp_order_confirm_payment(
    IN p_order_id UUID,
    IN p_payment_method VARCHAR,
    IN p_payment_reference VARCHAR,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order RECORD;
BEGIN
    SELECT * INTO v_order FROM orders WHERE id = p_order_id FOR UPDATE;

    IF NOT FOUND THEN
        p_success := false;
        p_message := 'Order not found';
        RETURN;
    END IF;

    IF v_order.status != 'pending' THEN
        p_success := false;
        p_message := format('Order status is %s, cannot confirm payment', v_order.status);
        RETURN;
    END IF;

    -- 更新订单状态
    UPDATE orders
    SET status = 'paid',
        payment_method = p_payment_method,
        paid_at = NOW(),
        updated_at = NOW()
    WHERE id = p_order_id;

    -- 提交库存预占
    UPDATE inventory_reservations
    SET is_committed = true
    WHERE order_id = p_order_id;

    p_success := true;
    p_message := 'Payment confirmed';

    PERFORM pg_notify('order_paid', jsonb_build_object(
        'order_id', p_order_id,
        'payment_reference', p_payment_reference
    )::TEXT);
END;
$$;

-- 4. 取消订单（自动释放库存）
CREATE OR REPLACE PROCEDURE sp_order_cancel(
    IN p_order_id UUID,
    IN p_reason TEXT,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order RECORD;
    v_reservation RECORD;
BEGIN
    SELECT * INTO v_order FROM orders WHERE id = p_order_id FOR UPDATE;

    IF NOT FOUND THEN
        p_success := false;
        p_message := 'Order not found';
        RETURN;
    END IF;

    IF v_order.status IN ('shipped', 'delivered') THEN
        p_success := false;
        p_message := 'Cannot cancel shipped or delivered order';
        RETURN;
    END IF;

    -- 恢复库存
    FOR v_reservation IN
        SELECT * FROM inventory_reservations WHERE order_id = p_order_id
    LOOP
        UPDATE products
        SET stock_quantity = stock_quantity + v_reservation.quantity
        WHERE id = v_reservation.product_id;
    END LOOP;

    -- 更新订单状态
    UPDATE orders
    SET status = 'cancelled',
        updated_at = NOW()
    WHERE id = p_order_id;

    -- 删除预占记录
    DELETE FROM inventory_reservations WHERE order_id = p_order_id;

    p_success := true;
    p_message := 'Order cancelled';
END;
$$;

-- 5. 获取用户订单列表（分页）
CREATE OR REPLACE FUNCTION fn_user_orders(
    p_user_id UUID,
    p_page INT DEFAULT 1,
    p_page_size INT DEFAULT 20
)
RETURNS TABLE (
    order_id UUID,
    status VARCHAR,
    total_amount DECIMAL,
    item_count BIGINT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.id,
        o.status,
        o.total_amount,
        COUNT(oi.id) as item_count,
        o.created_at
    FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    WHERE o.user_id = p_user_id
    GROUP BY o.id, o.status, o.total_amount, o.created_at
    ORDER BY o.created_at DESC
    LIMIT p_page_size OFFSET (p_page - 1) * p_page_size;
END;
$$;

-- 6. 销售报表
CREATE OR REPLACE FUNCTION fn_sales_report(
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    report_date DATE,
    order_count BIGINT,
    total_revenue DECIMAL,
    avg_order_value DECIMAL,
    unique_customers BIGINT
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        o.created_at::DATE as report_date,
        COUNT(*) as order_count,
        COALESCE(SUM(o.total_amount), 0) as total_revenue,
        COALESCE(AVG(o.total_amount), 0) as avg_order_value,
        COUNT(DISTINCT o.user_id) as unique_customers
    FROM orders o
    WHERE o.created_at BETWEEN p_start_date AND p_end_date
      AND o.status NOT IN ('cancelled', 'pending')
    GROUP BY o.created_at::DATE
    ORDER BY report_date;
END;
$$;
```

---

## 4. Python后端实现

```python
# ============================================
# database.py - 数据库连接管理
# ============================================

import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from functools import wraps

# 连接池配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '6432'),  # PgBouncer端口
    'database': os.getenv('DB_NAME', 'ecommerce'),
    'user': os.getenv('DB_USER', 'app_user'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

# 创建连接池
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=50,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    """获取数据库游标的上下文管理器"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

def call_procedure(proc_name, params=None, fetch_result=False):
    """
    调用存储过程的通用函数

    Args:
        proc_name: 存储过程名称
        params: 参数字典或元组
        fetch_result: 是否获取结果

    Returns:
        如果fetch_result为True，返回结果字典
    """
    with get_db_cursor(commit=True) as cursor:
        # 构建参数占位符
        if params:
            if isinstance(params, dict):
                placeholders = ', '.join([f'%({k})s' for k in params.keys()])
            else:
                placeholders = ', '.join(['%s'] * len(params))
        else:
            placeholders = ''

        # 调用存储过程
        sql = f"CALL {proc_name}({placeholders})"
        cursor.execute(sql, params)

        # 获取输出参数
        if fetch_result:
            cursor.execute("FETCH ALL IN \"\" ")
            result = cursor.fetchone()
            return result

        return None
```

```python
# ============================================
# services/order_service.py - 订单服务
# ============================================

import json
from database import call_procedure

class OrderService:
    """订单服务 - DCA实现"""

    @staticmethod
    def create_order(user_id: str, items: list, shipping_address: dict):
        """
        创建订单

        Args:
            user_id: 用户ID
            items: 订单项列表 [{"product_id": 1, "quantity": 2}, ...]
            shipping_address: 配送地址

        Returns:
            dict: 包含order_id, total, success, message
        """
        result = call_procedure(
            'sp_order_create',
            {
                'p_user_id': user_id,
                'p_items': json.dumps(items),
                'p_shipping_address': json.dumps(shipping_address)
            },
            fetch_result=True
        )

        return {
            'order_id': result[0],
            'total': float(result[1]) if result[1] else 0,
            'success': result[2],
            'message': result[3]
        }

    @staticmethod
    def confirm_payment(order_id: str, payment_method: str, payment_reference: str):
        """确认支付"""
        result = call_procedure(
            'sp_order_confirm_payment',
            {
                'p_order_id': order_id,
                'p_payment_method': payment_method,
                'p_payment_reference': payment_reference
            },
            fetch_result=True
        )

        return {
            'success': result[0],
            'message': result[1]
        }

    @staticmethod
    def cancel_order(order_id: str, reason: str):
        """取消订单"""
        result = call_procedure(
            'sp_order_cancel',
            {
                'p_order_id': order_id,
                'p_reason': reason
            },
            fetch_result=True
        )

        return {
            'success': result[0],
            'message': result[1]
        }

    @staticmethod
    def get_user_orders(user_id: str, page: int = 1, page_size: int = 20):
        """获取用户订单列表"""
        # 使用函数而不是存储过程
        from database import get_db_cursor

        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM fn_user_orders(%s, %s, %s)",
                (user_id, page, page_size)
            )
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

            return [dict(zip(columns, row)) for row in results]
```

```python
# ============================================
# app.py - Flask/FastAPI应用
# ============================================

from flask import Flask, request, jsonify
from services.order_service import OrderService
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'dca-ecommerce'})

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单"""
    data = request.json

    result = OrderService.create_order(
        user_id=data['user_id'],
        items=data['items'],
        shipping_address=data['shipping_address']
    )

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/orders/<order_id>/payment', methods=['POST'])
def confirm_payment(order_id):
    """确认支付"""
    data = request.json

    result = OrderService.confirm_payment(
        order_id=order_id,
        payment_method=data['payment_method'],
        payment_reference=data['payment_reference']
    )

    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/orders/<order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单"""
    data = request.json

    result = OrderService.cancel_order(
        order_id=order_id,
        reason=data.get('reason', '')
    )

    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/users/<user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """获取用户订单列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    orders = OrderService.get_user_orders(user_id, page, page_size)
    return jsonify({'orders': orders}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', False))
```

---

## 5. 部署配置

```yaml
# ============================================
# docker-compose.yml - 完整部署配置
# ============================================

version: '3.8'

services:
  # PostgreSQL主库
  postgres-primary:
    image: postgres:18-alpine
    container_name: dca-postgres-primary
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-SecurePass123!}
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
      - ./database/01_schema.sql:/docker-entrypoint-initdb.d/01_schema.sql
      - ./database/02_procedures.sql:/docker-entrypoint-initdb.d/02_procedures.sql
      - ./database/03_triggers.sql:/docker-entrypoint-initdb.d/03_triggers.sql
      - ./database/04_seed_data.sql:/docker-entrypoint-initdb.d/04_seed_data.sql
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    networks:
      - dca-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # PgBouncer连接池
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    container_name: dca-pgbouncer
    environment:
      DATABASES_HOST: postgres-primary
      DATABASES_PORT: 5432
      DATABASES_DATABASE: ecommerce
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 1000
      DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:6432"
    depends_on:
      - postgres-primary
    networks:
      - dca-network

  # 后端应用
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: dca-backend
    environment:
      DB_HOST: pgbouncer
      DB_PORT: 6432
      DB_NAME: ecommerce
      DB_USER: app_user
      DB_PASSWORD: ${DB_PASSWORD:-SecurePass123!}
    ports:
      - "5000:5000"
    depends_on:
      - pgbouncer
    networks:
      - dca-network
    restart: unless-stopped

  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: dca-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - dca-network

  # Grafana仪表盘
  grafana:
    image: grafana/grafana:latest
    container_name: dca-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - dca-network

volumes:
  postgres_primary_data:
  prometheus_data:
  grafana_data:

networks:
  dca-network:
    driver: bridge
```

---

**项目状态**: 生产就绪
**最后更新**: 2026-03-04
**版本**: v1.0
