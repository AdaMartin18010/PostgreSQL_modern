# MCP安全最佳实践指南

> **安全级别**: 企业级  
> **适用范围**: 生产环境部署

---

## 一、安全威胁模型

### 1.1 潜在风险

```
┌─────────────────────────────────────────────────────────┐
│                  MCP安全威胁模型                         │
├─────────────────────────────────────────────────────────┤
│  🔴 高优先级                                             │
│     - SQL注入攻击                                        │
│     - 权限提升                                            │
│     - 敏感数据泄露                                        │
│                                                         │
│  🟠 中优先级                                             │
│     - 工具中毒攻击 (Tool Poisoning)                      │
│     - 间接提示注入 (Indirect Prompt Injection)          │
│     - 资源耗尽攻击                                        │
│                                                         │
│  🟡 低优先级                                             │
│     - 信息泄露                                            │
│     - 服务拒绝                                            │
└─────────────────────────────────────────────────────────┘
```

### 1.2 MCP特定风险

根据最新研究 (arXiv:2506.13538, 2025):

| 攻击类型 | 风险等级 | 说明 |
|----------|----------|------|
| Tool Poisoning | 🔴 高 | 恶意MCP服务器篡改工具行为 |
| Context Injection | 🔴 高 | 通过资源内容注入恶意指令 |
| Privilege Escalation | 🔴 高 | 利用工具调用提升权限 |
| Data Exfiltration | 🟠 中 | 通过工具响应泄露数据 |

---

## 二、数据库层安全

### 2.1 最小权限原则

```sql
-- 创建专用只读用户
CREATE USER mcp_readonly WITH PASSWORD 'secure_random_password';

-- 仅授予SELECT权限
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;

-- 确保未来表也自动授权
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO mcp_readonly;

-- 限制连接数
ALTER USER mcp_readonly WITH CONNECTION LIMIT 10;
```

### 2.2 行级安全 (RLS)

```sql
-- 启用RLS
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- 创建策略
CREATE POLICY mcp_user_isolation ON sensitive_data
    FOR SELECT
    TO mcp_readonly
    USING (tenant_id = current_setting('app.current_tenant')::int);
```

### 2.3 查询限制

```python
# 在MCP Server中实施查询限制
DANGEROUS_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
    'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE',
    'COPY', '\\copy', 'pg_read_file', 'pg_exec'
]

def validate_query(query: str) -> bool:
    """验证查询安全性"""
    query_upper = query.strip().upper()
    
    # 检查危险关键字
    for keyword in DANGEROUS_KEYWORDS:
        if query_upper.startswith(keyword + ' '):
            return False
    
    # 检查注释注入
    if '--' in query or '/*' in query:
        return False
    
    # 只允许SELECT语句
    if not query_upper.startswith('SELECT '):
        return False
    
    return True
```

---

## 三、应用层安全

### 3.1 输入验证

```python
from pydantic import BaseModel, validator
import re

class QueryRequest(BaseModel):
    query: str
    max_rows: int = 100
    
    @validator('query')
    def validate_query(cls, v):
        # 长度限制
        if len(v) > 10000:
            raise ValueError("Query too long")
        
        # 只允许SELECT
        if not v.strip().upper().startswith('SELECT'):
            raise ValueError("Only SELECT queries allowed")
        
        # 禁止危险模式
        dangerous_patterns = [
            r';\s*DROP\s+',
            r';\s*DELETE\s+',
            r'UNION\s+SELECT',
            r'pg_\w+\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Dangerous pattern detected: {pattern}")
        
        return v
    
    @validator('max_rows')
    def validate_max_rows(cls, v):
        if v < 1 or v > 10000:
            raise ValueError("max_rows must be between 1 and 10000")
        return v
```

### 3.2 审计日志

```python
import logging
import json
from datetime import datetime

# 配置审计日志
audit_logger = logging.getLogger('mcp_audit')
audit_logger.setLevel(logging.INFO)

handler = logging.FileHandler('mcp_audit.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
audit_logger.addHandler(handler)

def log_tool_call(tool_name: str, arguments: dict, user_id: str = None):
    """记录工具调用审计日志"""
    audit_logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "tool_call",
        "tool": tool_name,
        "arguments": arguments,
        "user_id": user_id,
        "source_ip": get_client_ip()
    }))

def log_query_execution(query: str, duration_ms: float, row_count: int):
    """记录查询执行"""
    audit_logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "query_execution",
        "query_hash": hashlib.sha256(query.encode()).hexdigest()[:16],
        "duration_ms": duration_ms,
        "row_count": row_count
    }))
```

### 3.3 速率限制

```python
from collections import defaultdict
import time

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        
        # 清理旧请求记录
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # 记录新请求
        self.requests[client_id].append(now)
        return True

# 使用
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    client_id = get_client_id()
    
    if not rate_limiter.is_allowed(client_id):
        return [TextContent(type="text", text="Rate limit exceeded. Try again later.")]
    
    # 继续处理...
```

---

## 四、网络安全

### 4.1 传输加密

```python
# 使用SSL连接PostgreSQL
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"

# 对于本地stdio通信，依赖OS级别的权限控制
```

### 4.2 网络隔离

```yaml
# Docker Compose示例
version: '3.8'
services:
  postgres:
    image: postgres:18
    networks:
      - db_network
    environment:
      - POSTGRES_USER=mcp_user
      - POSTGRES_PASSWORD=secure_password
  
  mcp_server:
    build: .
    networks:
      - db_network
    environment:
      - DATABASE_URL=postgresql://mcp_user:secure_password@postgres:5432/db
    # 不暴露端口，仅通过stdio通信

networks:
  db_network:
    internal: true  # 内部网络，不暴露给主机
```

---

## 五、监控与告警

### 5.1 异常检测

```python
class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self):
        self.suspicious_patterns = [
            (r'SELECT\s+\*\s+FROM\s+password', 'Potential password table access'),
            (r'SELECT\s+\*\s+FROM\s+users', 'Bulk user data access'),
            (r'pg_sleep\s*\(', 'Potential DoS attempt'),
        ]
    
    def check_query(self, query: str, user_id: str) -> list[str]:
        """检查可疑查询"""
        alerts = []
        
        for pattern, description in self.suspicious_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                alerts.append(description)
                self.send_alert(user_id, query, description)
        
        return alerts
    
    def send_alert(self, user_id: str, query: str, description: str):
        """发送安全告警"""
        # 集成企业告警系统
        alert_data = {
            "severity": "high",
            "category": "suspicious_query",
            "user_id": user_id,
            "query_preview": query[:100],
            "description": description
        }
        # send_to_security_team(alert_data)
```

---

## 六、安全清单

### 部署前检查清单

- [ ] 使用专用只读数据库账号
- [ ] 启用查询验证（仅允许SELECT）
- [ ] 配置查询超时和结果限制
- [ ] 启用审计日志
- [ ] 实施速率限制
- [ ] 配置SSL/TLS加密
- [ ] 设置监控告警
- [ ] 定期审查访问日志
- [ ] 更新依赖到最新版本
- [ ] 进行渗透测试

---

## 七、参考资源

1. **MCP Security Paper** (2025): arXiv:2506.13538
2. **PostgreSQL Security Guide**: https://www.postgresql.org/docs/current/security.html
3. **OWASP Database Security**: https://owasp.org/www-project-database-security/

---

*安全是持续的过程，请定期审查和更新安全策略。*
