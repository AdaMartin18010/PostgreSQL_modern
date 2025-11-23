# 数据库设计视角 - PostgreSQL MVCC-ACID表设计最佳实践

> **文档编号**: DESIGN-INDEX
> **主题**: 数据库设计视角
> **版本**: PostgreSQL 17 & 18

---

## 📚 文档清单

1. ✅ [表结构设计深度分析](表结构设计深度分析.md)
   - **内容**: 列类型选择、列设计优化、规范化设计
   - **文档编号**: DESIGN-TABLE-001

2. ✅ [存储参数调优](存储参数调优.md)
   - **内容**: fillfactor、TOAST、autovacuum参数
   - **文档编号**: DESIGN-STORAGE-001

3. ✅ [分区表设计](分区表设计.md)
   - **内容**: 分区策略、分区级MVCC、性能优化
   - **文档编号**: DESIGN-PARTITION-001

4. ✅ [索引设计](索引设计.md)
   - **内容**: 索引类型选择、索引维护、最佳实践
   - **文档编号**: DESIGN-INDEX-001

5. ✅ [Rust数据结构与PostgreSQL表结构映射](Rust数据结构与PostgreSQL表结构映射.md) ⭐ 新增
   - **内容**: Struct与Table映射、Enum与PostgreSQL枚举类型、Option类型与NULL值处理、嵌套结构与JSONB
   - **文档编号**: DESIGN-RUST-DATASTRUCTURE-001

6. ✅ [Rust序列化与PostgreSQL存储](Rust序列化与PostgreSQL存储.md) ⭐ 新增
   - **内容**: Serde序列化框架、序列化格式对比、PostgreSQL存储优化、MVCC与序列化数据
   - **文档编号**: DESIGN-RUST-SERIALIZATION-001

7. ✅ [Rust类型系统与PostgreSQL类型系统](Rust类型系统与PostgreSQL类型系统.md) ⭐ 新增
    - **内容**: 基本类型映射、时间类型映射、复合类型映射、自定义类型映射、类型安全保证
    - **文档编号**: DESIGN-RUST-TYPESYSTEM-001

8. ✅ [Rust查询构建与PostgreSQL查询优化](Rust查询构建与PostgreSQL查询优化.md) ⭐ 新增
    - **内容**: 查询构建器设计、查询优化策略、MVCC查询优化、性能优化实践
    - **文档编号**: DESIGN-RUST-QUERY-001

9. ✅ [Rust内存布局优化](Rust内存布局优化.md) ⭐ 新增
    - **内容**: Rust内存布局基础、PostgreSQL存储布局、内存布局优化、MVCC内存优化
    - **文档编号**: DESIGN-RUST-MEMORY-001

10. ✅ [Rust集合类型与PostgreSQL数组](Rust集合类型与PostgreSQL数组.md) ⭐ 新增
    - **内容**: Rust集合类型、PostgreSQL数组类型、类型映射、MVCC与集合类型
    - **文档编号**: DESIGN-RUST-COLLECTIONS-001

11. ✅ [Rust批量操作与PostgreSQL MVCC](Rust批量操作与PostgreSQL-MVCC.md) ⭐ 新增
    - **内容**: 批量INSERT、批量UPDATE、批量DELETE、MVCC性能优化
    - **文档编号**: DESIGN-RUST-BATCH-001

12. ✅ [Rust缓存策略与PostgreSQL MVCC](Rust缓存策略与PostgreSQL-MVCC.md) ⭐ 新增
    - **内容**: 缓存策略、MVCC缓存一致性、缓存性能优化、MVCC与缓存协同
    - **文档编号**: DESIGN-RUST-CACHE-001

13. ✅ [Rust索引设计与PostgreSQL索引](Rust索引设计与PostgreSQL索引.md) ⭐ 新增
    - **内容**: PostgreSQL索引类型、Rust索引使用、MVCC与索引
    - **文档编号**: DESIGN-RUST-INDEX-001

14. ✅ [Rust数据访问模式优化](Rust数据访问模式优化.md) ⭐ 新增
    - **内容**: 访问模式分类、MVCC访问优化、访问模式最佳实践
    - **文档编号**: DESIGN-RUST-ACCESS-001

---

## 🎯 核心主题

### 表结构设计

- 列类型选择
- 列顺序优化
- 宽表vs窄表
- 规范化设计

### 存储参数

- fillfactor调优
- TOAST优化
- autovacuum参数

### 分区表

- 分区策略
- 分区级MVCC
- 性能优化

### 索引设计

- 索引类型选择
- 索引维护
- 最佳实践

---

## 🔗 相关文档

- [MVCC双视角认知体系](../../mvcc00.md)
- [场景化全景论证](../../mvcc01.md)
- [程序员视角驱动文档](../程序员视角/README.md)
- [运维视角监控体系](../运维视角/README.md)

---

**最后更新**: 2024年
**维护状态**: ✅ 持续更新
