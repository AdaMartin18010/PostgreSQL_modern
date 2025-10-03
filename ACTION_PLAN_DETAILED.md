# PostgreSQL_modern 项目改进行动计划（详细版）

> **计划制定日期**：2025年10月3日  
> **计划执行期**：2025年10月 - 2026年1月（12周）  
> **计划类型**：分阶段、可中断、可恢复

---

## 🎯 计划总览

### 执行原则

1. **渐进式改进**：每个Phase独立可交付
2. **可中断恢复**：每个任务有明确起止点，可随时暂停/恢复
3. **优先级驱动**：标注P0/P1/P2，资源不足时砍低优先级
4. **度量驱动**：每个任务有可验证的完成标准

### 阶段概览

| **阶段** | **周期** | **核心目标** | **交付物** | **优先级** |
|---------|---------|------------|-----------|----------|
| Phase 1 | W1-W2 | 紧急修复可信度 | 质量矩阵+基础扩充 | P0 |
| Phase 2 | W3-W6 | 结构性改进 | 学习路径+对标表 | P1 |
| Phase 3 | W7-W10 | 深度提升 | Level 3模块+案例 | P1 |
| Phase 4 | W11-W12 | 工程化 | CI/CD+社区化 | P2 |
| Phase 5 | W13+ | 持续演进 | 长期维护机制 | P2 |

---

## 📅 Phase 1：紧急修复（W1-W2）

### 目标

修复"过度承诺"问题，提升项目可信度，夯实基础内容。

---

### 任务 1.1：诚实的质量标注

**优先级**：P0  
**工作量**：4小时  
**负责人**：项目Owner

#### 行动清单

- [ ] **Step 1**：创建`QUALITY_MATRIX.md`（1小时）

  ```markdown
  # 模块成熟度矩阵
  
  | 模块 | 当前等级 | 目标等级 | 差距说明 | 预计达成时间 |
  |-----|---------|---------|---------|------------|
  | 01_sql_ddl_dcl | Level 1 | Level 3 | 缺原理详解、案例 | 2025-10-20 |
  | 02_transactions | Level 1 | Level 3 | 缺MVCC原理图 | 2025-10-25 |
  | ... | ... | ... | ... | ... |
  ```

- [ ] **Step 2**：更新主README（1小时）
  - 移除"100%完成"表述
  - 添加"项目现状"章节：

    ```markdown
    ## 📊 项目现状（2025-10-03）
    
    ### 已完成部分
    - ✅ 完整目录结构（16个一级目录）
    - ✅ PostgreSQL 17核心特性覆盖
    - ✅ 分布式数据库深度内容（Level 3）
    - ✅ 3个完整实战案例
    
    ### 进行中部分
    - 🚧 基础模块深度内容（Level 1 → Level 3）
    - 🚧 对标课程/Wiki落地（骨架已建）
    - 🚧 工程化体系建设（CI/测试）
    
    ### 计划完成时间
    - 基础模块：2025年10月底
    - 对标落地：2025年11月底
    - 完整体系：2025年12月底
    ```

- [ ] **Step 3**：在`PROJECT_COMPLETION_CHECKLIST.md`添加说明（30分钟）

  ```markdown
  ## ⚠️ 重要说明
  
  本清单中的"100%完成"指的是**第一阶段目标**（结构搭建+高级特性）的完成度。
  
  **未包含在此清单中的工作**：
  - 基础模块深度扩充（01/02/03目录）
  - 对标课程详细对照表
  - CI/CD自动化测试
  - 社区外部评审
  
  完整项目路线图见：`ACTION_PLAN_DETAILED.md`
  ```

- [ ] **Step 4**：为每个README添加成熟度标签（1.5小时）
  在每个目录的README顶部添加：

  ```markdown
  > **成熟度**：Level 1（骨架级） | 目标：Level 3（教程级）  
  > **更新日期**：2025-10-03 | 预计达成：2025-10-25
  ```

**完成标准**：

