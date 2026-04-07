#!/usr/bin/env python3
"""
PostgreSQL_Formal 项目链接全面审计脚本
扫描所有Markdown文件，验证内部链接和锚点链接
"""

import os
import re
import json
from pathlib import Path
from urllib.parse import urlparse, unquote
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path("e:/_src/PostgreSQL_modern/PostgreSQL_Formal")

# 链接正则表达式
LINK_PATTERN = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
# HTML img标签正则
IMG_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
# Markdown图片正则
MD_IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
# 标题正则
HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
# HTML锚点名称
HTML_ANCHOR_PATTERN = re.compile(r'<a[^>]+name=["\']([^"\']+)["\']', re.IGNORECASE)

class LinkAuditor:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.md_files = []  # 所有Markdown文件
        self.all_links = []  # 所有链接
        self.broken_links = []  # 失效链接
        self.valid_links = []  # 有效链接
        self.file_anchors = {}  # 文件锚点映射 {filepath: set(anchors)}
        
    def scan_markdown_files(self):
        """扫描所有Markdown文件"""
        for md_file in self.root_path.rglob('*.md'):
            # 排除备份目录
            if '.link_fix_backup' not in str(md_file):
                self.md_files.append(md_file)
        print(f"找到 {len(self.md_files)} 个Markdown文件")
        
    def extract_headings(self, content, filepath):
        """提取文件中的所有标题作为锚点"""
        anchors = set()
        
        # 提取Markdown标题
        for match in HEADING_PATTERN.finditer(content):
            level = len(match.group(1))
            title = match.group(2).strip()
            # 生成锚点ID
            anchor = self._generate_anchor(title)
            anchors.add(anchor.lower())
            anchors.add(anchor)
            
        # 提取HTML锚点
        for match in HTML_ANCHOR_PATTERN.finditer(content):
            anchors.add(match.group(1))
            
        # 特殊处理: 自动生成的TOC锚点
        anchors.add('目录')
        anchors.add('toc')
        anchors.add('summary')
        anchors.add('abstract')
        
        self.file_anchors[str(filepath)] = anchors
        return anchors
    
    def _generate_anchor(self, title):
        """根据标题生成锚点ID"""
        # 移除Markdown格式
        clean = re.sub(r'[*_`]', '', title)
        # 转换为小写
        clean = clean.lower()
        # 替换空格为连字符
        clean = re.sub(r'\s+', '-', clean)
        # 移除特殊字符
        clean = re.sub(r'[^\w\-\u4e00-\u9fff]', '', clean)
        return clean
    
    def extract_links(self, content, filepath):
        """从内容中提取所有链接"""
        links = []
        rel_path = str(filepath.relative_to(self.root_path))
        
        # 提取Markdown链接
        for match in LINK_PATTERN.finditer(content):
            text = match.group(1)
            url = match.group(2)
            links.append({
                'type': 'markdown',
                'text': text,
                'url': url,
                'source_file': rel_path,
                'line': content[:match.start()].count('\n') + 1
            })
        
        # 提取Markdown图片
        for match in MD_IMG_PATTERN.finditer(content):
            alt = match.group(1)
            url = match.group(2)
            links.append({
                'type': 'image',
                'text': alt,
                'url': url,
                'source_file': rel_path,
                'line': content[:match.start()].count('\n') + 1
            })
        
        # 提取HTML图片
        for match in IMG_PATTERN.finditer(content):
            url = match.group(1)
            links.append({
                'type': 'html_image',
                'text': '',
                'url': url,
                'source_file': rel_path,
                'line': content[:match.start()].count('\n') + 1
            })
            
        return links
    
    def classify_link(self, link):
        """分类链接类型"""
        url = link['url']
        
        # 外部链接
        if url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return 'external'
        
        # 锚点链接 (仅#开头)
        if url.startswith('#'):
            return 'anchor_only'
        
        # 图片链接
        if url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
            return 'image'
        
        # Markdown文档链接
        if '.md' in url or url.endswith('.md'):
            return 'internal_doc'
        
        # 相对路径文件
        if '/' in url or '\\' in url:
            return 'internal_file'
        
        return 'unknown'
    
    def resolve_path(self, source_file, link_url):
        """解析链接的绝对路径"""
        source_dir = (self.root_path / source_file).parent
        
        # 移除锚点部分
        if '#' in link_url:
            url_path = link_url.split('#')[0]
            anchor = link_url.split('#')[1]
        else:
            url_path = link_url
            anchor = None
            
        if not url_path:
            # 只有锚点，使用源文件
            return str(self.root_path / source_file), anchor
        
        # 解析路径
        if url_path.startswith('/'):
            # 绝对路径（相对于项目根）
            target = self.root_path / url_path.lstrip('/')
        else:
            # 相对路径
            target = source_dir / url_path
            
        try:
            return str(target.resolve()), anchor
        except:
            return str(target), anchor
    
    def validate_link(self, link):
        """验证单个链接"""
        link_type = self.classify_link(link)
        link['link_type'] = link_type
        
        # 外部链接 - 不验证内容，仅记录
        if link_type == 'external':
            link['status'] = 'external'
            return True
        
        url = link['url']
        source_file = link['source_file']
        
        # 纯锚点链接
        if link_type == 'anchor_only':
            anchor = url[1:]  # 移除 #
            target_file = str(self.root_path / source_file)
            
            if target_file not in self.file_anchors:
                # 尝试加载文件
                try:
                    content = Path(target_file).read_text(encoding='utf-8', errors='ignore')
                    self.extract_headings(content, Path(target_file))
                except:
                    pass
            
            anchors = self.file_anchors.get(target_file, set())
            anchor_lower = anchor.lower()
            
            if anchor in anchors or anchor_lower in anchors:
                link['status'] = 'valid'
                return True
            else:
                link['status'] = 'broken_anchor'
                link['expected_anchor'] = anchor
                link['available_anchors'] = list(anchors)[:10]  # 前10个可用锚点
                return False
        
        # 内部文档/文件链接
        target_path, anchor = self.resolve_path(source_file, url)
        
        # 检查文件是否存在
        if not os.path.exists(target_path):
            # 尝试添加.md扩展名
            if not target_path.endswith('.md'):
                target_path_md = target_path + '.md'
                if os.path.exists(target_path_md):
                    target_path = target_path_md
                else:
                    link['status'] = 'broken_file'
                    link['resolved_path'] = target_path
                    return False
            else:
                link['status'] = 'broken_file'
                link['resolved_path'] = target_path
                return False
        
        # 如果有锚点，验证锚点
        if anchor:
            if target_path not in self.file_anchors:
                try:
                    content = Path(target_path).read_text(encoding='utf-8', errors='ignore')
                    self.extract_headings(content, Path(target_path))
                except:
                    pass
            
            anchors = self.file_anchors.get(target_path, set())
            anchor_lower = anchor.lower()
            
            if anchor not in anchors and anchor_lower not in anchors:
                link['status'] = 'broken_anchor'
                link['expected_anchor'] = anchor
                link['target_file'] = target_path
                link['available_anchors'] = list(anchors)[:10]
                return False
        
        link['status'] = 'valid'
        link['resolved_path'] = target_path
        return True
    
    def run_audit(self):
        """运行完整审计"""
        print("=" * 60)
        print("PostgreSQL_Formal 链接全面审计")
        print("=" * 60)
        
        # 1. 扫描文件
        print("\n[1/4] 扫描Markdown文件...")
        self.scan_markdown_files()
        
        # 2. 预加载所有文件的锚点
        print("\n[2/4] 预加载文件锚点...")
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                self.extract_headings(content, md_file)
            except Exception as e:
                print(f"  警告: 无法读取 {md_file}: {e}")
        print(f"  已加载 {len(self.file_anchors)} 个文件的锚点")
        
        # 3. 提取所有链接
        print("\n[3/4] 提取链接...")
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                links = self.extract_links(content, md_file)
                self.all_links.extend(links)
            except Exception as e:
                print(f"  警告: 无法处理 {md_file}: {e}")
        print(f"  共提取 {len(self.all_links)} 个链接")
        
        # 4. 验证链接
        print("\n[4/4] 验证链接...")
        for i, link in enumerate(self.all_links):
            if i % 500 == 0:
                print(f"  进度: {i}/{len(self.all_links)}")
            
            is_valid = self.validate_link(link)
            if is_valid:
                self.valid_links.append(link)
            else:
                self.broken_links.append(link)
        
        print(f"\n验证完成:")
        print(f"  - 有效链接: {len(self.valid_links)}")
        print(f"  - 失效链接: {len(self.broken_links)}")
        
    def generate_report(self):
        """生成审计报告"""
        report_path = self.root_path / 'LINK_AUDIT_FULL_REPORT.md'
        
        # 统计
        total_files = len(self.md_files)
        total_links = len(self.all_links)
        valid_count = len(self.valid_links)
        broken_count = len(self.broken_links)
        external_count = len([l for l in self.all_links if l.get('link_type') == 'external'])
        
        # 按类型分类失效链接
        broken_files = [l for l in self.broken_links if l.get('status') == 'broken_file']
        broken_anchors = [l for l in self.broken_links if l.get('status') == 'broken_anchor']
        
        # 按源文件分组
        broken_by_file = defaultdict(list)
        for link in self.broken_links:
            broken_by_file[link['source_file']].append(link)
        
        report = f"""# PostgreSQL_Formal 链接全面审计报告

> 生成时间: {os.popen('date /t').read().strip()} {os.popen('time /t').read().strip()}
> 审计范围: PostgreSQL_Formal/ 全部子目录
> 文件类型: *.md

---

## 统计概览

| 指标 | 数量 |
|------|------|
| 总文档数 | {total_files} |
| 总链接数 | {total_links} |
| 外部链接 | {external_count} |
| 有效链接 | {valid_count} |
| 失效链接 | {broken_count} |
| 严重失效 (文件不存在) | {len(broken_files)} |
| 锚点失效 (标题不存在) | {len(broken_anchors)} |

### 状态分布

```
失效链接类型分布:
- 文件不存在: {'█' * len(broken_files)}{' ' * (20 - min(20, len(broken_files)))} {len(broken_files)}
- 锚点不存在: {'█' * len(broken_anchors)}{' ' * (20 - min(20, len(broken_anchors)))} {len(broken_anchors)}
```

---

## 严重失效链接 (文件不存在)

| 序号 | 源文件 | 失效链接 | 建议修复 |
|------|--------|----------|----------|
"""
        
        # 添加严重失效链接详情
        for i, link in enumerate(broken_files[:100], 1):  # 只显示前100个
            source = link['source_file']
            url = link['url']
            resolved = link.get('resolved_path', '')
            
            # 生成建议
            suggestion = self._suggest_fix(link)
            
            report += f"| {i} | `{source}` | `{url}` | {suggestion} |\n"
        
        if len(broken_files) > 100:
            report += f"| ... | ... | ... | 还有 {len(broken_files) - 100} 个... |\n"
        
        report += f"""

---

## 锚点失效链接 (标题不存在)

| 序号 | 源文件 | 链接 | 失效锚点 | 可用锚点示例 |
|------|--------|------|----------|-------------|
"""
        
        # 添加锚点失效详情
        for i, link in enumerate(broken_anchors[:100], 1):
            source = link['source_file']
            url = link['url']
            expected = link.get('expected_anchor', '')
            available = ', '.join(link.get('available_anchors', [])[:5])
            
            report += f"| {i} | `{source}` | `{url}` | `{expected}` | {available} |\n"
        
        if len(broken_anchors) > 100:
            report += f"| ... | ... | ... | ... | 还有 {len(broken_anchors) - 100} 个... |\n"
        
        report += f"""

---

## 按源文件分类的失效链接

"""
        
        for source_file, links in sorted(broken_by_file.items()):
            report += f"\n### {source_file}\n\n"
            report += "| 链接 | 类型 | 状态 | 建议 |\n"
            report += "|------|------|------|------|\n"
            
            for link in links[:20]:  # 每文件最多20个
                url = link['url'][:50] + '...' if len(link['url']) > 50 else link['url']
                link_type = link.get('link_type', 'unknown')
                status = link.get('status', 'unknown')
                suggestion = self._suggest_fix(link)[:30]
                
                report += f"| `{url}` | {link_type} | {status} | {suggestion} |\n"
            
            if len(links) > 20:
                report += f"| ... | | | 还有 {len(links) - 20} 个... |\n"
        
        report += f"""

---

## 修复建议

### 自动修复建议

以下是可以通过脚本自动修复的问题:

1. **大小写不匹配**: 链接指向的文件名大小写与实际文件名不符
2. **缺少 .md 扩展名**: 链接缺少 .md 后缀
3. **相对路径错误**: `../` 使用过多或不足

### 需要手动修复的清单

需要人工检查确认的问题:

"""
        
        # 列出需要手动检查的问题
        manual_fixes = []
        for link in self.broken_links:
            if link.get('status') == 'broken_file':
                manual_fixes.append(f"- `{link['source_file']}` → `{link['url']}`")
        
        report += '\n'.join(manual_fixes[:50])
        
        if len(manual_fixes) > 50:
            report += f"\n- ... 还有 {len(manual_fixes) - 50} 个需要手动修复"
        
        report += f"""

---

## 附录: 链接类型统计

| 类型 | 数量 |
|------|------|
| 外部链接 | {len([l for l in self.all_links if l.get('link_type') == 'external'])} |
| 内部文档 | {len([l for l in self.all_links if l.get('link_type') == 'internal_doc'])} |
| 纯锚点 | {len([l for l in self.all_links if l.get('link_type') == 'anchor_only'])} |
| 图片 | {len([l for l in self.all_links if l.get('link_type') == 'image'])} |
| 其他 | {len([l for l in self.all_links if l.get('link_type') not in ['external', 'internal_doc', 'anchor_only', 'image']])} |

---

## 修复优先级

1. **高优先级**: 核心文档中的失效链接（README.md, INDEX.md 等）
2. **中优先级**: 理论章节和核心技术文档
3. **低优先级**: 备份目录和归档文档

---

*报告由链接审计脚本自动生成*
"""
        
        report_path.write_text(report, encoding='utf-8')
        print(f"\n报告已生成: {report_path}")
        return report_path
    
    def _suggest_fix(self, link):
        """生成修复建议"""
        status = link.get('status')
        url = link['url']
        
        if status == 'broken_file':
            # 检查是否只是大小写问题
            resolved = link.get('resolved_path', '')
            if resolved:
                parent = Path(resolved).parent
                filename = Path(resolved).name
                if parent.exists():
                    for f in parent.iterdir():
                        if f.name.lower() == filename.lower() and f.name != filename:
                            return f"改为 `{f.relative_to(self.root_path)}`"
            
            # 检查是否缺少 .md 扩展名
            if not url.endswith('.md') and not '.' in Path(url).name:
                return f"改为 `{url}.md`"
            
            return "检查文件路径或文件名"
        
        elif status == 'broken_anchor':
            available = link.get('available_anchors', [])
            expected = link.get('expected_anchor', '')
            
            # 尝试找相似的锚点
            for a in available:
                if expected.lower() in a.lower() or a.lower() in expected.lower():
                    return f"改为 `#{a}`"
            
            return "检查标题名称"
        
        return "-"
    
    def export_json(self):
        """导出JSON格式的详细数据"""
        json_path = self.root_path / 'LINK_AUDIT_DATA.json'
        data = {
            'summary': {
                'total_files': len(self.md_files),
                'total_links': len(self.all_links),
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links)
            },
            'broken_links': self.broken_links,
            'all_links': self.all_links
        }
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"数据已导出: {json_path}")
        return json_path


def main():
    auditor = LinkAuditor(PROJECT_ROOT)
    auditor.run_audit()
    report_path = auditor.generate_report()
    json_path = auditor.export_json()
    
    print("\n" + "=" * 60)
    print("审计完成!")
    print(f"  报告: {report_path}")
    print(f"  数据: {json_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
