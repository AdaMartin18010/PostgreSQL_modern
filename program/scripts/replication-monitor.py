#!/usr/bin/env python3
"""
PostgreSQL复制监控工具
实时监控主从复制状态、延迟、冲突等
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import time
from datetime import datetime
import sys

class ReplicationMonitor:
    """复制监控"""

    def __init__(self, conn_str: str):
        self.conn = psycopg2.connect(conn_str, cursor_factory=RealDictCursor)
        self.cursor = self.conn.cursor()
        self.is_primary = self.check_role()

    def check_role(self) -> bool:
        """检查当前节点角色"""
        self.cursor.execute("SELECT pg_is_in_recovery();")
        in_recovery = self.cursor.fetchone()['pg_is_in_recovery']

        role = "从服务器" if in_recovery else "主服务器"
        print(f"当前节点角色: {role}")
        print()

        return not in_recovery

    def monitor_primary(self) -> dict:
        """监控主服务器复制状态"""

        # 复制连接状态
        self.cursor.execute("""
            SELECT
                application_name,
                client_addr,
                state,
                sync_state,
                sent_lsn,
                write_lsn,
                flush_lsn,
                replay_lsn,
                pg_wal_lsn_diff(sent_lsn, replay_lsn)::BIGINT AS lag_bytes,
                EXTRACT(EPOCH FROM (now() - backend_start))::INT AS connection_seconds,
                EXTRACT(EPOCH FROM (now() - COALESCE(reply_time, backend_start)))::INT AS last_reply_seconds
            FROM pg_stat_replication
            ORDER BY application_name;
        """)

        replicas = self.cursor.fetchall()

        if not replicas:
            print("⚠️  没有从服务器连接")
            return {'replicas': []}

        print(f"从服务器数量: {len(replicas)}")
        print()

        for r in replicas:
            print(f"从服务器: {r['application_name']}")
            print(f"  地址: {r['client_addr']}")
            print(f"  状态: {r['state']}")
            print(f"  同步模式: {r['sync_state']}")
            print(f"  延迟: {self.format_bytes(r['lag_bytes'])}")
            print(f"  连接时长: {self.format_duration(r['connection_seconds'])}")
            print(f"  最后响应: {self.format_duration(r['last_reply_seconds'])}前")

            # 告警
            if r['lag_bytes'] > 100 * 1024 * 1024:  # >100MB
                print(f"  ⚠️  延迟过大!")

            if r['last_reply_seconds'] > 60:  # >1分钟
                print(f"  ⚠️  响应延迟!")

            print()

        return {'replicas': replicas}

    def monitor_standby(self) -> dict:
        """监控从服务器复制状态"""

        # 接收状态
        self.cursor.execute("""
            SELECT
                status,
                receive_start_lsn,
                receive_start_tli,
                received_lsn,
                received_tli,
                last_msg_send_time,
                last_msg_receipt_time,
                latest_end_lsn,
                latest_end_time,
                slot_name,
                sender_host,
                sender_port,
                conninfo
            FROM pg_stat_wal_receiver;
        """)

        receiver = self.cursor.fetchone()

        if not receiver:
            print("⚠️  WAL接收器未运行")
            return {'receiver': None}

        print("WAL接收状态:")
        print(f"  状态: {receiver['status']}")
        print(f"  主服务器: {receiver['sender_host']}:{receiver['sender_port']}")

        if receiver['last_msg_receipt_time']:
            delay = (datetime.now() - receiver['last_msg_receipt_time'].replace(tzinfo=None)).total_seconds()
            print(f"  最后接收: {self.format_duration(int(delay))}前")

            if delay > 60:
                print(f"  ⚠️  接收延迟!")

        print()

        # 复制延迟
        self.cursor.execute("""
            SELECT
                pg_last_wal_receive_lsn() AS receive_lsn,
                pg_last_wal_replay_lsn() AS replay_lsn,
                pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn())::BIGINT AS replay_lag_bytes,
                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::INT AS replay_lag_seconds;
        """)

        lag = self.cursor.fetchone()

        print("复制延迟:")
        print(f"  接收LSN: {lag['receive_lsn']}")
        print(f"  回放LSN: {lag['replay_lsn']}")
        print(f"  回放延迟: {self.format_bytes(lag['replay_lag_bytes'])}")

        if lag['replay_lag_seconds']:
            print(f"  时间延迟: {self.format_duration(lag['replay_lag_seconds'])}")

            if lag['replay_lag_seconds'] > 300:  # >5分钟
                print(f"  ⚠️  延迟过大!")

        print()

        return {
            'receiver': receiver,
            'lag': lag
        }

    def check_replication_slots(self):
        """检查复制槽"""

        self.cursor.execute("""
            SELECT
                slot_name,
                slot_type,
                database,
                active,
                restart_lsn,
                confirmed_flush_lsn,
                pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)::BIGINT AS retained_bytes
            FROM pg_replication_slots
            ORDER BY slot_name;
        """)

        slots = self.cursor.fetchall()

        if not slots:
            return

        print("复制槽:")
        for slot in slots:
            print(f"  {slot['slot_name']}")
            print(f"    类型: {slot['slot_type']}")
            print(f"    活跃: {'是' if slot['active'] else '否'}")

            if slot['retained_bytes']:
                print(f"    保留WAL: {self.format_bytes(slot['retained_bytes'])}")

                if slot['retained_bytes'] > 1024 * 1024 * 1024:  # >1GB
                    print(f"    ⚠️  保留WAL过多!")

            print()

    def monitor_conflicts(self):
        """监控从服务器冲突"""

        if self.is_primary:
            return

        self.cursor.execute("""
            SELECT
                datname,
                confl_tablespace,
                confl_lock,
                confl_snapshot,
                confl_bufferpin,
                confl_deadlock
            FROM pg_stat_database_conflicts
            WHERE datname = current_database();
        """)

        conflicts = self.cursor.fetchone()

        if not conflicts:
            return

        total_conflicts = sum([
            conflicts['confl_tablespace'],
            conflicts['confl_lock'],
            conflicts['confl_snapshot'],
            conflicts['confl_bufferpin'],
            conflicts['confl_deadlock']
        ])

        if total_conflicts > 0:
            print("复制冲突:")
            print(f"  表空间冲突: {conflicts['confl_tablespace']}")
            print(f"  锁冲突: {conflicts['confl_lock']}")
            print(f"  快照冲突: {conflicts['confl_snapshot']}")
            print(f"  缓冲区冲突: {conflicts['confl_bufferpin']}")
            print(f"  死锁: {conflicts['confl_deadlock']}")
            print(f"  ⚠️  总冲突数: {total_conflicts}")
            print()

    def format_bytes(self, bytes_val: int) -> str:
        """格式化字节数"""
        if bytes_val is None:
            return "N/A"

        if bytes_val < 1024:
            return f"{bytes_val}B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.2f}KB"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / 1024 / 1024:.2f}MB"
        else:
            return f"{bytes_val / 1024 / 1024 / 1024:.2f}GB"

    def format_duration(self, seconds: int) -> str:
        """格式化时长"""
        if seconds is None:
            return "N/A"

        if seconds < 60:
            return f"{seconds}秒"
        elif seconds < 3600:
            return f"{seconds // 60}分{seconds % 60}秒"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}小时{minutes}分"

    def monitor_once(self):
        """单次监控"""

        print("="*80)
        print(f"PostgreSQL复制监控 - {datetime.now()}")
        print("="*80)
        print()

        if self.is_primary:
            self.monitor_primary()
            self.check_replication_slots()
        else:
            self.monitor_standby()
            self.monitor_conflicts()

    def monitor_continuous(self, interval: int = 5):
        """持续监控"""

        try:
            while True:
                # 清屏（Windows和Linux）
                import os
                os.system('cls' if os.name == 'nt' else 'clear')

                self.monitor_once()

                print(f"刷新间隔: {interval}秒 (Ctrl+C退出)")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n监控已停止")

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='PostgreSQL复制监控工具')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5432)
    parser.add_argument('--dbname', default='postgres')
    parser.add_argument('--user', default='postgres')
    parser.add_argument('--password')
    parser.add_argument('--interval', type=int, default=5, help='刷新间隔（秒）')
    parser.add_argument('--once', action='store_true', help='只监控一次')

    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user}"
    if args.password:
        conn_str += f" password={args.password}"

    try:
        monitor = ReplicationMonitor(conn_str)

        if args.once:
            monitor.monitor_once()
        else:
            monitor.monitor_continuous(interval=args.interval)

        monitor.close()

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
