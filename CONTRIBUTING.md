# 贡献指南

感谢您对PostgreSQL_Modern项目的关注！我们欢迎各种形式的贡献。

---

## 🎯 贡献方式

### 1. 报告问题

发现Bug或有改进建议？

- 搜索现有[Issues](https://github.com/AdaMartin18010/PostgreSQL_modern/issues)确认未被报告
- 创建新Issue，提供详细信息：
  - 问题描述
  - 复现步骤
  - 期望行为
  - 实际行为
  - 环境信息（PostgreSQL版本、OS等）

### 2. 提交代码

想要修复Bug或添加功能？

```bash
# 1. Fork项目
git clone https://github.com/yourusername/PostgreSQL_modern.git
cd PostgreSQL_modern

# 2. 创建分支
git checkout -b feature/your-feature-name

# 3. 进行修改
# ... 编写代码 ...

# 4. 运行测试
make test
make lint

# 5. 提交代码
git add .
git commit -m "feat: 添加XXX功能"

# 6. 推送分支
git push origin feature/your-feature-name

# 7. 创建Pull Request
```

### 3. 改进文档

文档永远有改进空间！

- 修正错别字
- 补充说明
- 添加示例
- 翻译文档

### 4. 分享经验

- 编写使用案例
- 分享最佳实践
- 制作教程视频
- 回答社区问题

---

## 📝 代码规范

### Python代码

```python
# 使用Black格式化
black scripts/*.py

# Flake8检查
flake8 scripts/*.py --max-line-length=100

# 类型提示
def function_name(param: str) -> int:
    """
    函数说明

    Args:
        param: 参数说明

    Returns:
        返回值说明
    """
    return 42
```

### SQL代码

```sql
-- 使用大写关键字
SELECT
    id,
    username,
    email
FROM users
WHERE status = 'active'
ORDER BY created_at DESC;

-- 添加注释
CREATE INDEX idx_users_email ON users(email);  -- 邮箱查询索引
```

### Markdown文档

```markdown
# 一级标题

## 二级标题

### 三级标题

- 列表项1
- 列表项2

**加粗文本**

`代码`

```sql
-- 代码块
SELECT * FROM users;
```

```

---

## 🧪 测试要求

### 单元测试

```python
# tests/test_new_feature.py

import pytest

def test_feature():
    """测试新功能"""
    result = your_function()
    assert result == expected_value
```

### 集成测试

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_health_check.py -v
```

### 性能测试

```bash
# 基准测试
make benchmark

# 验证性能无退化
python3 scripts/query-performance-tracker.py \
    --dbname testdb \
    --create-baseline
```

---

## 📋 Pull Request 检查清单

提交PR前请确认：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确
- [ ] 没有引入不必要的依赖
- [ ] 性能测试通过
- [ ] 代码已经格式化

---

## 💬 提交信息规范

使用[Conventional Commits](https://www.conventionalcommits.org/)规范：

```bash
# 格式
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关

### 示例

```bash
# 新功能
feat(scripts): 添加自动索引推荐工具

添加了基于查询统计的智能索引推荐功能：
- 分析查询模式
- 生成索引建议
- 评估性能收益

Closes #123

# Bug修复
fix(health-check): 修复连接数计算错误

修正了最大连接数获取逻辑

Fixes #456

# 文档
docs(README): 更新快速开始指南

补充了Docker部署步骤
```

---

## 🏗️ 项目结构

```
PostgreSQL_modern/
├── docs/                    # 技术文档
│   ├── 01-PostgreSQL18/    # PostgreSQL 18核心
│   ├── 02-AI-ML/           # AI/ML集成
│   ├── 04-Distributed/     # 分布式系统
│   └── 05-Production/      # 生产运维
├── scripts/                # 实用脚本
├── configs/                # 配置模板
├── DataBaseTheory/         # 数据库理论
├── tests/                  # 测试文件
├── .github/workflows/      # CI/CD
└── requirements.txt        # Python依赖
```

---

## 🎨 设计原则

### 1. 简洁性

- 代码简洁易读
- API设计直观
- 文档清晰明了

### 2. 性能

- 优化关键路径
- 避免不必要的操作
- 提供性能基准

### 3. 可靠性

- 完善的错误处理
- 充分的测试覆盖
- 详细的日志记录

### 4. 可维护性

- 模块化设计
- 清晰的注释
- 完整的文档

---

## 📚 开发环境搭建

### 1. 安装依赖

```bash
# Python依赖
make install

# 或手动安装
pip install -r requirements.txt
```

### 2. 启动开发环境

```bash
# 使用Docker
make up

# 检查状态
make health
```

### 3. 运行测试

```bash
# 所有测试
make test

# 代码检查
make lint

# 性能测试
make benchmark
```

---

## 🔍 代码审查

### Pull Request审查标准

#### 代码质量

- [ ] 代码清晰易读
- [ ] 遵循项目规范
- [ ] 无明显性能问题
- [ ] 错误处理完善

#### 测试

- [ ] 测试覆盖充分
- [ ] 边界情况考虑
- [ ] 性能无退化

#### 文档

- [ ] API文档完整
- [ ] 使用示例清晰
- [ ] 变更日志更新

#### 兼容性

- [ ] 向后兼容
- [ ] 跨平台支持
- [ ] 版本要求明确

---

## 🤝 社区准则

### 行为准则

1. **尊重他人**
   - 友好交流
   - 建设性反馈
   - 包容不同观点

2. **专业态度**
   - 关注技术本身
   - 避免人身攻击
   - 保持开放心态

3. **积极参与**
   - 分享知识
   - 帮助他人
   - 共同成长

---

## 📞 联系方式

### 获取帮助

- 📖 查阅[文档](Integrate)
- 🔍 搜索[Issues](https://github.com/AdaMartin18010/PostgreSQL_modern/issues)
- 💬 提问[Discussions](https://github.com/AdaMartin18010/PostgreSQL_modern/discussions)

### 报告安全问题

请通过私密方式报告安全漏洞，不要公开Issue。

---

## 🎓 学习资源

### 新贡献者

- [PostgreSQL官方文档](https://www.postgresql.org/docs/18/)
- [项目学习路径](LEARNING-PATH.md)
- [最佳实践指南](BEST-PRACTICES.md)

### 进阶开发

- [PostgreSQL内核](https://www.postgresql.org/docs/18/source.html)
- [项目架构设计](PROJECT-SUMMARY.md)
- [性能优化指南](Integrate/30-性能调优/PostgreSQL性能调优完整指南.md)

---

## 🎉 贡献者名单

感谢所有为项目做出贡献的开发者！

<!--
这里可以添加贡献者列表
或使用all-contributors工具自动生成
-->

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)。

贡献代码即表示您同意将代码以相同许可证开源。

---

**再次感谢您的贡献！让我们一起打造世界一流的PostgreSQL技术体系！** 🚀
