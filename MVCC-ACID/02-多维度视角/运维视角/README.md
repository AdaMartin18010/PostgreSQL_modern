# 运维视角 - PostgreSQL MVCC-ACID监控体系

> **文档编号**: OPS-INDEX
> **主题**: 运维视角监控体系
> **版本**: PostgreSQL 17 & 18

---

## 📚 文档清单

1. ✅ [监控指标体系](监控指标体系.md)
   - **内容**: 事务、锁、表膨胀、XID年龄、性能监控指标
   - **文档编号**: OPS-MONITOR-001

2. ✅ [Prometheus配置](Prometheus配置.md)
   - **内容**: PostgreSQL Exporter配置、Prometheus服务器配置、告警规则
   - **文档编号**: OPS-PROMETHEUS-001

3. ✅ [Grafana仪表盘](Grafana仪表盘.md)
   - **内容**: 数据源配置、各类监控仪表盘配置
   - **文档编号**: OPS-GRAFANA-001

---

## 🎯 核心主题

### 监控指标
- 事务监控（活动事务、长事务、阻塞事务）
- 锁监控（锁等待、锁持有、死锁）
- 表膨胀监控（死亡元组、表大小、VACUUM）
- XID年龄监控（数据库XID年龄、表XID年龄、回卷风险）
- 性能监控（慢查询、连接、复制）

### 监控工具
- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化仪表盘
- **PostgreSQL Exporter**: PostgreSQL指标导出

---

## 🔗 相关文档

- [MVCC双视角认知体系](../../mvcc00.md)
- [场景化全景论证](../../mvcc01.md)
- [程序员视角驱动文档](../程序员视角/README.md)

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
