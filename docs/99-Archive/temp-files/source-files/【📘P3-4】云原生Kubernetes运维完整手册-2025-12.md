# 📘 云原生Kubernetes运维完整手册

> **更新日期**: 2025年12月4日
> **适用环境**: Kubernetes + PostgreSQL
> **文档类型**: P3持续实践手册

---

## 📑 目录

- [一、Kubernetes部署最佳实践](#一kubernetes部署最佳实践)
- [二、Operator运维](#二operator运维)
- [三、备份恢复](#三备份恢复)
- [四、监控告警](#四监控告警)
- [五、扩容缩容](#五扩容缩容)
- [六、故障恢复](#六故障恢复)
- [七、安全加固](#七安全加固)
- [八、性能优化](#八性能优化)

---

## 一、Kubernetes部署最佳实践

### 1.1 StatefulSet部署

```yaml
# postgresql-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  serviceName: postgresql
  replicas: 3
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:18
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
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
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 5
          periodSeconds: 5
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

### 1.2 Service配置

```yaml
# postgresql-service.yaml
---
# Headless Service for StatefulSet
apiVersion: v1
kind: Service
metadata:
  name: postgresql
spec:
  clusterIP: None
  selector:
    app: postgresql
  ports:
  - port: 5432
    name: postgres

---
# Read-Write Service (Primary)
apiVersion: v1
kind: Service
metadata:
  name: postgresql-rw
spec:
  selector:
    app: postgresql
    role: primary
  ports:
  - port: 5432
    targetPort: 5432

---
# Read-Only Service (Replicas)
apiVersion: v1
kind: Service
metadata:
  name: postgresql-ro
spec:
  selector:
    app: postgresql
    role: replica
  ports:
  - port: 5432
    targetPort: 5432
```

---

## 二、Operator运维

### 2.1 安装Zalando Postgres Operator

```bash
# 添加Helm repo
helm repo add postgres-operator https://opensource.zalando.com/postgres-operator/charts/postgres-operator
helm repo update

# 安装Operator
helm install postgres-operator postgres-operator/postgres-operator \
  --namespace postgres-operator \
  --create-namespace

# 安装UI
helm install postgres-operator-ui postgres-operator/postgres-operator-ui \
  --namespace postgres-operator
```

### 2.2 创建PostgreSQL集群

```yaml
# postgresql-cluster.yaml
apiVersion: "acid.zalan.do/v1"
kind: postgresql
metadata:
  name: acid-cluster
spec:
  teamId: "acid"
  volume:
    size: 100Gi
    storageClass: fast-ssd
  numberOfInstances: 3
  users:
    app_user:
    - superuser
    - createdb
  databases:
    mydb: app_user
  postgresql:
    version: "18"
    parameters:
      shared_buffers: "2GB"
      max_connections: "200"
      work_mem: "10MB"
  resources:
    requests:
      cpu: "1000m"
      memory: "2Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"
  patroni:
    pg_hba:
    - hostssl all all 0.0.0.0/0 md5
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
```

### 2.3 常用Operator操作

```bash
# 查看集群状态
kubectl get postgresql

# 查看Pod状态
kubectl get pods -l cluster-name=acid-cluster

# 查看服务
kubectl get svc -l cluster-name=acid-cluster

# 扩容
kubectl patch postgresql acid-cluster --type='merge' \
  -p '{"spec":{"numberOfInstances":5}}'

# 手动故障转移
kubectl annotate postgresql acid-cluster \
  "acid.zalan.do/manual-failover=true"
```

---

## 三、备份恢复

### 3.1 使用PgBackRest

```yaml
# pgbackrest-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pgbackrest-config
data:
  pgbackrest.conf: |
    [global]
    repo1-path=/pgbackrest
    repo1-retention-full=7
    repo1-retention-diff=2

    [acid-cluster]
    pg1-path=/var/lib/postgresql/data/pgdata
    pg1-port=5432
    pg1-socket-path=/var/run/postgresql
```

```bash
# 全量备份
kubectl exec -it acid-cluster-0 -- \
  pgbackrest --stanza=acid-cluster backup --type=full

# 增量备份
kubectl exec -it acid-cluster-0 -- \
  pgbackrest --stanza=acid-cluster backup --type=incr

# 查看备份
kubectl exec -it acid-cluster-0 -- \
  pgbackrest --stanza=acid-cluster info
```

### 3.2 恢复

```bash
# 恢复到最新
kubectl exec -it acid-cluster-0 -- \
  pgbackrest --stanza=acid-cluster restore

# PITR恢复
kubectl exec -it acid-cluster-0 -- \
  pgbackrest --stanza=acid-cluster restore \
  --target="2025-12-01 12:00:00" \
  --type=time
```

---

## 四、监控告警

### 4.1 Prometheus监控

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: postgresql
spec:
  selector:
    matchLabels:
      app: postgresql
  endpoints:
  - port: metrics
    interval: 30s
```

### 4.2 Grafana仪表板

推荐使用：
- PostgreSQL Database (ID: 9628)
- PostgreSQL Exporter Quickstart (ID: 14114)

---

## 五、扩容缩容

### 5.1 垂直扩容（资源）

```bash
# 修改资源限制
kubectl patch postgresql acid-cluster --type='merge' -p '
{
  "spec": {
    "resources": {
      "requests": {"cpu": "2000m", "memory": "4Gi"},
      "limits": {"cpu": "4000m", "memory": "8Gi"}
    }
  }
}'

# 自动重启Pod应用更改
```

### 5.2 水平扩容（副本）

```bash
# 增加副本
kubectl patch postgresql acid-cluster --type='merge' \
  -p '{"spec":{"numberOfInstances":5}}'

# 减少副本（谨慎！）
kubectl patch postgresql acid-cluster --type='merge' \
  -p '{"spec":{"numberOfInstances":3}}'
```

---

## 六、故障恢复

### 6.1 Pod故障

```bash
# 查看Pod状态
kubectl get pods -l cluster-name=acid-cluster

# 查看Pod日志
kubectl logs acid-cluster-0

# 删除故障Pod（自动重建）
kubectl delete pod acid-cluster-0
```

### 6.2 主库故障

```bash
# Patroni自动故障转移
# 无需手动干预

# 查看新主库
kubectl get pods -l cluster-name=acid-cluster,spilo-role=master
```

### 6.3 存储故障

```bash
# 如果PVC损坏，从备份恢复
# 1. 删除故障Pod和PVC
kubectl delete pod acid-cluster-0
kubectl delete pvc pgdata-acid-cluster-0

# 2. 等待自动重建
# 3. 从备份恢复数据
```

---

## 七、安全加固

### 7.1 Secret管理

```yaml
# postgresql-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgresql-secret
type: Opaque
stringData:
  password: "strong_password_here"
  replication-password: "replication_password"
```

```bash
# 使用Sealed Secrets（推荐）
kubectl create secret generic postgresql-secret \
  --from-literal=password=strong_password \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

kubectl apply -f sealed-secret.yaml
```

### 7.2 Network Policy

```yaml
# networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: postgresql-netpol
spec:
  podSelector:
    matchLabels:
      app: postgresql
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: app-namespace
    ports:
    - protocol: TCP
      port: 5432
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
```

---

## 八、性能优化

### 8.1 资源QoS

```yaml
# 保证QoS
resources:
  requests:
    cpu: "2000m"
    memory: "4Gi"
  limits:
    cpu: "2000m"     # 相等 = Guaranteed
    memory: "4Gi"    # 相等 = Guaranteed
```

### 8.2 节点亲和性

```yaml
# 使用高性能节点
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: node-type
          operator: In
          values:
          - high-performance
```

### 8.3 拓扑分布

```yaml
# Pod分布到不同可用区
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      app: postgresql
```

---

**🚀 云原生时代，Kubernetes + PostgreSQL完美结合！** ☸️

---

**最后更新**: 2025年12月4日
**维护者**: PostgreSQL Modern Team
**文档编号**: P3-4-K8S-OPS-2025-12
