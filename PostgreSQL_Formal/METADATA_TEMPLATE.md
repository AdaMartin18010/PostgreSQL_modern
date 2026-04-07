# PostgreSQL_Formal 文档元数据标准

## 元数据格式规范

所有文档必须在文件开头包含以下 YAML 格式的元数据头：

```markdown
---
title: "文档标题"
version: "PostgreSQL 17"  # 或 18/19
version_number: "17.0"
release_date: "2024-09-26"
document_type: ["理论"|"实践"|"特性分析"|"操作指南"]
difficulty: ["入门"|"中级"|"高级"]
status: ["稳定"|"预览"|"实验性"]
language: "zh-CN"
created: "2026-04-07"
updated: "2026-04-07"
author: "PostgreSQL_Modern Team"
tags: ["tag1", "tag2", "tag3"]
related_documents:
  - "./related-doc-1.md"
  - "./related-doc-2.md"
prerequisites:
  - "前置知识1"
  - "前置知识2"
---
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 文档标题，简洁明了 |
| version | 是 | PostgreSQL 版本，如 "PostgreSQL 17" |
| version_number | 是 | 版本号，如 "17.0" |
| release_date | 是 | 版本发布日期，ISO 8601 格式 |
| document_type | 是 | 文档类型：理论/实践/特性分析/操作指南 |
| difficulty | 是 | 难度级别：入门/中级/高级 |
| status | 是 | 文档状态：稳定/预览/实验性 |
| language | 是 | 语言代码，中文为 "zh-CN" |
| created | 是 | 文档创建日期，ISO 8601 格式 |
| updated | 是 | 文档最后更新日期，ISO 8601 格式 |
| author | 是 | 文档作者或团队 |
| tags | 是 | 标签数组，3-8个相关标签 |
| related_documents | 否 | 相关文档路径列表 |
| prerequisites | 否 | 前置知识要求 |

## 标签建议

### 按主题分类

- **性能优化**: performance, vacuum, index, query-optimization
- **存储引擎**: storage, buffer-pool, wal, heap, toast
- **高可用**: high-availability, replication, failover, patroni
- **安全**: security, authentication, rbac, encryption
- **监控**: monitoring, observability, logging, tracing
- **SQL特性**: sql, json, merge, window-functions
- **运维**: dba, backup, upgrade, migration
- **扩展**: extension, pgvector, postgis

## 示例

### PG17 VACUUM 内存优化

```yaml
---
title: "PG17 VACUUM 内存优化深度分析"
version: "PostgreSQL 17"
version_number: "17.0"
release_date: "2024-09-26"
document_type: "特性分析"
difficulty: "高级"
status: "稳定"
language: "zh-CN"
created: "2026-04-07"
updated: "2026-04-07"
author: "PostgreSQL_Modern Team"
tags: ["性能优化", "VACUUM", "内存管理", "运维"]
related_documents:
  - "./17.07-Monitoring-Diagnostics-DEEP-V2.md"
  - "./17.08-Upgrade-Guide-DEEP-V2.md"
prerequisites:
  - "PostgreSQL VACUUM 基础概念"
  - "内存管理基础知识"
---
```

## 版本发布日期参考

| 版本 | 发布日期 |
|------|----------|
| PostgreSQL 17 | 2024-09-26 |
| PostgreSQL 18 | 2025-09-25 (预计) |
| PostgreSQL 19 | 2026-09 (预计) |
