---

> **📋 文档来源**: `PostgreSQL培训\09-高可用\【深入】PostgreSQL逻辑复制高级特性与冲突解决.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 【深入】PostgreSQL逻辑复制高级特性与冲突解决

> **创建时间**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家级
> **预计学习时间**: 1-2周

---

## 📑 目录

- [1.1 逻辑复制 vs 物理复制](#11-逻辑复制-vs-物理复制)
- [1.2 逻辑复制架构](#12-逻辑复制架构)
- [1.3 快速开始（15分钟）](#13-快速开始15分钟)
- [2.1 行过滤（Row Filter）](#21-行过滤row-filter)
- [2.2 列过滤（Column Filter）](#22-列过滤column-filter)
- [2.3 多个发布和订阅](#23-多个发布和订阅)
- [2.4 级联复制](#24-级联复制)
- [3.1 常见冲突类型](#31-常见冲突类型)
- [3.2 冲突检测](#32-冲突检测)
- [3.3 冲突解决策略](#33-冲突解决策略)
- [4.1 双向复制配置](#41-双向复制配置)
- [5.1 监控复制延迟](#51-监控复制延迟)
- [5.2 监控WAL占用](#52-监控wal占用)
- [5.3 复制性能监控](#53-复制性能监控)
- [6.1 批量应用优化](#61-批量应用优化)
- [6.2 大事务处理](#62-大事务处理)
- [6.3 初始数据同步优化](#63-初始数据同步优化)
- [7.1 案例：跨版本升级（PG 16 → PG 17）](#71-案例跨版本升级pg-16--pg-17)
- [7.2 案例：数据汇总（多源到一个数据仓库）](#72-案例数据汇总多源到一个数据仓库)
- [7.3 案例：读写分离（逻辑复制）](#73-案例读写分离逻辑复制)
- [8.1 选择性复制（部分行、部分列）](#81-选择性复制部分行部分列)
- [8.2 数据转换（Transform）](#82-数据转换transform)
- [官方文档](#官方文档)
- [扩展和工具](#扩展和工具)
- [最佳实践](#最佳实践)
---

## 1. 逻辑复制进阶

### 1.1 逻辑复制 vs 物理复制

| 特性 | 物理复制 | 逻辑复制 |
|------|---------|---------|
| **复制粒度** | 整个集群 | 表级别 |
| **跨版本** | ❌ 不支持 | ✅ 支持 |
| **选择性复制** | ❌ 全部复制 | ✅ 部分表 |
| **双向复制** | ❌ 单向 | ✅ 可以（需配置）|
| **DDL复制** | ✅ 自动 | ❌ 需手动 |
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **延迟** | 极低（<1ms） | 低（<100ms）|
| **适用场景** | 完整备份、只读副本 | 部分同步、跨版本升级、数据集成 |

### 1.2 逻辑复制架构

```text
┌──────────────────┐         ┌──────────────────┐
│  Publisher DB    │         │  Subscriber DB   │
│                  │         │                  │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Publication│  │         │  │Subscription│  │
│  │  (Table A) │  │         │  │  (Table A) │  │
│  │  (Table B) │  │         │  │  (Table B) │  │
│  └─────┬──────┘  │         │  └─────▲──────┘  │
│        │         │         │        │         │
│        ▼         │         │        │         │
│  ┌────────────┐  │  Logical│  ┌────────────┐  │
│  │ WAL Sender │──┼─ Repl. ─┼─>│ WAL Receiver│ │
│  └────────────┘  │  Stream │  └────────────┘  │
│        ▲         │         │        │         │
│        │         │         │        ▼         │
│  ┌────────────┐  │         │  ┌────────────┐  │
│  │ Logical    │  │         │  │ Apply      │  │
│  │ Decoding   │  │         │  │ Worker     │  │
│  └────────────┘  │         │  └────────────┘  │
└──────────────────┘         └──────────────────┘
```

### 1.3 快速开始（15分钟）

**发布端配置**：

```sql
-- 1. 配置postgresql.conf
wal_level = logical
max_wal_senders = 10
max_replication_slots = 10

-- 重启PostgreSQL
-- sudo systemctl restart postgresql

-- 2. 创建复制用户（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'replicator'
    ) THEN
        RAISE WARNING '用户replicator已存在';
        RETURN;
    END IF;

    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'rep_password';
    RAISE NOTICE '复制用户replicator创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '用户replicator已存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，需要超级用户权限';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建复制用户失败: %', SQLERRM;
END $$;

-- 3. 配置pg_hba.conf
-- host replication replicator 0.0.0.0/0 scram-sha-256

-- 4. 创建测试表（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        user_id serial PRIMARY KEY,
        username text UNIQUE NOT NULL,
        email text,
        created_at timestamptz DEFAULT now()
    );
    RAISE NOTICE '表users创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表users已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建测试表失败: %', SQLERRM;
END $$;

-- 插入测试数据（带错误处理）
DO $$
DECLARE
    inserted_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    INSERT INTO users (username, email)
    SELECT 'user_' || i, 'user' || i || '@example.com'
    FROM generate_series(1, 10000) i;

    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RAISE NOTICE '成功插入 % 条测试数据', inserted_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在';
    WHEN unique_violation THEN
        RAISE WARNING '插入数据时发生唯一性冲突';
    WHEN OTHERS THEN
        RAISE EXCEPTION '插入测试数据失败: %', SQLERRM;
END $$;

-- 5. 创建发布（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub'
    ) THEN
        DROP PUBLICATION my_pub;
        RAISE NOTICE '已删除现有发布: my_pub';
    END IF;

    CREATE PUBLICATION my_pub FOR TABLE users;
    RAISE NOTICE '发布my_pub创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布my_pub已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在，无法创建发布';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，需要超级用户权限';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- 或发布所有表（带错误处理）
