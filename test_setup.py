#!/usr/bin/env python3
"""验证Python环境是否正确配置"""

import sys

def test_python_version():
    print(f"Python版本: {sys.version}")
    version_info = sys.version_info
    if version_info < (3, 8):
        print(f"✗ 需要Python 3.8或更高版本，当前版本: {version_info.major}.{version_info.minor}")
        return False
    print(f"✓ Python版本检查通过 ({version_info.major}.{version_info.minor}.{version_info.micro})")
    return True

def test_psycopg2():
    try:
        import psycopg2
        print(f"✓ psycopg2版本: {psycopg2.__version__}")
        return True
    except ImportError as e:
        print(f"✗ psycopg2导入失败: {e}")
        print("  请运行: python -m pip install psycopg2-binary")
        return False

def test_other_deps():
    deps = {
        'yaml': 'pyyaml',
        'tabulate': 'tabulate',
        'pytest': 'pytest'
    }
    
    optional_status = []
    for module_name, package_name in deps.items():
        try:
            mod = __import__(module_name)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {package_name} 已安装 (版本: {version})")
            optional_status.append(True)
        except ImportError:
            print(f"⚠ {package_name} 未安装（可选，但推荐安装）")
            optional_status.append(False)
    
    return optional_status

def main():
    print("="*60)
    print("PostgreSQL_modern 环境验证")
    print("="*60 + "\n")
    
    all_good = True
    
    # 测试Python版本
    if not test_python_version():
        all_good = False
        print("\n请升级Python到3.8或更高版本")
        return False
    
    print()
    
    # 测试必需依赖
    if not test_psycopg2():
        all_good = False
        print("\n✗ 必需依赖缺失，无法运行测试")
        print("\n请执行以下命令安装所有依赖:")
        print("  python -m pip install -r requirements.txt")
        print("\n或只安装必需依赖:")
        print("  python -m pip install psycopg2-binary")
        return False
    
    print()
    
    # 测试可选依赖
    print("检查可选依赖:")
    optional_status = test_other_deps()
    
    print("\n" + "="*60)
    if all_good:
        print("✓ 所有必需依赖已正确安装")
        print("\n您可以运行测试了:")
        print("  python tests/scripts/run_single_test.py tests/sql_tests/example_test.sql")
        
        if not all(optional_status):
            print("\n建议安装所有依赖以获得最佳体验:")
            print("  python -m pip install -r requirements.txt")
    else:
        print("✗ 环境配置不完整")
    print("="*60)
    
    return all_good

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

