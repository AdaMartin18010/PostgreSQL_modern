# PostgreSQL_Formal 版本对齐与更新计划

> **制定日期**: 2026-04-07
> **对齐目标**: PostgreSQL 17 (已发布) + PostgreSQL 18 (已发布) + PostgreSQL 19 (开发中)
> **当前状态分析**: 项目主要覆盖 PG18 预览特性，缺少 PG17 正式覆盖

---

## 📊 第一部分：版本现状分析

### 1.1 PostgreSQL 官方版本时间线

| 版本 | 发布日期 | 状态 | 本项目覆盖 | 差距 |
|------|----------|------|------------|------|
| **PostgreSQL 16** | 2023-09-14 | 维护中 | 部分提及 | ⚠️ 无系统覆盖 |
| **PostgreSQL 17** | 2024-09-26 | ✅ 当前稳定版 | ❌ 几乎无覆盖 | 🔴 严重缺失 |
| **PostgreSQL 18** | 2025-09-25 | ✅ 已发布 | 有12篇深度文档 | 🟡 需核实准确性 |
| **PostgreSQL 19** | 2026-09 (预计) | 开发中 | ❌ 无覆盖 | 🟢 正常 |

### 1.2 关键发现

#### 🔴 发现 1：PG17 系统覆盖缺失

- 项目中几乎没有对 PG17 正式特性的系统性覆盖
- 00-NewFeatures-18 直接跳过了 PG17
- PG17 是重要的稳定版本，有大量生产用户

#### 🟡 发现 2：PG18 文档准确性待核实

根据官方信息核实 PG18 特性文档：

| 项目文档特性 | 声称版本 | 实际状态 | 核实结果 |
|--------------|----------|----------|----------|
| AIO (异步I/O) | PG18 | ✅ 已确认 | 准确 |
| B-tree Skip Scan | PG18 | ✅ 已确认 | 准确 |
| UUIDv7 | PG18 | ✅ 已确认 | 准确 |
| 虚拟生成列 | PG18 | ✅ 已确认 | 准确 |
| **时态约束** | PG18 | ⚠️ **存疑** | **需核实** |
| OAuth2/SSO | PG18 | ✅ 已确认 | 准确 |
| 并行GIN构建 | PG18 | ✅ 已确认 | 准确 |
| pg_upgrade增强 | PG18 | ✅ 已确认 | 准确 |
| pgvector | PG18 | ⚠️ 扩展 | 说明清楚 |
| CloudNativePG | PG18 | ⚠️ 外部工具 | 说明清楚 |
| OpenTelemetry | PG18 | ✅ 已确认 | 准确 |
| LZ4压缩 | PG18 | ✅ 已确认 | 准确 |

**⚠️ 特别关注点**：时态约束 (Temporal Constraints)

- 在 PG17 开发周期中被回滚
- 需要确认是否真的进入 PG18
- 当前文档可能需要标记为"预览/实验性"

### 1.3 PG17 核心特性清单（需补充覆盖）

根据官方发布说明，PG17 主要新特性：

#### 性能优化

1. **VACUUM 内存优化** - 新内部内存结构，内存消耗降低 20倍
2. **增量备份** - `pg_basebackup` 支持增量备份
3. **SQL/JSON 增强** - `JSON_TABLE` 函数支持
4. **MERGE 命令增强** - `WHEN NOT MATCHED BY SOURCE` 支持
5. **B-tree 索引优化** - 支持范围查询优化

#### 高可用与复制

1. **逻辑复制槽保留** - 升级时无需删除复制槽
2. **逻辑复制故障转移** - 支持故障转移控制
3. **`pg_createsubscriber`** - 物理副本转逻辑副本工具

#### 安全与运维

1. **`pg_maintain` 角色** - 维护操作权限分离
2. **`allow_alter_system`** - 禁止 ALTER SYSTEM 配置
3. **TLS ALPN 支持** - 直接 TLS 握手
4. **数据校验和默认开启** - 新集群默认启用

#### 监控与诊断

1. **`pg_wait_events`** 系统视图 - 等待事件详细视图
2. **EXPLAIN 增强** - 显示 I/O 块读写时间
3. **VACUUM 进度报告** - 显示索引清理进度
4. **`pg_stat_checkpointer`** - 检查点详细统计

