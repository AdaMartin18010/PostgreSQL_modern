# 贡献指南

感谢您对 PostgreSQL 现代教程项目的关注！本指南将帮助您了解如何为项目做出贡献。

## 目录

- [如何贡献](#如何贡献)
- [文档质量标准](#文档质量标准)
- [代码规范](#代码规范)
- [审校流程](#审校流程)
- [本地开发](#本地开发)
- [联系方式](#联系方式)

## 如何贡献

### 报告问题

发现错误或改进建议？请通过 [GitHub Issues](https://github.com/luyatshimbalanga/PostgreSQL_modern/issues) 提交：

- **搜索现有 Issue**：在创建新 Issue 前，请先搜索是否已有相关问题
- **使用正确模板**：选择合适的 Issue 模板（错误报告、文档改进、特性请求等）
- **提供详细信息**：
  - 问题的简要描述
  - 复现步骤
  - 期望行为与实际行为
  - 环境信息（操作系统、PostgreSQL 版本等）
  - 相关截图（如适用）

### 提交文档改进

1. **Fork 仓库**：点击右上角的 "Fork" 按钮
2. **克隆仓库**：
   ```bash
   git clone https://github.com/YOUR_USERNAME/PostgreSQL_modern.git
   cd PostgreSQL_modern
   ```
3. **创建分支**：
   ```bash
   git checkout -b improve-doc-section-name
   ```
4. **进行修改**：编辑相关 Markdown 文件
5. **本地预览**（推荐）：使用 Markdown 编辑器或 VS Code 预览
6. **提交更改**：
   ```bash
   git add .
   git commit -m "docs: 改进 XXX 章节的描述"
   git push origin improve-doc-section-name
   ```
7. **发起 Pull Request**：在 GitHub 上创建 PR，填写模板信息

### 贡献新内容

我们欢迎以下类型的新内容贡献：

- **新特性文档**：PostgreSQL 新版本特性的中文教程
- **实践案例**：真实场景的应用案例和最佳实践
- **性能测试**：基准测试和性能优化指南
- **工具推荐**：PostgreSQL 生态工具的介绍和使用教程
- **可视化内容**：图表、流程图、架构图等

贡献新内容前，请先通过 [Discussions](https://github.com/luyatshimbalanga/PostgreSQL_modern/discussions) 或 Issue 与维护者沟通，确保内容方向一致。

## 文档质量标准

为确保文档质量，所有贡献需符合以下标准：

### DEEP-V2 标准

- **D**etailed：内容详尽，涵盖原理、配置、实践
- **E**xample：每个概念配备可运行的示例代码
- **E**xercise：提供练习题巩固知识
- **P**roduction：面向生产环境的最佳实践
- **V**erified：经过实际测试验证
- **V**isualized：包含图表、流程图等可视化元素

### 内容要求

- [ ] 包含实际测试验证的代码示例
- [ ] 引用权威来源（官方文档、论文、技术规范）
- [ ] 提供版本兼容性说明
- [ ] 包含性能影响评估（如适用）
- [ ] 添加相关链接和延伸阅读

### 语言要求

- 使用简体中文
- 技术术语首次出现时附英文原文
- 保持语言简洁、准确

## 代码规范

### Markdown 格式

- 使用 ATX 标题样式（`#` 而非 `===`）
- 代码块需标注语言类型
- 表格使用标准 Markdown 表格语法
- 链接使用引用式或行内式，确保可访问

### 文件命名规范

- 使用英文小写字母
- 单词间用连字符 `-` 分隔
- 文件编号使用两位数字（如 `01-introduction.md`）

### 链接规范

- 内部链接使用相对路径
- 外部链接应包含协议（`https://`）
- 链接文本应具有描述性，避免 "点击这里"
- 定期检查链接有效性

## 审校流程

所有贡献将经过以下审校流程：

1. **自动检查**
   - Markdown 格式检查
   - 链接有效性验证
   - 拼写检查

2. **技术审校**
   - 内容准确性验证
   - 代码示例可运行性
   - 技术深度评估

3. **语言审校**
   - 中文表达准确性
   - 技术术语一致性
   - 可读性评估

4. **合并发布**
   - 维护者最终审核
   - 合并到主分支
   - 更新变更日志

## 本地开发

### 环境要求

- Python 3.8+
- VS Code（推荐）
- Git

### 设置开发环境

```bash
# 克隆仓库
git clone https://github.com/luyatshimbalanga/PostgreSQL_modern.git
cd PostgreSQL_modern

# 安装依赖（如有）
pip install -r requirements.txt

# 使用 VS Code 打开
code .
```

### 本地检查

在提交前，建议运行以下检查：

```bash
# 链接检查（如有工具）
python tools/link_checker.py

# 格式检查
markdownlint **/*.md
```

## 联系方式

- **技术讨论**：[GitHub Discussions](https://github.com/luyatshimbalanga/PostgreSQL_modern/discussions)
- **问题报告**：[GitHub Issues](https://github.com/luyatshimbalanga/PostgreSQL_modern/issues)
- **安全报告**：请直接联系维护者（请勿公开披露安全漏洞）

## 行为准则

参与本项目即表示您同意遵守我们的 [行为准则](./CODE_OF_CONDUCT.md)。请确保所有互动都保持尊重和专业。

---

再次感谢您的贡献！每一份努力都让这个项目变得更好。