- ✅ `QUALITY_MATRIX.md`已创建，16个模块全部标注
- ✅ 主README无"100%完成"表述，新增"项目现状"章节
- ✅ 至少10个README已添加成熟度标签

**输出文件**：

- `QUALITY_MATRIX.md`（新建）
- `README.md`（修改）
- `PROJECT_COMPLETION_CHECKLIST.md`（修改）
- 各目录README（修改）

---

### 任务 1.2：基础模块紧急扩充

**优先级**：P0  
**工作量**：20-24小时（分3个子任务）  
**负责人**：技术内容负责人

---

#### 子任务 1.2.1：扩充`01_sql_ddl_dcl/README.md`

**目标行数**：62 → 500行  
**工作量**：8小时

**内容大纲**（建议）：

```markdown
# 01_sql_ddl_dcl（扩充版）

## 📋 目录
[现有内容保留]

## 1. SQL语言基础（新增 ~100行）
### 1.1 数据类型详解
- 数值类型：INT vs BIGINT vs NUMERIC（精度陷阱）
- 字符类型：CHAR vs VARCHAR vs TEXT（性能对比）
- 日期时间：TIMESTAMP vs TIMESTAMPTZ（时区陷阱）
- JSON类型：JSON vs JSONB（存储与索引）

[配表格对比、代码示例]

### 1.2 标识符与命名规范
- 大小写敏感性（带引号 vs 不带引号）
- 保留字冲突处理
- Schema命名空间
- 命名最佳实践（团队规范模板）

## 2. DDL深度实战（新增 ~150行）
### 2.1 表设计陷阱案例
**案例1：主键选择的代价**
- 自增ID vs UUID vs 雪花ID
- 性能测试数据（插入TPS、表大小、索引大小）
- 决策树

**案例2：约束的性能影响**
- 外键约束：何时用、何时不用
- 检查约束：性能 vs 数据完整性
- 延迟约束验证

**案例3：分区表设计**
- 分区键选择（范围 vs 列表 vs 哈希）
- 子分区数量与查询性能
- 分区表维护（ATTACH/DETACH）

[每个案例：问题描述 → SQL代码 → 测试结果 → 最佳实践]

### 2.2 在线DDL最佳实践
- CREATE INDEX CONCURRENTLY原理与陷阱
- ALTER TABLE的锁级别
- 大表结构变更策略（逻辑复制/双写）

## 3. DML优化技巧（新增 ~100行）
### 3.1 批量操作
- INSERT多行 vs 单行（性能对比）
- COPY命令最佳实践
- RETURNING子句的妙用

### 3.2 CTE与窗口函数
- WITH RECURSIVE实战案例（树形数据）
- 窗口函数性能陷阱
- CTE物化 vs 内联

### 3.3 UPSERT模式
- INSERT ... ON CONFLICT
- 并发安全性分析
- 性能优化建议

## 4. DCL与权限模型（新增 ~80行）
### 4.1 角色与权限最佳实践
- 角色继承体系设计
- 最小权限原则
- 多租户权限隔离

### 4.2 行级安全（RLS）
- 策略创建与性能影响
- 与应用层鉴权对比
- 使用场景

## 5. PostgreSQL 17新特性（新增 ~50行）
- MERGE命令增强（如适用）
- SQL:2023新特性
- [链接到04_modern_features/pg17_new_features.md]

## 6. 常见陷阱汇总（新增 ~20行）
| 陷阱 | 表现 | 原因 | 解决方案 |
|-----|-----|-----|---------|
| 隐式类型转换导致索引失效 | Seq Scan | WHERE col::text | 修改列类型/表达式索引 |
| 大小写混用 | 列名找不到 | 未加引号 | 统一小写或全程带引号 |
| ... | ... | ... | ... |

[现有Checklist保留]
```

**完成标准**：

- ✅ 行数≥500行
- ✅ 代码示例≥15个
- ✅ 对比表格≥3个
- ✅ 实战案例≥3个
- ✅ 外部链接≥5个（官方文档、Wiki）