---

## 🎯 第二部分：版本对齐行动计划

### 2.1 重组文档结构

```
当前结构 (问题):
📦 00-NewFeatures-18/          ← 直接跳到18，跳过17
   ├── 18.01-AIO-DEEP-V2.md
   ├── ...
   └── 18.12-LZ4-Compression.md

建议新结构:
📦 00-Version-Specific/         ← 按版本组织
   ├── 📁 17-Released/          ← 新增：PG17 正式特性
   │   ├── 17.01-VACUMM-Memory-Optimization.md
   │   ├── 17.02-Incremental-Backup.md
   │   ├── 17.03-JSON_TABLE.md
   │   ├── 17.04-MERGE-Enhancements.md
   │   ├── 17.05-Logical-Replication-Slot-Preservation.md
   │   ├── 17.06-Logical-Replication-Failover.md
   │   ├── 17.07-pg_createsubscriber.md
   │   ├── 17.08-pg_maintain-Role.md
   │   ├── 17.09-pg_wait_events.md
   │   ├── 17.10-EXPLAIN-Enhancements.md
   │   └── 17.11-Data-Checksums-Default.md
   │
   ├── 📁 18-Released/          ← 现有文档迁移
   │   ├── 18.01-AIO-DEEP-V2.md
   │   ├── 18.02-SkipScan-DEEP-V2.md
   │   ├── 18.03-UUIDv7-DEEP-V2.md
   │   ├── 18.04-Virtual-Generated-Columns.md
   │   ├── 18.05-Temporal-Constraints.md  ← 需核实
   │   ├── 18.06-OAuth2-Integration.md
   │   ├── 18.07-Parallel-GIN-Build.md
   │   ├── 18.08-pg_upgrade-Enhancements.md
   │   ├── 18.09-pgvector.md
   │   ├── 18.10-CloudNativePG.md
   │   ├── 18.11-OpenTelemetry.md
   │   └── 18.12-LZ4-Compression.md
   │
   └── 📁 19-Preview/           ← 新增：PG19 预览
       └── (待开发)
```

### 2.2 任务清单与优先级

#### Phase 1：PG17 核心特性补充 (P0 - 最高优先级)

| 任务ID | 任务 | 优先级 | 工作量 | 截止日期 |
|--------|------|--------|--------|----------|
| PG17-01 | VACUUM 内存优化深度文档 | P0 | 3天 | Week 1 |
| PG17-02 | 增量备份完整指南 | P0 | 3天 | Week 1 |
| PG17-03 | SQL/JSON JSON_TABLE 详解 | P0 | 2天 | Week 2 |
| PG17-04 | MERGE 命令增强 | P0 | 2天 | Week 2 |
| PG17-05 | 逻辑复制升级改进 | P0 | 3天 | Week 2 |
| PG17-06 | pg_maintain 角色与安全 | P0 | 2天 | Week 3 |
| PG17-07 | 监控诊断增强汇总 | P0 | 2天 | Week 3 |
| PG17-08 | PG17 升级指南 | P0 | 2天 | Week 3 |

**Phase 1 交付物**:

- 8篇深度技术文档
- 每篇 5000+ 字
- 包含实际测试代码
- 与 PG16/PG15 的对比分析

#### Phase 2：PG18 文档核实与修正 (P1 - 高优先级)

| 任务ID | 任务 | 优先级 | 工作量 | 截止日期 |
|--------|------|--------|--------|----------|
| PG18-01 | 核实时态约束特性状态 | P1 | 1天 | Week 1 |
| PG18-02 | 更新 PG18 文档元数据 | P1 | 2天 | Week 2 |
| PG18-03 | 添加 PG18 升级注意事项 | P1 | 2天 | Week 2 |
| PG18-04 | 区分核心特性 vs 扩展/工具 | P1 | 1天 | Week 2 |

**关键决策点**:

```
关于 18.05-Temporal-Constraints-DEEP-V2.md:

方案 A：如果 PG18 确实包含时态约束
├── 更新文档，添加版本确认信息
└── 添加与 SQL:2011 标准的对比

方案 B：如果 PG18 不包含时态约束
├── 将文档移至 99-Archive/18.05-Temporal-Constraints-Preview.md
├── 添加说明：特性被延迟到 PG19 或更晚
└── 保留内容作为"预览/提案"文档
```

