# PostgreSQL 19 新特性跟踪

## 版本信息

- **预计发布**: 2026年9月
- **当前状态**: 开发中 (Feature Freeze 预计 2026年3月)
- **跟踪日期**: 2026-04-07
- **首个 Beta**: 预计 2026年5月

## CommitFest 时间线

| CommitFest | 时间 | 状态 | 说明 |
|------------|------|------|------|
| PG19-1 (CF 2025-07) | 2025-07-01 ~ 2025-07-31 | ✅ 已完成 | 第一阶段开发 |
| PG19-2 (CF 2025-09) | 2025-09-01 ~ 2025-09-30 | ✅ 已完成 | 第二阶段开发 |
| PG19-3 (CF 2025-11) | 2025-11-01 ~ 2025-11-30 | ✅ 已完成 | 第三阶段开发 |
| PG19-4 (CF 2026-01) | 2026-01-01 ~ 2026-01-31 | ✅ 已完成 | 第四阶段开发 |
| PG19-5 (CF 2026-03) | 2026-03-01 ~ 2026-03-31 | 🔄 进行中 | Feature Freeze 前最后阶段 |
| Feature Freeze | 2026年3月/4月 | ⏳ 预计 | 新特性冻结 |
| Beta 1 | 2026年5月 | ⏳ 预计 | 首个测试版本 |
| GA Release | 2026年9月/10月 | ⏳ 预计 | 正式版本发布 |

## 已确认重要特性

### 1. 分区表增强 ⭐ 高优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| MERGE PARTITIONS | ✅ 已提交 | 合并多个分区为一个分区 |
| SPLIT PARTITION | ✅ 已提交 | 将一个分区拆分为多个分区 |

**详细说明**:

- 实现了 `ALTER TABLE ... MERGE PARTITIONS ...` 命令
- 实现了 `ALTER TABLE ... SPLIT PARTITION ...` 命令
- 当前实现为单进程，在整个操作期间持有父表的 ACCESS EXCLUSIVE LOCK
- 不适合在高负载下的大型分区表上使用
- 为未来降低锁级别和并行执行奠定基础

**提交信息**:

- Commit: f2e4cc42795, 4b3d173629f
- 作者: Dmitry Koval, Alexander Korotkov 等

### 2. SQL 标准兼容性 ⭐ 高优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| GROUP BY ALL | ✅ 已提交 | 自动包含所有非聚合 SELECT 表达式 |
| Window Functions IGNORE NULLS | ✅ 已提交 | lag/lead/first_value/last_value/nth_value 支持 |
| standard_conforming_strings 移除 | ✅ 已提交 | 不再支持关闭该参数 |

**详细说明**:

- `GROUP BY ALL` 已纳入 SQL 标准
- Window functions 支持 `IGNORE NULLS` 和 `RESPECT NULLS` (默认)
- `standard_conforming_strings` 和 `escape_string_warning` 参数被移除

### 3. 逻辑复制增强 ⭐ 高优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| 动态 WAL 级别 | ✅ 已提交 | 根据逻辑复制槽自动调整 WAL 级别 |
| 槽同步监控 | ✅ 已提交 | 新增 slotsync_skip_reason 等监控列 |

**详细说明**:

- 创建逻辑复制槽时自动提升 effective_wal_level 到 logical
- 删除最后一个槽后自动降级到 replica
- 新增 `slotsync_skip_reason`, `slotsync_skip_count`, `slotsync_last_skip` 监控列

### 4. 性能优化 ⭐ 高优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| jsonb_agg 优化 | ✅ 已提交 | 整数和数值类型处理速度显著提升 |
| LISTEN/NOTIFY 优化 | ✅ 已提交 | 使用哈希表管理通道和接收者 |
| ICU 字符转换优化 | ✅ 已提交 | UTF8 数据库的大小写转换函数优化 |
| Buffer Cache 算法改进 | ✅ 已提交 | 使用 clock-sweep 算法替代空闲缓冲区列表 |

**性能数据**:

- jsonb_agg: PG18 677ms → PG19 374ms (提升约 45%)
- ICU upper(): PG18 3107ms → PG19 1816ms (提升约 42%)

