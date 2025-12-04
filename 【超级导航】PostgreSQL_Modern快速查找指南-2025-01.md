# 【超级导航】PostgreSQL_Modern 快速查找指南

> **创建时间**: 2025年1月
> **用途**: 帮助用户快速找到所需内容
> **适用**: 所有PostgreSQL_Modern用户

---

## 🎯 我想找什么？（快速跳转）

### 5秒定位

| 我想... | 直接跳转 |
|---------|---------|
| **5分钟快速入门** | → [快速开始指南](./PostgreSQL培训/00-项目文件/PostgreSQL快速开始指南.md) ⭐ |
| **解决紧急故障** | → [故障诊断](./PostgreSQL/runbook/) + [诊断脚本](./PostgreSQL/sql/) 🔴 |
| **查SQL命令** | → [SQL命令速查表](./PostgreSQL培训/00-项目文件/PostgreSQL_SQL命令速查表.md) ⚡ |
| **开发AI应用** | → [PostgreSQL_AI](./PostgreSQL_AI/README.md) 🤖 |
| **学习完整课程** | → [学习路径指南](./PostgreSQL培训/00-项目文件/PostgreSQL学习路径完整指南.md) 🎓 |
| **查看实战案例** | → [案例库](./PostgreSQL/cases/) 💼 |

---

## 📋 按需求导航

### 1. 我是新手，想入门PostgreSQL

**推荐路径（循序渐进）**：

```
第1天：了解PostgreSQL
├─ 📖 [PostgreSQL快速开始指南](./PostgreSQL培训/00-项目文件/PostgreSQL快速开始指南.md) (5分钟)
├─ 📖 [PostgreSQL历史与发展](./PostgreSQL培训/01-核心课程/01.00-PostgreSQL历史与发展.md) (15分钟)
└─ 📖 [系统架构与设计原理](./PostgreSQL培训/01-核心课程/01.01-系统架构与设计原理.md) (30分钟)

第1周：SQL基础
├─ 📖 [SQL基础培训](./PostgreSQL培训/01-SQL基础/SQL基础培训.md)
├─ 💻 练习：基本查询、插入、更新
└─ 🎓 完成作业：设计一个简单数据库

第2周：数据类型和函数
├─ 📖 [数据类型详解](./PostgreSQL培训/03-数据类型/数据类型详解.md)
├─ 📖 [函数与存储过程](./PostgreSQL培训/04-函数与编程/函数与存储过程.md)
└─ 💻 练习：使用不同数据类型和函数

第3-4周：查询优化和高级特性
├─ 📖 [索引与查询优化](./PostgreSQL培训/01-SQL基础/索引与查询优化.md)
├─ 📖 [高级SQL特性](./PostgreSQL培训/02-SQL高级特性/高级SQL特性.md)
└─ 🎯 项目：完整的博客系统数据库
```

**完整学习路径**：[PostgreSQL学习路径完整指南](./PostgreSQL培训/00-项目文件/PostgreSQL学习路径完整指南.md)

---

### 2. 我要开发AI应用

**推荐路径（快速上手）**：

```
理解AI数据库基础（1天）
├─ 📖 [PostgreSQL_AI主文档](./PostgreSQL_AI/README.md)
├─ 📖 [向量搜索原理](./PostgreSQL_AI/01-理论基础/)
└─ 📖 [RAG架构设计](./PostgreSQL_AI/01-理论基础/)

掌握核心技术（2-3天）
├─ 📖 [pgvector详解](./PostgreSQL_View/01-向量与混合搜索/)
├─ 📖 [pgai详解](./PostgreSQL_View/02-AI自治与自优化/)
├─ 💻 [一键部署脚本](./PostgreSQL_View/01-向量与混合搜索/最佳实践/部署脚本/)
└─ 🧪 实践：部署向量搜索系统

学习应用场景（3-5天）
├─ 📖 [RAG系统](./PostgreSQL_AI/04-应用场景/)
├─ 📖 [智能推荐](./PostgreSQL_AI/04-应用场景/)
├─ 📖 [50+行业场景](./PostgreSQL_View/08-落地案例/)
└─ 💼 案例学习：电商推荐系统

实战项目（1-2周）
├─ 📖 [语义搜索系统](./PostgreSQL/08-实战案例/06.01-语义搜索系统端到端实现.md)
├─ 📖 [RAG知识库项目](./PostgreSQL/08-实战案例/06.02-RAG知识库完整项目.md)
└─ 🎯 完整项目：自己的AI应用
```

