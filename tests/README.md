# PostgreSQL SQL 自动化测试框架

> **版本对标**：PostgreSQL 17（更新于 2025-10）  
> **目标**：为所有SQL示例提供自动化测试，确保代码质量和可执行性

---

## 📋 测试框架概述

### 设计目标

- ✅ 自动化执行所有SQL脚本
- ✅ 验证SQL语法正确性
- ✅ 检查执行结果
- ✅ 生成测试报告
- ✅ 持续集成（CI）支持

### 测试范围

- **基础模块**：01_sql_ddl_dcl, 02_transactions, 03_storage_access
- **实战案例**：08_ecosystem_cases（5个案例）
- **扩展功能**：pgvector, PostGIS, TimescaleDB, Citus

---

## 🏗️ 目录结构

```text
tests/
├── README.md                     # 本文件
├── config/
│   ├── database.yml              # 数据库连接配置
│   └── test_suites.yml           # 测试套件配置
├── fixtures/
│   ├── setup_test_db.sql         # 测试数据库初始化
│   ├── cleanup_test_db.sql       # 测试数据库清理
│   └── sample_data/              # 测试数据
├── sql_tests/
│   ├── 01_sql_ddl_dcl/           # 基础SQL测试
│   ├── 02_transactions/          # 事务测试
│   ├── 03_storage_access/        # 存储访问测试
│   └── 08_ecosystem_cases/       # 实战案例测试
├── integration_tests/
│   ├── test_full_workflow.py     # 完整流程测试
│   └── test_performance.py       # 性能基准测试
├── scripts/
│   ├── run_all_tests.py          # 主测试运行脚本
│   ├── run_single_test.py        # 单个测试运行脚本
│   └── generate_report.py        # 测试报告生成
└── reports/
    └── test_results.html          # 测试结果报告
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install psycopg2-binary pytest pyyaml tabulate

# 配置数据库连接
cp tests/config/database.yml.example tests/config/database.yml
# 编辑database.yml，填入你的数据库连接信息
```

### 2. 运行所有测试

```bash
# 运行所有测试
python tests/scripts/run_all_tests.py

# 运行特定模块测试
python tests/scripts/run_all_tests.py --module 01_sql_ddl_dcl

# 运行特定案例测试
python tests/scripts/run_all_tests.py --case full_text_search
```

### 3. 查看测试报告

```bash
# 生成HTML报告
python tests/scripts/generate_report.py

# 在浏览器中打开
start tests/reports/test_results.html  # Windows
open tests/reports/test_results.html   # macOS
xdg-open tests/reports/test_results.html  # Linux
```

---

## 📝 测试用例编写规范

### SQL测试文件格式

每个测试文件应包含以下部分：

```sql
-- TEST: 测试名称
-- DESCRIPTION: 测试描述
-- EXPECTED: 预期结果
-- TAGS: tag1, tag2

-- SETUP
CREATE TABLE test_table (id int, name text);

-- TEST_BODY
INSERT INTO test_table VALUES (1, 'test');
SELECT COUNT(*) FROM test_table;  -- EXPECT: 1

-- TEARDOWN
DROP TABLE test_table;
```

### 测试断言

支持以下断言类型：

```sql
-- 1. 行数断言
SELECT * FROM users;  -- EXPECT_ROWS: 10

-- 2. 值断言
SELECT COUNT(*) FROM orders;  -- EXPECT_VALUE: 100

-- 3. 错误断言
INSERT INTO readonly_table VALUES (1);  -- EXPECT_ERROR

-- 4. 性能断言
SELECT * FROM large_table;  -- EXPECT_TIME: < 100ms

-- 5. 结果集断言
SELECT id, name FROM users ORDER BY id LIMIT 1;
-- EXPECT_RESULT:
-- | id | name  |
-- |  1 | Alice |
```

---

## 🧪 测试套件

### 基础测试套件

#### 1. SQL DDL/DCL测试

- 创建/修改/删除表
- 约束测试（主键、外键、检查约束）
- 索引创建与使用
- 权限管理

#### 2. 事务测试

- ACID特性验证
- 隔离级别测试
- 锁机制测试
- 死锁检测

#### 3. 存储访问测试

- 索引类型测试
- 执行计划验证
- VACUUM/ANALYZE测试

### 实战案例测试

#### 1. 全文搜索测试

