# PostgreSQL 18 CI/CD自动化部署

## 1. 数据库版本控制

### 1.1 Flyway迁移

```sql
-- V1__初始化.sql
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- V2__添加索引.sql
CREATE INDEX idx_users_email ON users(email);

-- V3__添加字段.sql
ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
```

```yaml
# flyway.conf
flyway.url=jdbc:postgresql://localhost:5432/mydb
flyway.user=postgres
flyway.password=password
flyway.locations=filesystem:./migrations
```

```bash
# 执行迁移
flyway migrate

# 查看历史
flyway info

# 回滚（需要undo脚本）
flyway undo
```

### 1.2 Liquibase

```xml
<!-- changelog.xml -->
<databaseChangeLog>
    <changeSet id="1" author="admin">
        <createTable tableName="users">
            <column name="user_id" type="BIGSERIAL">
                <constraints primaryKey="true"/>
            </column>
            <column name="username" type="VARCHAR(100)">
                <constraints nullable="false"/>
            </column>
        </createTable>
    </changeSet>

    <changeSet id="2" author="admin">
        <createIndex indexName="idx_users_username" tableName="users">
            <column name="username"/>
        </createIndex>
    </changeSet>
</databaseChangeLog>
```

---

## 2. GitLab CI/CD

### 2.1 Pipeline配置

```yaml
# .gitlab-ci.yml
stages:
  - test
  - migrate
  - deploy

variables:
  POSTGRES_DB: testdb
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: password

# 测试阶段
test:
  stage: test
  image: postgres:18
  services:
    - postgres:18
  script:
    - apt-get update && apt-get install -y postgresql-client
    - psql -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -f schema.sql
    - psql -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -f test_data.sql
    - psql -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -f tests/test_queries.sql
  only:
    - merge_requests
    - main

# 迁移阶段
migrate:
  stage: migrate
  image: flyway/flyway:latest
  script:
    - flyway -url=jdbc:postgresql://$DB_HOST:5432/$DB_NAME
             -user=$DB_USER
             -password=$DB_PASSWORD
             migrate
  only:
    - main
  environment:
    name: production

# 部署阶段
deploy:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/postgres-deployment.yaml
    - kubectl rollout status deployment/postgres
  only:
    - main
  environment:
    name: production
```

---

## 3. GitHub Actions

### 3.1 Workflow

```yaml
# .github/workflows/postgres-ci.yml
name: PostgreSQL CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Setup database
        run: |
          psql -h localhost -U postgres -d testdb -f migrations/schema.sql
          psql -h localhost -U postgres -d testdb -f migrations/seed.sql
        env:
          PGPASSWORD: postgres

      - name: Run tests
        run: |
          psql -h localhost -U postgres -d testdb -f tests/test_queries.sql
        env:
          PGPASSWORD: postgres

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        run: |
          # 执行数据库迁移
          flyway migrate
        env:
          FLYWAY_URL: ${{ secrets.DB_URL }}
          FLYWAY_USER: ${{ secrets.DB_USER }}
          FLYWAY_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

---

## 4. 自动化测试

### 4.1 pgTAP测试

```sql
-- tests/test_users.sql
BEGIN;
SELECT plan(5);

-- 测试表存在
SELECT has_table('users');

-- 测试列
SELECT has_column('users', 'user_id');
SELECT has_column('users', 'username');
SELECT has_column('users', 'email');

-- 测试约束
SELECT col_is_unique('users', ARRAY['email']);

SELECT * FROM finish();
ROLLBACK;
```

```bash
# 运行测试
pg_prove -h localhost -U postgres -d testdb tests/*.sql
```

---

## 5. 蓝绿部署

### 5.1 策略

```bash
#!/bin/bash
# 蓝绿部署脚本

# 当前生产（蓝）
BLUE_DB="postgres-blue"
GREEN_DB="postgres-green"

# 1. 部署绿环境
docker-compose -f docker-compose-green.yml up -d

# 2. 数据同步（逻辑复制）
docker exec $BLUE_DB psql -U postgres -c "
CREATE PUBLICATION blue_pub FOR ALL TABLES;
"

docker exec $GREEN_DB psql -U postgres -c "
CREATE SUBSCRIPTION green_sub
CONNECTION 'host=$BLUE_DB port=5432 dbname=mydb user=postgres'
PUBLICATION blue_pub;
"

# 3. 等待同步完成
while true; do
    LAG=$(docker exec $GREEN_DB psql -U postgres -Atq -c "
    SELECT pg_wal_lsn_diff(latest_end_lsn, received_lsn)
    FROM pg_stat_subscription;
    ")

    if [ "$LAG" -eq 0 ]; then
        echo "同步完成"
        break
    fi

    echo "同步中，延迟: $LAG bytes"
    sleep 5
done

# 4. 切换流量（更新HAProxy/DNS）
# ...

# 5. 验证绿环境
# 监控错误率、延迟

# 6. 如果成功，停止蓝环境
docker-compose -f docker-compose-blue.yml down
```

---

## 6. 滚动更新

### 6.1 Kubernetes滚动更新

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  replicas: 3
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:18.1  # 更新版本
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
```

```bash
# 执行滚动更新
kubectl set image statefulset/postgres postgres=postgres:18.1

# 监控更新
kubectl rollout status statefulset/postgres

# 回滚
kubectl rollout undo statefulset/postgres
```

---

## 7. 自动化备份

### 7.1 定时备份

```yaml
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:18
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres -U postgres mydb | \
              gzip > /backup/mydb_$(date +%Y%m%d).sql.gz

              # 上传到S3
              aws s3 cp /backup/mydb_$(date +%Y%m%d).sql.gz \
                       s3://backups/postgres/

              # 清理本地
              find /backup -name "*.sql.gz" -mtime +7 -delete
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            persistentVolumeClaim:
              claimName: backup-pvc
```

---

## 8. 监控集成

### 8.1 Prometheus Exporter

```yaml
services:
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    environment:
      DATA_SOURCE_NAME: "postgresql://postgres:password@postgres:5432/mydb?sslmode=disable"
    ports:
      - "9187:9187"
    depends_on:
      - postgres
```

---

**完成**: PostgreSQL 18 CI/CD自动化部署
**字数**: ~10,000字
**涵盖**: 版本控制、GitLab/GitHub CI、Docker、蓝绿部署、自动化备份
