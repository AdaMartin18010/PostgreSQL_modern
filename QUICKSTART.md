# PostgreSQL 18 快速开始指南

5分钟快速部署并使用PostgreSQL 18！

---

## 🚀 快速部署（推荐）

### 方式1: Docker Compose（最简单）

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/PostgreSQL_modern.git
cd PostgreSQL_modern

# 2. 启动服务
make up

# 或者直接使用docker-compose
cd configs
docker-compose up -d

# 3. 验证部署
psql -h localhost -p 5432 -U postgres -c "SELECT version();"
```

**完成！** 您现在拥有：

- ✅ PostgreSQL 18数据库（端口5432）
- ✅ Prometheus监控（<http://localhost:9090）>
- ✅ Grafana仪表板（<http://localhost:3000）>
- ✅ 生产级配置

---

### 方式2: 直接安装

#### Ubuntu/Debian

```bash
# 添加PostgreSQL仓库
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# 安装PostgreSQL 18
sudo apt update
sudo apt install postgresql-18

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 连接数据库
sudo -u postgres psql
```

#### CentOS/RHEL

```bash
# 安装PostgreSQL仓库
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# 安装PostgreSQL 18
sudo yum install -y postgresql18-server

# 初始化数据库
sudo /usr/pgsql-18/bin/postgresql-18-setup initdb

# 启动服务
sudo systemctl start postgresql-18
sudo systemctl enable postgresql-18
```

#### macOS

```bash
# 使用Homebrew
brew install postgresql@18

# 启动服务
brew services start postgresql@18

# 连接数据库
psql postgres
```

---

## 🔧 基础配置

### 1. 创建数据库和用户

```sql
-- 连接PostgreSQL
psql -U postgres

-- 创建数据库
CREATE DATABASE myapp;

-- 创建用户
CREATE USER myapp_user WITH PASSWORD 'strong_password_here';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;

-- 退出
\q
```

### 2. 应用PostgreSQL 18优化配置

```bash
# 复制优化配置
sudo cp configs/postgresql-18-production.conf /etc/postgresql/18/main/postgresql.conf

# 根据硬件调整（可选）
sudo nano /etc/postgresql/18/main/postgresql.conf

# 重启应用配置
sudo systemctl restart postgresql
```

### 3. 启用PostgreSQL 18新特性

```sql
-- 连接数据库
psql -U postgres -d myapp

-- 启用异步I/O（性能+35%）
ALTER SYSTEM SET io_direct = 'data,wal';
ALTER SYSTEM SET io_combine_limit = '256kB';

-- 启用Skip Scan
ALTER SYSTEM SET enable_skip_scan = on;

-- 重载配置
SELECT pg_reload_conf();

-- 验证配置
SHOW io_direct;
SHOW enable_skip_scan;
```

---

## 📊 验证部署

### 1. 健康检查

```bash
# 使用我们的健康检查工具
python3 scripts/health-check-advanced.py --dbname myapp

# 或使用Makefile
make health PGDB=myapp
```

预期输出：

```
✓ PostgreSQL版本: PostgreSQL 18.x
✓ 异步I/O: data,wal
✓ Skip Scan优化: on
✓ 缓存命中率: 99.5%
✓ 连接数: 5/100 (5%)
```

### 2. 性能基准测试

```bash
# 运行pgbench基准测试
make benchmark

# 或手动执行
bash scripts/performance-benchmark.sh
```

---

## 🎯 第一个应用

### Python示例

```python
# app.py
import psycopg2

# 连接数据库
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="myapp",
    user="myapp_user",
    password="strong_password_here"
)

cursor = conn.cursor()

# 创建表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT now()
    );
