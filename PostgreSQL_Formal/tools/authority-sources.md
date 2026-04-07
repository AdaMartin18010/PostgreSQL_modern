# PostgreSQL 权威来源监控列表

本文档维护 PostgreSQL_Formal 项目引用的所有权威来源链接，并定义监控频率和更新检查流程。

**最后更新**: 2026-04-07
**版本**: 1.0
**维护者**: PostgreSQL_Formal 文档维护团队

---

## 1. 官方文档链接

### 1.1 核心文档

| 资源 | URL | 检查频率 | 上次检查 | 状态 | 备注 |
|------|-----|----------|----------|------|------|
| PostgreSQL 官网 | <https://www.postgresql.org/> | 每月 | 2026-04-07 | ✅ | 主入口 |
| 文档首页 | <https://www.postgresql.org/docs/> | 每月 | 2026-04-07 | ✅ | 版本选择器 |
| PG17 文档 | <https://www.postgresql.org/docs/17/> | 每季度 | 2026-04-07 | ✅ | 当前稳定版 |
| PG18 文档 | <https://www.postgresql.org/docs/18/> | 每月 | 2026-04-07 | ✅ | 开发版 |
| PG16 文档 | <https://www.postgresql.org/docs/16/> | 每季度 | 2026-04-07 | ✅ | 支持版本 |
| PG15 文档 | <https://www.postgresql.org/docs/15/> | 每季度 | 2026-04-07 | ✅ | 支持版本 |

### 1.2 特定主题文档

| 资源 | URL | 检查频率 | 上次检查 | 状态 | 备注 |
|------|-----|----------|----------|------|------|
| SQL 命令 | <https://www.postgresql.org/docs/17/sql-commands.html> | 每季度 | 2026-04-07 | ✅ | 命令参考 |
| 配置参数 | <https://www.postgresql.org/docs/17/runtime-config.html> | 每季度 | 2026-04-07 | ✅ | GUC 参数 |
| 数据类型 | <https://www.postgresql.org/docs/17/datatype.html> | 每季度 | 2026-04-07 | ✅ | 类型系统 |
| 函数和操作符 | <https://www.postgresql.org/docs/17/functions.html> | 每季度 | 2026-04-07 | ✅ | 函数参考 |
| 索引类型 | <https://www.postgresql.org/docs/17/indexes-types.html> | 每季度 | 2026-04-07 | ✅ | 索引文档 |
| 并发控制 | <https://www.postgresql.org/docs/17/mvcc.html> | 每季度 | 2026-04-07 | ✅ | MVCC |
| 性能建议 | <https://www.postgresql.org/docs/17/performance-tips.html> | 每季度 | 2026-04-07 | ✅ | 调优指南 |

---

## 2. Release Notes 链接

### 2.1 主要版本

| 版本 | Release Notes URL | 发布日期 | EOL 日期 | 检查频率 | 状态 |
|------|-------------------|----------|----------|----------|------|
| PostgreSQL 17 | <https://www.postgresql.org/docs/17/release-17.html> | 2024-09-26 | 2029-11-08 | 每季度 | ✅ |
| PostgreSQL 16 | <https://www.postgresql.org/docs/16/release-16.html> | 2023-09-14 | 2028-11-09 | 每季度 | ✅ |
| PostgreSQL 15 | <https://www.postgresql.org/docs/15/release-15.html> | 2022-10-13 | 2027-11-11 | 每季度 | ✅ |
| PostgreSQL 14 | <https://www.postgresql.org/docs/14/release-14.html> | 2021-09-30 | 2026-11-12 | 每季度 | ✅ |
| PostgreSQL 13 | <https://www.postgresql.org/docs/13/release-13.html> | 2020-09-24 | 2025-11-13 | 每季度 | ⚠️ |
| PostgreSQL 12 | <https://www.postgresql.org/docs/12/release-12.html> | 2019-10-03 | 2024-11-21 | 每季度 | ❌ EOL |