---

#### 子任务 1.2.2：扩充`02_transactions/README.md`

**目标行数**：49 → 600行  
**工作量**：10小时

**内容大纲**（建议）：

```markdown
    # 02_transactions（扩充版）

    ## 1. ACID深度解析（新增 ~120行）
    ### 1.1 原子性（Atomicity）
    - WAL机制原理（配架构图）
    - 崩溃恢复流程
    - 部分写问题与双写缓冲

    ### 1.2 一致性（Consistency）
    - 约束检查时机
    - 触发器与一致性
    - 应用层一致性 vs 数据库一致性

    ### 1.3 隔离性（Isolation）
    [见下节详解]

    ### 1.4 持久性（Durability）
    - fsync与数据安全
    - synchronous_commit参数权衡
    - 数据丢失场景分析

    ## 2. MVCC原理详解（新增 ~180行）
    ### 2.1 核心概念
    - XID（事务ID）分配与回卷
    - 快照（Snapshot）结构
    - 元组可见性规则（配流程图）

    ### 2.2 可见性判断
    ```sql
    -- 伪代码
    IF t_xmin IN snapshot.xip THEN
    -- 事务未提交，不可见
    ELSIF t_xmin < snapshot.xmin THEN
    -- 早期事务已提交，可见
    ...
    ```

    ### 2.3 冻结（Freeze）机制

    - 为什么需要冻结
    - autovacuum_freeze_max_age
    - 冻结风暴案例分析

    ### 2.4 系统表查询

    ```sql
    -- 查看当前事务ID
    SELECT txid_current();

    -- 查看表的冻结年龄
    SELECT relname, age(relfrozenxid)
    FROM pg_class
    WHERE relkind = 'r'
    ORDER BY age(relfrozenxid) DESC;
    ```

    ## 3. 隔离级别实战（新增 ~150行）

    ### 3.1 隔离级别对比表

    | 级别 | 脏读 | 不可重复读 | 幻读 | 写偏序 | PG实现 |
    |-----|-----|----------|-----|-------|-------|
    | Read Uncommitted | ❌ | ✅ | ✅ | ✅ | 等同RC |
    | Read Committed | ❌ | ✅ | ✅ | ✅ | 语句级快照 |
    | Repeatable Read | ❌ | ❌ | ❌ | ✅ | 事务级快照 |
    | Serializable | ❌ | ❌ | ❌ | ❌ | SSI |

    ### 3.2 每个级别的实战案例

    **案例1：Read Committed下的不可重复读**：

    ```sql
    -- Session A
    BEGIN;
    SELECT balance FROM accounts WHERE id = 1; -- 100

    -- Session B
    BEGIN;
    UPDATE accounts SET balance = 200 WHERE id = 1;
    COMMIT;

    -- Session A（继续）
    SELECT balance FROM accounts WHERE id = 1; -- 200（已变化！）
    COMMIT;
    ```

    [类似案例覆盖RR和Serializable]

    ### 3.3 SSI（可串行化快照隔离）原理

    - 危险结构检测
    - rw-conflicts追踪
    - 性能开销分析
    - 适用场景

    ## 4. 锁机制详解（新增 ~100行）

    ### 4.1 锁的层次与类型

    [表格：锁模式冲突矩阵]

    ### 4.2 行级锁实战

    - FOR UPDATE vs FOR SHARE
    - NOWAIT vs SKIP LOCKED
    - 热点行竞争优化

    ### 4.3 表级锁

    - ACCESS SHARE vs EXCLUSIVE
    - DDL锁等待案例

    ### 4.4 死锁检测与预防

    **死锁案例**：

    ```sql
    -- Session A
    BEGIN;
    UPDATE orders SET status = 'processing' WHERE id = 1;

    -- Session B
    BEGIN;
    UPDATE orders SET status = 'processing' WHERE id = 2;

    -- Session A
    UPDATE orders SET status = 'processed' WHERE id = 2; -- 等待B

    -- Session B
    UPDATE orders SET status = 'processed' WHERE id = 1; -- 死锁！
    ```

    **预防策略**：

    1. 统一锁顺序
    2. 使用NOWAIT快速失败
    3. 减少事务范围

    ## 5. 长事务危害与治理（新增 ~50行）

    ### 5.1 危害

    - MVCC膨胀
    - 冻结延迟
    - 复制延迟（逻辑复制）

    ### 5.2 检测

    ```sql
    -- 查询运行超过5分钟的事务
    SELECT pid, now() - xact_start AS duration, state, query
    FROM pg_stat_activity
    WHERE (now() - xact_start) > interval '5 minutes'
    AND state <> 'idle'
    ORDER BY duration DESC;
    ```

    ### 5.3 治理

    - 应用层拆分事务
    - 连接池idle_in_transaction_timeout
    - 主动监控与告警

    [现有Checklist保留并扩充]

```