-- DO $$
-- BEGIN
--     IF EXISTS (
--         SELECT 1 FROM pg_publication WHERE pubname = 'my_pub'
--     ) THEN
--         DROP PUBLICATION my_pub;
--         RAISE NOTICE '已删除现有发布: my_pub';
--     END IF;
--     CREATE PUBLICATION my_pub FOR ALL TABLES;
--     RAISE NOTICE '发布my_pub（所有表）创建成功';
-- EXCEPTION
--     WHEN duplicate_object THEN
--         RAISE WARNING '发布my_pub已存在';
--     WHEN insufficient_privilege THEN
--         RAISE EXCEPTION '权限不足，需要超级用户权限';
--     WHEN OTHERS THEN
--         RAISE EXCEPTION '创建发布失败: %', SQLERRM;
-- END $$;

-- 或发布特定列
-- CREATE PUBLICATION my_pub FOR TABLE users (user_id, username);
```

**订阅端配置**：

```sql
-- 1. 创建相同结构的表（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        user_id serial PRIMARY KEY,
        username text UNIQUE NOT NULL,
        email text,
        created_at timestamptz DEFAULT now()
    );
    RAISE NOTICE '表users创建成功';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表users已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表users失败: %', SQLERRM;
END $$;

-- 2. 创建订阅（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'my_sub'
    ) THEN
        RAISE WARNING '订阅my_sub已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub'
    ) THEN
        RAISE EXCEPTION '发布my_pub不存在，请先在发布端创建';
    END IF;

    CREATE SUBSCRIPTION my_sub
        CONNECTION 'host=publisher_host port=5432 dbname=source_db user=replicator password=rep_password'
        PUBLICATION my_pub;
    RAISE NOTICE '订阅my_sub创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅my_sub已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布my_pub不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到发布端数据库';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;

-- 3. 验证复制状态（带错误处理和性能测试）
DO $$
DECLARE
    subscription_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_stat_subscription'
    ) THEN
        RAISE WARNING 'pg_stat_subscription视图不存在（需要PostgreSQL 10+）';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO subscription_count
    FROM pg_stat_subscription;

    IF subscription_count > 0 THEN
        RAISE NOTICE '发现 % 条订阅统计记录', subscription_count;
    ELSE
        RAISE NOTICE '未发现订阅统计记录';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_subscription视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '验证复制状态失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM pg_stat_subscription;
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 4. 查看数据（带错误处理和性能测试）
DO $$
DECLARE
    user_count BIGINT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE WARNING '表users不存在，跳过数据验证';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO user_count FROM users;
    RAISE NOTICE 'users表记录数: % (应该是10000)', user_count;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表users不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看数据失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM users;
-- 执行时间: <100ms（取决于表大小）
-- 计划: Aggregate
-- 应该是10000

-- 5. 测试实时复制
-- 在发布端插入数据
-- INSERT INTO users (username, email) VALUES ('new_user', 'new@example.com');

-- 在订阅端查询
-- SELECT * FROM users WHERE username = 'new_user';  -- 应该很快出现
```

---

## 2. 发布订阅高级用法

### 2.1 行过滤（Row Filter）

```sql
-- PostgreSQL 15+支持
-- 发布端：只发布活跃用户（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'active_users_pub'
    ) THEN
        RAISE WARNING '发布active_users_pub已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    CREATE PUBLICATION active_users_pub
    FOR TABLE users
    WHERE (is_active = true);
    RAISE NOTICE '发布active_users_pub创建成功（仅发布活跃用户）';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布active_users_pub已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- 订阅端（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'active_users_sub'
    ) THEN
        RAISE WARNING '订阅active_users_sub已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'active_users_pub'
    ) THEN
        RAISE EXCEPTION '发布active_users_pub不存在，请先在发布端创建';
    END IF;

    CREATE SUBSCRIPTION active_users_sub
        CONNECTION '...'
        PUBLICATION active_users_pub;
    RAISE NOTICE '订阅active_users_sub创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅active_users_sub已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布active_users_pub不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到发布端数据库';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;

-- 只有is_active=true的用户会被复制
```

### 2.2 列过滤（Column Filter）

```sql
-- 发布端：只发布部分列（不包含敏感列，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'users_pub'
    ) THEN
        RAISE WARNING '发布users_pub已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    CREATE PUBLICATION users_pub
    FOR TABLE users (user_id, username, created_at);
    RAISE NOTICE '发布users_pub创建成功（不包含email敏感信息）';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布users_pub已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- 订阅端表结构（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        user_id int PRIMARY KEY,
        username text,
        created_at timestamptz
    );
    RAISE NOTICE '表users创建成功（不需要email列）';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表users已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表users失败: %', SQLERRM;
END $$;

-- 创建订阅（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'users_sub'
    ) THEN
        RAISE WARNING '订阅users_sub已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'users_pub'
    ) THEN
        RAISE EXCEPTION '发布users_pub不存在，请先在发布端创建';
    END IF;

    CREATE SUBSCRIPTION users_sub
        CONNECTION '...'
        PUBLICATION users_pub;
    RAISE NOTICE '订阅users_sub创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅users_sub已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布users_pub不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到发布端数据库';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;
