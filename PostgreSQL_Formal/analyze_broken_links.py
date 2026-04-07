import json
with open('LINK_AUDIT_DATA.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

broken = data['broken_links']
print(f"总失效链接: {len(broken)}")

# 按状态分类
by_status = {}
for link in broken:
    status = link.get('status', 'unknown')
    by_status[status] = by_status.get(status, 0) + 1

print('\n按状态分类:')
for status, count in sorted(by_status.items(), key=lambda x: -x[1]):
    print(f'  {status}: {count}')

# 按源文件分类
by_file = {}
for link in broken:
    source = link.get('source_file', 'unknown')
    by_file[source] = by_file.get(source, 0) + 1

print('\n失效链接最多的文件 (前10):')
for source, count in sorted(by_file.items(), key=lambda x: -x[1])[:10]:
    print(f'  {source}: {count}')

# 列出一些broken_file的例子
print('\n文件不存在的例子 (前20):')
file_broken = [l for l in broken if l.get('status') == 'broken_file']
for link in file_broken[:20]:
    print(f"  {link['source_file']} -> {link['url']}")
