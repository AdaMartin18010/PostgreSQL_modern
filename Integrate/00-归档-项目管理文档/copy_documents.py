#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档复制脚本
将源目录的文档复制到Integrate主题目录，并添加来源信息
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
INTEGRATE_DIR = ROOT_DIR / "Integrate"

# 文档映射规则 - 单个文件映射
DOCUMENT_MAPPING = {
    # 01-核心基础
    "PostgreSQL/01-核心课程/01.00-PostgreSQL历史与发展.md": "01-核心基础/01.01-历史与发展/",
    "PostgreSQL/01-核心课程/01.01-系统架构与设计原理.md": "01-核心基础/01.02-系统架构/",
    "PostgreSQL/01-核心课程/01.02-关系数据模型与理论.md": "01-核心基础/01.03-数据模型/",
    "PostgreSQL/01-核心课程/01.03-SQL语言规范与标准.md": "01-核心基础/01.04-SQL语言/",

    # 02-查询与优化
    "PostgreSQL/02-查询处理/02.01-查询优化器原理.md": "02-查询与优化/02.01-查询优化器/",
    "PostgreSQL/02-查询处理/02.02-索引结构与优化.md": "02-查询与优化/02.02-索引结构/",
    "PostgreSQL/02-查询处理/02.03-统计信息与代价模型.md": "02-查询与优化/02.04-统计信息/",
    "PostgreSQL/02-查询处理/02.04-执行计划与性能调优.md": "02-查询与优化/02.03-执行计划/",
    "PostgreSQL/02-查询处理/02.05-并行查询处理.md": "02-查询与优化/02.05-并行查询/",
    "PostgreSQL/03-查询与优化/02.01-查询优化器原理.md": "02-查询与优化/02.01-查询优化器/",
    "PostgreSQL/03-查询与优化/02.02-索引结构与优化.md": "02-查询与优化/02.02-索引结构/",
    "PostgreSQL/03-查询与优化/02.03-统计信息与代价模型.md": "02-查询与优化/02.04-统计信息/",
    "PostgreSQL/03-查询与优化/02.04-执行计划与性能调优.md": "02-查询与优化/02.03-执行计划/",
    "PostgreSQL/03-查询与优化/02.05-并行查询处理.md": "02-查询与优化/02.05-并行查询/",

    # 03-事务与并发
    "PostgreSQL/01-核心课程/01.04-事务管理与ACID特性.md": "03-事务与并发/03.02-ACID特性/",
    "PostgreSQL/01-核心课程/01.05-并发控制与MVCC机制.md": "03-事务与并发/03.01-MVCC机制/",

    # 04-存储与恢复
    "PostgreSQL/01-核心课程/01.06-存储管理与数据持久化.md": "04-存储与恢复/",
}

