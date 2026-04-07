#!/usr/bin/env python3
"""
PostgreSQL_Formal 知识图谱可视化生成器

功能:
1. 读取 KNOWLEDGE_GRAPH.yml
2. 生成 Mermaid 流程图
3. 生成 HTML 可视化页面
4. 生成 Markdown 导航文档

使用方法:
    python generate-graph.py [--output-dir OUTPUT_DIR] [--format FORMAT]

示例:
    python generate-graph.py --output-dir ../visualization --format all
    python generate-graph.py --format mermaid
    python generate-graph.py --format html
"""

import argparse
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加父目录到路径以支持直接运行
sys.path.insert(0, str(Path(__file__).parent))


class KnowledgeGraphVisualizer:
    """知识图谱可视化生成器"""
    
    def __init__(self, yaml_path: str):
        """初始化可视化器
        
        Args:
            yaml_path: KNOWLEDGE_GRAPH.yml 文件路径
        """
        self.yaml_path = Path(yaml_path)
        self.data = self._load_yaml()
        self.output_dir = Path(__file__).parent.parent / "visualization"
        
    def _load_yaml(self) -> Dict[str, Any]:
        """加载 YAML 数据"""
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_mermaid_concept_graph(self) -> str:
        """生成概念关系 Mermaid 图
        
        Returns:
            Mermaid 图定义字符串
        """
        lines = ["```mermaid", "graph TB"]
        
        concepts = self.data.get('concepts', [])
        
        # 定义子图（按类别分组）
        categories = {}
        for concept in concepts:
            cat = concept.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(concept)
        
        # 生成节点定义
        for concept in concepts:
            cid = concept['id']
            name = concept['name']
            difficulty = concept.get('difficulty', 'intermediate')
            
            # 根据难度设置样式
            style_class = f"class:{difficulty}"
            lines.append(f"    {cid}[\"{name}\"]")
        
        lines.append("")
        
        # 生成关系边
        for concept in concepts:
            cid = concept['id']
            for related in concept.get('related', []):
                lines.append(f"    {cid} --> {related}")
        
        # 添加文档关系
        relationships = self.data.get('relationships', [])
        for rel in relationships:
            from_node = self._doc_to_node(rel['from'])
            to_node = self._doc_to_node(rel['to'])
            rel_type = rel.get('type', 'related')
            
            if rel_type == 'prerequisite':
                lines.append(f"    {to_node} -.->|prereq| {from_node}")
            elif rel_type == 'extends':
                lines.append(f"    {from_node} ==>|extends| {to_node}")
            elif rel_type == 'contrasts':
                lines.append(f"    {from_node} -.->|contrasts| {to_node}")
            else:
                lines.append(f"    {from_node} --> {to_node}")
        
        # 添加样式类定义
        lines.extend([
            "",
            "    classDef beginner fill:#90EE90,stroke:#228B22",
            "    classDef intermediate fill:#FFD700,stroke:#FFA500",
            "    classDef advanced fill:#FF6B6B,stroke:#DC143C",
            "    classDef expert fill:#DDA0DD,stroke:#8B008B",
        ])
        
        lines.append("```")
        return '\n'.join(lines)
    
    def generate_mermaid_learning_path(self, path_id: str) -> Optional[str]:
        """生成学习路径 Mermaid 图
        
        Args:
            path_id: 学习路径 ID
            
        Returns:
            Mermaid 图定义字符串
        """
        learning_paths = self.data.get('learning_paths', {})
        if path_id not in learning_paths:
            return None
            
        path = learning_paths[path_id]
        lines = ["```mermaid", "flowchart LR"]
        
        steps = path.get('steps', [])
        prev_node = None
        
        for i, step in enumerate(steps):
            step_id = f"step_{i}"
            step_name = step.get('name', f'步骤 {i+1}')
            
            lines.append(f'    {step_id}["{step_name}"]')
            
            if prev_node:
                lines.append(f"    {prev_node} --> {step_id}")
            
            prev_node = step_id
            
            # 添加子文档
            docs = step.get('documents', [])
            for j, doc in enumerate(docs):
                doc_node = f"doc_{i}_{j}"
                doc_name = Path(doc).stem
                lines.append(f'    {doc_node}["{doc_name}"]')
                lines.append(f"    {step_id} -.-> {doc_node}")
        
        lines.append("```")
        return '\n'.join(lines)
    
    def generate_mermaid_category_matrix(self) -> str:
        """生成分类矩阵 Mermaid 图
        
        Returns:
            Mermaid 图定义字符串
        """
        lines = ["```mermaid", "mindmap"]
        
        categories = self.data.get('categories', {})
        
        lines.append("  root((PostgreSQL_Formal))")
        
        for cat_id, cat_data in categories.items():
            cat_name = cat_data.get('name', cat_id)
            lines.append(f"    {cat_name}")
            
            docs = cat_data.get('documents', [])
            for doc in docs[:5]:  # 限制显示数量
                doc_name = Path(doc).stem[:30]
                lines.append(f"      {doc_name}")
        
        lines.append("```")
        return '\n'.join(lines)
    
    def _doc_to_node(self, doc_path: str) -> str:
        """将文档路径转换为节点 ID
        
        Args:
            doc_path: 文档路径
            
        Returns:
            节点 ID
        """
        # 尝试匹配概念
        concepts = self.data.get('concepts', [])
        for concept in concepts:
            if doc_path in concept.get('documents', []):
                return concept['id']
        
        # 返回简化路径
        return Path(doc_path).stem.replace('-', '_').replace('.', '_')
    
    def generate_html_visualization(self) -> str:
        """生成 HTML 可视化页面
        
        Returns:
            HTML 页面内容
        """
        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PostgreSQL_Formal 知识图谱</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            padding: 40px 0;
            color: white;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-card .label {{
            color: #666;
            margin-top: 5px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #333;
            margin-bottom: 16px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .card h3 {{
            color: #555;
            margin: 20px 0 10px 0;
        }}
        
        .mermaid {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }}
        
        .concept-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}
        
        .concept-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }}
        
        .concept-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateX(5px);
        }}
        
        .concept-card h4 {{
            color: #333;
            margin-bottom: 8px;
        }}
        
        .concept-card p {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }}
        
        .concept-card .meta {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        .badge-beginner {{ background: #90EE90; color: #228B22; }}
        .badge-intermediate {{ background: #FFD700; color: #8B7508; }}
        .badge-advanced {{ background: #FF6B6B; color: #8B0000; }}
        .badge-expert {{ background: #DDA0DD; color: #8B008B; }}
        
        .badge-category {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .path-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        
        .path-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            border-left: 4px solid #28a745;
        }}
        
        .path-item h4 {{
            color: #333;
            margin-bottom: 8px;
        }}
        
        .path-item p {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }}
        
        .path-steps {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}
        
        .step-badge {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.85rem;
        }}
        
        .step-arrow {{
            color: #999;
        }}
        
        .category-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }}
        
        .category-item {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 16px;
            border-top: 4px solid #764ba2;
        }}
        
        .category-item h4 {{
            color: #333;
            margin-bottom: 8px;
        }}
        
        .category-item p {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }}
        
        .doc-count {{
            color: #999;
            font-size: 0.85rem;
        }}
        
        footer {{
            text-align: center;
            padding: 30px;
            color: white;
            opacity: 0.8;
        }}
        
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .tab {{
            padding: 10px 20px;
            background: none;
            border: none;
            cursor: pointer;
            color: #666;
            font-size: 1rem;
            transition: all 0.3s;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }}
        
        .tab:hover {{
            color: #667eea;
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8rem;
            }}
            
            .concept-grid,
            .category-list {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐘 PostgreSQL_Formal 知识图谱</h1>
            <p>建立文档关联，规划学习路径，掌握 PostgreSQL 核心技术</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{total_concepts}</div>
                <div class="label">核心概念</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_docs}</div>
                <div class="label">技术文档</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_paths}</div>
                <div class="label">学习路径</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_categories}</div>
                <div class="label">主题分类</div>
            </div>
        </div>
        
        <div class="card">
            <div class="tabs">
                <button class="tab active" onclick="showTab('concepts')">核心概念</button>
                <button class="tab" onclick="showTab('paths')">学习路径</button>
                <button class="tab" onclick="showTab('categories')">主题分类</button>
                <button class="tab" onclick="showTab('graph')">关系图谱</button>
            </div>
            
            <div id="concepts" class="tab-content active">
                <h2>核心概念</h2>
                <div class="concept-grid">
                    {concept_cards}
                </div>
            </div>
            
            <div id="paths" class="tab-content">
                <h2>学习路径</h2>
                <div class="path-list">
                    {path_cards}
                </div>
            </div>
            
            <div id="categories" class="tab-content">
                <h2>主题分类</h2>
                <div class="category-list">
                    {category_cards}
                </div>
            </div>
            
            <div id="graph" class="tab-content">
                <h2>概念关系图谱</h2>
                <div class="mermaid">
{concept_graph}
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>版本特性矩阵</h2>
            <div class="mermaid">
{version_matrix}
            </div>
        </div>
        
        <footer>
            <p>最后更新: {last_updated} | PostgreSQL_Formal 知识图谱 v{version}</p>
        </footer>
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        }});
        
        function showTab(tabId) {{
            // 隐藏所有内容
            document.querySelectorAll('.tab-content').forEach(el => {{
                el.classList.remove('active');
            }});
            
            // 移除所有活动标签
            document.querySelectorAll('.tab').forEach(el => {{
                el.classList.remove('active');
            }});
            
            // 显示选中内容
            document.getElementById(tabId).classList.add('active');
            
            // 激活对应标签
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
'''
        
        # 统计数据
        metadata = self.data.get('metadata', {})
        concepts = self.data.get('concepts', [])
        categories = self.data.get('categories', {})
        learning_paths = self.data.get('learning_paths', {})
        
        total_concepts = len(concepts)
        total_docs = metadata.get('total_documents', 194)
        total_paths = len(learning_paths)
        total_categories = len(categories)
        last_updated = metadata.get('last_updated', datetime.now().strftime('%Y-%m-%d'))
        version = metadata.get('version', '1.0.0')
        
        # 生成概念卡片
        concept_cards = []
        for concept in concepts:
            difficulty = concept.get('difficulty', 'intermediate')
            doc_count = len(concept.get('documents', []))
            
            card = f'''
            <div class="concept-card">
                <h4>{concept['name']}</h4>
                <p>{concept.get('description', '')}</p>
                <div class="meta">
                    <span class="badge badge-{difficulty}">{difficulty}</span>
                    <span class="badge badge-category">{concept.get('category', 'other')}</span>
                    <span class="doc-count">{doc_count} 篇文档</span>
                </div>
            </div>'''
            concept_cards.append(card)
        
        # 生成学习路径卡片
        path_cards = []
        for path_id, path in learning_paths.items():
            steps = path.get('steps', [])
            step_html = []
            for i, step in enumerate(steps):
                step_html.append(f'<span class="step-badge">{step.get("name", f"步骤 {i+1}")}</span>')
                if i < len(steps) - 1:
                    step_html.append('<span class="step-arrow">→</span>')
            
            card = f'''
            <div class="path-item">
                <h4>{path['name']}</h4>
                <p>{path.get('description', '')}</p>
                <p><small>目标受众: {path.get('target_audience', '通用')} | 预计学时: {path.get('estimated_hours', 'N/A')} 小时</small></p>
                <div class="path-steps">{''.join(step_html)}</div>
            </div>'''
            path_cards.append(card)
        
        # 生成分类卡片
        category_cards = []
        for cat_id, cat in categories.items():
            doc_count = len(cat.get('documents', []))
            
            card = f'''
            <div class="category-item">
                <h4>{cat['name']}</h4>
                <p>{cat.get('description', '')}</p>
                <span class="doc-count">{doc_count} 篇文档</span>
            </div>'''
            category_cards.append(card)
        
        # 生成 Mermaid 图
        concept_graph = self.generate_mermaid_concept_graph().replace('```mermaid\n', '').replace('\n```', '')
        version_matrix = self.generate_mermaid_category_matrix().replace('```mermaid\n', '').replace('\n```', '')
        
        # 填充模板
        html = html_template.format(
            total_concepts=total_concepts,
            total_docs=total_docs,
            total_paths=total_paths,
            total_categories=total_categories,
            last_updated=last_updated,
            version=version,
            concept_cards=''.join(concept_cards),
            path_cards=''.join(path_cards),
            category_cards=''.join(category_cards),
            concept_graph=concept_graph,
            version_matrix=version_matrix
        )
        
        return html
    
    def generate_markdown_nav(self) -> str:
        """生成 Markdown 导航文档
        
        Returns:
            Markdown 内容
        """
        lines = [
            "# PostgreSQL_Formal 知识图谱导航",
            "",
            f"> 📊 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📑 目录",
            "",
            "- [核心概念](#核心概念)",
            "- [学习路径](#学习路径)",
            "- [主题分类](#主题分类)",
            "- [版本特性](#版本特性)",
            "- [关系图谱](#关系图谱)",
            "",
            "---",
            "",
            "## 🧠 核心概念",
            ""
        ]
        
        # 按类别分组概念
        concepts_by_category = {}
        for concept in self.data.get('concepts', []):
            cat = concept.get('category', 'other')
            if cat not in concepts_by_category:
                concepts_by_category[cat] = []
            concepts_by_category[cat].append(concept)
        
        # 生成分组概念列表
        for cat, concepts in sorted(concepts_by_category.items()):
            cat_name = cat.replace('_', ' ').title()
            lines.append(f"### {cat_name}")
            lines.append("")
            
            for concept in concepts:
                difficulty = concept.get('difficulty', 'intermediate')
                difficulty_emoji = {
                    'beginner': '🟢',
                    'intermediate': '🟡',
                    'advanced': '🔴',
                    'expert': '⚫'
                }.get(difficulty, '⚪')
                
                lines.append(f"- {difficulty_emoji} **{concept['name']}** - {concept.get('description', '')}")
                
                # 添加文档链接
                for doc in concept.get('documents', [])[:2]:  # 限制显示数量
                    lines.append(f"  - [{Path(doc).name}]({doc})")
            
            lines.append("")
        
        # 学习路径
        lines.extend([
            "---",
            "",
            "## 🎯 学习路径",
            ""
        ])
        
        for path_id, path in self.data.get('learning_paths', {}).items():
            lines.append(f"### {path['name']}")
            lines.append(f"**目标受众:** {path.get('target_audience', '通用')}  ")
            lines.append(f"**预计学时:** {path.get('estimated_hours', 'N/A')} 小时")
            lines.append("")
            lines.append(f"{path.get('description', '')}")
            lines.append("")
            
            for i, step in enumerate(path.get('steps', [])):
                lines.append(f"{i+1}. **{step.get('name', f'步骤 {i+1}')}**")
                for doc in step.get('documents', []):
                    lines.append(f"   - [{Path(doc).name}]({doc})")
            lines.append("")
        
        # 主题分类
        lines.extend([
            "---",
            "",
            "## 📂 主题分类",
            ""
        ])
        
        for cat_id, cat in self.data.get('categories', {}).items():
            lines.append(f"### {cat['name']}")
            lines.append(f"{cat.get('description', '')}")
            lines.append("")
            lines.append(f"*包含 {len(cat.get('documents', []))} 篇文档*")
            lines.append("")
        
        # 版本特性
        lines.extend([
            "---",
            "",
            "## 📦 版本特性",
            ""
        ])
        
        version_matrix = self.data.get('version_matrix', {})
        for ver_id, ver_data in version_matrix.items():
            status_emoji = "✅" if ver_data.get('status') == 'released' else "🚧"
            lines.append(f"### {status_emoji} PostgreSQL {ver_data['version']}")
            
            if 'release_date' in ver_data:
                lines.append(f"**发布时间:** {ver_data['release_date']}")
            if 'expected_release' in ver_data:
                lines.append(f"**预计发布:** {ver_data['expected_release']}")
            
            lines.append("")
            lines.append("| 特性 | 分类 | 文档 |")
            lines.append("|------|------|------|")
            
            for feature in ver_data.get('features', []):
                lines.append(f"| {feature['name']} | {feature.get('category', 'N/A')} | [{Path(feature['document']).name}]({feature['document']}) |")
            
            lines.append("")
        
        # 关系图谱
        lines.extend([
            "---",
            "",
            "## 🕸️ 关系图谱",
            ""
        ])
        
        lines.append("### 概念关系图")
        lines.append("")
        lines.append(self.generate_mermaid_concept_graph())
        lines.append("")
        
        # 学习路径图
        lines.append("### 学习路径图")
        lines.append("")
        for path_id in self.data.get('learning_paths', {}).keys():
            mermaid = self.generate_mermaid_learning_path(path_id)
            if mermaid:
                lines.append(f"**{path_id}**")
                lines.append("")
                lines.append(mermaid)
                lines.append("")
        
        # 添加图例
        lines.extend([
            "---",
            "",
            "## 📖 图例",
            "",
            "### 难度标识",
            "",
            "| 标识 | 难度级别 | 说明 |",
            "|------|----------|------|",
            "| 🟢 | Beginner | 入门级，适合初学者 |",
            "| 🟡 | Intermediate | 中级，需要一定基础 |",
            "| 🔴 | Advanced | 高级，深入内部实现 |",
            "| ⚫ | Expert | 专家级，形式化分析 |",
            "",
            "### 关系类型",
            "",
            "| 符号 | 含义 |",
            "|------|------|",
            "| `-->` | 相关概念 |",
            "| `-.->` | 前置依赖 |",
            "| `==>` | 扩展/实现 |",
            "| `-.->\|contrasts\|` | 对比/替代 |"
        ])
        
        return '\n'.join(lines)
    
    def save_mermaid(self, output_path: str = None):
        """保存 Mermaid 图到文件
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.output_dir / "knowledge-graph.mmd"
        
        self._ensure_output_dir()
        
        content = self.generate_mermaid_concept_graph()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Mermaid 图已保存: {output_path}")
    
    def save_html(self, output_path: str = None):
        """保存 HTML 可视化页面
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.output_dir / "knowledge-graph.html"
        
        self._ensure_output_dir()
        
        content = self.generate_html_visualization()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ HTML 页面已保存: {output_path}")
    
    def save_markdown(self, output_path: str = None):
        """保存 Markdown 导航文档
        
        Args:
            output_path: 输出文件路径
        """
        if output_path is None:
            output_path = self.output_dir / "KNOWLEDGE-NAV.md"
        
        self._ensure_output_dir()
        
        content = self.generate_markdown_nav()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Markdown 导航已保存: {output_path}")
    
    def generate_all(self):
        """生成所有可视化输出"""
        print("🚀 开始生成 PostgreSQL_Formal 知识图谱可视化...")
        print(f"📂 输出目录: {self.output_dir}")
        print()
        
        self.save_mermaid()
        self.save_html()
        self.save_markdown()
        
        print()
        print("✨ 所有可视化文件生成完成!")
        print()
        print("生成文件:")
        print(f"  1. Mermaid 图: {self.output_dir / 'knowledge-graph.mmd'}")
        print(f"  2. HTML 页面: {self.output_dir / 'knowledge-graph.html'}")
        print(f"  3. Markdown 导航: {self.output_dir / 'KNOWLEDGE-NAV.md'}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PostgreSQL_Formal 知识图谱可视化生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 生成所有可视化
  python generate-graph.py
  
  # 指定输出目录
  python generate-graph.py --output-dir ./my-output
  
  # 仅生成 Mermaid
  python generate-graph.py --format mermaid
  
  # 仅生成 HTML
  python generate-graph.py --format html
  
  # 仅生成 Markdown
  python generate-graph.py --format markdown
        '''
    )
    
    parser.add_argument(
        '--yaml', '-y',
        default='../KNOWLEDGE_GRAPH.yml',
        help='KNOWLEDGE_GRAPH.yml 文件路径 (默认: ../KNOWLEDGE_GRAPH.yml)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='输出目录 (默认: ../visualization/)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['all', 'mermaid', 'html', 'markdown'],
        default='all',
        help='输出格式 (默认: all)'
    )
    
    args = parser.parse_args()
    
    # 确定 YAML 路径
    yaml_path = Path(args.yaml)
    if not yaml_path.is_absolute():
        yaml_path = Path(__file__).parent / yaml_path
    
    if not yaml_path.exists():
        # 尝试其他路径
        alt_path = Path(__file__).parent.parent / 'KNOWLEDGE_GRAPH.yml'
        if alt_path.exists():
            yaml_path = alt_path
        else:
            print(f"❌ 错误: 找不到知识图谱文件: {yaml_path}")
            sys.exit(1)
    
    # 创建可视化器
    visualizer = KnowledgeGraphVisualizer(str(yaml_path))
    
    # 设置输出目录
    if args.output_dir:
        visualizer.output_dir = Path(args.output_dir)
    
    # 生成指定格式
    print(f"📖 加载知识图谱: {yaml_path}")
    print()
    
    if args.format == 'all':
        visualizer.generate_all()
    elif args.format == 'mermaid':
        visualizer.save_mermaid()
    elif args.format == 'html':
        visualizer.save_html()
    elif args.format == 'markdown':
        visualizer.save_markdown()


if __name__ == '__main__':
    main()
