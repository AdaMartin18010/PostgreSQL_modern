# PostgreSQL_modern 项目工具集

本目录包含用于项目维护和质量保证的各种自动化工具。

---

## 📋 工具清单

### 1. 版本检查工具

#### `check_versions.sh`

**功能**：检查 PostgreSQL 和关键扩展的最新版本

**用法**：

```bash
# Linux/macOS
bash tools/check_versions.sh

# Windows (Git Bash)
bash tools/check_versions.sh
```

**检查内容**：

- PostgreSQL 最新版本
- pgvector 最新版本
- TimescaleDB 最新版本
- PostGIS 最新版本
- Citus 最新版本

**输出**：

- 当前追踪版本
- GitHub 最新版本
- 是否需要更新

---

### 2. 质量验证工具

#### `validate_quality.py`

**功能**：自动化执行项目质量验证

**用法**：

```bash
# 运行所有验证
python tools/validate_quality.py --all

# 仅检查外部链接
python tools/validate_quality.py --links

# 仅检查版本信息一致性
python tools/validate_quality.py --versions

# 仅检查内部链接
python tools/validate_quality.py --refs
```

**验证内容**：

1. **外部链接检查**（`--links`）
   - 扫描所有 Markdown 文件
   - 提取所有外部链接
   - 验证链接有效性
   - 生成失效链接报告

2. **版本信息检查**（`--versions`）
   - PostgreSQL 17 发布日期一致性
   - pgvector 版本一致性
   - TimescaleDB 版本一致性
   - PostGIS 版本一致性
   - Citus 版本一致性

3. **内部链接检查**（`--refs`）
   - 验证文档间相对链接
   - 检查引用的文件是否存在
   - 报告失效的内部链接

**输出**：

- 控制台彩色输出（实时进度）
- `QUALITY_VALIDATION_REPORT.md`（完整报告）

**依赖**：

```bash
pip install requests
```

---

#### `validate_quality.ps1`

**功能**：Windows PowerShell 版本的质量验证工具

**用法**：

```powershell
# 运行所有验证
.\tools\validate_quality.ps1 -All

# 仅检查外部链接
.\tools\validate_quality.ps1 -Links

# 仅检查版本信息
.\tools\validate_quality.ps1 -Versions

# 仅检查内部链接
.\tools\validate_quality.ps1 -Refs

# 显示帮助
.\tools\validate_quality.ps1 -Help
```

**特点**：

- 自动检查 Python 环境
- 自动安装缺失的依赖
- 彩色控制台输出
- 调用 Python 脚本执行验证

---

## 🚀 快速开始

### 场景1：检查项目链接有效性

```bash
# 1. 安装依赖（首次运行）
pip install requests

# 2. 运行链接检查
python tools/validate_quality.py --links

# 3. 查看报告
# 控制台会显示详细结果
# 失效链接会被列出，包括位置信息
```

### 场景2：验证版本信息一致性

```bash
# 检查所有版本信息是否统一
python tools/validate_quality.py --versions

# 如果发现不一致，会列出具体位置
```

### 场景3：完整质量验证

```bash
# 运行所有验证项目
python tools/validate_quality.py --all

# 或使用 PowerShell（Windows）
.\tools\validate_quality.ps1 -All

# 验证完成后查看报告
cat QUALITY_VALIDATION_REPORT.md
```

---

## 📊 验证标准

### 成功标准

- **外部链接有效率**：≥95%（至少50/52个链接有效）
- **版本信息一致性**：100%（所有文件版本信息统一）
- **内部链接有效性**：100%（所有内部链接可访问）

### 验证频率

- **每周**：运行完整验证
- **提交前**：运行快速验证（`--refs` + `--versions`）
- **发布前**：运行完整验证（`--all`）

---

## 🔧 工具开发

### 添加新的验证项

1. 在 `validate_quality.py` 中创建新的检查器类
2. 实现检查逻辑
3. 在 `main()` 函数中集成
4. 更新 README 文档

### 示例：添加 SQL 语法检查器

```python
class SQLChecker:
    """SQL 语法检查器"""
    
    def check_sql_files(self) -> Dict:
        """检查所有 SQL 文件的语法"""
        # 实现检查逻辑
        pass
```

---

## 📝 工具输出示例

### 链接检查输出

```text
============================================================
检查外部链接有效性
============================================================

ℹ️  找到 25 个文件，共 120 个链接（52 个唯一）
ℹ️  开始检查链接有效性...
检查 [52/52]: https://www.postgresql.org/docs/17/...

============================================================
链接检查结果
============================================================

总链接数（唯一）: 52
有效链接: 50 (96.2%)
失效链接: 2 (3.8%)

✅ 链接有效率 96.2% ≥ 95% ✅

============================================================
失效链接详情
============================================================

❌ https://example.com/404
  状态: 404
  位置:
    - GLOSSARY.md:45
    - README.md:120
```

### 版本检查输出

```text
============================================================
检查 PostgreSQL 17 发布日期
============================================================

✅ 所有文件的 PostgreSQL 17 发布日期统一为 '2024年9月26日'

============================================================
检查扩展版本一致性
============================================================

✅ pgvector: 版本一致 (0.8.0, v0.8.0)
✅ TimescaleDB: 版本一致 (2.17.2)
✅ PostGIS: 版本一致 (3.5.0)
✅ Citus: 版本一致 (12.1.4, v12.1.4)
```

---

## 🐛 故障排除

### 问题1：Python 未找到

**错误**：`'python' is not recognized as an internal or external command`

**解决**：

1. 安装 Python 3.8+ from <https://www.python.org/>
2. 确保 Python 添加到 PATH
3. 重启终端

### 问题2：requests 模块未安装

**错误**：`ModuleNotFoundError: No module named 'requests'`

**解决**：

```bash
pip install requests
```

### 问题3：链接检查超时

**错误**：大量链接显示 "Timeout"

**原因**：网络问题或请求过快

**解决**：

1. 检查网络连接
2. 增加脚本中的超时时间
3. 增加请求间隔（修改 `time.sleep(0.5)` 为更大值）

### 问题4：PowerShell 执行策略限制

**错误**：`cannot be loaded because running scripts is disabled`

**解决**：

```powershell
# 临时允许脚本执行（当前会话）
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 或永久允许（需要管理员权限）
Set-ExecutionPolicy RemoteSigned
```

---

## 📞 支持

如有问题或建议，请：

1. 查看本文档的故障排除部分
2. 查看 `QUALITY_VALIDATION_PLAN.md` 了解验证计划
3. 查看 `QUALITY_VALIDATION_QUICK_START.md` 了解快速入门

---

## 🔄 更新日志

### 2025-10-03

- ✅ 新增 `validate_quality.py` - 自动化质量验证工具
- ✅ 新增 `validate_quality.ps1` - PowerShell 版本
- ✅ 支持外部链接检查
- ✅ 支持版本信息一致性检查
- ✅ 支持内部链接检查
- ✅ 自动生成验证报告

### 2025-10-01

- ✅ 更新 `check_versions.sh` 扩展版本
- ✅ 添加 GitHub Actions 自动化

---

**维护者**：PostgreSQL_modern Project Team  
**最后更新**：2025年10月3日
