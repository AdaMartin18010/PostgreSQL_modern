# MVCC-ACID验证工具

> **文档编号**: TOOLS-MVCC-ACID-001
> **主题**: MVCC-ACID验证工具集合
> **版本**: v1.0
> **状态**: ✅ 已完成

---

## 📑 目录

- [MVCC-ACID验证工具](#mvcc-acid验证工具)
  - [📑 目录](#-目录)
  - [📋 概述](#-概述)
  - [🔧 工具列表](#-工具列表)
    - [1. 原子性测试工具](#1-原子性测试工具)
    - [2. 一致性测试工具](#2-一致性测试工具)
  - [📖 使用说明](#-使用说明)
  - [📝 总结](#-总结)

---

## 📋 概述

本目录包含PostgreSQL MVCC-ACID验证工具，用于测试和验证MVCC和ACID特性。

**工具目标**：

- **验证MVCC特性**：测试MVCC的版本控制、快照隔离等特性
- **验证ACID特性**：测试ACID的原子性、一致性、隔离性、持久性
- **自动化测试**：提供自动化测试工具，方便持续集成

**工具列表**：

1. `atomicity_test.py` - 原子性测试工具
2. `consistency_test.py` - 一致性测试工具
3. `isolation_test.py` - 隔离性测试工具
4. `durability_test.py` - 持久性测试工具
5. `mapping_test.py` - MVCC-ACID集成测试工具

---

## 🔧 工具列表

### 1. 原子性测试工具

**文件**：`atomicity_test.py`

**功能**：

- 测试完整回滚
- 测试部分回滚（保存点）
- 测试约束违反回滚
- 测试模拟崩溃恢复

**使用方法**：

```bash
# 设置测试表
python atomicity_test.py --connection "dbname=testdb user=postgres" --setup

# 运行所有测试
python atomicity_test.py --connection "dbname=testdb user=postgres" --test all

# 运行特定测试
python atomicity_test.py --connection "dbname=testdb user=postgres" --test rollback
```

**测试项**：

1. **完整回滚测试**：测试事务完全回滚
2. **部分回滚测试**：测试保存点回滚
3. **约束违反回滚测试**：测试约束违反时的回滚
4. **崩溃恢复测试**：测试模拟崩溃后的恢复

### 2. 一致性测试工具

**文件**：`consistency_test.py`

**功能**：

- 测试检查约束
- 测试唯一约束
- 测试外键约束
- 测试触发器一致性
- 测试数据完整性
- 测试事务一致性

**使用方法**：

```bash
# 设置测试表
python consistency_test.py --connection "dbname=testdb user=postgres" --setup

# 运行所有测试
python consistency_test.py --connection "dbname=testdb user=postgres" --test all

# 运行特定测试
python consistency_test.py --connection "dbname=testdb user=postgres" --test check
```

**测试项**：

1. **检查约束测试**：测试CHECK约束是否生效
2. **唯一约束测试**：测试UNIQUE约束是否生效
3. **外键约束测试**：测试外键约束是否生效
4. **触发器一致性测试**：测试触发器是否正确执行
5. **数据完整性测试**：测试数据完整性是否保证
6. **事务一致性测试**：测试事务一致性是否保证

### 3. 隔离性测试工具

**文件**：`isolation_test.py`

**功能**：

- 测试隔离级别（READ COMMITTED、REPEATABLE READ、SERIALIZABLE）
- 测试并发更新冲突
- 测试写偏序异常
- 测试幻读异常

**使用方法**：

```bash
# 设置测试表
python isolation_test.py --connection "dbname=testdb user=postgres" --setup

# 运行所有测试
python isolation_test.py --connection "dbname=testdb user=postgres" --test all

# 运行特定测试
python isolation_test.py --connection "dbname=testdb user=postgres" --test read_committed
```

**测试项**：

1. **READ COMMITTED测试**：测试READ COMMITTED隔离级别的行为
2. **REPEATABLE READ测试**：测试REPEATABLE READ隔离级别的行为
3. **SERIALIZABLE测试**：测试SERIALIZABLE隔离级别的行为
4. **并发更新测试**：测试并发更新冲突处理
5. **写偏序测试**：测试写偏序异常
6. **幻读测试**：测试幻读异常

---

## 📖 使用说明

### 环境要求

**Python版本**：Python 3.7+

**依赖包**：

```bash
pip install psycopg2-binary
```

### 连接字符串格式

**标准格式**：

```
dbname=数据库名 user=用户名 password=密码 host=主机 port=端口
```

**示例**：

```bash
# 本地连接
dbname=testdb user=postgres password=postgres host=localhost

# 远程连接
dbname=testdb user=postgres password=postgres host=192.168.1.100 port=5432
```

### 运行示例

**原子性测试**：

```bash
# 1. 设置测试环境
python atomicity_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --setup

# 2. 运行所有测试
python atomicity_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test all

# 3. 运行特定测试
python atomicity_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test rollback
```

**一致性测试**：

```bash
# 1. 设置测试环境
python consistency_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --setup

# 2. 运行所有测试
python consistency_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test all

# 3. 运行特定测试
python consistency_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test check
```

**隔离性测试**：

```bash
# 1. 设置测试环境
python isolation_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --setup

# 2. 运行所有测试
python isolation_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test all

# 3. 运行特定测试
python isolation_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test read_committed
```

**持久性测试**：

```bash
# 1. 设置测试环境
python durability_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --setup

# 2. 运行所有测试
python durability_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test all

# 3. 运行特定测试
python durability_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test wal_write
```

**MVCC-ACID集成测试**：

```bash
# 1. 设置测试环境
python mapping_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --setup

# 2. 运行所有测试
python mapping_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test all

# 3. 运行特定测试
python mapping_test.py \
    --connection "dbname=testdb user=postgres password=postgres host=localhost" \
    --test mvcc_to_acid
```

### 测试结果

**输出格式**：

```
============================================================
一致性测试结果
============================================================

✅ 通过 - 检查约束测试
  消息: 测试通过

✅ 通过 - 唯一约束测试
  消息: 测试通过

❌ 失败 - 外键约束测试
  错误: 测试失败

============================================================
```

**退出码**：

- `0`：所有测试通过
- `1`：至少一个测试失败

---

## 📝 总结

### 工具特点

1. **完整性**：覆盖原子性、一致性和隔离性的主要测试场景
2. **易用性**：提供命令行接口，易于使用
3. **可扩展性**：代码结构清晰，易于扩展新测试
4. **可靠性**：包含错误处理和日志记录

### 4. 持久性测试工具

**文件**：`durability_test.py`

**功能**：

- 测试WAL写入
- 测试同步提交
- 测试数据持久性
- 测试事务持久性
- 测试WAL重放
- 测试检查点

**使用方法**：

```bash
# 设置测试表
python durability_test.py --connection "dbname=testdb user=postgres" --setup

# 运行所有测试
python durability_test.py --connection "dbname=testdb user=postgres" --test all

# 运行特定测试
python durability_test.py --connection "dbname=testdb user=postgres" --test wal_write
```

**测试项**：

1. **WAL写入测试**：测试WAL写入功能
2. **同步提交测试**：测试同步提交功能
3. **数据持久性测试**：测试数据持久性
4. **事务持久性测试**：测试事务持久性
5. **WAL重放测试**：测试WAL重放功能
6. **检查点测试**：测试检查点功能

---

## 📝 总结

### 工具特点

1. **完整性**：覆盖原子性、一致性、隔离性和持久性的主要测试场景
2. **易用性**：提供命令行接口，易于使用
3. **可扩展性**：代码结构清晰，易于扩展新测试
4. **可靠性**：包含错误处理和日志记录

### 5. MVCC-ACID集成测试工具

**文件**：`mapping_test.py`

**功能**：

- 测试MVCC到ACID的映射关系
- 测试ACID到MVCC的映射关系
- 测试MVCC-ACID等价性
- 测试MVCC-ACID状态机

**使用方法**：

```bash
# 设置测试表
python mapping_test.py --connection "dbname=testdb user=postgres" --setup

# 运行所有测试
python mapping_test.py --connection "dbname=testdb user=postgres" --test all

# 运行特定测试
python mapping_test.py --connection "dbname=testdb user=postgres" --test mvcc_to_acid
```

**测试项**：

1. **MVCC到ACID映射关系测试**：测试版本->原子性、快照->隔离性、可见性->一致性
2. **ACID到MVCC映射关系测试**：测试原子性->版本、隔离性->快照、持久性->WAL
3. **MVCC-ACID等价性测试**：测试MVCC操作和ACID操作的等价性
4. **MVCC-ACID状态机测试**：测试状态转换（pending->active->committed）

---

## 📝 总结

### 工具特点

1. **完整性**：覆盖原子性、一致性、隔离性、持久性和集成测试的主要测试场景
2. **易用性**：提供命令行接口，易于使用
3. **可扩展性**：代码结构清晰，易于扩展新测试
4. **可靠性**：包含错误处理和日志记录

### 后续扩展

1. **性能测试工具**：开发性能测试工具
2. **集成测试扩展**：扩展集成测试场景

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