**完成标准**：

- ✅ 行数≥600行
- ✅ 原理图≥2个（MVCC可见性、锁冲突矩阵）
- ✅ 代码示例≥20个
- ✅ 对比表格≥2个
- ✅ 实战案例≥5个

---

#### 子任务 1.2.3：扩充`03_storage_access/README.md`

**目标行数**：63 → 600行  
**工作量**：10小时

**内容大纲**（建议）：

```markdown
    # 03_storage_access（扩充版）

    ## 1. 存储结构详解（新增 ~100行）
    ### 1.1 堆表（Heap Table）
    - 页面结构（8KB）
    - 元组头部（t_xmin, t_xmax, t_ctid）
    - TOAST原理与性能影响

    ### 1.2 FILLFACTOR
    - 默认值100 vs 建议值90
    - 适用场景（UPDATE密集表）
    - 性能测试数据

    ### 1.3 表膨胀
    - 产生原因（MVCC + 未及时VACUUM）
    - 检测脚本（[链接到bloat_check.sql]）
    - 治理：VACUUM FULL vs pg_repack

    ## 2. 索引类型深度对比（新增 ~200行）
    ### 2.1 B-tree索引
    **原理**：
    - B+树结构（配图）
    - 叶子节点链表
    - 为什么适合范围查询

    **适用场景**：
    - 等值查询（=）
    - 范围查询（<, >, BETWEEN）
    - 排序（ORDER BY）
    - 最左前缀原则

    **陷阱**：
    ```sql
    -- 索引失效案例
    CREATE INDEX idx_users_email ON users(email);

    -- 会使用索引
    SELECT * FROM users WHERE email = 'user@example.com';

    -- 不会使用索引（函数调用）
    SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

    -- 解决：表达式索引
    CREATE INDEX idx_users_email_lower ON users(LOWER(email));
    ```

    ### 2.2 GIN索引

    **原理**：

    - 倒排索引结构
    - 适合多值列（数组、JSONB、全文检索）

    **案例**：

    ```sql
    -- JSONB索引
    CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    attributes JSONB
    );

    CREATE INDEX idx_products_attributes ON products USING GIN (attributes);

    -- 高效查询
    SELECT * FROM products WHERE attributes @> '{"color": "red"}';
    ```

    **性能对比**：

    | 操作 | 无索引 | B-tree | GIN | 说明 |
    |-----|-------|--------|-----|-----|
    | 等值查询 | 100ms | 5ms | 3ms | GIN略优 |
    | 包含查询 | 200ms | N/A | 4ms | GIN专用 |
    | 插入 | 1ms | 1.2ms | 2ms | GIN更新慢 |

    ### 2.3 GiST索引

    - 适用场景（几何、范围、全文）
    - 与GIN对比
    - PostGIS实战案例

    ### 2.4 BRIN索引

    - 适用场景（时间序列、自增ID）
    - 超大表（TB级）性能优势
    - 案例：日志表索引

    ### 2.5 Hash索引

    - 何时使用（PG 10+已改进）
    - 与B-tree对比

    ### 2.6 索引选择决策树

    ```
    是多值列（数组/JSONB）？
    ├─ 是 → GIN
    └─ 否 → 是范围查询？
        ├─ 是 → 表有序（时间序列）？
        │    ├─ 是 → BRIN
        │    └─ 否 → B-tree
        └─ 否 → 是几何/空间数据？
                ├─ 是 → GiST
                └─ 否 → B-tree
    ```

    ## 3. 执行计划解读（新增 ~150行）

    ### 3.1 EXPLAIN输出解读

    ```sql
    EXPLAIN (ANALYZE, BUFFERS) 
    SELECT * FROM orders 
    WHERE user_id = 123 
    ORDER BY created_at DESC 
    LIMIT 10;
    ```

    **输出示例**：

    ```
    Limit  (cost=0.43..8.45 rows=10 width=120) (actual time=0.023..0.045 rows=10 loops=1)
    Buffers: shared hit=5
    ->  Index Scan Backward using idx_orders_user_created on orders  
        (cost=0.43..802.56 rows=1000 width=120) (actual time=0.022..0.042 rows=10 loops=1)
            Index Cond: (user_id = 123)
            Buffers: shared hit=5
    Planning Time: 0.123 ms
    Execution Time: 0.067 ms
    ```

    **关键指标解读**：

    - **cost**：代价估算（启动代价..总代价）
    - **rows**：估计行数 vs 实际行数（差距过大说明统计信息失真）
    - **actual time**：实际执行时间
    - **Buffers**：缓冲区命中（shared hit）vs 磁盘读取（read）
    - **loops**：节点执行次数（>1警惕嵌套循环）

    ### 3.2 常见扫描类型

    | 扫描类型 | 触发条件 | 性能 | 优化建议 |
    |---------|---------|-----|---------|
    | Seq Scan | 无索引/全表扫描 | 慢（大表） | 添加索引 |
    | Index Scan | 索引覆盖+回表 | 中等 | 覆盖索引 |
    | Index Only Scan | 索引覆盖列 | 快 | 理想状态 |
    | Bitmap Index Scan | 多索引合并 | 中等 | 检查索引选择性 |

    ### 3.3 JOIN策略

    - Nested Loop：小表驱动
    - Hash Join：等值连接+内存足够
    - Merge Join：已排序数据

    ### 3.4 统计信息

    ```sql
    -- 更新统计信息
    ANALYZE orders;

    -- 查看统计信息
    SELECT * FROM pg_stats WHERE tablename = 'orders';

    -- 扩展统计（多列相关性）
    CREATE STATISTICS stats_orders_user_status 
    ON user_id, status 
    FROM orders;
    ```

    ## 4. 维护操作详解（新增 ~100行）

    ### 4.1 VACUUM原理

    - 死元组回收
    - FSM（Free Space Map）更新
    - 冻结旧事务

    ### 4.2 VACUUM vs VACUUM FULL

    | 操作 | 锁级别 | 空间回收 | 执行时间 | 推荐场景 |
    |-----|-------|---------|---------|---------|
    | VACUUM | ShareUpdateExclusiveLock | 标记可用 | 短 | 常规维护 |
    | VACUUM FULL | AccessExclusiveLock | 完全回收 | 长 | 重度膨胀 |

    ### 4.3 Autovacuum调优

    ```sql
    -- 表级调优
    ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- 默认0.2
    autovacuum_analyze_scale_factor = 0.02  -- 默认0.1
    );
    ```

    ### 4.4 REINDEX

    - 何时需要（索引膨胀、损坏）
    - REINDEX CONCURRENTLY（PG 12+）
    - 风险与最佳实践

    ## 5. PostgreSQL 17存储优化（新增 ~50行）

    - 流式I/O优化（大表扫描）
    - VACUUM内存管理改进
    - [链接到pg17_new_features.md]

    [现有Checklist保留并扩充]

```

