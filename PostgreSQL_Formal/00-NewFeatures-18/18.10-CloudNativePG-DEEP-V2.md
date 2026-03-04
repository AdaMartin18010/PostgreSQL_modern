# 18.10 CloudNativePG 深度分析：Kubernetes原生PostgreSQL

## 目录

- [18.10 CloudNativePG 深度分析：Kubernetes原生PostgreSQL](#1810-cloudnativepg-深度分析kubernetes原生postgresql)
  - [目录](#目录)
  - [1. Kubernetes存储理论基础](#1-kubernetes存储理论基础)
    - [1.1 StatefulSet管理](#11-statefulset管理)
      - [1.1.1 StatefulSet核心特性](#111-statefulset核心特性)
      - [1.1.2 存储卷声明模板](#112-存储卷声明模板)
      - [1.1.3 Pod管理策略](#113-pod管理策略)
    - [1.2 PV/PVC机制](#12-pvpvc机制)
      - [1.2.1 存储抽象层次](#121-存储抽象层次)
      - [1.2.2 访问模式矩阵](#122-访问模式矩阵)
      - [1.2.3 容量计算](#123-容量计算)
    - [1.3 存储类选择](#13-存储类选择)
      - [1.3.1 存储性能模型](#131-存储性能模型)
      - [1.3.2 云厂商存储对比](#132-云厂商存储对比)
      - [1.3.3 存储类配置](#133-存储类配置)
  - [2. CloudNativePG架构设计](#2-cloudnativepg架构设计)
    - [2.1 Operator模式](#21-operator模式)
      - [2.1.1 Kubernetes Operator原理](#211-kubernetes-operator原理)
      - [2.1.2 CRD资源定义](#212-crd资源定义)
      - [2.1.3 控制器架构](#213-控制器架构)
    - [2.2 故障转移机制](#22-故障转移机制)
      - [2.2.1 高可用架构](#221-高可用架构)
      - [2.2.2 故障检测算法](#222-故障检测算法)
      - [2.2.3 故障转移流程](#223-故障转移流程)
    - [2.3 备份恢复架构](#23-备份恢复架构)
      - [2.3.1 备份类型](#231-备份类型)
      - [2.3.2 备份调度](#232-备份调度)
      - [2.3.3 并行备份配置](#233-并行备份配置)
  - [3. 生产实践部署](#3-生产实践部署)
    - [3.1 Helm部署](#31-helm部署)
      - [3.1.1 部署架构](#311-部署架构)
      - [3.1.2 生产环境配置](#312-生产环境配置)
      - [3.1.3 部署命令](#313-部署命令)
      - [3.1.4 配置验证](#314-配置验证)
    - [3.2 监控集成](#32-监控集成)
      - [3.2.1 Prometheus监控架构](#321-prometheus监控架构)
      - [3.2.2 ServiceMonitor配置](#322-servicemonitor配置)
      - [3.2.3 自定义查询配置](#323-自定义查询配置)
      - [3.2.4 Grafana仪表板](#324-grafana仪表板)
    - [3.3 自动扩缩容](#33-自动扩缩容)
      - [3.3.1 HPA配置](#331-hpa配置)
      - [3.3.2 VPA配置](#332-vpa配置)
      - [3.3.3 存储扩容](#333-存储扩容)
  - [4. 高可用与灾难恢复](#4-高可用与灾难恢复)
    - [4.1 同步复制配置](#41-同步复制配置)
      - [4.1.1 复制模式](#411-复制模式)
      - [4.1.2 CloudNativePG复制配置](#412-cloudnativepg复制配置)
      - [4.1.3 复制延迟监控](#413-复制延迟监控)
    - [4.2 跨可用区部署](#42-跨可用区部署)
      - [4.2.1 拓扑分布](#421-拓扑分布)
      - [4.2.2 Pod拓扑分布约束](#422-pod拓扑分布约束)
      - [4.2.3 存储区域感知](#423-存储区域感知)
    - [4.3 灾难恢复](#43-灾难恢复)
      - [4.3.1 备份策略](#431-备份策略)
      - [4.3.2 跨区域恢复](#432-跨区域恢复)
      - [4.3.3 故障转移演练](#433-故障转移演练)
  - [5. 运维与监控](#5-运维与监控)
    - [5.1 日常运维](#51-日常运维)
      - [5.1.1 集群状态检查](#511-集群状态检查)
      - [5.1.2 备份验证](#512-备份验证)
    - [5.2 性能调优](#52-性能调优)
      - [5.2.1 连接池配置](#521-连接池配置)
      - [5.2.2 VACUUM和ANALYZE调度](#522-vacuum和analyze调度)
      - [5.2.3 WAL归档管理](#523-wal归档管理)
    - [5.3 安全加固](#53-安全加固)
      - [5.3.1 网络策略](#531-网络策略)
      - [5.3.2 TLS配置](#532-tls配置)
      - [5.3.3 RBAC配置](#533-rbac配置)
  - [总结](#总结)
  - [参考公式汇总](#参考公式汇总)
    - [5.4 升级与维护](#54-升级与维护)
      - [5.4.1 PostgreSQL版本升级](#541-postgresql版本升级)
      - [5.4.2 滚动维护窗口](#542-滚动维护窗口)
      - [5.4.3 配置热重载](#543-配置热重载)
    - [5.5 故障排查](#55-故障排查)
      - [5.5.1 常见故障场景](#551-常见故障场景)
      - [5.5.2 日志分析](#552-日志分析)
      - [5.5.3 性能瓶颈诊断](#553-性能瓶颈诊断)
    - [5.6 多租户架构](#56-多租户架构)
      - [5.6.1 命名空间隔离](#561-命名空间隔离)
      - [5.6.2 资源配额管理](#562-资源配额管理)
  - [6. 实战案例研究](#6-实战案例研究)
    - [6.1 金融交易系统](#61-金融交易系统)
    - [6.2 电商平台](#62-电商平台)
    - [6.3 SaaS多租户数据库](#63-saas多租户数据库)
  - [7. 性能基准测试](#7-性能基准测试)
    - [7.1 pgbench测试](#71-pgbench测试)
    - [7.2 性能指标收集](#72-性能指标收集)
  - [8. 最佳实践总结](#8-最佳实践总结)
    - [8.1 部署检查清单](#81-部署检查清单)
    - [8.2 运维黄金法则](#82-运维黄金法则)
    - [8.3 容量规划公式](#83-容量规划公式)
  - [总结](#总结-1)
  - [参考公式汇总](#参考公式汇总-1)

---

## 1. Kubernetes存储理论基础

### 1.1 StatefulSet管理

StatefulSet是Kubernetes管理有状态应用的核心控制器，为PostgreSQL等数据库提供稳定的网络标识和持久化存储。

#### 1.1.1 StatefulSet核心特性

**稳定网络标识：**

StatefulSet创建的Pod具有可预测的DNS名称：

$$DNS_{pod} = \{pod-name\}.\{service-name\}.\{namespace\}.svc.cluster.local$$

对于名为 `postgres` 的StatefulSet，3个副本的网络标识为：

```
postgres-0.postgres.default.svc.cluster.local
postgres-1.postgres.default.svc.cluster.local
postgres-2.postgres.default.svc.cluster.local
```

**Pod序号标识：**

$$Pod_{name} = \{statefulset-name\}-\{ordinal\}, \quad ordinal \in [0, replicas-1]$$

**有序部署与扩缩容：**

部署顺序（升序）：

$$Deploy_{order} = (0, 1, 2, ..., n-1)$$

缩容顺序（降序）：

$$Scale\_down_{order} = (n-1, n-2, ..., 1, 0)$$

#### 1.1.2 存储卷声明模板

StatefulSet使用VolumeClaimTemplate为每个Pod创建独立的PVC：

```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: ["ReadWriteOnce"]
    storageClassName: fast-ssd
    resources:
      requests:
        storage: 100Gi
```

PVC命名规则：

$$PVC_{name} = \{volumeClaimTemplate\}-\{statefulset-name\}-\{ordinal\}$$

生成的PVC列表：

$$PVCs = \{data-postgres-0, data-postgres-1, data-postgres-2\}$$

#### 1.1.3 Pod管理策略

**OrderedReady策略（默认）：**

Pod创建/更新/删除顺序约束：

$$Pod_{i} \text{ 就绪} \Rightarrow Pod_{i+1} \text{ 可创建}$$

**Parallel策略：**

所有Pod并行管理，适用于初始化阶段：

$$\forall i \in [0, n-1]: Pod_i \text{ 并行启动}$$

### 1.2 PV/PVC机制

#### 1.2.1 存储抽象层次

Kubernetes存储的三层抽象：

```
┌─────────────────────────────────────────────────────────┐
│                     Application                         │
│                    (PostgreSQL)                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│       PersistentVolumeClaim (PVC)                       │
│  - 资源请求：storage: 100Gi                             │
│  - 访问模式：ReadWriteOnce                              │
│  - 存储类：fast-ssd                                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│          PersistentVolume (PV)                          │
│  - 实际存储资源                                         │
│  - ReclaimPolicy: Retain/Delete/Recycle                 │
│  - 后端存储：EBS/Azure Disk/GCE PD/本地SSD              │
└─────────────────────────────────────────────────────────┘
```

#### 1.2.2 访问模式矩阵

| 访问模式 | 说明 | 适用场景 |
|---------|------|---------|
| ReadWriteOnce (RWO) | 单节点读写 | PostgreSQL主节点 |
| ReadOnlyMany (ROX) | 多节点只读 | 备份读取 |
| ReadWriteMany (RWX) | 多节点读写 | 共享存储（不推荐PG） |
| ReadWriteOncePod (RWOP) | 单Pod读写 | Kubernetes 1.22+ |

CloudNativePG的访问模式选择：

$$AccessMode_{primary} = RWO$$

$$AccessMode_{replica} = RWO \text{（独立PV）}$$

#### 1.2.3 容量计算

PostgreSQL存储容量规划：

$$Storage_{total} = Storage_{data} + Storage_{wal} + Storage_{backup}$$

其中：

$$Storage_{data} = \sum_{i} Table_{i} + Index_{i}$$

$$Storage_{wal} = wal\_segment\_size \cdot wal\_keep\_size$$

$$Storage_{backup} = Storage_{data} \cdot retention\_ratio \cdot compression\_ratio$$

WAL保留计算：

$$WAL_{retention} = \max(wal\_keep\_size, replication\_slots \cdot slot\_keep\_size)$$

### 1.3 存储类选择

#### 1.3.1 存储性能模型

存储I/O性能指标：

**IOPS计算：**

$$IOPS_{required} = \frac{Transactions_{peak} \cdot IO_{per\_transaction}}{Parallelism}$$

**吞吐量计算：**

$$Throughput = \frac{Data_{read/write}}{Time}$$

**延迟要求：**

$$Latency_{p99} < 10ms \text{（OLTP）}$$

$$Latency_{p99} < 100ms \text{（OLAP可接受）}$$

#### 1.3.2 云厂商存储对比

| 云厂商 | 存储类型 | IOPS范围 | 吞吐量 | 延迟 |
|-------|---------|---------|-------|------|
| AWS | gp3 | 3,000-16,000 | 125-1,000 MB/s | ~5ms |
| AWS | io1/io2 | 16,000-64,000 | 1,000 MB/s | ~1ms |
| Azure | Premium SSD | 120-20,000 | 25-900 MB/s | ~5ms |
| GCP | PD-SSD | 15,000-100,000 | 1,200 MB/s | ~3ms |
| 阿里云 | ESSD | 10,000-1,000,000 | 300-4,000 MB/s | ~1ms |

#### 1.3.3 存储类配置

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: postgres-premium
provisioner: ebs.csi.aws.com  # AWS EBS CSI Driver
parameters:
  type: io2
  iopsPerGB: "50"
  encrypted: "true"
  kmsKeyId: alias/aws/ebs
allowVolumeExpansion: true
mountOptions:
  - noatime
  - nodiratime
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Retain
```

IOPS计算公式：

$$IOPS_{io2} = \min(64000, \max(100, VolumeSize_{GiB} \cdot IOPS_{per\_GB}))$$

---

## 2. CloudNativePG架构设计

### 2.1 Operator模式

#### 2.1.1 Kubernetes Operator原理

Operator遵循控制循环模式：

```
         ┌─────────────┐
         │   Desired   │
         │    State    │
         └──────┬──────┘
                │
                ▼
    ┌───────────────────────┐
    │      Operator         │
    │  (Control Loop)       │
    │                       │
    │  1. Observe (监控)     │
    │  2. Diff (比较)        │
    │  3. Act (执行)         │
    └───────┬───────────────┘
            │
            ▼
    ┌───────────────────────┐
    │    Actual State       │
    │   (PostgreSQL集群)     │
    └───────────────────────┘
```

控制循环周期：

$$T_{reconcile} = \frac{1}{frequency_{operator}}$$

CloudNativePG默认调和间隔：

$$T_{reconcile} \approx 30s$$

#### 2.1.2 CRD资源定义

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-db
spec:
  instances: 3
  postgresql:
    version: "16"
    parameters:
      max_connections: "200"
      shared_buffers: "1GB"
      effective_cache_size: "3GB"
  storage:
    size: 100Gi
    storageClass: postgres-premium
  resources:
    requests:
      memory: "2Gi"
      cpu: "2"
    limits:
      memory: "4Gi"
      cpu: "4"
  replicationSlots:
    highAvailability:
      enabled: true
```

CRD字段结构：

$$Spec = \{Instances, Version, Storage, Resources, Replication, Backup\}$$

#### 2.1.3 控制器架构

CloudNativePG控制器组件：

```
┌─────────────────────────────────────────────────────────┐
│                  CloudNativePG Operator                 │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Cluster   │  │    Pooler   │  │  Scheduled  │     │
│  │  Controller │  │  Controller │  │   Backup    │     │
│  └─────────────┘  └─────────────┘  │ Controller  │     │
│                                     └─────────────┘     │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Webhook   │  │   Plugin    │  │   Metrics   │     │
│  │   Server    │  │   Manager   │  │   Exporter  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 故障转移机制

#### 2.2.1 高可用架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes Service                      │
│                (production-db-rw / production-db-ro)         │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  postgres-0  │  │  postgres-1  │  │  postgres-2  │
    │   (Primary)  │  │  (Replica)   │  │  (Replica)   │
    │              │  │              │  │              │
    │  ReadWrite   │  │   ReadOnly   │  │   ReadOnly   │
    │   Service    │  │   Service    │  │              │
    └──────────────┘  └──────────────┘  └──────────────┘
           │                 │                 │
           └─────────────────┴─────────────────┘
                              │
                     Streaming Replication
```

#### 2.2.2 故障检测算法

**健康检查机制：**

$$Health_{score} = \alpha \cdot Health_{liveness} + \beta \cdot Health_{readiness}$$

超时计算：

$$Timeout_{failover} = \max(GracePeriod, ReplicationLag_{threshold})$$

**故障判定条件：**

$$
IsFailed = \begin{cases}
True & \text{if } T_{unhealthy} > T_{threshold} \\
False & \text{otherwise}
\end{cases}
$$

#### 2.2.3 故障转移流程

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Detect  │────▶│  2. Decide  │────▶│  3. Promote │
│  Failure    │     │  New Primary│     │  Replica    │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  6. Resume  │◀────│  5. Redirect│◀────│  4. Update  │
│  Service    │     │  Traffic    │     │  Service    │
└─────────────┘     └─────────────┘     └─────────────┘
```

故障转移时间公式：

$$T_{failover} = T_{detect} + T_{election} + T_{promote} + T_{update}$$

典型值：

$$T_{failover} \approx 30s - 60s$$

**选举算法：**

选择最佳备库的评分函数：

$$Score_{replica} = w_1 \cdot \frac{1}{Lag_{replication}} + w_2 \cdot Timeline_{replica} + w_3 \cdot Priority_{replica}$$

### 2.3 备份恢复架构

#### 2.3.1 备份类型

**WAL归档备份：**

$$Backup_{incremental} = \{BaseBackup_{t0}, WAL_{[t0, t1]}, WAL_{[t1, t2]}, ...\}$$

**PITR时间点恢复：**

$$RecoveryPoint_{target} \in [Backup_{oldest}, NOW]$$

**对象存储集成：**

| 存储类型 | 配置示例 | 适用场景 |
|---------|---------|---------|
| S3 | s3://bucket/path | AWS环境 |
| GCS | gs://bucket/path | GCP环境 |
| Azure Blob | <https://account.blob.core.windows.net> | Azure环境 |
| MinIO | s3://minio-endpoint | 私有云 |

#### 2.3.2 备份调度

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  backupOwnerReference: self
  cluster:
    name: production-db
  method: barmanObjectStore
```

备份窗口计算：

$$BackupWindow = \frac{DataSize}{NetworkBandwidth} + Overhead$$

#### 2.3.3 并行备份配置

```yaml
spec:
  backup:
    barmanObjectStore:
      destinationPath: "s3://postgres-backups/production"
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: SECRET_ACCESS_KEY
      data:
        parallelism: 4  # 并行度
        compression: gzip
      wal:
        compression: gzip
        retention: "7d"
```

并行备份加速比：

$$Speedup = \min(N_{parallel}, \frac{IOPS_{storage}}{IOPS_{single}})$$

---

## 3. 生产实践部署

### 3.1 Helm部署

#### 3.1.1 部署架构

```text
┌─────────────────────────────────────────────────────────────┐
│                      Helm Chart Structure                    │
├─────────────────────────────────────────────────────────────┤
│  cnpg/                                                       │
│  ├── Chart.yaml          # Chart元数据                       │
│  ├── values.yaml         # 默认配置值                        │
│  ├── values-production.yaml  # 生产环境配置                  │
│  └── templates/                                              │
│      ├── _helpers.tpl    # 模板辅助函数                      │
│      ├── cluster.yaml    # PostgreSQL集群定义                │
│      ├── pooler.yaml     # 连接池配置                        │
│      ├── backup.yaml     # 备份计划                          │
│      ├── monitoring.yaml # 监控配置                          │
│      └── secrets.yaml    # 密钥管理                          │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 生产环境配置

```yaml
# values-production.yaml
global:
  namespace: postgres-production
  storageClass: premium-rwo

cluster:
  name: production-cluster
  instances: 3

  postgresql:
    version: "16"
    parameters:
      # 连接配置
      max_connections: "500"
      superuser_reserved_connections: "5"

      # 内存配置
      shared_buffers: "4GB"
      effective_cache_size: "12GB"
      work_mem: "32MB"
      maintenance_work_mem: "1GB"

      # WAL配置
      wal_buffers: "64MB"
      min_wal_size: "2GB"
      max_wal_size: "8GB"
      wal_keep_size: "2GB"
      checkpoint_completion_target: "0.9"

      # 并发配置
      max_worker_processes: "16"
      max_parallel_workers_per_gather: "8"
      max_parallel_workers: "16"
      max_parallel_maintenance_workers: "4"

      # 查询优化
      random_page_cost: "1.1"  # SSD存储
      effective_io_concurrency: "200"
      default_statistics_target: "500"

  storage:
    size: 500Gi
    resizeInUseVolumes: true

  resources:
    requests:
      memory: "8Gi"
      cpu: "4"
    limits:
      memory: "16Gi"
      cpu: "8"

  affinity:
    enablePodAntiAffinity: true
    topologyKey: topology.kubernetes.io/zone

  failover:
    switchoverDelay: 300
    failoverDelay: 60

pooler:
  enabled: true
  instances: 2
  poolMode: transaction
  parameters:
    max_client_conn: "10000"
    default_pool_size: "50"
    reserve_pool_size: "10"
    reserve_pool_timeout: "5"

backup:
  enabled: true
  retentionPolicy: "30d"
  schedule: "0 */6 * * *"  # 每6小时
  s3:
    bucket: "postgres-backups-production"
    region: "us-east-1"
    path: "/production-cluster"

monitoring:
  enabled: true
  customQueriesConfigMap:
    name: cnpg-custom-queries
    key: queries.yaml
```

#### 3.1.3 部署命令

```bash
# 添加Helm仓库
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm repo update

# 安装Operator
helm upgrade --install cnpg-operator cnpg/cloudnative-pg \
  --namespace cnpg-system \
  --create-namespace \
  --version 0.20.0

# 部署生产集群
helm upgrade --install production-db cnpg/cnpg-cluster \
  --namespace postgres-production \
  --create-namespace \
  --values values-production.yaml \
  --wait

# 验证部署
kubectl get clusters.postgresql.cnpg.io -n postgres-production
kubectl get pods -n postgres-production -l app=production-cluster
```

#### 3.1.4 配置验证

```bash
# 检查集群状态
kubectl cnpg status production-cluster -n postgres-production

# 输出示例
Cluster Summary
Name:               production-cluster
Namespace:          postgres-production
PostgreSQL Version: 16.2
Instances:          3
Ready Instances:    3
Status:             Cluster in healthy state

Instances Status
Name            Role    Status  Lag in MB
----            ----    ------  ---------
production-0    primary running 0
production-1    replica running 0
production-2    replica running 0
```

### 3.2 监控集成

#### 3.2.1 Prometheus监控架构

```text
┌─────────────────────────────────────────────────────────────┐
│                    Prometheus Monitoring                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   CNPG Pod   │      │   CNPG Pod   │      │ CNPG Pod  │ │
│  │  (Primary)   │      │  (Replica)   │      │ (Replica) │ │
│  │              │      │              │      │           │ │
│  │ ┌──────────┐ │      │ ┌──────────┐ │      │ ┌────────┐│ │
│  │ │ postgres │ │      │ │ postgres │ │      │ │postgres││ │
│  │ │ exporter │ │      │ │ exporter │ │      │ │exporter││ │
│  │ │ :9187    │ │      │ │ :9187    │ │      │ │ :9187  ││ │
│  │ └────┬─────┘ │      │ └────┬─────┘ │      │ └────┬───┘│ │
│  └──────┼───────┘      └──────┼───────┘      └──────┼────┘ │
│         │                     │                     │      │
│         └─────────────────────┴─────────────────────┘      │
│                              │                             │
│                              ▼                             │
│                    ┌───────────────────┐                   │
│                    │    Prometheus     │                   │
│                    │    Server         │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│                              ▼                             │
│                    ┌───────────────────┐                   │
│                    │      Grafana      │                   │
│                    │   Dashboards      │                   │
│                    └───────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 3.2.2 ServiceMonitor配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cnpg-metrics
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames:
      - postgres-production
  selector:
    matchLabels:
      cnpg.io/cluster: production-cluster
  endpoints:
    - port: metrics
      interval: 30s
      scrapeTimeout: 10s
      path: /metrics
      metricRelabelings:
        - sourceLabels: [__name__]
          regex: 'cnpg_.*'
          action: keep
```

#### 3.2.3 自定义查询配置

```yaml
# custom-queries.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cnpg-custom-queries
  namespace: postgres-production
data:
  queries.yaml: |
    pg_database_size:
      query: |
        SELECT
          datname AS database,
          pg_database_size(datname) AS bytes
        FROM pg_database
        WHERE datallowconn
      metrics:
        - database:
            usage: LABEL
            description: Database name
        - bytes:
            usage: GAUGE
            description: Database size in bytes

    pg_replication_lag:
      query: |
        SELECT
          CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
               THEN 0
               ELSE EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
          END AS lag_seconds,
          CASE WHEN pg_is_in_recovery() THEN 1 ELSE 0 END AS is_replica
      metrics:
        - lag_seconds:
            usage: GAUGE
            description: Replication lag in seconds
        - is_replica:
            usage: GAUGE
            description: Is this instance a replica

    pg_connection_stats:
      query: |
        SELECT
          count(*) FILTER (WHERE state = 'active') AS active,
          count(*) FILTER (WHERE state = 'idle') AS idle,
          count(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction,
          count(*) AS total
        FROM pg_stat_activity
        WHERE backend_type = 'client backend'
      metrics:
        - active:
            usage: GAUGE
            description: Active connections
        - idle:
            usage: GAUGE
            description: Idle connections
        - idle_in_transaction:
            usage: GAUGE
            description: Idle in transaction connections
        - total:
            usage: GAUGE
            description: Total connections
```

#### 3.2.4 Grafana仪表板

```json
{
  "dashboard": {
    "title": "CloudNativePG Production",
    "panels": [
      {
        "title": "Replication Lag",
        "targets": [
          {
            "expr": "cnpg_pg_stat_replication_pg_wal_lsn_diff / 1024 / 1024",
            "legendFormat": "{{pod}} - Lag (MB)"
          }
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {"type": "gt", "params": [100]},
              "operator": {"type": "and"},
              "query": {"params": ["A", "5m", "now"]},
              "reducer": {"type": "avg"},
              "type": "query"
            }
          ],
          "executionErrorState": "alerting",
          "name": "Replication Lag Alert",
          "message": "Replication lag exceeded 100MB"
        }
      },
      {
        "title": "Transaction Rate",
        "targets": [
          {
            "expr": "rate(cnpg_pg_stat_database_xact_commit[1m])",
            "legendFormat": "{{datname}} - Commits/sec"
          },
          {
            "expr": "rate(cnpg_pg_stat_database_xact_rollback[1m])",
            "legendFormat": "{{datname}} - Rollbacks/sec"
          }
        ]
      },
      {
        "title": "Storage Usage",
        "targets": [
          {
            "expr": "cnpg_pg_database_size_bytes / 1024 / 1024 / 1024",
            "legendFormat": "{{datname}} - Size (GB)"
          }
        ]
      }
    ]
  }
}
```

### 3.3 自动扩缩容

#### 3.3.1 HPA配置

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cnpg-pooler-hpa
  namespace: postgres-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: production-cluster-pooler
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: pg_stat_activity_count
        target:
          type: AverageValue
          averageValue: "80"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

#### 3.3.2 VPA配置

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: cnpg-vpa
  namespace: postgres-production
spec:
  targetRef:
    apiVersion: postgresql.cnpg.io/v1
    kind: Cluster
    name: production-cluster
  updatePolicy:
    updateMode: "Off"  # 仅建议模式，数据库通常手动调整
  resourcePolicy:
    containerPolicies:
      - containerName: postgres
        minAllowed:
          cpu: 2
          memory: 4Gi
        maxAllowed:
          cpu: 16
          memory: 64Gi
        controlledResources: ["cpu", "memory"]
```

#### 3.3.3 存储扩容

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-cluster
spec:
  storage:
    size: 500Gi
    resizeInUseVolumes: true

  # 存储告警和自动扩容触发
  monitoring:
    customMetrics:
      - name: pg_database_size
        query: |
          SELECT
            datname,
            pg_database_size(datname) as size
          FROM pg_database
          WHERE datallowconn
```

存储扩容公式：

$$
Storage_{new} = \begin{cases}
Storage_{current} \cdot 1.5 & \text{if } Usage > 80\% \\
Storage_{current} & \text{otherwise}
\end{cases}
$$

---

## 4. 高可用与灾难恢复

### 4.1 同步复制配置

#### 4.1.1 复制模式

**同步复制公式：**

$$Commit_{latency} = T_{local\_write} + T_{network} + T_{replica\_fsync}$$

**synchronous_commit选项：**

| 设置 | 描述 | 持久性 | 性能 |
|-----|------|-------|------|
| off | 异步提交 | 低 | 最高 |
| local | 本地确认 | 中 | 高 |
| remote_write | 备库接收 | 中高 | 中等 |
| on | 备库刷盘 | 高 | 较低 |
| remote_apply | 备库应用 | 最高 | 最低 |

#### 4.1.2 CloudNativePG复制配置

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: ha-cluster
spec:
  instances: 3

  postgresql:
    synchronous:
      method: any  # 任意一个备库确认
      number: 1    # 需要1个同步备库
      # 或指定具体实例
      # instances:
      #   - ha-cluster-1
      #   - ha-cluster-2

  replicationSlots:
    highAvailability:
      enabled: true
      slotPrefix: _cnpg_

  failover:
    switchoverDelay: 60
    failoverDelay: 30
```

**Quorum Commit：**

$$N_{sync} = \lfloor \frac{N_{replicas} + 1}{2} \rfloor$$

对于3节点集群：

$$N_{sync} = \lfloor \frac{3 + 1}{2} \rfloor = 2$$

#### 4.1.3 复制延迟监控

```sql
-- 主库查询复制延迟
SELECT
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- 备库查询接收延迟
SELECT
    pg_last_wal_receive_lsn() AS receive_lsn,
    pg_last_wal_replay_lsn() AS replay_lsn,
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) AS lag_bytes,
    pg_last_xact_replay_timestamp() AS last_replay_time,
    now() - pg_last_xact_replay_timestamp() AS lag_time;
```

### 4.2 跨可用区部署

#### 4.2.1 拓扑分布

```
┌─────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Availability Zone A                  │   │
│  │  ┌─────────────┐                                    │   │
│  │  │ postgres-0  │  Primary                           │   │
│  │  │  (Primary)  │                                    │   │
│  │  └─────────────┘                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Availability Zone B                  │   │
│  │  ┌─────────────┐                                    │   │
│  │  │ postgres-1  │  Replica                           │   │
│  │  │  (Replica)  │                                    │   │
│  │  └─────────────┘                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Availability Zone C                  │   │
│  │  ┌─────────────┐                                    │   │
│  │  │ postgres-2  │  Replica                           │   │
│  │  │  (Replica)  │                                    │   │
│  │  └─────────────┘                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Pod拓扑分布约束

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: multi-az-cluster
spec:
  instances: 3

  affinity:
    enablePodAntiAffinity: true
    topologyKey: topology.kubernetes.io/zone

    podAntiAffinityType: required  # 强制分布在不同AZ

    additionalPodAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                cnpg.io/cluster: multi-az-cluster
            topologyKey: kubernetes.io/hostname

  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "postgres"
      effect: "NoSchedule"
```

#### 4.2.3 存储区域感知

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: zone-aware-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
allowedTopologies:
  - matchLabelExpressions:
      - key: topology.ebs.csi.aws.com/zone
        values:
          - us-east-1a
          - us-east-1b
          - us-east-1c
volumeBindingMode: WaitForFirstConsumer
```

跨AZ延迟模型：

$$Latency_{cross\_az} = Latency_{intra\_az} + Latency_{backbone}$$

典型值：

- 同AZ延迟: 0.1-0.5ms
- 跨AZ延迟: 1-3ms

### 4.3 灾难恢复

#### 4.3.1 备份策略

**3-2-1备份原则：**

$$Backup_{strategy} = 3_{copies} \cdot 2_{media} \cdot 1_{offsite}$$

**备份频率计算：**

$$RPO_{max} = \min(FullBackup_{interval}, WAL_{retention})$$

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: disaster-recovery-backup
spec:
  immediate: true
  schedule: "0 */4 * * *"  # 每4小时全量备份
  backupOwnerReference: self
  cluster:
    name: production-cluster
  method: barmanObjectStore

---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-cluster
spec:
  backup:
    barmanObjectStore:
      destinationPath: "s3://postgres-dr-bucket/production"
      s3Credentials:
        accessKeyId:
          name: dr-backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: dr-backup-creds
          key: SECRET_ACCESS_KEY
      # 跨区域复制
      additionalArgs:
        - "--s3-sync-snapshots"
      data:
        compression: bzip2
        jobs: 4
      wal:
        compression: bzip2
        maxParallel: 4
```

#### 4.3.2 跨区域恢复

```yaml
# 在灾备区域创建恢复集群
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: dr-recovery-cluster
  namespace: postgres-dr
spec:
  instances: 3

  bootstrap:
    recovery:
      source: production-cluster
      # 指定恢复时间点
      recoveryTarget:
        targetTime: "2026-03-04T12:00:00Z"
        # 或指定LSN
        # targetLSN: "0/3000000"

  externalClusters:
    - name: production-cluster
      barmanObjectStore:
        destinationPath: "s3://postgres-dr-bucket/production"
        s3Credentials:
          accessKeyId:
            name: dr-backup-creds
            key: ACCESS_KEY_ID
          secretAccessKey:
            name: dr-backup-creds
            key: SECRET_ACCESS_KEY
        serverName: production-cluster

  storage:
    size: 500Gi
    storageClass: dr-region-ssd
```

#### 4.3.3 故障转移演练

```bash
# !/bin/bash
# disaster-recovery-drill.sh

set -e

PRIMARY_CLUSTER="production-cluster"
DR_CLUSTER="dr-recovery-cluster"
NAMESPACE="postgres-production"
DR_NAMESPACE="postgres-dr"

echo "=== 灾难恢复演练开始 ==="

# 1. 记录当前状态
echo "1. 记录主集群状态..."
kubectl cnpg status ${PRIMARY_CLUSTER} -n ${NAMESPACE} > /tmp/primary-status-before.txt

# 2. 模拟主集群故障
echo "2. 模拟主集群故障..."
kubectl delete cluster ${PRIMARY_CLUSTER} -n ${NAMESPACE} --wait=false

# 3. 等待故障检测（模拟）
echo "3. 等待故障检测..."
sleep 60

# 4. 在DR区域创建恢复集群
echo "4. 启动DR集群..."
kubectl apply -f dr-recovery-cluster.yaml -n ${DR_NAMESPACE}

# 5. 等待DR集群就绪
echo "5. 等待DR集群就绪..."
kubectl wait --for=condition=Ready cluster/${DR_CLUSTER} -n ${DR_NAMESPACE} --timeout=600s

# 6. 验证数据完整性
echo "6. 验证数据完整性..."
kubectl cnpg backup --immediate ${DR_CLUSTER} -n ${DR_NAMESPACE}

# 7. 应用连接切换
echo "7. 应用连接切换到DR集群..."
# 更新应用配置指向DR端点

# 8. 记录恢复时间
echo "8. 记录恢复指标..."
echo "RTO: $(cat /tmp/rto-timer.txt)"
echo "RPO: $(cat /tmp/rpo-timer.txt)"

echo "=== 灾难恢复演练完成 ==="
```

恢复指标：

$$RTO = T_{detect} + T_{decision} + T_{restore} + T_{verify}$$

$$RPO = T_{last\_backup} - T_{failure}$$

---

## 5. 运维与监控

### 5.1 日常运维

#### 5.1.1 集群状态检查

```bash
# !/bin/bash
# daily-health-check.sh

CLUSTER_NAME="production-cluster"
NAMESPACE="postgres-production"

echo "=== CloudNativePG 每日健康检查 ==="
echo "时间: $(date)"

# 1. 集群整体状态
echo -e "\n1. 集群状态:"
kubectl cnpg status ${CLUSTER_NAME} -n ${NAMESPACE}

# 2. Pod状态检查
echo -e "\n2. Pod状态:"
kubectl get pods -n ${NAMESPACE} -l cnpg.io/cluster=${CLUSTER_NAME} -o wide

# 3. PVC使用检查
echo -e "\n3. 存储使用:"
kubectl get pvc -n ${NAMESPACE} -l cnpg.io/cluster=${CLUSTER_NAME}

# 4. 复制延迟检查
echo -e "\n4. 复制延迟:"
PRIMARY_POD=$(kubectl get pods -n ${NAMESPACE} -l cnpg.io/cluster=${CLUSTER_NAME},role=primary -o name | head -1)
kubectl exec -it ${PRIMARY_POD} -n ${NAMESPACE} -- psql -c "
SELECT
    client_addr,
    state,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS lag
FROM pg_stat_replication;
"

# 5. 连接数检查
echo -e "\n5. 连接数:"
kubectl exec -it ${PRIMARY_POD} -n ${NAMESPACE} -- psql -c "
SELECT
    state,
    COUNT(*)
FROM pg_stat_activity
GROUP BY state;
"

# 6. 锁等待检查
echo -e "\n6. 锁等待:"
kubectl exec -it ${PRIMARY_POD} -n ${NAMESPACE} -- psql -c "
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"

echo -e "\n=== 健康检查完成 ==="
```

#### 5.1.2 备份验证

```bash
# !/bin/bash
# backup-verification.sh

BACKUP_NAME=$(kubectl get scheduledbackup -n postgres-production -o jsonpath='{.items[0].metadata.name}')

echo "=== 备份验证 ==="

# 1. 列出备份
echo "1. 可用备份列表:"
kubectl cnpg backup --list -n postgres-production | head -20

# 2. 验证最新备份完整性
echo -e "\n2. 验证最新备份:"
LATEST_BACKUP=$(kubectl get backup -n postgres-production --sort-by=.status.stoppedAt -o jsonpath='{.items[-1].metadata.name}')
kubectl describe backup ${LATEST_BACKUP} -n postgres-production

# 3. 测试恢复（到临时集群）
echo -e "\n3. 测试恢复..."
cat <<EOF | kubectl apply -f -
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: backup-test-cluster
  namespace: postgres-test
spec:
  instances: 1
  bootstrap:
    recovery:
      backup:
        name: ${LATEST_BACKUP}
  storage:
    size: 100Gi
EOF

kubectl wait --for=condition=Ready cluster/backup-test-cluster -n postgres-test --timeout=300s

# 4. 验证数据
echo -e "\n4. 验证数据完整性..."
kubectl exec -it backup-test-cluster-1 -n postgres-test -- psql -c "SELECT count(*) FROM critical_table;"

# 5. 清理测试集群
echo -e "\n5. 清理测试资源..."
kubectl delete cluster backup-test-cluster -n postgres-test

echo "=== 备份验证完成 ==="
```

### 5.2 性能调优

#### 5.2.1 连接池配置

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: production-pooler
  namespace: postgres-production
spec:
  cluster:
    name: production-cluster
  instances: 3
  type: rw  # rw 或 ro
  poolMode: transaction  # session, transaction, statement

  parameters:
    max_client_conn: "10000"
    default_pool_size: "50"
    min_pool_size: "10"
    reserve_pool_size: "10"
    reserve_pool_timeout: "5"
    max_db_connections: "100"
    max_user_connections: "100"
    server_idle_timeout: "600"
    server_lifetime: "3600"
    server_connect_timeout: "5"
    query_timeout: "300"
    query_wait_timeout: "120"
    client_idle_timeout: "0"
    client_login_timeout: "60"
    autodb_idle_timeout: "3600"
```

连接池公式：

$$PoolSize = \frac{MaxConnections \cdot 0.8}{NumPoolers}$$

$$TotalPoolSize = PoolSize \cdot NumPoolers$$

#### 5.2.2 VACUUM和ANALYZE调度

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pg-maintenance
  namespace: postgres-production
spec:
  schedule: "0 3 * * 0"  # 每周日凌晨3点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: maintenance
            image: ghcr.io/cloudnative-pg/postgresql:16
            command:
            - /bin/sh
            - -c
            - |
              PRIMARY_POD=$(kubectl get pods -n postgres-production -l cnpg.io/cluster=production-cluster,role=primary -o name | head -1 | cut -d/ -f2)

              # VACUUM ANALYZE所有数据库
              kubectl exec -it ${PRIMARY_POD} -n postgres-production -- psql -c "
                DO \$\$
                DECLARE
                    db RECORD;
                BEGIN
                    FOR db IN SELECT datname FROM pg_database WHERE datallowconn AND NOT datistemplate
                    LOOP
                        RAISE NOTICE 'Processing database: %', db.datname;
                        PERFORM dblink_exec('dbname=' || db.datname, 'VACUUM ANALYZE');
                    END LOOP;
                END \$\$;
              "

              # 重建索引
              kubectl exec -it ${PRIMARY_POD} -n postgres-production -- psql -d appdb -c "
                DO \$\$
                DECLARE
                    idx RECORD;
                BEGIN
                    FOR idx IN
                        SELECT schemaname, tablename, indexname
                        FROM pg_indexes
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                    LOOP
                        EXECUTE 'REINDEX INDEX CONCURRENTLY ' || quote_ident(idx.schemaname) || '.' || quote_ident(idx.indexname);
                    END LOOP;
                END \$\$;
              "
          restartPolicy: OnFailure
          serviceAccountName: pg-maintenance-sa
```

#### 5.2.3 WAL归档管理

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-cluster
spec:
  postgresql:
    parameters:
      # WAL配置
      wal_level: replica
      wal_log_hints: "on"
      wal_compression: "on"
      max_wal_size: "8GB"
      min_wal_size: "2GB"
      checkpoint_timeout: "15min"
      checkpoint_completion_target: "0.9"

      # WAL保留
      wal_keep_size: "2GB"

      # 归档配置
      archive_mode: "on"
      archive_timeout: "5min"

  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      wal:
        retention: "7d"
        compression: gzip
        maxParallel: 4
```

WAL空间计算：

$$WAL_{space} = WAL_{keep} + WAL_{archived} + WAL_{reserve}$$

### 5.3 安全加固

#### 5.3.1 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cnpg-network-policy
  namespace: postgres-production
spec:
  podSelector:
    matchLabels:
      cnpg.io/cluster: production-cluster
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # 允许来自应用命名空间的访问
    - from:
        - namespaceSelector:
            matchLabels:
              name: app-namespace
      ports:
        - protocol: TCP
          port: 5432
    # 允许来自监控系统的访问
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9187
    # 允许集群内部通信
    - from:
        - podSelector:
            matchLabels:
              cnpg.io/cluster: production-cluster
      ports:
        - protocol: TCP
          port: 5432
  egress:
    # 允许访问备份存储
    - to: []
      ports:
        - protocol: TCP
          port: 443
    # 允许DNS查询
    - to: []
      ports:
        - protocol: UDP
          port: 53
```

#### 5.3.2 TLS配置

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: tls-cluster
spec:
  instances: 3

  postgresql:
    parameters:
      ssl: "on"
      ssl_cert_file: /etc/ssl/certs/server.crt
      ssl_key_file: /etc/ssl/private/server.key
      ssl_ca_file: /etc/ssl/certs/ca.crt
      ssl_crl_file: /etc/ssl/certs/ca.crl
      ssl_ciphers: 'HIGH:!aNULL:!MD5'
      ssl_prefer_server_ciphers: "on"
      ssl_min_protocol_version: TLSv1.2

  certificates:
    serverTLSSecret: server-tls-secret
    serverCASecret: server-ca-secret
    replicationTLSSecret: replication-tls-secret
    clientCASecret: client-ca-secret

  storage:
    size: 100Gi
```

#### 5.3.3 RBAC配置

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cnpg-operator-role
  namespace: postgres-production
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims"]
    verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets"]
    verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
  - apiGroups: ["postgresql.cnpg.io"]
    resources: ["clusters", "backups", "scheduledbackups", "poolers"]
    verbs: ["create", "delete", "get", "list", "patch", "update", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cnpg-operator-binding
  namespace: postgres-production
subjects:
  - kind: ServiceAccount
    name: cnpg-operator
    namespace: cnpg-system
roleRef:
  kind: Role
  name: cnpg-operator-role
  apiGroup: rbac.authorization.k8s.io
```

---

## 总结

CloudNativePG将PostgreSQL与Kubernetes深度集成，提供了企业级的数据库即服务体验。通过本文的深度分析，我们掌握了：

1. **Kubernetes存储基础**：StatefulSet、PV/PVC机制、存储类选择
2. **CloudNativePG架构**：Operator模式、故障转移、备份恢复
3. **生产实践**：Helm部署、监控集成、自动扩缩容
4. **高可用设计**：同步复制、跨可用区部署、灾难恢复

在生产环境中，应根据业务需求合理规划集群拓扑、存储配置和备份策略，确保数据安全和服务连续性。

---

## 参考公式汇总

| 编号 | 公式 | 说明 |
|-----|------|------|
| 1 | $DNS_{pod} = \{pod-name\}.\{service-name\}.\{namespace\}.svc.cluster.local$ | Pod DNS命名 |
| 2 | $Pod_{name} = \{statefulset-name\}-\{ordinal\}$ | Pod命名规则 |
| 3 | $Storage_{total} = Storage_{data} + Storage_{wal} + Storage_{backup}$ | 总存储计算 |
| 4 | $IOPS_{required} = \frac{Transactions_{peak} \cdot IO_{per\_transaction}}{Parallelism}$ | IOPS需求 |
| 5 | $IOPS_{io2} = \min(64000, \max(100, VolumeSize_{GiB} \cdot IOPS_{per\_GB}))$ | io2 IOPS计算 |
| 6 | $T_{reconcile} = \frac{1}{frequency_{operator}}$ | 调和周期 |
| 7 | $T_{failover} = T_{detect} + T_{election} + T_{promote} + T_{update}$ | 故障转移时间 |
| 8 | $Score_{replica} = w_1 \cdot \frac{1}{Lag_{replication}} + w_2 \cdot Timeline_{replica} + w_3 \cdot Priority_{replica}$ | 备库评分 |
| 9 | $Backup_{strategy} = 3_{copies} \cdot 2_{media} \cdot 1_{offsite}$ | 备份策略 |
| 10 | $RTO = T_{detect} + T_{decision} + T_{restore} + T_{verify}$ | 恢复时间目标 |
| 11 | $RPO = T_{last\_backup} - T_{failure}$ | 恢复点目标 |
| 12 | $Latency_{cross\_az} = Latency_{intra\_az} + Latency_{backbone}$ | 跨AZ延迟 |

---

*文档版本: v2.0*
*更新日期: 2026-03-04*
*适用版本: PostgreSQL 16 + CloudNativePG 1.22+*

### 5.4 升级与维护

#### 5.4.1 PostgreSQL版本升级

**原地升级（小版本）：**

```yaml
# 修改版本号触发滚动升级
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-cluster
spec:
  postgresql:
    version: "16.3"  # 从16.2升级到16.3
```

升级过程遵循以下顺序：

$$Upgrade_{order} = (replica_n, ..., replica_1, primary)$$

**大版本升级（使用pg_upgrade）：**

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: upgraded-cluster
spec:
  instances: 3
  postgresql:
    version: "17"

  bootstrap:
    pg_upgrade:
      source: production-cluster
      # 升级选项
      options:
        - "--link"  # 使用硬链接加速升级

  externalClusters:
    - name: production-cluster
      connectionParameters:
        host: production-cluster-rw
        port: "5432"
        user: postgres
        database: postgres
      password:
        name: production-cluster-app
        key: password
```

升级时间估算：

$$T_{upgrade} = T_{data\_copy} + T_{catalog\_update} + T_{verification}$$

使用 `--link` 选项时：

$$T_{upgrade}^{link} \approx T_{catalog\_update} \ll T_{data\_copy}$$

#### 5.4.2 滚动维护窗口

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-cluster
  annotations:
    # 维护窗口配置
    cnpg.io/maintenanceWindow: "0 2 * * SUN"  # 每周日凌晨2点
spec:
  instances: 3

  # 节点维护时的Pod驱逐处理
  nodeMaintenanceWindow:
    inProgress: false
    reusePVC: true  # 节点恢复后重用原有PVC
```

#### 5.4.3 配置热重载

```sql
-- 无需重启的在线配置调整
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
SELECT pg_reload_conf();

-- 验证配置
SHOW work_mem;
SHOW maintenance_work_mem;
```

### 5.5 故障排查

#### 5.5.1 常见故障场景

**Pod启动失败排查：**

```bash
# 查看Pod事件
kubectl describe pod production-cluster-0 -n postgres-production

# 查看Operator日志
kubectl logs -n cnpg-system deployment/cnpg-controller-manager | grep production-cluster

# 检查PVC绑定状态
kubectl get pvc -n postgres-production -l cnpg.io/cluster=production-cluster

# 检查存储类
kubectl get storageclass
kubectl describe storageclass premium-rwo
```

**复制延迟排查：**

```bash
# 进入主库查看复制状态
kubectl exec -it production-cluster-0 -n postgres-production -- psql -c "
SELECT
    client_addr,
    usename,
    application_name,
    state,
    sync_state,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes,
    reply_time
FROM pg_stat_replication;
"

# 备库查看接收状态
kubectl exec -it production-cluster-1 -n postgres-production -- psql -c "
SELECT
    pg_last_wal_receive_lsn() as receive_lsn,
    pg_last_wal_replay_lsn() as replay_lsn,
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as apply_lag,
    pg_last_xact_replay_timestamp() as last_replay_time;
"
```

#### 5.5.2 日志分析

```bash
# 收集集群日志
kubectl cnpg logs production-cluster -n postgres-production --tail 1000 > cluster-logs.txt

# 查看特定时间段的错误
kubectl logs -n postgres-production production-cluster-0 --since=1h | grep -i error

# 查看慢查询
kubectl exec -it production-cluster-0 -n postgres-production -- psql -c "
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
"
```

#### 5.5.3 性能瓶颈诊断

```sql
-- 检查锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_app,
    blocking_activity.application_name AS blocking_app
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 检查长时间运行的查询
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    xact_start,
    query_start,
    state,
    wait_event_type,
    wait_event,
    LEFT(query, 100) AS query_preview
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY query_start;
```

### 5.6 多租户架构

#### 5.6.1 命名空间隔离

```yaml
# 生产租户
apiVersion: v1
kind: Namespace
metadata:
  name: postgres-tenant-a
  labels:
    tenant: tenant-a
    environment: production
---
# 开发租户
apiVersion: v1
kind: Namespace
metadata:
  name: postgres-tenant-b
  labels:
    tenant: tenant-b
    environment: development
---
# 每个租户独立集群
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: tenant-a-db
  namespace: postgres-tenant-a
spec:
  instances: 3
  resources:
    requests:
      memory: "8Gi"
      cpu: "4"
    limits:
      memory: "16Gi"
      cpu: "8"
  storage:
    size: 500Gi
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: tenant-b-db
  namespace: postgres-tenant-b
spec:
  instances: 1  # 开发环境单实例
  resources:
    requests:
      memory: "2Gi"
      cpu: "1"
    limits:
      memory: "4Gi"
      cpu: "2"
  storage:
    size: 50Gi
```

#### 5.6.2 资源配额管理

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: postgres-quota
  namespace: postgres-tenant-a
spec:
  hard:
    requests.storage: "1Ti"
    persistentvolumeclaims: "10"
    pods: "20"
    requests.memory: "64Gi"
    requests.cpu: "32"
    limits.memory: "128Gi"
    limits.cpu: "64"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: postgres-limits
  namespace: postgres-tenant-a
spec:
  limits:
    - default:
        memory: "4Gi"
        cpu: "2"
      defaultRequest:
        memory: "2Gi"
        cpu: "1"
      type: Container
```

---

## 6. 实战案例研究

### 6.1 金融交易系统

**场景：** 高频交易系统，要求RTO < 30秒，RPO = 0

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: trading-db
  namespace: finance-production
spec:
  instances: 5  # 更多副本提高可用性

  postgresql:
    version: "16"
    parameters:
      # 极致性能配置
      max_connections: "1000"
      shared_buffers: "8GB"
      effective_cache_size: "24GB"
      work_mem: "64MB"
      maintenance_work_mem: "2GB"

      # WAL优化
      wal_level: replica
      wal_sync_method: open_sync  # 直接同步
      synchronous_commit: remote_apply  # 同步应用到备库
      wal_writer_delay: "1ms"
      wal_writer_flush_after: "0"

      # 检查点优化
      checkpoint_timeout: "10min"
      max_wal_size: "16GB"
      min_wal_size: "4GB"
      checkpoint_completion_target: "0.95"

      # 并发优化
      max_worker_processes: "32"
      max_parallel_workers_per_gather: "16"
      max_parallel_workers: "32"
      max_parallel_maintenance_workers: "8"

    synchronous:
      method: first
      number: 2  # 至少2个备库确认

  storage:
    size: 2Ti
    storageClass: io2-optimized

  resources:
    requests:
      memory: "32Gi"
      cpu: "16"
    limits:
      memory: "64Gi"
      cpu: "32"

  affinity:
    enablePodAntiAffinity: true
    topologyKey: topology.kubernetes.io/zone

  failover:
    switchoverDelay: 10  # 快速切换
    failoverDelay: 5

  backup:
    retentionPolicy: "7d"  # 短期保留，快速恢复
    barmanObjectStore:
      destinationPath: "s3://trading-backups/db"
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: SECRET_ACCESS_KEY
      data:
        compression: none  # 不压缩，追求速度
        jobs: 8
```

### 6.2 电商平台

**场景：** 大型电商平台，需要读写分离和自动扩缩容

```yaml
# 主集群
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: ecommerce-db
  namespace: ecommerce-production
spec:
  instances: 3
  postgresql:
    version: "16"
    parameters:
      max_connections: "500"
      shared_buffers: "4GB"
  storage:
    size: 1Ti
  resources:
    requests:
      memory: "8Gi"
      cpu: "4"
    limits:
      memory: "16Gi"
      cpu: "8"
---
# 只读副本池（水平扩展读流量）
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: ecommerce-db-replicas
  namespace: ecommerce-production
spec:
  instances: 5  # 更多只读副本
  postgresql:
    version: "16"
    parameters:
      max_connections: "200"
      shared_buffers: "2GB"
  storage:
    size: 1Ti
  resources:
    requests:
      memory: "4Gi"
      cpu: "2"
    limits:
      memory: "8Gi"
      cpu: "4"

  replica:
    enabled: true
    source: ecommerce-db
---
# 连接池配置
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: ecommerce-rw-pooler
spec:
  cluster:
    name: ecommerce-db
  instances: 3
  type: rw
  poolMode: transaction
  parameters:
    max_client_conn: "20000"
    default_pool_size: "100"
---
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: ecommerce-ro-pooler
spec:
  cluster:
    name: ecommerce-db
  instances: 5
  type: ro
  poolMode: session
  parameters:
    max_client_conn: "50000"
    default_pool_size: "200"
---
# HPA自动扩缩容
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ecommerce-pooler-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ecommerce-ro-pooler
  minReplicas: 5
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### 6.3 SaaS多租户数据库

**场景：** SaaS平台，每个租户独立Schema

```sql
-- 创建租户管理函数
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_id TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', 'tenant_' || tenant_id);

    -- 创建租户表
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )', 'tenant_' || tenant_id);

    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.orders (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES %I.users(id),
            amount DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT NOW()
        )', 'tenant_' || tenant_id, 'tenant_' || tenant_id);

    -- 设置默认搜索路径
    EXECUTE format('
        ALTER DATABASE current_database()
        SET search_path = %L, public', 'tenant_' || tenant_id);
END;
$$ LANGUAGE plpgsql;

-- 连接时自动切换Schema
CREATE OR REPLACE FUNCTION set_tenant_schema()
RETURNS EVENT_TRIGGER AS $$
DECLARE
    tenant_id TEXT;
BEGIN
    -- 从应用上下文获取租户ID
    tenant_id := current_setting('app.current_tenant', true);
    IF tenant_id IS NOT NULL AND tenant_id != '' THEN
        EXECUTE format('SET search_path = %I, public', 'tenant_' || tenant_id);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 监控各租户资源使用
CREATE VIEW tenant_resource_usage AS
SELECT
    schemaname,
    pg_size_pretty(sum(pg_total_relation_size(schemaname || '.' || tablename))) AS total_size,
    count(*) AS table_count
FROM pg_tables
WHERE schemaname LIKE 'tenant_%'
GROUP BY schemaname;
```

```yaml
# CloudNativePG配置
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: saas-tenant-db
  namespace: saas-production
spec:
  instances: 3
  postgresql:
    version: "16"
    parameters:
      # 支持大量schema
      max_locks_per_transaction: "512"
      max_pred_locks_per_transaction: "128"

      # 连接配置
      max_connections: "1000"
      shared_buffers: "8GB"
      effective_cache_size: "24GB"

      # 自动清理优化
      autovacuum_max_workers: "6"
      autovacuum_naptime: "10s"

  storage:
    size: 2Ti

  # 按tenant_id分区备份
  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      destinationPath: "s3://saas-backups/tenants"
      s3Credentials:
        accessKeyId:
          name: backup-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-creds
          key: SECRET_ACCESS_KEY
```

---

## 7. 性能基准测试

### 7.1 pgbench测试

```bash
#!/bin/bash
# pgbench-benchmark.sh

CLUSTER_NAME="production-cluster"
NAMESPACE="postgres-production"
DB_NAME="appdb"

# 获取主库服务
DB_HOST=$(kubectl get service ${CLUSTER_NAME}-rw -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
DB_PORT="5432"
DB_USER="app"

# 初始化测试数据
kubectl exec -it ${CLUSTER_NAME}-0 -n ${NAMESPACE} -- pgbench \
    -h localhost \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -i \
    -s 100  # 规模因子

# 运行基准测试
echo "=== 开始基准测试 ==="

# 只读测试
echo "只读测试 (SELECT-only):"
kubectl exec -it ${CLUSTER_NAME}-0 -n ${NAMESPACE} -- pgbench \
    -h localhost \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -c 50 \  # 50并发连接
    -j 10 \  # 10线程
    -T 300 \ # 运行300秒
    -S       # 只读模式

# 读写混合测试
echo "读写混合测试:"
kubectl exec -it ${CLUSTER_NAME}-0 -n ${NAMESPACE} -- pgbench \
    -h localhost \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -c 100 \
    -j 20 \
    -T 300

# 写入压力测试
echo "写入压力测试:"
kubectl exec -it ${CLUSTER_NAME}-0 -n ${NAMESPACE} -- pgbench \
    -h localhost \
    -U ${DB_USER} \
    -d ${DB_NAME} \
    -c 50 \
    -j 10 \
    -T 300 \
    -N  # 跳过更新以测试INSERT

echo "=== 基准测试完成 ==="
```

### 7.2 性能指标收集

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pgbench-metrics
  namespace: monitoring
data:
  queries.yaml: |
    pg_stat_pgbench_tps:
      query: |
        SELECT
          'transactions_per_second' as metric,
          xact_commit / GREATEST(extract(epoch from (now() - stats_reset)), 1) as value
        FROM pg_stat_database
        WHERE datname = current_database()
      metrics:
        - metric:
            usage: LABEL
          value:
            usage: GAUGE

    pg_stat_query_latency:
      query: |
        SELECT
          quantile
          percentile_cont(0.99) WITHIN GROUP (ORDER BY mean_exec_time) as p99_latency,
          percentile_cont(0.95) WITHIN GROUP (ORDER BY mean_exec_time) as p95_latency,
          avg(mean_exec_time) as avg_latency
        FROM pg_stat_statements
      metrics:
        - p99_latency:
            usage: GAUGE
            description: P99 query latency in ms
        - p95_latency:
            usage: GAUGE
            description: P95 query latency in ms
        - avg_latency:
            usage: GAUGE
            description: Average query latency in ms
```

---

## 8. 最佳实践总结

### 8.1 部署检查清单

**基础设施：**

- [ ] 存储类支持动态卷供应
- [ ] 存储类支持卷扩容
- [ ] 节点有足够的资源（CPU/内存）
- [ ] 网络策略允许Pod间通信
- [ ] 备份存储桶已创建并配置权限

**集群配置：**

- [ ] 实例数 >= 3（生产环境）
- [ ] 资源配置（requests/limits）合理
- [ ] 反亲和性配置启用
- [ ] 同步复制配置符合RPO要求
- [ ] 备份策略配置完成
- [ ] 监控告警配置完成

**安全配置：**

- [ ] TLS证书已配置
- [ ] 网络策略已应用
- [ ] RBAC权限已配置
- [ ] 数据库密码使用Secret管理
- [ ] 备份加密已启用

### 8.2 运维黄金法则

1. **备份验证**：定期测试备份恢复流程
2. **监控先行**：部署前先配置监控告警
3. **渐进变更**：小批量滚动更新，避免大规模同时变更
4. **容量规划**：提前规划存储扩容，避免磁盘满
5. **文档记录**：所有变更都有文档记录和回滚方案

### 8.3 容量规划公式

**存储容量规划：**

$$Storage_{required} = Data_{initial} \cdot GrowthRate^{Years} \cdot (1 + Overhead_{wal} + Overhead_{backup})$$

其中：

- $Data_{initial}$: 初始数据量
- $GrowthRate$: 年增长率（如1.5表示年增长50%）
- $Overhead_{wal}$: WAL开销（通常10-20%）
- $Overhead_{backup}$: 备份开销（取决于保留策略）

**连接数规划：**

$$Connections_{max} = Applications \cdot Connections_{per\_app} \cdot PeakFactor$$

$$PoolSize = \frac{Connections_{max}}{NumPoolers} \cdot ConnectionReuseRatio$$

**内存配置：**

$$SharedBuffers = \min(25\% \cdot TotalMemory, 32GB)$$

$$EffectiveCacheSize = TotalMemory - SharedBuffers - OSOverhead$$

$$WorkMem = \frac{TotalMemory - SharedBuffers}{MaxConnections \cdot 0.5}$$

---

## 总结

CloudNativePG将PostgreSQL与Kubernetes深度集成，提供了企业级的数据库即服务体验。通过本文的深度分析，我们掌握了：

1. **Kubernetes存储基础**：StatefulSet、PV/PVC机制、存储类选择
2. **CloudNativePG架构**：Operator模式、故障转移、备份恢复
3. **生产实践**：Helm部署、监控集成、自动扩缩容
4. **高可用设计**：同步复制、跨可用区部署、灾难恢复
5. **运维管理**：日常运维、性能调优、安全加固、故障排查
6. **实战案例**：金融交易系统、电商平台、SaaS多租户架构

在生产环境中，应根据业务需求合理规划集群拓扑、存储配置和备份策略，确保数据安全和服务连续性。

---

## 参考公式汇总

| 编号 | 公式 | 说明 |
|-----|------|------|
| 1 | $DNS_{pod} = \{pod-name\}.\{service-name\}.\{namespace\}.svc.cluster.local$ | Pod DNS命名 |
| 2 | $Pod_{name} = \{statefulset-name\}-\{ordinal\}$ | Pod命名规则 |
| 3 | $Storage_{total} = Storage_{data} + Storage_{wal} + Storage_{backup}$ | 总存储计算 |
| 4 | $IOPS_{required} = \frac{Transactions_{peak} \cdot IO_{per\_transaction}}{Parallelism}$ | IOPS需求 |
| 5 | $IOPS_{io2} = \min(64000, \max(100, VolumeSize_{GiB} \cdot IOPS_{per\_GB}))$ | io2 IOPS计算 |
| 6 | $T_{reconcile} = \frac{1}{frequency_{operator}}$ | 调和周期 |
| 7 | $T_{failover} = T_{detect} + T_{election} + T_{promote} + T_{update}$ | 故障转移时间 |
| 8 | $Score_{replica} = w_1 \cdot \frac{1}{Lag_{replication}} + w_2 \cdot Timeline_{replica} + w_3 \cdot Priority_{replica}$ | 备库评分 |
| 9 | $Backup_{strategy} = 3_{copies} \cdot 2_{media} \cdot 1_{offsite}$ | 备份策略 |
| 10 | $RTO = T_{detect} + T_{decision} + T_{restore} + T_{verify}$ | 恢复时间目标 |
| 11 | $RPO = T_{last\_backup} - T_{failure}$ | 恢复点目标 |
| 12 | $Latency_{cross\_az} = Latency_{intra\_az} + Latency_{backbone}$ | 跨AZ延迟 |

---

*文档版本: v2.0*
*更新日期: 2026-03-04*
*适用版本: PostgreSQL 16 + CloudNativePG 1.22+*
