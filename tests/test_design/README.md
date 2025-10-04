# PostgreSQL_modern 测试设计文档

> **目的**：为基础模块（01/02/03）设计完整的测试用例  
> **目标**：测试覆盖率达到100%  
> **预计新增测试**：45+场景

---

## 📋 测试设计概览

### 设计状态

| 模块 | 测试数量 | 状态 | 完成日期 | 文档链接 |
|------|---------|------|---------|---------|
| **01_sql_ddl_dcl** | 20+ | ✅ 设计完成 | 2025-10-03 | [设计文档](01_sql_ddl_dcl_test_design.md) |
| **02_transactions** | 15+ | 📋 计划中 | 2025-10-04 | TBD |
| **03_storage_access** | 10+ | 📋 计划中 | 2025-10-04 | TBD |
| **总计** | **45+** | - | - | - |

---

## 🎯 设计原则

### 1. 独立性

- 每个测试用例独立运行
- 使用唯一的对象名称（表、索引、角色）
- 完整的SETUP和TEARDOWN

### 2. 可重复性

- 测试结果一致
- 不依赖外部状态
- 自动清理资源

### 3. 覆盖率

- 核心功能100%覆盖
- 边界条件测试
- PostgreSQL 17新特性

### 4. 可维护性

- 清晰的测试命名
- 详细的注释说明
- 标准化的断言

---

## 📚 测试设计文档

### 01_sql_ddl_dcl - SQL DDL/DCL基础（20+测试）

**文档**：[01_sql_ddl_dcl_test_design.md](01_sql_ddl_dcl_test_design.md)

**测试覆盖**：

- **DDL操作**（8个）：CREATE/ALTER/DROP TABLE、约束管理
- **索引操作**（4个）：B-tree、GIN、UNIQUE、REINDEX
- **DCL操作**（4个）：GRANT/REVOKE、角色管理
- **Schema操作**（2个）：CREATE/DROP SCHEMA、搜索路径
- **PG17特性**（2个）：MERGE语句、增量备份

**关键测试**：

- ✅ 主键、外键、CHECK、UNIQUE约束
- ✅ 级联删除（CASCADE）
- ✅ B-tree和GIN索引创建
- ✅ 权限管理（表级、Schema级）
- ✅ 角色继承
- ✅ MERGE语句（PG17增强）

---

### 02_transactions - 事务管理（15+测试）

**状态**：设计中

**计划覆盖**：

- **隔离级别**（4个）
  - READ UNCOMMITTED
  - READ COMMITTED（默认）
  - REPEATABLE READ
  - SERIALIZABLE

- **事务控制**（3个）
  - BEGIN/COMMIT/ROLLBACK
  - SAVEPOINT/ROLLBACK TO SAVEPOINT
  - 嵌套事务

- **并发控制**（4个）
  - 脏读测试
  - 不可重复读测试
  - 幻读测试
  - 写偏斜测试

- **锁机制**（2个）
  - 行锁（FOR UPDATE/SHARE）
  - 表锁（LOCK TABLE）

- **MVCC机制**（2个）
  - 快照隔离验证
  - XID可见性测试

---

### 03_storage_access - 存储与访问（10+测试）

**状态**：设计中

**计划覆盖**：

- **EXPLAIN分析**（3个）
  - Sequential Scan
  - Index Scan
  - Index Only Scan

- **索引选择**（2个）
  - 优化器索引选择
  - 强制索引使用（pg_hint_plan）

- **VACUUM操作**（2个）
  - VACUUM回收死元组
  - VACUUM FULL重建表

- **表膨胀**（2个）
  - 检测表膨胀
  - HOT更新验证

- **统计信息**（1个）
  - ANALYZE更新统计

---

## 🔧 测试框架增强需求

### 当前测试框架（已有）

- ✅ 基本断言：`EXPECT_ROWS`、`EXPECT_VALUE`
- ✅ 错误检测：`EXPECT_ERROR`
- ✅ 时间验证：`EXPECT_TIME`
- ✅ 结果集验证：`EXPECT_RESULT`
- ✅ HTML报告生成

### 需要增强的功能

#### 1. DDL测试支持

```python
# 新增宏
EXPECT_TABLE_EXISTS(table_name) -> bool
EXPECT_INDEX_EXISTS(index_name) -> bool
EXPECT_CONSTRAINT_EXISTS(constraint_name) -> bool
EXPECT_SCHEMA_EXISTS(schema_name) -> bool
```