**注意**：AI主题有重叠，建议：

- **理论和架构** → PostgreSQL_AI
- **技术详解和案例** → PostgreSQL_View
- **实战代码和工具** → PostgreSQL知识库

---

### 3. 我要解决生产问题

**紧急故障（立即）**：

```
生产故障快速响应（15-30分钟）
├─ 🔴 [故障诊断手册](./DataBaseTheory/00-总览/PostgreSQL18故障诊断手册-2025-12-04.md)
├─ 🔴 [常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md)
├─ 💻 [诊断脚本](./DataBaseTheory/22-工具脚本/)
└─ 📖 [故障诊断案例库](./DataBaseTheory/20-故障诊断案例库/)
```

**性能优化（1-2天）**：

```
性能问题诊断和优化（1-2天）
├─ 📋 [性能调优检查清单](./PostgreSQL培训/00-项目文件/PostgreSQL性能调优检查清单.md)
├─ 📖 [性能调优深入](./PostgreSQL培训/11-性能调优/性能调优深入.md)
├─ 💻 [性能监控脚本](./DataBaseTheory/22-工具脚本/01-性能监控脚本.sh)
├─ 📊 [性能问题案例库](./PostgreSQL/cases/)
└─ 📖 [性能调优案例](./DataBaseTheory/00-总览/PostgreSQL18性能调优案例-2025-12-04.md)
```

**Runbook手册**：

| 运维任务 | Runbook |
|---------|---------|
| 性能调优变更 | [性能调优变更闭环](./PostgreSQL/runbook/01-性能调优变更闭环Runbook.md) |
| 监控诊断 | [监控与诊断落地指南](./PostgreSQL/runbook/02-监控与诊断落地指南Runbook.md) |
| 增量备份 | [增量备份与恢复](./PostgreSQL/runbook/03-增量备份与恢复Runbook.md) |
| 集群演练 | [集群与高可用演练SOP](./PostgreSQL/runbook/04-集群与高可用演练SOP.md) |
| 向量检索 | [向量检索落地指南](./PostgreSQL/runbook/05-向量检索落地指南Runbook.md) |
| 日志管理 | [日志与可观测性落地](./PostgreSQL/runbook/06-日志与可观测性落地指南Runbook.md) |

---

### 4. 我要深入理解理论

**推荐路径（学术研究）**：

```
理论基础（1-2周）
├─ 📖 [MVCC理论](./MVCC-ACID-CAP/01-理论基础/事务模型/)
├─ 📖 [ACID公理系统](./MVCC-ACID-CAP/01-理论基础/公理系统/)
├─ 📖 [CAP定理证明](./MVCC-ACID-CAP/01-理论基础/CAP理论/)
└─ 📐 [形式化定义](./MVCC-ACID-CAP/01-理论基础/形式化证明/)

形式化证明（2-3周）
├─ 📐 [25+定理证明](./MVCC-ACID-CAP/04-形式化论证/形式化证明/)
├─ 📐 [PostgreSQL18定理](./MVCC-ACID-CAP/04-形式化论证/形式化证明/PostgreSQL18定理证明.md)
├─ 📊 [性能模型](./MVCC-ACID-CAP/04-形式化论证/性能模型/)
└─ 🧪 [验证工具](./MVCC-ACID-CAP/05-验证工具/)

实践验证（1-2周）
├─ 💻 [17个实验工具](./MVCC-ACID-CAP/05-验证工具/pg18-tests/)
├─ 📖 [实验手册](./MVCC-ACID-CAP/05-验证工具/pg18-tests/【实验手册】PostgreSQL18完整实验指南-2025-12-04.md)
├─ 📖 [7个实战案例](./DataBaseTheory/19-场景案例库/)
└─ 🎯 验证理论正确性
```

**理论与实践闭环**：

| 理论主题 | 理论文档 | 实践案例 | 验证工具 |
|---------|---------|---------|---------|
| **MVCC** | [MVCC理论](./MVCC-ACID-CAP/01-理论基础/事务模型/) | [电商秒杀](./DataBaseTheory/19-场景案例库/01-电商秒杀系统/) | [MVCC测试](./MVCC-ACID-CAP/05-验证工具/) |
| **ACID** | [ACID公理](./MVCC-ACID-CAP/01-理论基础/公理系统/) | [金融交易](./DataBaseTheory/19-场景案例库/05-金融交易系统/) | [ACID测试](./MVCC-ACID-CAP/05-验证工具/) |
| **CAP** | [CAP定理](./MVCC-ACID-CAP/01-理论基础/CAP理论/) | [分布式场景](./MVCC-ACID-CAP/03-场景实践/分布式系统/) | [CAP验证](./MVCC-ACID-CAP/05-验证工具/) |

