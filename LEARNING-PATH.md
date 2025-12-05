# PostgreSQL 18 学习路径图

本文档提供从零基础到PostgreSQL专家的完整学习路径。

---

## 🎯 学习目标设定

### 角色定位

选择您的学习目标：

| 角色 | 学习时长 | 核心技能 | 就业方向 |
|------|---------|----------|----------|
| **应用开发者** | 2-4周 | SQL查询、ORM、性能优化 | 全栈开发、后端开发 |
| **数据库管理员** | 2-3月 | 运维、备份、性能调优 | DBA、运维工程师 |
| **架构师** | 3-6月 | 分布式、高可用、架构设计 | 技术架构师、CTO |
| **AI工程师** | 1-2月 | 向量数据库、RAG、ML集成 | AI工程师、ML工程师 |

---

## 📚 Level 0: 前置知识

### 必备基础

- [x] SQL基础（SELECT、INSERT、UPDATE、DELETE）
- [x] 数据库基本概念（表、索引、事务）
- [x] Linux基础命令
- [x] 基础编程（Python或任意语言）

### 学习资源

- **时间**: 1周
- **资源**: [SQL Tutorial](https://www.sqltutorial.org/)
- **练习**: [LeetCode SQL题库](https://leetcode.com/problemset/database/)

---

## 📚 Level 1: PostgreSQL入门（1-2周）

### 学习目标

- 理解PostgreSQL架构
- 掌握基本SQL操作
- 能够设计简单数据库

### 学习路径

#### Week 1: 安装与基础

**Day 1-2: 环境搭建**

```bash
# 1. 阅读安装指南
- docs/05-Production/17-Docker容器化完整指南.md

# 2. 使用Docker快速部署
cd configs
docker-compose up -d

# 3. 验证安装
psql -c "SELECT version();"
```

**Day 3-4: SQL基础**

```bash
# 学习材料
- docs/01-PostgreSQL18/19-高级SQL查询技巧.md
- docs/01-PostgreSQL18/20-实用SQL模式集锦.md

# 实践
- 创建数据库
- 创建表
- 插入数据
- 查询数据
```

**Day 5-7: 数据类型与约束**

```bash
# 学习材料
- docs/01-PostgreSQL18/14-数据类型深度解析.md
- docs/01-PostgreSQL18/39-外键与约束完全实战.md

# 实践
- 使用各种数据类型
- 添加主键、外键
- 使用CHECK约束
```

#### Week 2: 进阶查询

**Day 1-3: 高级SQL**

```bash
# 学习材料
- docs/01-PostgreSQL18/17-窗口函数完整实战.md
- docs/01-PostgreSQL18/38-CTE与递归查询完全指南.md

# 实践
- 窗口函数
- CTE查询
- 递归查询
```

**Day 4-7: 实战项目**

```bash
# 完成第一个项目
- DataBaseTheory/19-场景案例库/01-电商系统/

# 任务
- 设计电商数据库
- 实现核心查询
- 性能优化
```

### 检验标准

- [ ] 能独立设计3NF数据库
- [ ] 熟练使用JOIN查询
- [ ] 理解索引基本概念
- [ ] 完成1个实战项目

---

## 📚 Level 2: PostgreSQL进阶（3-4周）

### 学习目标

- 掌握性能优化技巧
- 理解事务与并发
- 会使用高级特性

### 学习路径

#### Week 1: 性能优化

**索引优化**

```bash
# 学习材料
- docs/01-PostgreSQL18/02-Skip-Scan深度解析.md
- DataBaseTheory/09-数据模型与规范化/05-索引与查询优化/17-索引选择算法.md

# 实践
- 创建各类索引
- 分析EXPLAIN结果
- 优化慢查询
```

**查询优化**

```bash
# 学习材料
- docs/01-PostgreSQL18/34-EXPLAIN执行计划完全解读.md
- docs/01-PostgreSQL18/35-慢查询优化实战案例.md

# 实践
- 分析10个慢查询案例
- 使用工具脚本
```

#### Week 2: 事务与并发

```bash
# 学习材料
- docs/01-PostgreSQL18/16-事务隔离级别深度解析.md
- docs/01-PostgreSQL18/18-并发控制深度解析.md

# 实践
- 理解MVCC
- 测试隔离级别
- 解决并发问题
```

#### Week 3: PostgreSQL 18新特性

```bash
# 学习材料
- docs/01-PostgreSQL18/01-异步IO深度解析.md
- docs/01-PostgreSQL18/09-Skip-Scan深度解析.md
- docs/01-PostgreSQL18/40-PostgreSQL18新特性总结.md

# 配置优化
- 启用异步I/O
- 配置Skip Scan
- 性能基准测试
```

#### Week 4: JSON与高级特性

```bash
# 学习材料
- docs/01-PostgreSQL18/12-JSONB高级应用指南.md
- docs/01-PostgreSQL18/37-JSON-JSONB完整实战.md

# 实践
- JSONB查询
- GIN索引
- 文档存储
```

### 检验标准

- [ ] 能分析EXPLAIN结果
- [ ] 理解MVCC原理
- [ ] 掌握10+优化技巧
- [ ] 完成性能优化项目

---

## 📚 Level 3: 生产运维（4-6周）

### 学习目标

- 掌握生产部署
- 会备份恢复
- 能监控告警

### 学习路径

#### Week 1-2: 高可用架构

```bash
# 学习材料
- docs/05-Production/07-Patroni高可用完整指南.md
- docs/05-Production/06-Kubernetes生产部署完整指南.md

# 实践
- 搭建主从复制
- 配置Patroni
- 故障转移测试
```

#### Week 3-4: 备份恢复

```bash
# 学习材料
- docs/05-Production/08-备份恢复完整实战.md
- docs/05-Production/15-灾难恢复演练手册.md

# 实践
- 配置pgBackRest
- 执行PITR恢复
- 灾难恢复演练
```

#### Week 5-6: 监控告警

```bash
# 学习材料
- docs/05-Production/12-监控告警完整方案.md
- configs/prometheus.yml
- configs/alerts/postgresql-alerts.yml

# 实践
- 部署Prometheus+Grafana
- 配置告警规则
- 处理告警事件
```

### 检验标准

- [ ] 能搭建HA架构
- [ ] 掌握备份恢复流程
- [ ] 会配置监控告警
- [ ] 通过灾难恢复演练

---

## 📚 Level 4: 分布式与架构（6-8周）

### 学习目标

- 掌握分布式架构
- 理解CAP理论
- 会设计大规模系统

### 学习路径

#### Week 1-2: Citus分布式

```bash
# 学习材料
- docs/04-Distributed/06-Citus分布式实战指南.md
- docs/04-Distributed/08-分布式事务实战.md

# 实践
- 部署Citus集群
- 数据分片
- 分布式查询
```

#### Week 3-4: 逻辑复制

```bash
# 学习材料
- docs/04-Distributed/07-逻辑复制分布式架构.md
- docs/04-Distributed/09-CDC变更数据捕获实战.md

# 实践
- 配置逻辑复制
- CDC实时同步
- 冲突解决
```

#### Week 5-6: 微服务架构

```bash
# 学习材料
- docs/04-Distributed/10-分布式锁实战.md
- DataBaseTheory/19-场景案例库/04-多租户SaaS系统/

# 实践
- 分布式锁
- 多租户设计
- 服务网格集成
```

#### Week 7-8: 架构设计

```bash
# 学习材料
- docs/05-Production/16-容量规划实战指南.md
- docs/05-Production/21-容量规划计算器.md

# 实践
- 容量规划
- 架构评审
- 压力测试
```

### 检验标准

- [ ] 能设计分布式架构
- [ ] 理解CAP权衡
- [ ] 掌握分片策略
- [ ] 完成大规模系统设计

---

## 📚 Level 5: AI/ML集成（4-6周）

### 学习目标

- 掌握向量数据库
- 会构建RAG系统
- 能集成AI模型

### 学习路径

#### Week 1-2: 向量数据库

```bash
# 学习材料
- docs/02-AI-ML/08-向量数据库实战指南.md
- docs/02-AI-ML/09-向量索引优化实战.md

# 实践
- 安装pgvector
- HNSW索引
- 向量相似搜索
```

#### Week 3-4: RAG系统

```bash
# 学习材料
- docs/02-AI-ML/10-RAG系统完整实现.md
- DataBaseTheory/21-AI知识库/07-LangChain深度集成完整指南.md

# 实践
- 构建RAG系统
- LangChain集成
- 性能优化
```

#### Week 5-6: 模型部署

```bash
# 学习材料
- docs/02-AI-ML/11-模型服务化部署.md
- docs/02-AI-ML/12-模型微调与优化.md

# 实践
- 模型量化
- 批量推理
- A/B测试
```

### 检验标准

- [ ] 能构建向量搜索系统
- [ ] 掌握RAG架构
- [ ] 会部署AI模型
- [ ] 完成AI应用项目

---

## 📚 Level 6: 专家进阶（持续学习）

### 学习目标

- 深入理解内核
- 贡献开源社区
- 成为技术专家

### 学习路径

#### 内核源码

```bash
# PostgreSQL源码
- WAL实现
- MVCC机制
- 查询优化器
- 存储引擎
```

#### 性能调优

```bash
# 学习材料
- docs/01-PostgreSQL18/08-性能调优实战指南.md
- docs/01-PostgreSQL18/21-SQL优化50条军规.md
- DataBaseTheory/23-性能基准测试/

# 实践
- TPC-H基准测试
- 生产环境优化
- 编写调优工具
```

#### 社区贡献

```bash
# 开源贡献
- 提交Bug报告
- 修复问题
- 编写扩展
- 分享经验
```

---

## 🎓 学习资源

### 官方文档

- [PostgreSQL官方文档](https://www.postgresql.org/docs/18/)
- [PostgreSQL Wiki](https://wiki.postgresql.org/)

### 在线课程

- Udemy: PostgreSQL从入门到精通
- Coursera: Database Management Essentials
- YouTube: Hussein Nasser的PostgreSQL系列

### 推荐书籍

- 《PostgreSQL 即学即用》
- 《PostgreSQL内核分析》
- 《高性能PostgreSQL》

### 社区资源

- [PostgreSQL中文社区](http://www.postgres.cn/)
- [Stack Overflow PostgreSQL标签](https://stackoverflow.com/questions/tagged/postgresql)
- [Reddit r/PostgreSQL](https://www.reddit.com/r/PostgreSQL/)

---

## 📊 学习进度跟踪

### 自我评估清单

#### 基础能力 (Level 1-2)

- [ ] 熟练使用psql
- [ ] 能设计规范化数据库
- [ ] 掌握SQL高级查询
- [ ] 理解索引原理
- [ ] 会分析EXPLAIN
- [ ] 完成3+实战项目

#### 进阶能力 (Level 3-4)

- [ ] 能部署HA架构
- [ ] 掌握备份恢复
- [ ] 会配置监控
- [ ] 理解分布式原理
- [ ] 能设计大规模系统
- [ ] 完成5+生产项目

#### 专家能力 (Level 5-6)

- [ ] 深入理解内核
- [ ] 掌握性能调优
- [ ] AI/ML集成经验
- [ ] 贡献开源社区
- [ ] 技术影响力
- [ ] 完成10+企业级项目

---

## 🎯 学习建议

### 学习方法

1. **理论+实践**: 看完文档立即动手实践
2. **项目驱动**: 通过项目串联知识点
3. **源码阅读**: 阅读优秀项目源码
4. **社区交流**: 参与讨论，分享经验
5. **持续学习**: 关注新特性，不断精进

### 避免的坑

- ❌ 只看不练
- ❌ 跳跃式学习
- ❌ 忽视基础
- ❌ 不做笔记
- ❌ 孤立学习

### 学习工具

- **笔记**: Notion、Obsidian
- **练习**: Docker本地环境
- **监控**: Grafana仪表板
- **工具**: 本项目的20个脚本

---

## 💼 职业发展

### 岗位要求

**初级DBA (0-2年)**

- 基础SQL
- 备份恢复
- 日常维护

**中级DBA (2-5年)**

- 性能优化
- 高可用架构
- 故障排查

**高级DBA (5+年)**

- 架构设计
- 容量规划
- 团队管理

**PostgreSQL专家**

- 内核优化
- 开源贡献
- 技术布道

### 薪资参考

- 初级: 10-20K
- 中级: 20-35K
- 高级: 35-60K
- 专家: 60K+

---

## 🎉 结语

PostgreSQL学习是一个持续的过程，建议：

1. **循序渐进**: 从基础到高级，稳扎稳打
2. **项目实战**: 通过项目巩固知识
3. **持续更新**: 关注PostgreSQL新版本
4. **社区分享**: 分享经验，帮助他人
5. **保持热情**: 享受学习和成长的过程

---

**祝您学习愉快，成为PostgreSQL专家！** 🚀
