#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL_Formal 链接验证工具
验证所有 Markdown 文件的内部链接、锚点链接和图片链接
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# 基础路径
BASE_DIR = Path("e:/_src/PostgreSQL_modern/PostgreSQL_Formal")
REPORT_FILE = BASE_DIR / "LINK_VERIFICATION_REPORT.md"

# 正则表达式模式
# 匹配 [text](link) 格式
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
# 匹配 [text]: link 格式 (参考式链接)
REF_LINK_PATTERN = re.compile(r'^\[([^\]]+)\]:\s*(\S+)', re.MULTILINE)
# 匹配 ![alt](path) 格式图片
IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
# 匹配 HTML <img> 标签
HTML_IMG_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
# 匹配锚点标题
HEADER_PATTERN = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
# 匹配标题的自定义锚点 {#anchor}
HEADER_ANCHOR_PATTERN = re.compile(r'^(#{1,6}\s+.+?)\s*\{#([^}]+)\}\s*$', re.MULTILINE)


def slugify(text):
    """将标题转换为 GitHub 风格的锚点 ID"""
    # 移除表情符号和特殊字符
    text = re.sub(r'[^\w\s-]', '', text.lower())
    # 替换空格为连字符
    text = re.sub(r'[\s]+', '-', text)
    # 移除重复的连字符
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def extract_all_md_files():
    """提取所有 Markdown 文件"""
    md_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        # 跳过 .git 和 node_modules 等目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules']]
        for file in files:
            if file.endswith('.md'):
                full_path = Path(root) / file
                md_files.append(full_path)
    return sorted(md_files)