### 2.2 小版本 Release Notes

| 版本 | URL 模式 | 检查频率 | 备注 |
|------|----------|----------|------|
| PG17 小版本 | <https://www.postgresql.org/docs/17/release-{X}.html> | 每月 | X = 17.1, 17.2... |
| PG18 小版本 | <https://www.postgresql.org/docs/18/release-{X}.html> | 每月 | X = 18.0, 18.1... |

### 2.3 预发布版本

| 类型 | URL | 检查频率 | 状态 |
|------|-----|----------|------|
| PG18 Beta | <https://www.postgresql.org/docs/18/> | 每周 | 开发中 |
| PG18 RC | <https://www.postgresql.org/docs/18/> | 每周 | 待发布 |
| 开发文档 | <https://www.postgresql.org/docs/devel/> | 每周 | 最新 |

---

## 3. 社区资源

### 3.1 邮件列表

| 列表 | URL | 检查频率 | 用途 | 状态 |
|------|-----|----------|------|------|
| pgsql-announce | <https://www.postgresql.org/list/pgsql-announce/> | 每月 | 发布公告 | ✅ |
| pgsql-hackers | <https://www.postgresql.org/list/pgsql-hackers/> | 每月 | 开发讨论 | ✅ |
| pgsql-general | <https://www.postgresql.org/list/pgsql-general/> | 每季度 | 通用讨论 | ✅ |
| pgsql-docs | <https://www.postgresql.org/list/pgsql-docs/> | 每季度 | 文档讨论 | ✅ |

### 3.2 CommitFest

| 资源 | URL | 检查频率 | 用途 | 状态 |
|------|-----|----------|------|------|
| CommitFest 首页 | <https://commitfest.postgresql.org/> | 每月 | 补丁审核 | ✅ |
| 当前 CommitFest | <https://commitfest.postgresql.org/{id}/> | 每周 | 活跃补丁 | ✅ |

### 3.3 源代码仓库

| 资源 | URL | 检查频率 | 用途 | 状态 |
|------|-----|----------|------|------|
| Git 仓库 | <https://git.postgresql.org/gitweb/> | 每月 | 源码浏览 | ✅ |
| GitHub 镜像 | <https://github.com/postgres/postgres> | 每月 | 镜像仓库 | ✅ |

---

## 4. 扩展和工具

### 4.1 核心扩展

| 扩展 | 官方文档 | 检查频率 | 状态 |
|------|----------|----------|------|
| pgvector | <https://github.com/pgvector/pgvector> | 每月 | ✅ |
| PostGIS | <https://postgis.net/documentation/> | 每季度 | ✅ |
| pg_stat_statements | <https://www.postgresql.org/docs/17/pgstatstatements.html> | 每季度 | ✅ |
| pgcrypto | <https://www.postgresql.org/docs/17/pgcrypto.html> | 每季度 | ✅ |
| uuid-ossp | <https://www.postgresql.org/docs/17/uuid-ossp.html> | 每季度 | ✅ |

### 4.2 外部工具

| 工具 | URL | 检查频率 | 状态 |
|------|-----|----------|------|
| pgAdmin | <https://www.pgadmin.org/docs/> | 每季度 | ✅ |
| psql | <https://www.postgresql.org/docs/17/app-psql.html> | 每季度 | ✅ |
| pg_dump | <https://www.postgresql.org/docs/17/app-pgdump.html> | 每季度 | ✅ |
| pg_basebackup | <https://www.postgresql.org/docs/17/app-pgbasebackup.html> | 每季度 | ✅ |
| pg_upgrade | <https://www.postgresql.org/docs/17/pgupgrade.html> | 每季度 | ✅ |

### 4.3 云原生工具

| 工具 | URL | 检查频率 | 状态 |
|------|-----|----------|------|
| CloudNativePG | <https://cloudnative-pg.io/documentation/> | 每月 | ✅ |
| Patroni | <https://patroni.readthedocs.io/> | 每季度 | ✅ |
| pgBackRest | <https://pgbackrest.org/documentation.html> | 每季度 | ✅ |

