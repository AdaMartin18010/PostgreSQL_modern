# PostgreSQL 18 on Kubernetes 生产部署完整指南

## 1. CloudNativePG Operator

### 1.1 Operator安装

```bash
# 安装CloudNativePG Operator
kubectl apply -f \
  https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.21/releases/cnpg-1.21.0.yaml

# 验证安装
kubectl get deployment -n cnpg-system cnpg-controller-manager

# 检查CRD
kubectl get crd | grep postgresql
```

### 1.2 核心概念

```yaml
# Cluster CRD - 主要资源
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: pg-cluster
spec:
  instances: 3  # 1主2从
  postgresql:
    parameters:
      max_connections: "200"
      shared_buffers: "2GB"

  storage:
    size: 100Gi
    storageClass: fast-ssd

  backup:
    barmanObjectStore:
      destinationPath: s3://backups/pg
      s3Credentials:
        accessKeyId:
          name: s3-creds
          key: ACCESS_KEY_ID
```

---

## 2. 集群部署

### 2.1 基础PostgreSQL集群

```yaml
# pg-cluster.yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: production-pg
  namespace: database
spec:
  instances: 3

  imageName: ghcr.io/cloudnative-pg/postgresql:18

  postgresql:
    parameters:
      # 性能参数
      shared_buffers: "4GB"
      effective_cache_size: "12GB"
      maintenance_work_mem: "1GB"
      work_mem: "256MB"

      # WAL参数
      wal_level: "replica"
      max_wal_size: "4GB"

      # 连接参数
      max_connections: "200"

      # PostgreSQL 18新特性
      io_direct: "data"
      io_combine_limit: "128kB"

    pg_hba:
      - host all all 10.0.0.0/8 scram-sha-256
      - host replication streaming 10.0.0.0/8 scram-sha-256

  # 主从复制
  replicationSlots:
    highAvailability:
      enabled: true
    updateInterval: 30

  # 存储
  storage:
    size: 500Gi
    storageClass: ceph-rbd-ssd
    pvcTemplate:
      accessModes:
        - ReadWriteOnce
      resources:
        requests:
          storage: 500Gi

  # 资源限制
  resources:
    requests:
      cpu: "4"
      memory: "16Gi"
    limits:
      cpu: "8"
      memory: "32Gi"

  # 监控
  monitoring:
    enabled: true
    podMonitorEnabled: true

  # 备份
  backup:
    barmanObjectStore:
      destinationPath: s3://pg-backups/production
      wal:
        compression: gzip
        maxParallel: 2
      data:
        compression: gzip
        jobs: 4
      s3Credentials:
        accessKeyId:
          name: s3-creds
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: s3-creds
          key: SECRET_ACCESS_KEY

    retentionPolicy: "30d"

  # 高可用
  failoverDelay: 0
  switchoverDelay: 60

  # 节点亲和性
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: postgresql
                operator: In
                values:
                  - production-pg
          topologyKey: kubernetes.io/hostname
```

### 2.2 部署

```bash
# 创建namespace
kubectl create namespace database

# 创建secrets
kubectl create secret generic s3-creds \
  --from-literal=ACCESS_KEY_ID=xxx \
  --from-literal=SECRET_ACCESS_KEY=yyy \
  -n database

# 部署集群
kubectl apply -f pg-cluster.yaml

# 查看状态
kubectl get cluster -n database
kubectl get pods -n database -l postgresql=production-pg

# 查看详细信息
kubectl describe cluster production-pg -n database
```

---

## 3. 连接与访问

### 3.1 Service配置

```yaml
# 自动创建的Services:
# 1. production-pg-rw (读写，指向Primary)
# 2. production-pg-ro (只读，指向所有实例)
# 3. production-pg-r  (只读，只指向Replica)

# 应用连接示例
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DB_HOST: "production-pg-rw.database.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "mydb"
  DB_USER: "app"
```

### 3.2 连接池（PgBouncer）

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: pg-pooler
  namespace: database
