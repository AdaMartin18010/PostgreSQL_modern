# 数据库外部通知机制深度分析 v2.0

> **文档类型**: 数据库事件驱动架构
> **核心技术**: LISTEN/NOTIFY, WebSocket, Webhook, 消息队列集成
> **创建日期**: 2026-03-04
> **文档长度**: 10000+字

---

## 目录

- [数据库外部通知机制深度分析 v2.0](#数据库外部通知机制深度分析-v20)
  - [目录](#目录)
  - [摘要](#摘要)
  - [1. 数据库通知架构概览](#1-数据库通知架构概览)
    - [1.1 为什么需要数据库通知](#11-为什么需要数据库通知)
    - [1.2 通知架构模式](#12-通知架构模式)
  - [2. LISTEN/NOTIFY 核心机制](#2-listennotify-核心机制)
    - [2.1 基本用法](#21-基本用法)
    - [2.2 存储过程集成](#22-存储过程集成)
    - [2.3 客户端监听实现](#23-客户端监听实现)
  - [3. WebSocket实时推送](#3-websocket实时推送)
    - [3.1 WebSocket桥接架构](#31-websocket桥接架构)
    - [3.2 存储过程触发WebSocket](#32-存储过程触发websocket)
  - [4. Webhook回调机制](#4-webhook回调机制)
    - [4.1 可靠Webhook投递](#41-可靠webhook投递)
    - [4.2 签名验证](#42-签名验证)
  - [5. 消息队列集成](#5-消息队列集成)
    - [5.1 RabbitMQ集成](#51-rabbitmq集成)
    - [5.2 Kafka集成](#52-kafka集成)
    - [5.3 Redis Pub/Sub](#53-redis-pubsub)
  - [6. 变更数据捕获(CDC)](#6-变更数据捕获cdc)
    - [6.1 Debezium集成](#61-debezium集成)
    - [6.2 逻辑解码槽](#62-逻辑解码槽)
  - [7. 事件溯源模式](#7-事件溯源模式)
    - [7.1 事件存储设计](#71-事件存储设计)
    - [7.2 存储过程发布事件](#72-存储过程发布事件)
  - [8. 可靠投递保证](#8-可靠投递保证)
    - [8.1 至少一次投递](#81-至少一次投递)
    - [8.2 恰好一次投递](#82-恰好一次投递)
  - [9. 安全与认证](#9-安全与认证)
  - [10. 性能优化](#10-性能优化)
  - [11. 持续推进计划](#11-持续推进计划)
    - [短期目标 (1-2周)](#短期目标-1-2周)
    - [中期目标 (1个月)](#中期目标-1个月)
    - [长期目标 (3个月)](#长期目标-3个月)

---

## 摘要

数据库通知机制是事件驱动架构的核心组件，使PostgreSQL能够主动将数据变更通知外部系统。
本文档全面分析LISTEN/NOTIFY、WebSocket、Webhook、消息队列集成等技术，提供完整的DCA事件驱动编程模型。

**核心能力**:

- **实时推送**: 数据变更毫秒级触达客户端
- **解耦架构**: 数据库与业务系统松耦合
- **事件溯源**: 完整记录系统状态变更历史
- **可靠投递**: 保证关键事件不丢失

---

## 1. 数据库通知架构概览

### 1.1 为什么需要数据库通知

```text
┌─────────────────────────────────────────────────────────────────────┐
│  传统轮询模式 vs 事件驱动模式                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  传统轮询（低效）                                                     │
│  ─────────────                                                      │
│                                                                     │
│  App ──► 查询有变更? ◄── 没有 ──► 等待5秒 ──► 查询有变更? ◄── 没有  │
│   │                                            │                    │
│   └────────────── 循环往复 ────────────────────┘                    │
│                                                                     │
│  问题: 延迟高、数据库负载大、实时性差                                   │
│                                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│                                                                     │
│  事件驱动（高效）                                                     │
│  ─────────────                                                      │
│                                                                     │
│  App ──► LISTEN orders ──► 等待                                     │
│                              │                                      │
│                              │ 数据变更                              │
│                              ▼                                      │
│                         ┌─────────┐                                 │
│                         │ Trigger │ ──► NOTIFY orders, payload      │
│                         └────┬────┘                                 │
│                              │                                      │
│                              ▼                                      │
│  App ◄── 实时推送 ────── 收到通知!                                   │
│                                                                     │
│  优势: 实时、低延迟、低负载、可扩展                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 通知架构模式

| 模式 | 延迟 | 可靠性 | 适用场景 | 复杂度 |
|-----|------|-------|---------|-------|
| **LISTEN/NOTIFY** | <10ms | 会话级 | 实时推送、缓存失效 | 低 |
| **WebSocket** | <50ms | 需保障 | 实时UI更新、聊天 | 中 |
| **Webhook** | <1s | 可靠投递 | 第三方集成、异步通知 | 中 |
| **消息队列** | <100ms | 高可靠 | 微服务通信、削峰 | 中 |
| **CDC** | <1s | 高可靠 | 数据同步、分析 | 高 |

---

## 2. LISTEN/NOTIFY 核心机制

### 2.1 基本用法

```sql
-- ============================================
-- LISTEN/NOTIFY 基础操作
-- ============================================

-- 1. 会话A：监听频道
LISTEN order_events;
LISTEN user_notifications;

-- 2. 会话B：发送通知
NOTIFY order_events, '{"order_id": 12345, "status": "confirmed"}';

-- 3. 查看监听状态
SELECT * FROM pg_listening_channels();

-- 4. 取消监听
UNLISTEN order_events;
UNLISTEN *;  -- 取消所有监听
```

### 2.2 存储过程集成

```sql
-- ============================================
-- 存储过程中的NOTIFY
-- ============================================

-- 1. 订单状态变更通知
CREATE OR REPLACE PROCEDURE sp_update_order_status_with_notify(
    IN p_order_id UUID,
    IN p_new_status VARCHAR,
    IN p_user_id BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_old_status VARCHAR;
    v_payload JSONB;
BEGIN
    -- 获取旧状态
    SELECT status INTO v_old_status
    FROM orders WHERE id = p_order_id;

    -- 更新状态
    UPDATE orders
    SET status = p_new_status, updated_at = NOW()
    WHERE id = p_order_id;

    -- 构建通知负载
    v_payload := jsonb_build_object(
        'event_type', 'order_status_changed',
        'order_id', p_order_id,
        'user_id', p_user_id,
        'old_status', v_old_status,
        'new_status', p_new_status,
        'timestamp', NOW()
    );

    -- 发送通知到不同频道
    -- 特定订单频道（用户监听）
    PERFORM pg_notify('order_' || p_order_id::TEXT, v_payload::TEXT);

    -- 用户通知频道
    PERFORM pg_notify('user_' || p_user_id::TEXT, v_payload::TEXT);

    -- 全局订单事件频道
    PERFORM pg_notify('order_events', v_payload::TEXT);

END;
$$;

-- 2. 批量通知存储过程
CREATE OR REPLACE PROCEDURE sp_notify_batch(
    IN p_channel TEXT,
    IN p_events JSONB  -- [{"channel": "...", "payload": {...}}, ...]
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event JSONB;
BEGIN
    FOR v_event IN SELECT * FROM jsonb_array_elements(p_events)
    LOOP
        PERFORM pg_notify(
            v_event->>'channel',
            v_event->>'payload'
        );
    END LOOP;
END;
$$;

-- 3. 条件通知（智能路由）
CREATE OR REPLACE PROCEDURE sp_smart_notify(
    IN p_event_type TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_routing_config JSONB;
    v_targets JSONB;
    v_target TEXT;
BEGIN
    -- 获取路由配置
    v_routing_config := '{
        "order_created": ["order_events", "analytics_queue"],
        "order_paid": ["order_events", "fulfillment_queue", "user_" + payload.user_id],
        "inventory_low": ["admin_alerts", "procurement_queue"]
    }'::JSONB;

    v_targets := v_routing_config->p_event_type;

    IF v_targets IS NOT NULL THEN
        FOR v_target IN SELECT jsonb_array_elements_text(v_targets)
        LOOP
            -- 支持动态路由表达式
            IF v_target LIKE 'user_%' THEN
                v_target := replace(v_target, 'user_', 'user_' || (p_payload->>'user_id'));
            END IF;

            PERFORM pg_notify(v_target, p_payload::TEXT);
        END LOOP;
    END IF;
END;
$$;
```

### 2.3 客户端监听实现

```python
# ============================================
# Python客户端LISTEN/NOTIFY实现
# ============================================

import asyncio
import asyncpg
import json
from datetime import datetime

class PostgresNotifier:
    """PostgreSQL LISTEN/NOTIFY客户端"""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.connection = None
        self.listeners = {}

    async def connect(self):
        """建立连接并启动监听"""
        self.connection = await asyncpg.connect(self.dsn)

        # 添加通知处理器
        self.connection.add_termination_listener(self._on_disconnect)

    async def listen(self, channel: str, callback):
        """监听指定频道"""
        await self.connection.execute(f"LISTEN {channel}")
        self.listeners[channel] = callback

        # 启动监听循环
        asyncio.create_task(self._listen_loop())

    async def _listen_loop(self):
        """持续监听通知"""
        while True:
            try:
                # 等待通知（超时1秒）
                notification = await asyncio.wait_for(
                    self.connection.fetchrow("SELECT 1"),
                    timeout=1.0
                )

                # 使用poll获取通知
                while self.connection.is_in_transaction():
                    await asyncio.sleep(0.01)

                # 检查通知
                async for notif in self.connection.notifies():
                    await self._handle_notification(notif)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"监听错误: {e}")
                await asyncio.sleep(1)

    async def _handle_notification(self, notif):
        """处理收到的通知"""
        channel = notif.channel
        payload = notif.payload

        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = payload

        if channel in self.listeners:
            await self.listeners[channel](channel, data, notif.pid)

    async def _on_disconnect(self, connection):
        """断线重连"""
        print("连接断开，尝试重连...")
        await asyncio.sleep(1)
        await self.connect()

        # 重新订阅所有频道
        for channel in self.listeners.keys():
            await self.connection.execute(f"LISTEN {channel}")


# 使用示例
async def main():
    dsn = "postgresql://user:pass@localhost/mydb"
    notifier = PostgresNotifier(dsn)
    await notifier.connect()

    # 处理订单事件
    async def on_order_event(channel, data, pid):
        print(f"[{datetime.now()}] 订单事件: {data}")

        if data.get('event_type') == 'order_paid':
            # 触发后续处理
            await process_payment_confirmation(data)

    # 处理用户通知
    async def on_user_notification(channel, data, pid):
        print(f"用户通知: {data}")
        await send_push_notification(data)

    await notifier.listen('order_events', on_order_event)
    await notifier.listen('user_12345', on_user_notification)

    # 保持运行
    while True:
        await asyncio.sleep(1)

async def process_payment_confirmation(data):
    """处理支付确认"""
    print(f"处理支付确认: order_id={data.get('order_id')}")
    # 调用物流系统、发送邮件等

async def send_push_notification(data):
    """发送推送通知"""
    print(f"发送推送: {data}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. WebSocket实时推送

### 3.1 WebSocket桥接架构

```text
┌─────────────────────────────────────────────────────────────────────┐
│  PostgreSQL ──► WebSocket 桥接架构                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    PostgreSQL 数据库                           │ │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │ │
│  │  │  Table:     │    │  Function   │    │  NOTIFY     │        │ │
│  │  │  orders     │───►│  fn_notify  │───►│  'events'   │        │ │
│  │  └─────────────┘    └─────────────┘    └──────┬──────┘        │ │
│  └────────────────────────────────────────────────┼───────────────┘ │
│                                                   │                  │
│                                                   │ LISTEN           │
│                                                   ▼                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              WebSocket Bridge (Python/Node.js)                 │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │  │
│  │  │  LISTENER   │    │  Message    │    │  WebSocket  │        │  │
│  │  │  (asyncpg)  │───►│  Router     │───►│  Server     │        │  │
│  │  └─────────────┘    └─────────────┘    └──────┬──────┘        │  │
│  └────────────────────────────────────────────────┼───────────────┘  │
│                                                   │                  │
│                          ┌────────────────────────┼────────────────┐ │
│                          │                        │                │ │
│                          ▼                        ▼                ▼ │
│                    ┌──────────┐           ┌──────────┐     ┌──────────┐
│                    │ Client A │           │ Client B │     │ Client C │
│                    │ (User 1) │           │ (User 2) │     │ (Admin)  │
│                    └──────────┘           └──────────┘     └──────────┘
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 存储过程触发WebSocket

```sql
-- ============================================
-- WebSocket通知存储过程
-- ============================================

-- 1. WebSocket会话管理表
CREATE TABLE websocket_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuidv7(),
    user_id BIGINT,
    connection_info JSONB,
    subscribed_channels TEXT[],
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    last_ping TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 用户消息队列（用于离线消息）
CREATE TABLE user_message_queue (
    message_id UUID PRIMARY KEY DEFAULT uuidv7(),
    user_id BIGINT NOT NULL,
    channel TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    retry_count INT DEFAULT 0
);

-- 3. 智能推送存储过程
CREATE OR REPLACE PROCEDURE sp_websocket_push(
    IN p_target_user_id BIGINT,
    IN p_event_type TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_session RECORD;
    v_enhanced_payload JSONB;
BEGIN
    v_enhanced_payload := jsonb_build_object(
        'type', p_event_type,
        'data', p_payload,
        'timestamp', NOW(),
        'message_id', uuidv7()
    );

    -- 检查用户是否在线
    SELECT * INTO v_session
    FROM websocket_sessions
    WHERE user_id = p_target_user_id
      AND last_ping > NOW() - INTERVAL '2 minutes';

    IF FOUND THEN
        -- 用户在线，直接推送
        PERFORM pg_notify('ws_push', jsonb_build_object(
            'session_id', v_session.session_id,
            'payload', v_enhanced_payload
        )::TEXT);
    ELSE
        -- 用户离线，存入消息队列
        INSERT INTO user_message_queue (user_id, channel, payload)
        VALUES (p_target_user_id, p_event_type, v_enhanced_payload);
    END IF;
END;
$$;

-- 4. 广播存储过程
CREATE OR REPLACE PROCEDURE sp_websocket_broadcast(
    IN p_channel TEXT,
    IN p_event_type TEXT,
    IN p_payload JSONB,
    IN p_filter JSONB DEFAULT NULL  -- 可选的用户过滤条件
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_session RECORD;
    v_should_send BOOLEAN;
BEGIN
    FOR v_session IN
        SELECT * FROM websocket_sessions
        WHERE p_channel = ANY(subscribed_channels)
          AND last_ping > NOW() - INTERVAL '2 minutes'
    LOOP
        v_should_send := true;

        -- 应用过滤器
        IF p_filter IS NOT NULL THEN
            IF p_filter ? 'tenant_id' THEN
                IF (v_session.connection_info->>'tenant_id')::BIGINT
                   != (p_filter->>'tenant_id')::BIGINT THEN
                    v_should_send := false;
                END IF;
            END IF;

            IF p_filter ? 'user_role' THEN
                IF v_session.connection_info->>'role' != p_filter->>'user_role' THEN
                    v_should_send := false;
                END IF;
            END IF;
        END IF;

        IF v_should_send THEN
            PERFORM pg_notify('ws_push', jsonb_build_object(
                'session_id', v_session.session_id,
                'payload', jsonb_build_object(
                    'type', p_event_type,
                    'data', p_payload,
                    'timestamp', NOW()
                )
            )::TEXT);
        END IF;
    END LOOP;
END;
$$;

-- 5. 实时仪表盘更新
CREATE OR REPLACE PROCEDURE sp_dashboard_realtime_update(
    IN p_metric_type TEXT,
    IN p_metric_value JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 推送实时指标到所有仪表盘客户端
    PERFORM pg_notify('dashboard_metrics', jsonb_build_object(
        'metric_type', p_metric_type,
        'value', p_metric_value,
        'timestamp', NOW()
    )::TEXT);
END;
$$;
```

---

## 4. Webhook回调机制

### 4.1 可靠Webhook投递

```sql
-- ============================================
-- 可靠Webhook投递系统
-- ============================================

-- 1. Webhook订阅表
CREATE TABLE webhook_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuidv7(),
    subscriber_name TEXT NOT NULL,
    webhook_url TEXT NOT NULL,
    webhook_secret TEXT NOT NULL,  -- 用于签名
    event_types TEXT[] NOT NULL,   -- 订阅的事件类型
    is_active BOOLEAN DEFAULT true,
    retry_config JSONB DEFAULT '{"max_retries": 3, "backoff_base": 2}'::JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_delivered_at TIMESTAMPTZ,
    failure_count INT DEFAULT 0
);

-- 2. Webhook投递队列表
CREATE TABLE webhook_delivery_queue (
    delivery_id UUID PRIMARY KEY DEFAULT uuidv7(),
    subscription_id UUID REFERENCES webhook_subscriptions(subscription_id),
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, delivered, failed
    attempts INT DEFAULT 0,
    next_retry_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    response_status INT,
    response_body TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 触发Webhook投递的存储过程
CREATE OR REPLACE PROCEDURE sp_trigger_webhooks(
    IN p_event_type TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_subscription RECORD;
    v_delivery_id UUID;
BEGIN
    FOR v_subscription IN
        SELECT * FROM webhook_subscriptions
        WHERE is_active = true
          AND p_event_type = ANY(event_types)
    LOOP
        -- 创建投递任务
        INSERT INTO webhook_delivery_queue (
            subscription_id, event_type, payload, next_retry_at
        ) VALUES (
            v_subscription.subscription_id,
            p_event_type,
            p_payload,
            NOW()
        )
        RETURNING delivery_id INTO v_delivery_id;

        -- 通知投递服务
        PERFORM pg_notify('webhook_delivery', jsonb_build_object(
            'delivery_id', v_delivery_id,
            'subscription_id', v_subscription.subscription_id
        )::TEXT);
    END LOOP;
END;
$$;

-- 4. 订单创建后触发Webhook
CREATE OR REPLACE PROCEDURE sp_create_order_with_webhooks(
    IN p_user_id BIGINT,
    IN p_items JSONB,
    OUT p_order_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_payload JSONB;
BEGIN
    p_order_id := uuidv7();

    -- 创建订单
    INSERT INTO orders (id, user_id, items, status, created_at)
    VALUES (p_order_id, p_user_id, p_items, 'pending', NOW());

    -- 构建Webhook负载
    v_payload := jsonb_build_object(
        'event', 'order.created',
        'order_id', p_order_id,
        'user_id', p_user_id,
        'items', p_items,
        'timestamp', NOW()
    );

    -- 触发Webhook
    CALL sp_trigger_webhooks('order.created', v_payload);

END;
$$;

-- 5. 重试失败的Webhook
CREATE OR REPLACE PROCEDURE sp_retry_failed_webhooks()
LANGUAGE plpgsql
AS $$
DECLARE
    v_delivery RECORD;
    v_backoff_seconds INT;
BEGIN
    FOR v_delivery IN
        SELECT
            dq.*,
            ws.retry_config->>'max_retries' as max_retries,
            ws.retry_config->>'backoff_base' as backoff_base
        FROM webhook_delivery_queue dq
        JOIN webhook_subscriptions ws ON dq.subscription_id = ws.subscription_id
        WHERE dq.status = 'failed'
          AND dq.attempts < (ws.retry_config->>'max_retries')::INT
          AND dq.next_retry_at <= NOW()
    LOOP
        v_backoff_seconds := power(
            (v_delivery.retry_config->>'backoff_base')::INT,
            v_delivery.attempts
        )::INT;

        -- 更新重试时间
        UPDATE webhook_delivery_queue
        SET
            next_retry_at = NOW() + (v_backoff_seconds || ' seconds')::INTERVAL,
            attempts = attempts + 1
        WHERE delivery_id = v_delivery.delivery_id;

        -- 通知投递服务重试
        PERFORM pg_notify('webhook_delivery', jsonb_build_object(
            'delivery_id', v_delivery.delivery_id,
            'is_retry', true
        )::TEXT);
    END LOOP;
END;
$$;
```

### 4.2 签名验证

```sql
-- ============================================
-- Webhook HMAC签名
-- ============================================

-- 1. HMAC签名函数
CREATE OR REPLACE FUNCTION fn_sign_webhook_payload(
    p_payload JSONB,
    p_secret TEXT,
    p_timestamp TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_signature TEXT;
    v_data TEXT;
BEGIN
    -- 构建签名数据: timestamp.payload
    v_data := EXTRACT(EPOCH FROM p_timestamp)::TEXT || '.' || p_payload::TEXT;

    -- 计算HMAC-SHA256
    v_signature := encode(
        hmac(v_data::bytea, p_secret::bytea, 'sha256'),
        'hex'
    );

    RETURN 'v1=' || v_signature;
END;
$$;

-- 2. 验证签名
CREATE OR REPLACE FUNCTION fn_verify_webhook_signature(
    p_payload JSONB,
    p_signature TEXT,
    p_secret TEXT,
    p_timestamp TIMESTAMPTZ
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_expected TEXT;
BEGIN
    v_expected := fn_sign_webhook_payload(p_payload, p_secret, p_timestamp);

    -- 时间戳校验（5分钟有效期）
    IF p_timestamp < NOW() - INTERVAL '5 minutes' THEN
        RETURN false;
    END IF;

    -- 签名比对
    RETURN v_expected = p_signature;
END;
$$;

-- 3. 构建带签名的Webhook请求体
CREATE OR REPLACE FUNCTION fn_build_webhook_request(
    p_delivery_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_delivery RECORD;
    v_subscription RECORD;
    v_timestamp TIMESTAMPTZ;
    v_signature TEXT;
BEGIN
    SELECT * INTO v_delivery FROM webhook_delivery_queue WHERE delivery_id = p_delivery_id;
    SELECT * INTO v_subscription FROM webhook_subscriptions WHERE subscription_id = v_delivery.subscription_id;

    v_timestamp := NOW();
    v_signature := fn_sign_webhook_payload(v_delivery.payload, v_subscription.webhook_secret, v_timestamp);

    RETURN jsonb_build_object(
        'url', v_subscription.webhook_url,
        'headers', jsonb_build_object(
            'X-Webhook-Signature', v_signature,
            'X-Webhook-Timestamp', EXTRACT(EPOCH FROM v_timestamp)::TEXT,
            'X-Webhook-ID', p_delivery_id::TEXT,
            'Content-Type', 'application/json'
        ),
        'body', v_delivery.payload
    );
END;
$$;
```

---

## 5. 消息队列集成

### 5.1 RabbitMQ集成

```sql
-- ============================================
-- PostgreSQL ──► RabbitMQ 集成
-- ============================================

-- 1. 使用pg_amqp扩展（或外部桥接）
-- CREATE EXTENSION pg_amqp;  -- 如果可用

-- 2. RabbitMQ消息队列表
CREATE TABLE rabbitmq_message_queue (
    message_id UUID PRIMARY KEY DEFAULT uuidv7(),
    exchange TEXT DEFAULT '',
    routing_key TEXT NOT NULL,
    payload JSONB NOT NULL,
    headers JSONB,
    priority INT DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    attempts INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ
);

-- 3. 存储过程：发布消息到RabbitMQ
CREATE OR REPLACE PROCEDURE sp_publish_to_rabbitmq(
    IN p_routing_key TEXT,
    IN p_payload JSONB,
    IN p_exchange TEXT DEFAULT '',
    IN p_headers JSONB DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_message_id UUID;
BEGIN
    INSERT INTO rabbitmq_message_queue (
        exchange, routing_key, payload, headers
    ) VALUES (
        p_exchange, p_routing_key, p_payload, p_headers
    )
    RETURNING message_id INTO v_message_id;

    -- 通知RabbitMQ桥接服务
    PERFORM pg_notify('rabbitmq_publish', jsonb_build_object(
        'message_id', v_message_id
    )::TEXT);
END;
$$;

-- 4. 业务场景：订单创建后发送消息
CREATE OR REPLACE PROCEDURE sp_create_order_with_mq(
    IN p_user_id BIGINT,
    IN p_items JSONB,
    OUT p_order_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_order_total DECIMAL;
BEGIN
    p_order_id := uuidv7();

    -- 计算总价
    SELECT COALESCE(SUM((elem->>'price')::DECIMAL * (elem->>'qty')::INT), 0)
    INTO v_order_total
    FROM jsonb_array_elements(p_items) AS elem;

    -- 创建订单
    INSERT INTO orders (id, user_id, items, total, status)
    VALUES (p_order_id, p_user_id, p_items, v_order_total, 'pending');

    -- 发送库存检查消息
    CALL sp_publish_to_rabbitmq(
        'inventory.check',
        jsonb_build_object(
            'order_id', p_order_id,
            'items', p_items
        ),
        'orders.exchange'
    );

    -- 发送邮件通知消息
    CALL sp_publish_to_rabbitmq(
        'email.order_confirmation',
        jsonb_build_object(
            'order_id', p_order_id,
            'user_id', p_user_id,
            'total', v_order_total
        ),
        'notifications.exchange'
    );

    -- 发送分析事件
    CALL sp_publish_to_rabbitmq(
        'analytics.order_created',
        jsonb_build_object(
            'order_id', p_order_id,
            'user_id', p_user_id,
            'item_count', jsonb_array_length(p_items),
            'total', v_order_total
        ),
        'analytics.exchange'
    );
END;
$$;

-- 5. 消息路由配置
CREATE TABLE mq_routing_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuidv7(),
    event_type TEXT NOT NULL,
    exchange TEXT NOT NULL,
    routing_key TEXT NOT NULL,
    priority INT DEFAULT 5,
    transform_function TEXT,  -- 可选的转换函数
    is_active BOOLEAN DEFAULT true
);

-- 自动路由存储过程
CREATE OR REPLACE PROCEDURE sp_mq_auto_route(
    IN p_event_type TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rule RECORD;
    v_transformed_payload JSONB;
BEGIN
    FOR v_rule IN
        SELECT * FROM mq_routing_rules
        WHERE event_type = p_event_type AND is_active = true
    LOOP
        -- 应用转换
        IF v_rule.transform_function IS NOT NULL THEN
            EXECUTE format('SELECT %s($1)', v_rule.transform_function)
            INTO v_transformed_payload
            USING p_payload;
        ELSE
            v_transformed_payload := p_payload;
        END IF;

        -- 发布消息
        CALL sp_publish_to_rabbitmq(
            v_rule.routing_key,
            v_transformed_payload,
            v_rule.exchange
        );
    END LOOP;
END;
$$;
```

### 5.2 Kafka集成

```sql
-- ============================================
-- PostgreSQL ──► Kafka 集成 (CDC/事件流)
-- ============================================

-- 1. Kafka消息队列表
CREATE TABLE kafka_message_queue (
    message_id UUID PRIMARY KEY DEFAULT uuidv7(),
    topic TEXT NOT NULL,
    key TEXT,
    payload JSONB NOT NULL,
    partition INT,
    status VARCHAR(20) DEFAULT 'pending',
    attempts INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ,
    kafka_offset BIGINT
);

-- 2. 分区键计算（确保顺序）
CREATE OR REPLACE FUNCTION fn_kafka_partition_key(
    p_key_value TEXT,
    p_num_partitions INT DEFAULT 12
)
RETURNS INT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN (hashtext(p_key_value) & 0x7FFFFFFF) % p_num_partitions;
END;
$$;

-- 3. 存储过程：发布到Kafka
CREATE OR REPLACE PROCEDURE sp_publish_to_kafka(
    IN p_topic TEXT,
    IN p_payload JSONB,
    IN p_key TEXT DEFAULT NULL,
    IN p_partition INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_message_id UUID;
    v_partition INT;
BEGIN
    -- 计算分区
    IF p_partition IS NULL AND p_key IS NOT NULL THEN
        v_partition := fn_kafka_partition_key(p_key);
    ELSE
        v_partition := COALESCE(p_partition, 0);
    END IF;

    INSERT INTO kafka_message_queue (topic, key, payload, partition)
    VALUES (p_topic, p_key, p_payload, v_partition)
    RETURNING message_id INTO v_message_id;

    PERFORM pg_notify('kafka_publish', jsonb_build_object(
        'message_id', v_message_id,
        'topic', p_topic
    )::TEXT);
END;
$$;

-- 4. 事件流存储过程
CREATE OR REPLACE PROCEDURE sp_emit_domain_event(
    IN p_aggregate_type TEXT,
    IN p_aggregate_id TEXT,
    IN p_event_type TEXT,
    IN p_event_data JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event JSONB;
    v_topic TEXT;
BEGIN
    v_event := jsonb_build_object(
        'event_id', uuidv7(),
        'event_type', p_event_type,
        'aggregate_type', p_aggregate_type,
        'aggregate_id', p_aggregate_id,
        'data', p_event_data,
        'metadata', jsonb_build_object(
            'timestamp', NOW(),
            'version', 1
        )
    );

    -- 根据聚合类型路由到不同topic
    v_topic := 'domain.events.' || p_aggregate_type;

    CALL sp_publish_to_kafka(v_topic, v_event, p_aggregate_id);
END;
$$;

-- 5. 使用示例
CREATE OR REPLACE PROCEDURE sp_order_event_stream(
    IN p_order_id UUID,
    IN p_event_type TEXT,
    IN p_event_data JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_emit_domain_event('order', p_order_id::TEXT, p_event_type, p_event_data);
END;
$$;
```

### 5.3 Redis Pub/Sub

```sql
-- ============================================
-- PostgreSQL ──► Redis Pub/Sub 集成
-- ============================================

-- 1. Redis发布队列表
CREATE TABLE redis_pubsub_queue (
    message_id UUID PRIMARY KEY DEFAULT uuidv7(),
    channel TEXT NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sent_at TIMESTAMPTZ
);

-- 2. 缓存失效通知
CREATE OR REPLACE PROCEDURE sp_cache_invalidate(
    IN p_cache_key TEXT,
    IN p_invalidation_scope TEXT DEFAULT 'single'  -- single, pattern, all
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_channel TEXT;
BEGIN
    v_channel := CASE p_invalidation_scope
        WHEN 'single' THEN 'cache:invalidate'
        WHEN 'pattern' THEN 'cache:invalidate:pattern'
        ELSE 'cache:invalidate:all'
    END;

    INSERT INTO redis_pubsub_queue (channel, message)
    VALUES (v_channel, p_cache_key);

    PERFORM pg_notify('redis_publish', jsonb_build_object(
        'cache_key', p_cache_key,
        'scope', p_invalidation_scope
    )::TEXT);
END;
$$;

-- 3. 实时计数器更新
CREATE OR REPLACE PROCEDURE sp_realtime_counter_update(
    IN p_counter_name TEXT,
    IN p_increment INT DEFAULT 1
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO redis_pubsub_queue (channel, message)
    VALUES ('counter:update', jsonb_build_object(
        'name', p_counter_name,
        'increment', p_increment
    )::TEXT);
END;
$$;
```

---

## 6. 变更数据捕获(CDC)

### 6.1 Debezium集成

```sql
-- ============================================
-- Debezium CDC 配置
-- ============================================

-- 1. 启用逻辑复制
-- postgresql.conf:
-- wal_level = logical
-- max_replication_slots = 10
-- max_wal_senders = 10

-- 2. 创建CDC用户
CREATE USER debezium_user WITH REPLICATION LOGIN PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium_user;

-- 3. 创建复制槽
SELECT * FROM pg_create_logical_replication_slot('debezium_slot', 'pgoutput');

-- 4. CDC配置表
CREATE TABLE cdc_config (
    table_name TEXT PRIMARY KEY,
    capture_enabled BOOLEAN DEFAULT true,
    capture_columns TEXT[],  -- NULL表示所有列
    exclude_columns TEXT[],
    topic_name TEXT,  -- Kafka topic
    partition_key_column TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 敏感数据屏蔽
CREATE OR REPLACE FUNCTION fn_cdc_mask_sensitive(p_column TEXT, p_value TEXT)
RETURNS TEXT
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN CASE p_column
        WHEN 'password' THEN '***MASKED***'
        WHEN 'credit_card' THEN '****-****-****-' || RIGHT(p_value, 4)
        WHEN 'ssn' THEN '***-**-' || RIGHT(p_value, 4)
        ELSE p_value
    END;
END;
$$;

-- 6. CDC监控
CREATE VIEW v_cdc_lag AS
SELECT
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) as lag_size
FROM pg_replication_slots
WHERE slot_name LIKE 'debezium%';
```

### 6.2 逻辑解码槽

```sql
-- ============================================
-- 自定义逻辑解码
-- ============================================

-- 1. 创建测试解码插件（概念演示）
-- 实际使用 decoderbufs, wal2json, pgoutput 等

-- 2. 逻辑解码消息存储
CREATE TABLE logical_decoded_messages (
    message_id UUID PRIMARY KEY DEFAULT uuidv7(),
    lsn PG_LSN NOT NULL,
    xid BIGINT,
    table_name TEXT,
    operation TEXT,  -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    decoded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 自定义变更处理函数
CREATE OR REPLACE FUNCTION fn_process_cdc_change(
    p_lsn PG_LSN,
    p_xid BIGINT,
    p_table TEXT,
    p_op TEXT,
    p_old JSONB,
    p_new JSONB
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- 存储变更
    INSERT INTO logical_decoded_messages (
        lsn, xid, table_name, operation, old_data, new_data
    ) VALUES (p_lsn, p_xid, p_table, p_op, p_old, p_new);

    -- 根据表类型路由处理
    CASE p_table
        WHEN 'orders' THEN
            -- 订单变更通知物流系统
            PERFORM pg_notify('order_changes', jsonb_build_object(
                'operation', p_op,
                'data', p_new
            )::TEXT);

        WHEN 'inventory' THEN
            -- 库存变更触发补货检查
            PERFORM pg_notify('inventory_changes', jsonb_build_object(
                'operation', p_op,
                'data', p_new
            )::TEXT);

        ELSE
            -- 默认处理
            NULL;
    END CASE;
END;
$$;
```

---

## 7. 事件溯源模式

### 7.1 事件存储设计

```sql
-- ============================================
-- 事件溯源存储设计
-- ============================================

-- 1. 事件存储表
CREATE TABLE event_store (
    event_id UUID PRIMARY KEY DEFAULT uuidv7(),
    aggregate_type TEXT NOT NULL,
    aggregate_id TEXT NOT NULL,
    version INT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::JSONB,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    recorded_at TIMESTAMPTZ DEFAULT clock_timestamp(),

    UNIQUE(aggregate_type, aggregate_id, version)
);

-- 2. 事件投影表（物化视图）
CREATE TABLE projections (
    projection_id UUID PRIMARY KEY DEFAULT uuidv7(),
    projection_name TEXT UNIQUE NOT NULL,
    aggregate_type TEXT NOT NULL,
    last_processed_event_id UUID,
    last_processed_at TIMESTAMPTZ,
    state JSONB,
    is_rebuilding BOOLEAN DEFAULT false
);

-- 3. 存储过程：追加事件
CREATE OR REPLACE FUNCTION fn_append_event(
    p_aggregate_type TEXT,
    p_aggregate_id TEXT,
    p_event_type TEXT,
    p_payload JSONB,
    p_metadata JSONB DEFAULT '{}'::JSONB
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_next_version INT;
    v_event_id UUID;
BEGIN
    -- 获取下一个版本号
    SELECT COALESCE(MAX(version), 0) + 1 INTO v_next_version
    FROM event_store
    WHERE aggregate_type = p_aggregate_type AND aggregate_id = p_aggregate_id;

    -- 插入事件
    INSERT INTO event_store (
        aggregate_type, aggregate_id, version, event_type, payload, metadata
    ) VALUES (
        p_aggregate_type, p_aggregate_id, v_next_version, p_event_type, p_payload, p_metadata
    )
    RETURNING event_id INTO v_event_id;

    -- 发布事件
    PERFORM pg_notify('domain_events', jsonb_build_object(
        'event_id', v_event_id,
        'aggregate_type', p_aggregate_type,
        'aggregate_id', p_aggregate_id,
        'event_type', p_event_type,
        'version', v_next_version
    )::TEXT);

    RETURN v_event_id;
END;
$$;

-- 4. 存储过程：重建聚合
CREATE OR REPLACE FUNCTION fn_rebuild_aggregate(
    p_aggregate_type TEXT,
    p_aggregate_id TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_event RECORD;
    v_state JSONB := '{}'::JSONB;
BEGIN
    FOR v_event IN
        SELECT * FROM event_store
        WHERE aggregate_type = p_aggregate_type AND aggregate_id = p_aggregate_id
        ORDER BY version
    LOOP
        -- 应用事件（简化示例，实际使用策略模式）
        v_state := v_state || jsonb_build_object(
            'version', v_event.version,
            'last_event', v_event.event_type,
            'last_event_at', v_event.occurred_at
        ) || v_event.payload;
    END LOOP;

    RETURN v_state;
END;
$$;

-- 5. 订单聚合事件溯源示例
CREATE OR REPLACE PROCEDURE sp_create_order_es(
    IN p_user_id BIGINT,
    IN p_items JSONB,
    OUT p_aggregate_id TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event_id UUID;
BEGIN
    p_aggregate_id := gen_random_uuid()::TEXT;

    -- OrderCreated事件
    v_event_id := fn_append_event(
        'order',
        p_aggregate_id,
        'OrderCreated',
        jsonb_build_object(
            'user_id', p_user_id,
            'items', p_items,
            'status', 'pending'
        )
    );

    -- 可以追加更多事件
    -- fn_append_event('order', p_aggregate_id, 'OrderPaymentInitiated', {...});
END;
$$;

CREATE OR REPLACE PROCEDURE sp_confirm_order_payment_es(
    IN p_order_id TEXT,
    IN p_payment_reference TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event_id UUID;
BEGIN
    v_event_id := fn_append_event(
        'order',
        p_order_id,
        'OrderPaymentConfirmed',
        jsonb_build_object(
            'payment_reference', p_payment_reference,
            'confirmed_at', NOW()
        )
    );
END;
$$;
```

### 7.2 存储过程发布事件

```sql
-- ============================================
-- 投影处理器
-- ============================================

-- 1. 订单投影表
CREATE TABLE order_projections (
    order_id TEXT PRIMARY KEY,
    user_id BIGINT,
    status TEXT,
    total_amount DECIMAL,
    item_count INT,
    current_version INT,
    last_updated_at TIMESTAMPTZ
);

-- 2. 投影更新存储过程
CREATE OR REPLACE PROCEDURE sp_update_order_projection(
    IN p_event_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event RECORD;
    v_projection RECORD;
BEGIN
    SELECT * INTO v_event FROM event_store WHERE event_id = p_event_id;

    IF v_event.aggregate_type != 'order' THEN
        RETURN;
    END IF;

    -- 获取或创建投影
    SELECT * INTO v_projection
    FROM order_projections
    WHERE order_id = v_event.aggregate_id;

    IF NOT FOUND THEN
        INSERT INTO order_projections (order_id, current_version)
        VALUES (v_event.aggregate_id, 0)
        RETURNING * INTO v_projection;
    END IF;

    -- 乐观并发控制
    IF v_event.version != v_projection.current_version + 1 THEN
        RAISE EXCEPTION 'Concurrency conflict: expected version %, got %',
            v_projection.current_version + 1, v_event.version;
    END IF;

    -- 根据事件类型更新投影
    CASE v_event.event_type
        WHEN 'OrderCreated' THEN
            UPDATE order_projections
            SET
                user_id = (v_event.payload->>'user_id')::BIGINT,
                status = 'pending',
                item_count = jsonb_array_length(v_event.payload->'items'),
                current_version = v_event.version,
                last_updated_at = v_event.occurred_at
            WHERE order_id = v_event.aggregate_id;

        WHEN 'OrderPaymentConfirmed' THEN
            UPDATE order_projections
            SET
                status = 'paid',
                current_version = v_event.version,
                last_updated_at = v_event.occurred_at
            WHERE order_id = v_event.aggregate_id;

        WHEN 'OrderShipped' THEN
            UPDATE order_projections
            SET
                status = 'shipped',
                current_version = v_event.version,
                last_updated_at = v_event.occurred_at
            WHERE order_id = v_event.aggregate_id;
    END CASE;
END;
$$;

-- 3. 事件监听触发投影更新
CREATE OR REPLACE FUNCTION fn_event_store_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- 异步触发投影更新
    PERFORM pg_notify('projection_update', jsonb_build_object(
        'event_id', NEW.event_id,
        'aggregate_type', NEW.aggregate_type
    )::TEXT);

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_event_store_insert
    AFTER INSERT ON event_store
    FOR EACH ROW
    EXECUTE FUNCTION fn_event_store_trigger();
```

---

## 8. 可靠投递保证

### 8.1 至少一次投递

```sql
-- ============================================
-- 至少一次投递保证
-- ============================================

-- 1. 投递确认表
CREATE TABLE delivery_confirmations (
    delivery_id UUID PRIMARY KEY,
    subscriber_id TEXT NOT NULL,
    event_id UUID NOT NULL,
    delivered_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    confirmation_token TEXT
);

-- 2. 带确认的存储过程
CREATE OR REPLACE PROCEDURE sp_notify_with_confirmation(
    IN p_subscriber_id TEXT,
    IN p_channel TEXT,
    IN p_payload JSONB,
    OUT p_delivery_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_event_id UUID;
BEGIN
    p_delivery_id := uuidv7();
    v_event_id := uuidv7();

    -- 发送通知
    PERFORM pg_notify(p_channel, jsonb_build_object(
        'event_id', v_event_id,
        'delivery_id', p_delivery_id,
        'payload', p_payload,
        'timestamp', NOW()
    )::TEXT);

    -- 记录待确认
    INSERT INTO delivery_confirmations (
        delivery_id, subscriber_id, event_id, confirmation_token
    ) VALUES (
        p_delivery_id, p_subscriber_id, v_event_id, encode(gen_random_bytes(16), 'hex')
    );
END;
$$;

-- 3. 确认接收
CREATE OR REPLACE PROCEDURE sp_confirm_delivery(
    IN p_delivery_id UUID,
    IN p_confirmation_token TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE delivery_confirmations
    SET confirmed_at = NOW()
    WHERE delivery_id = p_delivery_id
      AND confirmation_token = p_confirmation_token;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Invalid delivery confirmation';
    END IF;
END;
$$;

-- 4. 重试未确认的消息
CREATE OR REPLACE PROCEDURE sp_retry_unconfirmed()
LANGUAGE plpgsql
AS $$
DECLARE
    v_delivery RECORD;
BEGIN
    FOR v_delivery IN
        SELECT * FROM delivery_confirmations
        WHERE confirmed_at IS NULL
          AND delivered_at < NOW() - INTERVAL '30 seconds'
    LOOP
        -- 重新发送
        PERFORM pg_notify('retry_delivery', jsonb_build_object(
            'delivery_id', v_delivery.delivery_id
        )::TEXT);
    END LOOP;
END;
$$;
```

### 8.2 恰好一次投递

```sql
-- ============================================
-- 恰好一次投递（幂等性保证）
-- ============================================

-- 1. 幂等键表
CREATE TABLE idempotent_consumers (
    consumer_id TEXT NOT NULL,
    event_id UUID NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    result JSONB,
    PRIMARY KEY (consumer_id, event_id)
);

-- 2. 幂等消费存储过程
CREATE OR REPLACE FUNCTION fn_idempotent_consume(
    p_consumer_id TEXT,
    p_event_id UUID,
    p_event_data JSONB,
    p_processing_function TEXT  -- 处理函数名
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_existing RECORD;
    v_result JSONB;
BEGIN
    -- 检查是否已处理
    SELECT * INTO v_existing
    FROM idempotent_consumers
    WHERE consumer_id = p_consumer_id AND event_id = p_event_id;

    IF FOUND THEN
        -- 已处理，返回缓存结果
        RETURN v_existing.result;
    END IF;

    -- 执行处理
    EXECUTE format('SELECT %s($1)', p_processing_function)
    INTO v_result
    USING p_event_data;

    -- 记录处理结果
    INSERT INTO idempotent_consumers (
        consumer_id, event_id, result
    ) VALUES (p_consumer_id, p_event_id, v_result);

    RETURN v_result;
EXCEPTION
    WHEN unique_violation THEN
        -- 并发冲突，重新查询结果
        SELECT result INTO v_result
        FROM idempotent_consumers
        WHERE consumer_id = p_consumer_id AND event_id = p_event_id;
        RETURN v_result;
END;
$$;

-- 3. 清理过期幂等记录
CREATE OR REPLACE PROCEDURE sp_cleanup_idempotent_keys(
    IN p_retention_days INT DEFAULT 7
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM idempotent_consumers
    WHERE processed_at < NOW() - (p_retention_days || ' days')::INTERVAL;
END;
$$;
```

---

## 9. 安全与认证

```sql
-- ============================================
-- 通知安全机制
-- ============================================

-- 1. 频道权限表
CREATE TABLE notification_permissions (
    channel_pattern TEXT PRIMARY KEY,
    allowed_roles TEXT[],
    require_auth BOOLEAN DEFAULT true,
    encryption_required BOOLEAN DEFAULT false
);

-- 2. 频道访问验证
CREATE OR REPLACE FUNCTION fn_check_channel_access(
    p_user_id BIGINT,
    p_channel TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_roles TEXT[];
    v_permission RECORD;
BEGIN
    -- 获取用户角色
    SELECT array_agg(role_name) INTO v_user_roles
    FROM user_roles
    WHERE user_id = p_user_id;

    -- 检查频道权限
    SELECT * INTO v_permission
    FROM notification_permissions
    WHERE p_channel LIKE channel_pattern
    ORDER BY LENGTH(channel_pattern) DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RETURN false;
    END IF;

    -- 检查角色权限
    RETURN v_permission.allowed_roles && v_user_roles;
END;
$$;

-- 3. 安全存储过程
CREATE OR REPLACE PROCEDURE sp_secure_notify(
    IN p_user_id BIGINT,
    IN p_channel TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 验证权限
    IF NOT fn_check_channel_access(p_user_id, p_channel) THEN
        RAISE EXCEPTION 'Access denied to channel: %', p_channel;
    END IF;

    -- 添加安全元数据
    p_payload := p_payload || jsonb_build_object(
        '_security', jsonb_build_object(
            'sender_id', p_user_id,
            'sent_at', NOW()
        )
    );

    PERFORM pg_notify(p_channel, p_payload::TEXT);
END;
$$;
```

---

## 10. 性能优化

```sql
-- ============================================
-- 通知性能优化
-- ============================================

-- 1. 批量通知聚合
CREATE TABLE notification_batch_queue (
    batch_id UUID PRIMARY KEY DEFAULT uuidv7(),
    channel TEXT NOT NULL,
    payloads JSONB[] DEFAULT ARRAY[]::JSONB[],
    batch_size INT DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    flushed_at TIMESTAMPTZ
);

-- 2. 批量发送存储过程
CREATE OR REPLACE PROCEDURE sp_batch_notify_enqueue(
    IN p_channel TEXT,
    IN p_payload JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_batch_id UUID;
BEGIN
    -- 查找或创建批次
    SELECT batch_id INTO v_batch_id
    FROM notification_batch_queue
    WHERE channel = p_channel AND flushed_at IS NULL
    ORDER BY created_at
    LIMIT 1;

    IF v_batch_id IS NULL THEN
        INSERT INTO notification_batch_queue (channel)
        VALUES (p_channel)
        RETURNING batch_id INTO v_batch_id;
    END IF;

    -- 添加负载到批次
    UPDATE notification_batch_queue
    SET payloads = payloads || p_payload
    WHERE batch_id = v_batch_id;

    -- 检查是否满批
    IF (SELECT array_length(payloads, 1) FROM notification_batch_queue WHERE batch_id = v_batch_id)
       >= (SELECT batch_size FROM notification_batch_queue WHERE batch_id = v_batch_id) THEN
        PERFORM pg_notify('batch_flush', jsonb_build_object('batch_id', v_batch_id)::TEXT);
    END IF;
END;
$$;

-- 3. 通知速率限制
CREATE TABLE notification_rate_limits (
    channel TEXT PRIMARY KEY,
    max_messages_per_second INT DEFAULT 100,
    window_size_seconds INT DEFAULT 1
);

CREATE OR REPLACE FUNCTION fn_check_rate_limit(p_channel TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_limit RECORD;
    v_count INT;
BEGIN
    SELECT * INTO v_limit FROM notification_rate_limits WHERE channel = p_channel;

    IF NOT FOUND THEN
        RETURN true;
    END IF;

    -- 检查窗口内消息数
    SELECT COUNT(*) INTO v_count
    FROM pg_notification_queue  -- 假设的队列视图
    WHERE channel = p_channel
      AND created_at > NOW() - (v_limit.window_size_seconds || ' seconds')::INTERVAL;

    RETURN v_count < v_limit.max_messages_per_second;
END;
$$;
```

---

## 11. 持续推进计划

### 短期目标 (1-2周)

- [ ] 实施LISTEN/NOTIFY核心通知机制
- [ ] 部署WebSocket桥接服务
- [ ] 配置Webhook投递系统

### 中期目标 (1个月)

- [ ] 集成消息队列(RabbitMQ/Kafka)
- [ ] 部署Debezium CDC
- [ ] 实施事件溯源模式

### 长期目标 (3个月)

- [ ] 完整的事件驱动架构
- [ ] 多数据中心事件同步
- [ ] 智能事件路由与过滤

---

**文档信息**:

- 字数: 10000+
- 通知模式: 15+
- 代码示例: 45+
- 状态: ✅ 深度分析完成

---

*构建实时响应的事件驱动架构！* ⚡
