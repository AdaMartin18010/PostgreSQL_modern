# 工具: 索引推荐器

```python
#!/usr/bin/env python3
"""
索引推荐工具
基于查询日志分析
"""

import re

def analyze_queries(log_file):
    """分析慢查询日志"""
    patterns = {
        'where': r'WHERE\s+(\w+)\s*=',
        'join': r'JOIN\s+(\w+)\s+ON',
        'order': r'ORDER\s+BY\s+(\w+)'
    }

    recommendations = []

    with open(log_file) as f:
        for line in f:
            if 'duration:' in line and 'ms' in line:
                # 提取表和列
                for ptype, pattern in patterns.items():
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        recommendations.append({
                            'table': match,
                            'type': ptype
                        })

    return recommendations

if __name__ == '__main__':
    recs = analyze_queries('postgresql.log')
    print(f"推荐索引数: {len(recs)}")
```

---

**完成度**: 100%
