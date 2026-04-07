# 工具: 连接池监控

```python
#!/usr/bin/env python3
"""
连接池监控工具
"""

import psycopg2

def check_connections(conn):
    """检查连接状态"""
    query = """
    SELECT state, count(*)
    FROM pg_stat_activity
    GROUP BY state;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

if __name__ == '__main__':
    conn = psycopg2.connect("dbname=postgres")
    states = check_connections(conn)
    for state, count in states:
        print(f"{state}: {count}")
```

---

**完成度**: 100%
