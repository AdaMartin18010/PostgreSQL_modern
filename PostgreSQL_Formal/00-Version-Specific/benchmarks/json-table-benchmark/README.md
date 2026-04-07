# JSON_TABLE 性能基准测试 (PG17)

## 测试目标

验证 PostgreSQL 17 中 `JSON_TABLE` 函数的性能，对比传统 `jsonb_to_recordset` 方法，评估在大数据量和复杂 JSON 结构下的处理效率。

## PG17 新特性

PostgreSQL 17 引入了 SQL:2016 标准的 `JSON_TABLE` 函数：

- 将 JSON 数据转换为关系表格式
- 支持嵌套 JSON 结构处理
- 支持错误处理 (ERROR/EMPTY/NULL ON ERROR)
- 更直观的语法和更好的性能

## 测试环境要求

### 硬件配置

- CPU: 4核+
- RAM: 8GB+
- 磁盘: SSD 推荐

### 软件要求

- Docker 20.10+
- PostgreSQL 17 镜像

## 测试场景

### 场景 1: JSON_TABLE vs jsonb_to_recordset 基准对比

- 测试数据量: 1K, 10K, 100K, 1M 行
- 对比指标: 执行时间、内存使用、执行计划

### 场景 2: 不同 JSON 复杂度测试

- 简单 JSON (扁平结构)
- 中等复杂度 (2-3 层嵌套)
- 复杂 JSON (5+ 层深度嵌套、数组)

### 场景 3: 嵌套 JSON 处理

- 处理嵌套对象
- 处理 JSON 数组展开
- 多级路径提取

### 场景 4: 执行计划对比

- 分析两种方法的查询计划
- 成本估算对比
- 实际执行差异

## 预期结果

| 数据量 | jsonb_to_recordset | JSON_TABLE | 性能提升 |
|--------|-------------------|------------|----------|
| 1K     | ~10ms             | ~8ms       | 20%      |
| 10K    | ~100ms            | ~70ms      | 30%      |
| 100K   | ~1.5s             | ~0.8s      | 45%      |
| 1M     | ~20s              | ~10s       | 50%      |

## 目录结构

```
json-table-benchmark/
├── README.md              # 本文件
├── docker-compose.yml     # Docker 环境配置
├── setup.sql             # 测试数据和函数准备
├── benchmark.sql         # 基准测试 SQL
├── test-runner.sh        # 自动化测试脚本
└── results-template.md   # 结果记录模板
```

## 快速开始

```bash
# 1. 启动测试环境
docker-compose up -d

# 2. 初始化测试数据
docker exec -i pg17-json-test psql -U postgres -f /benchmark/setup.sql

# 3. 运行基准测试
./test-runner.sh

# 4. 查看结果
cat results/json-table-benchmark.md
```

## 测试方法

```sql
-- 示例: 对比测试
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM jsonb_to_recordset(
    (SELECT jsonb_agg(data) FROM json_test WHERE batch_id = 1)
) AS x(id int, name text, value numeric);

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM JSON_TABLE(
    (SELECT jsonb_agg(data) FROM json_test WHERE batch_id = 1),
    '$[*]' COLUMNS (
        id int PATH '$.id',
        name text PATH '$.name',
        value numeric PATH '$.value'
    )
) AS jt;
```

## 注意事项

1. **数据类型映射**: 确保 JSON_TABLE 和普通转换的数据类型一致
2. **错误处理**: 测试不同错误处理策略的性能影响
3. **内存使用**: 大数据量测试时监控内存消耗
4. **预热**: 多次运行以获得稳定的性能数据
