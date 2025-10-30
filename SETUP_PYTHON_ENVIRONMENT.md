# Python 环境安装与配置指南

## 问题说明

在 `tests/scripts/run_single_test.py` 第 12 行出现错误:

```text
Import "psycopg2" could not be resolved from source
```

这是因为 Python 包 `psycopg2-binary` 未安装在您的系统中。

---

## 解决方案

### 方案 1: 安装 Python（如果未安装）

#### Windows 系统推荐方法

**选项 A: 从 Microsoft Store 安装 (最简单)**:

1. 打开 Microsoft Store
2. 搜索 "Python 3.12" 或 "Python 3.11"
3. 点击"获取"并安装
4. 安装完成后，在 PowerShell 中验证:

   ```powershell
   python --version
   ```

**选项 B: 从 Python 官网安装**:

1. 访问 <https://www.python.org/downloads/>
2. 下载最新的 Python 3.x 版本（推荐 3.11 或 3.12）
3. 运行安装程序
4. **重要**: 勾选 "Add Python to PATH" 选项
5. 完成安装后重启 PowerShell

### 方案 2: 安装依赖包

安装 Python 后，在项目根目录执行:

```powershell
# 方法1: 使用requirements.txt（推荐）
python -m pip install -r requirements.txt

# 方法2: 单独安装
python -m pip install psycopg2-binary pytest pyyaml tabulate

# 方法3: 只安装测试所需的最小依赖
python -m pip install psycopg2-binary
```

### 方案 3: 使用虚拟环境（最佳实践）

```powershell
# 1. 在项目根目录创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 注意: 如果遇到执行策略错误，运行:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. 安装依赖
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. 验证安装
python -c "import psycopg2; print('psycopg2 安装成功!')"
```

---

## IDE 配置（重要）

### Cursor / VS Code

如果使用虚拟环境，需要让 IDE 识别它:

1. **按 `Ctrl+Shift+P`** 打开命令面板
2. 输入 **"Python: Select Interpreter"**
3. 选择虚拟环境中的 Python 解释器:

   ```text
   .\venv\Scripts\python.exe
   ```

或者创建/更新 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.analysis.extraPaths": ["${workspaceFolder}/tests/scripts"],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.pycodestyleEnabled": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. 点击齿轮图标 → Add
3. 选择 "Existing environment"
4. 浏览到 `venv\Scripts\python.exe`

---

## 验证安装

创建测试文件 `test_setup.py`:

```python
#!/usr/bin/env python3
"""验证Python环境是否正确配置"""

import sys

def test_python_version():
    print(f"Python版本: {sys.version}")
    assert sys.version_info >= (3, 8), "需要Python 3.8或更高版本"
    print("✓ Python版本检查通过")

def test_psycopg2():
    try:
        import psycopg2
        print(f"✓ psycopg2版本: {psycopg2.__version__}")
        return True
    except ImportError as e:
        print(f"✗ psycopg2导入失败: {e}")
        return False

def test_other_deps():
    deps = ['yaml', 'tabulate']
    for dep in deps:
        try:
            __import__(dep)
            print(f"✓ {dep} 已安装")
        except ImportError:
            print(f"⚠ {dep} 未安装（可选）")

if __name__ == '__main__':
    print("="*60)
    print("PostgreSQL_modern 环境验证")
    print("="*60 + "\n")

    test_python_version()

    if test_psycopg2():
        print("\n✓ 所有必需依赖已正确安装")
        print("您可以运行测试了:")
        print("  python tests/scripts/run_single_test.py tests/sql_tests/example_test.sql")
    else:
        print("\n✗ 请先安装psycopg2-binary:")
        print("  python -m pip install psycopg2-binary")

    print("\n检查可选依赖:")
    test_other_deps()
```

运行验证:

```powershell
python test_setup.py
```

---

## 常见错误及解决方案

### 错误 1: "python 不是内部或外部命令"

**原因**: Python 未安装或未添加到 PATH

**解决**:

- 按照"方案 1"安装 Python
- 重启 PowerShell 终端
- 如果仍然失败，手动添加到 PATH:
  1. 搜索"环境变量"
  2. 编辑系统变量 PATH
  3. 添加 Python 安装路径（如 `C:\Users\YourName\AppData\Local\Programs\Python\Python311`）

### 错误 2: "无法加载文件，因为在此系统上禁止运行脚本"

**原因**: PowerShell 执行策略限制

**解决**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 错误 3: "ModuleNotFoundError: No module named 'psycopg2'"

**原因**: 包未安装或安装到了错误的 Python 环境

**解决**:

```powershell
# 确认使用正确的Python
python -m pip list | Select-String psycopg2

# 如果没有，重新安装
python -m pip install --force-reinstall psycopg2-binary
```

### 错误 4: IDE 中仍然显示导入错误

**原因**: IDE 使用了错误的 Python 解释器

**解决**:

- 重启 IDE
- 按照"IDE 配置"部分重新选择解释器
- 重新加载窗口（Ctrl+Shift+P → "Developer: Reload Window"）

---

## 依赖说明

| 包名            | 版本要求 | 用途                  | 必需性   |
| --------------- | -------- | --------------------- | -------- |
| psycopg2-binary | >=2.9.9  | PostgreSQL 数据库连接 | **必需** |
| pytest          | >=7.4.0  | 测试框架              | 推荐     |
| pyyaml          | >=6.0.1  | 配置文件解析          | 推荐     |
| tabulate        | >=0.9.0  | 表格格式化输出        | 可选     |

---

## 快速命令参考

```powershell
# 检查Python版本
python --version

# 查看已安装的包
python -m pip list

# 安装所有依赖
python -m pip install -r requirements.txt

# 升级pip
python -m pip install --upgrade pip

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\Activate.ps1

# 停用虚拟环境
deactivate
```

---

## 相关文档

- [tests/QUICK_START.md](tests/QUICK_START.md) - 测试框架快速开始
- [tests/README.md](tests/README.md) - 完整测试文档
- [requirements.txt](requirements.txt) - 项目依赖列表

---

**创建日期**: 2025-10-03  
**适用系统**: Windows 10/11  
**Python 版本**: 3.8+
