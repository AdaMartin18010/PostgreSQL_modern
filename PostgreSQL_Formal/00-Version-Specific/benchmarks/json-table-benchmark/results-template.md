# JSON_TABLE 性能测试结果记录模板

## 测试基本信息

| 项目 | 内容 |
|------|------|
| 测试日期 | YYYY-MM-DD |
| 测试人员 | |
| 测试环境 | Docker / 物理机 |
| PostgreSQL 版本 | 17.x |
| work_mem | 256MB |
| shared_buffers | 2GB |

## 测试数据

### 数据规模

| 复杂度 | 数据量 | 表大小 | 平均每行大小 |
|--------|--------|--------|--------------|
| simple | 1K | | |
| simple | 10K | | |
| simple | 100K | | |
| medium | 1K | | |
| medium | 10K | | |
| complex | 1K | | |
| complex | 10K | | |

### 简单 JSON 结构示例

```json
{
  "id": 1,
  "name": "Item_1",
  "value": 1234.56,
  "status": "active",
  "quantity": 100,
  "price": 99.99
}
```

### 中等复杂度 JSON 结构示例

```json
{
  "id": 1,
  "product": {
    "name": "Product_1",
    "sku": "SKU-...",
    "category": { "id": 1, "name": "Category_1" }
  },
  "pricing": { "base_price": 99.99, "discount": 0.1 },
  "inventory": { "quantity": 1000, "warehouse_id": 5 }
}
```

### 复杂 JSON 结构示例

```json
{
  "order_id": "ORD-12345",
  "customer": { "id": 1, "name": "...", "address": { ... } },
  "items": [ { "item_id": 1, "quantity": 2, ... }, ... ],
  "payment": { "amount": 299.99, "status": "completed" }
}
```

## 测试结果

### 1. 简单 JSON - 1K 行

#### jsonb_to_recordset

```sql
SELECT * FROM jsonb_to_recordset(
    (SELECT jsonb_agg(data) FROM json_test WHERE batch_id = 1)
) AS x(id BIGINT, name TEXT, value NUMERIC, status TEXT, quantity INT);
```

**执行计划:**

```
[粘贴 EXPLAIN ANALYZE 输出]
```

**性能指标:**

- Planning Time: ms
- Execution Time: ms
- Actual Rows:
- Shared Hit Blocks:
- Shared Read Blocks:

#### JSON_TABLE

```sql
SELECT * FROM JSON_TABLE(
    (SELECT jsonb_agg(data) FROM json_test WHERE batch_id = 1),
    '$[*]' COLUMNS (
        id BIGINT PATH '$.id',
        name TEXT PATH '$.name',
        value NUMERIC PATH '$.value',
        status TEXT PATH '$.status',
        quantity INT PATH '$.quantity'
    )
) AS jt;
```

**执行计划:**

```
[粘贴 EXPLAIN ANALYZE 输出]
```

**性能指标:**

- Planning Time: ms
- Execution Time: ms
- Actual Rows:
- Shared Hit Blocks:
- Shared Read Blocks:

**对比总结:**

- 性能差异: %
- 内存使用差异: %

### 2. 简单 JSON - 10K 行

| 指标 | jsonb_to_recordset | JSON_TABLE | 差异 |
|------|-------------------|------------|------|
| 执行时间 | ms | ms | % |
| 计划时间 | ms | ms | % |
| Buffer Hit | | | |
| Buffer Read | | | |

### 3. 简单 JSON - 100K 行

| 指标 | jsonb_to_recordset | JSON_TABLE | 差异 |
|------|-------------------|------------|------|
| 执行时间 | ms | ms | % |
| 内存使用 | MB | MB | % |

### 4. 中等复杂度 JSON - 1K 行

#### 传统方法 (JSONB 路径操作)

```sql
SELECT
    data->'product'->>'name' as product_name,
    (data->'pricing'->>'base_price')::NUMERIC as price
FROM json_test WHERE batch_id = 11;
```

**性能指标:**

- 执行时间: ms