---

## 5. 版本和发布信息

### 5.1 版本策略

| 资源 | URL | 检查频率 | 状态 |
|------|-----|----------|------|
| 版本策略 | <https://www.postgresql.org/support/versioning/> | 每季度 | ✅ |
| 发布计划 | <https://www.postgresql.org/developer/roadmap/> | 每季度 | ✅ |
| 安全信息 | <https://www.postgresql.org/support/security/> | 每月 | ✅ |

### 5.2 下载页面

| 资源 | URL | 检查频率 | 状态 |
|------|-----|----------|------|
| 源码下载 | <https://www.postgresql.org/ftp/source/> | 每月 | ✅ |
| 二进制下载 | <https://www.postgresql.org/download/> | 每月 | ✅ |

---

## 6. 检查频率设置

### 6.1 频率定义

| 频率 | 说明 | 适用资源 |
|------|------|----------|
| 每周 | 每 7 天检查一次 | 开发中版本、CommitFest |
| 每月 | 每 30 天检查一次 | 活跃维护文档、安全公告 |
| 每季度 | 每 90 天检查一次 | 稳定版本文档、EOL 信息 |
| 每年 | 每 365 天检查一次 | 历史版本、归档资源 |

### 6.2 检查日历 (2026)

| 季度 | 开始日期 | 结束日期 | 主要任务 |
|------|----------|----------|----------|
| Q1 | 2026-01-01 | 2026-03-31 | 年度检查、PG18 预览 |
| Q2 | 2026-04-01 | 2026-06-30 | 常规检查、PG18 Beta |
| Q3 | 2026-07-01 | 2026-09-30 | 常规检查、PG18 RC |
| Q4 | 2026-10-01 | 2026-12-31 | 年度检查、PG18 发布 |

---

## 7. 监控自动化

### 7.1 建议工具

| 工具 | 用途 | 配置 |
|------|------|------|
| `link_verifier.py` | 链接有效性检查 | 每周运行 |
| RSS 订阅 | 新版本通知 | pg-announce |
| 邮件列表 | 开发动态 | pgsql-hackers |

### 7.2 RSS/Atom 订阅源

| 源 | URL | 用途 |
|----|-----|------|
| PostgreSQL 新闻 | <https://www.postgresql.org/news.xml> | 官方新闻 |
| 发布通知 | <https://www.postgresql.org/versions.rss> | 版本更新 |

---

## 8. 历史变更记录

| 日期 | 版本 | 变更内容 | 维护者 |
|------|------|----------|--------|
| 2026-04-07 | 1.0 | 初始创建 | 文档维护团队 |
| - | - | - | - |

---

## 9. 相关文档

- [季度对齐检查清单](./quarterly-alignment-checklist.md)
- [季度对齐报告模板](../reports/quarterly-alignment-report-template.md)
- [AUTHORITY_CONTENT_INDEX.md](../AUTHORITY_CONTENT_INDEX.md)

---

## 10. 附录

### A. URL 验证脚本

```bash
#!/bin/bash
# 验证所有链接有效性
# 保存为: validate_authority_links.sh

URLS=(
  "https://www.postgresql.org/"
  "https://www.postgresql.org/docs/17/"
  "https://www.postgresql.org/docs/18/"
  # 添加更多 URL...
)

for url in "${URLS[@]}"; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  echo "[$status] $url"
done
```

### B. 检查清单模板

```markdown
## YYYY-MM-DD 月度检查

- [ ] 官方网站可访问
- [ ] PG17 文档可访问
- [ ] PG18 文档可访问
- [ ] Release Notes 可访问
- [ ] 无新增 404 错误
- [ ] 安全公告已查看
- [ ] CommitFest 状态已更新

检查人: [姓名]
备注: [如有]
```

---

**注意**: 本列表应每季度审查一次，确保链接有效性和监控频率的合理性。
