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
  - [6. 高级功能](#6-高级功能)
    - [6.1 查询历史](#61-查询历史)
    - [6.2 查询结果导出](#62-查询结果导出)
    - [6.3 代码片段](#63-代码片段)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 工作区配置](#71-工作区配置)
    - [7.2 查询模板](#72-查询模板)
    - [7.3 扩展推荐](#73-扩展推荐)
  - [8. 故障排查](#8-故障排查)
    - [8.1 连接问题](#81-连接问题)
    - [8.2 扩展问题](#82-扩展问题)
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
  "sql-formatter.keywordCase": "upper",
  "sql-formatter.indentSize": 2,
  "sql-formatter.maxLineLength": 100
}
```

### 5.2 格式化快捷键

```text
格式化SQL: Shift+Alt+F
格式化选中: Ctrl+K Ctrl+F
```

## 6. 高级功能

### 6.1 查询历史

**查看历史**：

```text
1. 打开命令面板 (Ctrl+Shift+P)
2. 输入 "SQLTools: Show Query History"
3. 查看历史查询
4. 重新执行查询
```

**历史配置**：

```json
{
  "sqltools.queryHistory": {
    "enabled": true,
    "maxHistory": 100,
    "saveToFile": true,
    "filePath": ".sqltools/history.json"
  }
}
```

### 6.2 查询结果导出

**导出格式**：

```text
1. 执行查询
2. 右键结果 → Export
3. 选择格式（CSV、JSON、Excel）
4. 保存文件
```

**导出配置**：

```json
{
  "sqltools.results": {
    "exportFormats": ["csv", "json", "excel"],
    "defaultFormat": "csv",
    "includeHeaders": true
  }
}
```

### 6.3 代码片段

**创建片段**：

```json
{
  "PostgreSQL": {
    "prefix": "pg-select",
    "body": [
      "SELECT ${1:*}",
      "FROM ${2:table}",
      "WHERE ${3:condition};"
    ],
    "description": "PostgreSQL SELECT查询"
  }
}
```

**常用片段**：

```json
{
  "pg-create-table": {
    "prefix": "pg-create-table",
    "body": [
      "CREATE TABLE ${1:table_name} (",
      "  id SERIAL PRIMARY KEY,",
      "  ${2:columns}",
      ");"
    ]
  },
  "pg-insert": {
    "prefix": "pg-insert",
    "body": [
      "INSERT INTO ${1:table} (${2:columns})",
      "VALUES (${3:values});"
    ]
  }
}
```

## 7. 最佳实践

### 7.1 工作区配置

**项目配置**：

```json
{
  "sqltools.connections": [
    {
      "name": "项目数据库",
      "driver": "PostgreSQL",
      "server": "${env:DB_HOST}",
      "port": 5432,
      "database": "${env:DB_NAME}",
      "username": "${env:DB_USER}",
      "password": "${env:DB_PASSWORD}"
    }
  ]
}
```

### 7.2 查询模板

**常用查询模板**：

```sql
-- 表结构查询
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = '$TABLE_NAME$'
ORDER BY ordinal_position;

-- 表大小查询
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 7.3 扩展推荐

**推荐扩展列表**：

```json
{
  "recommendations": [
    "ms-ossdata.vscode-postgresql",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg",
    "adpyke.vscode-sql-formatter",
    "ckolkman.vscode-postgres",
    "ms-python.python"
  ]
}
```

## 8. 故障排查

### 8.1 连接问题

**常见问题**：

1. **连接超时**

   ```json
   {
     "connectTimeout": 30000,
     "tcpKeepAlive": true
   }
   ```

2. **SSL连接失败**

   ```json
   {
     "sslmode": "prefer",
     "sslrootcert": "/path/to/ca-cert.pem"
   }
   ```

3. **认证失败**
   - 检查用户名和密码
   - 检查pg_hba.conf配置
   - 检查用户权限

### 8.2 扩展问题

**扩展不工作**：

1. 重新加载窗口：`Ctrl+Shift+P` → `Reload Window`
2. 检查扩展是否启用
3. 查看扩展日志：`Output` → 选择扩展
4. 重新安装扩展

---

## 📚 相关文档

- [IDE配置指南.md](./IDE配置指南.md) - IDE配置完整指南
- [IntelliJ配置.md](./IntelliJ配置.md) - IntelliJ配置
- [开发工具链.md](./开发工具链.md) - 开发工具链
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