#### JSON_TABLE

```sql
SELECT jt.* FROM json_test t,
JSON_TABLE(t.data, '$' COLUMNS (
    product_name TEXT PATH '$.product.name',
    price NUMERIC PATH '$.pricing.base_price'
)) AS jt WHERE t.batch_id = 11;
```

**性能指标:**

- 执行时间: ms

### 5. 复杂嵌套 JSON - 数组展开

#### jsonb_array_elements

```sql
SELECT t.data->>'order_id', i->>'product_name', (i->>'quantity')::INT
FROM json_test t, jsonb_array_elements(t.data->'items') i
WHERE t.batch_id = 21;
```

**性能指标:**

- 执行时间: ms
- 实际返回行数:

#### JSON_TABLE (NESTED PATH)

```sql
SELECT jt.* FROM json_test t,
JSON_TABLE(t.data, '$' COLUMNS (
    order_id TEXT PATH '$.order_id',
    NESTED PATH '$.items[*]' COLUMNS (
        product_name TEXT PATH '$.product_name',
        quantity INT PATH '$.quantity'
    )
)) AS jt WHERE t.batch_id = 21;
```

**性能指标:**

- 执行时间: ms
- 实际返回行数:

## 汇总对比

### 执行时间对比

| 测试场景 | jsonb_to_recordset | JSON_TABLE | 提升 |
|----------|-------------------|------------|------|
| simple_1k | ms | ms | % |
| simple_10k | ms | ms | % |
| simple_100k | ms | ms | % |
| medium_1k | ms | ms | % |
| medium_10k | ms | ms | % |
| complex_1k | ms | ms | % |
| nested_array_1k | ms | ms | % |

### 性能提升趋势

```
数据量
1M    │                                     ╱ JSON_TABLE
      │                                 ╱
100K  │                             ╱
      │                         ╱
10K   │                     ╱
      │                 ╱
1K    │             ╱     jsonb_to_recordset
      │         ╱
      │     ╱
      │ ╱
      └────────────────────────────────────
        1K    10K   100K  1M    10M
```

## 观察与结论

### 主要发现

1. **性能提升**:
   - 小数据量 (1K): JSON_TABLE 比 jsonb_to_recordset 快 %
   - 中数据量 (10K-100K): JSON_TABLE 比 jsonb_to_recordset 快 %
   - 大数据量 (1M+): JSON_TABLE 比 jsonb_to_recordset 快 %

2. **内存使用**:
   - jsonb_to_recordset: 需要构建完整 JSONB 聚合
   - JSON_TABLE: 流式处理，内存使用更优

3. **语法对比**:
   - JSON_TABLE: 符合 SQL:2016 标准，更直观
   - jsonb_to_recordset: PostgreSQL 特有，需要显式类型定义

### 推荐使用场景

| 场景 | 推荐方法 | 原因 |
|------|----------|------|
| 简单扁平 JSON | JSON_TABLE | 标准语法，性能好 |
| 嵌套 JSON 提取 | JSON_TABLE | NESTED PATH 语法简洁 |
| 数组展开 | JSON_TABLE | NESTED PATH 支持 |
| 错误处理要求 | JSON_TABLE | ERROR/NULL ON ERROR |
| PG 特定扩展 | jsonb_to_recordset | 兼容旧版本 |

### 最佳实践

1. **大数据量处理**:
   - 使用分页或流式处理
   - 考虑适当提高 work_mem

2. **复杂嵌套结构**:
   - 优先使用 JSON_TABLE 的 NESTED PATH
   - 避免多层子查询

3. **索引优化**:
   - 对常用查询路径创建 GIN 索引
   - 考虑物化视图缓存结果

4. **错误处理**:
   - 使用 ERROR ON ERROR 捕获数据质量问题
   - 或使用 NULL ON ERROR 保证查询连续性

## 原始数据文件

- 测试日志: `results/benchmark_*.log`
- 数据库统计: `results/db_stats_*.txt`
- CSV 数据: `results/benchmark_data.csv`
