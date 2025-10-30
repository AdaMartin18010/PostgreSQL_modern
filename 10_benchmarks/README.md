# PostgreSQL 性能基准测试指南

> 版本对标（更新于 2025-10）| PostgreSQL 17

## 📋 目录

- [主题边界](#主题边界)
- [核心概念](#核心概念)
- [测试方法论](#测试方法论)
- [工具生态](#工具生态)
- [关键指标](#关键指标)
- [测试场景](#测试场景)
- [最佳实践](#最佳实践)
- [文档索引](#文档索引)

---

## 主题边界

本目录涵盖PostgreSQL数据库的**系统化性能基准测试**，包括：

- ✅ **基准方法**：实验设计、变量控制、热身与重复、置信区间
- ✅ **测试工具**：pgbench、TPC系列、自定义脚本、监控集成
- ✅ **负载模型**：OLTP、OLAP、混合负载、读写比例、连接池策略
- ✅ **性能指标**：TPS/QPS、延迟分布、I/O效率、WAL/检查点影响
- ✅ **路径分析**：执行计划、锁等待、膨胀监控、Autovacuum干扰
- ✅ **结果解读**：统计分析、瓶颈定位、优化建议、对比报告

---

## 核心概念

### 1. 基准测试的目标

| 目标类型 | 说明 | 示例 |
|---------|------|------|
| **容量规划** | 确定硬件资源需求 | 支持10万TPS需要多少CPU/内存？ |
| **性能验证** | 验证优化效果 | 调整shared_buffers后性能提升多少？ |
| **稳定性测试** | 评估长时间运行表现 | 7天持续运行是否出现性能衰减？ |
| **对比评估** | 不同方案/版本对比 | PostgreSQL 16 vs 17性能差异？ |
| **瓶颈定位** | 找出系统瓶颈 | CPU、I/O、网络哪个是瓶颈？ |

### 2. 负载分类

```text
OLTP（联机事务处理）
├── 特点：短事务、高并发、读写混合
├── 典型操作：INSERT、UPDATE、SELECT单行
└── 评估指标：TPS、P95/P99延迟

OLAP（联机分析处理）
├── 特点：长查询、复杂JOIN、大量聚合
├── 典型操作：复杂SELECT、窗口函数、GROUP BY
└── 评估指标：查询时长、I/O吞吐、并行度

HTAP（混合负载）
├── 特点：OLTP+OLAP混合
├── 典型场景：实时报表、实时分析
└── 评估指标：事务延迟 + 分析查询时长
```

### 3. 性能指标体系

```text
吞吐量指标
├── TPS (Transactions Per Second)     # 每秒事务数
├── QPS (Queries Per Second)          # 每秒查询数
└── Throughput (MB/s)                 # I/O吞吐量

延迟指标
├── Average Latency                   # 平均延迟
├── P50 / Median                      # 中位数延迟
├── P95                               # 95%分位延迟
├── P99                               # 99%分位延迟
└── Max Latency                       # 最大延迟

资源指标
├── CPU Utilization                   # CPU使用率
├── Memory Usage                      # 内存使用
├── Disk I/O (IOPS, Bandwidth)        # 磁盘I/O
├── Network I/O                       # 网络I/O
└── Connection Count                  # 连接数

数据库内部指标
├── Cache Hit Ratio                   # 缓存命中率
├── WAL Generation Rate               # WAL生成速率
├── Checkpoint Frequency              # 检查点频率
├── Lock Waits                        # 锁等待
└── Bloat Ratio                       # 膨胀率
```

---

## 测试方法论

### 1. 实验设计原则

```text
✅ 控制变量法
├── 单一变量测试：每次只改变一个参数
├── 基线对比：建立稳定的基线测试
└── 多次重复：至少重复3次取平均值

✅ 热身与稳定状态
├── 预热阶段：运行5-10分钟预热缓存
├── 稳定测试：在稳定状态下采集数据
└── 足够时长：测试时间≥5分钟（推荐10-30分钟）

✅ 环境一致性
├── 硬件配置：相同的CPU/内存/磁盘
├── 软件版本：相同的PostgreSQL版本和配置
├── 数据规模：相同的数据量和分布
└── 网络条件：相同的网络延迟和带宽
```

### 2. 标准测试流程

```bash
# 阶段1：环境准备
┌─────────────────────────────────────┐
│ 1. 重启数据库（清空缓存）             │
│ 2. 初始化测试数据                    │
│ 3. 创建索引和统计                    │
│ 4. VACUUM ANALYZE                   │
└─────────────────────────────────────┘
          ↓
# 阶段2：预热
┌─────────────────────────────────────┐
│ 运行5-10分钟预热测试                 │
│ 加载热数据到缓存                     │
└─────────────────────────────────────┘
          ↓
# 阶段3：基准测试
┌─────────────────────────────────────┐
│ 执行正式测试（10-30分钟）            │
│ 同时采集系统和数据库指标             │
└─────────────────────────────────────┘
          ↓
# 阶段4：数据分析
┌─────────────────────────────────────┐
│ 1. 统计TPS/延迟分布                 │
│ 2. 分析资源使用情况                 │
│ 3. 检查执行计划和瓶颈               │
│ 4. 生成对比报告                     │
└─────────────────────────────────────┘
```

---

## 工具生态

### 1. pgbench（官方工具）

**特点**：

- ✅ PostgreSQL官方提供，与数据库版本同步
- ✅ 内置TPC-B like基准测试
- ✅ 支持自定义SQL脚本
- ✅ 详细的性能统计

**适用场景**：

- OLTP性能测试
- 参数调优验证
- 硬件性能评估
- 版本对比测试

**详细文档**：[pgbench_example.md](./pgbench_example.md)

### 2. TPC系列基准

| 基准 | 类型 | 说明 |
|------|------|------|
| **TPC-C** | OLTP | 电商订单处理系统模拟 |
| **TPC-H** | OLAP | 决策支持系统查询 |
| **TPC-DS** | OLAP | 复杂零售决策支持 |
| **TPC-E** | OLTP | 经纪公司业务模拟 |

**参考资源**：

- TPC官网：<http://www.tpc.org/>
- HammerDB（开源TPC实现）：<https://www.hammerdb.com/>

### 3. 专业基准工具

```text
sysbench
├── 特点：支持多数据库、自定义Lua脚本
├── 场景：通用性能测试
└── 安装：apt/yum install sysbench

pgbouncer-bench
├── 特点：测试连接池性能
├── 场景：连接池效果验证
└── 项目：github.com/pgbouncer/pgbouncer

pgsql-io-bench
├── 特点：专注I/O性能测试
├── 场景：磁盘性能评估
└── 工具：dd、fio、pgbench结合

自定义应用基准
├── 特点：模拟真实业务负载
├── 场景：生产环境性能预测
└── 方法：录制重放生产SQL
```

---

## 关键指标

### 1. TPS/QPS解读

```text
TPS = 事务总数 / 测试时长

示例：
- 60秒内完成54826个事务
- TPS = 54826 / 60 = 913.77

注意：
✅ 区分"包含连接时间"和"不包含连接时间"
✅ 稳定TPS比峰值TPS更重要
✅ 关注TPS波动（标准差）
```

### 2. 延迟分布

```text
P50（中位数）：50%的请求延迟低于此值
P95：         95%的请求延迟低于此值
P99：         99%的请求延迟低于此值
P99.9：       99.9%的请求延迟低于此值

示例：
Average: 17.5ms
P50:     15.2ms  ← 大部分用户体验
P95:     28.3ms  ← 95%用户可接受
P99:     45.6ms  ← 尾部延迟
Max:     120ms   ← 最差情况

评估标准：
✅ P95 < 50ms   （OLTP良好）
✅ P99 < 100ms  （OLTP可接受）
❌ P99 > 200ms  （需要优化）
```

### 3. 资源使用

```sql
-- CPU使用率
-- 理想范围：60-80%（留有余量）
-- 过低：可能有其他瓶颈
-- 过高：可能需要扩展或优化

-- 内存使用
SELECT 
    pg_size_pretty(SUM(heap_blks_hit) * 8192) as cache_hit_size,
    ROUND(100.0 * SUM(heap_blks_hit) / 
          NULLIF(SUM(heap_blks_hit + heap_blks_read), 0), 2) as hit_ratio
FROM pg_statio_user_tables;
-- 目标：缓存命中率 > 95%

-- I/O统计
SELECT * FROM pg_stat_bgwriter;
-- 关注：buffers_checkpoint vs buffers_backend
```

---

## 测试场景

### 场景1：单机OLTP性能上限

**目标**：找出单机最大TPS

```bash
# 逐步增加并发，找到TPS峰值
for c in 8 16 32 64 128 256; do
    echo "Testing with $c clients..."
    pgbench -T 300 -c $c -j 8 testdb | grep "tps ="
done

# 分析：
# - TPS随并发增加而提升，到某个点后不再增长
# - 超过峰值后TPS下降，延迟增加（资源饱和）
```

### 场景2：读写比例测试

**目标**：评估不同读写比例下的性能

```bash
# 100%读
pgbench -S -T 300 -c 64 -j 8 testdb

# 80%读 + 20%写
pgbench -b select-only@80 -b tpcb-like@20 -T 300 -c 64 testdb

# 50%读 + 50%写
pgbench -b select-only@50 -b tpcb-like@50 -T 300 -c 64 testdb

# 100%写
pgbench -N -T 300 -c 64 -j 8 testdb
```

### 场景3：长时间稳定性测试

**目标**：验证7×24小时运行稳定性

```bash
# 运行24小时，每10分钟输出进度
pgbench -T 86400 -c 32 -j 4 -P 600 testdb > stability_test.log

# 分析：
# - TPS是否随时间衰减
# - 是否出现突然的性能下降
# - 检查是否与Autovacuum/Checkpoint相关
```

### 场景4：参数调优对比

**目标**：量化参数优化效果

```bash
# 基线测试（默认参数）
pgbench -T 300 -c 32 testdb > baseline.log

# 修改参数
psql -c "ALTER SYSTEM SET shared_buffers = '8GB';"
psql -c "ALTER SYSTEM SET work_mem = '64MB';"
pg_ctl restart

# 对比测试
pgbench -T 300 -c 32 testdb > optimized.log

# 计算性能提升
grep "tps =" baseline.log optimized.log
```

---

## 最佳实践

### 1. 测试环境要求

```text
硬件要求：
✅ 与生产环境相同或相近的硬件配置
✅ 独立的测试服务器（避免干扰）
✅ 可靠的存储（SSD推荐）
✅ 稳定的网络连接

软件配置：
✅ 相同的PostgreSQL版本
✅ 相同的配置参数
✅ 相同的操作系统设置
✅ 关闭不必要的后台服务

数据准备：
✅ 有代表性的数据规模
✅ 真实的数据分布
✅ 完整的索引和约束
✅ 最新的统计信息（ANALYZE）
```

### 2. 常见错误

```text
❌ 避免的错误：

1. 测试时间过短
   - 问题：缓存未预热，结果不稳定
   - 建议：至少运行5分钟

2. 不预热缓存
   - 问题：冷启动性能不代表真实情况
   - 建议：测试前运行预热阶段

3. 单次测试
   - 问题：结果可能受偶然因素影响
   - 建议：重复3-5次取平均值

4. 忽略背景任务
   - 问题：Autovacuum等影响结果
   - 建议：监控pg_stat_activity

5. 不记录环境信息
   - 问题：无法复现测试
   - 建议：记录完整配置和版本
```

### 3. 报告模板

```markdown
## PostgreSQL性能测试报告

### 测试环境
- PostgreSQL版本：17.0
- 服务器配置：8核CPU，32GB内存，SSD
- 操作系统：Ubuntu 22.04
- 测试时间：2025-10-03

### 测试场景
- 工具：pgbench
- 数据规模：100万行（scale=10）
- 并发数：32客户端，4线程
- 测试时长：300秒

### 测试结果
| 指标 | 基线 | 优化后 | 提升 |
|------|------|--------|------|
| TPS | 913 | 1450 | +58.8% |
| P95延迟 | 28.3ms | 18.5ms | -34.6% |
| 缓存命中率 | 94.2% | 98.5% | +4.3% |

### 优化措施
1. shared_buffers: 2GB → 8GB
2. work_mem: 4MB → 64MB
3. checkpoint_timeout: 5min → 15min

### 结论与建议
- 性能提升显著，建议应用到生产环境
- 继续监控长期稳定性
- 考虑进一步优化索引策略
```

---

## 文档索引

### 详细指南

- **[pgbench完整使用指南](./pgbench_example.md)** - 519行深度教程
- **[pgbench OLTP手册](./pgbench_oltp_playbook.md)** - OLTP场景实践
- **[分布式基准测试](./distributed_benchmarks.md)** - Citus等分布式场景
- **[数据采集清单](./collect_checklist.md)** - 监控指标采集

### 报告模板

- **[报告模板目录](./report_templates/)** - 标准化报告模板

### PG18 对齐新增模板

- **[向量/混合搜索指标模板](./vector_hybrid_metrics_template.md)**
- **[多模一体化基准模板](./multimodel_benchmark_template.md)**

参考论证：`13_ai_alignment/00_论证总览_AI_View_对齐_PG18.md`

### 相关章节

- **[09_deployment_ops/](../09_deployment_ops/)** - 运维和监控
- **[04_modern_features/](../04_modern_features/)** - PostgreSQL 17新特性
- **[08_ecosystem_cases/](../08_ecosystem_cases/)** - 实战案例

---

## 权威参考

- **pgbench官方文档**：<https://www.postgresql.org/docs/17/pgbench.html>
- **性能调优指南**：<https://www.postgresql.org/docs/17/performance-tips.html>
- **EXPLAIN使用**：<https://www.postgresql.org/docs/17/using-explain.html>
- **监控统计**：<https://www.postgresql.org/docs/17/monitoring-stats.html>
- **TPC基准**：<http://www.tpc.org/>

---

## 知识地图

```text
基准测试体系
├── 1. 目标定义
│   ├── 容量规划
│   ├── 性能验证
│   ├── 稳定性测试
│   └── 对比评估
│
├── 2. 场景设计
│   ├── OLTP场景
│   ├── OLAP场景
│   ├── 混合负载
│   └── 压力测试
│
├── 3. 工具选择
│   ├── pgbench
│   ├── TPC系列
│   ├── 自定义脚本
│   └── 监控工具
│
├── 4. 执行测试
│   ├── 环境准备
│   ├── 预热阶段
│   ├── 正式测试
│   └── 数据采集
│
└── 5. 结果分析
    ├── 性能指标
    ├── 瓶颈定位
    ├── 优化建议
    └── 报告输出
```

---

**最后更新**：2025-10  
**维护者**：PostgreSQL_modern项目组
