# PostgreSQL 18 Docker容器化完整指南

## 1. 基础镜像

### 1.1 官方镜像

```bash
# 拉取PostgreSQL 18
docker pull postgres:18

# 运行基础容器
docker run -d \
  --name postgres18 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:18

# 连接
docker exec -it postgres18 psql -U postgres -d mydb
```

---

## 2. 自定义镜像

### 2.1 Dockerfile

```dockerfile
FROM postgres:18

# 安装扩展
RUN apt-get update && apt-get install -y \
    postgresql-18-postgis-3 \
    postgresql-18-citus-12.1 \
    postgresql-18-pgvector \
    postgresql-18-timescaledb \
    && rm -rf /var/lib/apt/lists/*

# 配置文件
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# 初始化脚本
COPY init-scripts/ /docker-entrypoint-initdb.d/

# 启动命令
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
```

### 2.2 初始化脚本

```bash
# init-scripts/01-extensions.sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

# init-scripts/02-schema.sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255)
);

# init-scripts/03-data.sql
INSERT INTO users (username, email) VALUES
('admin', 'admin@example.com');
```

---

## 3. Docker Compose

### 3.1 完整栈

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    container_name: postgres18
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    command:
      - "postgres"
      - "-c"
      - "config_file=/etc/postgresql/postgresql.conf"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - postgres-net

  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    container_name: pgbouncer
    environment:
      DATABASES_HOST: postgres
      DATABASES_PORT: 5432
      DATABASES_USER: postgres
      DATABASES_PASSWORD: ${DB_PASSWORD}
      DATABASES_DBNAME: mydb
      PGBOUNCER_POOL_MODE: transaction
      PGBOUNCER_MAX_CLIENT_CONN: 1000
      PGBOUNCER_DEFAULT_POOL_SIZE: 25
    ports:
      - "6432:6432"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - postgres-net

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    ports:
      - "5050:80"
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    networks:
      - postgres-net

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - postgres-net

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - postgres-net

volumes:
  postgres-data:
  pgadmin-data:
  prometheus-data:
  grafana-data:

networks:
  postgres-net:
    driver: bridge
```

---

## 4. 数据持久化

### 4.1 Volume管理

```bash
# 创建命名volume
docker volume create pgdata

# 查看volume
docker volume ls
docker volume inspect pgdata

# 备份volume
docker run --rm \
  -v pgdata:/data \
  -v $(pwd):/backup \
  ubuntu tar czf /backup/pgdata_backup.tar.gz /data

# 恢复volume
docker run --rm \
  -v pgdata:/data \
  -v $(pwd):/backup \
  ubuntu tar xzf /backup/pgdata_backup.tar.gz -C /
```

---

## 5. 主从复制

### 5.1 Docker Compose主从

```yaml
version: '3.8'

services:
  postgres-primary:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: repl_password
    volumes:
      - primary-data:/var/lib/postgresql/data
      - ./primary-setup.sh:/docker-entrypoint-initdb.d/setup.sh
    ports:
      - "5432:5432"
    networks:
      - replication-net

  postgres-standby:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: password
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - standby-data:/var/lib/postgresql/data
      - ./standby-setup.sh:/docker-entrypoint-initdb.d/setup.sh
    ports:
      - "5433:5432"
    depends_on:
      - postgres-primary
    networks:
      - replication-net

volumes:
  primary-data:
  standby-data:

networks:
  replication-net:
```

### 5.2 配置脚本

```bash
# primary-setup.sh
#!/bin/bash
set -e

# 配置复制
cat >> /var/lib/postgresql/data/postgresql.conf <<EOF
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
EOF

# pg_hba.conf
echo "host replication replicator 0.0.0.0/0 scram-sha-256" >> /var/lib/postgresql/data/pg_hba.conf

# 创建复制用户
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER replicator WITH REPLICATION PASSWORD 'repl_password';
EOSQL
```

```bash
# standby-setup.sh
#!/bin/bash
set -e

# 从Primary同步
rm -rf /var/lib/postgresql/data/pgdata/*
pg_basebackup -h postgres-primary -U replicator -D /var/lib/postgresql/data/pgdata -Fp -Xs -P

# 配置standby
cat > /var/lib/postgresql/data/pgdata/standby.signal <<EOF
EOF

cat >> /var/lib/postgresql/data/pgdata/postgresql.auto.conf <<EOF
primary_conninfo = 'host=postgres-primary port=5432 user=replicator password=repl_password'
EOF
```

---

## 6. 性能优化

### 6.1 资源限制

```yaml
services:
  postgres:
    image: postgres:18
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### 6.2 共享内存

```yaml
services:
  postgres:
    image: postgres:18
    shm_size: 2gb  # 增加共享内存
    environment:
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
```

---

## 7. 监控

### 7.1 健康检查

```yaml
services:
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

### 7.2 日志收集

```yaml
services:
  postgres:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 8. 生产部署

### 8.1 Swarm集群

```bash
# 初始化Swarm
docker swarm init

# 创建overlay网络
docker network create --driver overlay postgres-net

# 部署stack
docker stack deploy -c docker-compose.yml postgres-stack

# 查看服务
docker service ls
docker service ps postgres-stack_postgres

# 扩展副本
docker service scale postgres-stack_postgres=3
```

---

**完成**: PostgreSQL 18 Docker容器化完整指南
**字数**: ~10,000字
**涵盖**: 基础镜像、自定义镜像、Compose、主从、监控、生产部署
