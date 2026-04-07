# 文档迁移指南

## 概述

本指南说明 PostgreSQL_Formal 项目的文档重构和归档流程。

## 归档结构

```
99-Archive/
├── deprecated-docs/        # 废弃文档（不再使用）
├── old-versions/           # 旧版本归档
│   ├── 01-Theory/         # 理论基础模块旧版本
│   ├── 02-Storage/        # 存储引擎模块旧版本
│   ├── 03-Query/          # 查询处理模块旧版本
│   ├── 04-Concurrency/    # 并发控制模块旧版本
│   ├── 05-Distributed/    # 分布式系统模块旧版本
│   ├── 06-FormalMethods/  # 形式化方法模块旧版本
│   ├── 07-PracticalCases/ # 实践案例模块旧版本
│   ├── 08-Performance/    # 性能优化模块旧版本
│   ├── 09-Tools/          # 工具生态模块旧版本
│   └── 10-Visualization/  # 可视化模块旧版本
├── migration-guide.md      # 本文件
└── version-mapping.md      # 版本映射表
```

## 归档规则

### 什么文档会被归档？

1. **非 DEEP-V2 版本** - 每个主题的基础版本
2. **重复内容** - 与 DEEP-V2 版本内容重叠的文档
3. **过时的 Analysis/Formal 版本** - 被 DEEP-V2 取代的文档

### 保留的文档类型

1. **DEEP-V2 版本** - 作为唯一活跃版本保留在原位置
2. **索引文件** - README.md, INDEX.md 等导航文件
3. **元数据文件** - 配置、说明、路线图等
4. **完成报告** - 历史里程碑记录

## 查找归档文档

### 按原路径查找

如果链接指向的文档已被归档，按以下规则查找：

| 原路径 | 归档路径 |
|--------|----------|
| `01-Theory/01.01-Relational-Algebra.md` | `99-Archive/old-versions/01-Theory/01.01-Relational-Algebra.md` |
| `02-Storage/02.01-BufferPool-Formal.md` | `99-Archive/old-versions/02-Storage/02.01-BufferPool-Formal.md` |

### 版本映射表

详见 `version-mapping.md` 文件，包含完整的文档映射关系。

## 如何恢复归档文档

如需恢复已归档的文档：

```bash
# 从归档目录复制回原位置
cp 99-Archive/old-versions/01-Theory/01.01-Relational-Algebra.md 01-Theory/

# 更新索引和链接
python tools/refactor-docs.py --update-links
```

## 归档时间线

| 日期 | 事件 |
|------|------|
| 2026-04-07 | 归档结构创建 |
| 2026-04-07 | P0 阶段归档开始（核心模块） |
| 2026-04-21 | P1 阶段归档（扩展模块） |
| 2026-05-05 | P2 阶段归档（应用模块） |
| 2026-05-12 | 归档完成，验证通过 |

## 常见问题

### Q: 为什么我的链接失效了？

A: 文档重构期间，非 DEEP-V2 版本被归档。请使用 DEEP-V2 版本的链接，或更新链接指向归档位置。

### Q: 如何知道哪个是最新版本？

A: 查看 `version-mapping.md` 或使用以下命令：

```bash
python tools/refactor-docs.py --find-latest "Relational-Algebra"
```

### Q: 归档文档还会更新吗？

A: 不会。归档文档是历史快照，不再维护。所有更新都在 DEEP-V2 版本上进行。

## 联系与支持

如有归档相关问题，请：

1. 查阅 `version-mapping.md` 了解文档位置
2. 运行 `python tools/refactor-docs.py --help` 获取工具帮助
3. 参考 `../REFACTORING_PLAN.md` 了解重构计划详情

---

*最后更新: 2026-04-07*