```

### 2.3 多个发布和订阅

```sql
-- 发布端：创建多个发布（带错误处理）
DO $$
BEGIN
    -- 创建pub_users发布
    IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_users') THEN
        RAISE WARNING '发布pub_users已存在';
    ELSE
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
            RAISE EXCEPTION '表users不存在';
        END IF;
        CREATE PUBLICATION pub_users FOR TABLE users;
        RAISE NOTICE '发布pub_users创建成功';
    END IF;

    -- 创建pub_orders发布
    IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_orders') THEN
        RAISE WARNING '发布pub_orders已存在';
    ELSE
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'orders') THEN
            RAISE EXCEPTION '表orders不存在';
        END IF;
        CREATE PUBLICATION pub_orders FOR TABLE orders;
        RAISE NOTICE '发布pub_orders创建成功';
    END IF;

    -- 创建pub_products发布
    IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_products') THEN
        RAISE WARNING '发布pub_products已存在';
    ELSE
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'products') THEN
            RAISE EXCEPTION '表products不存在';
        END IF;
        CREATE PUBLICATION pub_products FOR TABLE products;
        RAISE NOTICE '发布pub_products创建成功';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '某些发布已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '相关表不存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- 订阅端：订阅多个发布（带错误处理）
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_subscription WHERE subname = 'sub_all') THEN
        RAISE WARNING '订阅sub_all已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_users') THEN
        RAISE EXCEPTION '发布pub_users不存在';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_orders') THEN
        RAISE EXCEPTION '发布pub_orders不存在';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_products') THEN
        RAISE EXCEPTION '发布pub_products不存在';
    END IF;

    CREATE SUBSCRIPTION sub_all
        CONNECTION '...'
        PUBLICATION pub_users, pub_orders, pub_products;
    RAISE NOTICE '订阅sub_all创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅sub_all已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '相关发布不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到发布端数据库';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;

-- 或者：多个订阅（带错误处理）
DO $$
BEGIN
    -- 创建sub_users订阅
    IF EXISTS (SELECT 1 FROM pg_subscription WHERE subname = 'sub_users') THEN
        RAISE WARNING '订阅sub_users已存在';
    ELSE
        IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_users') THEN
            RAISE EXCEPTION '发布pub_users不存在';
        END IF;
        CREATE SUBSCRIPTION sub_users
            CONNECTION '...'
            PUBLICATION pub_users;
        RAISE NOTICE '订阅sub_users创建成功';
    END IF;

    -- 创建sub_orders订阅
    IF EXISTS (SELECT 1 FROM pg_subscription WHERE subname = 'sub_orders') THEN
        RAISE WARNING '订阅sub_orders已存在';
    ELSE
        IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'pub_orders') THEN
            RAISE EXCEPTION '发布pub_orders不存在';
        END IF;
        CREATE SUBSCRIPTION sub_orders
            CONNECTION '...'
            PUBLICATION pub_orders;
        RAISE NOTICE '订阅sub_orders创建成功';
    END IF;
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '某些订阅已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '相关发布不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到发布端数据库';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;
```

### 2.4 级联复制

```sql
-- 架构：Publisher → Subscriber1 → Subscriber2

-- Publisher：创建发布（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub'
    ) THEN
        RAISE WARNING '发布my_pub已存在';
        RETURN;
    END IF;

    CREATE PUBLICATION my_pub FOR ALL TABLES;
    RAISE NOTICE '发布my_pub创建成功（所有表）';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布my_pub已存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- Subscriber1：订阅并转发（带错误处理）
-- 1. 订阅Publisher
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'sub_from_publisher'
    ) THEN
        RAISE WARNING '订阅sub_from_publisher已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub'
    ) THEN
        RAISE EXCEPTION '发布my_pub不存在，请先在Publisher创建';
    END IF;

    CREATE SUBSCRIPTION sub_from_publisher
        CONNECTION 'host=publisher ...'
        PUBLICATION my_pub;
    RAISE NOTICE '订阅sub_from_publisher创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅sub_from_publisher已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布my_pub不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到Publisher';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;

-- 2. 创建自己的发布（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub_forwarded'
    ) THEN
        RAISE WARNING '发布my_pub_forwarded已存在';
        RETURN;
    END IF;

    CREATE PUBLICATION my_pub_forwarded FOR ALL TABLES;
    RAISE NOTICE '发布my_pub_forwarded创建成功（用于转发）';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布my_pub_forwarded已存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- Subscriber2：订阅Subscriber1（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'sub_from_subscriber1'
    ) THEN
        RAISE WARNING '订阅sub_from_subscriber1已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'my_pub_forwarded'
    ) THEN
        RAISE EXCEPTION '发布my_pub_forwarded不存在，请先在Subscriber1创建';
    END IF;

    CREATE SUBSCRIPTION sub_from_subscriber1
        CONNECTION 'host=subscriber1 ...'
        PUBLICATION my_pub_forwarded;
    RAISE NOTICE '订阅sub_from_subscriber1创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅sub_from_subscriber1已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布my_pub_forwarded不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到Subscriber1';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;
```

---

## 3. 冲突检测和解决

### 3.1 常见冲突类型

| 冲突类型 | 原因 | 默认行为 | 解决方案 |
|---------|------|---------|---------|
| **主键冲突** | INSERT冲突主键 | 停止复制 | on_error = skip |
| **UPDATE未找到** | UPDATE的行不存在 | 停止复制 | 检查数据一致性 |
| **DELETE未找到** | DELETE的行不存在 | 跳过 | 无需处理 |
| **CHECK约束** | 数据不满足约束 | 停止复制 | 调整约束或数据 |
| **外键约束** | 外键引用不存在 | 停止复制 | 先复制父表 |

### 3.2 冲突检测

```sql
-- 查看复制错误
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_time,
    (latest_end_time - last_msg_receipt_time) AS replication_lag
FROM pg_stat_subscription;

-- 查看详细错误
SELECT * FROM pg_subscription_rel WHERE srsubstate = 'd';  -- 'd' = 数据同步失败

