# PostgreSQL 19 跟踪来源列表

本文件列出了跟踪 PostgreSQL 19 新特性进展的权威信息来源。

---

## 1. 官方来源

### 1.1 PostgreSQL 官方网站

| 来源 | URL | 说明 | 更新频率 |
|------|-----|------|----------|
| 官方路线图 | <https://www.postgresql.org/developer/roadmap/> | 发布计划和路线图 | 不定期 |
| Beta 信息 | <https://www.postgresql.org/developer/beta/> | Beta 测试信息 | 每版本更新 |
| 发布说明 (WIP) | <https://www.postgresql.org/docs/devel/release.html> | 开发版本发布说明 | 持续更新 |
| 官方博客 | <https://www.postgresql.org/blog/> | 官方新闻和公告 | 不定期 |

### 1.2 CommitFest

| 来源 | URL | 说明 | 更新频率 |
|------|-----|------|----------|
| CommitFest 主页 | <https://commitfest.postgresql.org/> | 所有 CommitFest 汇总 | 实时 |
| CF 2025-07 (PG19-1) | <https://commitfest.postgresql.org/53/> | 第一阶段 CommitFest | 已关闭 |
| CF 2025-09 (PG19-2) | <https://commitfest.postgresql.org/54/> | 第二阶段 CommitFest | 已关闭 |
| CF 2025-11 (PG19-3) | <https://commitfest.postgresql.org/55/> | 第三阶段 CommitFest | 已关闭 |
| CF 2026-01 (PG19-4) | <https://commitfest.postgresql.org/56/> | 第四阶段 CommitFest | 已关闭 |
| CF 2026-03 (PG19-5) | <https://commitfest.postgresql.org/57/> | 第五阶段 CommitFest | 进行中 |

---

## 2. 邮件列表

### 2.1 主要开发列表

| 列表名称 | 地址 | 说明 | 订阅方式 |
|----------|------|------|----------|
| pgsql-hackers | <pgsql-hackers@lists.postgresql.org> | 核心开发者讨论 | 邮件订阅 |
| pgsql-committers | <pgsql-committers@lists.postgresql.org> | 提交日志 | 邮件订阅 |
| pgsql-announce | <pgsql-announce@lists.postgresql.org> | 发布公告 | 邮件订阅 |

### 2.2 邮件列表归档

| 来源 | URL | 说明 |
|------|-----|------|
| PostgreSQL 邮件归档 | <https://www.postgresql.org/list/> | 所有邮件列表归档 |
| PostgresHackers 搜索 | <https://www.postgresql.org/search/?m=1&l=pgsql-hackers> | Hackers 列表搜索 |
| PG Archives | <https://www.postgresql-archive.org/> | 第三方归档 |

---

## 3. 核心开发者博客

### 3.1 个人博客 (定期更新)

| 作者 | 博客地址 | 主要内容 | 更新频率 |
|------|----------|----------|----------|
| Hubert Lubaczewski (depesz) | <https://www.depesz.com> | "Waiting for PostgreSQL" 系列 | 每周 |
| Tomas Vondra | <https://tvondra.blogspot.com/> | 性能优化、新特性 | 不定期 |
| Robert Haas | <http://rhaas.blogspot.com/> | 开发深度分析 | 不定期 |
| Bruce Momjian | <https://momjian.us/main/blogs/pgblog.html> | PG 内部原理 | 不定期 |
| Peter Eisentraut | <https://peter.eisentraut.org/> | SQL 标准、开发流程 | 不定期 |

### 3.2 公司技术博客

| 来源 | 地址 | 主要内容 | 更新频率 |
|------|------|----------|----------|
| Postgres Professional | <https://postgrespro.com/blog> | CommitFest 详细回顾 | 每月 |
| EDB Blog | <https://www.enterprisedb.com/blog> | 企业级特性分析 | 每周 |
| Cybertec | <https://www.cybertec-postgresql.com/en/blog/> | 技术深度文章 | 每周 |
| 2ndQuadrant | <https://www.2ndquadrant.com/en/blog/> | 高级特性 | 每周 |

---

## 4. 中文社区来源

### 4.1 中文博客和资讯

