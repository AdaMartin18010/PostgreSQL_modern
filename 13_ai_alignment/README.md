## PostgreSQL 18 · AI 时代对齐与论证（Alignment & Argumentation）

本目录汇总基于 `ai_view.md` 的知识归纳，全面对齐 PostgreSQL 18 的最新特性与本项目主题，输出面向落地
的"论证文件 + 改进计划"。

### 🚀 快速导航

- **第一次访问？** 查看 [`QUICK_NAVIGATION.md`](QUICK_NAVIGATION.md) - 快速找到你需要的内容
- **需要技术选型？** 查看 [`07_知识矩阵总览.md`](07_知识矩阵总览.md) - 技术选型对比与决策框架
- **需要深度论证？** 查看各主题文件（01-05）- 论证分析、场景分析、决策思路、思维导图、知识矩阵

### 目录

- 00 论证总览：核心观点、证据、边界与对项目的影响
- 01 向量与混合搜索：pgvector + RRF（融合全文/语义）
- 02 AI 自治：自治优化与智能运维（pg_ai/自动调优）
- 03 Serverless 与分支：Neon/Supabase 的数据 Git 能力
- 04 多模一体化：JSONB/时序/图/向量一体化治理与查询
- 05 合规与可信：AI Act/行级主权/动态脱敏/审计
- 06 改进与完善计划：对齐本项目目录与验证路径
- 07 知识矩阵总览：整合所有主题的技术选型对比与决策框架

参考映射（示例）：

- 向量/混合搜索 → `05_ai_vector/`、`08_ecosystem_cases/`
- 事务/存储/访问 → `02_transactions/`、`03_storage_access/`
- 部署与运维 → `09_deployment_ops/`、`04_modern_features/`

更多：索引参见 `13_ai_alignment/INDEX.md`