### 5. 监控和可观测性 ⭐ 中优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| VACUUM 进度监控增强 | ✅ 已提交 | 新增 mode, started_by 列 |
| VACUUM 内存使用信息 | ✅ 已提交 | verbose 模式显示内存使用详情 |
| vacuumdb --dry-run | ✅ 已提交 | 预览将要执行的命令 |
| pg_get_multixact_stats() | ✅ 已提交 | 多事务统计信息函数 |
| pg_stat_progress_basebackup | ✅ 已提交 | 新增 backup_type 列 |
| log_lock_waits 默认启用 | ✅ 已提交 | 默认开启锁等待日志 |

### 6. 工具和数据导出 ⭐ 中优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| pg_dump 扩展统计信息 | ✅ 已提交 | 支持导出扩展统计信息 |
| file_fdw 跳过行 | ✅ 已提交 | 指定跳过初始行数 |

### 7. PL/Python 增强 ⭐ 中优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| Event Triggers in PL/Python | ✅ 已提交 | 支持用 PL/Python 编写事件触发器 |

### 8. 其他改进 ⭐ 低优先级

| 特性 | 状态 | 说明 |
|------|------|------|
| pg_available_extensions 扩展 | ✅ 已提交 | 新增 location 列显示安装目录 |
| random() 日期时间范围 | ✅ 已提交 | 生成指定范围内的随机日期时间 |
| base64url 编码 | ✅ 已提交 | encode/decode 函数支持 base64url |
| debug_print_raw_parse | ✅ 已提交 | 显示原始解析树 |
| 错误消息改进 | ✅ 已提交 | 函数参数名错误的更精确提示 |

## 潜在重要特性 (开发中/待审查)

| 特性 | 状态 | 优先级 | 说明 |
|------|------|--------|------|
| Bi-directional Replication | 🔄 开发中 | 高 | 双向逻辑复制 |
| 并行 VACUUM | 🔄 开发中 | 高 | 并行执行 VACUUM |
| NUMA 支持优化 | 🔄 开发中 | 中 | NUMA 架构性能优化 |
| 异步 MergeAppend | 🔄 审查中 | 中 | 异步执行 MergeAppend 节点 |
| Star Join 优化 | 🔄 审查中 | 中 | 星型连接查询优化 |
| COPY 格式可扩展 | 🔄 审查中 | 低 | 使 COPY 格式可扩展 |

## 值得关注

### 邮件列表讨论热点

- **pgsql-hackers**: 分区表 MERGE/SPLIT 后续优化讨论
- **pgsql-hackers**: 逻辑复制性能优化
- **pgsql-hackers**: PG20 多线程架构早期讨论

### 核心开发者博客

- [depesz.com](https://www.depesz.com): 定期发布 "Waiting for PostgreSQL 19" 系列
- [postgrespro.com/blog](https://postgrespro.com/blog): CommitFest 详细回顾

### 相关补丁提交

- CommitFest 2026-03 正在审查的补丁
- 性能优化相关补丁
- 监控功能增强补丁

## 重要会议和活动

| 会议 | 时间 | 相关主题 |
|------|------|----------|
| POSETTE 2026 | 2026-04 | Postgres 19 Hackers Panel |
| PGConf.dev 2026 | 2026-05 | 核心开发者会议 |
| Feature Freeze | 2026-03/04 | 新特性冻结截止 |

## 参考链接

- [官方路线图](https://www.postgresql.org/developer/roadmap/)
- [Beta 信息](https://www.postgresql.org/developer/beta/)
- [CommitFest 主页](https://commitfest.postgresql.org/)
- [PG19 CommitFest 1](https://commitfest.postgresql.org/53/)

## 更新日志

- **2026-04-07**: 初始跟踪文档创建
  - 添加版本信息和 CommitFest 时间线
  - 整理已确认特性 (基于 2026-01 CommitFest 结果)
  - 添加潜在特性和值得关注项目

---

*最后更新: 2026-04-07*
*维护者: PostgreSQL 中文社区*