---

### 5. 我要进行技术选型

**推荐路径（决策支持）**：

```
版本选择（1天）
├─ 📊 [技术栈综合对比](./PostgreSQL培训/00-项目文件/PostgreSQL技术栈综合对比指南.md)
├─ 📖 [PostgreSQL 18新特性](./PostgreSQL/02-版本特性/02.01-PostgreSQL-18-新特性.md)
├─ 📖 [PostgreSQL 17新特性](./PostgreSQL培训/16-PostgreSQL17新特性/README.md)
└─ ⚖️ 对比选择最合适版本

扩展选择（1天）
├─ 📊 扩展对比（在技术栈对比指南中）
├─ 📖 [pgvector向量搜索](./PostgreSQL培训/18-新技术趋势/pgvector向量数据库详解.md)
├─ 📖 [TimescaleDB时序](./PostgreSQL培训/18-新技术趋势/)
└─ ⚖️ 选择需要的扩展

云平台选择（1-2天）
├─ 📊 云服务商对比（在技术栈对比指南中）
├─ 📖 [AWS最佳实践](见对标文档)
├─ 📖 [Azure最佳实践](见对标文档)
├─ 📖 [阿里云最佳实践](见对标文档)
└─ ⚖️ 选择云平台

架构设计（3-5天）
├─ 📖 [系统架构](./PostgreSQL_AI/02-技术架构/)
├─ 📖 [部署架构](./PostgreSQL/05-部署架构/)
├─ 📖 [高可用方案](./PostgreSQL/09-高可用/)
└─ 🎯 完成架构设计
```

---

### 6. 我要版本升级

**推荐路径（安全升级）**：

```
升级准备（1-2天）
├─ 📖 [版本迁移完整指南](./PostgreSQL培训/00-项目文件/PostgreSQL版本迁移完整指南.md)
├─ 📖 [迁移风险评估](迁移指南中)
├─ 💻 [兼容性检查脚本](迁移指南中)
└─ 📋 迁移计划

测试环境升级（2-3天）
├─ 📖 [pg_upgrade方法](迁移指南中)
├─ 📖 [逻辑复制方法](迁移指南中)
├─ 💻 执行升级
└─ 🧪 功能测试

生产环境升级（1天）
├─ 📖 [回滚方案](迁移指南中)
├─ 💻 执行升级
├─ 📊 性能验证
└─ ✅ 升级完成
```

---

## 🧭 按角色导航

### 角色1：初学者

**我的目标**：系统学习PostgreSQL，掌握基本技能

**推荐项目**：

1. **主项目**：[PostgreSQL培训](./PostgreSQL培训/README.md)
   - 从SQL基础开始
   - 按12周课程学习
   - 完成每周作业

2. **辅助资源**：
   - [快速参考卡片](./PostgreSQL培训/00-项目文件/PostgreSQL快速参考卡片集.md) - 速查
   - [常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md) - 遇到问题查

**学习路径**：

```
Month 1: SQL基础
├─ Week 1: SQL基础语法
├─ Week 2: 数据类型和函数
├─ Week 3: 查询优化
└─ Week 4: 入门项目

Month 2: 进阶特性
├─ Week 5: 高级SQL
├─ Week 6: 性能调优
├─ Week 7: 事务和并发
└─ Week 8: 进阶项目

Month 3: 实战应用
├─ Week 9-12: 完整项目实战
└─ 可选：学习AI集成或深入理论
```

---

### 角色2：开发者

**我的目标**：快速解决开发问题，编写高效SQL

**推荐项目**：

1. **主项目**：[PostgreSQL知识库](./PostgreSQL/README.md)
   - 实战案例
   - SQL脚本库
   - Docker示例

2. **辅助资源**：
   - [SQL命令速查表](./PostgreSQL培训/00-项目文件/PostgreSQL_SQL命令速查表.md)
   - [常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md)

**快速入口**：

