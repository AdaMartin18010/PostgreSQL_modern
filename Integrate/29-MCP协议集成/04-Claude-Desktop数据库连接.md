# Claude Desktop与PostgreSQL MCP集成指南

> **实战目标**: 5分钟内完成Claude Desktop与PostgreSQL的连接配置  
> **前置要求**: Claude Desktop已安装，PostgreSQL可访问

---

## 一、Claude Desktop简介

Claude Desktop是Anthropic推出的桌面版AI助手，**原生支持MCP协议**，可以连接各种数据源和工具。

### 核心能力

- 自然语言查询数据库
- AI驱动的数据分析
- 自动生成SQL和可视化建议
- 上下文感知的数据库操作

---

## 二、快速配置步骤

### Step 1: 安装Python依赖

```bash
pip install mcp asyncpg pydantic
```

### Step 2: 下载MCP服务器代码

将 `postgres_mcp_server.py` 保存到本地目录，例如：
```
C:\tools\postgres_mcp_server.py
```

### Step 3: 配置Claude Desktop

打开Claude Desktop配置目录：

**Windows**:
```
%APPDATA%\Claude\settings.json
```

**macOS**:
```
~/Library/Application Support/Claude/settings.json
```

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "postgresql": {
      "command": "python",
      "args": ["C:\\tools\\postgres_mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:password@localhost:5432/mydb",
        "READ_ONLY_MODE": "true"
      }
    }
  }
}
```

### Step 4: 重启Claude Desktop

完全退出并重新打开Claude Desktop。

### Step 5: 验证连接

在Claude Desktop中输入：

```
请查看数据库中有哪些表？
```

如果配置正确，Claude会自动调用MCP工具获取表列表。

---

## 三、使用示例

### 示例1: 自然语言查询

**用户**: "查询用户表中最新的10条记录"

**Claude会自动**:
1. 调用 `search_tables` 查找用户表
2. 调用 `get_table_schema` 获取表结构
3. 调用 `execute_sql` 执行查询
4. 返回格式化结果

### 示例2: 数据分析

**用户**: "分析订单表的数据分布情况"

**Claude会自动**:
1. 获取订单表结构
2. 执行统计查询
3. 分析数据特征
4. 生成可视化建议

### 示例3: 性能诊断

**用户**: "有哪些慢查询需要优化？"

**Claude会自动**:
1. 读取 `postgres://slow-queries` 资源
2. 分析执行计划
3. 提供优化建议

---

## 四、高级配置

### 多数据库支持

```json
{
  "mcpServers": {
    "postgres-production": {
      "command": "python",
      "args": ["C:/tools/postgres_mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@prod-host:5432/proddb",
        "READ_ONLY_MODE": "true"
      }
    },
    "postgres-analytics": {
      "command": "python",
      "args": ["C:/tools/postgres_mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@analytics-host:5432/analytics",
        "READ_ONLY_MODE": "false"
      }
    }
  }
}
```

### 安全最佳实践

1. **使用只读模式**: 设置 `READ_ONLY_MODE=true`
2. **限制查询超时**: 设置 `QUERY_TIMEOUT=30`
3. **使用专用只读账号**: 创建仅具有SELECT权限的数据库用户
4. **启用SSL**: 使用 `postgresql://...?sslmode=require`

---

## 五、故障排查

### 问题1: Claude无法识别MCP服务器

**解决**:
- 检查配置文件路径是否正确
- 验证Python路径和脚本路径
- 查看Claude Desktop日志

### 问题2: 数据库连接失败

**解决**:
- 测试数据库连接字符串: `psql "postgresql://..."`
- 检查防火墙设置
- 验证用户名密码

### 问题3: 查询超时

**解决**:
- 增加 `QUERY_TIMEOUT` 值
- 优化查询语句
- 检查数据库性能

---

## 六、下一步

- 学习 [02-PostgreSQL MCP服务器开发](./02-PostgreSQL-MCP服务器开发.md) 自定义功能
- 了解 [05-MCP安全最佳实践](./05-MCP安全最佳实践.md)
- 探索 [03-LangChain与MCP集成](./03-LangChain与MCP集成.md)

---

*配置完成！现在您可以通过自然语言与PostgreSQL数据库对话了。*
