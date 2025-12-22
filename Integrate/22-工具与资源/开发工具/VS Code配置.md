# VS Code配置指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐ 初级

---

## 📋 目录

- [VS Code配置指南](#vs-code配置指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. 扩展安装](#2-扩展安装)
    - [2.1 推荐扩展](#21-推荐扩展)
    - [2.2 扩展配置](#22-扩展配置)
  - [3. 连接配置](#3-连接配置)
    - [3.1 SQL Tools配置](#31-sql-tools配置)
    - [3.2 连接测试](#32-连接测试)
  - [4. 查询执行](#4-查询执行)
    - [4.1 执行查询](#41-执行查询)
    - [4.2 查看结果](#42-查看结果)
  - [5. 代码格式化](#5-代码格式化)
    - [5.1 格式化配置](#51-格式化配置)
    - [5.2 格式化快捷键](#52-格式化快捷键)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

VS Code是轻量级、功能强大的代码编辑器，通过扩展可以很好地支持PostgreSQL开发。

**优势**:

- 轻量级
- 丰富的扩展生态
- 免费开源
- 跨平台

---

## 2. 扩展安装

### 2.1 推荐扩展

```bash
# PostgreSQL扩展
code --install-extension ms-ossdata.vscode-postgresql

# SQL Tools扩展
code --install-extension mtxr.sqltools
code --install-extension mtxr.sqltools-driver-pg

# SQL格式化
code --install-extension adpyke.vscode-sql-formatter
```

### 2.2 扩展配置

```json
{
  "postgresql.connections": [
    {
      "host": "localhost",
      "port": 5432,
      "database": "mydb",
      "user": "postgres"
    }
  ]
}
```

---

## 3. 连接配置

### 3.1 SQL Tools配置

```json
{
  "sqltools.connections": [
    {
      "name": "PostgreSQL Local",
      "driver": "PostgreSQL",
      "server": "localhost",
      "port": 5432,
      "database": "mydb",
      "username": "postgres",
      "password": "${env:PGPASSWORD}"
    }
  ]
}
```

### 3.2 连接测试

```text
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "SQLTools: Connect"
3. 选择连接
4. 查看连接状态
```

---

## 4. 查询执行

### 4.1 执行查询

```sql
-- 在SQL文件中
-- 选中SQL语句
-- 按 Ctrl+E 执行
SELECT * FROM users;
```

### 4.2 查看结果

```text
1. 执行查询后
2. 结果在侧边栏显示
3. 可以导出为CSV/JSON
4. 可以保存查询历史
```

---

## 5. 代码格式化

### 5.1 格式化配置

```json
{
  "sql-formatter.uppercase": true,
  "sql-formatter.linesBetweenQueries": 2,
  "sql-formatter.keywordCase": "upper"
}
```

### 5.2 格式化快捷键

```text
格式化SQL: Shift+Alt+F
格式化选中: Ctrl+K Ctrl+F
```

---

## 📚 相关文档

- [IDE配置指南.md](./IDE配置指南.md) - IDE配置完整指南
- [IntelliJ配置.md](./IntelliJ配置.md) - IntelliJ配置
- [开发工具链.md](./开发工具链.md) - 开发工具链
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