**完成标准**：

- ✅ 行数≥600行
- ✅ 架构图≥2个（页面结构、索引决策树）
- ✅ 代码示例≥25个
- ✅ 对比表格≥4个
- ✅ 执行计划案例≥3个

---

### 任务 1.3：版本时效性检查

**优先级**：P0  
**工作量**：4小时  
**负责人**：项目维护者

#### 行动清单1

- [ ] **Step 1**：检查扩展最新版本（2小时）

  ```bash
  # 脚本：tools/check_versions.sh
  #!/bin/bash
  
  # pgvector
  echo "=== pgvector ==="
  curl -s https://api.github.com/repos/pgvector/pgvector/releases/latest | jq -r '.tag_name'
  
  # TimescaleDB
  echo "=== TimescaleDB ==="
  curl -s https://api.github.com/repos/timescale/timescaledb/releases/latest | jq -r '.tag_name'
  
  # PostGIS
  echo "=== PostGIS ==="
  curl -s https://api.github.com/repos/postgis/postgis/releases/latest | jq -r '.tag_name'
  
  # Citus
  echo "=== Citus ==="
  curl -s https://api.github.com/repos/citusdata/citus/releases/latest | jq -r '.tag_name'
  ```

- [ ] **Step 2**：更新版本建议（1小时）
  修改`04_modern_features/version_diff_16_to_17.md`：