spec:
  cluster:
    name: production-pg

  instances: 3
  type: rw  # rw 或 ro

  pgbouncer:
    poolMode: transaction
    parameters:
      max_client_conn: "1000"
      default_pool_size: "25"
      reserve_pool_size: "5"
      server_idle_timeout: "600"

  template:
    spec:
      containers:
        - name: pgbouncer
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
```

---

## 4. 备份与恢复

### 4.1 定时备份

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: daily-backup
  namespace: database
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  backupOwnerReference: self
  cluster:
    name: production-pg

  immediate: false

  target: primary
```

### 4.2 按需备份

```bash
# 创建即时备份
kubectl cnpg backup production-pg -n database

# 查看备份
kubectl get backup -n database

# 备份详情
kubectl describe backup production-pg-20231204 -n database
```

### 4.3 恢复

```yaml
# 从备份恢复新集群
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: restored-pg
spec:
  instances: 3

  bootstrap:
    recovery:
      source: production-pg
      recoveryTarget:
        targetTime: "2023-12-04 12:00:00"  # PITR

  externalClusters:
    - name: production-pg
      barmanObjectStore:
        destinationPath: s3://pg-backups/production
        s3Credentials:
          accessKeyId:
            name: s3-creds
            key: ACCESS_KEY_ID
          secretAccessKey:
            name: s3-creds
            key: SECRET_ACCESS_KEY

  storage:
    size: 500Gi
```

---

## 5. 监控

### 5.1 Prometheus集成

```yaml
# ServiceMonitor (自动创建)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: production-pg
spec:
  selector:
    matchLabels:
      postgresql: production-pg
  endpoints:
    - port: metrics
      interval: 30s
```

### 5.2 关键指标

```promql
# 数据库状态
pg_up

# 主从延迟
pg_replication_lag_seconds

# 连接数
pg_stat_database_numbackends

# TPS
rate(pg_stat_database_xact_commit[5m])

# 缓存命中率
rate(pg_stat_database_blks_hit[5m]) /
(rate(pg_stat_database_blks_hit[5m]) + rate(pg_stat_database_blks_read[5m]))

# 慢查询
pg_stat_statements_mean_exec_time_seconds > 1
```

### 5.3 Grafana Dashboard

```json
{
  "dashboard": {
    "title": "PostgreSQL CloudNativePG",
    "panels": [
      {
        "title": "Database Status",
        "targets": [
          {
            "expr": "pg_up{cluster=\"production-pg\"}"
          }
        ]
      },
      {
        "title": "Replication Lag",
        "targets": [
          {
            "expr": "pg_replication_lag_seconds{cluster=\"production-pg\"}"
          }
        ]
      },
      {
        "title": "QPS",
        "targets": [
          {
            "expr": "rate(pg_stat_database_xact_commit{cluster=\"production-pg\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## 6. 高可用测试

### 6.1 故障模拟

```bash
# 1. 删除Primary Pod
PRIMARY=$(kubectl get pod -n database \
  -l "postgresql=production-pg,role=primary" \
  -o jsonpath='{.items[0].metadata.name}')

kubectl delete pod $PRIMARY -n database

# 观察自动failover
kubectl get pods -n database -w

# 2. 节点故障
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data

# 3. 网络分区（使用Chaos Mesh）
kubectl apply -f network-partition.yaml
```

### 6.2 Switchover

```bash
# 手动切换主节点
kubectl cnpg promote production-pg-2 -n database

# 查看新的Primary
kubectl get cluster production-pg -n database -o jsonpath='{.status.currentPrimary}'
```

---

## 7. 扩缩容

### 7.1 水平扩容

```bash
# 增加副本
kubectl cnpg scale production-pg --replicas=5 -n database

# 减少副本
kubectl cnpg scale production-pg --replicas=2 -n database
```

### 7.2 垂直扩容

```yaml
# 更新资源配置
spec:
  resources:
    requests:
      cpu: "8"
      memory: "32Gi"
    limits:
      cpu: "16"
      memory: "64Gi"
