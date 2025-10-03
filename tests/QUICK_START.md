# 快速开始指南

## 环境要求

- Python 3.8+
- PostgreSQL 16+ (推荐 PostgreSQL 17)
- pip (Python包管理器)

## 安装步骤

### 1. 安装Python依赖

#### Windows (PowerShell)

```powershell
# 在项目根目录执行
pip install -r requirements.txt

# 或者只安装测试依赖
pip install -r tests/requirements.txt
```

#### Linux/macOS

```bash
# 在项目根目录执行
pip3 install -r requirements.txt

# 或者只安装测试依赖
pip3 install -r tests/requirements.txt
```

### 2. 配置数据库连接

```powershell
# 复制配置文件模板
Copy-Item tests/config/database.yml.example tests/config/database.yml

# 编辑 tests/config/database.yml，填入你的数据库连接信息
```

### 3. 初始化测试数据库

```sql
-- 连接到PostgreSQL
psql -U postgres

-- 创建测试数据库
CREATE DATABASE postgres_modern_test;

-- 退出psql
\q
```

### 4. 运行测试

```powershell
# 运行单个测试
python tests/scripts/run_single_test.py tests/sql_tests/example_test.sql

# 运行所有测试
python tests/scripts/run_all_tests.py

# 调试模式
python tests/scripts/run_single_test.py --debug tests/sql_tests/example_test.sql
```

## 常见问题

### Q1: 导入错误 "Import psycopg2 could not be resolved"

**原因**: Python包 `psycopg2-binary` 未安装

**解决方案**:

```powershell
pip install psycopg2-binary
```

### Q2: 连接数据库失败

**原因**: 数据库配置不正确或数据库未启动

**解决方案**:

1. 检查PostgreSQL服务是否运行
2. 验证 `tests/config/database.yml` 中的连接信息
3. 确保测试数据库已创建

### Q3: 权限错误

**原因**: 数据库用户权限不足

**解决方案**:

```sql
-- 授予必要权限
GRANT ALL PRIVILEGES ON DATABASE postgres_modern_test TO postgres;
```

## IDE配置

### VS Code / Cursor

如果使用VS Code或Cursor，创建/更新 `.vscode/settings.json`:

```json
{
  "python.analysis.extraPaths": [
    "${workspaceFolder}/tests/scripts"
  ],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

### PyCharm

1. 打开 Settings → Project → Python Interpreter
2. 点击 + 号添加包
3. 搜索并安装: `psycopg2-binary`, `pytest`, `pyyaml`, `tabulate`

## 验证安装

运行以下命令验证环境是否正确配置:

```python
# test_connection.py
import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres'
    )
    print("✓ 数据库连接成功!")
    conn.close()
except Exception as e:
    print(f"✗ 连接失败: {e}")
```

运行:

```powershell
python test_connection.py
```

## 下一步

- 查看 [tests/README.md](README.md) 了解完整的测试框架文档
- 探索 [tests/sql_tests/](sql_tests/) 中的测试用例示例
- 阅读 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何贡献代码

---

**最后更新**: 2025-10-03