- tsvector/tsquery功能
- GIN索引性能
- 搜索结果相关性

#### 2. CDC测试

- 触发器CDC功能
- 逻辑复制CDC
- 变更数据完整性

#### 3. 地理围栏测试

- PostGIS扩展功能
- 空间查询正确性
- GiST索引性能

#### 4. 联邦查询测试

- postgres_fdw连接
- 跨库查询正确性
- 数据一致性

#### 5. 实时分析测试

- 高频写入性能
- 物化视图刷新
- 聚合查询正确性

---

## 🔧 测试工具

### 主测试脚本（run_all_tests.py）

**功能**：

- 自动发现测试文件
- 并行执行测试
- 收集测试结果
- 生成测试报告

**使用示例**：

```bash
# 运行所有测试
python tests/scripts/run_all_tests.py

# 运行特定标签的测试
python tests/scripts/run_all_tests.py --tags smoke

# 并行运行（4个进程）
python tests/scripts/run_all_tests.py --parallel 4

# 详细输出
python tests/scripts/run_all_tests.py --verbose

# 失败时停止
python tests/scripts/run_all_tests.py --fail-fast
```

### 单个测试脚本（run_single_test.py）

**功能**：

- 运行单个SQL测试文件
- 详细的错误信息
- 调试模式

**使用示例**：

```bash
# 运行单个测试
python tests/scripts/run_single_test.py tests/sql_tests/01_sql_ddl_dcl/test_create_table.sql

# 调试模式（打印所有SQL）
python tests/scripts/run_single_test.py --debug test_file.sql
```

---

## 📊 测试报告

### HTML报告

包含以下内容：

- 测试总览（通过/失败/跳过数量）
- 测试执行时间
- 失败测试详情
- 性能基准对比
- 覆盖率统计

### 命令行输出

```text
=== PostgreSQL SQL Test Suite ===

Running tests: ████████████████████ 100% (50/50)

Results:
  ✓ Passed:  45
  ✗ Failed:   3
  ⊘ Skipped:  2
  
Total time: 12.34s

Failed tests:
  1. tests/sql_tests/02_transactions/test_deadlock.sql
     Error: deadlock detected
  2. tests/sql_tests/08_ecosystem_cases/test_cdc.sql
     Error: extension "postgres_fdw" not available
  3. tests/sql_tests/03_storage_access/test_vacuum.sql
     Error: permission denied
```

---

## 🔄 持续集成（CI）

### GitHub Actions工作流

文件：`.github/workflows/sql-tests.yml`

```yaml
name: SQL Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install psycopg2-binary pytest pyyaml tabulate
    
    - name: Run SQL tests
      run: |
        python tests/scripts/run_all_tests.py --ci
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: tests/reports/
```

---

## 🎯 最佳实践

### 1. 测试隔离

- ✅ 每个测试使用独立的schema
- ✅ 测试后清理所有数据
- ✅ 避免测试之间的依赖

### 2. 测试数据

- ✅ 使用fixtures准备测试数据
- ✅ 数据量适中（避免过大）
- ✅ 数据多样性（覆盖边界情况）

### 3. 性能测试

- ✅ 设置合理的性能基准
- ✅ 关注性能回归
- ✅ 记录性能趋势

### 4. 错误处理

- ✅ 测试预期的错误情况
- ✅ 验证错误消息
- ✅ 测试边界条件

### 5. 文档同步

- ✅ 测试与文档保持一致
- ✅ 及时更新测试用例
- ✅ 记录测试覆盖率

---

## 📚 扩展阅读

- **pgTAP**：PostgreSQL单元测试框架 - <https://pgtap.org/>
- **pg_prove**：TAP测试运行器 - <https://pgtap.org/documentation.html>
- **pytest-postgresql**：Python PostgreSQL测试插件 - <https://github.com/ClearcodeHQ/pytest-postgresql>
- **GitHub Actions**：CI/CD配置 - <https://docs.github.com/en/actions>

---

## 🤝 贡献指南

### 添加新测试

1. 在对应目录创建测试文件
2. 按照规范编写测试用例
3. 本地验证测试通过
4. 提交PR并等待CI验证

### 报告测试问题

如果发现测试失败或不准确：

1. 在GitHub创建Issue
2. 包含测试文件路径
3. 附上错误信息和日志
4. 说明预期行为

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025-10-03  
**测试框架版本**：1.0.0