| 来源 | 地址 | 说明 | 更新频率 |
|------|------|------|----------|
| IvorySQL 博客 | <https://www.cnblogs.com/ivorysql/> | 中文 PG 动态 | 每日 |
| PostgreSQL 中文社区 | <http://www.postgres.cn/> | 中文官方社区 | 不定期 |
| 开源中国 PG 专区 | <https://www.oschina.net/p/postgresql> | 中文新闻 | 不定期 |

---

## 5. 社交媒体和新闻

### 5.1 Twitter/X 账号

| 账号 | 说明 | 关注度 |
|------|------|--------|
| @PostgreSQL | 官方账号 | 高 |
| @postgresweekly | Postgres Weekly 新闻 | 高 |
| @pgconf | PGConf 系列会议 | 中 |

### 5.2 新闻聚合

| 来源 | 地址 | 说明 |
|------|------|------|
| Postgres Weekly | <https://postgresweekly.com/> | 每周 PG 新闻摘要 |
| Planet PostgreSQL | <https://planet.postgresql.org/> | 博客聚合 |
| PostgreSQL Weekly News | <https://wiki.postgresql.org/wiki/WeeklyNews> | 社区周报 |

---

## 6. 代码仓库

### 6.1 官方 Git 仓库

| 来源 | URL | 说明 |
|------|-----|------|
| 官方 Git | <https://git.postgresql.org/gitweb/> | 官方 Git 仓库 |
| GitHub 镜像 | <https://github.com/postgres/postgres> | GitHub 镜像 |
| Commit 历史 | <https://git.postgresql.org/gitweb/?p=postgresql.git> | 提交历史 |

### 6.2 补丁审查

| 来源 | URL | 说明 |
|------|-----|------|
| CF Bot | <https://commitfest.postgresql.org/> | 自动补丁测试 |
| Patchwork | <https://patchwork.postgresql.org/> | 补丁管理 |

---

## 7. 会议和活动

### 7.1 主要会议

| 会议 | 时间 | 地址 | 说明 |
|------|------|------|------|
| PGConf.dev 2026 | 2026-05 | <https://www.pgconf.dev/> | 核心开发者会议 |
| POSETTE 2026 | 2026-04 | <https://posetteconf.com/> | 线上 PG 会议 |
| PGDay | 各地 | <https://www.postgresql.org/about/events/> | 各地 PGDay |

### 7.2 会议日程

| 来源 | URL | 说明 |
|------|-----|------|
| PG Events | <https://www.postgresql.org/about/events/> | 官方活动日历 |
| Postgres Events | <https://postgresconf.org/> | PostgresConf 系列 |

---

## 8. 文档和 Wiki

### 8.1 官方文档

| 来源 | URL | 说明 |
|------|-----|------|
| 开发文档 | <https://www.postgresql.org/docs/devel/> | 开发版本文档 |
| 开发者 FAQ | <https://wiki.postgresql.org/wiki/Developer_FAQ> | 开发者常见问题 |
| 开发 wiki | <https://wiki.postgresql.org/wiki/Development_information> | 开发信息 |

### 8.2 特性信息

| 来源 | URL | 说明 |
|------|-----|------|
| TODO 列表 | <https://wiki.postgresql.org/wiki/Todo> | 待办特性列表 |
| 正在进行的补丁 | <https://wiki.postgresql.org/wiki/Current_pending_patches> | 待审查补丁 |

---

## 9. 推荐 RSS/Atom 订阅

```
# 官方来源
https://www.postgresql.org/blog/feed.xml
https://www.postgresql.org/news.rss

# 博客聚合
https://planet.postgresql.org/rss20.xml

# 新闻
https://postgresweekly.com/rss
```

---

## 10. 定期检查清单

### 每周检查

- [ ] depesz.com "Waiting for PostgreSQL 19" 更新
- [ ] Postgres Professional CommitFest 回顾
- [ ] Postgres Weekly 周报

### 每月检查

- [ ] CommitFest 状态更新
- [ ] 核心开发者博客汇总
- [ ] 邮件列表热点话题

### 里程碑检查

- [ ] Feature Freeze 前特性确认
- [ ] Beta 版本发布
- [ ] RC 版本发布
- [ ] GA 版本发布

---

## 更新日志

- **2026-04-07**: 初始来源列表创建

---

*最后更新: 2026-04-07*
*维护者: PostgreSQL 中文社区*
