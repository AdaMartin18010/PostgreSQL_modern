# DCA缓存层集成方案

> **文档类型**: 缓存集成指南
> **缓存类型**: Redis, Memcached
> **更新日期**: 2026-03-04

---

## 目录

- [DCA缓存层集成方案](#dca缓存层集成方案)
  - [目录](#目录)
  - [1. 缓存策略](#1-缓存策略)
    - [1.1 缓存架构](#11-缓存架构)
    - [1.2 缓存策略矩阵](#12-缓存策略矩阵)
  - [2. Redis集成](#2-redis集成)
    - [2.1 Redis配置](#21-redis配置)
    - [2.2 Redis配置文件](#22-redis配置文件)
  - [3. 缓存一致性](#3-缓存一致性)
    - [3.1 数据库触发器自动失效缓存](#31-数据库触发器自动失效缓存)
    - [3.2 Python缓存管理器](#32-python缓存管理器)
  - [4. 性能优化](#4-性能优化)
    - [4.1 缓存命中率监控](#41-缓存命中率监控)
    - [4.2 缓存优化建议](#42-缓存优化建议)

---

## 1. 缓存策略

### 1.1 缓存架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           应用层                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Cache Layer                                   │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│  │  │  L1 本地缓存  │  │  L2 Redis    │  │  L3 数据库    │               │  │
│  │  │ (Caffeine)   │  │  (Cluster)   │  │  PostgreSQL  │               │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│  Cache-Aside (Lazy Loading)        │                                        │
│  Write-Through / Write-Behind      │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
```

### 1.2 缓存策略矩阵

| 数据类型 | 缓存策略 | TTL | 更新方式 |
|---------|---------|-----|---------|
| 用户信息 | Cache-Aside | 1小时 | 主动失效 |
| 产品信息 | Cache-Aside | 5分钟 | 主动失效 |
| 订单详情 | Cache-Aside | 30秒 | 主动失效 |
| 库存数量 | Write-Through | 10秒 | 实时同步 |
| 热销榜单 | Write-Behind | 1分钟 | 定时刷新 |
| 报表数据 | Cache-Aside | 1小时 | 定时刷新 |

---

## 2. Redis集成

### 2.1 Redis配置

```yaml
# docker-compose.redis.yml
version: '3.8'

services:
  redis-master:
    image: redis:7-alpine
    container_name: dca-redis-master
    ports:
      - "6379:6379"
    volumes:
      - redis_master_data:/data
      - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - dca-network

  redis-slave-1:
    image: redis:7-alpine
    container_name: dca-redis-slave-1
    ports:
      - "6380:6379"
    command: redis-server --slaveof redis-master 6379
    networks:
      - dca-network

  redis-slave-2:
    image: redis:7-alpine
    container_name: dca-redis-slave-2
    ports:
      - "6381:6379"
    command: redis-server --slaveof redis-master 6379
    networks:
      - dca-network

  redis-sentinel-1:
    image: redis:7-alpine
    container_name: dca-redis-sentinel-1
    ports:
      - "26379:26379"
    volumes:
      - ./redis/sentinel.conf:/usr/local/etc/redis/sentinel.conf
    command: redis-sentinel /usr/local/etc/redis/sentinel.conf
    networks:
      - dca-network

volumes:
  redis_master_data:

networks:
  dca-network:
    external: true
```

### 2.2 Redis配置文件

```conf
# redis.conf
bind 0.0.0.0
port 6379
daemonize no

# 内存配置
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# AOF配置
appendonly yes
appendfsync everysec

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# 监控
latency-monitor-threshold 100
```

---

## 3. 缓存一致性

### 3.1 数据库触发器自动失效缓存

```sql
-- ============================================
-- 缓存失效触发器
-- ============================================

-- 创建缓存失效日志表
CREATE TABLE cache_invalidation_queue (
    id BIGSERIAL PRIMARY KEY,
    cache_key TEXT NOT NULL,
    invalidation_type TEXT NOT NULL,  -- 'delete', 'pattern'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed BOOLEAN DEFAULT false,
    processed_at TIMESTAMPTZ
);

-- 创建缓存失效触发器函数
CREATE OR REPLACE FUNCTION fn_invalidate_cache()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_cache_key TEXT;
    v_pattern TEXT;
BEGIN
    -- 根据表名构建缓存key
    CASE TG_TABLE_NAME
        WHEN 'users' THEN
            v_cache_key := 'user:' || COALESCE(NEW.id, OLD.id)::TEXT;
            v_pattern := 'users:*';
        WHEN 'products' THEN
            v_cache_key := 'product:' || COALESCE(NEW.id, OLD.id)::TEXT;
            v_pattern := 'products:*';
        WHEN 'orders' THEN
            v_cache_key := 'order:' || COALESCE(NEW.id, OLD.id)::TEXT;
            v_pattern := 'orders:*';
        ELSE
            v_cache_key := TG_TABLE_NAME || ':' || COALESCE(NEW.id, OLD.id)::TEXT;
            v_pattern := TG_TABLE_NAME || ':*';
    END CASE;

    -- 记录失效请求
    INSERT INTO cache_invalidation_queue (cache_key, invalidation_type)
    VALUES
        (v_cache_key, 'delete'),
        (v_pattern, 'pattern');

    -- 发送通知（由后台进程处理）
    PERFORM pg_notify('cache_invalidation', jsonb_build_object(
        'key', v_cache_key,
        'pattern', v_pattern,
        'table', TG_TABLE_NAME,
        'operation', TG_OP
    )::TEXT);

    RETURN COALESCE(NEW, OLD);
END;
$$;

-- 应用到关键表
CREATE TRIGGER trg_invalidate_cache_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION fn_invalidate_cache();

CREATE TRIGGER trg_invalidate_cache_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION fn_invalidate_cache();

CREATE TRIGGER trg_invalidate_cache_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION fn_invalidate_cache();
```

### 3.2 Python缓存管理器

```python
# ============================================
# cache/manager.py - 缓存管理器
# ============================================

import json
import redis
import hashlib
from functools import wraps
from typing import Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis缓存管理器"""

    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30
        )
        self.default_ttl = 300  # 5分钟默认TTL

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except redis.RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存"""
        try:
            serialized = json.dumps(value, default=str)
            return self.redis_client.setex(
                key,
                ttl or self.default_ttl,
                serialized
            )
        except redis.RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return self.redis_client.delete(key) > 0
        except redis.RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error(f"Redis delete pattern error: {e}")
            return 0

    def invalidate(self, key: str) -> bool:
        """使缓存失效（带发布通知）"""
        result = self.delete(key)
        try:
            self.redis_client.publish('cache_invalidation', json.dumps({
                'action': 'delete',
                'key': key
            }))
        except redis.RedisError:
            pass
        return result

    def get_or_set(self, key: str, getter: Callable, ttl: int = None) -> Any:
        """获取或设置缓存"""
        # 尝试从缓存获取
        value = self.get(key)
        if value is not None:
            return value

        # 从数据源获取
        value = getter()

        # 设置缓存
        if value is not None:
            self.set(key, value, ttl)

        return value

    def clear_all(self) -> bool:
        """清空所有缓存（谨慎使用）"""
        try:
            return self.redis_client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis flush error: {e}")
            return False


def cached(key_prefix: str, ttl: int = 300, key_builder: Callable = None):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # 默认key构建
                key_parts = [key_prefix]
                if args:
                    key_parts.append(str(args[0]))
                cache_key = ':'.join(key_parts)

            # 从缓存获取
            cache = CacheManager()
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行函数
            result = func(*args, **kwargs)

            # 设置缓存
            if result is not None:
                cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


# 缓存预热脚本
class CacheWarmer:
    """缓存预热器"""

    def __init__(self, cache: CacheManager):
        self.cache = cache

    def warm_user_cache(self, user_ids: list):
        """预热用户缓存"""
        from services.user_service import UserService

        for user_id in user_ids:
            user = UserService.get_user_by_id(user_id)
            if user:
                self.cache.set(f'user:{user_id}', user, ttl=3600)
                logger.info(f"Warmed cache for user {user_id}")

    def warm_product_cache(self, product_ids: list):
        """预热产品缓存"""
        from services.product_service import ProductService

        for product_id in product_ids:
            product = ProductService.get_product_by_id(product_id)
            if product:
                self.cache.set(f'product:{product_id}', product, ttl=300)

    def warm_hot_products(self):
        """预热热销产品"""
        from services.product_service import ProductService

        hot_products = ProductService.get_hot_products(limit=100)
        self.cache.set('products:hot', hot_products, ttl=600)
```

---

## 4. 性能优化

### 4.1 缓存命中率监控

```sql
-- ============================================
-- 缓存性能视图
-- ============================================

CREATE VIEW v_cache_performance AS
SELECT
    'user' as cache_type,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE cache_hit = true) as cache_hits,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cache_hit = true) / COUNT(*), 2) as hit_ratio,
    AVG(response_time_ms) as avg_response_time
FROM cache_log
WHERE cache_type = 'user'
  AND timestamp > NOW() - INTERVAL '1 hour'

UNION ALL

SELECT
    'product' as cache_type,
    COUNT(*) as total_requests,
    COUNT(*) FILTER (WHERE cache_hit = true) as cache_hits,
    ROUND(100.0 * COUNT(*) FILTER (WHERE cache_hit = true) / COUNT(*), 2) as hit_ratio,
    AVG(response_time_ms) as avg_response_time
FROM cache_log
WHERE cache_type = 'product'
  AND timestamp > NOW() - INTERVAL '1 hour';
```

### 4.2 缓存优化建议

```python
# ============================================
# 缓存优化工具
# ============================================

class CacheOptimizer:
    """缓存优化器"""

    def __init__(self, cache: CacheManager):
        self.cache = cache

    def analyze_key_patterns(self) -> dict:
        """分析key使用模式"""
        # 获取所有key
        all_keys = self.cache.redis_client.keys('*')

        # 按前缀分组
        patterns = {}
        for key in all_keys:
            prefix = key.split(':')[0] if ':' in key else 'other'
            patterns[prefix] = patterns.get(prefix, 0) + 1

        return patterns

    def recommend_ttl(self, key_pattern: str) -> int:
        """推荐TTL设置"""
        # 根据访问频率和更新频率推荐TTL
        access_stats = self._get_access_stats(key_pattern)
        update_stats = self._get_update_stats(key_pattern)

        if access_stats['frequency'] > 1000:  # 高频访问
            if update_stats['frequency'] < 10:  # 低频更新
                return 3600  # 1小时
            else:
                return 60  # 1分钟
        else:  # 低频访问
            return 300  # 5分钟

    def cleanup_expired_patterns(self):
        """清理过期模式的缓存"""
        # 找出长期未访问的key
        old_keys = self.cache.redis_client.keys('*')
        for key in old_keys:
            ttl = self.cache.redis_client.ttl(key)
            if ttl == -1:  # 永不过期
                # 设置一个合理的过期时间
                self.cache.redis_client.expire(key, 86400)  # 24小时
```

---

**文档版本**: v1.0
**更新日期**: 2026-03-04