| 任务 | 快速入口 |
|------|---------|
| 查SQL语法 | [SQL命令速查表](./PostgreSQL培训/00-项目文件/PostgreSQL_SQL命令速查表.md) |
| 查询优化 | [查询优化器](./PostgreSQL/03-查询与优化/02.01-查询优化器原理.md) |
| 解决问题 | [常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md) |
| 参考案例 | [案例库](./PostgreSQL/cases/) |
| 复制代码 | [SQL脚本库](./PostgreSQL/sql/) + [examples](./PostgreSQL/examples/) |

---

### 角色3：DBA

**我的目标**：保障系统稳定，优化性能，快速排障

**推荐项目**：

1. **主项目**：[PostgreSQL知识库](./PostgreSQL/README.md)
   - Runbook手册
   - 监控诊断
   - 备份恢复

2. **辅助资源**：
   - [PostgreSQL培训/运维章节](./PostgreSQL培训/)
   - [DataBaseTheory工具脚本](./DataBaseTheory/22-工具脚本/)

**日常工作**：

| 场景 | Runbook | 工具脚本 |
|------|---------|---------|
| 日常监控 | [监控诊断Runbook](./PostgreSQL/runbook/02-监控与诊断落地指南Runbook.md) | [监控脚本](./DataBaseTheory/22-工具脚本/01-性能监控脚本.sh) |
| 性能调优 | [性能调优Runbook](./PostgreSQL/runbook/01-性能调优变更闭环Runbook.md) | [优化建议](./DataBaseTheory/22-工具脚本/02-自动优化建议.sql) |
| 备份恢复 | [备份恢复Runbook](./PostgreSQL/runbook/03-增量备份与恢复Runbook.md) | [备份脚本](./PostgreSQL/runbook/) |
| 故障排查 | [故障诊断手册](./DataBaseTheory/00-总览/PostgreSQL18故障诊断手册-2025-12-04.md) | [诊断脚本](./DataBaseTheory/22-工具脚本/) |
| 高可用演练 | [高可用演练SOP](./PostgreSQL/runbook/04-集群与高可用演练SOP.md) | [演练脚本](./PostgreSQL/runbook/) |

---

### 角色4：架构师

**我的目标**：技术选型，架构设计，技术决策

**推荐项目**：

1. **核心项目**：
   - [PostgreSQL_AI](./PostgreSQL_AI/README.md) - 技术架构和对比
   - [MVCC-ACID-CAP](./MVCC-ACID-CAP/README.md) - 理论深度

2. **辅助资源**：
   - [PostgreSQL知识库/部署架构](./PostgreSQL/05-部署架构/)
   - [技术栈对比指南](./PostgreSQL培训/00-项目文件/PostgreSQL技术栈综合对比指南.md)

**决策流程**：

```
需求分析（1-2天）
├─ 业务需求
├─ 技术约束
└─ 预算和时间

方案设计（3-5天）
├─ 📊 [技术栈对比](./PostgreSQL培训/00-项目文件/PostgreSQL技术栈综合对比指南.md)
├─ 📖 [架构设计](./PostgreSQL_AI/02-技术架构/)
├─ 📖 [部署架构](./PostgreSQL/05-部署架构/)
└─ 💼 [参考案例](./PostgreSQL_View/08-落地案例/)

方案评审（1-2天）
├─ 📊 [对比分析](./PostgreSQL_AI/06-对比分析/)
├─ 📊 [TCO分析](./PostgreSQL_AI/06-对比分析/)
└─ ⚖️ 风险评估

实施规划（2-3天）
├─ 📖 [实施路径](./PostgreSQL_AI/07-实施路径/)
├─ 📖 [风险应对](./PostgreSQL_AI/07-实施路径/)
└─ 📋 实施计划
```

---

### 角色5：AI工程师

**我的目标**：开发AI应用，集成向量搜索，构建RAG系统

**推荐项目**：

1. **核心项目**：
   - [PostgreSQL_AI](./PostgreSQL_AI/README.md) - 理论和架构
   - [PostgreSQL_View](./PostgreSQL_View/README.md) - 技术和案例

2. **辅助资源**：
   - [PostgreSQL知识库/AI专题](./PostgreSQL/07-前沿技术/AI-时代/)
   - [实战案例](./PostgreSQL/08-实战案例/)

**快速入口**：

