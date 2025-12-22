# IntelliJ IDEA配置指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐ 初级

---

## 📋 目录

- [IntelliJ IDEA配置指南](#intellij-idea配置指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 数据库连接](#2-数据库连接)
    - [2.1 创建连接](#21-创建连接)
    - [2.2 连接配置](#22-连接配置)
  - [3. SQL编辑器](#3-sql编辑器)
    - [3.1 编辑器功能](#31-编辑器功能)
    - [3.2 查询执行](#32-查询执行)
  - [4. 代码生成](#4-代码生成)
    - [4.1 生成实体类](#41-生成实体类)
    - [4.2 生成查询](#42-生成查询)
  - [5. 调试配置](#5-调试配置)
    - [5.1 调试PL/pgSQL](#51-调试plpgsql)
    - [5.2 调试配置](#52-调试配置)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

IntelliJ IDEA是功能强大的IDE，内置数据库工具，可以很好地支持PostgreSQL开发。

**优势**:

- 内置数据库工具
- 强大的代码补全
- 智能重构
- 集成调试

---

## 2. 数据库连接

### 2.1 创建连接

```
1. View → Tool Windows → Database
2. 点击 + → Data Source → PostgreSQL
3. 配置连接信息
4. 测试连接
```

### 2.2 连接配置

```text
Host: localhost
Port: 5432
Database: mydb
User: postgres
Password: [密码]
SSL: prefer
```

---

## 3. SQL编辑器

### 3.1 编辑器功能

```text
1. 语法高亮
2. 代码补全
3. 错误检查
4. 格式化
5. 执行计划
```

### 3.2 查询执行

```sql
-- 选中SQL语句
-- 按 Ctrl+Enter 执行
SELECT * FROM users;
```

---

## 4. 代码生成

### 4.1 生成实体类

```
1. 右键表名
2. Scripted Extensions → Generate POJOs
3. 选择生成选项
4. 生成代码
```

### 4.2 生成查询

```
1. 右键表名
2. Generate → Query
3. 选择查询类型
4. 生成SQL
```

---

## 5. 调试配置

### 5.1 调试PL/pgSQL

```
1. 设置断点
2. 右键函数 → Debug
3. 查看变量值
4. 单步执行
```

### 5.2 调试配置

```text
Run → Edit Configurations
- 添加PostgreSQL配置
- 设置调试参数
- 保存配置
```

---

## 📚 相关文档

- [IDE配置指南.md](./IDE配置指南.md) - IDE配置完整指南
- [VS Code配置.md](./VS Code配置.md) - VS Code配置
- [开发工具链.md](./开发工具链.md) - 开发工具链
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