def extract_links_from_file(file_path):
    """从文件中提取所有链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  警告: 无法读取文件 {file_path}: {e}")
        return [], [], [], []
    
    links = []
    images = []
    anchors = []
    ref_links = []
    
    # 提取行内链接 [text](url)
    for match in LINK_PATTERN.finditer(content):
        text = match.group(1)
        url = match.group(2)
        # 跳过图片
        start_pos = match.start()
        if start_pos > 0 and content[start_pos-1] == '!':
            continue
        links.append({
            'text': text,
            'url': url,
            'line': content[:start_pos].count('\n') + 1,
            'type': 'inline'
        })
    
    # 提取参考式链接 [text]: url
    for match in REF_LINK_PATTERN.finditer(content):
        text = match.group(1)
        url = match.group(2)
        ref_links.append({
            'text': text,
            'url': url,
            'line': content[:match.start()].count('\n') + 1,
            'type': 'reference'
        })
    
    # 提取图片 ![alt](path)
    for match in IMAGE_PATTERN.finditer(content):
        alt = match.group(1)
        path = match.group(2)
        images.append({
            'alt': alt,
            'path': path,
            'line': content[:match.start()].count('\n') + 1,
            'type': 'markdown'
        })
    
    # 提取 HTML 图片 <img src="...">
    for match in HTML_IMG_PATTERN.finditer(content):
        path = match.group(1)
        images.append({
            'alt': '',
            'path': path,
            'line': content[:match.start()].count('\n') + 1,
            'type': 'html'
        })
    
    # 提取标题锚点
    # 先找自定义锚点 {#anchor}
    for match in HEADER_ANCHOR_PATTERN.finditer(content):
        anchor = match.group(2)
        anchors.append(anchor)
    
    # 再找普通标题
    for match in HEADER_PATTERN.finditer(content):
        header_text = match.group(1).strip()
        # 移除行内标记
        header_text = re.sub(r'`([^`]+)`', r'\1', header_text)
        anchor = slugify(header_text)
        if anchor and anchor not in anchors:
            anchors.append(anchor)
    
    return links, images, anchors, ref_links


def classify_link(url):
    """分类链接类型"""
    if url.startswith('http://') or url.startswith('https://') or url.startswith('//'):
        return 'external'
    elif url.startswith('#'):
        return 'anchor'
    elif url.startswith('mailto:'):
        return 'mailto'
    elif url.startswith('tel:'):
        return 'tel'
    elif url.endswith('.md') or '.md#' in url:
        return 'internal_md'
    elif url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp')):
        return 'image_file'
    elif url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.tar', '.gz')):
        return 'attachment'
    elif url.startswith('./') or url.startswith('../') or (not url.startswith('/') and '.' in url):
        return 'relative_file'
    else:
        return 'other'


def resolve_link_path(source_file, url):
    """解析链接的完整路径"""
    if url.startswith('/'):
        # 绝对路径（相对于项目根）
        return BASE_DIR.parent / url.lstrip('/')
    else:
        # 相对路径
        return (source_file.parent / url).resolve()


def verify_link(source_file, link, all_files, all_anchors):
    """验证单个链接"""
    url = link['url']
    link_type = classify_link(url)
    
    result = {
        'link': link,
        'type': link_type,
        'status': 'unknown',
        'message': '',
        'suggestion': ''
    }
    
    if link_type == 'external':
        result['status'] = 'skipped'
        result['message'] = '外部链接（未验证）'
    
    elif link_type == 'mailto' or link_type == 'tel':
        result['status'] = 'valid'
        result['message'] = '邮件/电话链接'
    
    elif link_type == 'anchor':
        anchor = url[1:]  # 移除 #
        source_rel = str(source_file.relative_to(BASE_DIR))
        if source_rel in all_anchors:
            if anchor in all_anchors[source_rel]:
                result['status'] = 'valid'
                result['message'] = f'锚点存在: #{anchor}'
            else:
                result['status'] = 'invalid'
                result['message'] = f'锚点不存在: #{anchor}'
                # 尝试提供建议
                similar = [a for a in all_anchors[source_rel] if anchor.lower() in a.lower() or a.lower() in anchor.lower()]
                if similar:
                    result['suggestion'] = f'可能的锚点: #{similar[0]}'
        else:
            result['status'] = 'warning'
            result['message'] = '无法获取文件锚点信息'
    
    elif link_type in ('internal_md', 'relative_file', 'image_file', 'attachment'):
        # 分离路径和锚点
        if '#' in url:
            file_part, anchor = url.split('#', 1)
        else:
            file_part, anchor = url, None
        
        if not file_part:
            # 纯锚点链接，指向当前文件
            source_rel = str(source_file.relative_to(BASE_DIR))
            if source_rel in all_anchors and anchor:
                if anchor in all_anchors[source_rel]:
                    result['status'] = 'valid'
                    result['message'] = f'锚点存在: #{anchor}'
                else:
                    result['status'] = 'invalid'
                    result['message'] = f'锚点不存在: #{anchor}'
            elif not anchor:
                result['status'] = 'valid'
                result['message'] = '链接到当前文件'
            else:
                result['status'] = 'warning'
                result['message'] = '无法验证锚点'
        else:
            # 解析目标路径
            try:
                target_path = resolve_link_path(source_file, file_part)
                target_rel = target_path.relative_to(BASE_DIR)
                target_str = str(target_rel).replace('\\', '/')
                
                if target_path.exists():
                    if anchor:
                        # 需要验证锚点
                        if target_str in all_anchors:
                            if anchor in all_anchors[target_str]:
                                result['status'] = 'valid'
                                result['message'] = f'文件和锚点都存在: {target_str}#{anchor}'
                            else:
                                result['status'] = 'invalid'
                                result['message'] = f'文件存在但锚点不存在: #{anchor}'
                                similar = [a for a in all_anchors[target_str] if anchor.lower() in a.lower() or a.lower() in anchor.lower()]
                                if similar:
                                    result['suggestion'] = f'可能的锚点: #{similar[0]}'
                        else:
                            result['status'] = 'warning'
                            result['message'] = '文件存在但无法验证锚点'
                    else:
                        result['status'] = 'valid'
                        result['message'] = f'文件存在: {target_str}'
                else:
                    result['status'] = 'invalid'
                    result['message'] = f'文件不存在: {target_str}'
                    # 尝试提供修复建议
                    dir_name = target_path.parent.name
                    file_name = target_path.name
                    # 在当前目录查找
                    alt_path = source_file.parent / file_name
                    if alt_path.exists():
                        rel_path = alt_path.relative_to(source_file.parent)
                        result['suggestion'] = f'改为: ./{rel_path}'
                    # 在其他位置查找
                    for f in all_files:
                        if f.name == file_name:
                            try:
                                rel_path = f.relative_to(source_file.parent)
                                result['suggestion'] = f'改为: ./{rel_path}'
                                break
                            except:
                                pass
            except Exception as e:
                result['status'] = 'error'
                result['message'] = f'路径解析错误: {e}'
    
    else:
        result['status'] = 'unknown'
        result['message'] = f'未知链接类型: {link_type}'
    
    return result


def verify_image(source_file, image):
    """验证图片链接"""
    path = image['path']
    result = {
        'image': image,
        'status': 'unknown',
        'message': '',
        'suggestion': ''
    }
    
    if path.startswith('http://') or path.startswith('https://'):
        result['status'] = 'skipped'
        result['message'] = '外部图片（未验证）'
    elif path.startswith('data:'):
        result['status'] = 'valid'
        result['message'] = 'Data URI 图片'
    else:
        try:
            target_path = resolve_link_path(source_file, path)
            if target_path.exists():
                result['status'] = 'valid'
                result['message'] = f'图片存在: {path}'
            else:
                result['status'] = 'invalid'
                result['message'] = f'图片不存在: {path}'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'路径解析错误: {e}'
    
    return result


def main():
    print("=" * 60)
    print("PostgreSQL_Formal 链接验证工具")
    print("=" * 60)
    
    # 第1步: 扫描所有文件
    print("\n[1/4] 扫描所有 Markdown 文件...")
    md_files = extract_all_md_files()
    print(f"  发现 {len(md_files)} 个 Markdown 文件")
    
    # 第2步: 提取所有链接和锚点
    print("\n[2/4] 提取链接和锚点...")
    all_links = {}  # file -> list of links
    all_images = {}  # file -> list of images
    all_anchors = {}  # file -> list of anchors
    all_ref_links = {}  # file -> list of ref links
    
    for file_path in md_files:
        rel_path = str(file_path.relative_to(BASE_DIR))
        links, images, anchors, ref_links = extract_links_from_file(file_path)
        if links:
            all_links[rel_path] = links
        if images:
            all_images[rel_path] = images
        if anchors:
            all_anchors[rel_path] = anchors
        if ref_links:
            all_ref_links[rel_path] = ref_links
    
    print(f"  发现 {sum(len(v) for v in all_links.values())} 个行内链接")
    print(f"  发现 {sum(len(v) for v in all_ref_links.values())} 个参考式链接")
    print(f"  发现 {sum(len(v) for v in all_images.values())} 个图片")
    print(f"  发现 {sum(len(v) for v in all_anchors.values())} 个标题锚点")
    
    # 第3步: 验证链接
    print("\n[3/4] 验证链接...")
    link_results = []
    image_results = []
    
    for file_path in md_files:
        rel_path = str(file_path.relative_to(BASE_DIR))
        
        # 验证行内链接
        if rel_path in all_links:
            for link in all_links[rel_path]:
                result = verify_link(file_path, link, md_files, all_anchors)
                result['source_file'] = rel_path
                link_results.append(result)
        
        # 验证参考式链接
        if rel_path in all_ref_links:
            for link in all_ref_links[rel_path]:
                result = verify_link(file_path, link, md_files, all_anchors)
                result['source_file'] = rel_path
                link_results.append(result)
        
        # 验证图片
        if rel_path in all_images:
            for image in all_images[rel_path]:
                result = verify_image(file_path, image)
                result['source_file'] = rel_path
                image_results.append(result)
    
    print(f"  已验证 {len(link_results)} 个链接")
    print(f"  已验证 {len(image_results)} 个图片")
    
    # 统计
    link_stats = {
        'valid': sum(1 for r in link_results if r['status'] == 'valid'),
        'invalid': sum(1 for r in link_results if r['status'] == 'invalid'),
        'warning': sum(1 for r in link_results if r['status'] == 'warning'),
        'skipped': sum(1 for r in link_results if r['status'] == 'skipped'),
        'error': sum(1 for r in link_results if r['status'] == 'error'),
        'unknown': sum(1 for r in link_results if r['status'] == 'unknown'),
    }
    
    image_stats = {
        'valid': sum(1 for r in image_results if r['status'] == 'valid'),
        'invalid': sum(1 for r in image_results if r['status'] == 'invalid'),
        'warning': sum(1 for r in image_results if r['status'] == 'warning'),
        'skipped': sum(1 for r in image_results if r['status'] == 'skipped'),
        'error': sum(1 for r in image_results if r['status'] == 'error'),
    }
    
    print(f"\n  链接统计: 有效={link_stats['valid']}, 失效={link_stats['invalid']}, "
          f"警告={link_stats['warning']}, 跳过={link_stats['skipped']}")
    print(f"  图片统计: 有效={image_stats['valid']}, 失效={image_stats['invalid']}, "
          f"警告={image_stats['warning']}, 跳过={image_stats['skipped']}")
    
    # 第4步: 生成报告
    print("\n[4/4] 生成报告...")
    generate_report(
        md_files, 
        all_links, 
        all_images, 
        all_anchors,
        link_results, 
        image_results, 
        link_stats, 
        image_stats
    )
    print(f"  报告已保存: {REPORT_FILE}")
    
    print("\n" + "=" * 60)
    print("验证完成!")
    print("=" * 60)
    
    return link_stats, image_stats


def generate_report(md_files, all_links, all_images, all_anchors, link_results, image_results, link_stats, image_stats):
    """生成 Markdown 报告"""
    
    # 收集失效链接
    invalid_links = [r for r in link_results if r['status'] == 'invalid']
    warning_links = [r for r in link_results if r['status'] == 'warning']
    invalid_images = [r for r in image_results if r['status'] == 'invalid']
    warning_images = [r for r in image_results if r['status'] == 'warning']
    
    # 按文件分组
    invalid_by_file = defaultdict(list)
    for r in invalid_links:
        invalid_by_file[r['source_file']].append(r)
    for r in invalid_images:
        invalid_by_file[r['source_file']].append(r)
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# PostgreSQL_Formal 链接验证报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 统计信息
        f.write("## 统计信息\n\n")
        f.write("| 指标 | 数值 |\n")
        f.write("|------|------|\n")
        f.write(f"| 总文档数 | {len(md_files)} |\n")
        f.write(f"| 总链接数 | {len(link_results)} |\n")
        f.write(f"| 总图片数 | {len(image_results)} |\n")
        f.write(f"| **有效链接** | **{link_stats['valid'] + link_stats['skipped']}** |\n")
        f.write(f"| **失效链接** | **{link_stats['invalid']}** |\n")
        f.write(f"| **警告链接** | **{link_stats['warning']}** |\n")
        f.write(f"| 有效图片 | {image_stats['valid'] + image_stats['skipped']} |\n")
        f.write(f"| 失效图片 | {image_stats['invalid']} |\n")
        f.write(f"| 警告图片 | {image_stats['warning']} |\n\n")
        
        # 详细统计
        f.write("### 链接分类统计\n\n")
        f.write("| 类型 | 数量 |\n")
        f.write("|------|------|\n")
        link_types = defaultdict(int)
        for r in link_results:
            link_types[r['type']] += 1
        for t, c in sorted(link_types.items(), key=lambda x: -x[1]):
            f.write(f"| {t} | {c} |\n")
        f.write("\n")
        
        # 失效链接详情
        f.write("## 失效链接详情\n\n")
        if invalid_links:
            f.write("| 源文件 | 行号 | 失效链接 | 链接文本 | 建议修复 |\n")
            f.write("|--------|------|----------|----------|----------|\n")
            for r in invalid_links:
                source = r['source_file']
                line = r['link'].get('line', '-')
                url = r['link']['url']
                text = r['link']['text'][:30] + '...' if len(r['link']['text']) > 30 else r['link']['text']
                suggestion = r.get('suggestion', '')
                f.write(f"| {source} | {line} | `{url}` | {text} | {suggestion} |\n")
        else:
            f.write("✅ **没有发现失效链接！**\n\n")
        
        f.write("\n")
        
        # 失效图片详情
        if invalid_images:
            f.write("## 失效图片详情\n\n")
            f.write("| 源文件 | 行号 | 失效路径 | 建议修复 |\n")
            f.write("|--------|------|----------|----------|\n")
            for r in invalid_images:
                source = r['source_file']
                line = r['image'].get('line', '-')
                path = r['image']['path']
                suggestion = r.get('suggestion', '')
                f.write(f"| {source} | {line} | `{path}` | {suggestion} |\n")
            f.write("\n")
        
        # 警告链接
        if warning_links:
            f.write("## 警告链接详情\n\n")
            f.write("| 源文件 | 行号 | 警告链接 | 警告信息 |\n")
            f.write("|--------|------|----------|----------|\n")
            for r in warning_links[:50]:  # 只显示前50个
                source = r['source_file']
                line = r['link'].get('line', '-')
                url = r['link']['url']
                msg = r['message']
                f.write(f"| {source} | {line} | `{url}` | {msg} |\n")
            if len(warning_links) > 50:
                f.write(f"| ... | ... | ... | 还有 {len(warning_links) - 50} 个警告... |\n")
            f.write("\n")
        
        # 需要修复的文件列表
        f.write("## 需要修复的文件列表\n\n")
        if invalid_by_file:
            # 按失效链接数量排序
            sorted_files = sorted(invalid_by_file.items(), key=lambda x: -len(x[1]))
            f.write("| 文件 | 失效链接数 | 状态 |\n")
            f.write("|------|------------|------|\n")
            for file, results in sorted_files:
                count = len(results)
                f.write(f"| {file} | {count} | [ ] 待修复 |\n")
            f.write("\n")
        else:
            f.write("✅ **所有文件的链接都有效！**\n\n")
        
        # 链接最多的文件
        f.write("## 链接最多的文件（Top 20）\n\n")
        file_link_counts = []
        for file_path in all_links:
            count = len(all_links[file_path])
            file_link_counts.append((file_path, count))
        file_link_counts.sort(key=lambda x: -x[1])
        
        f.write("| 文件 | 链接数 |\n")
        f.write("|------|--------|\n")
        for file, count in file_link_counts[:20]:
            f.write(f"| {file} | {count} |\n")
        f.write("\n")
        
        # 常见问题模式
        if invalid_links:
            f.write("## 常见问题模式\n\n")
            
            # 分析常见问题
            missing_anchors = [r for r in invalid_links if '锚点不存在' in r['message']]
            missing_files = [r for r in invalid_links if '文件不存在' in r['message']]
            
            if missing_anchors:
                f.write(f"### 锚点错误 ({len(missing_anchors)} 个)\n\n")
                f.write("链接指向的锚点在目标文件中不存在。常见原因:\n")
                f.write("- 标题被修改但链接未更新\n")
                f.write("- 锚点名称拼写错误\n")
                f.write("- 使用了中文标题但锚点是英文\n\n")
            
            if missing_files:
                f.write(f"### 文件不存在错误 ({len(missing_files)} 个)\n\n")
                f.write("链接指向的文件不存在。常见原因:\n")
                f.write("- 文件被移动或删除\n")
                f.write("- 路径拼写错误\n")
                f.write("- 相对路径计算错误\n\n")
        
        # 修复建议
        f.write("## 修复建议\n\n")
        f.write("### 自动修复\n\n")
        
        auto_fixable = [r for r in invalid_links if r.get('suggestion')]
        if auto_fixable:
            f.write(f"发现 {len(auto_fixable)} 个可能可以自动修复的链接:\n\n")
            for r in auto_fixable[:10]:
                f.write(f"- `{r['source_file']}`: `{r['link']['url']}` -> {r['suggestion']}\n")
            if len(auto_fixable) > 10:
                f.write(f"- ... 还有 {len(auto_fixable) - 10} 个\n")
        else:
            f.write("没有明显可以自动修复的简单路径错误。\n")
        
        f.write("\n### 手动修复步骤\n\n")
        f.write("1. 查看上面的**失效链接详情**表格\n")
        f.write("2. 对于每个失效链接，打开源文件定位到对应行\n")
        f.write("3. 根据实际情况修复:\n")
        f.write("   - 如果是路径错误，修正相对路径\n")
        f.write("   - 如果是锚点错误，更新为正确的标题锚点\n")
        f.write("   - 如果目标文件已删除，移除链接或指向新位置\n")
        f.write("4. 修复后重新运行本验证工具确认\n\n")
        
        # 附录: 所有文档的锚点列表
        f.write("## 附录: 文档锚点索引\n\n")
        f.write("<details>\n<summary>点击查看所有文档的锚点列表（用于参考）</summary>\n\n")
        for file_path, anchors in sorted(all_anchors.items()):
            if anchors:
                f.write(f"### {file_path}\n\n")
                for anchor in anchors[:20]:  # 每个文件最多显示20个
                    f.write(f"- `#{anchor}`\n")
                if len(anchors) > 20:
                    f.write(f"- ... 还有 {len(anchors) - 20} 个锚点\n")
                f.write("\n")
        f.write("</details>\n\n")
    
    print(f"  报告详情:")
    print(f"    - 失效链接: {len(invalid_links)}")
    print(f"    - 警告链接: {len(warning_links)}")
    print(f"    - 失效图片: {len(invalid_images)}")
    print(f"    - 需要修复的文件: {len(invalid_by_file)}")


if __name__ == '__main__':
    main()