| 技术 | 理论（PostgreSQL_AI） | 实践（PostgreSQL_View） | 代码（PostgreSQL知识库） |
|------|---------------------|----------------------|------------------------|
| **向量搜索** | [向量处理能力](./PostgreSQL_AI/03-核心能力/) | [pgvector详解](./PostgreSQL_View/01-向量与混合搜索/) | [语义搜索项目](./PostgreSQL/08-实战案例/06.01-语义搜索系统端到端实现.md) |
| **RAG系统** | [RAG场景](./PostgreSQL_AI/04-应用场景/) | [RAG架构实战](./PostgreSQL/07-前沿技术/05.04-RAG架构实战指南.md) | [RAG知识库项目](./PostgreSQL/08-实战案例/06.02-RAG知识库完整项目.md) |
| **AI自治** | [AI原生调用](./PostgreSQL_AI/03-核心能力/) | [pg_ai详解](./PostgreSQL_View/02-AI自治与自优化/) | [AI工具脚本](./PostgreSQL_View/02-AI自治与自优化/配置示例/) |

---

### 角色6：研究者

**我的目标**：理论研究，学术论文，形式化验证

**推荐项目**：

1. **主项目**：[MVCC-ACID-CAP](./MVCC-ACID-CAP/README.md)
   - 完整理论体系
   - 形式化证明
   - 验证工具

2. **辅助资源**：
   - [DataBaseTheory](./DataBaseTheory/README.md) - 实践验证
   - [PostgreSQL知识库/理论引用](./PostgreSQL/10-理论引用/)

**研究路径**：

```
理论学习（4-6周）
├─ 📖 [MVCC理论](./MVCC-ACID-CAP/01-理论基础/)
├─ 📐 [形式化证明](./MVCC-ACID-CAP/04-形式化论证/形式化证明/)
└─ 📊 [性能模型](./MVCC-ACID-CAP/04-形式化论证/性能模型/)

实验验证（2-4周）
├─ 💻 [验证工具](./MVCC-ACID-CAP/05-验证工具/)
├─ 📖 [实验手册](./MVCC-ACID-CAP/05-验证工具/pg18-tests/【实验手册】PostgreSQL18完整实验指南-2025-12-04.md)
└─ 🧪 进行实验

论文写作（4-8周）
├─ 📖 参考66+学术论文引用
├─ 📊 使用实验数据
└─ 📝 撰写论文
```

---

## 📊 按紧急度导航

### 🔴 紧急：生产故障（立即）

**立即行动**：

1. **故障诊断**：[故障诊断手册](./DataBaseTheory/00-总览/PostgreSQL18故障诊断手册-2025-12-04.md)
2. **快速检查**：
   - [健康检查脚本](./DataBaseTheory/22-工具脚本/03-健康检查.py)
   - [性能监控脚本](./DataBaseTheory/22-工具脚本/01-性能监控脚本.sh)
3. **故障案例**：[故障诊断案例库](./DataBaseTheory/20-故障诊断案例库/)
4. **常见问题**：[常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md)

**按故障类型**：

| 故障类型 | 诊断步骤 | 案例参考 |
|---------|---------|---------|
| **慢查询** | [慢查询诊断](./DataBaseTheory/20-故障诊断案例库/01-慢查询诊断.md) | [性能案例](./DataBaseTheory/00-总览/PostgreSQL18性能调优案例-2025-12-04.md) |
| **锁冲突** | [锁冲突诊断](./DataBaseTheory/20-故障诊断案例库/02-锁冲突诊断.md) | [并发案例](./PostgreSQL/cases/) |
| **内存溢出** | [内存诊断](./DataBaseTheory/20-故障诊断案例库/03-内存溢出诊断.md) | [资源案例](./PostgreSQL/cases/) |
| **连接耗尽** | [连接池管理](./PostgreSQL培训/13-运维管理/连接池管理.md) | [连接案例](./PostgreSQL/cases/) |

---

### 🟡 重要：版本升级/技术选型（本周）

**本周完成**：

1. **版本升级**：
   - [版本迁移指南](./PostgreSQL培训/00-项目文件/PostgreSQL版本迁移完整指南.md)
   - [迁移脚本](见迁移指南)
   - [回滚方案](见迁移指南)

2. **技术选型**：
   - [技术栈对比](./PostgreSQL培训/00-项目文件/PostgreSQL技术栈综合对比指南.md)
   - [架构设计](./PostgreSQL_AI/02-技术架构/)
   - [对比分析](./PostgreSQL_AI/06-对比分析/)