```markdown
    ### 扩展兼容性验证
    
    **PostgreSQL 17兼容扩展版本**（更新于2025-10-03）：
    
    | 扩展 | 最低版本 | 推荐版本 | 最新版本 | 验证状态 |
    |-----|---------|---------|---------|---------|
    | pgvector | 0.7.0 | 0.7.4 | [动态] | ✅ 已验证 |
    | TimescaleDB | 2.14.0 | 2.16.1 | [动态] | ✅ 已验证 |
    | PostGIS | 3.4.0 | 3.4.2 | [动态] | ✅ 已验证 |
    | Citus | 12.0.0 | 12.1.1 | [动态] | ✅ 已验证 |
    
    **检查命令**：
    ```sql
    SELECT * FROM pg_available_extensions 
    WHERE name IN ('vector', 'timescaledb', 'postgis', 'citus');
    ```
```

- [ ] **Step 3**：检查PostgreSQL 18状态（30分钟）
  - 访问：<https://www.postgresql.org/developer/roadmap/>
  - 检查PostgreSQL 18 Beta发布状态
  - 如已发布，创建`04_modern_features/pg18_preview.md`

- [ ] **Step 4**：创建版本监控Issue模板（30分钟）

```markdown
    # .github/ISSUE_TEMPLATE/version_update.md
    ---
    name: 版本更新检查
    about: 每月检查上游版本更新
    title: '[VERSION] 2025-XX月版本巡检'
    labels: 'maintenance, version'
    assignees: ''
    ---

    ## 检查清单

    ### PostgreSQL核心
    - [ ] 当前最新稳定版：__.__
    - [ ] 项目已对齐版本：17
    - [ ] 是否需要更新：是/否

    ### pgvector
    - [ ] 最新版本：v__.__.__
    - [ ] 项目建议版本：____
    - [ ] 是否需要更新：是/否

    [类似检查TimescaleDB/PostGIS/Citus]

    ## 更新计划
    - [ ] 更新version_diff文档
    - [ ] 更新扩展README
    - [ ] 测试新版本兼容性
    - [ ] 更新CHANGELOG
```

**完成标准**：

- ✅ `tools/check_versions.sh`已创建并可运行
- ✅ 至少4个扩展版本已验证更新
- ✅ PostgreSQL 18状态已确认（如有Beta，已创建preview文档）
- ✅ 版本监控Issue模板已创建

**输出文件**：

- `tools/check_versions.sh`（新建）
- `04_modern_features/version_diff_16_to_17.md`（更新）
- `04_modern_features/pg18_preview.md`（如适用，新建）
- `.github/ISSUE_TEMPLATE/version_update.md`（新建）

---

### Phase 1 交付物检查清单

**在Phase 1结束前，必须确认**：

