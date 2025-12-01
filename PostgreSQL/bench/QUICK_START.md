# 基准测试快速开始指南

> **PostgreSQL版本**: 18 ⭐ | 17 | 16
> **最后更新**: 2025-11-12
> **预计时间**: 15-30 分钟

---

## 🎯 5 分钟快速体验

### 步骤 1: 环境检查（1 分钟）

```bash
# 检查 PostgreSQL 是否运行
pg_isready

# 检查 pgbench 是否可用
pgbench --version
```

### 步骤 2: 初始化测试数据（2 分钟）

```bash
# 创建测试数据库
createdb pgbench_test

# 初始化数据（scale factor = 10，约 100 万行）
pgbench -i -s 10 pgbench_test
```

### 步骤 3: 运行第一个测试（2 分钟）

```bash
# 运行标准 TPC-B 测试（32 并发，60 秒）
pgbench -c 32 -j 32 -T 60 -r pgbench_test
```

**预期输出**：

```text
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 10
query mode: simple
number of clients: 32
number of threads: 32
duration: 60 s
number of transactions actually processed: 12345
latency average = 77.234 ms
tps = 411.234 (including connections establishing)
```

---

## 📊 完整测试流程（30 分钟）

### 场景 1: 标准 OLTP 性能测试

#### 1. 准备环境

```bash
# 创建测试数据库
createdb pgbench_test

# 初始化数据（根据实际情况调整 scale factor）
pgbench -i -s 100 pgbench_test  # scale factor = 100，约 1000 万行
```

#### 2. 运行基线测试

```bash
# 预热（不记录结果）
pgbench -c 32 -j 32 -T 60 pgbench_test

# 正式测试（记录结果）
pgbench -c 32 -j 32 -T 300 -r -l pgbench_test > result_baseline.log 2>&1
```

#### 3. 分析结果

**Linux/macOS**：

```bash
cd tools
chmod +x extract_pgbench_metrics.sh analyze_pgbench_log.sh

# 提取关键指标
./extract_pgbench_metrics.sh ../result_baseline.log

# 分析延迟分布
./analyze_pgbench_log.sh ../pgbench_log.*
```

**Windows**：

```powershell
cd tools

# 提取关键指标
.\extract_pgbench_metrics.ps1 -InputFile "..\result_baseline.log"

# 分析延迟分布
.\analyze_pgbench_log.ps1 -LogFiles (Get-ChildItem ..\pgbench_log.*).Name
```

#### 4. 记录结果

使用测试报告模板记录结果（见下方）。

---

### 场景 2: 混合查询性能测试

#### 1. 准备数据

```sql
-- 连接到数据库
\c your_database

-- 创建测试表（参考混合查询-基准模板.md）
CREATE TABLE IF NOT EXISTS docs (
    id bigserial PRIMARY KEY,
    text text NOT NULL,
    embedding vector(768),
    category text,
    created_at timestamptz DEFAULT now()
);

-- 创建索引
CREATE INDEX ON docs USING gin (to_tsvector('simple', text));
CREATE INDEX ON docs USING hnsw (embedding vector_l2_ops);

-- 插入测试数据（建议 100万+ 文档）
-- 参考 sql/vector_examples.sql
```

#### 2. 运行测试

```bash
# 使用混合查询脚本
cd scripts

# 基础混合查询
pgbench -c 32 -j 32 -T 300 -r -f mix_basic.sql postgres > result_mix_basic.log 2>&1

# RRF 融合查询
pgbench -c 32 -j 32 -T 300 -r -f mix_rrf.sql postgres > result_mix_rrf.log 2>&1
```

#### 3. 监控性能

```sql
-- 在另一个会话中执行监控查询
\i sql/benchmark_monitoring.sql

-- 或使用 SQL 监控脚本中的特定查询
```

---

## 🔧 常用命令速查

### pgbench 基础命令

```bash
# 初始化数据
pgbench -i -s <scale_factor> <database>

# 标准测试
pgbench -c <clients> -j <threads> -T <seconds> <database>

# 自定义脚本测试
pgbench -c <clients> -j <threads> -T <seconds> -f <script.sql> <database>

# 记录延迟日志
pgbench -c <clients> -j <threads> -T <seconds> -l <database>
```

### 系统监控

```bash
# 启动系统监控（Linux/macOS）
cd tools
./monitor_system.sh 300 test_run &

# 运行测试
pgbench -c 32 -j 32 -T 300 postgres
```

### 结果分析

```bash
# 提取指标（Linux/macOS）
./tools/extract_pgbench_metrics.sh result.log

# 分析延迟（Linux/macOS）
./tools/analyze_pgbench_log.sh pgbench_log.*

# Windows PowerShell
.\tools\extract_pgbench_metrics.ps1 -InputFile "result.log"
.\tools\analyze_pgbench_log.ps1 -LogFiles (Get-ChildItem pgbench_log.*).Name
```

---

## 📋 测试检查清单

### 测试前

- [ ] PostgreSQL 已安装并运行
- [ ] pgbench 工具可用
- [ ] 测试数据库已创建
- [ ] 测试数据已准备（如需要）
- [ ] 索引已创建（如需要）
- [ ] 系统监控工具已准备

### 测试中

- [ ] 系统监控已启动
- [ ] 测试脚本已运行
- [ ] 输出已重定向到日志文件
- [ ] 延迟日志已记录（如需要）

### 测试后

- [ ] 关键指标已提取
- [ ] 延迟分布已分析
- [ ] 系统资源使用已记录
- [ ] 结果已记录到报告模板
- [ ] 与基线进行了对比

---

## 🎓 下一步

### 新手

1. 阅读 [README.md](./README.md) 了解完整体系
2. 选择适合的基准模板开始测试
3. 使用工具分析结果

### 进阶

1. 学习 [pgbench-模板.md](./pgbench-模板.md) 深入了解 pgbench
2. 尝试 [混合查询-基准模板.md](./混合查询-基准模板.md) 测试混合查询
3. 探索 [feature_bench/](./feature_bench/) PostgreSQL 17+ 新特性

### 专家

1. 创建自定义测试脚本
2. 集成到 CI/CD 流程
3. 建立性能基线库

---

## 🔗 相关资源

- **完整文档**: [README.md](./README.md)
- **更新日志**: [CHANGELOG.md](./CHANGELOG.md)
- **工具说明**: [tools/README.md](./tools/README.md)
- **脚本说明**: [scripts/README.md](./scripts/README.md)
- **SQL 监控**: [sql/README.md](./sql/README.md)

---

## ❓ 常见问题

### Q: pgbench 命令未找到？

**A**: 安装 postgresql-contrib 包：

```bash
# Ubuntu/Debian
sudo apt-get install postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-contrib
```

### Q: 测试结果不稳定？

**A**:

1. 确保测试前先运行预热
2. 多次运行取平均值
3. 检查是否有其他负载干扰
4. 确保系统资源充足

### Q: 如何对比不同配置的性能？

**A**:

1. 使用相同的测试参数
2. 记录所有配置信息
3. 使用测试报告模板记录结果
4. 使用 SQL 监控脚本的对比功能

---

**🎉 开始你的基准测试之旅！**