---

### 🟢 学习：系统学习/技能提升（长期）

**长期计划**：

1. **系统学习**：
   - [学习路径指南](./PostgreSQL培训/00-项目文件/PostgreSQL学习路径完整指南.md)
   - [12周课程](./PostgreSQL培训/)
   - [实战项目](./PostgreSQL/08-实战案例/)

2. **技能提升**：
   - [高级特性](./PostgreSQL/04-高级特性/)
   - [AI集成](./PostgreSQL_AI/)
   - [理论深化](./MVCC-ACID-CAP/)

---

## 🗺️ 项目关系图

```
PostgreSQL_Modern（顶层）
├─ PostgreSQL培训（151份）- 学习导向
│  ├─ 与PostgreSQL知识库重叠40% ⚠️
│  └─ 建议：学习看培训，查询看知识库
│
├─ PostgreSQL_AI（48份）- 理论和架构
│  ├─ 与PostgreSQL_View重叠60% ⚠️
│  └─ 建议：理论看AI，技术看View
│
├─ PostgreSQL_View（200+份）- 技术和案例
│  ├─ 与PostgreSQL_AI重叠60% ⚠️
│  └─ 建议：技术看View，理论看AI
│
├─ PostgreSQL知识库（460+份）- 实战和工具
│  ├─ 与PostgreSQL培训重叠40% ⚠️
│  └─ 建议：实战看知识库，学习看培训
│
├─ MVCC-ACID-CAP（150+份）- 理论深度
│  ├─ 与DataBaseTheory分离 ⚠️
│  └─ 建议：理论看MVCC，实践看DataBase
│
└─ DataBaseTheory（55份）- PG18实践
   ├─ 与MVCC-ACID-CAP分离 ⚠️
   └─ 建议：实践看DataBase，理论看MVCC
```

**改进计划**：

- ✅ 已完成批判性评价
- 🔄 正在优化导航
- ⏳ 计划结构重组（6→3项目）

详见：[改进计划](./【顶层批判性评价】PostgreSQL_Modern项目全面对标与改进计划-2025-01.md)

---

## 💡 使用建议

### 建议1：根据紧急度选择

- 🔴 **紧急故障**：立即查故障诊断和Runbook
- 🟡 **重要但不紧急**：本周查迁移指南和技术对比
- 🟢 **学习提升**：长期按学习路径系统学习

### 建议2：避免迷失在重叠内容中

**AI主题**：

- 需要理论和架构 → PostgreSQL_AI
- 需要技术和案例 → PostgreSQL_View
- 需要实战代码 → PostgreSQL知识库

**培训主题**：

- 系统学习 → PostgreSQL培训
- 快速查询 → PostgreSQL知识库
- 实战案例 → PostgreSQL知识库

**理论主题**：

- 深度理论 → MVCC-ACID-CAP
- 实践验证 → DataBaseTheory

### 建议3：善用快速参考

- [SQL命令速查表](./PostgreSQL培训/00-项目文件/PostgreSQL_SQL命令速查表.md)
- [快速参考卡片集](./PostgreSQL培训/00-项目文件/PostgreSQL快速参考卡片集.md)
- [常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md)
- [术语表/概念词典/缩写表](./MVCC-ACID-CAP/00-项目文件/快速参考/)

---

## 📞 获取帮助

### 找不到想要的内容？

1. **搜索关键词**：在项目中搜索关键词
2. **查看索引**：
   - [PostgreSQL培训/文档索引](./PostgreSQL培训/00-项目文件/项目文档索引总览.md)
   - [PostgreSQL知识库/INDEX](./PostgreSQL/INDEX.md)
   - [PostgreSQL_AI/主题导航](./PostgreSQL_AI/README.md)
3. **提交Issue**：描述您要找什么，我们会补充

### 遇到问题？

1. **常见问题**：[常见问题手册](./PostgreSQL培训/00-项目文件/PostgreSQL常见问题快速查询手册.md)
2. **故障诊断**：[故障诊断手册](./DataBaseTheory/00-总览/PostgreSQL18故障诊断手册-2025-12-04.md)
3. **社区支持**：PostgreSQL中文社区、Stack Overflow

---

**创建时间**: 2025年1月
**维护者**: PostgreSQL Modern Team
**更新频率**: 持续更新

💡 **提示**：将本文档加入书签，随时快速定位所需内容！
