# PostgreSQL_Formal 链接检查自动化机制

本文档介绍 PostgreSQL_Formal 项目的链接检查自动化机制，包括脚本使用、报告解读和自动化配置。

---

## 📁 文件结构

```
PostgreSQL_Formal/
├── tools/
│   ├── monthly-link-check.sh    # 链接检查脚本（主程序）
│   └── LINK_CHECK_README.md     # 本说明文档
├── reports/
│   ├── TEMPLATE.md              # 报告模板
│   ├── monthly-link-report-YYYY-MM.md    # 月度报告（自动生成）
│   └── monthly-link-summary-YYYY-MM.txt  # 简要摘要（自动生成）
└── .github/
    └── workflows/
        └── monthly-link-check.yml  # GitHub Actions 工作流
```

---

## 🚀 快速开始

### 本地运行

```bash
# 进入工具目录
cd PostgreSQL_Formal/tools

# 运行链接检查
./monthly-link-check.sh

# 查看帮助
./monthly-link-check.sh --help
```

### 常用选项

```bash
# 指定输出目录
./monthly-link-check.sh -o ./custom-reports

# 静默模式（只输出错误）
./monthly-link-check.sh --quiet

# 查看版本
./monthly-link-check.sh --version
```

---

## 📊 报告说明

### 报告位置

每月运行后会生成以下文件：

| 文件 | 说明 |
|------|------|
| `reports/monthly-link-report-YYYY-MM.md` | 详细报告（Markdown 格式） |
| `reports/monthly-link-summary-YYYY-MM.txt` | 简要摘要（纯文本） |

### 报告内容

1. **统计信息** - 总链接数、有效/失效链接数量
2. **健康度评分** - 百分比评分和状态评级
3. **失效链接详情** - 需要修复的具体链接列表
4. **警告链接详情** - 可能有问题但非失效的链接
5. **待修复文件列表** - 按问题数量排序的文件列表
6. **修复建议** - 常见问题和修复步骤

### 健康度评级

| 评分 | 评级 | 说明 |
|------|------|------|
| 95-100% | 🟢 优秀 | 链接状态良好，无需处理 |
| 90-94% | 🟡 良好 | 少量问题，建议修复 |
| 80-89% | 🟠 一般 | 需要关注并修复 |
| <80% | 🔴 需修复 | 问题严重，需要立即处理 |

---

## ⚙️ 自动化配置

### GitHub Actions 自动运行

工作流配置文件: `.github/workflows/monthly-link-check.yml`

**触发条件:**

1. **定时运行** - 每月 1 日 UTC 02:00 自动运行
2. **手动触发** - 通过 Actions 页面手动运行
3. **PR 触发** - 当 PR 修改 Markdown 文件时自动检查

**工作流功能:**

- ✅ 自动运行链接检查
- ✅ 生成并上传报告产物
- ✅ 发现失效链接时自动创建/更新 Issue
- ✅ PR 检查时添加评论

### 手动触发工作流

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Monthly Link Check" 工作流
3. 点击 "Run workflow"
4. 选择是否创建 Issue
5. 点击 "Run workflow"

---

## 🔧 故障排除

### 脚本无法运行

**问题:** Permission denied

**解决:**

```bash
chmod +x tools/monthly-link-check.sh
```

**问题:** 找不到 bash（Windows 环境）

**解决:**

- 使用 Git Bash 或 WSL
- 或在 Linux/macOS 环境下运行

### 检查时间过长

**原因:** 项目文件较多（262+ 个 Markdown 文件）

**建议:**

- 使用 `--quiet` 模式减少输出
- 在 CI 环境中运行而非本地

### 锚点检测不准确

**原因:** 中文锚点的特殊字符处理

**解决:**

- 检查报告中的"建议修复"列
- 手动验证锚点是否正确

---

## 📝 维护指南

### 添加新的排除目录

编辑 `tools/monthly-link-check.sh`，修改 `run_link_check` 函数中的 find 命令：

```bash
local md_files=$(find "$PROJECT_DIR" -type f -name "*.md" \
    ! -path "*/node_modules/*" \
    ! -path "*/.link_fix_backup/*" \
    ! -path "*/your-new-dir/*" | sort)
```

### 修改报告格式

编辑 `generate_report` 函数，自定义报告模板。

### 调整定时计划

编辑 `.github/workflows/monthly-link-check.yml` 中的 cron 表达式：

```yaml
on:
  schedule:
    # 分 时 日 月 周
    - cron: '0 2 1 * *'  # 每月 1 日 02:00 UTC
```

---

## 📈 链接检查覆盖范围

### 支持的链接类型

| 类型 | 示例 | 检查方式 |
|------|------|----------|
| 页内锚点 | `#标题` | ✅ 验证锚点存在 |
| 文件 + 锚点 | `file.md#锚点` | ✅ 验证文件和锚点 |
| Markdown 文件 | `./path/file.md` | ✅ 验证文件存在 |
| 相对路径文件 | `../images/pic.png` | ✅ 验证文件存在 |
| 外部链接 | `https://...` | ⚪ 仅统计 |

### 排除的目录

以下目录的内容不会纳入检查：

- `node_modules/` - 依赖目录
- `.link_fix_backup/` - 链接修复备份
- `.link_fix_backup_2026/` - 链接修复备份
- `.authority_source_backup/` - 权威源备份

---

## 🤝 贡献指南

### 报告问题

发现链接检查脚本的 bug 或需要新功能？

1. 检查现有 Issue 是否已存在
2. 创建新 Issue，使用 `link-check` 标签
3. 提供复现步骤和错误信息

### 改进脚本

1. Fork 仓库
2. 创建功能分支
3. 修改 `tools/monthly-link-check.sh`
4. 提交 PR 并描述改动

---

## 📚 相关文档

- [报告模板](../reports/TEMPLATE.md) - 报告格式参考
- [LINK_VERIFICATION_REPORT.md](../LINK_VERIFICATION_REPORT.md) - 完整链接验证报告
- [LINK_FIX_REPORT.md](../LINK_FIX_REPORT.md) - 链接修复历史记录

---

## 🔄 更新日志

### v1.0.0 (2026-04-07)

- ✅ 初始版本发布
- ✅ 支持 Markdown 文件扫描
- ✅ 支持内部链接和锚点检查
- ✅ 生成详细 Markdown 报告
- ✅ GitHub Actions 自动运行
- ✅ 自动 Issue 创建

---

## 📧 联系

如有问题或建议，请通过以下方式联系：

- 创建 GitHub Issue
- 查看项目文档首页

---

*最后更新: 2026-04-07*
