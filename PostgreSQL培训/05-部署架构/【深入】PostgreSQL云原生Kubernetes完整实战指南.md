# 【深入】PostgreSQL云原生Kubernetes完整实战指南

> **创建时间**: 2025年1月
> **技术版本**: Kubernetes 1.28+, PostgreSQL 17+/18+
> **难度等级**: ⭐⭐⭐⭐⭐ 专家级
> **预计学习时间**: 2-3周

---

## 📑 目录

- [1. Kubernetes基础](#1-kubernetes基础)
- [2. StatefulSet详解](#2-statefulset详解)
- [3. PostgreSQL Operator](#3-postgresql-operator)
- [4. 存储管理（PV/PVC）](#4-存储管理pvpvc)
- [5. 配置管理（ConfigMap/Secret）](#5-配置管理configmapsecret)
- [6. 高可用架构](#6-高可用架构)
- [7. 监控和日志](#7-监控和日志)
- [8. 备份和恢复](#8-备份和恢复)
- [9. 完整生产案例](#9-完整生产案例)

---

## 1. Kubernetes基础

### 1.1 为什么选择Kubernetes运行PostgreSQL

**优势**：

| 优势 | 说明 | 价值 |
|------|------|------|
| **自动化运维** | 自动故障转移、自动扩缩容 | 降低运维成本60% |
| **资源隔离** | CPU、内存限制，多租户 | 提高资源利用率40% |
| **声明式配置** | YAML配置，GitOps | 配置管理效率+80% |
| **可移植性** | 多云、混合云部署 | 避免厂商锁定 |
| **微服务集成** | 与应用统一管理 | 简化架构 |

**挑战**：

- 🔴 **数据持久化**：需要正确配置PV/PVC
- 🔴 **性能优化**：需要调优CPU/内存/存储
- 🔴 **复杂性**：学习曲线陡峭

### 1.2 快速开始（30分钟）

```yaml
# postgres-simple.yaml - 最简单的部署（单实例）
apiVersion: v1
kind: Namespace
metadata:
  name: postgres-demo
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: postgres-demo
type: Opaque
stringData:
  password: "your-secure-password-here"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  namespace: postgres-demo
data:
  POSTGRES_DB: "demodb"
  POSTGRES_USER: "demouser"
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: postgres-demo
spec:
  serviceName: postgres
  replicas: 1
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
        envFrom:
        - configMapRef:
            name: postgres-config
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "500m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: postgres-demo
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  clusterIP: None  # Headless Service
```

**部署**：

```bash
# 应用配置
kubectl apply -f postgres-simple.yaml

# 查看状态
kubectl get all -n postgres-demo
kubectl get pvc -n postgres-demo

# 连接测试
kubectl exec -it postgres-0 -n postgres-demo -- psql -U demouser -d demodb

# 端口转发（本地连接）
kubectl port-forward -n postgres-demo postgres-0 5432:5432

# 本地连接
psql -h localhost -U demouser -d demodb
```

---

## 2. StatefulSet详解

### 2.1 StatefulSet vs Deployment

| 特性 | StatefulSet | Deployment |
|------|------------|-----------|
| **Pod名称** | 固定（postgres-0, postgres-1） | 随机 |
| **网络标识** | 固定（postgres-0.postgres） | 不固定 |
| **存储** | 每个Pod独立PVC | 共享PVC或无状态 |
| **启动顺序** | 顺序启动（0→1→2） | 并行启动 |
| **更新策略** | 滚动更新（逆序） | 滚动更新 |
| **适用** | 有状态应用（数据库） | 无状态应用（Web） |

### 2.2 StatefulSet完整配置

```yaml
# postgres-statefulset.yaml - 生产级配置
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: postgres
spec:
  serviceName: postgres
  replicas: 3  # 1主2从
  selector:
    matchLabels:
      app: postgres
      cluster: postgres-ha

  # 更新策略
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0  # 从最后一个Pod开始更新

  # Pod管理策略
  podManagementPolicy: OrderedReady  # 或Parallel

  template:
    metadata:
      labels:
        app: postgres
        cluster: postgres-ha
    spec:
      # 反亲和性（不同节点）
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

      # 初始化容器
      initContainers:
      - name: init-permissions
        image: busybox
        command:
        - sh
        - -c
        - |
          chown -R 999:999 /var/lib/postgresql/data
          chmod 700 /var/lib/postgresql/data
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data

      containers:
      - name: postgres
        image: postgres:17-alpine
        ports:
        - containerPort: 5432
          name: postgres

        # 环境变量
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP

        # 启动命令
        command:
        - sh
        - -c
        - |
          # 判断是主节点还是从节点
          if [ "$HOSTNAME" = "postgres-0" ]; then
            # 主节点配置
            echo "Starting as primary"
            export POSTGRES_INITDB_ARGS="--data-checksums --encoding=UTF8"
          else
            # 从节点配置（使用pg_basebackup）
            echo "Starting as replica"
            # 等待主节点就绪
            until pg_isready -h postgres-0.postgres; do sleep 1; done
            # 从主节点复制数据
            pg_basebackup -h postgres-0.postgres -D $PGDATA -U replication -v -P -X stream
          fi
          # 启动PostgreSQL
          exec docker-entrypoint.sh postgres

        # 存活探针
        livenessProbe:
          exec:
            command:
            - sh
            - -c
            - pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        # 就绪探针
        readinessProbe:
          exec:
            command:
            - sh
            - -c
            - pg_isready -U $POSTGRES_USER -d $POSTGRES_DB && psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1"
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 1

        # 资源配置
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

        # 存储挂载
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        - name: postgres-config
          mountPath: /etc/postgresql/postgresql.conf
          subPath: postgresql.conf
        - name: postgres-hba
          mountPath: /etc/postgresql/pg_hba.conf
          subPath: pg_hba.conf

      # 配置卷
      volumes:
      - name: postgres-config
        configMap:
          name: postgres-config-files
      - name: postgres-hba
        configMap:
          name: postgres-hba-config

  # 存储声明模板
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd  # 使用SSD存储类
      resources:
        requests:
          storage: 100Gi
```

---

## 3. PostgreSQL Operator

### 3.1 Operator模式

**什么是Operator**：

Operator是Kubernetes的扩展，使用自定义资源（CRD）和控制器，实现复杂应用的自动化运维。

**流行的PostgreSQL Operator**：

| Operator | 开发者 | 特性 | 成熟度 |
|----------|--------|------|--------|
| **Zalando Postgres Operator** | Zalando | 高可用、备份、监控 | ⭐⭐⭐⭐⭐ |
| **Crunchy PostgreSQL Operator** | Crunchy Data | 企业级、PGO 5+ | ⭐⭐⭐⭐⭐ |
| **CloudNativePG** | EDB | 云原生、简洁 | ⭐⭐⭐⭐⭐ |
| **KubeDB** | AppsCode | 多数据库支持 | ⭐⭐⭐⭐ |

### 3.2 Zalando Postgres Operator

**安装**：

```bash
# 添加Helm仓库
helm repo add postgres-operator-charts https://opensource.zalando.com/postgres-operator/charts/postgres-operator
helm repo update

# 安装Operator
helm install postgres-operator postgres-operator-charts/postgres-operator \
    --namespace postgres-operator \
    --create-namespace

# 安装UI（可选）
helm install postgres-operator-ui postgres-operator-charts/postgres-operator-ui \
    --namespace postgres-operator
```

**创建集群**：

```yaml
# postgres-cluster.yaml
apiVersion: "acid.zalan.do/v1"
kind: postgresql
metadata:
  name: postgres-cluster
  namespace: default
spec:
  teamId: "myteam"
  volume:
    size: 100Gi
    storageClass: fast-ssd
  numberOfInstances: 3  # 1主2从

  users:
    app_user:
    - superuser
    - createdb

  databases:
    app_db: app_user

  postgresql:
    version: "17"
    parameters:
      shared_buffers: "1GB"
      max_connections: "200"
      work_mem: "16MB"
      maintenance_work_mem: "512MB"
      effective_cache_size: "4GB"
      wal_level: "replica"
      max_wal_senders: "10"
      max_replication_slots: "10"

  resources:
    requests:
      cpu: "2000m"
      memory: "4Gi"
    limits:
      cpu: "4000m"
      memory: "8Gi"

  # 高可用配置
  patroni:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 33554432  # 32MB
    synchronous_mode: true
    synchronous_mode_strict: false

  # 连接池
  enableConnectionPooler: true
  connectionPooler:
    numberOfInstances: 2
    mode: "transaction"
    parameters:
      max_client_conn: "1000"
      default_pool_size: "25"
```

**部署和管理**：

```bash
# 部署集群
kubectl apply -f postgres-cluster.yaml

# 查看集群状态
kubectl get postgresql
kubectl describe postgresql postgres-cluster

# 查看Pod
kubectl get pods -l cluster-name=postgres-cluster

# 连接到主库
kubectl exec -it postgres-cluster-0 -- psql -U postgres

# 查看复制状态
kubectl exec -it postgres-cluster-0 -- patronictl list

# 手动故障切换
kubectl exec -it postgres-cluster-0 -- patronictl switchover

# 扩容/缩容
kubectl patch postgresql postgres-cluster --type='json' \
  -p='[{"op": "replace", "path": "/spec/numberOfInstances", "value": 5}]'

# 升级PostgreSQL版本
kubectl patch postgresql postgres-cluster --type='json' \
  -p='[{"op": "replace", "path": "/spec/postgresql/version", "value": "18"}]'
```

### 3.3 CloudNativePG Operator

**安装**：

```bash
# 安装CloudNativePG Operator
kubectl apply -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.22/releases/cnpg-1.22.0.yaml

# 验证
kubectl get deployment -n cnpg-system
```

**创建集群**：

```yaml
# cnpg-cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cnpg
spec:
  instances: 3
  imageName: ghcr.io/cloudnative-pg/postgresql:17

  bootstrap:
    initdb:
      database: app_db
      owner: app_user
      dataChecksums: true
      encoding: UTF8

  storage:
    storageClass: fast-ssd
    size: 100Gi

  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"

  postgresql:
    parameters:
      shared_buffers: "1GB"
      max_connections: "200"
      work_mem: "16MB"
      max_parallel_workers: "8"
      max_wal_size: "2GB"
      min_wal_size: "1GB"

  # 备份配置
  backup:
    barmanObjectStore:
      destinationPath: s3://my-backups/postgres-cnpg/
      s3Credentials:
        accessKeyId:
          name: aws-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: aws-creds
          key: SECRET_ACCESS_KEY
      wal:
        compression: gzip
      data:
        compression: gzip
    retentionPolicy: "30d"

  # 监控
  monitoring:
    enablePodMonitor: true
```

---

## 4. 存储管理（PV/PVC）

### 4.1 存储类（StorageClass）

```yaml
# storage-class-ssd.yaml - 本地SSD存储
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
# 创建本地PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv-0
spec:
  capacity:
    storage: 100Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  local:
    path: /mnt/disks/ssd0
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node1
---
# storage-class-ebs.yaml - AWS EBS存储
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3-encrypted
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
  kmsKeyId: "arn:aws:kms:us-west-2:111122223333:key/..."
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### 4.2 PVC扩容

```bash
# 查看PVC
kubectl get pvc -n postgres

# 编辑PVC（扩容到200Gi）
kubectl edit pvc postgres-storage-postgres-0 -n postgres

# 或使用patch
kubectl patch pvc postgres-storage-postgres-0 -n postgres \
  -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 触发扩容（需要重启Pod）
kubectl delete pod postgres-0 -n postgres

# 验证
kubectl exec -it postgres-0 -n postgres -- df -h /var/lib/postgresql/data
```

### 4.3 存储性能优化

```yaml
# 使用本地NVMe SSD
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-nvme
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
---
# 或使用CSI驱动的高性能存储
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ultra-ssd
provisioner: disk.csi.azure.com
parameters:
  skuname: UltraSSD_LRS
  cachingMode: None
  diskIOPSReadWrite: "50000"
  diskMBpsReadWrite: "1000"
```

---

## 5. 配置管理（ConfigMap/Secret）

### 5.1 PostgreSQL配置（ConfigMap）

```yaml
# postgres-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config-files
  namespace: postgres
data:
  postgresql.conf: |
    # 连接配置
    listen_addresses = '*'
    max_connections = 200
    superuser_reserved_connections = 3

    # 内存配置
    shared_buffers = 2GB
    effective_cache_size = 8GB
    work_mem = 32MB
    maintenance_work_mem = 512MB

    # WAL配置
    wal_level = replica
    wal_log_hints = on
    max_wal_senders = 10
    max_replication_slots = 10
    wal_keep_size = 1GB

    # 检查点配置
    checkpoint_timeout = 15min
    max_wal_size = 4GB
    min_wal_size = 1GB
    checkpoint_completion_target = 0.9

    # 查询优化
    random_page_cost = 1.1
    effective_io_concurrency = 200

    # 并行查询
    max_parallel_workers_per_gather = 4
    max_parallel_workers = 8
    max_worker_processes = 8

    # 日志配置
    logging_collector = on
    log_destination = 'stderr'
    log_directory = 'log'
    log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
    log_rotation_age = 1d
    log_rotation_size = 100MB
    log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
    log_checkpoints = on
    log_connections = on
    log_disconnections = on
    log_lock_waits = on
    log_temp_files = 0
    log_autovacuum_min_duration = 0
    log_error_verbosity = default

    # 统计信息
    track_activities = on
    track_counts = on
    track_io_timing = on
    track_functions = pl

    # Autovacuum
    autovacuum = on
    autovacuum_max_workers = 3
    autovacuum_naptime = 1min

  pg_hba.conf: |
    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    local   all             all                                     trust
    host    all             all             0.0.0.0/0               scram-sha-256
    host    all             all             ::/0                    scram-sha-256
    host    replication     replication     0.0.0.0/0               scram-sha-256
    host    replication     replication     ::/0                    scram-sha-256
```

### 5.2 密钥管理（Secret）

```yaml
# postgres-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: postgres
type: Opaque
stringData:
  postgres-password: "main-db-password"
  replication-password: "replication-password"
  app-user-password: "app-user-password"
---
# 使用外部密钥管理（AWS Secrets Manager）
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: postgres-secrets
  namespace: postgres
spec:
  provider: aws
  parameters:
    objects: |
      - objectName: "postgres/main-password"
        objectType: "secretsmanager"
        objectAlias: "postgres-password"
```

---

## 6. 高可用架构

### 6.1 基于Patroni的高可用

**架构图**：

```
┌─────────────────────────────────────────┐
│           Kubernetes Cluster            │
│  ┌─────────────────────────────────┐   │
│  │     PostgreSQL StatefulSet      │   │
│  │  ┌─────┐  ┌─────┐  ┌─────┐    │   │
│  │  │ P-0 │  │ P-1 │  │ P-2 │    │   │
│  │  │主库 │  │从库 │  │从库 │    │   │
│  │  └──┬──┘  └──┬──┘  └──┬──┘    │   │
│  │     │        │        │         │   │
│  │     └────────┴────────┘         │   │
│  │              │                   │   │
│  │    ┌─────────▼────────┐         │   │
│  │    │     Patroni      │         │   │
│  │    │  (HA Controller) │         │   │
│  │    └─────────┬────────┘         │   │
│  │              │                   │   │
│  │    ┌─────────▼────────┐         │   │
│  │    │      etcd        │         │   │
│  │    │  (Config Store)  │         │   │
│  │    └──────────────────┘         │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │       Service (ClusterIP)       │   │
│  │  postgres-primary (R/W)         │   │
│  │  postgres-replica (R/O)         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**完整配置示例**：参考上文Zalando Operator

### 6.2 自动故障切换测试

```bash
# 模拟主库故障
kubectl delete pod postgres-0 -n postgres

# 监控故障切换
watch kubectl get pods -n postgres -L role

# 应该看到：
# - postgres-1从"replica"变为"master"
# - postgres-0重启后变为"replica"

# 验证新主库
kubectl exec -it postgres-1 -n postgres -- psql -U postgres -c "SELECT pg_is_in_recovery()"
# 返回：f（false，表示是主库）

# 验证旧主库（现在是从库）
kubectl exec -it postgres-0 -n postgres -- psql -U postgres -c "SELECT pg_is_in_recovery()"
# 返回：t（true，表示是从库）
```

---

## 7. 监控和日志

### 7.1 Prometheus监控

```yaml
# postgres-exporter.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-exporter
  namespace: postgres
  labels:
    app: postgres-exporter
spec:
  ports:
  - port: 9187
    name: metrics
  selector:
    app: postgres-exporter
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-exporter
  namespace: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres-exporter
  template:
    metadata:
      labels:
        app: postgres-exporter
    spec:
      containers:
      - name: postgres-exporter
        image: quay.io/prometheuscommunity/postgres-exporter:latest
        ports:
        - containerPort: 9187
          name: metrics
        env:
        - name: DATA_SOURCE_NAME
          value: "postgresql://postgres:$(POSTGRES_PASSWORD)@postgres-0.postgres:5432/postgres?sslmode=disable"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
---
# ServiceMonitor（Prometheus Operator）
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: postgres-exporter
  namespace: postgres
spec:
  selector:
    matchLabels:
      app: postgres-exporter
  endpoints:
  - port: metrics
    interval: 30s
```

**Grafana Dashboard**：

- Dashboard ID: 9628 (PostgreSQL Database)
- Dashboard ID: 455 (PostgreSQL Overview)

### 7.2 日志聚合（EFK/PLG）

```yaml
# filebeat-configmap.yaml - 收集PostgreSQL日志
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: postgres
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*postgres*.log
      processors:
        - add_kubernetes_metadata:
            host: ${NODE_NAME}
            matchers:
            - logs_path:
                logs_path: "/var/log/containers/"

    output.elasticsearch:
      hosts: ['elasticsearch:9200']
      index: "postgres-logs-%{+yyyy.MM.dd}"

    setup.kibana:
      host: "kibana:5601"
```

---

## 8. 备份和恢复

### 8.1 使用pgBackRest

```yaml
# pgbackrest-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pgbackrest-config
  namespace: postgres
data:
  pgbackrest.conf: |
    [global]
    repo1-type=s3
    repo1-s3-bucket=my-postgres-backups
    repo1-s3-region=us-west-2
    repo1-s3-endpoint=s3.amazonaws.com
    repo1-retention-full=4
    repo1-retention-diff=8

    [postgres]
    pg1-path=/var/lib/postgresql/data/pgdata
    pg1-port=5432
    pg1-socket-path=/var/run/postgresql
---
# 备份CronJob
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: postgres
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pgbackrest
            image: pgbackrest/pgbackrest:latest
            command:
            - sh
            - -c
            - |
              pgbackrest --stanza=postgres --type=full backup
            volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
            - name: pgbackrest-config
              mountPath: /etc/pgbackrest
          volumes:
          - name: postgres-data
            persistentVolumeClaim:
              claimName: postgres-storage-postgres-0
          - name: pgbackrest-config
            configMap:
              name: pgbackrest-config
          restartPolicy: OnFailure
```

---

## 9. 完整生产案例

### 9.1 电商平台PostgreSQL on Kubernetes

**需求**：

- 3节点高可用
- 100GB初始存储，支持扩容
- 自动备份到S3
- Prometheus监控
- 自动故障切换

**完整部署清单**（`production-postgres/`）：

```bash
production-postgres/
├── 00-namespace.yaml
├── 01-storage-class.yaml
├── 02-secrets.yaml
├── 03-configmap-postgres.yaml
├── 04-configmap-patroni.yaml
├── 05-statefulset.yaml
├── 06-service.yaml
├── 07-postgres-exporter.yaml
├── 08-backup-cronjob.yaml
└── README.md
```

**一键部署**：

```bash
# 部署全部资源
kubectl apply -f production-postgres/

# 验证
kubectl get all -n postgres-prod

# 连接测试
kubectl run -it --rm psql-client --image=postgres:17 --restart=Never -n postgres-prod -- \
  psql -h postgres-primary -U app_user -d app_db
```

---

## 📚 参考资源

### Kubernetes官方

1. [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
2. [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
3. [Operators](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)

### PostgreSQL Operators

1. [Zalando Postgres Operator](https://github.com/zalando/postgres-operator)
2. [CloudNativePG](https://cloudnative-pg.io/)
3. [Crunchy PostgreSQL Operator](https://access.crunchydata.com/documentation/postgres-operator/latest/)

### 最佳实践

1. [Running PostgreSQL on Kubernetes](https://www.postgresql.org/docs/current/high-availability.html)
2. [Kubernetes Patterns](https://k8spatterns.io/)

---

**创建时间**: 2025年1月
**最后更新**: 2025年1月
**维护者**: PostgreSQL Modern Team
**难度等级**: ⭐⭐⭐⭐⭐ 专家级

☸️ **在Kubernetes上运行生产级PostgreSQL！**