-- 查看日志
SHOW log_directory;
-- tail -f /var/log/postgresql/postgresql-*.log | grep "logical replication"
```

### 3.3 冲突解决策略

**策略1：跳过冲突（适用于可容忍数据丢失）**:

```sql
-- PostgreSQL 15+
ALTER SUBSCRIPTION my_sub SET (disable_on_error = false);
-- 遇到错误继续复制，跳过问题行

-- 查看被跳过的行
-- 需要在日志中查看
```

**策略2：手动解决冲突**:

```sql
-- 步骤1：查看冲突详情（从日志）
-- 假设冲突：INSERT users (user_id=123, username='alice')
-- 错误：duplicate key value violates unique constraint "users_pkey"

-- 步骤2：在订阅端检查（带错误处理和性能测试）
DO $$
DECLARE
    user_exists BOOLEAN;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE WARNING '表users不存在，跳过检查';
        RETURN;
    END IF;

    SELECT EXISTS(SELECT 1 FROM users WHERE user_id = 123) INTO user_exists;
    IF user_exists THEN
        RAISE NOTICE '用户123存在';
    ELSE
        RAISE NOTICE '用户123不存在';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '表users不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '检查用户失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE user_id = 123;
-- 执行时间: <10ms（如果使用索引）
-- 计划: Index Scan

-- 步骤3：决策
-- 选项A：保留订阅端数据，跳过发布端数据
DELETE FROM users WHERE user_id = 123;  -- 然后复制会重新INSERT

-- 选项B：删除订阅端数据，使用发布端数据
-- （不需要操作，复制会失败，手动修复后继续）

-- 步骤4：重置订阅状态
ALTER SUBSCRIPTION my_sub ENABLE;
```

**策略3：使用触发器处理冲突**:

```sql
-- 在订阅端创建冲突解决触发器（带错误处理）
-- 注意：逻辑复制不能直接使用ON CONFLICT，需要在应用层或使用规则系统
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'resolve_user_conflict'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        DROP FUNCTION resolve_user_conflict() CASCADE;
        RAISE NOTICE '已删除现有函数: resolve_user_conflict';
    END IF;

    CREATE OR REPLACE FUNCTION resolve_user_conflict()
    RETURNS trigger AS $$
    BEGIN
        -- 注意：此函数仅作为示例，逻辑复制不能直接使用ON CONFLICT
        -- INSERT冲突：更新现有行（需要在应用层处理）
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    RAISE NOTICE '函数resolve_user_conflict创建成功（示例函数）';
EXCEPTION
    WHEN duplicate_function THEN
        RAISE WARNING '函数resolve_user_conflict已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建函数失败: %', SQLERRM;
END $$;

-- 替代方案：使用RULE（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_rules
        WHERE schemaname = 'public' AND rulename = 'users_insert_conflict'
    ) THEN
        DROP RULE users_insert_conflict ON users;
        RAISE NOTICE '已删除现有规则: users_insert_conflict';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    CREATE RULE users_insert_conflict AS
        ON INSERT TO users
        WHERE EXISTS (SELECT 1 FROM users WHERE user_id = NEW.user_id)
        DO INSTEAD
            UPDATE users SET
                username = NEW.username,
                email = NEW.email
            WHERE user_id = NEW.user_id;

    RAISE NOTICE '规则users_insert_conflict创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '规则users_insert_conflict已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建规则失败: %', SQLERRM;
END $$;
```

**策略4：时间戳冲突解决（Last-Write-Wins）**:

```sql
-- 表结构（添加时间戳列，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        DROP TABLE users CASCADE;
        RAISE NOTICE '已删除现有表: users';
    END IF;

    CREATE TABLE users (
        user_id int PRIMARY KEY,
        username text,
        email text,
        updated_at timestamptz DEFAULT now()
    );
    RAISE NOTICE '表users创建成功（带时间戳列）';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表users已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表users失败: %', SQLERRM;
END $$;

-- 冲突解决规则（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'lww_conflict_resolution'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        DROP FUNCTION lww_conflict_resolution() CASCADE;
        RAISE NOTICE '已删除现有函数: lww_conflict_resolution';
    END IF;

    -- LWW冲突解决触发器函数（带完整错误处理）
    CREATE OR REPLACE FUNCTION lww_conflict_resolution()
    RETURNS trigger
    LANGUAGE plpgsql
    AS $$
    BEGIN
        -- 检查NEW和OLD记录
        IF NEW IS NULL THEN
            RAISE WARNING 'NEW记录为空，无法进行冲突解决';
            RETURN NULL;
        END IF;

        IF OLD IS NULL THEN
            RAISE WARNING 'OLD记录为空，返回NEW记录';
            RETURN NEW;
        END IF;

        -- 验证时间戳字段存在
        IF NEW.updated_at IS NULL THEN
            RAISE WARNING 'NEW.updated_at为空，设置当前时间';
            NEW.updated_at := NOW();
        END IF;

        IF OLD.updated_at IS NULL THEN
            RAISE WARNING 'OLD.updated_at为空，使用NEW记录';
            RETURN NEW;
        END IF;

        -- LWW冲突解决：如果新数据更新时间更晚，则更新
        IF NEW.updated_at > OLD.updated_at THEN
            RETURN NEW;
        ELSE
            -- 保留旧数据
            RETURN OLD;
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING 'lww_conflict_resolution触发器函数执行失败: %', SQLERRM;
            RETURN OLD;  -- 出错时保留旧数据
    END;
    $$;

    RAISE NOTICE '函数lww_conflict_resolution创建成功';
