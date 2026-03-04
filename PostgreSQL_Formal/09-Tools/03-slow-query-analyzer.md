# 工具: 慢查询分析器

```python
#!/usr/bin/env python3
"""
慢查询分析工具
"""

import re
from collections import defaultdict

def parse_slow_log(log_file):
    """解析PostgreSQL慢查询日志"""
    pattern = r'duration: ([\d.]+) ms.*statement: (.*)'

    slow_queries = defaultdict(list)

    with open(log_file) as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                duration = float(match.group(1))
                query = match.group(2)

                # 归一化查询
                normalized = re.sub(r'\$\d+', '?', query)
                slow_queries[normalized].append(duration)

    return slow_queries

def print_report(queries):
    """打印报告"""
    print("Top 10 Slow Queries:")
    sorted_queries = sorted(
        queries.items(),
        key=lambda x: sum(x[1])/len(x[1]),
        reverse=True
    )[:10]

    for query, durations in sorted_queries:
        avg = sum(durations) / len(durations)
        print(f"Avg: {avg:.2f}ms, Count: {len(durations)}")
        print(f"Query: {query[:100]}...")

if __name__ == '__main__':
    queries = parse_slow_log('postgresql-slow.log')
    print_report(queries)
```

---

**完成度**: 100%
