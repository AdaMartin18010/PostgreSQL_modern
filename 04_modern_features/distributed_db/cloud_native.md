# 云原生与跨区域多活

> PostgreSQL 在云原生环境中的部署与多活架构实践

## 📋 目录

- [云原生与跨区域多活](#云原生与跨区域多活)
  - [📋 目录](#-目录)
  - [1. 云原生基础架构](#1-云原生基础架构)
    - [1.1 云原生原则](#11-云原生原则)
    - [1.2 云服务模式](#12-云服务模式)
  - [2. 容器化部署](#2-容器化部署)
    - [2.1 Docker 镜像构建](#21-docker-镜像构建)
    - [2.2 Docker Compose 配置](#22-docker-compose-配置)
  - [3. Kubernetes 编排](#3-kubernetes-编排)
    - [3.1 StatefulSet 部署](#31-statefulset-部署)
    - [3.2 Service 配置](#32-service-配置)
    - [3.3 持久卷配置](#33-持久卷配置)
  - [4. 跨可用区部署](#4-跨可用区部署)
    - [4.1 Pod 拓扑约束](#41-pod-拓扑约束)
    - [4.2 副本放置策略](#42-副本放置策略)
  - [5. 跨区域多活](#5-跨区域多活)
    - [5.1 读写分离架构](#51-读写分离架构)
    - [5.2 多区域复制](#52-多区域复制)
    - [5.3 冲突解决策略](#53-冲突解决策略)
  - [6. 灾难恢复](#6-灾难恢复)
    - [6.1 WAL 归档配置](#61-wal-归档配置)
    - [6.2 Point-in-Time Recovery](#62-point-in-time-recovery)
    - [6.3 备份策略](#63-备份策略)
  - [7. 云存储集成](#7-云存储集成)
    - [7.1 AWS S3 集成](#71-aws-s3-集成)
    - [7.2 Azure Blob Storage 集成](#72-azure-blob-storage-集成)
  - [8. 工程实践](#8-工程实践)
    - [8.1 资源配置建议](#81-资源配置建议)
    - [8.2 监控和告警](#82-监控和告警)
    - [8.3 安全最佳实践](#83-安全最佳实践)
  - [参考资源](#参考资源)

## 1. 云原生基础架构

### 1.1 云原生原则

**不可变基础设施**:

- 容器镜像不可变
- 配置通过环境变量或配置映射注入
- 状态分离，数据持久化到外部存储

**声明式配置**:

- 使用 YAML/JSON 定义期望状态
- Kubernetes 自动维护实际状态
- GitOps 流程管理配置变更

**微服务架构**:

- PostgreSQL 作为数据层服务
- 通过 Service 暴露统一访问接口
- 支持水平扩展和故障隔离

### 1.2 云服务模式

**IaaS（基础设施即服务）**:

- 自建 PostgreSQL 集群
- 完全控制配置和优化
- 需要自己管理运维

**PaaS（平台即服务）**:

- 使用云厂商托管 PostgreSQL
- 自动化备份、监控、高可用
- 简化运维，但灵活性降低

**DBaaS（数据库即服务）**:

- RDS、Aurora、Cloud SQL 等
- 完全托管，专注业务逻辑
- 成本可能较高

## 2. 容器化部署

### 2.1 Docker 镜像构建

```dockerfile
# 基于官方PostgreSQL 17镜像
FROM postgres:17

# 设置环境变量
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=mydb
ENV PGDATA=/var/lib/postgresql/data/pgdata

# 安装扩展
RUN apt-get update && apt-get install -y \
    postgresql-17-citus \
    postgresql-17-pgvector \
    && rm -rf /var/lib/apt/lists/*

# 复制初始化脚本
COPY init.sql /docker-entrypoint-initdb.d/

# 复制配置文件
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# 暴露端口
EXPOSE 5432

# 健康检查
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD pg_isready -U postgres || exit 1
```

### 2.2 Docker Compose 配置

```yaml
version: "3.8"

services:
  postgres-primary:
    image: postgres:17-citus
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: mydb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      postgres -c shared_preload_libraries=citus -c max_connections=200 -c shared_buffers=256MB -c
      effective_cache_size=1GB -c maintenance_work_mem=64MB -c checkpoint_completion_target=0.9 -c
      wal_buffers=16MB -c default_statistics_target=100 -c random_page_cost=1.1 -c
      effective_io_concurrency=200
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres-standby:
    image: postgres:17-citus
    environment:
      POSTGRES_PASSWORD: postgres
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres-standby-data:/var/lib/postgresql/data
    command: >
      bash -c " until pg_basebackup --pgdata=/var/lib/postgresql/data/pgdata -R
      --slot=replication_slot --host=postgres-primary --port=5432; do
        echo 'Waiting for primary to connect...'
        sleep 1s
      done echo 'Backup done, starting replica...' postgres "
    depends_on:
      - postgres-primary

volumes:
  postgres-data:
  postgres-standby-data:
```

## 3. Kubernetes 编排

### 3.1 StatefulSet 部署

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: database
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:17
          ports:
            - containerPort: 5432
              name: postgres
          env:
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: PGDATA
              value: /var/lib/postgresql/data/pgdata
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
            - name: config
              mountPath: /etc/postgresql
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
          livenessProbe:
            exec:
              command:
                - pg_isready
                - -U
                - postgres
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command:
                - pg_isready
                - -U
                - postgres
            initialDelaySeconds: 5
            periodSeconds: 5
      volumes:
        - name: config
          configMap:
            name: postgres-config
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-ssd
        resources:
          requests:
            storage: 100Gi
```

### 3.2 Service 配置

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-primary
  namespace: database
spec:
  selector:
    app: postgres
    role: primary
  ports:
    - port: 5432
      targetPort: 5432
  clusterIP: None # Headless service
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-replica
  namespace: database
spec:
  selector:
    app: postgres
    role: replica
  ports:
    - port: 5432
      targetPort: 5432
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-external
  namespace: database
spec:
  type: LoadBalancer
  selector:
    app: postgres
    role: primary
  ports:
    - port: 5432
      targetPort: 5432
```

### 3.3 持久卷配置

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: database
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

## 4. 跨可用区部署

### 4.1 Pod 拓扑约束

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  template:
    spec:
      # Pod反亲和性：不同Pod分布在不同节点
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values:
                      - postgres
              topologyKey: kubernetes.io/hostname
        # 节点亲和性：优先选择特定可用区
        nodeAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              preference:
                matchExpressions:
                  - key: topology.kubernetes.io/zone
                    operator: In
                    values:
                      - us-east-1a
                      - us-east-1b
                      - us-east-1c
      # 拓扑分布约束：确保副本均匀分布
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: postgres
```

### 4.2 副本放置策略

**同步复制配置**:

```sql
-- 配置同步备用服务器
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby1, standby2)';
SELECT pg_reload_conf();

-- 检查复制状态
SELECT application_name, state, sync_state, sync_priority
FROM pg_stat_replication;
```

## 5. 跨区域多活

### 5.1 读写分离架构

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-proxy-config
data:
  pgbouncer.ini: |
    [databases]
    mydb_write = host=postgres-primary port=5432 dbname=mydb
    mydb_read = host=postgres-replica port=5432 dbname=mydb

    [pgbouncer]
    listen_addr = 0.0.0.0
    listen_port = 6432
    auth_type = md5
    auth_file = /etc/pgbouncer/userlist.txt
    pool_mode = transaction
    max_client_conn = 1000
    default_pool_size = 25
```

### 5.2 多区域复制

**配置逻辑复制**:

```sql
-- 主区域（us-east-1）
CREATE PUBLICATION pub_multi_region FOR ALL TABLES;

-- 从区域（us-west-2）
CREATE SUBSCRIPTION sub_from_east
CONNECTION 'host=primary-us-east-1.example.com dbname=mydb user=replication'
PUBLICATION pub_multi_region
WITH (copy_data = true, create_slot = true);

-- 监控复制延迟
SELECT
    subscription_name,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), latest_end_lsn)) as lag,
    latest_end_time as last_msg_time,
    now() - latest_end_time as time_lag
FROM pg_stat_subscription;
```

### 5.3 冲突解决策略

```sql
-- 配置冲突解决
ALTER SUBSCRIPTION sub_from_east SET (disable_on_error = false);

-- 监控冲突
SELECT * FROM pg_stat_subscription_stats
WHERE subscription_name = 'sub_from_east';

-- 跳过冲突的事务
ALTER SUBSCRIPTION sub_from_east SKIP (lsn = '0/12345678');
```

## 6. 灾难恢复

### 6.1 WAL 归档配置

```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://my-pg-backup/wal/%f'
archive_timeout = 300  -- 5分钟

-- 连续归档到S3
restore_command = 'aws s3 cp s3://my-pg-backup/wal/%f %p'
```

### 6.2 Point-in-Time Recovery

```sql
-- recovery.conf (PostgreSQL 12+使用recovery.signal)
restore_command = 'aws s3 cp s3://my-pg-backup/wal/%f %p'
recovery_target_time = '2025-10-03 12:00:00'
recovery_target_action = 'promote'
```

### 6.3 备份策略

```bash
# 使用pg_basebackup进行基础备份
pg_basebackup -h primary.example.com -D /backup/base \
  -Ft -z -P --wal-method=stream

# 使用pg_dump进行逻辑备份
pg_dump -h primary.example.com -U postgres -Fc mydb > mydb_backup.dump

# 上传到S3
aws s3 cp /backup/base/base.tar.gz s3://my-pg-backup/base/$(date +%Y%m%d)/
```

## 7. 云存储集成

### 7.1 AWS S3 集成

```sql
-- 安装aws_s3扩展
CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;

-- 导出数据到S3
SELECT aws_s3.query_export_to_s3(
    'SELECT * FROM orders WHERE created_at > NOW() - INTERVAL ''1 day''',
    aws_commons.create_s3_uri('my-bucket', 'exports/orders.csv', 'us-east-1')
);

-- 从S3导入数据
SELECT aws_s3.table_import_from_s3(
    'orders',
    '',
    '(FORMAT CSV, HEADER true)',
    aws_commons.create_s3_uri('my-bucket', 'imports/orders.csv', 'us-east-1')
);
```

### 7.2 Azure Blob Storage 集成

```sql
-- 使用azure_storage扩展
CREATE EXTENSION IF NOT EXISTS azure_storage;

-- 配置Azure连接
CREATE SERVER azure_server
    FOREIGN DATA WRAPPER azure_storage_fdw
    OPTIONS (account 'myaccount', container 'mycontainer');
```

## 8. 工程实践

### 8.1 资源配置建议

**CPU 和内存**:

- 开发环境：2 CPU, 4GB 内存
- 生产环境：4-8 CPU, 16-32GB 内存
- 内存分配：shared_buffers = 25%内存，effective_cache_size = 75%内存

**存储**:

- 使用 SSD 存储（IOPS 3000+）
- 启用卷快照备份
- 监控存储使用率（告警阈值 80%）

### 8.2 监控和告警

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-postgres-exporter
data:
  queries.yaml: |
    pg_replication_lag:
      query: "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) as lag"
      metrics:
        - lag:
            usage: "GAUGE"
            description: "Replication lag behind primary in seconds"

    pg_database_size:
      query: "SELECT pg_database_size(current_database()) as size_bytes"
      metrics:
        - size_bytes:
            usage: "GAUGE"
            description: "Database size in bytes"
```

### 8.3 安全最佳实践

**网络安全**:

- 使用 VPC 隔离
- 配置安全组限制访问
- 启用 TLS/SSL 加密连接

**认证和授权**:

- 使用 IAM 角色认证
- 实施最小权限原则
- 定期轮换密码

**数据加密**:

- 启用静态加密（EBS 加密）
- 启用传输加密（SSL/TLS）
- 敏感数据列级加密

## 参考资源

- [Kubernetes
  StatefulSets](<https://kubernetes.io/docs/concepts/workloads/controllers/statefulset>/)
- [PostgreSQL 高可用](<https://www.postgresql.org/docs/current/high-availability.htm>l)
- [AWS RDS for PostgreSQL](<https://aws.amazon.com/rds/postgresql>/)
- [Cloud Native PostgreSQL](<https://cloudnative-pg.io>/)