# 目录批量映射规则 - 源目录 -> 目标目录
DIRECTORY_MAPPING = {
    # 02-查询与优化
    "PostgreSQL培训/11-性能调优/": "02-查询与优化/02.06-性能调优/",
    "DataBaseTheory/05-索引与查询优化/": "02-查询与优化/",

    # 03-事务与并发
    "MVCC-ACID-CAP/01-理论基础/": "03-事务与并发/",
    "MVCC-ACID-CAP/03-场景实践/": "03-事务与并发/03.07-场景实践/",
    "DataBaseTheory/03-事务与并发控制/": "03-事务与并发/",

    # 04-存储与恢复
    "PostgreSQL培训/06-存储管理/": "04-存储与恢复/",
    "PostgreSQL培训/08-备份恢复/": "04-存储与恢复/",
    "DataBaseTheory/06-存储与恢复/": "04-存储与恢复/",

    # 05-安全与合规
    "PostgreSQL/03-高级特性/03.02-安全机制与访问控制.md": "05-安全与合规/",
    "PostgreSQL培训/07-安全/": "05-安全与合规/",
    "PostgreSQL_View/05-合规与可信/": "05-安全与合规/",
    "DataBaseTheory/07-安全与合规/": "05-安全与合规/",

    # 06-扩展系统
    "PostgreSQL/03-高级特性/03.01-扩展系统与插件开发.md": "06-扩展系统/",
    "PostgreSQL培训/12-扩展开发/": "06-扩展系统/",

    # 07-多模型数据库
    "PostgreSQL/03-高级特性/03.05-向量数据库支持.md": "07-多模型数据库/07.01-向量数据库/",
    "PostgreSQL/03-高级特性/03.06-图数据库功能.md": "07-多模型数据库/07.02-图数据库/",
    "PostgreSQL_View/04-多模一体化/": "07-多模型数据库/",
    "PostgreSQL培训/03-数据类型/【深入】JSON-JSONB高级查询完整指南.md": "07-多模型数据库/07.03-JSONB/",
    "PostgreSQL培训/03-数据类型/【深入】PostGIS空间数据库完整实战指南.md": "07-多模型数据库/07.04-空间数据/",

    # 08-流处理与时序
    "PostgreSQL/03-高级特性/03.03-流处理与CEP.md": "08-流处理与时序/",
    "PostgreSQL培训/03-数据类型/【深入】TimescaleDB时序数据库完整实战指南.md": "08-流处理与时序/",
    "DataBaseTheory/10-流处理与时序/": "08-流处理与时序/",

    # 09-逻辑复制
    "DataBaseTheory/16-逻辑复制与冲突/": "09-逻辑复制/",

    # 11-部署架构
    "PostgreSQL/05-部署架构/": "11-部署架构/",
    "PostgreSQL/04-部署运维/": "11-部署架构/",
    "PostgreSQL培训/05-部署架构/": "11-部署架构/",

    # 12-监控与诊断
    "PostgreSQL/06-运维实践/监控与诊断/": "12-监控与诊断/",
    "PostgreSQL培训/10-监控诊断/": "12-监控与诊断/",

    # 13-高可用架构
    "PostgreSQL/06-运维实践/": "13-高可用架构/",
    "PostgreSQL培训/09-高可用/": "13-高可用架构/",
    "PostgreSQL_View/06-架构设计/高可用架构/": "13-高可用架构/",

    # 14-云原生与容器化
    "PostgreSQL/05-部署架构/容器化部署/": "14-云原生与容器化/",
    "PostgreSQL_View/03-Serverless与分支/": "14-云原生与容器化/",
    "kubernetes/": "14-云原生与容器化/",

    # 15-分布式系统
    "MVCC-ACID-CAP/04-形式化论证/CAP同构性论证/": "15-分布式系统/",
    "DataBaseTheory/04-分布式系统理论/": "15-分布式系统/",
    "PostgreSQL/04-高级特性/03.07-分布式事务处理.md": "15-分布式系统/",
    "docs/04-Distributed/": "15-分布式系统/",

    # 16-应用设计与开发
    "PostgreSQL/09-应用设计/": "16-应用设计与开发/",
    "PostgreSQL培训/04-函数与编程/": "16-应用设计与开发/",
    "PostgreSQL培训/06-应用开发/": "16-应用设计与开发/",

    # 17-数据模型设计
    "PostgreSQL/09-应用设计/数据模型设计/": "17-数据模型设计/",
    "DataBaseTheory/09-数据模型与规范化/": "17-数据模型设计/",
    "PostgreSQL培训/14-设计/": "17-数据模型设计/",

    # 19-实战案例
    "PostgreSQL/08-实战案例/": "19-实战案例/",
    "PostgreSQL_View/08-落地案例/": "19-实战案例/",
    "DataBaseTheory/19-场景案例库/": "19-实战案例/",
    "PostgreSQL/cases/": "19-实战案例/",

    # 20-故障诊断案例
    "DataBaseTheory/20-故障诊断案例库/": "20-故障诊断案例/",
    "PostgreSQL/runbook/": "20-故障诊断案例/",

    # 22-工具与资源
    "DataBaseTheory/22-工具脚本/": "22-工具与资源/",
    "DataBaseTheory/23-性能基准测试/": "22-工具与资源/",
    "PostgreSQL/08-工具资源/": "22-工具与资源/",
    "PostgreSQL/bench/": "22-工具与资源/",
    "scripts/": "22-工具与资源/",

    # 23-对比分析
    "PostgreSQL_AI/06-对比分析/": "23-对比分析/",
    "DataBaseTheory/17-系统对比与分析/": "23-对比分析/",
    "docs/06-Comparison/": "23-对比分析/",

    # 24-迁移指南
    "PostgreSQL/02-版本特性/02.03-版本对比与迁移指南.md": "24-迁移指南/",
    "PostgreSQL_View/09-实践指南/迁移指南/": "24-迁移指南/",

    # 25-理论体系
    "DataBaseTheory/01-形式化方法与基础理论/": "25-理论体系/25.01-形式化方法/",
    "DataBaseTheory/02-范畴论应用/": "25-理论体系/25.02-范畴论/",
    "DataBaseTheory/08-查询语言与语义/": "25-理论体系/25.03-查询语义/",
    "MVCC-ACID-CAP/01-理论基础/": "25-理论体系/",

    # 26-数据管理
    "DataBaseTheory/12-数据管理模型/": "26-数据管理/",
    "DataBaseTheory/13-数据编排/": "26-数据管理/",
    "PostgreSQL培训/05-数据管理/": "26-数据管理/",

    # 27-统计与估计
    "DataBaseTheory/15-统计与估计/": "27-统计与估计/",

    # 28-知识图谱
    "docs/03-KnowledgeGraph/": "28-知识图谱/",
    "DataBaseTheory/21-AI知识库/": "28-知识图谱/",
    "PostgreSQL培训/12-扩展开发/【深入】知识图谱本体建模与推理指南.md": "28-知识图谱/",
    "PostgreSQL/08-工具资源/08.02-知识图谱构建.md": "28-知识图谱/",

    # 21-最佳实践
    "BEST-PRACTICES.md": "21-最佳实践/",
    "PostgreSQL/08-工具资源/08.04-最佳实践总结.md": "21-最佳实践/",
    "PostgreSQL_View/09-实践指南/": "21-最佳实践/",

    # 10-AI与机器学习
    "PostgreSQL_AI/": "10-AI与机器学习/",
    "PostgreSQL_View/01-向量与混合搜索/": "10-AI与机器学习/10.01-向量处理/",
    "PostgreSQL_View/02-AI自治与自优化/": "10-AI与机器学习/10.04-AI自治/",
    "docs/02-AI-ML/": "10-AI与机器学习/",
    "PostgreSQL培训/14-AI与机器学习/": "10-AI与机器学习/",

    # 18-版本特性
    "PostgreSQL/02-版本特性/": "18-版本特性/",
    "PostgreSQL培训/16-PostgreSQL17新特性/": "18-版本特性/18.02-PostgreSQL17新特性/",
    "PostgreSQL培训/17-PostgreSQL18新特性/": "18-版本特性/18.01-PostgreSQL18新特性/",
    "docs/01-PostgreSQL18/": "18-版本特性/18.01-PostgreSQL18新特性/",
}

