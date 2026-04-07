# VACUUM 内存优化基准测试 (PG17)

## 测试目标

验证 PostgreSQL 17 中 VACUUM 内存优化特性的性能提升，特别是 `vacuum_buffer_usage_limit` 参数的影响。

## PG17 新特性

PostgreSQL 17 引入了 VACUUM 内存使用优化：

- 新的 `vacuum_buffer_usage_limit` 参数控制 VACUUM 的缓冲区使用
- 默认值为 256MB（相比之前版本的 2MB ring buffer 大幅提升）
- 减少 WAL 生成和 I/O 开销
- 显著提升大表 VACUUM 性能

## 测试环境要求

### 硬件配置

- CPU: 4核+ (推荐 8核)
- RAM: 16GB+ (推荐 32GB)
- 磁盘: SSD，建议 500GB+ 可用空间

### 软件要求

- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 16 和 17 镜像

## 测试脚本

```bash
# 1. 启动测试环境
docker-compose up -d

# 2. 运行测试
./test-vacuum.sh

# 3. 收集结果
# 结果将保存在 results/ 目录
```

## 测试场景

### 场景 1: 100GB 表 VACUUM 对比 (PG16 vs PG17)

- 创建 100GB 测试表（含大量 dead tuples）
- 分别测试 PG16 和 PG17 的 VACUUM 性能
- 对比指标：执行时间、内存使用、WAL 生成量

### 场景 2: 内存使用监控

- 使用 `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` 监控缓冲区使用
- 监控系统级内存消耗 (RSS)
- 记录峰值内存使用

### 场景 3: 配置参数影响

- 测试不同 `vacuum_buffer_usage_limit` 值：
  - 128MB
  - 256MB (默认)
  - 512MB
  - 1GB
  - 2GB

### 场景 4: 多表并发 VACUUM

- 同时 VACUUM 多个大表
- 测试内存分配策略

## 预期结果

基于官方声明和测试数据：

| 指标 | PG16 | PG17 | 提升 |
|------|------|------|------|
| 100GB 表 VACUUM 时间 | ~45分钟 | ~20分钟 | 55%+ |
| 峰值内存使用 | ~2MB | 256MB | 配置可控 |
| WAL 生成量 | 基准 | -30% | 减少 I/O |

## 结果记录

参见 [results-template.md](./results-template.md) 记录测试结果。

## 注意事项

1. **磁盘空间**: 确保有足够的磁盘空间用于测试数据
2. **内存限制**: Docker 容器需要足够的内存限制
3. **I/O 性能**: SSD 强烈推荐，HDD 测试结果可能不准确
4. **多次运行**: 建议每个测试运行 3 次取平均值