EXCEPTION
    WHEN duplicate_function THEN
        RAISE WARNING '函数lww_conflict_resolution已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建函数失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'lww_trigger'
        AND tgrelid = 'users'::regclass
    ) THEN
        DROP TRIGGER lww_trigger ON users;
        RAISE NOTICE '已删除现有触发器: lww_trigger';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'users'
    ) THEN
        RAISE EXCEPTION '表users不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'lww_conflict_resolution'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        RAISE EXCEPTION '函数lww_conflict_resolution不存在，请先创建';
    END IF;

    CREATE TRIGGER lww_trigger
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION lww_conflict_resolution();

    RAISE NOTICE '触发器lww_trigger创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '触发器lww_trigger已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表users不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION '函数lww_conflict_resolution不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;
```

---

## 4. 双向复制

### 4.1 双向复制配置

**需求**：两个数据中心，双向同步

```sql
-- 数据中心A（dc-a）
-- 1. 创建表（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        DROP TABLE products CASCADE;
        RAISE NOTICE '已删除现有表: products';
    END IF;

    CREATE TABLE products (
        product_id int PRIMARY KEY,
        product_name text,
        price numeric,
        updated_at timestamptz DEFAULT now(),
        updated_from text DEFAULT 'dc-a'  -- 标识更新来源
    );
    RAISE NOTICE '表products创建成功（dc-a）';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表products已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表products失败: %', SQLERRM;
END $$;

-- 2. 创建发布（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'pub_dc_a'
    ) THEN
        RAISE WARNING '发布pub_dc_a已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        RAISE EXCEPTION '表products不存在，请先创建';
    END IF;

    CREATE PUBLICATION pub_dc_a FOR TABLE products;
    RAISE NOTICE '发布pub_dc_a创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布pub_dc_a已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表products不存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

-- 3. 创建订阅（从dc-b，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'sub_from_dc_b'
    ) THEN
        RAISE WARNING '订阅sub_from_dc_b已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'pub_dc_b'
    ) THEN
        RAISE EXCEPTION '发布pub_dc_b不存在，请先在数据中心B创建';
    END IF;

    CREATE SUBSCRIPTION sub_from_dc_b
        CONNECTION 'host=dc-b port=5432 dbname=mydb user=replicator password=xxx'
        PUBLICATION pub_dc_b;
    RAISE NOTICE '订阅sub_from_dc_b创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅sub_from_dc_b已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布pub_dc_b不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到数据中心B';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;

-- 数据中心B（dc-b）
-- 相同配置，但方向相反（带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        DROP TABLE products CASCADE;
        RAISE NOTICE '已删除现有表: products';
    END IF;

    CREATE TABLE products (
        product_id int PRIMARY KEY,
        product_name text,
        price numeric,
        updated_at timestamptz DEFAULT now(),
        updated_from text DEFAULT 'dc-b'
    );
    RAISE NOTICE '表products创建成功（dc-b）';
EXCEPTION
    WHEN duplicate_table THEN
        RAISE WARNING '表products已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建表products失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'pub_dc_b'
    ) THEN
        RAISE WARNING '发布pub_dc_b已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        RAISE EXCEPTION '表products不存在，请先创建';
    END IF;

    CREATE PUBLICATION pub_dc_b FOR TABLE products;
    RAISE NOTICE '发布pub_dc_b创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '发布pub_dc_b已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表products不存在';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建发布';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建发布失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_subscription WHERE subname = 'sub_from_dc_a'
    ) THEN
        RAISE WARNING '订阅sub_from_dc_a已存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'pub_dc_a'
    ) THEN
        RAISE EXCEPTION '发布pub_dc_a不存在，请先在数据中心A创建';
    END IF;

    CREATE SUBSCRIPTION sub_from_dc_a
        CONNECTION 'host=dc-a port=5432 dbname=mydb user=replicator password=xxx'
        PUBLICATION pub_dc_a;
    RAISE NOTICE '订阅sub_from_dc_a创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '订阅sub_from_dc_a已存在';
    WHEN undefined_object THEN
        RAISE EXCEPTION '发布pub_dc_a不存在';
    WHEN connection_exception THEN
        RAISE EXCEPTION '无法连接到数据中心A';
    WHEN insufficient_privilege THEN
        RAISE EXCEPTION '权限不足，无法创建订阅';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建订阅失败: %', SQLERRM;
END $$;
```

**冲突处理（双向复制）**：

```sql
-- 方案1：基于时间戳（Last-Write-Wins，带错误处理）
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'bidirectional_lww_trigger'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        DROP FUNCTION bidirectional_lww_trigger() CASCADE;
        RAISE NOTICE '已删除现有函数: bidirectional_lww_trigger';
    END IF;

    CREATE OR REPLACE FUNCTION bidirectional_lww_trigger()
    RETURNS trigger AS $$
    DECLARE
        source_dc text;
    BEGIN
        -- 获取复制来源
        source_dc := current_setting('application_name', true);

        -- 如果是从订阅来的更新
        IF source_dc LIKE 'sub_from_%' THEN
            -- 比较时间戳
            IF NEW.updated_at <= OLD.updated_at THEN
                -- 旧数据，不更新
                RETURN OLD;
            END IF;
        ELSE
            -- 本地更新，设置updated_from
            NEW.updated_from := 'dc-a';  -- 或dc-b
            NEW.updated_at := now();
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    RAISE NOTICE '函数bidirectional_lww_trigger创建成功';
EXCEPTION
    WHEN duplicate_function THEN
        RAISE WARNING '函数bidirectional_lww_trigger已存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建函数失败: %', SQLERRM;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'bidirectional_trigger'
        AND tgrelid = 'products'::regclass
    ) THEN
        DROP TRIGGER bidirectional_trigger ON products;
        RAISE NOTICE '已删除现有触发器: bidirectional_trigger';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'products'
    ) THEN
        RAISE EXCEPTION '表products不存在，请先创建';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'bidirectional_lww_trigger'
        AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ) THEN
        RAISE EXCEPTION '函数bidirectional_lww_trigger不存在，请先创建';
    END IF;

    CREATE TRIGGER bidirectional_trigger
        BEFORE UPDATE ON products
        FOR EACH ROW
        EXECUTE FUNCTION bidirectional_lww_trigger();

    RAISE NOTICE '触发器bidirectional_trigger创建成功';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE WARNING '触发器bidirectional_trigger已存在';
    WHEN undefined_table THEN
        RAISE EXCEPTION '表products不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION '函数bidirectional_lww_trigger不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '创建触发器失败: %', SQLERRM;
