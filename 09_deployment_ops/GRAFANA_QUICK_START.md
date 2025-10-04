# 🚀 Grafana Dashboard 快速启动指南

**目标**：10分钟内完成PostgreSQL 17 Grafana Dashboard部署

**前置要求**：

- ✅ PostgreSQL 17.x 正在运行
- ✅ 有管理员权限

---

## ⚡ 快速部署（3步）

### Step 1：安装Grafana（5分钟）

```bash
# Windows（使用Chocolatey）
choco install grafana

# 或下载安装包
# <https://grafana.com/grafana/download>

# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb <https://packages.grafana.com/oss/deb> stable main"
wget -q -O - <https://packages.grafana.com/gpg.key> | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# 启动Grafana
sudo systemctl start grafana-server

# 访问: <http://localhost:3000>
# 默认账号: admin / admin
```

---

### Step 2：配置数据源（2分钟）

1. **登录Grafana**: <http://localhost:3000（admin/admin）>

2. **添加PostgreSQL数据源**:
   - 点击左侧菜单 ⚙️ Configuration → Data Sources
   - 点击 "Add data source"
   - 选择 "PostgreSQL"

3. **填写连接信息**:

   ```yaml
   Name: PostgreSQL-Prod
   Host: localhost:5432
   Database: your_database_name
   User: postgres  # 或您的数据库用户
   Password: your_password
   SSL Mode: disable  # 本地测试可以disable
   Version: 17.x
   ```

4. **点击 "Save & Test"**（应该显示绿色 ✓）

---

### Step 3：导入Dashboard（3分钟）

1. **导入Dashboard JSON**:
   - 点击左侧菜单 + → Import
   - 点击 "Upload JSON file"
   - 选择: `09_deployment_ops/grafana_dashboard.json`
   - 点击 "Load"

2. **选择数据源**:
   - Datasource: 选择 "PostgreSQL-Prod"
   - 点击 "Import"

3. **查看Dashboard**:
   - Dashboard将自动打开
   - 您应该看到6大监控面板和24个图表

---

## ✅ 验证

访问Dashboard后，您应该看到：

```text
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL 17 Production Monitoring                     │
├─────────────────────────────────────────────────────────┤
│  📊 连接数: XX    TPS: XXX    缓存率: 99%   延迟: 0s    │
├─────────────────────────────────────────────────────────┤
│  连接状态分布（饼图）      数据库连接分布（柱状图）      │
├─────────────────────────────────────────────────────────┤
│  TOP 10 慢查询（表格）                                   │
├─────────────────────────────────────────────────────────┤
│  锁统计（柱状图）          TOP 10表（表格）              │
├─────────────────────────────────────────────────────────┤
│  性能趋势（时间序列图）                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ 故障排除

### 问题1：数据源测试失败

**解决方案**：

```sql
-- 1. 确认PostgreSQL正在运行
SELECT version();

-- 2. 检查用户权限
\du

-- 3. 如果权限不足，授予必要权限
GRANT CONNECT ON DATABASE your_database TO your_user;
GRANT pg_monitor TO your_user;
```

---

### 问题2：面板显示"No Data"

**原因**：可能需要 `pg_stat_statements` 扩展

**解决方案**：

```sql
-- 1. 创建扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 2. 配置postgresql.conf（需要重启）
shared_preload_libraries = 'pg_stat_statements'

-- 3. 重启PostgreSQL
sudo systemctl restart postgresql
```

---

### 问题3：复制监控面板为空

**原因**：当前是单机环境，没有配置复制

**解决方案**：

- 如果不需要复制监控，可以删除该面板
- 或参考 `04_modern_features/` 配置主备复制

---

## 📊 Dashboard功能说明

### 刷新设置

默认：30秒自动刷新

修改：

- 右上角时间范围选择器旁边的下拉菜单
- 可选：10s, 30s, 1m, 5m, 15m

---

### 时间范围

默认：Last 1 hour

修改：

- 右上角点击时间范围
- 可选：Last 5m, 15m, 1h, 6h, 24h
- 或自定义范围

---

### 数据库切换

如果有多个数据库：

- 顶部的 "database" 下拉菜单
- 选择要监控的数据库

---

## 🔔 配置告警（可选）

### 高连接数告警

1. 进入 "当前连接数" 面板
2. 点击面板标题 → Edit
3. 点击 "Alert" 标签
4. 设置条件:

   ```yaml
   Condition: WHEN last() OF A IS ABOVE 80
   FOR: 5m
   ```

5. 添加通知渠道（Email/Slack/webhook）
6. 保存

---

## 📚 更多信息

详细文档：

- 完整实施指南: [grafana_dashboard_guide.md](grafana_dashboard_guide.md)
- 监控指标说明: [monitoring_metrics.md](monitoring_metrics.md)
- 监控SQL查询: [monitoring_queries.sql](monitoring_queries.sql)

---

## ✨ 提示

1. **性能优化**：
   - 如果Dashboard很慢，增加刷新间隔到1分钟
   - 检查PostgreSQL的 `pg_stat_statements.max` 设置

2. **安全**：
   - 生产环境建议配置SSL
   - 使用只读监控用户

3. **定制**：
   - 可以根据需要添加/删除面板
   - 可以调整阈值和颜色

---

**完成！现在您已经有了一个功能完整的PostgreSQL 17监控Dashboard！** 🎉

**下一步**：

- 配置告警规则
- 定制面板布局
- 添加更多监控指标

**需要帮助**？查看 [grafana_dashboard_guide.md](grafana_dashboard_guide.md) 获取详细说明。
