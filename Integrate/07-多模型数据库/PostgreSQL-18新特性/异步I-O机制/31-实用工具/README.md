# 31. 实用工具与脚本集合

> **章节编号**: 31
> **章节标题**: 实用工具与脚本集合
> **来源文档**: PostgreSQL 18 异步 I/O 机制

---

## 31. 实用工具与脚本集合

## 📑 目录

- [31.2 性能测试工具](#312-性能测试工具)
- [31.3 监控诊断工具](#313-监控诊断工具)
- [31.4 自动化运维工具](#314-自动化运维工具)

---

---

### 31.2 性能测试工具

#### 31.2.1 异步I/O性能对比测试工具

**功能**: 对比同步I/O和异步I/O的性能差异

**脚本** (`aio_performance_comparison.py`):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O性能对比测试工具
"""
import psycopg2
import time
import statistics
import json
from datetime import datetime

class AIOPerformanceComparison:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.results = {
            'sync_io': {},
            'async_io': {}
        }

    def setup_test_table(self, row_count=100000):
        """创建测试表"""
        cur = self.conn.cursor()

        # 删除旧表
        cur.execute("DROP TABLE IF EXISTS aio_test_table;")
        self.conn.commit()

        # 创建测试表
        cur.execute("""
            CREATE TABLE aio_test_table (
                id SERIAL PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        self.conn.commit()

        print(f"✓ 测试表已创建，准备插入 {row_count} 行数据...")

    def test_batch_insert(self, batch_size=1000, num_batches=10):
        """测试批量插入性能"""
        cur = self.conn.cursor()
        times = []

        for i in range(num_batches):
            start_time = time.time()

            cur.execute("""
                INSERT INTO aio_test_table (data)
                SELECT 'Test data ' || generate_series(1, %s)
            """, (batch_size,))

            self.conn.commit()
            elapsed = time.time() - start_time
            times.append(elapsed)

            if (i + 1) % 5 == 0:
                print(f"  已完成批次: {i + 1}/{num_batches}")

        return {
            'total_time': sum(times),
            'avg_time': statistics.mean(times),
            'min_time': min(times),
            'max_time': max(times),
            'throughput': (batch_size * num_batches) / sum(times)
        }

    def test_full_table_scan(self):
        """测试全表扫描性能"""
        cur = self.conn.cursor()

        start_time = time.time()
        cur.execute("SELECT COUNT(*) FROM aio_test_table;")
        result = cur.fetchone()
        elapsed = time.time() - start_time

        return {
            'time': elapsed,
            'rows': result[0] if result else 0
        }

    def test_io_config(self, io_direct_setting, effective_io_concurrency):
        """测试特定I/O配置"""
        cur = self.conn.cursor()

        # 设置配置
        cur.execute("ALTER SYSTEM SET io_direct = %s", (io_direct_setting,))
        cur.execute("ALTER SYSTEM SET effective_io_concurrency = %s",
                   (effective_io_concurrency,))
        cur.execute("SELECT pg_reload_conf();")

        # 等待配置生效
        time.sleep(2)

        # 验证配置
        cur.execute("SELECT setting FROM pg_settings WHERE name = 'io_direct'")
        actual_io_direct = cur.fetchone()[0]

        cur.execute("SELECT setting FROM pg_settings WHERE name = 'effective_io_concurrency'")
        actual_concurrency = cur.fetchone()[0]

        return actual_io_direct == io_direct_setting and \
               actual_concurrency == str(effective_io_concurrency)

    def run_comparison(self, row_count=100000, batch_size=1000):
        """运行性能对比测试"""
        print("=== PostgreSQL 18异步I/O性能对比测试 ===\n")

        # 准备测试数据
        self.setup_test_table(row_count)

        # 测试1: 同步I/O
        print("\n[测试1] 同步I/O配置...")
        if not self.test_io_config('off', 1):
            print("错误: 无法设置同步I/O配置")
            return

        print("  测试批量插入性能...")
        sync_insert = self.test_batch_insert(batch_size, 10)

        print("  测试全表扫描性能...")
        sync_scan = self.test_full_table_scan()

        self.results['sync_io'] = {
            'insert': sync_insert,
            'scan': sync_scan
        }

        # 清理数据
        cur = self.conn.cursor()
        cur.execute("TRUNCATE TABLE aio_test_table;")
        self.conn.commit()

        # 测试2: 异步I/O
        print("\n[测试2] 异步I/O配置...")
        if not self.test_io_config('data,wal', 200):
            print("错误: 无法设置异步I/O配置")
            return

        print("  测试批量插入性能...")
        async_insert = self.test_batch_insert(batch_size, 10)

        print("  测试全表扫描性能...")
        async_scan = self.test_full_table_scan()

        self.results['async_io'] = {
            'insert': async_insert,
            'scan': async_scan
        }

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        sync_insert = self.results['sync_io']['insert']
        async_insert = self.results['async_io']['insert']
        sync_scan = self.results['sync_io']['scan']
        async_scan = self.results['async_io']['scan']

        insert_improvement = ((sync_insert['total_time'] - async_insert['total_time']) /
                             sync_insert['total_time'] * 100)
        scan_improvement = ((sync_scan['time'] - async_scan['time']) /
                           sync_scan['time'] * 100)

        print("\n" + "="*60)
        print("性能对比测试报告")
        print("="*60)

        print("\n批量插入性能:")
        print(f"  同步I/O: {sync_insert['total_time']:.2f}秒 "
              f"({sync_insert['throughput']:.0f} rows/s)")
        print(f"  异步I/O: {async_insert['total_time']:.2f}秒 "
              f"({async_insert['throughput']:.0f} rows/s)")
        print(f"  性能提升: {insert_improvement:.1f}%")

        print("\n全表扫描性能:")
        print(f"  同步I/O: {sync_scan['time']:.2f}秒")
        print(f"  异步I/O: {async_scan['time']:.2f}秒")
        print(f"  性能提升: {scan_improvement:.1f}%")

        print("\n" + "="*60)

        # 保存报告到文件
        report_file = f"aio_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n详细报告已保存到: {report_file}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 18异步I/O性能对比测试工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--database', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='数据库用户')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--rows', type=int, default=100000, help='测试数据行数')
    parser.add_argument('--batch-size', type=int, default=1000, help='批量大小')

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }

    if args.password:
        db_config['password'] = args.password

    tester = AIOPerformanceComparison(db_config)
    tester.run_comparison(args.rows, args.batch_size)

if __name__ == '__main__':
    main()
```

**使用方法**:

```bash
# 运行性能对比测试
python3 aio_performance_comparison.py

# 自定义测试参数
python3 aio_performance_comparison.py --rows 500000 --batch-size 2000

# 指定数据库连接
python3 aio_performance_comparison.py --host prod-db --user dba
```

---

### 31.3 监控诊断工具

#### 31.3.1 实时I/O监控工具

**功能**: 实时监控异步I/O性能指标

**脚本** (`realtime_io_monitor.py`):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O实时监控工具
"""
import psycopg2
import time
import os
from datetime import datetime

class RealtimeIOMonitor:
    def __init__(self, db_config, interval=5):
        self.conn = psycopg2.connect(**db_config)
        self.interval = interval
        self.running = True

    def get_io_stats(self):
        """获取I/O统计信息"""
        cur = self.conn.cursor()

        # 获取I/O统计
        cur.execute("""
            SELECT
                context,
                SUM(reads) as total_reads,
                SUM(writes) as total_writes,
                AVG(read_time) as avg_read_time,
                AVG(write_time) as avg_write_time,
                MAX(read_time) as max_read_time,
                MAX(write_time) as max_write_time
            FROM pg_stat_io
            GROUP BY context
            ORDER BY total_reads + total_writes DESC;
        """)

        return cur.fetchall()

    def get_config(self):
        """获取当前配置"""
        cur = self.conn.cursor()

        cur.execute("""
            SELECT name, setting
            FROM pg_settings
            WHERE name IN (
                'io_direct',
                'effective_io_concurrency',
                'wal_io_concurrency',
                'io_uring_queue_depth'
            )
            ORDER BY name;
        """)

        return dict(cur.fetchall())

    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def display_stats(self, io_stats, config):
        """显示统计信息"""
        self.clear_screen()

        print("="*80)
        print(f"PostgreSQL 18异步I/O实时监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        print("\n【配置信息】")
        for param, value in config.items():
            print(f"  {param}: {value}")

        print("\n【I/O统计】")
        print(f"{'Context':<20} {'Reads':>12} {'Writes':>12} {'Avg Read':>12} {'Avg Write':>12}")
        print("-"*80)

        for row in io_stats:
            context, reads, writes, avg_read, avg_write, max_read, max_write = row
            print(f"{context:<20} {reads:>12} {writes:>12} "
                  f"{avg_read:>10.2f}ms {avg_write:>10.2f}ms")

        print("\n按Ctrl+C退出...")

    def run(self):
        """运行监控"""
        try:
            while self.running:
                io_stats = self.get_io_stats()
                config = self.get_config()
                self.display_stats(io_stats, config)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n\n监控已停止")
        finally:
            self.conn.close()

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 18异步I/O实时监控工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--database', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='数据库用户')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }

    if args.password:
        db_config['password'] = args.password

    monitor = RealtimeIOMonitor(db_config, args.interval)
    monitor.run()

if __name__ == '__main__':
    main()
```

**使用方法**:

```bash
# 启动实时监控
python3 realtime_io_monitor.py

# 自定义刷新间隔
python3 realtime_io_monitor.py --interval 10

# 监控远程数据库
python3 realtime_io_monitor.py --host prod-db --user dba
```

#### 31.3.2 I/O性能分析工具

**功能**: 深入分析I/O性能，识别瓶颈

**脚本** (`io_performance_analyzer.py`):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O性能分析工具
"""
import psycopg2
import json
from datetime import datetime, timedelta

class IOPerformanceAnalyzer:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)

    def analyze_io_bottlenecks(self):
        """分析I/O瓶颈"""
        cur = self.conn.cursor()

        cur.execute("""
            WITH io_stats AS (
                SELECT
                    context,
                    SUM(reads) as total_reads,
                    SUM(writes) as total_writes,
                    AVG(read_time) as avg_read_time,
                    AVG(write_time) as avg_write_time,
                    MAX(read_time) as max_read_time,
                    MAX(write_time) as max_write_time,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY read_time) as p99_read_time,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY write_time) as p99_write_time
                FROM pg_stat_io
                GROUP BY context
            )
            SELECT
                context,
                total_reads,
                total_writes,
                avg_read_time,
                avg_write_time,
                max_read_time,
                max_write_time,
                p99_read_time,
                p99_write_time,
                CASE
                    WHEN avg_read_time > 20 THEN '严重'
                    WHEN avg_read_time > 10 THEN '中等'
                    WHEN avg_read_time > 5 THEN '轻微'
                    ELSE '正常'
                END as read_severity,
                CASE
                    WHEN avg_write_time > 20 THEN '严重'
                    WHEN avg_write_time > 10 THEN '中等'
                    WHEN avg_write_time > 5 THEN '轻微'
                    ELSE '正常'
                END as write_severity
            FROM io_stats
            ORDER BY avg_read_time + avg_write_time DESC;
        """)

        return cur.fetchall()

    def generate_recommendations(self, bottlenecks):
        """生成优化建议"""
        recommendations = []

        for row in bottlenecks:
            context, reads, writes, avg_read, avg_write, max_read, max_write, \
            p99_read, p99_write, read_sev, write_sev = row

            if read_sev in ['严重', '中等']:
                recommendations.append({
                    'context': context,
                    'issue': '读取延迟过高',
                    'severity': read_sev,
                    'current_value': f"{avg_read:.2f}ms",
                    'recommendation': self._get_read_recommendation(avg_read, context)
                })

            if write_sev in ['严重', '中等']:
                recommendations.append({
                    'context': context,
                    'issue': '写入延迟过高',
                    'severity': write_sev,
                    'current_value': f"{avg_write:.2f}ms",
                    'recommendation': self._get_write_recommendation(avg_write, context)
                })

        return recommendations

    def _get_read_recommendation(self, avg_read_time, context):
        """获取读取优化建议"""
        if avg_read_time > 20:
            return "1) 检查存储性能 2) 提高effective_io_concurrency到400+ 3) 检查是否有I/O竞争"
        elif avg_read_time > 10:
            return "1) 提高effective_io_concurrency到300+ 2) 优化查询使用索引"
        else:
            return "考虑提高effective_io_concurrency以进一步优化"

    def _get_write_recommendation(self, avg_write_time, context):
        """获取写入优化建议"""
        if avg_write_time > 20:
            return "1) 检查WAL写入性能 2) 提高wal_io_concurrency到250+ 3) 优化WAL配置"
        elif avg_write_time > 10:
            return "1) 提高wal_io_concurrency到200+ 2) 检查WAL文件位置"
        else:
            return "考虑提高wal_io_concurrency以进一步优化"

    def generate_report(self):
        """生成分析报告"""
        bottlenecks = self.analyze_io_bottlenecks()
        recommendations = self.generate_recommendations(bottlenecks)

        print("="*80)
        print("PostgreSQL 18异步I/O性能分析报告")
        print("="*80)

        print("\n【I/O性能分析】")
        print(f"{'Context':<20} {'Avg Read':>12} {'Avg Write':>12} {'Read Severity':>15} {'Write Severity':>15}")
        print("-"*80)

        for row in bottlenecks:
            context, reads, writes, avg_read, avg_write, max_read, max_write, \
            p99_read, p99_write, read_sev, write_sev = row
            print(f"{context:<20} {avg_read:>10.2f}ms {avg_write:>10.2f}ms "
                  f"{read_sev:>15} {write_sev:>15}")

        if recommendations:
            print("\n【优化建议】")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec['context']} - {rec['issue']}")
                print(f"   严重程度: {rec['severity']}")
                print(f"   当前值: {rec['current_value']}")
                print(f"   建议: {rec['recommendation']}")
        else:
            print("\n✓ 未发现明显的I/O瓶颈")

        print("\n" + "="*80)

        # 保存报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'bottlenecks': [
                {
                    'context': row[0],
                    'avg_read_time': float(row[3]),
                    'avg_write_time': float(row[4]),
                    'read_severity': row[9],
                    'write_severity': row[10]
                }
                for row in bottlenecks
            ],
            'recommendations': recommendations
        }

        report_file = f"io_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n详细报告已保存到: {report_file}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 18异步I/O性能分析工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--database', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='数据库用户')
    parser.add_argument('--password', help='数据库密码')

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }

    if args.password:
        db_config['password'] = args.password

    analyzer = IOPerformanceAnalyzer(db_config)
    analyzer.generate_report()

if __name__ == '__main__':
    main()
```

---

### 31.4 自动化运维工具

#### 31.4.1 自动化健康检查工具

**功能**: 定期自动执行健康检查，发现问题并告警

**脚本** (`auto_health_check.py`):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O自动化健康检查工具
"""
import psycopg2
import json
import sys
from datetime import datetime

class AutoHealthCheck:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.checks = []
        self.severity_count = {'critical': 0, 'warning': 0, 'info': 0}

    def check_async_io_config(self):
        """检查异步I/O配置"""
        cur = self.conn.cursor()

        cur.execute("SELECT setting FROM pg_settings WHERE name = 'io_direct'")
        io_direct = cur.fetchone()[0]

        if io_direct == 'off':
            self.add_check('critical', '异步I/O配置',
                          'io_direct未启用，异步I/O可能未生效',
                          'ALTER SYSTEM SET io_direct = \'data,wal\';')
        else:
            self.add_check('info', '异步I/O配置',
                          f'io_direct已启用: {io_direct}', None)

    def check_io_concurrency(self):
        """检查I/O并发度配置"""
        cur = self.conn.cursor()

        cur.execute("SELECT setting::INTEGER FROM pg_settings WHERE name = 'effective_io_concurrency'")
        concurrency = cur.fetchone()[0]

        if concurrency < 50:
            self.add_check('warning', 'I/O并发度配置',
                          f'effective_io_concurrency={concurrency}，可能过低，建议至少200',
                          'ALTER SYSTEM SET effective_io_concurrency = 200;')
        elif concurrency > 500:
            self.add_check('warning', 'I/O并发度配置',
                          f'effective_io_concurrency={concurrency}，可能过高，建议300-500',
                          'ALTER SYSTEM SET effective_io_concurrency = 400;')
        else:
            self.add_check('info', 'I/O并发度配置',
                          f'effective_io_concurrency={concurrency}，配置合理', None)

    def check_io_latency(self):
        """检查I/O延迟"""
        cur = self.conn.cursor()

        cur.execute("""
            SELECT AVG(read_time), AVG(write_time)
            FROM pg_stat_io
            WHERE context = 'normal'
        """)

        avg_read, avg_write = cur.fetchone()

        if avg_read and avg_read > 10:
            self.add_check('warning', 'I/O读取延迟',
                          f'平均读取延迟: {avg_read:.2f}ms，超过10ms阈值',
                          '检查存储性能或提高effective_io_concurrency')

        if avg_write and avg_write > 10:
            self.add_check('warning', 'I/O写入延迟',
                          f'平均写入延迟: {avg_write:.2f}ms，超过10ms阈值',
                          '检查WAL写入性能或提高wal_io_concurrency')

    def add_check(self, severity, check_name, message, recommendation):
        """添加检查结果"""
        self.checks.append({
            'severity': severity,
            'check_name': check_name,
            'message': message,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        })
        self.severity_count[severity] = self.severity_count.get(severity, 0) + 1

    def run_all_checks(self):
        """运行所有检查"""
        self.check_async_io_config()
        self.check_io_concurrency()
        self.check_io_latency()

    def generate_report(self, json_output=False):
        """生成检查报告"""
        if json_output:
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.severity_count,
                'checks': self.checks
            }
            print(json.dumps(report, indent=2))
        else:
            print("="*80)
            print("PostgreSQL 18异步I/O健康检查报告")
            print("="*80)
            print(f"\n检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            print("\n【检查摘要】")
            print(f"  严重问题: {self.severity_count['critical']}")
            print(f"  警告: {self.severity_count['warning']}")
            print(f"  信息: {self.severity_count['info']}")

            if self.checks:
                print("\n【检查详情】")
                for i, check in enumerate(self.checks, 1):
                    severity_icon = {
                        'critical': '❌',
                        'warning': '⚠️',
                        'info': 'ℹ️'
                    }.get(check['severity'], '•')

                    print(f"\n{i}. {severity_icon} [{check['severity'].upper()}] {check['check_name']}")
                    print(f"   {check['message']}")
                    if check['recommendation']:
                        print(f"   建议: {check['recommendation']}")

            print("\n" + "="*80)

        # 返回退出码
        if self.severity_count['critical'] > 0:
            return 2
        elif self.severity_count['warning'] > 0:
            return 1
        else:
            return 0

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 18异步I/O自动化健康检查工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--database', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='数据库用户')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }

    if args.password:
        db_config['password'] = args.password

    checker = AutoHealthCheck(db_config)
    checker.run_all_checks()
    exit_code = checker.generate_report(args.json)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
```

**使用方法**:

```bash
# 运行健康检查
python3 auto_health_check.py

# JSON格式输出（适合集成到监控系统）
python3 auto_health_check.py --json

# 集成到cron定期执行
# */15 * * * * /usr/local/bin/auto_health_check.py --host prod-db --json | logger -t pg-health-check
```

#### 31.4.2 自动化性能优化工具

**功能**: 自动分析性能并应用优化

**脚本** (`auto_performance_optimizer.py`):

```python
#!/usr/bin/env python3
"""
PostgreSQL 18异步I/O自动化性能优化工具
"""
import psycopg2
import time
from datetime import datetime

class AutoPerformanceOptimizer:
    def __init__(self, db_config, dry_run=False):
        self.conn = psycopg2.connect(**db_config)
        self.dry_run = dry_run
        self.optimizations = []

    def analyze_and_optimize(self):
        """分析并优化性能"""
        print("=== PostgreSQL 18异步I/O自动化性能优化 ===\n")

        # 1. 分析当前性能
        print("[1/3] 分析当前性能...")
        current_perf = self.analyze_performance()

        # 2. 生成优化建议
        print("[2/3] 生成优化建议...")
        recommendations = self.generate_recommendations(current_perf)

        # 3. 应用优化
        print("[3/3] 应用优化...")
        self.apply_optimizations(recommendations)

        # 4. 验证优化效果
        if not self.dry_run:
            print("\n[验证] 验证优化效果...")
            time.sleep(5)  # 等待配置生效
            new_perf = self.analyze_performance()
            self.compare_performance(current_perf, new_perf)

    def analyze_performance(self):
        """分析当前性能"""
        cur = self.conn.cursor()

        cur.execute("""
            SELECT
                AVG(read_time) as avg_read_time,
                AVG(write_time) as avg_write_time,
                SUM(reads) + SUM(writes) as total_io_ops
            FROM pg_stat_io
            WHERE context = 'normal'
        """)

        result = cur.fetchone()
        return {
            'avg_read_time': result[0] or 0,
            'avg_write_time': result[1] or 0,
            'total_io_ops': result[2] or 0
        }

    def generate_recommendations(self, performance):
        """生成优化建议"""
        recommendations = []
        cur = self.conn.cursor()

        # 获取当前配置
        cur.execute("SELECT setting::INTEGER FROM pg_settings WHERE name = 'effective_io_concurrency'")
        current_concurrency = cur.fetchone()[0]

        # 根据性能生成建议
        if performance['avg_read_time'] > 10:
            new_concurrency = min(current_concurrency * 2, 500)
            recommendations.append({
                'parameter': 'effective_io_concurrency',
                'current': current_concurrency,
                'recommended': new_concurrency,
                'reason': f'读取延迟过高 ({performance["avg_read_time"]:.2f}ms)'
            })

        cur.execute("SELECT setting::INTEGER FROM pg_settings WHERE name = 'wal_io_concurrency'")
        current_wal_concurrency = cur.fetchone()[0]

        if performance['avg_write_time'] > 10:
            new_wal_concurrency = min(current_wal_concurrency * 2, 300)
            recommendations.append({
                'parameter': 'wal_io_concurrency',
                'current': current_wal_concurrency,
                'recommended': new_wal_concurrency,
                'reason': f'写入延迟过高 ({performance["avg_write_time"]:.2f}ms)'
            })

        return recommendations

    def apply_optimizations(self, recommendations):
        """应用优化"""
        if not recommendations:
            print("  ✓ 无需优化")
            return

        cur = self.conn.cursor()

        for rec in recommendations:
            if self.dry_run:
                print(f"  [DRY-RUN] ALTER SYSTEM SET {rec['parameter']} = {rec['recommended']};")
                print(f"    原因: {rec['reason']}")
            else:
                try:
                    cur.execute(f"ALTER SYSTEM SET {rec['parameter']} = %s",
                               (rec['recommended'],))
                    print(f"  ✓ 已优化 {rec['parameter']}: {rec['current']} → {rec['recommended']}")
                    self.optimizations.append(rec)
                except Exception as e:
                    print(f"  ✗ 优化 {rec['parameter']} 失败: {e}")

        if not self.dry_run and self.optimizations:
            cur.execute("SELECT pg_reload_conf();")
            print("  ✓ 配置已重新加载")

    def compare_performance(self, before, after):
        """对比优化前后性能"""
        print("\n性能对比:")
        print(f"  读取延迟: {before['avg_read_time']:.2f}ms → {after['avg_read_time']:.2f}ms")
        print(f"  写入延迟: {before['avg_write_time']:.2f}ms → {after['avg_write_time']:.2f}ms")

        read_improvement = ((before['avg_read_time'] - after['avg_read_time']) /
                           before['avg_read_time'] * 100) if before['avg_read_time'] > 0 else 0
        write_improvement = ((before['avg_write_time'] - after['avg_write_time']) /
                            before['avg_write_time'] * 100) if before['avg_write_time'] > 0 else 0

        if read_improvement > 0:
            print(f"  读取性能提升: {read_improvement:.1f}%")
        if write_improvement > 0:
            print(f"  写入性能提升: {write_improvement:.1f}%")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='PostgreSQL 18异步I/O自动化性能优化工具')
    parser.add_argument('--host', default='localhost', help='数据库主机')
    parser.add_argument('--port', type=int, default=5432, help='数据库端口')
    parser.add_argument('--database', default='postgres', help='数据库名')
    parser.add_argument('--user', default='postgres', help='数据库用户')
    parser.add_argument('--password', help='数据库密码')
    parser.add_argument('--dry-run', action='store_true', help='仅显示建议，不应用')

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user
    }

    if args.password:
        db_config['password'] = args.password

    optimizer = AutoPerformanceOptimizer(db_config, args.dry_run)
    optimizer.analyze_and_optimize()

if __name__ == '__main__':
    main()
```

**使用方法**:

```bash
# 查看优化建议（不应用）
python3 auto_performance_optimizer.py --dry-run

# 自动应用优化
python3 auto_performance_optimizer.py

# 定期自动优化（使用cron）
# */30 * * * * /usr/local/bin/auto_performance_optimizer.py --host prod-db
```

---

---

**返回**: [文档首页](../README.md) | [上一章节](../30-可视化图表/README.md) | [下一章节](../37-实战演练/README.md)