END $$;
```

**方案2：使用pglogical扩展（推荐）**:

```bash
# 安装pglogical
sudo apt-get install postgresql-17-pglogical
```

```sql
-- 数据中心A
CREATE EXTENSION pglogical;

SELECT pglogical.create_node(
    node_name := 'dc_a',
    dsn := 'host=dc-a port=5432 dbname=mydb'
);

SELECT pglogical.create_replication_set(
    set_name := 'default',
    replicate_insert := true,
    replicate_update := true,
    replicate_delete := true,
    replicate_truncate := true
);

SELECT pglogical.replication_set_add_table(
    set_name := 'default',
    relation := 'products',
    synchronize_data := true
);

-- 订阅dc-b
SELECT pglogical.create_subscription(
    subscription_name := 'sub_dc_b',
    provider_dsn := 'host=dc-b port=5432 dbname=mydb user=replicator',
    replication_sets := ARRAY['default'],
    synchronize_structure := false,
    synchronize_data := true,
    forward_origins := ARRAY['all']  -- 转发所有来源的数据
);

-- 数据中心B（类似配置）
-- ...
```

---

## 5. 逻辑复制监控

### 5.1 监控复制延迟

```sql
-- 发布端：查看复制槽（带错误处理和性能测试）
DO $$
DECLARE
    slot_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_replication_slots'
    ) THEN
        RAISE WARNING 'pg_replication_slots表不存在';
        RETURN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'pg_current_wal_lsn') THEN
        RAISE EXCEPTION 'pg_current_wal_lsn函数不存在';
    END IF;

    SELECT COUNT(*) INTO slot_count
    FROM pg_replication_slots
    WHERE slot_type = 'logical';

    IF slot_count > 0 THEN
        RAISE NOTICE '发现 % 个逻辑复制槽', slot_count;
    ELSE
        RAISE NOTICE '未发现逻辑复制槽';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_replication_slots表不存在';
    WHEN undefined_function THEN
        RAISE EXCEPTION 'pg_current_wal_lsn函数不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看复制槽失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    slot_name,
    plugin,
    slot_type,
    database,
    active,
    restart_lsn,
    confirmed_flush_lsn,
    pg_current_wal_lsn() - confirmed_flush_lsn AS replication_lag_bytes,
    pg_size_pretty(pg_current_wal_lsn() - confirmed_flush_lsn) AS lag_size
FROM pg_replication_slots
WHERE slot_type = 'logical';
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 订阅端：查看订阅状态（带错误处理和性能测试）
DO $$
DECLARE
    subscription_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_stat_subscription'
    ) THEN
        RAISE WARNING 'pg_stat_subscription视图不存在（需要PostgreSQL 10+）';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO subscription_count
    FROM pg_stat_subscription;

    IF subscription_count > 0 THEN
        RAISE NOTICE '发现 % 条订阅统计记录', subscription_count;
    ELSE
        RAISE NOTICE '未发现订阅统计记录';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING 'pg_stat_subscription视图不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看订阅状态失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time,
    latest_end_time,
    EXTRACT(EPOCH FROM (now() - latest_end_time)) AS lag_seconds
FROM pg_stat_subscription;
-- 执行时间: <50ms
-- 计划: Seq Scan

-- 详细的表级别状态（带错误处理和性能测试）
DO $$
DECLARE
    rel_count INT;
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_subscription_rel'
    ) THEN
        RAISE WARNING 'pg_subscription_rel表不存在';
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'pg_catalog' AND table_name = 'pg_subscription'
    ) THEN
        RAISE WARNING 'pg_subscription表不存在';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO rel_count
    FROM pg_subscription_rel;

    IF rel_count > 0 THEN
        RAISE NOTICE '发现 % 条订阅关系记录', rel_count;
    ELSE
        RAISE NOTICE '未发现订阅关系记录';
    END IF;
EXCEPTION
    WHEN undefined_table THEN
        RAISE WARNING '相关表不存在';
    WHEN OTHERS THEN
        RAISE EXCEPTION '查看表级别状态失败: %', SQLERRM;
END $$;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT
    sr.srsubid,
    s.subname,
    sr.srrelid::regclass AS table_name,
    sr.srsubstate,  -- r=ready, d=data_sync, s=sync, i=init
    sr.srsublsn
FROM pg_subscription_rel sr
JOIN pg_subscription s ON sr.srsubid = s.oid;
-- 执行时间: <100ms（取决于订阅关系数量）
-- 计划: Hash Join -> Seq Scan
```

### 5.2 监控WAL占用

```sql
-- 检查WAL堆积（复制槽占用）
SELECT
    slot_name,
    pg_size_pretty(
        pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)
    ) AS wal_retained,
    active
FROM pg_replication_slots
WHERE slot_type = 'logical'
ORDER BY pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) DESC;

-- 告警：WAL堆积超过10GB
SELECT
    slot_name,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) / 1024 / 1024 / 1024.0 AS wal_gb
FROM pg_replication_slots
WHERE slot_type = 'logical'
  AND pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 10737418240;  -- 10GB
