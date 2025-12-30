# IDE配置指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐ 初级

---

## 📋 目录

- [IDE配置指南](#ide配置指南)
  - [📋 目录](#-目录)
  - [1. 概述](#1-概述)
  - [2. VS Code配置](#2-vs-code配置)
    - [2.1 安装扩展](#21-安装扩展)
    - [2.2 连接配置](#22-连接配置)
  - [3. IntelliJ IDEA配置](#3-intellij-idea配置)
    - [3.1 数据库连接](#31-数据库连接)
    - [3.2 SQL格式化](#32-sql格式化)
  - [4. DataGrip配置](#4-datagrip配置)
    - [4.1 连接配置](#41-连接配置)
    - [4.2 查询配置](#42-查询配置)
  - [5. DBeaver配置](#5-dbeaver配置)
    - [5.1 连接配置](#51-连接配置)
    - [5.2 编辑器配置](#52-编辑器配置)
  - [6. 通用配置](#6-通用配置)
    - [6.1 连接参数](#61-连接参数)
    - [6.2 性能优化](#62-性能优化)
    - [6.3 安全配置](#63-安全配置)
    - [6.4 调试配置](#64-调试配置)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 IDE选择建议](#71-ide选择建议)
    - [7.2 配置优化建议](#72-配置优化建议)
    - [7.3 故障排查](#73-故障排查)
  - [📚 相关文档](#-相关文档)

---

## 1. 概述

IDE配置是PostgreSQL开发的基础。选择合适的IDE和正确配置可以显著提高开发效率。

**支持的IDE**:

- VS Code
- IntelliJ IDEA
- DataGrip
- DBeaver

---

## 2. VS Code配置

### 2.1 安装扩展

```json
{
  "recommendations": [
    "ms-ossdata.vscode-postgresql",
    "ckolkman.vscode-postgres",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
```

### 2.2 连接配置

```json
{
  "sqltools.connections": [
    {
      "name": "PostgreSQL",
      "driver": "PostgreSQL",
      "server": "localhost",
      "port": 5432,
      "database": "mydb",
      "username": "postgres",
      "password": "password"
    }
  ]
}
```

---

## 3. IntelliJ IDEA配置

### 3.1 数据库连接

```text
1. Database → Data Source → PostgreSQL
2. 配置连接信息
3. 测试连接
4. 应用配置
```

### 3.2 SQL格式化

```text
Settings → Editor → Code Style → SQL
- 设置缩进
- 设置关键字大小写
- 设置格式化规则
```

---

## 4. DataGrip配置

### 4.1 连接配置

```text
1. 创建数据源
2. 选择PostgreSQL
3. 配置连接参数
4. 测试连接
```

### 4.2 查询配置

```text
Settings → Database → Query Execution
- 设置查询超时
- 设置结果集大小
- 设置自动提交
```

---

## 5. DBeaver配置

### 5.1 连接配置

```text
1. 新建连接
2. 选择PostgreSQL
3. 配置连接信息
4. 测试连接
```

### 5.2 编辑器配置

```text
Window → Preferences → Editors → SQL Editor
- 设置SQL格式化
- 设置自动完成
- 设置语法高亮
```

---

## 6. 通用配置

### 6.1 连接参数

**标准连接参数**：

```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "postgres",
  "password": "password",
  "ssl": false,
  "connectTimeout": 10,
  "applicationName": "IDE-Client"
}
```

**高级连接参数**：

```json
{
  "options": "-c statement_timeout=30000",
  "tcpKeepAlive": true,
  "keepAliveIdle": 600,
  "keepAliveInterval": 30,
  "keepAliveCount": 3
}
```

### 6.2 性能优化

**连接池配置**：

```json
{
  "maxConnections": 10,
  "minConnections": 2,
  "idleTimeout": 30000,
  "connectionTimeout": 10000
}
```

**查询优化配置**：

```json
{
  "queryTimeout": 30000,
  "resultSetSize": 1000,
  "fetchSize": 100,
  "autoCommit": true
}
```

### 6.3 安全配置

**SSL连接配置**：

```json
{
  "ssl": true,
  "sslmode": "require",
  "sslrootcert": "/path/to/ca-cert.pem",
  "sslcert": "/path/to/client-cert.pem",
  "sslkey": "/path/to/client-key.pem"
}
```

**SSH隧道配置**：

```json
{
  "ssh": {
    "host": "ssh.example.com",
    "port": 22,
    "username": "sshuser",
    "privateKey": "/path/to/private_key",
    "localPort": 5432,
    "remoteHost": "localhost",
    "remotePort": 5432
  }
}
```

### 6.4 调试配置

**查询日志配置**：

```json
{
  "logQueries": true,
  "logParameters": false,
  "logExecutionTime": true,
  "logSlowQueries": true,
  "slowQueryThreshold": 1000
}
```

**性能监控配置**：

```json
{
  "enablePerformanceMonitoring": true,
  "monitorInterval": 5000,
  "alertOnSlowQueries": true,
  "slowQueryThreshold": 1000
}
```

## 7. 最佳实践

### 7.1 IDE选择建议

**VS Code**：

- ✅ 轻量级，启动快
- ✅ 丰富的扩展生态
- ✅ 适合日常开发和调试
- ❌ 大型项目性能较差

**IntelliJ IDEA / DataGrip**：

- ✅ 强大的数据库工具
- ✅ 优秀的代码补全
- ✅ 适合大型项目
- ❌ 资源占用较大

**DBeaver**：

- ✅ 免费开源
- ✅ 跨平台支持
- ✅ 支持多种数据库
- ❌ 界面相对简单

### 7.2 配置优化建议

**1. 连接管理**：

```json
{
  "connections": [
    {
      "name": "开发环境",
      "host": "dev.example.com",
      "database": "dev_db"
    },
    {
      "name": "测试环境",
      "host": "test.example.com",
      "database": "test_db"
    },
    {
      "name": "生产环境（只读）",
      "host": "prod.example.com",
      "database": "prod_db",
      "readOnly": true
    }
  ]
}
```

**2. 查询模板配置**：

```sql
-- 常用查询模板
-- 1. 表结构查询
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'users'
ORDER BY ordinal_position;

-- 2. 索引查询
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'users';

-- 3. 表大小查询
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**3. 代码格式化配置**：

```json
{
  "sql.format": {
    "keywordCase": "upper",
    "indentSize": 2,
    "maxLineLength": 100,
    "alignColumns": true,
    "spacesAroundOperators": true
  }
}
```

### 7.3 故障排查

**常见问题及解决方案**：

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

3. **查询性能问题**

   ```json
   {
     "queryTimeout": 60000,
     "resultSetSize": 500,
     "fetchSize": 50
   }
   ```

---

## 📚 相关文档

- [VS Code配置.md](./VS Code配置.md) - VS Code详细配置
- [IntelliJ配置.md](./IntelliJ配置.md) - IntelliJ详细配置
- [开发工具链.md](./开发工具链.md) - 开发工具链整合
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
