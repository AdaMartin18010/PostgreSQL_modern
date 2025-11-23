# PostgreSQL MVCC-ACID验证工具

> **文档编号**: TOOLS-INDEX
> **主题**: 验证工具
> **版本**: PostgreSQL 17 & 18

---

## 📚 工具清单

### 测试用例

1. ✅ [可见性测试](测试用例/可见性测试.sql)
   - **内容**: 测试不同隔离级别下的可见性行为
   - **用途**: 验证MVCC可见性规则
   - **测试场景**: RC/RR/SERIALIZABLE隔离级别、幻读、写偏序等

2. ✅ [性能测试](测试用例/性能测试.sh)
   - **内容**: 性能测试脚本（吞吐量、延迟、并发、压力测试）
   - **用途**: 评估MVCC性能影响
   - **测试指标**: TPS、延迟、HOT更新率、版本链长度

3. ✅ [故障注入](测试用例/故障注入.sh)
   - **内容**: 故障注入脚本（XID回卷、表膨胀、死锁等）
   - **用途**: 测试MVCC健壮性
   - **故障场景**: XID回卷、表膨胀、死锁、长事务、版本链过长

### 监控脚本

1. ✅ [事务监控](监控脚本/事务监控.sh)
   - **内容**: 监控事务状态、长事务、阻塞事务
   - **用途**: 实时监控事务状态
   - **监控指标**: 活跃事务、长事务、阻塞事务、MVCC统计、XID年龄

2. ✅ [锁监控](监控脚本/锁监控.sh)
   - **内容**: 监控锁状态、锁等待、死锁
   - **用途**: 实时监控锁状态
   - **监控指标**: 所有锁、锁等待、表级锁、行级锁、事务锁、死锁统计

---

## 🚀 快速开始

### 可见性测试

```bash
# 连接到PostgreSQL
psql -h localhost -U postgres -d postgres

# 执行可见性测试
\i 测试用例/可见性测试.sql
```

### 性能测试

```bash
# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export DB_USER=postgres
export CONCURRENT_USERS=10
export TEST_DURATION=60
export ISOLATION_LEVEL="READ COMMITTED"

# 运行性能测试
bash 测试用例/性能测试.sh
```

### 故障注入

```bash
# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export DB_USER=postgres

# 运行故障注入
bash 测试用例/故障注入.sh
```

### 事务监控

```bash
# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export DB_USER=postgres
export WARNING_THRESHOLD=300  # 5分钟
export CRITICAL_THRESHOLD=600  # 10分钟

# 运行事务监控
bash 监控脚本/事务监控.sh
```

### 锁监控

```bash
# 设置环境变量
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=postgres
export DB_USER=postgres

# 运行锁监控
bash 监控脚本/锁监控.sh
```

---

## 📊 测试场景

### 可见性测试场景

1. **READ COMMITTED隔离级别**
   - 脏读防止
   - 不可重复读允许
   - 语句级快照

2. **REPEATABLE READ隔离级别**
   - 脏读防止
   - 不可重复读防止
   - 幻读防止
   - 事务级快照

3. **SERIALIZABLE隔离级别**
   - SSI冲突检测
   - 写偏序异常检测
   - 可串行化保证

### 性能测试场景

1. **吞吐量测试**
   - 测试不同隔离级别下的TPS
   - 评估性能影响

2. **延迟测试**
   - 测试单操作延迟
   - 评估响应时间

3. **并发测试**
   - 测试并发事务性能
   - 评估并发能力

4. **压力测试**
   - 测试高负载下的性能
   - 评估系统极限

### 故障注入场景

1. **XID回卷**
   - 模拟XID接近回卷
   - 测试VACUUM效果

2. **表膨胀**
   - 模拟大量更新产生版本链
   - 测试VACUUM清理效果

3. **死锁**
   - 模拟死锁场景
   - 测试死锁检测

4. **长事务**
   - 模拟长事务
   - 测试快照保持

5. **版本链过长**
   - 模拟版本链过长
   - 测试性能影响

---

## 📝 使用说明

### 环境要求

- PostgreSQL 17或18
- bash shell（Linux/macOS）或Git Bash（Windows）
- psql客户端
- pgbench工具

### 配置说明

所有脚本支持环境变量配置：

- `DB_HOST`: 数据库主机（默认: localhost）
- `DB_PORT`: 数据库端口（默认: 5432）
- `DB_NAME`: 数据库名称（默认: postgres）
- `DB_USER`: 数据库用户（默认: postgres）
- `CONCURRENT_USERS`: 并发用户数（默认: 10）
- `TEST_DURATION`: 测试时长（秒，默认: 60）
- `ISOLATION_LEVEL`: 隔离级别（默认: READ COMMITTED）
- `WARNING_THRESHOLD`: 警告阈值（秒，默认: 300）
- `CRITICAL_THRESHOLD`: 严重阈值（秒，默认: 600）

### 注意事项

1. **测试环境**: 建议在测试环境运行，避免影响生产环境
2. **数据备份**: 运行测试前备份数据
3. **资源监控**: 监控系统资源使用情况
4. **结果分析**: 仔细分析测试结果，理解MVCC行为

---

## 🔗 相关文档

- [MVCC双视角认知体系](../mvcc00.md)
- [场景化全景论证](../mvcc01.md)
- [监控指标体系](../02-多维度视角/运维视角/监控指标体系.md)
- [形式化论证](../04-形式化论证/理论论证/README.md)

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