```

### 5.3 复制性能监控

```sql
-- 查看复制worker状态
SELECT
    pid,
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication
WHERE application_name LIKE 'sub_%';

-- 查看apply worker统计
SELECT * FROM pg_stat_subscription_stats;
-- PostgreSQL 15+提供统计信息
```

---

## 6. 性能优化

### 6.1 批量应用优化

```sql
-- 订阅端配置
ALTER SUBSCRIPTION my_sub SET (streaming = on);  -- PostgreSQL 14+流式应用
ALTER SUBSCRIPTION my_sub SET (binary = true);   -- PostgreSQL 14+二进制格式
ALTER SUBSCRIPTION my_sub SET (parallel_apply_workers = 4);  -- PostgreSQL 16+并行应用

-- 发布端优化
ALTER SYSTEM SET wal_sender_timeout = '60s';
ALTER SYSTEM SET max_logical_replication_workers = 8;
SELECT pg_reload_conf();
```

### 6.2 大事务处理

```sql
-- 问题：大事务（如批量导入）导致复制延迟

-- 发布端：分批提交
DO $$
DECLARE
    batch_size int := 10000;
    total_rows int := 0;
BEGIN
    LOOP
        -- 插入一批
        WITH batch AS (
            INSERT INTO users (username, email)
            SELECT 'user_' || (1000000 + i), 'email' || i || '@example.com'
            FROM generate_series(total_rows + 1, total_rows + batch_size) i
            RETURNING *
        )
        SELECT COUNT(*) INTO batch_size FROM batch;

        EXIT WHEN batch_size = 0;

        total_rows := total_rows + batch_size;

        COMMIT;  -- 提交一批

        -- 限流
        PERFORM pg_sleep(0.1);
    END LOOP;
END $$;

-- 订阅端：调整配置
ALTER SUBSCRIPTION my_sub SET (streaming = on);  -- 流式应用大事务
```

### 6.3 初始数据同步优化

```sql
-- 方案1：禁用触发器和约束（同步期间）
ALTER TABLE users DISABLE TRIGGER ALL;
ALTER TABLE users ALTER CONSTRAINT users_pkey DEFERRABLE;

-- 创建订阅（copy_data = true）
CREATE SUBSCRIPTION my_sub
    CONNECTION '...'
    PUBLICATION my_pub
    WITH (copy_data = true);

-- 等待初始同步完成
SELECT * FROM pg_subscription_rel WHERE srsubstate != 'r';

-- 重新启用
ALTER TABLE users ENABLE TRIGGER ALL;

-- 方案2：使用pg_dump/restore（更快）
-- 1. 在发布端dump
pg_dump -h publisher -U postgres -t users --no-owner --no-acl -Fc > users.dump

-- 2. 在订阅端restore
pg_restore -h subscriber -U postgres -d mydb users.dump

-- 3. 创建订阅（不同步初始数据）
CREATE SUBSCRIPTION my_sub
    CONNECTION '...'
    PUBLICATION my_pub
    WITH (copy_data = false);  -- 不同步初始数据
```

---

## 7. 完整生产案例

### 7.1 案例：跨版本升级（PG 16 → PG 17）

**需求**：零停机升级PostgreSQL

**方案**：使用逻辑复制

```bash
# 步骤1：准备新服务器（PG 17）
sudo apt-get install postgresql-17
sudo -u postgres initdb -D /var/lib/postgresql/17/main

# 步骤2：在旧服务器（PG 16）创建发布
psql -U postgres <<EOF
-- 配置
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- 创建发布
CREATE PUBLICATION upgrade_pub FOR ALL TABLES;

-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'xxx';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;
EOF

# 步骤3：在新服务器（PG 17）创建结构
pg_dump -h old-server -U postgres --schema-only | psql -h new-server -U postgres

# 步骤4：创建订阅
psql -h new-server -U postgres <<EOF
CREATE SUBSCRIPTION upgrade_sub
    CONNECTION 'host=old-server port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION upgrade_pub
    WITH (copy_data = true);
EOF

# 步骤5：等待初始同步完成
psql -h new-server -U postgres -c "
    SELECT
        COUNT(*) FILTER (WHERE srsubstate = 'r') AS ready_tables,
        COUNT(*) AS total_tables
    FROM pg_subscription_rel;
"

# 步骤6：监控复制延迟
watch -n 1 "psql -h new-server -U postgres -c \"
    SELECT
        subname,
        EXTRACT(EPOCH FROM (now() - latest_end_time)) AS lag_seconds
    FROM pg_stat_subscription;
\""

# 步骤7：等待延迟<1秒，切换应用
# 1. 停止写入旧服务器
# 2. 等待复制完全同步
# 3. 切换应用指向新服务器
# 4. 验证

# 步骤8：清理
psql -h new-server -U postgres -c "DROP SUBSCRIPTION upgrade_sub"
psql -h old-server -U postgres -c "DROP PUBLICATION upgrade_pub"
```

### 7.2 案例：数据汇总（多源到一个数据仓库）

**需求**：3个应用数据库→1个分析数据库

```sql
-- 数据仓库端
-- 1. 创建汇总表
CREATE TABLE dw_orders (
    source_db text NOT NULL,      -- 来源标识
    order_id bigint NOT NULL,
    order_date date,
    customer_id int,
    amount numeric,
    created_at timestamptz,
    PRIMARY KEY (source_db, order_id)
) PARTITION BY LIST (source_db);

-- 2. 为每个源创建分区
CREATE TABLE dw_orders_app1 PARTITION OF dw_orders FOR VALUES IN ('app1');
CREATE TABLE dw_orders_app2 PARTITION OF dw_orders FOR VALUES IN ('app2');
CREATE TABLE dw_orders_app3 PARTITION OF dw_orders FOR VALUES IN ('app3');

