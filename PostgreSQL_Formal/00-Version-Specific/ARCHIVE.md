# PostgreSQL 版本历史档案

> 📅 最后更新: 2026-04-07
>
> 本文档归档 PostgreSQL 16 及以下版本的历史信息，用于版本演进研究和升级规划参考。

---

## 版本生命周期

PostgreSQL 全球开发组遵循**5年支持周期**策略：每个主要版本从初始发布之日起接收5年的社区支持。

| 版本 | 发布日期 | EOL日期 | 状态 | 本文档覆盖 |
|------|----------|---------|------|------------|
| PG 16 | 2023-09-14 | 2028-11-09 | 🔵 维护中 | 部分 |
| PG 15 | 2022-10-13 | 2027-11-11 | 🔵 维护中 | 无 |
| PG 14 | 2021-09-30 | 2026-11-12 | 🟡 即将EOL | 无 |
| PG 13 | 2020-09-24 | 2025-11-13 | 🔴 已停止支持 | 无 |
| PG 12 | 2019-10-03 | 2024-11-21 | 🔴 已停止支持 | 无 |
| PG 11 | 2018-10-18 | 2023-11-09 | 🔴 已停止支持 | 无 |
| PG 10 | 2017-10-05 | 2022-11-10 | 🔴 已停止支持 | 无 |
| PG 9.6 | 2016-09-29 | 2021-11-11 | 🔴 已停止支持 | 无 |
| PG 9.5 | 2016-01-07 | 2021-02-11 | 🔴 已停止支持 | 无 |

> **图例说明**: 🔵 积极维护 | 🟡 即将结束支持 | 🔴 已停止支持

---

## 各版本重要特性回顾

### PostgreSQL 16 (2023-09-14)

**SQL/JSON 增强**

- SQL/JSON 构造器: `JSON_ARRAY()`, `JSON_OBJECT()`
- SQL/JSON 路径表达式增强

**复制与高可用**

- 逻辑复制副本节点（从备库进行逻辑复制）
- 双向逻辑复制支持
- 逻辑复制并行应用改进

**性能优化**

- VACUUM 并行处理改进
- 自动真空缓冲区策略优化
- 分析命令性能提升

**管理运维**

- `pg_stat_io` 视图：详细的 I/O 统计信息
- 新增预定义角色 `pg_create_subscription`
- 更多细粒度的权限控制

---

### PostgreSQL 15 (2022-10-13)

**SQL 功能**

- **MERGE 命令** (SQL 标准)：单条语句实现 INSERT/UPDATE/DELETE
- 正则表达式新函数: `regexp_count()`, `regexp_instr()`, `regexp_like()`, `regexp_substr()`
- `range_agg` 支持 multirange 类型
- 视图 `security_invoker` 选项

**备份与压缩**

- 备份压缩增强：支持 gzip/lz4/zstd
- 服务端压缩选项
- WAL 压缩支持 LZ4 和 Zstandard

**逻辑复制**

- 列级别过滤
- 行级别过滤
- 选择性复制特定列

**性能**

- 排序性能提升 25%-400%
- 窗口函数性能优化
- `SELECT DISTINCT` 支持并行执行

---

### PostgreSQL 14 (2021-09-30)

**数据类型**

- **Multirange 类型**：支持多区间范围类型
- 范围类型操作增强

**性能**

- 查询管道增强
- 并行查询改进
- 连接性能优化

**管理**

- 多范围类型支持
- 逻辑复制增强

---

### PostgreSQL 13 (2020-09-24)

**性能**

- 增量排序
- 并行真空处理
- B-tree 索引优化

**逻辑复制**

- 分区表逻辑复制支持
- `publish_via_partition_root` 选项

**功能**

- 行级安全策略增强
- 更多 DML 操作返回统计信息

---

### PostgreSQL 12 (2019-10-03)

**性能**

- **JIT 编译** (Just-In-Time) 默认启用
- CTE 支持内联优化
- 分区表性能大幅提升

**功能**

- 生成列 (Generated Columns)
- 可插拔表存储接口
- 多列统计信息

**索引**

- REINDEX CONCURRENTLY
- 分区表支持外键引用

---

### PostgreSQL 11 (2018-10-18)

**分区表**

- **哈希分区** (Hash Partitioning)
- **默认分区** (Default Partition)
- 分区表支持主键、外键、唯一约束
- UPDATE 分区键支持自动迁移

**并行查询**

- 并行哈希连接
- 并行 CREATE INDEX
- 并行分区扫描

**存储过程**

- 真正的存储过程支持 (支持事务控制)

---

### PostgreSQL 10 (2017-10-05)

**分区表**

- **声明式分区** (Declarative Partitioning)
- RANGE 和 LIST 分区
- 分区裁剪 (Partition Pruning)

**逻辑复制**

- **逻辑复制** 内置支持 (发布/订阅模式)
- 基于逻辑解码的复制

**并行查询**

- 并行位图堆扫描
- 并行索引扫描
- 并行合并连接

---

### PostgreSQL 9.6 (2016-09-29)

**并行查询**

- **并行顺序扫描** (Parallel Sequential Scan)
- 并行聚合

**性能**

- 同步复制改进
- 多核 CPU 利用增强

**文本搜索**

- 短语搜索支持

---

### PostgreSQL 9.5 (2016-01-07)

**数据类型**

- **JSONB** 路径操作符
- BRIN 索引 (Block Range Indexes)

**SQL 功能**

- UPSERT (`INSERT ON CONFLICT`)
- GROUPING SETS, CUBE, ROLLUP
- 行级安全策略 (Row-Level Security)

---

## 版本升级建议

### PG14 → PG15 注意事项

| 检查项 | 说明 |
|--------|------|
| MERGE 命令 | 可利用新特性简化 UPSERT 逻辑 |
| 压缩配置 | WAL 压缩新增 LZ4/zstd 选项 |
| 权限变更 | `CREATEROLE` 权限限制更严格 |
| 排序内存 | 排序性能提升，可能需要调整 work_mem |

### PG15 → PG16 注意事项

| 检查项 | 说明 |
|--------|------|
| SQL/JSON | 可使用新构造器简化 JSON 操作 |
| 逻辑复制 | 支持从备库复制，架构更灵活 |
| VACUUM | 并行 VACUUM 性能提升 |
| 权限角色 | 新增 `pg_create_subscription` 角色 |

### PG16 → PG17 注意事项

> 参考: `PostgreSQL_Formal/00-Version-Specific/17-Released/17.08-Upgrade-Guide-DEEP-V2.md`

| 检查项 | 说明 |
|--------|------|
| VACUUM 内存 | 优化了 VACUUM 内存使用 |
| 增量备份 | 支持增量备份 |
| JSON_TABLE | SQL/JSON 标准支持 |
| MERGE 增强 | RETURNING 子句支持 |

---

## EOL 版本风险提示

运行已停止支持的 PostgreSQL 版本将面临以下风险：

- 🔴 **安全风险**: 不再接收安全补丁，存在已知漏洞
- 🔴 **合规风险**: 无法满足安全审计和合规要求
- 🔴 **支持风险**: 社区不再提供技术支持
- 🟡 **迁移成本**: 版本跨度越大，升级难度越高

---

## 参考资源

- [PostgreSQL 官方版本支持政策](https://www.postgresql.org/support/versioning/)
- [PostgreSQL 发布说明](https://www.postgresql.org/docs/release/)
- [PostgreSQL EOL 日期](https://eosl.date/eol/product/postgresql/)