- [ ] `QUALITY_MATRIX.md`已创建，所有模块已标注成熟度
- [ ] 主README已移除过度承诺表述，添加"项目现状"章节
- [ ] `01_sql_ddl_dcl/README.md`已达到500+行
- [ ] `02_transactions/README.md`已达到600+行
- [ ] `03_storage_access/README.md`已达到600+行
- [ ] 版本检查脚本已创建并运行
- [ ] 至少4个扩展版本信息已更新
- [ ] 版本监控Issue模板已创建

**验收标准**：

- 总新增内容：~1,800行（高质量文档）
- 代码示例：≥60个
- 实战案例：≥10个
- 外部评审：至少1人审查基础模块扩充内容

---

## 📅 Phase 2-5 概要（详细计划见后续）

### Phase 2：结构性改进（W3-W6）

**关键任务**：

1. 创建`00_overview/LEARNING_PATHS.md`（4条学习路径）
2. 扩充`GLOSSARY.md`至200+行
3. 完成`12_comparison_wiki_uni/mapping_table.md`（20个主题对照）
4. 在3个核心README嵌入对标阅读链接

**交付物**：

- 学习路径文档
- 完整术语表
- 对标映射表
- 更新的README（嵌入对标链接）

---

### Phase 3：深度提升（W7-W10）

**关键任务**：

1. 3个基础模块达到Level 3（每个600-900行）
2. 新增3个生产级案例（高并发OLTP、OLAP仓库、多租户SaaS）
3. 创建`tools/`目录，添加3个工具脚本

**交付物**：

- Level 3基础模块（3个）
- 生产级案例（3个）
- 实用工具脚本（3个）

---

### Phase 4：工程化（W11-W12）

**关键任务**：

1. 搭建GitHub Actions CI（SQL测试、链接检查）
2. 完善贡献者指南（100行）
3. 邀请3-5名外部专家评审

**交付物**：

- CI/CD配置文件
- 详细贡献指南
- 外部评审报告

---

### Phase 5：持续演进（W13+）

**长期机制**：

1. 月度版本巡检（自动化Issue）
2. 季度深度案例（1个/季度）
3. 年度对标课程更新
4. 社区贡献者培养

---

## 📊 进度跟踪

### 使用方法

**方式1：GitHub Issues**：

- 为每个Phase创建Milestone
- 为每个任务创建Issue，关联Milestone
- 使用Labels标注优先级（P0/P1/P2）

**方式2：项目看板**：

- 创建`PROJECT_BOARD.md`
- 使用TODO/IN_PROGRESS/DONE列
- 每周更新进度

**方式3：周报**：

- 每周五更新`WEEKLY_REPORT.md`
- 记录完成任务、遇到问题、下周计划

---

## 💡 应急预案

### 如果时间不足

**优先级裁剪**：

- **必保**（P0）：Phase 1全部任务
- **重保**（P1）：Phase 2任务1-2，Phase 3任务1
- **可砍**（P2）：Phase 4全部，Phase 2任务3-4

### 如果人力不足

**最小可行方案**：

1. **只做Phase 1**（2周）→ 发布v0.2（基础夯实版）
2. **Phase 1 + Phase 2任务1**（4周）→ 发布v0.3（可导航版）
3. **完整Phase 1-3**（10周）→ 发布v1.0（教程级）

### 如果需要外部帮助

**可寻求帮助的领域**：

- 基础模块扩充：PostgreSQL DBA（内容审校）
- 案例开发：后端工程师（场景设计）
- 对标工作：高校教师/学生（课程对照）
- 工程化：DevOps工程师（CI/CD搭建）

---

## 📞 联系与反馈

**项目负责人**：[待填写]  
**技术审校**：[待邀请]  
**社区反馈渠道**：GitHub Issues

---

**最后更新**：2025-10-03  
**下次评审**：2025-10-20（Phase 1结束后）

---

*本计划是工作指南，而非教条。根据实际情况灵活调整，但必须保持透明沟通。*