-- 3. 订阅所有源
CREATE SUBSCRIPTION sub_app1
    CONNECTION 'host=app1-db port=5432 dbname=app1 user=replicator password=xxx'
    PUBLICATION pub_orders
    WITH (
        origin = none,
        transform = 'add_column_default(source_db, ''app1'')'  -- 添加source_db列
    );

CREATE SUBSCRIPTION sub_app2
    CONNECTION 'host=app2-db ...'
    PUBLICATION pub_orders;

CREATE SUBSCRIPTION sub_app3
    CONNECTION 'host=app3-db ...'
    PUBLICATION pub_orders;

-- 4. 查询汇总数据
SELECT
    source_db,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM dw_orders
WHERE order_date >= current_date - 30
GROUP BY source_db;
```

### 7.3 案例：读写分离（逻辑复制）

```sql
-- 主库：所有表发布
CREATE PUBLICATION readonly_pub FOR ALL TABLES;

-- 只读副本1：订阅所有表
CREATE SUBSCRIPTION readonly_sub1
    CONNECTION 'host=primary port=5432 dbname=mydb user=replicator password=xxx'
    PUBLICATION readonly_pub
    WITH (
        copy_data = true,
        streaming = on,
        binary = true
    );

-- 只读副本2
CREATE SUBSCRIPTION readonly_sub2
    CONNECTION '...'
    PUBLICATION readonly_pub;

-- 应用层配置
-- 写操作 → primary
-- 读操作 → 负载均衡(readonly_sub1, readonly_sub2)
```

---

## 8. 高级场景

### 8.1 选择性复制（部分行、部分列）

```sql
-- 场景：只同步VIP客户的订单到数据仓库

-- 发布端
CREATE PUBLICATION vip_orders_pub
FOR TABLE orders
WHERE (
    customer_id IN (SELECT customer_id FROM vip_customers)
);

-- 订阅端
CREATE SUBSCRIPTION vip_orders_sub
    CONNECTION '...'
    PUBLICATION vip_orders_pub;

-- 只有VIP客户的订单会被复制
```

### 8.2 数据转换（Transform）

```sql
-- PostgreSQL 17+ 支持（规划中）
-- 当前版本可以使用触发器实现

-- 订阅端：数据转换触发器
-- 转换订单数据触发器函数（带完整错误处理）
CREATE OR REPLACE FUNCTION transform_orders()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    v_exchange_rate NUMERIC := 6.8;  -- USD to CNY汇率
BEGIN
    -- 检查NEW记录
    IF NEW IS NULL THEN
        RAISE WARNING 'NEW记录为空，无法转换订单数据';
        RETURN NULL;
    END IF;

    -- 转换货币
    BEGIN
        IF NEW.amount IS NOT NULL THEN
            IF NEW.amount < 0 THEN
                RAISE WARNING '订单金额为负数: %, 跳过转换', NEW.amount;
            ELSE
                NEW.amount := NEW.amount * v_exchange_rate;

                -- 检查数值溢出
                IF NEW.amount > 999999999.99 THEN
                    RAISE EXCEPTION '转换后金额超出范围: %', NEW.amount;
                END IF;
            END IF;
        ELSE
            RAISE WARNING '订单金额为空，跳过货币转换';
        END IF;
    EXCEPTION
        WHEN numeric_value_out_of_range THEN
            RAISE EXCEPTION '货币转换数值溢出';
        WHEN OTHERS THEN
            RAISE WARNING '货币转换失败: %', SQLERRM;
    END;

    -- 脱敏客户邮箱
    BEGIN
        IF NEW.customer_email IS NOT NULL AND TRIM(NEW.customer_email) != '' THEN
            NEW.customer_email := regexp_replace(
                NEW.customer_email,
                '(.{2})(.*)(@.*)',
                '\1***\3',
                'g'
            );

            -- 验证脱敏结果
            IF NEW.customer_email IS NULL OR NEW.customer_email = '' THEN
                RAISE WARNING '邮箱脱敏失败，保留原值';
            END IF;
        ELSE
            RAISE WARNING '客户邮箱为空，跳过脱敏';
        END IF;
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '邮箱脱敏失败: %', SQLERRM;
    END;

    -- 添加同步时间戳
    BEGIN
        NEW.synced_at := NOW();
    EXCEPTION
        WHEN OTHERS THEN
            RAISE WARNING '设置同步时间戳失败: %', SQLERRM;
    END;

    RETURN NEW;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'transform_orders触发器函数执行失败: %', SQLERRM;
        RETURN NEW;  -- 即使出错也返回NEW，避免阻塞主操作
END;
$$;

CREATE TRIGGER transform_trigger
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW
    WHEN (pg_trigger_depth() = 1)  -- 只对复制触发
    EXECUTE FUNCTION transform_orders();
```

---

## 📚 参考资源

### 官方文档

1. [Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html)
2. [Publication](https://www.postgresql.org/docs/current/sql-createpublication.html)
3. [Subscription](https://www.postgresql.org/docs/current/sql-createsubscription.html)

### 扩展和工具

1. [pglogical](https://github.com/2ndQuadrant/pglogical) - 增强的逻辑复制
2. [Bucardo](https://bucardo.org/) - 多主复制
3. [SymmetricDS](https://www.symmetricds.org/) - 数据库同步工具

### 最佳实践

1. [Logical Replication Best Practices](https://wiki.postgresql.org/wiki/Logical_Replication_Best_Practices)
2. [Conflict Resolution Strategies](https://www.postgresql.org/docs/current/logical-replication-conflicts.html)

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐⭐ 专家级

🔄 **掌握逻辑复制，实现灵活的数据同步！**
