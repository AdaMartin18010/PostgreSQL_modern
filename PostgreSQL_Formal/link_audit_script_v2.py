#!/usr/bin/env python3
"""
PostgreSQL_Formal 项目链接全面审计脚本 V2
更准确地识别真正的Markdown链接
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path("e:/_src/PostgreSQL_modern/PostgreSQL_Formal")

# 更精确的链接正则表达式
# 匹配 [text](url) 格式，但排除行内代码中的 `[
LINK_PATTERN = re.compile(r'(?<!`)\[([^\]]+)\]\(([^)]+)\)(?!`)')
# 图片链接
MD_IMG_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
# HTML img标签
IMG_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
# HTML锚点
HTML_ANCHOR_PATTERN = re.compile(r'<a[^>]+name=["\']([^"\']+)["\']', re.IGNORECASE)
# 标题正则
HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

class LinkAuditor:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.md_files = []
        self.all_links = []
        self.broken_links = []
        self.valid_links = []
        self.file_anchors = {}
        
    def scan_markdown_files(self):
        """扫描所有Markdown文件"""
        for md_file in self.root_path.rglob('*.md'):
            if '.link_fix_backup' not in str(md_file):
                self.md_files.append(md_file)
        print(f"找到 {len(self.md_files)} 个Markdown文件")
        
    def extract_headings(self, content, filepath):
        """提取文件中的所有标题作为锚点"""
        anchors = set()
        
        for match in HEADING_PATTERN.finditer(content):
            title = match.group(2).strip()
            anchor = self._generate_anchor(title)
            anchors.add(anchor.lower())
            anchors.add(anchor)
            
        for match in HTML_ANCHOR_PATTERN.finditer(content):
            anchors.add(match.group(1))
            
        anchors.add('目录')
        anchors.add('toc')
        
        self.file_anchors[str(filepath)] = anchors
        return anchors
    
    def _generate_anchor(self, title):
        """根据标题生成锚点ID"""
        clean = re.sub(r'[*_`]', '', title)
        clean = clean.lower()
        clean = re.sub(r'\s+', '-', clean)
        clean = re.sub(r'[^\w\-\u4e00-\u9fff]', '', clean)
        return clean
    
    def extract_links(self, content, filepath):
        """从内容中提取所有链接"""
        links = []
        rel_path = str(filepath.relative_to(self.root_path))
        
        # 提取Markdown链接 - 过滤掉行内代码中的
        for match in LINK_PATTERN.finditer(content):
            text = match.group(1)
            url = match.group(2)
            
            # 跳过看起来像代码的链接文本
            if text.startswith('`') and text.endswith('`'):
                continue
            if url.startswith('`') or url.endswith('`'):
                continue
                
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
        
        if url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return 'external'
        
        if url.startswith('#'):
            return 'anchor_only'
        
        if any(url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']):
            return 'image'
        
        if '.md' in url or url.endswith('.md'):
            return 'internal_doc'
        
        if '/' in url or '\\' in url:
            return 'internal_file'
        
        # 如果URL不包含.，可能是一个缺少.md扩展名的文档链接
        if '.' not in url.split('/')[-1].split('\\')[-1]:
            return 'internal_doc_no_ext'
        
        return 'unknown'
    
    def resolve_path(self, source_file, link_url):
        """解析链接的绝对路径"""
        source_dir = (self.root_path / source_file).parent
        
        if '#' in link_url:
            url_path = link_url.split('#')[0]
            anchor = link_url.split('#')[1]
        else:
            url_path = link_url
            anchor = None
            
        if not url_path:
            return str(self.root_path / source_file), anchor
        
        if url_path.startswith('/'):
            target = self.root_path / url_path.lstrip('/')
        else:
            target = source_dir / url_path
            
        try:
            return str(target.resolve()), anchor
        except:
            return str(target), anchor
    
    def validate_link(self, link):
        """验证单个链接"""
        link_type = self.classify_link(link)
        link['link_type'] = link_type
        
        if link_type == 'external':
            link['status'] = 'external'
            return True
        
        url = link['url']
        source_file = link['source_file']
        
        # 纯锚点链接
        if link_type == 'anchor_only':
            anchor = url[1:]
            target_file = str(self.root_path / source_file)
            
            if target_file not in self.file_anchors:
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
                link['available_anchors'] = list(anchors)[:10]
                return False
        
        # 内部文档/文件链接
        target_path, anchor = self.resolve_path(source_file, url)
        
        # 尝试不同的路径变体
        path_variants = [target_path]
        if not target_path.endswith('.md'):
            path_variants.append(target_path + '.md')
        
        found = False
        for variant in path_variants:
            if os.path.exists(variant):
                target_path = variant
                found = True
                break
        
        if not found:
            link['status'] = 'broken_file'
            link['resolved_path'] = target_path
            return False
        
        # 验证锚点
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
        print("PostgreSQL_Formal 链接全面审计 V2")
        print("=" * 60)
        
        print("\n[1/4] 扫描Markdown文件...")
        self.scan_markdown_files()
        
        print("\n[2/4] 预加载文件锚点...")
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                self.extract_headings(content, md_file)
            except Exception as e:
                pass
        print(f"  已加载 {len(self.file_anchors)} 个文件的锚点")
        
        print("\n[3/4] 提取链接...")
        for md_file in self.md_files:
            try:
                content = md_file.read_text(encoding='utf-8', errors='ignore')
                links = self.extract_links(content, md_file)
                self.all_links.extend(links)
            except Exception as e:
                pass
        print(f"  共提取 {len(self.all_links)} 个链接")
        
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
        report_path = self.root_path / 'LINK_AUDIT_FULL_REPORT_V2.md'
        
        total_files = len(self.md_files)
        total_links = len(self.all_links)
        valid_count = len(self.valid_links)
        broken_count = len(self.broken_links)
        external_count = len([l for l in self.all_links if l.get('link_type') == 'external'])
        
        broken_files = [l for l in self.broken_links if l.get('status') == 'broken_file']
        broken_anchors = [l for l in self.broken_links if l.get('status') == 'broken_anchor']
        
        broken_by_file = defaultdict(list)
        for link in self.broken_links:
            broken_by_file[link['source_file']].append(link)
        
        report = f"""# PostgreSQL_Formal 链接全面审计报告 V2

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

