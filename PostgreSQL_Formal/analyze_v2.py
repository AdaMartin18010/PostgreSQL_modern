import json
with open('LINK_AUDIT_DATA_V2.json', 'r', encoding='utf-8') as f:
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

print('\n失效链接的文件 (前20):')
for source, count in sorted(by_file.items(), key=lambda x: -x[1])[:20]:
    print(f'  {source}: {count}')

# 详细列出broken_file
print('\n文件不存在的详细列表:')
file_broken = [l for l in broken if l.get('status') == 'broken_file']
for link in file_broken:
    print(f"  {link['source_file']} -> '{link['url']}' (文本: '{link['text']}')")

# 详细列出broken_anchor  
print('\n锚点失效的详细列表:')
anchor_broken = [l for l in broken if l.get('status') == 'broken_anchor']
for link in anchor_broken[:30]:
    print(f"  {link['source_file']} -> '{link['url']}' (期望: {link.get('expected_anchor', '')})")
