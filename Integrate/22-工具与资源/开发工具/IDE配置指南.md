# IDE配置指南

> **创建日期**: 2025年1月
> **技术版本**: PostgreSQL 17+/18+
> **难度等级**: ⭐⭐ 初级

---

## 📋 目录

- [IDE配置指南](#ide配置指南)
  - [1. 概述](#1-概述)
  - [2. VS Code配置](#2-vs-code配置)
  - [3. IntelliJ IDEA配置](#3-intellij-idea配置)
  - [4. DataGrip配置](#4-datagrip配置)
  - [5. DBeaver配置](#5-dbeaver配置)
  - [6. 通用配置](#6-通用配置)

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

```
1. Database → Data Source → PostgreSQL
2. 配置连接信息
3. 测试连接
4. 应用配置
```

### 3.2 SQL格式化

```
Settings → Editor → Code Style → SQL
- 设置缩进
- 设置关键字大小写
- 设置格式化规则
```

---

## 4. DataGrip配置

### 4.1 连接配置

```
1. 创建数据源
2. 选择PostgreSQL
3. 配置连接参数
4. 测试连接
```

### 4.2 查询配置

```
Settings → Database → Query Execution
- 设置查询超时
- 设置结果集大小
- 设置自动提交
```

---

## 5. DBeaver配置

### 5.1 连接配置

```
1. 新建连接
2. 选择PostgreSQL
3. 配置连接信息
4. 测试连接
```

### 5.2 编辑器配置

```
Window → Preferences → Editors → SQL Editor
- 设置SQL格式化
- 设置自动完成
- 设置语法高亮
```

---

## 6. 通用配置

### 6.1 连接参数

```text
主机: localhost
端口: 5432
数据库: mydb
用户名: postgres
密码: [密码]
SSL模式: prefer
```

### 6.2 性能优化

```text
1. 启用连接池
2. 设置查询超时
3. 限制结果集大小
4. 使用只读连接
```

---

## 📚 相关文档

- [VS Code配置.md](./VS Code配置.md) - VS Code详细配置
- [IntelliJ配置.md](./IntelliJ配置.md) - IntelliJ详细配置
- [开发工具链.md](./开发工具链.md) - 开发工具链整合
- [22-工具与资源/README.md](../README.md) - 工具与资源主题

---

**最后更新**: 2025年1月