---

## 失效链接详情

### 严重失效链接 (文件不存在)

| 序号 | 源文件 | 失效链接 | 链接文本 |
|------|--------|----------|----------|
"""
        
        for i, link in enumerate(broken_files[:50], 1):
            source = link['source_file']
            url = link['url'][:60] + '...' if len(link['url']) > 60 else link['url']
            text = link['text'][:30] + '...' if len(link['text']) > 30 else link['text']
            report += f"| {i} | `{source}` | `{url}` | {text} |\n"
        
        if len(broken_files) > 50:
            report += f"| ... | ... | ... | 还有 {len(broken_files) - 50} 个... |\n"
        
        report += f"""

### 锚点失效链接 (标题不存在)

| 序号 | 源文件 | 链接 | 失效锚点 |
|------|--------|------|----------|
"""
        
        for i, link in enumerate(broken_anchors[:50], 1):
            source = link['source_file']
            url = link['url'][:50] + '...' if len(link['url']) > 50 else link['url']
            expected = link.get('expected_anchor', '')
            report += f"| {i} | `{source}` | `{url}` | `{expected}` |\n"
        
        if len(broken_anchors) > 50:
            report += f"| ... | ... | ... | 还有 {len(broken_anchors) - 50} 个... |\n"
        
        report += f"""

---

## 按源文件分类的失效链接 (前20文件)

"""
        
        for source_file, links in sorted(broken_by_file.items(), key=lambda x: -len(x[1]))[:20]:
            report += f"\n### {source_file} ({len(links)}个)\n\n"
            report += "| 链接 | 类型 | 状态 |\n"
            report += "|------|------|------|\n"
            
            for link in links[:10]:
                url = link['url'][:50] + '...' if len(link['url']) > 50 else link['url']
                link_type = link.get('link_type', 'unknown')
                status = link.get('status', 'unknown')
                report += f"| `{url}` | {link_type} | {status} |\n"
            
            if len(links) > 10:
                report += f"| ... | | | 还有 {len(links) - 10} 个... |\n"
        
        report += """

---

## 修复建议

1. **文件不存在问题**:
   - 检查路径是否正确
   - 确认目标文件是否存在
   - 修复相对路径（添加/移除 `../`）

2. **锚点失效问题**:
   - 检查标题名称是否正确
   - 特殊字符可能需要转义或移除
   - 中文标题注意编码问题

---

*报告由链接审计脚本V2自动生成*
"""
        
        report_path.write_text(report, encoding='utf-8')
        print(f"\n报告已生成: {report_path}")
        return report_path
    
    def export_json(self):
        """导出JSON格式的详细数据"""
        json_path = self.root_path / 'LINK_AUDIT_DATA_V2.json'
        data = {
            'summary': {
                'total_files': len(self.md_files),
                'total_links': len(self.all_links),
                'valid_links': len(self.valid_links),
                'broken_links': len(self.broken_links)
            },
            'broken_links': self.broken_links,
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