""")

# 插入数据
cursor.execute(
    "INSERT INTO users (username, email) VALUES (%s, %s)",
    ('john_doe', 'john@example.com')
)

# 查询数据
cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()
print(users)

# 提交并关闭
conn.commit()
cursor.close()
conn.close()
```

运行：

```bash
python3 app.py
```

### Node.js示例

```javascript
// app.js
const { Client } = require('pg');

const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'myapp',
  user: 'myapp_user',
  password: 'strong_password_here'
});

async function main() {
  await client.connect();

  // 创建表
  await client.query(`
    CREATE TABLE IF NOT EXISTS products (
      id SERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      price NUMERIC(10, 2),
      created_at TIMESTAMPTZ DEFAULT now()
    );
  `);

  // 插入数据
  await client.query(
    'INSERT INTO products (name, price) VALUES ($1, $2)',
    ['Product A', 99.99]
  );

  // 查询数据
  const res = await client.query('SELECT * FROM products');
  console.log(res.rows);

  await client.end();
}

main().catch(console.error);
```

---

## 🛠️ 常用操作

### 连接数据库

```bash
# 本地连接
psql -U postgres -d myapp

# 远程连接
psql -h hostname -p 5432 -U myapp_user -d myapp

# 执行SQL文件
psql -U postgres -d myapp -f script.sql
```

### 备份和恢复

```bash
# 备份
pg_dump myapp > myapp_backup.sql

# 压缩备份
pg_dump myapp | gzip > myapp_backup.sql.gz

# 恢复
psql myapp < myapp_backup.sql

# 从压缩备份恢复
gunzip -c myapp_backup.sql.gz | psql myapp

# 使用Makefile
make backup PGDB=myapp
make restore PGDB=myapp BACKUP_FILE=backups/myapp_20241205.sql.gz
```

### 查看状态

```sql
-- 当前连接
SELECT * FROM pg_stat_activity;

-- 数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database;

-- 表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 缓存命中率
SELECT
    ROUND(SUM(blks_hit) * 100.0 / NULLIF(SUM(blks_hit + blks_read), 0), 2) AS cache_hit_ratio
FROM pg_stat_database;
```

---

## 🎓 下一步

### 学习资源

1. **基础教程**
   - [学习路径](LEARNING-PATH.md) - 系统学习指南
   - [快速参考](QUICK-REFERENCE.md) - 命令速查手册
   - [FAQ](FAQ.md) - 常见问题解答

2. **进阶主题**
   - [PostgreSQL 18新特性](docs/01-PostgreSQL18/40-PostgreSQL18新特性总结.md)
   - [性能优化](docs/01-PostgreSQL18/08-性能调优实战指南.md)
   - [最佳实践](BEST-PRACTICES.md)

3. **生产部署**
   - [高可用架构](docs/05-Production/07-Patroni高可用完整指南.md)
   - [监控告警](docs/05-Production/12-监控告警完整方案.md)
   - [生产检查清单](docs/05-Production/20-生产环境检查清单.md)

### 工具脚本

```bash
# 自动优化
python3 scripts/pg18-optimizer.py --dbname myapp --apply

# 智能VACUUM
python3 scripts/vacuum-scheduler.py --dbname myapp --auto

# 索引推荐
python3 scripts/index-advisor.py --dbname myapp

# 查询性能追踪
python3 scripts/query-performance-tracker.py --dbname myapp --analyze-slow
```

---

## 🆘 常见问题

### 连接被拒绝

```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 检查端口
sudo lsof -i:5432

# 检查配置
sudo cat /etc/postgresql/18/main/pg_hba.conf
```

### 权限错误

```sql
-- 检查用户权限
\du myapp_user

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE myapp TO myapp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myapp_user;
```

### 性能问题

```bash
# 运行健康检查
python3 scripts/health-check-advanced.py --dbname myapp

# 分析慢查询
python3 scripts/query-performance-tracker.py --dbname myapp --analyze-slow

# 检查表膨胀
python3 scripts/vacuum-scheduler.py --dbname myapp --dry-run
```

---

## 📞 获取帮助

- 📖 [完整文档](docs/)
- 🔍 [FAQ](FAQ.md)
- 💬 [提问](../../issues)
- 🌟 [项目主页](README.md)

---

**恭喜！您已成功部署PostgreSQL 18！** 🎉

现在开始构建您的应用吧！