```

### 7.3 存储扩容

```bash
# 编辑PVC
kubectl edit pvc production-pg-1 -n database

# 修改size
spec:
  resources:
    requests:
      storage: 1Ti  # 从500Gi增加到1Ti
```

---

## 8. 安全加固

### 8.1 TLS配置

```yaml
spec:
  certificates:
    serverTLSSecret: pg-server-cert
    serverCASecret: pg-ca-cert
    clientCASecret: pg-client-ca
    replicationTLSSecret: pg-replication-cert
```

### 8.2 RBAC

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pg-operator
  namespace: database
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pg-operator
rules:
  - apiGroups: ["postgresql.cnpg.io"]
    resources: ["clusters"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pg-operator
subjects:
  - kind: ServiceAccount
    name: pg-operator
roleRef:
  kind: Role
  name: pg-operator
  apiGroup: rbac.authorization.k8s.io
```

### 8.3 Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: pg-netpol
spec:
  podSelector:
    matchLabels:
      postgresql: production-pg
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: myapp
      ports:
        - protocol: TCP
          port: 5432
```

---

## 9. 升级策略

### 9.1 滚动升级

```yaml
spec:
  imageName: ghcr.io/cloudnative-pg/postgresql:18.1

  primaryUpdateStrategy: unsupervised
  primaryUpdateMethod: switchover
```

### 9.2 升级流程

```bash
# 1. 查看当前版本
kubectl get cluster production-pg -o jsonpath='{.spec.imageName}'

# 2. 更新镜像
kubectl cnpg upgrade production-pg \
  --image ghcr.io/cloudnative-pg/postgresql:18.1 \
  -n database

# 3. 监控升级
kubectl get pods -n database -w

# 4. 验证
kubectl exec -it production-pg-1 -n database -- psql -U postgres -c "SELECT version();"
```

---

## 10. 故障排查

### 10.1 常见问题

**Pod无法启动**:

```bash
# 查看日志
kubectl logs production-pg-1 -n database

# 查看事件
kubectl describe pod production-pg-1 -n database

# 检查PVC
kubectl get pvc -n database
```

**主从同步延迟**:

```bash
# 查看复制状态
kubectl exec -it production-pg-1 -n database -- \
  psql -U postgres -c "SELECT * FROM pg_stat_replication;"

# 检查网络
kubectl exec -it production-pg-1 -n database -- \
  ping production-pg-2.production-pg-pods
```

**备份失败**:

```bash
# 查看backup对象
kubectl describe backup production-pg-backup -n database

# 检查S3连接
kubectl exec -it production-pg-1 -n database -- \
  barman-cloud-backup-list s3://pg-backups/production
```

---

## 11. 生产最佳实践

### 11.1 资源规划

```yaml
# 生产环境推荐配置
spec:
  instances: 3  # 至少3个实例

  resources:
    requests:
      cpu: "4"      # 4核起步
      memory: "16Gi"  # 16GB内存
    limits:
      cpu: "8"
      memory: "32Gi"

  storage:
    size: 500Gi    # 根据数据量规划
    storageClass: high-performance-ssd
```

### 11.2 监控告警

```yaml
# PrometheusRule
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: pg-alerts
spec:
  groups:
    - name: postgresql
      rules:
        - alert: PostgreSQLDown
          expr: pg_up == 0
          for: 1m
          annotations:
            summary: "PostgreSQL实例宕机"

        - alert: ReplicationLagHigh
          expr: pg_replication_lag_seconds > 60
          for: 5m
          annotations:
            summary: "主从延迟过高"

        - alert: ConnectionsHigh
          expr: pg_stat_database_numbackends > 180
          for: 5m
          annotations:
            summary: "连接数接近上限"
```

### 11.3 备份策略

```text
备份方案:
├─ 每日全量备份 (保留30天)
├─ 实时WAL归档
├─ 每周验证恢复
└─ 异地备份副本
```

---

**完成**: Kubernetes生产部署完整指南
**字数**: ~10,000字
**涵盖**: CloudNativePG、HA、监控、备份、安全