#### Phase 3：版本迁移与索引更新 (P1 - 高优先级)

| 任务ID | 任务 | 优先级 | 工作量 | 截止日期 |
|--------|------|--------|--------|----------|
| MIG-01 | 创建新的 00-Version-Specific 目录 | P1 | 1天 | Week 3 |
| MIG-02 | 迁移 PG18 文档到新结构 | P1 | 1天 | Week 3 |
| MIG-03 | 更新所有内部链接 | P1 | 2天 | Week 4 |
| MIG-04 | 创建版本选择导航页 | P1 | 1天 | Week 4 |
| MIG-05 | 更新主 README | P1 | 1天 | Week 4 |

#### Phase 4：DCA 版本对齐 (P2 - 中优先级)

| 任务ID | 任务 | 优先级 | 工作量 | 截止日期 |
|--------|------|--------|--------|----------|
| DCA-01 | 更新 DCA 文档中的 PG 版本引用 | P2 | 2天 | Week 5 |
| DCA-02 | 添加 PG17/PG18 新特性的 DCA 实践 | P2 | 3天 | Week 5-6 |
| DCA-03 | 更新 Docker 环境到 PG17/PG18 | P2 | 1天 | Week 5 |

---

## 📋 第三部分：详细内容规划

### 3.1 PG17 文档内容模板

每篇 PG17 特性文档应包含：

```markdown
# PG17 特性名称

> **版本**: PostgreSQL 17 (2024-09-26 发布)
> **类型**: [性能/功能/安全/运维]
> **影响等级**: [高/中/低]
> **升级建议**: [必须/推荐/可选]

## 1. 特性概述
- 一句话描述
- 解决的问题
- 与之前版本的对比

## 2. 技术原理
- 实现机制
- 源码分析 (关键函数)
- 性能数据

## 3. 使用指南
- 启用/配置方法
- 参数说明
- 最佳实践

## 4. 升级注意事项
- 从 PG16 升级的特殊步骤
- 回滚方案
- 兼容性检查

## 5. 实际测试
- 测试环境
- 测试脚本
- 性能对比结果

## 6. 与云厂商集成
- AWS RDS PG17 支持情况
- Azure PostgreSQL 支持情况
- 阿里云 PG17 支持情况
```

### 3.2 PG17 特性详细规格

#### 17.01 - VACUUM 内存优化

**核心内容**:

```
主题: VACUUM Memory Management Overhaul
关键改进:
- 新内存结构: VacuumMem 替代旧实现
- 内存消耗: 降低 20倍
- 性能提升: 大型表 VACUUM 速度提升 30-50%
- 配置参数: vacuum_buffer_usage_limit

源码分析:
- src/backend/commands/vacuum.c
- src/backend/storage/buffer/freelist.c

测试场景:
- 100GB+ 表 VACUUM 对比
- 内存使用监控
```

#### 17.02 - 增量备份

**核心内容**:

```
主题: Incremental pg_basebackup
关键改进:
- 支持基于 WAL summary 的增量备份
- 新工具: pg_combinebackup
- 参数: --incremental=MODE

使用场景:
- 日备份策略优化
- 大型数据库备份时间从几小时缩短到几十分钟

兼容性:
- 需要 PostgreSQL 17+ 的 pg_basebackup
- 恢复时需要 pg_combinebackup
```

#### 17.03 - SQL/JSON JSON_TABLE

**核心内容**:

```
主题: JSON_TABLE Function
关键改进:
- 将 JSON 数组转换为关系表
- 支持嵌套路径
- 符合 SQL:2016 标准

使用示例:
SELECT * FROM JSON_TABLE(
    data,
    '$.items[*]'
    COLUMNS (
        id INTEGER PATH '$.id',
        name TEXT PATH '$.name'
    )
) AS jt;

性能考虑:
- 与 jsonb_to_recordset 对比
- 执行计划分析
```

#### 17.04 - MERGE 增强

**核心内容**:

```
主题: MERGE Command Enhancements
关键改进:
- WHEN NOT MATCHED BY SOURCE 子句
- 支持视图作为目标
- RETURNING 子句增强
- merge_action() 函数

应用场景:
- 数据同步 (Sync patterns)
- CDC 场景
- 数据仓库 ETL
```

