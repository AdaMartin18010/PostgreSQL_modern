# PostgreSQL 18 最佳实践指南

全面的PostgreSQL生产环境最佳实践，涵盖开发、运维、安全等各个方面。

---

## 🗂️ 目录

- [PostgreSQL 18 最佳实践指南](#postgresql-18-最佳实践指南)
  - [🗂️ 目录](#️-目录)
  - [数据库设计](#数据库设计)
    - [✅ 推荐做法](#-推荐做法)
      - [1. 命名规范](#1-命名规范)
      - [2. 数据类型选择](#2-数据类型选择)
      - [3. 主键策略](#3-主键策略)
      - [4. 外键约束](#4-外键约束)
    - [❌ 避免的做法](#-避免的做法)
  - [SQL编写](#sql编写)
    - [✅ 推荐做法](#-推荐做法-1)
      - [1. 参数化查询](#1-参数化查询)
      - [2. 使用LIMIT](#2-使用limit)
      - [3. 避免SELECT \*](#3-避免select-)
      - [4. 使用EXISTS代替COUNT](#4-使用exists代替count)
      - [5. 批量操作](#5-批量操作)
  - [索引策略](#索引策略)
    - [✅ 推荐做法](#-推荐做法-2)
      - [1. 为WHERE条件创建索引](#1-为where条件创建索引)
      - [2. 为外键创建索引](#2-为外键创建索引)
      - [3. 组合索引顺序](#3-组合索引顺序)
      - [4. 部分索引](#4-部分索引)
      - [5. 表达式索引](#5-表达式索引)
    - [❌ 避免的做法](#-避免的做法-1)
  - [性能优化](#性能优化)
    - [✅ 推荐做法](#-推荐做法-3)
      - [1. 定期VACUUM](#1-定期vacuum)
      - [2. 定期ANALYZE](#2-定期analyze)
      - [3. 使用连接池](#3-使用连接池)
      - [4. 配置合适的work\_mem](#4-配置合适的work_mem)
      - [5. PostgreSQL 18特性](#5-postgresql-18特性)
  - [安全加固](#安全加固)
    - [✅ 推荐做法](#-推荐做法-4)
      - [1. 强密码策略](#1-强密码策略)
      - [2. 最小权限原则](#2-最小权限原则)
      - [3. 限制网络访问](#3-限制网络访问)
      - [4. SSL加密](#4-ssl加密)
      - [5. 审计日志](#5-审计日志)
  - [备份恢复](#备份恢复)
    - [✅ 推荐做法](#-推荐做法-5)
      - [1. 自动化备份](#1-自动化备份)
      - [2. 测试恢复](#2-测试恢复)
      - [3. 异地备份](#3-异地备份)
      - [4. PITR配置](#4-pitr配置)
  - [监控告警](#监控告警)
    - [✅ 推荐做法](#-推荐做法-6)
      - [1. 关键指标监控](#1-关键指标监控)
      - [2. 告警分级](#2-告警分级)
      - [3. 自动化处理](#3-自动化处理)
  - [运维管理](#运维管理)
    - [✅ 推荐做法](#-推荐做法-7)
      - [1. 变更管理](#1-变更管理)
      - [2. 文档化](#2-文档化)
      - [3. 定期维护](#3-定期维护)
  - [📋 检查清单](#-检查清单)
    - [部署前检查](#部署前检查)
    - [日常运维检查](#日常运维检查)
  - [参考资料](#参考资料)

---

## 数据库设计

### ✅ 推荐做法

#### 1. 命名规范

```sql
-- 表名：小写+下划线，单数形式
users, orders, order_items

-- 列名：小写+下划线，有意义的名称
user_id, created_at, is_active

-- 索引命名：idx_表名_列名
CREATE INDEX idx_users_email ON users(email);

-- 外键命名：fk_表名_列名
ALTER TABLE orders ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES users(id);

-- 约束命名：chk_表名_描述
ALTER TABLE products ADD CONSTRAINT chk_products_price
    CHECK (price > 0);
```

#### 2. 数据类型选择

```sql
-- ✅ 正确选择
id BIGSERIAL PRIMARY KEY             -- 大表用BIGINT
username VARCHAR(50)                 -- 合理长度
email VARCHAR(255)                   -- 标准邮箱长度
amount NUMERIC(10, 2)                -- 精确金额
is_active BOOLEAN                    -- 布尔值
created_at TIMESTAMPTZ               -- 带时区

-- ❌ 避免
id SERIAL                            -- 大表会溢出
username TEXT                        -- 无限制
email CHAR(255)                      -- 浪费空间
amount REAL                          -- 金额不精确
is_active CHAR(1)                    -- 浪费空间
created_at TIMESTAMP                 -- 无时区信息
```

#### 3. 主键策略

```sql
-- ✅ 推荐：BIGSERIAL
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

-- ✅ PostgreSQL 18: UUIDv7（时间排序）
CREATE TABLE logs (
    id UUID DEFAULT gen_uuid_v7() PRIMARY KEY,
    data JSONB
);

-- ❌ 避免：业务字段作主键
-- 业务规则可能变化
CREATE TABLE users (
    email VARCHAR(255) PRIMARY KEY  -- ❌
);
```

#### 4. 外键约束

```sql
-- ✅ 推荐：明确级联行为
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE RESTRICT         -- 防止意外删除
        ON UPDATE CASCADE
);

-- ⚠️  谨慎使用CASCADE
-- CASCADE可能导致大量数据被删除
FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE  -- 用户删除时，订单也删除
```

### ❌ 避免的做法

```sql
-- ❌ 存储JSON字符串
data TEXT  -- 存储 '{"key": "value"}'

-- ✅ 使用JSONB
data JSONB

-- ❌ 不使用约束
CREATE TABLE orders (
    user_id INT  -- 无外键约束
);

-- ✅ 使用约束
CREATE TABLE orders (
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ❌ 过度规范化
-- 导致JOIN过多

-- ❌ 过度反规范化
-- 导致数据冗余和一致性问题
```

---

## SQL编写

### ✅ 推荐做法

#### 1. 参数化查询

```python
# ✅ 正确：防止SQL注入
cursor.execute(
    "SELECT * FROM users WHERE username = %s",
    (username,)
)

# ❌ 危险：SQL注入
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

#### 2. 使用LIMIT

```sql
-- ✅ 限制返回行数
SELECT * FROM users ORDER BY created_at DESC LIMIT 100;

-- ❌ 返回所有行
SELECT * FROM users ORDER BY created_at DESC;
```

#### 3. 避免SELECT *

```sql
-- ✅ 只选择需要的列
SELECT id, username, email FROM users;

-- ❌ 选择所有列（浪费资源）
SELECT * FROM users;
```

#### 4. 使用EXISTS代替COUNT

```sql
-- ✅ 快速检查存在性
SELECT EXISTS(SELECT 1 FROM users WHERE email = 'test@example.com');

-- ❌ 慢（扫描所有行）
SELECT COUNT(*) FROM users WHERE email = 'test@example.com';
```

#### 5. 批量操作

```sql
-- ✅ 批量INSERT
INSERT INTO users (username, email) VALUES
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com'),
    ('user3', 'user3@example.com');

-- ❌ 逐条INSERT
INSERT INTO users (username, email) VALUES ('user1', 'user1@example.com');
INSERT INTO users (username, email) VALUES ('user2', 'user2@example.com');
INSERT INTO users (username, email) VALUES ('user3', 'user3@example.com');

-- ✅ 批量UPDATE
UPDATE products p
SET price = v.new_price
FROM (VALUES
    (1, 99.99),
    (2, 149.99),
    (3, 199.99)
) AS v(product_id, new_price)
WHERE p.product_id = v.product_id;
```

---

## 索引策略

### ✅ 推荐做法

#### 1. 为WHERE条件创建索引

```sql
-- 高频查询
SELECT * FROM users WHERE email = 'test@example.com';

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
```

#### 2. 为外键创建索引

```sql
-- PostgreSQL不会自动为外键创建索引
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ✅ 手动创建索引
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

#### 3. 组合索引顺序

```sql
-- ✅ 高选择性列在前
CREATE INDEX idx_users_status_created ON users(status, created_at);
-- 查询: WHERE status = 'active' AND created_at > '2024-01-01'

-- ❌ 低选择性列在前
CREATE INDEX idx_users_created_status ON users(created_at, status);
```

#### 4. 部分索引

```sql
-- ✅ 只索引活跃用户
CREATE INDEX idx_active_users_email ON users(email)
WHERE status = 'active';

-- 节省索引空间，提升性能
```

#### 5. 表达式索引

```sql
-- 查询使用LOWER
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- ✅ 创建表达式索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

### ❌ 避免的做法

```sql
-- ❌ 为所有列创建索引
-- 索引有维护成本

-- ❌ 创建冗余索引
CREATE INDEX idx1 ON users(email);
CREATE INDEX idx2 ON users(email, username);  -- 冗余

-- ❌ 在小表上创建索引
-- 表<1000行时，索引可能比全表扫描慢
```

---

## 性能优化

### ✅ 推荐做法

#### 1. 定期VACUUM

```sql
-- ✅ 定期VACUUM
VACUUM ANALYZE users;

-- 配置autovacuum（默认启用）
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_naptime = '1min';
```

#### 2. 定期ANALYZE

```sql
-- ✅ 保持统计信息最新
ANALYZE users;

-- 大规模数据变更后
INSERT INTO users SELECT * FROM temp_users;
ANALYZE users;  -- 立即更新统计
```

#### 3. 使用连接池

```python
# ✅ 使用连接池
from psycopg2.pool import SimpleConnectionPool

pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    host='localhost',
    database='mydb'
)

conn = pool.getconn()
# ... 使用连接 ...
pool.putconn(conn)

# 或使用pgBouncer
```

#### 4. 配置合适的work_mem

```sql
-- ✅ 临时增加复杂查询的work_mem
SET work_mem = '256MB';
-- 执行复杂查询
SET work_mem = '64MB';  -- 恢复默认值

-- ❌ 全局设置过大的work_mem
-- work_mem * max_connections 可能超过内存
```

#### 5. PostgreSQL 18特性

```sql
-- ✅ 启用异步I/O（性能+35%）
ALTER SYSTEM SET io_direct = 'data,wal';

-- ✅ 启用Skip Scan
ALTER SYSTEM SET enable_skip_scan = on;

SELECT pg_reload_conf();
```

---

## 安全加固

### ✅ 推荐做法

#### 1. 强密码策略

```sql
-- ✅ 使用scram-sha-256
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- ✅ 强密码
CREATE USER app_user WITH PASSWORD 'X7$mK9@pL2!nQ4&vR8';

-- ❌ 弱密码
CREATE USER app_user WITH PASSWORD 'password123';
```

#### 2. 最小权限原则

```sql
-- ✅ 只授予必要权限
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO app_user;

-- ❌ 授予超级用户权限
CREATE USER app_user WITH SUPERUSER;
```

#### 3. 限制网络访问

```conf
# pg_hba.conf

# ✅ 限制IP范围
hostssl  all  all  10.0.1.0/24  scram-sha-256

# ❌ 允许所有IP
host  all  all  0.0.0.0/0  trust
```

#### 4. SSL加密

```sql
-- ✅ 强制SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_prefer_server_ciphers = on;

# pg_hba.conf
hostssl  all  all  0.0.0.0/0  scram-sha-256
```

#### 5. 审计日志

```sql
-- ✅ 记录所有DDL
ALTER SYSTEM SET log_statement = 'ddl';

-- 记录慢查询
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1秒

-- 记录连接
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
```

---

## 备份恢复

### ✅ 推荐做法

#### 1. 自动化备份

```bash
# ✅ 定时备份（crontab）
0 2 * * * pg_dump mydb | gzip > /backup/mydb_$(date +\%Y\%m\%d).sql.gz

# ✅ 使用专业工具
pgbackrest backup --stanza=main --type=full
```

#### 2. 测试恢复

```bash
# ✅ 定期测试恢复流程
# 每月至少一次

# 1. 恢复到测试环境
pg_restore -d test_db backup.dump

# 2. 验证数据完整性
psql test_db -c "SELECT COUNT(*) FROM users;"

# 3. 记录恢复时间
```

#### 3. 异地备份

```bash
# ✅ 备份到多个位置
# - 本地存储
# - 云存储（S3/OSS）
# - 异地数据中心
```

#### 4. PITR配置

```sql
-- ✅ 启用WAL归档
ALTER SYSTEM SET archive_mode = on;
ALTER SYSTEM SET archive_command = 'cp %p /backup/wal/%f';
```

---

## 监控告警

### ✅ 推荐做法

#### 1. 关键指标监控

```yaml
监控指标:
  - 连接数使用率 (>80%告警)
  - 缓存命中率 (<95%告警)
  - TPS
  - 平均查询时间
  - 锁等待
  - 复制延迟
  - 磁盘空间 (<20%告警)
  - CPU使用率
  - 内存使用率
```

#### 2. 告警分级

```yaml
严重(Critical): 5分钟内响应
  - PostgreSQL宕机
  - 复制断开
  - 磁盘满

警告(Warning): 30分钟内响应
  - 缓存命中率低
  - 连接数高
  - 长事务

信息(Info): 关注即可
  - 性能趋势
  - 资源使用
```

#### 3. 自动化处理

```bash
# ✅ 自动重启（谨慎）
if ! pg_isready; then
    systemctl restart postgresql
    send_alert "PostgreSQL自动重启"
fi

# ✅ 自动清理
python3 vacuum-scheduler.py --auto
```

---

## 运维管理

### ✅ 推荐做法

#### 1. 变更管理

```text
✅ 变更流程:
1. 在开发环境测试
2. 在测试环境验证
3. 准备回滚方案
4. 在维护窗口执行
5. 监控执行结果
6. 记录变更日志
```

#### 2. 文档化

```text
✅ 必需文档:
- 架构文档
- 配置清单
- 备份策略
- 恢复流程
- 应急预案
- 联系人列表
- 变更记录
```

#### 3. 定期维护

```bash
# ✅ 每日
- 检查备份状态
- 查看告警
- 检查慢查询日志

# ✅ 每周
- VACUUM重要表
- 检查索引
- 查看统计信息

# ✅ 每月
- 测试恢复
- 审查权限
- 更新文档
- 容量规划

# ✅ 每季度
- 灾难恢复演练
- 性能基准测试
- 安全审计
```

---

## 📋 检查清单

### 部署前检查

```text
□ 硬件配置满足要求
□ 操作系统配置优化
□ PostgreSQL配置优化
□ 数据库设计评审
□ 索引策略合理
□ 安全配置完成
□ 备份策略配置
□ 监控告警配置
□ 文档编写完成
□ 灾难恢复计划
```

### 日常运维检查

```text
□ 备份正常完成
□ 无严重告警
□ 连接数正常
□ 缓存命中率正常
□ 无锁等待
□ 复制延迟正常
□ 磁盘空间充足
□ 慢查询在可控范围
```

---

## 参考资料

- [PostgreSQL 18新特性](docs/01-PostgreSQL18/40-PostgreSQL18新特性总结.md)
- [性能调优指南](docs/01-PostgreSQL18/08-性能调优实战指南.md)
- [安全加固指南](docs/05-Production/10-安全加固完整指南.md)
- [生产环境检查清单](docs/05-Production/20-生产环境检查清单.md)

---

**持续改进**: 最佳实践随PostgreSQL版本演进而更新，请定期复习。
