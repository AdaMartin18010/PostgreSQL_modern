#!/usr/bin/env python3
"""修复根目录文件中的 docs/configs/DataBaseTheory 链接及 GitHub 占位链接"""

import re
from pathlib import Path

GITHUB_BASE = "https://github.com/AdaMartin18010/PostgreSQL_modern"

# 映射表：旧路径 -> 新路径（相对项目根）。按从长到短排序，先替换更具体的路径。
# 若新路径为目录且存在，则原链接可为目录链接（末尾 /）。
MAPPING = [
    # ----- configs -> program/configs -----
    ("configs/postgresql-18-production.conf", "program/configs/postgresql-18-production.conf"),
    ("configs/docker-compose.yml", "program/configs/docker-compose.yml"),
    ("./configs/docker-compose.yml", "program/configs/docker-compose.yml"),
    ("configs/alerts/", "program/configs/alerts/"),
    ("./configs/alerts/", "program/configs/alerts/"),
    ("configs/", "program/configs/"),
    ("./configs/", "program/configs/"),
    # ----- DataBaseTheory -> Integrate / program -----
    ("DataBaseTheory/21-AI知识库/11-LangChain企业知识库完整案例.md", "Integrate/10-AI与机器学习/README.md"),
    ("DataBaseTheory/21-AI知识库/", "Integrate/10-AI与机器学习/"),
    ("DataBaseTheory/23-性能基准测试/", "Integrate/22-工具与资源/"),
    ("DataBaseTheory/19-场景案例库/", "Integrate/19-实战案例/"),
    ("DataBaseTheory/22-工具脚本/", "program/scripts/"),
    ("./DataBaseTheory/22-工具脚本/", "program/scripts/"),
    ("./DataBaseTheory/19-场景案例库/", "Integrate/19-实战案例/"),
    ("./DataBaseTheory/23-性能基准测试/", "Integrate/22-工具与资源/"),
    # ----- docs 具体文件 -----
    ("docs/01-PostgreSQL18/40-PostgreSQL18新特性总结.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/40-PostgreSQL18新特性总结.md"),
    ("docs/01-PostgreSQL18/08-性能调优实战指南.md", "Integrate/30-性能调优/PostgreSQL性能调优完整指南.md"),
    ("docs/01-PostgreSQL18/35-慢查询优化实战案例.md", "Integrate/02-查询与优化/02.06-性能调优/【案例集】PostgreSQL慢查询优化完整实战手册.md"),
    ("docs/01-PostgreSQL18/02-Skip-Scan深度解析.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/02-范围扫描Skip-Scan完整指南.md"),
    ("docs/01-PostgreSQL18/36-SQL注入防御完整指南.md", "Integrate/05-安全与合规/安全加固/PostgreSQL安全加固完整指南.md"),
    ("docs/01-PostgreSQL18/01-异步IO深度解析.md", "Integrate/07-多模型数据库/PostgreSQL-18新特性/异步I-O机制/README.md"),
    ("docs/01-PostgreSQL18/03-UUIDv7实战指南.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/04-UUIDv7完整指南.md"),
    ("docs/05-Production/10-安全加固完整指南.md", "Integrate/05-安全与合规/零信任架构完整指南.md"),
    ("docs/05-Production/20-生产环境检查清单.md", "Integrate/21-最佳实践/README.md"),
    ("docs/05-Production/17-Docker容器化完整指南.md", "Integrate/14-云原生与容器化/README.md"),
    ("docs/05-Production/09-升级迁移完整指南.md", "Integrate/24-迁移指南/README.md"),
    ("docs/05-Production/13-连接池实战指南.md", "Integrate/11-部署架构/README.md"),
    ("docs/05-Production/11-故障排查完整手册.md", "Integrate/20-故障诊断案例/README.md"),
    ("docs/05-Production/08-备份恢复完整实战.md", "Integrate/04-存储与恢复/备份恢复体系详解.md"),
    ("docs/05-Production/12-监控告警完整方案.md", "Integrate/12-监控与诊断/README.md"),
    ("docs/05-Production/07-Patroni高可用完整指南.md", "Integrate/13-高可用架构/README.md"),
    ("docs/05-Production/21-容量规划计算器.md", "Integrate/31-容量规划/README.md"),
    ("docs/05-Production/22-生产故障案例集.md", "Integrate/20-故障诊断案例/README.md"),
    ("docs/01-PostgreSQL18/41-PostgreSQL开发者速查表.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/README.md"),
    ("docs/01-PostgreSQL18/42-PostgreSQL故障排查手册.md", "Integrate/20-故障诊断案例/README.md"),
    ("docs/01-PostgreSQL18/43-SQL优化速查手册.md", "Integrate/02-查询与优化/02.06-性能调优/性能调优体系详解.md"),
    ("docs/01-PostgreSQL18/33-批量操作性能优化.md", "Integrate/02-查询与优化/02.06-性能调优/性能调优深入.md"),
    ("docs/06-Comparison/02-向量数据库完整对比.md", "Integrate/23-对比分析/README.md"),
    ("./docs/01-PostgreSQL18/01-AIO异步IO完整深度指南.md", "Integrate/07-多模型数据库/PostgreSQL-18新特性/异步I-O机制/README.md"),
    ("./docs/01-PostgreSQL18/02-跳跃扫描Skip-Scan完整指南.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/02-范围扫描Skip-Scan完整指南.md"),
    ("./docs/01-PostgreSQL18/04-UUIDv7完整指南.md", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/04-UUIDv7完整指南.md"),
    ("./docs/01-PostgreSQL18/14-并行查询与JIT编译增强指南.md", "Integrate/02-查询与优化/02.05-并行查询/README.md"),
    ("./docs/01-PostgreSQL18/11-VACUUM增强与积极冻结策略完整指南.md", "Integrate/04-存储与恢复/VACUUM与维护.md"),
    ("./docs/01-PostgreSQL18/13-查询优化器增强完整指南.md", "Integrate/02-查询与优化/02.01-查询优化器/02.01-查询优化器原理.md"),
    ("./docs/01-PostgreSQL18/15-WAL与检查点优化完整指南.md", "Integrate/04-存储与恢复/09-WAL深度解析.md"),
    ("./docs/01-PostgreSQL18/27-多模态数据库能力指南.md", "Integrate/07-多模型数据库/README.md"),
    ("./docs/03-KnowledgeGraph/05-知识图谱构建完整流程指南.md", "Integrate/28-知识图谱/README.md"),
    ("./docs/03-KnowledgeGraph/01-Apache-AGE完整深化指南-v2.md", "Integrate/06-扩展系统/【深入】Apache AGE图数据库完整实战指南.md"),
    ("./docs/03-KnowledgeGraph/07-LLM与知识图谱深度集成.md", "Integrate/28-知识图谱/README.md"),
    ("./docs/03-KnowledgeGraph/08-知识抽取与NER完整指南.md", "Integrate/28-知识图谱/README.md"),
    ("./docs/03-KnowledgeGraph/09-RAG+知识图谱混合架构.md", "Integrate/10-AI与机器学习/README.md"),
    ("./docs/02-AI-ML/01-pgvector完整深化指南.md", "Integrate/10-AI与机器学习/pgvector-0.8.1-新特性完整指南.md"),
    ("./docs/02-AI-ML/02-LangChain生产级集成指南.md", "Integrate/10-AI与机器学习/README.md"),
    ("./docs/02-AI-ML/06-RAG生产架构完整指南.md", "Integrate/10-AI与机器学习/README.md"),
    ("./docs/00-START-HERE/00-项目已达100%完整度.md", "Integrate/README.md"),
    ("./docs/00-START-HERE/02-快速开始-5分钟上手.md", "Integrate/README.md"),
    ("./docs/00-START-HERE/03-学习路径-完整地图.md", "Integrate/00-导航索引.md"),
    ("./docs/00-START-HERE/05-FAQ常见问题.md", "FAQ.md"),
    ("./docs/INDEX.md", "Integrate/00-导航索引.md"),
    ("./docs/【🏆终极完成】PostgreSQL18完整技术体系-三阶段总结-2025-12-04.md", "Integrate/README.md"),
    ("./docs/【🎉知识图谱深度扩展完成】PostgreSQL-KG-Final-2025-12-04.md", "Integrate/28-知识图谱/README.md"),
    ("./docs/【📊最终数据】PostgreSQL_Modern-Complete-Stats-2025-12-04.md", "Integrate/README.md"),
    ("./docs/【🏆最终完成】PostgreSQL_Modern完整技术体系-2025-12-04.md", "Integrate/README.md"),
    # ----- docs 目录 -----
    ("docs/01-PostgreSQL18/", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/"),
    ("docs/02-AI-ML/", "Integrate/10-AI与机器学习/"),
    ("docs/03-KnowledgeGraph/", "Integrate/28-知识图谱/"),
    ("docs/04-Distributed/", "Integrate/15-分布式系统/"),
    ("docs/05-Production/", "Integrate/11-部署架构/"),
    ("docs/00-START-HERE/", "Integrate/"),
    ("./docs/01-PostgreSQL18/", "Integrate/18-版本特性/18.01-PostgreSQL18新特性/"),
    ("./docs/02-AI-ML/", "Integrate/10-AI与机器学习/"),
    ("./docs/03-KnowledgeGraph/", "Integrate/28-知识图谱/"),
    ("./docs/04-Distributed/", "Integrate/15-分布式系统/"),
    ("./docs/05-Production/", "Integrate/11-部署架构/"),
    ("./docs/00-START-HERE/", "Integrate/"),
    ("docs/", "Integrate/"),
    ("./docs/", "Integrate/"),
]

# GitHub 链接替换（仅用于 CONTRIBUTING 等）
GITHUB_REPLACEMENTS = [
    ("../../issues", f"{GITHUB_BASE}/issues"),
    ("../../discussions", f"{GITHUB_BASE}/discussions"),
]

ROOT_FILES = [
    Path("BEST-PRACTICES.md"),
    Path("FAQ.md"),
    Path("CONTRIBUTING.md"),
    Path("README.md"),
    Path("QUICKSTART.md"),
    Path("FINAL-MILESTONE.md"),
    Path("START-HERE.md"),
    Path("WHATS-NEW.md"),
    Path("【🚀QUICK-START】5分钟快速上手指南.md"),
]


def _exists(target: str) -> bool:
    p = Path(target)
    if target.endswith("/"):
        p = Path(target.rstrip("/"))
        return p.is_dir() or (p / "README.md").exists()
    return p.exists()


def get_rel(from_f: Path, to_str: str) -> str:
    to = Path(to_str.rstrip("/"))
    if not to.is_absolute():
        to = Path.cwd() / to
    try:
        r = to.relative_to(Path(from_f).parent.resolve())
        return str(r).replace("\\", "/")
    except ValueError:
        return to_str.replace("\\", "/")


def fix_file(fpath: Path, dry_run: bool) -> bool:
    try:
        text = fpath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {fpath}: {e}")
        return False

    orig = text

    for old, new in MAPPING:
        if not _exists(new):
            continue
        rel = get_rel(fpath, new)
        # ](old) or ](old#anchor)
        pattern = r'\]\(' + re.escape(old) + r'(#[^\)]*)?\)'
        def repl(m):
            a = m.group(1) or ""
            return f"]({rel}{a})"
        text = re.sub(pattern, repl, text)

    for old, new in GITHUB_REPLACEMENTS:
        text = re.sub(r'\]\(' + re.escape(old) + r'\)', f"]({new})", text)

    if text != orig:
        if not dry_run:
            fpath.write_text(text, encoding="utf-8")
            print(f"Fixed: {fpath}")
        return True
    return False


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="Apply fixes")
    args = ap.parse_args()
    dry_run = not args.fix

    n = 0
    for f in ROOT_FILES:
        if f.exists():
            n += fix_file(f, dry_run)
    print(f"Files updated: {n} (dry_run={dry_run})")


if __name__ == "__main__":
    main()
