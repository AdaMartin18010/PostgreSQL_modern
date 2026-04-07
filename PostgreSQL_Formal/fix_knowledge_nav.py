import re

content = open('visualization/KNOWLEDGE-NAV.md', 'r', encoding='utf-8').read()

# 修复相对路径 - 添加 ../ 前缀
patterns = [
    (r'\]\((11-Database-Centric-Architecture/)', r'](../\1'),
    (r'\]\((04-Concurrency/)', r'](../\1'),
    (r'\]\((05-Distributed/)', r'](../\1'),
    (r'\]\((01-Theory/)', r'](../\1'),
    (r'\]\((09-Tools/)', r'](../\1'),
    (r'\]\((00-NewFeatures-18/)', r'](../\1'),
    (r'\]\((00-Version-Specific/)', r'](../\1'),
    (r'\]\((06-FormalMethods/)', r'(../\1'),
    (r'\]\((02-Storage/)', r'](../\1'),
    (r'\]\((03-Query/)', r'](../\1'),
    (r'\]\((07-PracticalCases/)', r'](../\1'),
    (r'\]\((08-Performance/)', r'](../\1'),
    (r'\]\((10-Visualization/)', r'](../\1'),
]

for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

open('visualization/KNOWLEDGE-NAV.md', 'w', encoding='utf-8').write(content)
print("KNOWLEDGE-NAV.md 链接路径已修复")
