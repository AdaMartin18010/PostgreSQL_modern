# 程序员视角 - PostgreSQL MVCC事务管理最佳实践

> **文档编号**: DEV-INDEX
> **主题**: 程序员视角驱动和ORM框架事务管理
> **版本**: PostgreSQL 17 & 18

---

## 📚 文档清单

### 编程语言驱动

1. ✅ [Python驱动事务管理](Python驱动事务管理.md)
   - **驱动**: psycopg2 / asyncpg
   - **内容**: 同步/异步事务管理、MVCC最佳实践、实际场景案例
   - **文档编号**: DEV-PYTHON-001

2. ✅ [Java驱动事务管理](Java驱动事务管理.md)
   - **驱动**: JDBC / HikariCP
   - **内容**: JDBC基础、HikariCP连接池、Spring事务管理
   - **文档编号**: DEV-JAVA-001

3. ✅ [Go驱动事务管理](Go驱动事务管理.md)
   - **驱动**: pgx
   - **内容**: pgx基础、连接池管理、MVCC最佳实践
   - **文档编号**: DEV-GO-001

4. ✅ [Node.js驱动事务管理](Node.js驱动事务管理.md)
   - **驱动**: pg (node-postgres)
   - **内容**: pg基础、连接池管理、Promise模式事务管理
   - **文档编号**: DEV-NODEJS-001

### ORM框架

5. ✅ [ORM框架事务管理](ORM框架事务管理.md)
   - **框架**: Django ORM, SQLAlchemy, TypeORM, Prisma
   - **内容**: 各ORM框架事务管理、MVCC最佳实践、框架对比
   - **文档编号**: DEV-ORM-001

---

## 🎯 核心主题

### 事务管理基础

- 连接管理
- 事务操作（BEGIN, COMMIT, ROLLBACK）
- 隔离级别设置
- 错误处理和重试

### MVCC最佳实践

- 短事务原则
- 批量操作优化
- 并发控制（SELECT FOR UPDATE, 乐观锁, 悲观锁）
- 性能优化

### 实际场景案例

- 电商库存扣减
- 银行转账
- 日志写入

---

## 📊 快速导航

### 按语言查找

- **Python** → [Python驱动事务管理](Python驱动事务管理.md)
- **Java** → [Java驱动事务管理](Java驱动事务管理.md)
- **Go** → [Go驱动事务管理](Go驱动事务管理.md)
- **Node.js** → [Node.js驱动事务管理](Node.js驱动事务管理.md)

### 按框架查找

- **Django ORM** → [ORM框架事务管理](ORM框架事务管理.md)
- **SQLAlchemy** → [ORM框架事务管理](ORM框架事务管理.md)
- **TypeORM** → [ORM框架事务管理](ORM框架事务管理.md)
- **Prisma** → [ORM框架事务管理](ORM框架事务管理.md)

### 按主题查找

- **事务管理基础** → 所有文档第一部分
- **连接池管理** → Python/Java/Go/Node.js文档第二部分
- **MVCC最佳实践** → 所有文档第三部分
- **实际场景案例** → 所有文档第四部分

---

## 🔗 相关文档

- [MVCC双视角认知体系](../../mvcc00.md)
- [场景化全景论证](../../mvcc01.md)
- [PostgreSQL版本特性](../../01-理论基础/PostgreSQL版本特性/README.md)

---

**最后更新**: 2024年
**维护状态**: ✅ 已完成
