#!/usr/bin/env python3
"""
PostgreSQL备份验证工具
功能: 自动验证备份完整性和可恢复性
"""

import psycopg2
import subprocess
import tempfile
import shutil
import os
from datetime import datetime
import argparse

class BackupValidator:
    """备份验证工具"""
    
    def __init__(self, backup_path: str, test_db_port: int = 5433):
        self.backup_path = backup_path
        self.test_db_port = test_db_port
        self.test_dir = None
    
    def validate_backup(self):
        """验证备份"""
        
        print(f"验证备份: {self.backup_path}")
        print(f"时间: {datetime.now()}")
        print("="*80)
        
        # 1. 检查备份文件
        if not os.path.exists(self.backup_path):
            print(f"✗ 备份文件不存在: {self.backup_path}")
            return False
        
        file_size = os.path.getsize(self.backup_path) / (1024**3)
        print(f"✓ 备份文件大小: {file_size:.2f} GB")
        
        # 2. 创建临时测试目录
        self.test_dir = tempfile.mkdtemp(prefix='pg_test_')
        print(f"✓ 测试目录: {self.test_dir}")
        
        try:
            # 3. 恢复备份
            if not self.restore_backup():
                return False
            
            # 4. 启动测试实例
            if not self.start_test_instance():
                return False
            
            # 5. 验证数据完整性
            if not self.verify_data():
                return False
            
            # 6. 停止测试实例
            self.stop_test_instance()
            
            print("\n" + "="*80)
            print("✅ 备份验证成功")
            return True
            
        except Exception as e:
            print(f"\n✗ 验证失败: {e}")
            return False
        
        finally:
            # 清理
            self.cleanup()
    
    def restore_backup(self):
        """恢复备份"""
        
        print("\n[1/4] 恢复备份...")
        
        try:
            if self.backup_path.endswith('.sql'):
                # pg_dump格式
                subprocess.run([
                    'psql', '-h', 'localhost', '-p', str(self.test_db_port),
                    '-U', 'postgres', '-f', self.backup_path
                ], check=True, capture_output=True)
            
            elif self.backup_path.endswith('.dump'):
                # pg_restore格式
                subprocess.run([
                    'pg_restore', '-h', 'localhost', '-p', str(self.test_db_port),
                    '-U', 'postgres', '-d', 'postgres', self.backup_path
                ], check=True, capture_output=True)
            
            else:
                # pgbackrest/物理备份
                shutil.copytree(self.backup_path, self.test_dir, dirs_exist_ok=True)
            
            print("✓ 备份恢复成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ 恢复失败: {e.stderr.decode()}")
            return False
    
    def start_test_instance(self):
        """启动测试实例"""
        
        print("\n[2/4] 启动测试实例...")
        
        try:
            subprocess.run([
                'pg_ctl', '-D', self.test_dir,
                '-o', f'-p {self.test_db_port}',
                'start'
            ], check=True, capture_output=True, timeout=30)
            
            print("✓ 测试实例启动成功")
            return True
            
        except Exception as e:
            print(f"✗ 启动失败: {e}")
            return False
    
    def verify_data(self):
        """验证数据完整性"""
        
        print("\n[3/4] 验证数据...")
        
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=self.test_db_port,
                user='postgres',
                database='postgres'
            )
            cursor = conn.cursor()
            
            # 检查表数量
            cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';")
            table_count = cursor.fetchone()[0]
            print(f"✓ 表数量: {table_count}")
            
            # 检查关键表
            critical_tables = ['users', 'orders']  # 根据实际情况修改
            
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table};")
                    row_count = cursor.fetchone()[0]
                    print(f"✓ {table}: {row_count} 行")
                except:
                    print(f"⚠ {table}: 表不存在或无法访问")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"✗ 数据验证失败: {e}")
            return False
    
    def stop_test_instance(self):
        """停止测试实例"""
        
        print("\n[4/4] 停止测试实例...")
        
        try:
            subprocess.run([
                'pg_ctl', '-D', self.test_dir, 'stop'
            ], check=True, capture_output=True, timeout=30)
            
            print("✓ 测试实例已停止")
            
        except Exception as e:
            print(f"⚠ 停止失败: {e}")
    
    def cleanup(self):
        """清理临时文件"""
        
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            print("✓ 清理完成")

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL备份验证工具')
    parser.add_argument('--backup', required=True, help='备份文件路径')
    parser.add_argument('--test-port', type=int, default=5433, help='测试实例端口')
    
    args = parser.parse_args()
    
    validator = BackupValidator(args.backup, args.test_port)
    success = validator.validate_backup()
    
    exit(0 if success else 1)

if __name__ == '__main__':
    main()
```

**使用**:
```bash
# 验证备份
python3 18-备份验证工具.py --backup /backup/mydb_20241201.sql

# 定期验证（每周）
0 3 * * 0 python3 /path/to/18-备份验证工具.py --backup /backup/latest.dump
```
