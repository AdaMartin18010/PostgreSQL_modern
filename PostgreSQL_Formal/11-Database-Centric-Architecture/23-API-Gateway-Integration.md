# DCA API网关集成方案

> **文档类型**: API网关集成指南
> **网关类型**: Kong, Nginx, Traefik
> **更新日期**: 2026-03-04

---

## 目录

- [DCA API网关集成方案](#dca-api网关集成方案)
  - [目录](#目录)
  - [1. 架构概述](#1-架构概述)
  - [2. Kong网关配置](#2-kong网关配置)
    - [2.1 docker-compose.yml](#21-docker-composeyml)
    - [2.2 Kong配置脚本](#22-kong配置脚本)
  - [3. Nginx配置](#3-nginx配置)
    - [3.1 Nginx配置文件](#31-nginx配置文件)
  - [4. 认证集成](#4-认证集成)
    - [4.1 JWT认证](#41-jwt认证)
    - [4.2 API Key认证](#42-api-key认证)

---

## 1. 架构概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API网关层                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   客户端     │  │   客户端     │  │   客户端     │  │     移动端          │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                    │            │
│         └────────────────┴────────────────┴────────────────────┘            │
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                         API Gateway (Kong/Nginx)                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│  │  │  限流/熔断    │  │  认证/授权    │  │  缓存层       │  │  日志监控  │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │  │
│  └─────────────────────────────────┬─────────────────────────────────────┘  │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                      DCA Backend (Python/Go)                          │  │
│  │                    调用数据库存储过程                                   │  │
│  └─────────────────────────────────┬─────────────────────────────────────┘  │
│                                    │                                        │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                        PostgreSQL DCA                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │  │
│  │  │ 存储过程      │  │ 触发器        │  │ 函数         │  │ 视图      │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Kong网关配置

### 2.1 docker-compose.yml

```yaml
version: '3.8'

services:
  kong-database:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: kong
      POSTGRES_DB: kong
      POSTGRES_PASSWORD: kong
    volumes:
      - kong_db:/var/lib/postgresql/data
    networks:
      - dca-network

  kong-migration:
    image: kong:latest
    command: kong migrations bootstrap
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
    depends_on:
      - kong-database
    networks:
      - dca-network

  kong:
    image: kong:latest
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: 0.0.0.0:8001
      KONG_PLUGINS: bundled,jwt-keycloak,prometheus
    ports:
      - "8000:8000"  # 代理入口
      - "8001:8001"  # Admin API
      - "8443:8443"  # HTTPS代理
      - "8444:8444"  # HTTPS Admin
    depends_on:
      - kong-migration
    networks:
      - dca-network

  konga:
    image: pantsel/konga:latest
    environment:
      NODE_ENV: production
      DB_ADAPTER: postgres
      DB_HOST: kong-database
      DB_USER: kong
      DB_PASSWORD: kong
      DB_DATABASE: konga
      TOKEN_SECRET: your-secret-key
    ports:
      - "1337:1337"
    depends_on:
      - kong-database
    networks:
      - dca-network

volumes:
  kong_db:

networks:
  dca-network:
    external: true
```

### 2.2 Kong配置脚本

```bash
#!/bin/bash
# ============================================
# setup-kong.sh - Kong网关初始化配置
# ============================================

KONG_ADMIN="http://localhost:8001"

# 1. 创建服务
echo "创建服务..."
curl -i -X POST ${KONG_ADMIN}/services \
  --data name=dca-order-service \
  --data url='http://backend:5000'

# 2. 创建路由
echo "创建路由..."
curl -i -X POST ${KONG_ADMIN}/services/dca-order-service/routes \
  --data 'paths[]=/api/orders' \
  --data name=orders-route

# 3. 启用JWT认证插件
echo "启用JWT认证..."
curl -X POST ${KONG_ADMIN}/services/dca-order-service/plugins \
  --data "name=jwt"

# 4. 启用限流插件
echo "启用限流..."
curl -X POST ${KONG_ADMIN}/services/dca-order-service/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100" \
  --data "config.policy=redis" \
  --data "config.redis_host=redis"

# 5. 启用Prometheus监控
echo "启用Prometheus监控..."
curl -X POST ${KONG_ADMIN}/services/dca-order-service/plugins \
  --data "name=prometheus"

# 6. 启用日志记录
echo "启用日志记录..."
curl -X POST ${KONG_ADMIN}/services/dca-order-service/plugins \
  --data "name=http-log" \
  --data "config.http_endpoint=http://log-collector:8080/logs"

# 7. 创建消费者
echo "创建API消费者..."
curl -X POST ${KONG_ADMIN}/consumers \
  --data username=dca-app-client

# 8. 创建JWT凭证
echo "创建JWT凭证..."
curl -X POST ${KONG_ADMIN}/consumers/dca-app-client/jwt \
  -H "Content-Type: application/x-www-form-urlencoded"

echo "Kong配置完成"
```

---

## 3. Nginx配置

### 3.1 Nginx配置文件

```nginx
# /etc/nginx/conf.d/dca-api.conf

upstream dca_backend {
    least_conn;
    server backend1:5000 max_fails=3 fail_timeout=30s;
    server backend2:5000 max_fails=3 fail_timeout=30s;
    server backend3:5000 max_fails=3 fail_timeout=30s;
    keepalive 64;
}

# 限流区域
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    listen 80;
    server_name api.dca.example.com;

    # 强制HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.dca.example.com;

    # SSL配置
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
    ssl_prefer_server_ciphers on;

    # 日志
    access_log /var/log/nginx/dca-api-access.log json_analytics;
    error_log /var/log/nginx/dca-api-error.log;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 请求体大小限制
    client_max_body_size 10m;
    client_body_buffer_size 128k;

    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # 订单API
    location /api/orders {
        # 限流
        limit_req zone=api_limit burst=20 nodelay;
        limit_conn addr 10;

        # 缓存
        proxy_cache dca_cache;
        proxy_cache_valid 200 5m;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout invalid_header updating;

        # 代理到后端
        proxy_pass http://dca_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 仅对GET请求缓存
        proxy_cache_methods GET HEAD;
    }

    # 写入操作（不缓存）
    location /api/orders/create {
        limit_req zone=api_limit burst=10 nodelay;

        proxy_pass http://dca_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 管理API（IP限制）
    location /api/admin {
        allow 10.0.0.0/8;
        deny all;

        proxy_pass http://dca_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Prometheus指标
    location /metrics {
        allow 10.0.0.0/8;
        deny all;

        proxy_pass http://dca_backend/metrics;
    }
}

# 日志格式定义
log_format json_analytics escape=json '{'
    '"time_local":"$time_local",'
    '"remote_addr":"$remote_addr",'
    '"request":"$request",'
    '"status": "$status",'
    '"body_bytes_sent":"$body_bytes_sent",'
    '"request_time":"$request_time",'
    '"upstream_response_time":"$upstream_response_time",'
    '"upstream_addr":"$upstream_addr",'
    '"http_referrer":"$http_referer",'
    '"http_user_agent":"$http_user_agent"'
'}';

# 缓存配置
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=dca_cache:100m
                 max_size=1g inactive=60m use_temp_path=off;
```

---

## 4. 认证集成

### 4.1 JWT认证

```python
# ============================================
# auth/jwt_handler.py - JWT认证处理
# ============================================

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

class JWTHandler:
    """JWT认证处理器"""

    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def generate_token(self, user_id, role='user', expires_in=3600):
        """生成JWT令牌"""
        payload = {
            'user_id': str(user_id),
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token):
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def decode_token_without_verification(self, token):
        """仅解码不验证（用于获取header）"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except:
            return None


def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401

        try:
            scheme, token = auth_header.split(' ')
            if scheme.lower() != 'bearer':
                return jsonify({'error': 'Invalid authorization scheme'}), 401
        except ValueError:
            return jsonify({'error': 'Invalid authorization header format'}), 401

        jwt_handler = JWTHandler(current_app.config['JWT_SECRET_KEY'])
        payload = jwt_handler.verify_token(token)

        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # 设置用户上下文
        request.user_id = payload.get('user_id')
        request.user_role = payload.get('role')

        # 设置数据库上下文（用于RLS）
        from database import get_db_cursor
        with get_db_cursor() as cursor:
            cursor.execute("SELECT fn_set_user_context(%s)", (request.user_id,))

        return f(*args, **kwargs)

    return decorated_function


def require_role(role):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'user_role') or request.user_role != role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 4.2 API Key认证

```python
# ============================================
# auth/api_key_handler.py - API Key认证
# ============================================

import secrets
import hashlib
from datetime import datetime, timedelta
from database import get_db_cursor

class APIKeyHandler:
    """API Key处理器"""

    @staticmethod
    def generate_api_key():
        """生成新的API Key"""
        # 生成随机key
        api_key = 'dca_' + secrets.token_urlsafe(32)

        # 生成secret
        api_secret = secrets.token_urlsafe(64)

        # 哈希存储
        secret_hash = hashlib.sha256(api_secret.encode()).hexdigest()

        return api_key, api_secret, secret_hash

    @staticmethod
    def validate_api_key(api_key, api_secret):
        """验证API Key"""
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, client_name, permissions, expires_at
                FROM api_keys
                WHERE api_key = %s
                  AND secret_hash = %s
                  AND is_active = true
                  AND (expires_at IS NULL OR expires_at > NOW())
            """, (api_key, hashlib.sha256(api_secret.encode()).hexdigest()))

            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'client_name': result[1],
                    'permissions': result[2],
                    'expires_at': result[3]
                }
            return None

    @staticmethod
    def create_api_key(client_name, permissions, expires_days=365):
        """创建新的API Key"""
        api_key, api_secret, secret_hash = APIKeyHandler.generate_api_key()

        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO api_keys (api_key, secret_hash, client_name, permissions, expires_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                api_key,
                secret_hash,
                client_name,
                permissions,
                datetime.now() + timedelta(days=expires_days) if expires_days else None
            ))

        return {
            'api_key': api_key,
            'api_secret': api_secret,
            'client_name': client_name
        }


# API Key数据库表
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS api_keys (
    id BIGSERIAL PRIMARY KEY,
    api_key VARCHAR(100) UNIQUE NOT NULL,
    secret_hash VARCHAR(128) NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    permissions TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(api_key);
"""
```

---

**文档版本**: v1.0
**更新日期**: 2026-03-04
