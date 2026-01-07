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
  - [6. 高级功能](#6-高级功能)
    - [6.1 数据库图表](#61-数据库图表)
    - [6.2 数据导出导入](#62-数据导出导入)
    - [6.3 SQL模板](#63-sql模板)
  - [7. 最佳实践](#7-最佳实践)
    - [7.1 连接管理](#71-连接管理)
    - [7.2 查询优化](#72-查询优化)
    - [7.3 代码补全配置](#73-代码补全配置)
  - [8. 故障排查](#8-故障排查)
    - [8.1 连接问题](#81-连接问题)
    - [8.2 性能问题](#82-性能问题)
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

```text
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

```text
1. 右键表名
2. Scripted Extensions → Generate POJOs
3. 选择生成选项
4. 生成代码
```

### 4.2 生成查询

```text
1. 右键表名
2. Generate → Query
3. 选择查询类型
4. 生成SQL
```

---

## 5. 调试配置

### 5.1 调试PL/pgSQL

**调试步骤**：

```text
1. 设置断点
2. 右键函数 → Debug
3. 查看变量值
4. 单步执行
```

**调试配置示例**：

```sql
-- 创建测试函数
CREATE OR REPLACE FUNCTION test_function(param1 INTEGER)
RETURNS INTEGER AS $$
DECLARE
    result INTEGER;
BEGIN
    result := param1 * 2;  -- 设置断点
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 在IntelliJ中调试
-- 1. 在函数中设置断点
-- 2. 右键函数 → Debug 'test_function'
-- 3. 输入参数值
-- 4. 查看变量和执行流程
```

### 5.2 调试配置

**配置步骤**：

```text
Run → Edit Configurations
- 添加PostgreSQL配置
- 设置调试参数
- 保存配置
```

**调试参数配置**：

```json
{
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "postgres",
  "debugMode": true,
  "breakpoints": {
    "enabled": true,
    "stopOnException": true
  }
}
```

## 6. 高级功能

### 6.1 数据库图表

**生成ER图**：

```text
1. 右键数据库 → Diagrams → Show Visualization
2. 选择表
3. 生成ER图
4. 导出为图片
```

**图表配置**：

```json
{
  "diagram": {
    "showForeignKeys": true,
    "showIndexes": false,
    "layout": "hierarchical",
    "theme": "light"
  }
}
```

### 6.2 数据导出导入

**导出数据**：

```text
1. 右键表 → Export Data
2. 选择格式（CSV、JSON、SQL）
3. 配置导出选项
4. 导出数据
```

**导入数据**：

```text
1. 右键表 → Import Data
2. 选择文件
3. 配置导入选项
4. 导入数据
```

### 6.3 SQL模板

**创建模板**：

```text
1. Settings → Editor → Live Templates
2. 添加SQL模板
3. 配置变量
4. 保存模板
```

**常用模板示例**：

```sql
-- 模板：查询表结构
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = '$SCHEMA$'
  AND table_name = '$TABLE$'
ORDER BY ordinal_position;

-- 模板：查询表大小
SELECT
    pg_size_pretty(pg_total_relation_size('$SCHEMA$.$TABLE$')) AS size;
```

## 7. 最佳实践

### 7.1 连接管理

**多环境配置**：

```json
{
  "connections": [
    {
      "name": "开发环境",
      "host": "dev.example.com",
      "database": "dev_db",
      "color": "green"
    },
    {
      "name": "测试环境",
      "host": "test.example.com",
      "database": "test_db",
      "color": "yellow"
    },
    {
      "name": "生产环境（只读）",
      "host": "prod.example.com",
      "database": "prod_db",
      "readOnly": true,
      "color": "red"
    }
  ]
}
```

### 7.2 查询优化

**查询分析工具**：

```sql
-- 使用EXPLAIN (ANALYZE, BUFFERS, TIMING)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM users WHERE id = 1;

-- 在IntelliJ中查看执行计划
-- 1. 执行查询
-- 2. 点击"Explain Plan"按钮
-- 3. 查看执行计划树
-- 4. 分析性能瓶颈
```

### 7.3 代码补全配置

**SQL补全设置**：

```json
{
  "codeCompletion": {
    "enabled": true,
    "caseSensitive": false,
    "showKeywords": true,
    "showTables": true,
    "showColumns": true,
    "showFunctions": true
  }
}
```

## 8. 故障排查

### 8.1 连接问题

**常见问题**：

1. **连接超时**
   - 检查网络连接
   - 增加连接超时时间
   - 检查防火墙设置

2. **SSL连接失败**
   - 检查SSL证书配置
   - 尝试使用`prefer`模式
   - 检查证书路径

3. **认证失败**
   - 检查用户名和密码
   - 检查pg_hba.conf配置
   - 检查用户权限

### 8.2 性能问题

**优化建议**：

1. **减少结果集大小**

   ```sql
   -- 使用LIMIT限制结果
   SELECT * FROM users LIMIT 100;
   ```

2. **使用索引**

   ```sql
   -- 确保查询使用索引
   EXPLAIN SELECT * FROM users WHERE id = 1;
   ```

3. **优化查询**

   ```sql
   -- 避免SELECT *
   SELECT id, name FROM users;
   ```

---

## 📚 相关文档

- [IDE配置指南.md](./IDE配置指南.md) - IDE配置完整指南
- [VS Code配置.md](./VS Code配置.md) - VS Code配置
- [开发工具链.md](./开发工具链.md) - 开发工具链
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