def add_source_header(content: str, source_path: str) -> str:
    """在文档开头添加来源信息"""
    header = f"""---

> **📋 文档来源**: `{source_path}`
> **📅 复制日期**: {datetime.now().strftime('%Y-%m-%d')}
> **⚠️ 注意**: 本文档为复制版本，原文件保持不变

---

"""
    # 如果文档已经有YAML front matter，在front matter后添加
    if content.startswith("---"):
        lines = content.split("\n")
        # 找到第二个---的位置
        end_idx = 1
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_idx = i + 1
                break
        return "\n".join(lines[:end_idx]) + "\n" + header + "\n".join(lines[end_idx:])
    else:
        return header + content

def copy_document(source_rel: str, target_rel: str):
    """复制单个文档"""
    source_path = ROOT_DIR / source_rel
    target_dir = INTEGRATE_DIR / target_rel
    target_path = target_dir / source_path.name

    if not source_path.exists():
        print(f"⚠️  源文件不存在: {source_path}")
        return False

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)

    # 读取源文件
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败 {source_path}: {e}")
        return False

    # 添加来源信息
    content_with_header = add_source_header(content, source_rel)

    # 写入目标文件
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content_with_header)
        print(f"✅ 已复制: {source_rel} -> {target_rel}")
        return True
    except Exception as e:
        print(f"❌ 写入文件失败 {target_path}: {e}")
        return False

def copy_directory(source_dir_rel: str, target_dir_rel: str):
    """批量复制目录下的所有.md文件"""
    source_dir = ROOT_DIR / source_dir_rel
    target_dir = INTEGRATE_DIR / target_dir_rel

    if not source_dir.exists():
        print(f"⚠️  源目录不存在: {source_dir}")
        return 0, 0

    success_count = 0
    fail_count = 0

    # 遍历所有.md文件
    for md_file in source_dir.rglob("*.md"):
        # 计算相对路径
        rel_path = md_file.relative_to(source_dir)
        target_file = target_dir / rel_path

        # 创建目标目录
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # 读取并复制文件
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 添加来源信息
            content_with_header = add_source_header(content, str(md_file.relative_to(ROOT_DIR)))

            # 写入目标文件
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content_with_header)

            print(f"✅ 已复制: {md_file.relative_to(ROOT_DIR)} -> {target_file.relative_to(INTEGRATE_DIR)}")
            success_count += 1
        except Exception as e:
            print(f"❌ 复制失败 {md_file}: {e}")
            fail_count += 1

    return success_count, fail_count

def main():
    """主函数"""
    print("🚀 开始复制文档...")
    print(f"📁 项目根目录: {ROOT_DIR}")
    print(f"📁 Integrate目录: {INTEGRATE_DIR}\n")

    success_count = 0
    fail_count = 0

    # 复制单个文件
    print("\n📄 复制单个文件...")
    for source_rel, target_rel in DOCUMENT_MAPPING.items():
        if copy_document(source_rel, target_rel):
            success_count += 1
        else:
            fail_count += 1

    # 批量复制目录
    print("\n📁 批量复制目录...")
    for source_dir_rel, target_dir_rel in DIRECTORY_MAPPING.items():
        print(f"\n处理目录: {source_dir_rel}")
        s, f = copy_directory(source_dir_rel, target_dir_rel)
        success_count += s
        fail_count += f

    print(f"\n📊 复制完成:")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📝 总计: {success_count + fail_count}")

if __name__ == "__main__":
    main()
