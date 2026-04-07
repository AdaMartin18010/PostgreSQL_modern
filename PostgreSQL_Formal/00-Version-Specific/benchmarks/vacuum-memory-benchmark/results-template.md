# VACUUM 内存优化测试结果记录模板

## 测试基本信息

| 项目 | 内容 |
|------|------|
| 测试日期 | YYYY-MM-DD |
| 测试人员 | |
| 测试环境 | Docker / 物理机 |
| PG16 版本 | |
| PG17 版本 | |

## 硬件配置

| 组件 | 配置 |
|------|------|
| CPU | |
| 内存 | |
| 磁盘类型 | SSD / NVMe / HDD |
| 磁盘容量 | |
| 操作系统 | |

## 测试参数

| 参数 | 值 |
|------|-----|
| 测试表大小 | GB |
| Dead Tuple 比例 | % |
| 测试迭代次数 | |
| shared_buffers | |
| maintenance_work_mem | |

## 测试结果

### 1. 数据生成时间

| 版本 | 第1次 | 第2次 | 第3次 | 平均值 |
|------|-------|-------|-------|--------|
| PG16 | | | | |
| PG17 | | | | |

### 2. Dead Tuple 创建时间

| 版本 | 第1次 | 第2次 | 第3次 | 平均值 |
|------|-------|-------|-------|--------|
| PG16 | | | | |
| PG17 | | | | |

### 3. VACUUM 性能对比 (PG16 vs PG17 默认)

| 指标 | PG16 | PG17 | 提升比例 |
|------|------|------|----------|
| VACUUM 执行时间 | | | |
| 峰值内存使用 | | | |
| WAL 生成量 | | | |
| 扫描页面数 | | | |
| 移除元组数 | | | |

### 4. PG17 vacuum_buffer_usage_limit 参数影响

| Buffer Limit | 执行时间 | 内存使用 | WAL 生成 | 备注 |
|--------------|----------|----------|----------|------|
| 128MB | | | | |
| 256MB (默认) | | | | |
| 512MB | | | | |
| 1GB | | | | |
| 2GB | | | | |

### 5. 详细指标

#### PG16

```
表大小:
Live Tuples:
Dead Tuples:
VACUUM 开始时间:
VACUUM 结束时间:
总耗时: 秒

系统资源监控:
- CPU 使用率峰值: %
- 内存使用峰值: MB
- 磁盘 I/O 读取: MB
- 磁盘 I/O 写入: MB
```

#### PG17 (256MB 默认)

```
表大小:
Live Tuples:
Dead Tuples:
vacuum_buffer_usage_limit: 256MB
VACUUM 开始时间:
VACUUM 结束时间:
总耗时: 秒

系统资源监控:
- CPU 使用率峰值: %
- 内存使用峰值: MB
- 磁盘 I/O 读取: MB
- 磁盘 I/O 写入: MB
```

## VACUUM VERBOSE 输出

### PG16

```sql
VACUUM (VERBOSE, ANALYZE) large_test_table;
```

```
[粘贴输出]
```

### PG17

```sql
VACUUM (VERBOSE, ANALYZE) large_test_table;
```

```
[粘贴输出]
```

## 执行计划对比

### PG16 Buffers 使用

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
VACUUM large_test_table;
```

```json
[粘贴 JSON 输出]
```

### PG17 Buffers 使用

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
VACUUM large_test_table;
```

```json
[粘贴 JSON 输出]
```

## 观察与结论

### 性能提升总结

1. **执行时间**: PG17 相比 PG16
2. **内存效率**:
3. **I/O 优化**:

### 参数调优建议

- 对于大表 (>100GB): 建议设置 vacuum_buffer_usage_limit =
- 对于并发 VACUUM:
- 内存受限环境:

### 注意事项

1.
2.
3.

## 原始数据文件

- PG16 结果: `results/pg16_*.json`
- PG17 结果: `results/pg17_*.json`
- 完整报告: `results/BENCHMARK_REPORT_*.md`
