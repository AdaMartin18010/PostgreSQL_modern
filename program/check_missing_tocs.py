#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

def has_toc(content):
    """Check if file has a table of contents"""
    toc_patterns = [
        r'^##\s*[📑目录|目录|Table of Contents]',
        r'^##\s*目录',
        r'^#\s*目录',
        r'^##\s*📑',
        r'^##\s*Table of Contents',
        r'^\s*-\s*\[.*\]\(#.*\)',  # Markdown TOC format
    ]
    lines = content.split('\n')
    for i, line in enumerate(lines[:50]):  # Check first 50 lines
        for pattern in toc_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
    return False

def count_code_blocks(content):
    """Count code blocks in content"""
    return len(re.findall(r'```(?:python|rust|sql|c|java|go|javascript|typescript)', content, re.IGNORECASE))

def count_sections(content):
    """Count main sections (##)"""
    return len(re.findall(r'^##\s+', content, re.MULTILINE))

def analyze_file(filepath):
    """Analyze a markdown file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        has_toc_flag = has_toc(content)
        code_count = count_code_blocks(content)
        section_count = count_sections(content)
        line_count = len(content.split('\n'))

        # Check for case studies
        has_cases = bool(re.search(r'案例|实际应用|部署案例|应用场景', content))

        return {
            'has_toc': has_toc_flag,
            'code_count': code_count,
            'section_count': section_count,
            'line_count': line_count,
            'has_cases': has_cases
        }
    except Exception as e:
        return None

# Find all markdown files
base_dir = Path('DataBaseTheory/90-事务与并发设计理论体系')
md_files = list(base_dir.rglob('*.md'))

results = []
for md_file in md_files:
    if 'README' in md_file.name or '完整性检查' in md_file.name or '报告' in md_file.name:
        continue
    rel_path = md_file.relative_to(Path('DataBaseTheory'))
    analysis = analyze_file(md_file)
    if analysis:
        results.append((str(rel_path), analysis))

# Sort by missing TOC first, then by code count
results.sort(key=lambda x: (x[1]['has_toc'], -x[1]['code_count']))

print('Files missing TOC:')
print('=' * 80)
missing_toc = [r for r in results if not r[1]['has_toc']]
for path, data in missing_toc[:20]:
    print(f'{path}')
    print(f'  Sections: {data["section_count"]}, Code blocks: {data["code_count"]}, Lines: {data["line_count"]}, Has cases: {data["has_cases"]}')
    print()

print(f'\nTotal files missing TOC: {len(missing_toc)}')
print(f'Total files analyzed: {len(results)}')

# Files with low code count
print('\n\nFiles with low code content (need enrichment):')
print('=' * 80)
low_code = [r for r in results if r[1]['code_count'] < 3 and r[1]['section_count'] > 5]
for path, data in sorted(low_code, key=lambda x: x[1]['code_count'])[:15]:
    print(f'{path}')
    print(f'  Code blocks: {data["code_count"]}, Sections: {data["section_count"]}, Has cases: {data["has_cases"]}')
    print()
