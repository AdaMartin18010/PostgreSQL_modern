# 17. 容器化部署指南

> **章节编号**: 17
> **章节标题**: 容器化部署指南
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

**返回**: [文档首页](../README.md) | [上一章节](../16-性能测试工具/README.md) | [下一章节](../18-CICD集成/README.md)

## 📑 目录

- [17.1 Docker部署](#171-docker部署)
- [17.2 Kubernetes部署](#172-kubernetes部署)
- [17.3 容器化性能优化](#173-容器化性能优化)
- [17.4 容器化部署检查清单](#174-容器化部署检查清单)

---

## 17. 容器化部署指南

### 17.1 Docker部署

**Dockerfile示例（PostgreSQL 18 + 异步I/O）**:

```dockerfile
# PostgreSQL 18 Dockerfile with Async I/O Support
FROM postgres:18

# 设置环境变量
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --locale=C"

# 复制配置文件
COPY postgresql.conf /etc/postgresql/postgresql.conf
COPY pg_hba.conf /etc/postgresql/pg_hba.conf

# 创建初始化脚本
COPY init-async-io.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-async-io.sh

# 暴露端口
EXPOSE 5432

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U postgres || exit 1
```

**postgresql.conf配置（异步I/O优化）**:

```ini
# PostgreSQL 18异步I/O配置（Docker环境）
# 文件: postgresql.conf

# 异步I/O配置
io_direct = 'data,wal'
effective_io_concurrency = 200
maintenance_io_concurrency = 200
wal_io_concurrency = 200

# 内存配置（根据容器资源调整）
shared_buffers = 256MB  # 容器环境推荐值
work_mem = 16MB
maintenance_work_mem = 128MB

# 连接配置
max_connections = 100
enable_builtin_connection_pooling = on
connection_pool_size = 50

# 监控配置
track_io_timing = on
log_min_duration_statement = 1000
```

**初始化脚本（init-async-io.sh）**:

```bash
#!/bin/bash
# PostgreSQL 18异步I/O初始化脚本（Docker环境）
set -e

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

echo "=== PostgreSQL 18异步I/O初始化 ==="

# 检查系统支持（Linux）
if [ "$(uname)" = "Linux" ]; then
    KERNEL_VERSION=$(uname -r | cut -d. -f1,2)
    echo "内核版本: $KERNEL_VERSION"

    if [ "$(echo "$KERNEL_VERSION >= 5.1" | bc)" -eq 0 ]; then
        echo "⚠️  警告: 内核版本可能不支持io_uring（需要5.1+）"
    else
        echo "✅ 内核版本支持io_uring"
    fi
fi

# 使用psql执行配置（需要等待PostgreSQL启动）
until psql -U postgres -c "SELECT 1" > /dev/null 2>&1; do
    echo "等待PostgreSQL启动..."
    sleep 1
done

echo "PostgreSQL已启动，配置异步I/O..."

# 配置异步I/O
psql -U postgres <<-EOSQL
    -- 启用异步I/O
    ALTER SYSTEM SET io_direct = 'data,wal';
    ALTER SYSTEM SET effective_io_concurrency = 200;
    ALTER SYSTEM SET maintenance_io_concurrency = 200;
    ALTER SYSTEM SET wal_io_concurrency = 200;

    -- 重新加载配置
    SELECT pg_reload_conf();

    -- 验证配置
    SELECT name, setting
    FROM pg_settings
    WHERE name IN ('io_direct', 'effective_io_concurrency');
EOSQL

echo "✅ 异步I/O配置完成"
```

**Docker Compose配置**:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    container_name: postgresql-18-async-io
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
      - ./pg_hba.conf:/etc/postgresql/pg_hba.conf
      - ./init-async-io.sh:/docker-entrypoint-initdb.d/init-async-io.sh
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    # 资源限制（根据实际需求调整）
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    # 共享内存配置（Docker需要）
    shm_size: 256mb
    # 特权模式（某些系统可能需要以支持io_uring）
    # privileged: true  # 仅在必要时启用

volumes:
  postgres_data:
    driver: local
```

### 17.2 Kubernetes部署

**StatefulSet配置（PostgreSQL 18 + 异步I/O）**:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql-18-async-io
  namespace: postgresql
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql-18
  template:
    metadata:
      labels:
        app: postgresql-18
    spec:
      containers:
      - name: postgresql
        image: postgres:18
        env:
        - name: POSTGRES_DB
          value: mydb
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgresql-secret
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        ports:
        - containerPort: 5432
          name: postgresql
        volumeMounts:
        - name: postgresql-data
          mountPath: /var/lib/postgresql/data
        - name: postgresql-config
          mountPath: /etc/postgresql
        - name: dshm
          mountPath: /dev/shm
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U postgres
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
        # 初始化容器：配置异步I/O
        lifecycle:
          postStart:
            exec:
              command:
              - /bin/sh
              - -c
              - |
                until psql -U postgres -c "SELECT 1" > /dev/null 2>&1; do
                  sleep 1
                done
                psql -U postgres <<-EOSQL
                  ALTER SYSTEM SET io_direct = 'data,wal';
                  ALTER SYSTEM SET effective_io_concurrency = 200;
                  ALTER SYSTEM SET maintenance_io_concurrency = 200;
                  ALTER SYSTEM SET wal_io_concurrency = 200;
                  SELECT pg_reload_conf();
                EOSQL
      volumes:
      - name: postgresql-config
        configMap:
          name: postgresql-config
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: 256Mi
  volumeClaimTemplates:
  - metadata:
      name: postgresql-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgresql-config
  namespace: postgresql
data:
  postgresql.conf: |
    # PostgreSQL 18异步I/O配置（Kubernetes环境）
    io_direct = 'data,wal'
    effective_io_concurrency = 200
    maintenance_io_concurrency = 200
    wal_io_concurrency = 200

    # 内存配置
    shared_buffers = 1GB
    work_mem = 64MB
    maintenance_work_mem = 512MB

    # 连接配置
    max_connections = 200
    enable_builtin_connection_pooling = on
    connection_pool_size = 100

    # 监控配置
    track_io_timing = on
    log_min_duration_statement = 1000
---
apiVersion: v1
kind: Secret
metadata:
  name: postgresql-secret
  namespace: postgresql
type: Opaque
stringData:
  password: postgres
---
apiVersion: v1
kind: Service
metadata:
  name: postgresql
  namespace: postgresql
spec:
  selector:
    app: postgresql-18
  ports:
  - port: 5432
    targetPort: 5432
    name: postgresql
  type: ClusterIP
```

**Kubernetes部署脚本**:

```bash
#!/bin/bash
# Kubernetes部署PostgreSQL 18异步I/O（带错误处理）
set -e

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

echo "=== Kubernetes部署PostgreSQL 18异步I/O ==="

# 1. 创建命名空间
echo "创建命名空间..."
kubectl create namespace postgresql --dry-run=client -o yaml | kubectl apply -f - || error_exit "创建命名空间失败"

# 2. 创建Secret
echo "创建Secret..."
kubectl create secret generic postgresql-secret \
    --from-literal=password="${POSTGRES_PASSWORD:-postgres}" \
    --namespace=postgresql \
    --dry-run=client -o yaml | kubectl apply -f - || error_exit "创建Secret失败"

# 3. 创建ConfigMap
echo "创建ConfigMap..."
kubectl create configmap postgresql-config \
    --from-file=postgresql.conf=./postgresql.conf \
    --namespace=postgresql \
    --dry-run=client -o yaml | kubectl apply -f - || error_exit "创建ConfigMap失败"

# 4. 部署StatefulSet
echo "部署StatefulSet..."
kubectl apply -f postgresql-statefulset.yaml || error_exit "部署StatefulSet失败"

# 5. 等待Pod就绪
echo "等待Pod就绪..."
kubectl wait --for=condition=ready pod \
    -l app=postgresql-18 \
    -n postgresql \
    --timeout=300s || error_exit "Pod未就绪"

# 6. 验证部署
echo "验证部署..."
POD_NAME=$(kubectl get pods -n postgresql -l app=postgresql-18 -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n postgresql "$POD_NAME" -- psql -U postgres -c "
    SELECT name, setting
    FROM pg_settings
    WHERE name IN ('io_direct', 'effective_io_concurrency');
" || error_exit "验证失败"

echo "✅ Kubernetes部署完成"
```

### 17.3 容器化性能优化

**Docker性能优化配置**:

```yaml
# docker-compose.yml性能优化配置
version: '3.8'

services:
  postgresql:
    image: postgres:18
    # 共享内存配置（重要！）
    shm_size: 512mb
    # CPU和内存限制
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
    # 网络优化
    network_mode: bridge
    # I/O调度优化（需要特权模式）
    # cap_add:
    #   - SYS_NICE
    #   - SYS_RESOURCE
    # 或者使用privileged模式（不推荐，仅在必要时）
    # privileged: true
```

**Kubernetes性能优化配置**:

```yaml
# StatefulSet性能优化配置
spec:
  template:
    spec:
      containers:
      - name: postgresql
        # 资源请求和限制
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        # 共享内存
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        # 安全上下文（允许io_uring）
        securityContext:
          capabilities:
            add:
            - SYS_NICE
            - SYS_RESOURCE
          # 如果需要io_uring，可能需要特权模式（不推荐）
          # privileged: true
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: 512Mi
```

### 17.4 容器化部署检查清单

**容器化部署前检查**（带错误处理）:

```bash
#!/bin/bash
# 容器化部署检查清单（带错误处理）
set -e

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

echo "=== 容器化部署检查清单 ==="

# 1. 检查Docker/Kubernetes环境
if command -v docker &> /dev/null; then
    echo "✅ Docker已安装: $(docker --version)"
    DOCKER_AVAILABLE=true
else
    echo "⚠️  Docker未安装"
    DOCKER_AVAILABLE=false
fi

if command -v kubectl &> /dev/null; then
    echo "✅ Kubernetes已安装: $(kubectl version --client --short)"
    K8S_AVAILABLE=true
else
    echo "⚠️  Kubernetes未安装"
    K8S_AVAILABLE=false
fi

# 2. 检查系统支持（Linux）
if [ "$(uname)" = "Linux" ]; then
    KERNEL_VERSION=$(uname -r)
    echo "内核版本: $KERNEL_VERSION"

    # 检查io_uring支持
    if [ -f "/boot/config-$(uname -r)" ]; then
        if grep -q "CONFIG_IO_URING=y" "/boot/config-$(uname -r)"; then
            echo "✅ io_uring支持已确认"
        else
            echo "⚠️  无法确认io_uring支持"
        fi
    else
        echo "⚠️  无法检查io_uring支持（配置文件不存在）"
    fi

    # 检查文件描述符限制
    FD_LIMIT=$(ulimit -n)
    echo "文件描述符限制: $FD_LIMIT"
    if [ "$FD_LIMIT" -lt 65536 ]; then
        echo "⚠️  文件描述符限制较低，建议增加到65536+"
    else
        echo "✅ 文件描述符限制充足"
    fi
fi

# 3. 检查存储
if [ "$DOCKER_AVAILABLE" = true ]; then
    DOCKER_STORAGE=$(docker info 2>/dev/null | grep "Storage Driver" | awk '{print $3}')
    echo "Docker存储驱动: $DOCKER_STORAGE"

    if [ "$DOCKER_STORAGE" = "overlay2" ]; then
        echo "✅ 推荐的存储驱动（overlay2）"
    else
        echo "⚠️  建议使用overlay2存储驱动"
    fi
fi

# 4. 检查资源
if [ "$DOCKER_AVAILABLE" = true ]; then
    DOCKER_MEM=$(docker info 2>/dev/null | grep "Total Memory" | awk '{print $3}')
    echo "Docker可用内存: $DOCKER_MEM"
fi

echo ""
echo "✅ 容器化部署检查完成"
```

---