#### 2. DCL测试支持

```python
# 新增宏
EXPECT_PRIVILEGE(role, object, privilege) -> bool
EXPECT_ROLE_EXISTS(role_name) -> bool
SET_ROLE(role_name)  # 切换执行用户
```

#### 3. EXPLAIN验证支持

```python
# 新增宏
EXPECT_PLAN_TYPE(query, expected_plan_type) -> bool
EXPECT_INDEX_USED(query, index_name) -> bool
PARSE_EXPLAIN_JSON(query) -> dict
```

#### 4. 事务隔离测试支持

```python
# 新增功能
CONCURRENT_SESSION(session_id)  # 创建并发会话
SWITCH_SESSION(session_id)      # 切换会话
WAIT_FOR_LOCK(timeout)          # 等待锁释放
```

---

## 📊 测试覆盖目标

### 当前状态（Phase 1-5）

- **测试场景数**：91个
- **覆盖模块**：04-12模块
- **覆盖率**：高级特性100%，基础模块0%

### 目标状态（v1.0）

- **测试场景数**：136+个（91 + 45+）
- **覆盖模块**：01-12模块（全部）
- **覆盖率**：100%

### 模块测试分布

| 模块 | 当前测试数 | 新增测试数 | 目标测试数 |
|------|-----------|-----------|-----------|
| 01_sql_ddl_dcl | 0 | 20+ | 20+ |
| 02_transactions | 0 | 15+ | 15+ |
| 03_storage_access | 0 | 10+ | 10+ |
| 04_modern_features | 25 | 0 | 25 |
| 05_ai_vector | 12 | 0 | 12 |
| 06_timeseries | 8 | 0 | 8 |
| 07_extensions | 15 | 0 | 15 |
| 08_ecosystem_cases | 20 | 0 | 20 |
| 09_deployment_ops | 6 | 0 | 6 |
| 10_benchmarks | 5 | 0 | 5 |
| **总计** | **91** | **45+** | **136+** |

---

## 📅 实施时间线

### Week 4（2025-10-11 至 2025-10-17）

**任务1**：测试框架增强（4小时）

- 实现DDL测试支持
- 实现DCL测试支持
- 实现EXPLAIN验证支持

**任务2**：01模块测试实现（3小时）

- 实现20个测试用例
- 运行并验证测试

**任务3**：测试设计文档（3小时）

- 完成02_transactions测试设计
- 完成03_storage_access测试设计

### Week 5-8（2025-10-18 至 2025-11-14）

**任务4**：02模块测试实现（5小时）

- 实现15个事务测试用例
- 实现并发测试场景

**任务5**：03模块测试实现（3小时）

- 实现10个存储测试用例
- 实现EXPLAIN验证

**任务6**：测试集成与验证（2小时）

- 运行全部136+测试
- 生成测试报告
- 修复失败测试

---

## 🚀 测试运行指南

### 运行所有测试

```bash
# 运行全部测试（包括新增的45+测试）
python tests/scripts/run_all_tests.py

# 仅运行基础模块测试
python tests/scripts/run_all_tests.py --modules 01,02,03

# 仅运行01模块测试
python tests/scripts/run_all_tests.py --modules 01
```

### 查看测试报告

```bash
# 打开HTML报告
open tests/reports/test_report_YYYYMMDD_HHMMSS.html

# 查看测试统计
python tests/scripts/show_test_stats.py
```

---

## 📈 成功标准

### 定量指标

- ✅ 测试场景数：91 → 136+（+49%）
- ✅ 模块覆盖率：70% → 100%
- ✅ 测试通过率：100%（136/136）
- ✅ 测试执行时间：<5分钟（全部测试）

### 定性指标

- ✅ 所有核心功能有测试覆盖
- ✅ 边界条件测试完整
- ✅ PostgreSQL 17新特性测试
- ✅ 测试文档清晰详细

---

## 📚 相关文档

- 📋 [测试框架说明](../README.md)
- 🚀 [Week 4行动计划](../../WEEK_3_ACTION_PLAN.md)
- 🎯 [项目路线图](../../PROJECT_ROADMAP.md)
- 📊 [v1.0里程碑](../../PROJECT_ROADMAP.md#-v10测试覆盖100)

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025年10月3日  
**下次更新**：2025年10月4日（完成02/03模块设计）

---

🎯 **测试设计就绪，Week 4即可开始实施！** 🎯