#### 17.05 - 逻辑复制升级改进

**核心内容**:

```
主题: Logical Replication Upgrades
关键改进:
- 升级时保留逻辑复制槽
- pg_upgrade 自动处理
- 不再需要重新同步

技术细节:
- 复制槽持久化机制
- 与 pg_upgrade 的集成
- 故障转移槽同步
```

---

## 🔄 第四部分：版本支持策略

### 4.1 长期版本支持计划

```
版本支持矩阵 (建议):

PostgreSQL 版本 | 官方EOL   | 本文档支持 | 优先级
----------------|-----------|------------|--------
PG 19           | 2029+     | 预览/跟踪   | 低
PG 18           | 2028+     | 完整支持    | 高
PG 17           | 2027+     | 完整支持    | 最高
PG 16           | 2026+     | 维护支持    | 中
PG 15           | 2026      | 存档        | 低
PG 14及以下     | 已/EOL    | 存档        | 最低
```

### 4.2 内容更新频率

| 内容类型 | 更新频率 | 负责人 |
|----------|----------|--------|
| 新发布版本特性 | 发布后 1个月内 | TBD |
| 现有版本补丁版本 | 每季度审查 | TBD |
| 安全更新 | 即时 | TBD |
| 性能基准 | 每半年 | TBD |

---

## ✅ 第五部分：待确认事项

### 关键决策点 (需要您确认)

#### 决策 1：PG17 覆盖优先级

- [ ] **选项 A**: 优先补齐 PG17 文档 (建议)
  - 投入 3-4 周完成 8 篇核心文档
  - 优先满足当前生产用户需求

- [ ] **选项 B**: 保持现状，仅更新 PG18
  - PG17 仅做简单概述
  - 重点维护 PG18 内容

#### 决策 2：文档结构变更

- [ ] **选项 A**: 采用新的 00-Version-Specific/ 结构 (建议)
  - 清晰按版本组织
  - 便于后续维护

- [ ] **选项 B**: 保持现有 00-NewFeatures-18/ 结构
  - 仅添加 PG17 子目录
  - 减少重构工作量

#### 决策 3：时态约束文档处理

- [ ] **选项 A**: 核实 PG18 正式发布说明后决定
  - 需要 1-2 天调研时间
  - 根据事实调整

- [ ] **选项 B**: 暂时标记为"实验性/预览"
  - 添加免责声明
  - 保留内容但注明状态

#### 决策 4：版本测试环境

- [ ] **选项 A**: 同时支持 PG16/PG17/PG18 三个版本
  - Docker 环境提供多个版本
  - 文档标注版本兼容性

- [ ] **选项 B**: 主要支持 PG17 (稳定版)
  - PG18 作为预览支持
  - 简化维护工作量

---

## 📊 第六部分：预期成果与时间表

### 完整计划甘特图

```
Week:  1    2    3    4    5    6
       |----|----|----|----|----|
Phase 1: PG17 文档
[Vacuum]====>
[Backup]====>
[JSON]  ==>
[MERGE] ==>
[Replication]==>
[Security]==>
[Monitor]==>
[Upgrade]==>

Phase 2: PG18 核实
[Verify] =>
[Update]   =>

Phase 3: 迁移
[Restructure]    ====>
[Links]              ====>

Phase 4: DCA 对齐
[DCA Update]                ====>
```

### 6周后交付物

1. **8篇 PG17 深度文档** (每篇 5000+ 字)
2. **更新后的版本目录结构**
3. **核实的 PG18 文档集**
4. **版本选择导航页**
5. **更新的 Docker 环境** (支持 PG17/PG18)

### 成功指标

| 指标 | 当前 | 目标 | 测量方式 |
|------|------|------|----------|
| PG17 特性覆盖率 | 5% | 80%+ | 核心特性文档数 |
| 版本结构清晰度 | 中 | 高 | 目录导航评分 |
| 内容准确性 | 90% | 95%+ | 错误报告数 |
| 读者满意度 | 未知 | 4.5/5 | 反馈调查 |

---

**计划制定**: 2026-04-07
**建议启动日期**: 待确认后
**预计完成日期**: 6周后

---

*此计划待您审阅确认后执行*
