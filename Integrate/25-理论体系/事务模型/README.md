---

> **📋 文档来源**: `MVCC-ACID-CAP\25-理论体系\事务模型\README.md`
> **📅 复制日期**: 2025-12-22
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

# 事务模型 - PostgreSQL MVCC-ACID分布式事务

> **文档编号**: TRANSACTION-INDEX
> **主题**: 事务模型
> **版本**: PostgreSQL 17 & 18

---

## 📚 文档清单

1. ✅ [两阶段提交深度分析](两阶段提交深度分析.md)
   - **内容**: 2PC原理、PostgreSQL实现、性能影响
   - **文档编号**: TRANSACTION-2PC-001

2. ✅ [XA事务深度分析](XA事务深度分析.md)
   - **内容**: XA协议、PostgreSQL支持、事务管理器集成
   - **文档编号**: TRANSACTION-XA-001

3. ✅ [分布式事务协调](分布式事务协调.md)
   - **内容**: 协调器设计、故障恢复、性能优化
   - **文档编号**: TRANSACTION-COORDINATION-001

4. ✅ [最终一致性](最终一致性.md)
   - **内容**: 最终一致性原理、PostgreSQL实现、应用场景
   - **文档编号**: TRANSACTION-EVENTUAL-001

5. ✅ [分布式事务最佳实践](分布式事务最佳实践.md)
   - **内容**: 方案对比、设计模式、故障处理、性能优化
   - **文档编号**: TRANSACTION-BESTPRACTICES-001

6. ✅ [隔离级别深度分析](隔离级别深度分析.md) ⭐ 新增（P2改进）
   - **内容**: ANSI SQL标准、PostgreSQL实现、快照隔离vs可串行化、实际异常案例、性能影响
   - **文档编号**: TRANSACTION-ISOLATION-DEEP-001

7. ✅ [分布式事务模式深度对比](分布式事务模式深度对比.md) ⭐ 新增（P2改进）
   - **内容**: 2PC、XA、Saga、TCC深度对比、实际系统案例、最佳实践
   - **文档编号**: TRANSACTION-DISTRIBUTED-PATTERNS-001

8. ✅ [MVCC与锁机制](MVCC_Lock_Transaction/mvcc_lock00.md) ⭐ 新增
   - **内容**: MVCC与锁机制对比、并发控制策略、形式化证明
   - **文档编号**: TRANSACTION-MVCC-LOCK-001

9. ✅ [MVCC与锁机制（补充）](MVCC_Lock_Transaction/mvcc_lock.md) ⭐ 新增
   - **内容**: MVCC与锁机制深度分析、冲突处理、最佳实践
   - **文档编号**: TRANSACTION-MVCC-LOCK-002

---

## 🎯 核心主题

### 分布式事务协议

- 两阶段提交（2PC）
- XA事务
- 最终一致性

### 事务协调

- 协调器设计
- 故障恢复
- 性能优化

### 设计模式

- Saga模式
- TCC模式
- 事件溯源

---

## 🔗 相关文档

- [MVCC高级分析与形式证明](../../03-事务与并发/03.01-MVCC高级分析与形式证明.md)
- [MVCC与其他并发控制模型对比](../../03-事务与并发/03.02-MVCC与其他并发控制模型对比与极限分析.md)
- [形式化方法](../../25-理论体系/25.01-形式化方法/README.md) - 形式化论证相关
- [性能调优](../../30-性能调优/README.md) - 性能模型相关

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
