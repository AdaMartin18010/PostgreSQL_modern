# 03-自我监测系统

> **所属主题**: PostgreSQL 18 自动化运维与自我监测
> **章节编号**: 03
> **创建日期**: 2025年1月

---

## 📋 目录

- [03-自我监测系统](#03-自我监测系统)
  - [📋 目录](#-目录)
  - [章节说明](#章节说明)
    - [PostgreSQL 18监测增强](#postgresql-18监测增强)
    - [快速开始](#快速开始)
    - [监测指标说明](#监测指标说明)
  - [子章节](#子章节)
  - [相关资源](#相关资源)
    - [相关章节](#相关章节)
    - [参考资料](#参考资料)
  - [导航](#导航)

---

## 章节说明

本章节介绍PostgreSQL 18的自我监测系统，包括：

- **pg_stat_io增强监控**：PostgreSQL 18新增read_bytes/write_bytes列，提供字节级别I/O统计
- **后端I/O追踪**：pg_stat_get_backend_io()函数支持后端级别I/O追踪
- **连接性能监测**：log_connections细粒度配置，记录连接阶段耗时
- **WAL性能监测**：pg_stat_checkpointer增强，提供详细的检查点统计

### PostgreSQL 18监测增强

PostgreSQL 18在自我监测方面的重要增强：

1. **I/O统计增强**（3.1）：
   - `read_bytes`、`write_bytes`、`extend_bytes`列
   - 字节级别统计，更准确的I/O性能分析

2. **后端I/O追踪**（3.2）：
   - `pg_stat_get_backend_io()`函数
   - 后端级别I/O统计，便于诊断特定后端的问题

3. **连接性能监测**（3.3）：
   - `log_connections`细粒度配置
   - 记录连接各阶段的耗时，识别连接瓶颈

4. **检查点统计增强**（3.4）：
   - `pg_stat_checkpointer`新增`num_done`列
   - 更详细的检查点性能统计

### 快速开始

1. **启用I/O监控**（推荐优先配置）
   - 阅读：[3.1 pg_stat_io增强监控](./01-pg_stat_io增强监控.md)
   - 查询I/O统计：`SELECT * FROM pg_stat_io;`

2. **设置连接性能监测**
   - 阅读：[3.3 连接性能监测](./03-连接性能监测.md)
   - 配置：`log_connections = on`

3. **监控后端I/O**
   - 阅读：[3.2 后端I/O追踪](./02-后端I-O追踪.md)
   - 使用函数：`SELECT * FROM pg_stat_get_backend_io(pid);`

### 监测指标说明

| 监测视图/函数 | 主要指标 | 用途 |
|-------------|---------|------|
| `pg_stat_io` | read_bytes, write_bytes | 系统级I/O性能分析 |
| `pg_stat_get_backend_io()` | backend级别I/O | 特定后端I/O诊断 |
| `pg_stat_activity` | 连接状态和耗时 | 连接性能监测 |
| `pg_stat_checkpointer` | 检查点统计 | WAL性能分析 |

---

## 子章节

| 章节编号 | 子章节 | 文件 | 说明 |
|---------|--------|------|------|
| 3.1 | pg_stat_io增强监控 | [01-pg_stat_io增强监控.md](./01-pg_stat_io增强监控.md) | ✅ I/O统计增强（read_bytes/write_bytes） |
| 3.2 | 后端I/O追踪 | [02-后端I-O追踪.md](./02-后端I-O追踪.md) | ✅ pg_stat_get_backend_io()函数使用 |
| 3.3 | 连接性能监测 | [03-连接性能监测.md](./03-连接性能监测.md) | ✅ 连接阶段耗时监测 |
| 3.4 | WAL性能监测 | [04-WAL性能监测.md](./04-WAL性能监测.md) | ✅ WAL和检查点统计 |

> **注意**: ✅ 所有章节已完成内容拆分

---

## 相关资源

### 相关章节

- [02-自动化性能调优](../02-自动化性能调优/README.md) - 性能优化配置
- [04-自动化诊断](../04-自动化诊断/README.md) - 基于监测数据的自动诊断
- [05-自动化运维脚本](../05-自动化运维脚本/README.md) - 自动化健康检查
- [07-监控仪表板](../07-监控仪表板/README.md) - 监控仪表板设计

### 参考资料

- [PostgreSQL 18 监控统计文档](https://www.postgresql.org/docs/18/monitoring-stats.html)
- [PostgreSQL 18 pg_stat_io文档](https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-IO-VIEW)
- [PostgreSQL 18 日志配置文档](https://www.postgresql.org/docs/18/runtime-config-logging.html)

## 导航

- [返回主文档](../README.md)
- [上一章：02-自动化性能调优](../02-自动化性能调优/README.md)
- [下一章：04-自动化诊断](../04-自动化诊断/README.md)

---

**最后更新**: 2025年1月
**文档版本**: v2.0（已添加完整目录、详细说明、监测指标说明）
