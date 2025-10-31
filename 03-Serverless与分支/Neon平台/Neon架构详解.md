# Neon 架构详解

> **更新时间**: 2025 年 11 月 1 日  
> **技术版本**: Neon v3.0+

## 📋 概述

Neon 是业界领先的 Serverless PostgreSQL 平台，通过 Scale-to-Zero 和数据库分支功能，让 AI Agent 可以
零成本进行数据库实验，成为"数据 Git"的完美实现。

## 🏗️ 架构设计

```text
┌─────────────────────────────────────────────────┐
│         Application Layer                       │
│  AI Agent | LangChain | RAG Apps                │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Neon API Layer                          │
│  ┌──────────────────────────────────────────┐   │
│  │      Branch Manager (分支管理)            │   │
│  │  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Create   │  │  Merge   │              │   │
│  │  │ Branch   │  │  Branch  │              │   │
│  │  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │      Scale-to-Zero Manager               │   │
│  │  ┌──────────┐  ┌──────────┐              │   │
│  │  │ Auto     │  │  Fast    │              │   │
│  │  │ Scale    │  │  Resume  │              │   │
│  │  └──────────┘  └──────────┘              │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Compute Layer (计算层)                  │
│  ┌──────────────────────────────────────────┐   │
│  │      Compute Nodes (计算节点)             │   │
│  │  - PostgreSQL Instances                  │   │
│  │  - Auto Scaling                          │   │
│  │  - Fast Startup                          │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Storage Layer (存储层)                  │
│  ┌──────────────────────────────────────────┐   │
│  │      Safekeeper (安全守护)                │   │
│  │  - WAL Storage                           │   │
│  │  - Replication                           │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │      Page Server (页面服务器)             │   │
│  │  - Page Storage                          │   │
│  │  - Snapshot Management                   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## 🎯 核心特性

### 1. Scale-to-Zero

**零成本停机**: 数据库在无活动时自动停止，成本为零

```javascript
// Neon API 示例
const neon = require("@neondatabase/serverless");

// 数据库在无活动时自动停止
const client = neon(process.env.DATABASE_URL);

// 第一次查询时自动启动（<2秒）
const result = await client.query("SELECT NOW()");
```

### 2. 数据库分支 (Branching)

**Git 式数据库管理**: 为每次实验创建独立分支

```javascript
// 创建分支
const branch = await neon.branches.create({
  project_id: "project-id",
  name: "experiment-001",
  parent_branch: "main"
});

// 分支连接字符串
const branchUrl = branch.connection_uri;
```

### 3. 即时快照 (Instant Snapshots)

**零成本快照**: 基于 Copy-on-Write 技术的即时快照

```javascript
// 创建快照
const snapshot = await neon.snapshots.create({
  branch_id: branch.id,
  name: "before-migration"
});

// 从快照恢复
const restoredBranch = await neon.branches.create({
  name: "restored-branch",
  parent_branch: snapshot.id
});
```

## 💻 使用指南

### 1. 快速开始

```bash
# 安装 Neon CLI
npm install -g neonctl

# 登录
neonctl auth

# 创建项目
neonctl projects create my-project

# 创建数据库
neonctl databases create my-db --project-id my-project-id
```

### 2. 分支管理

```javascript
const { Neon } = require("@neondatabase/serverless");

const neon = new Neon(process.env.NEON_API_KEY);

// 创建分支
async function createBranch(projectId, parentBranch, name) {
  const branch = await neon.branches.create({
    project_id: projectId,
    name: name,
    parent_branch: parentBranch
  });

  return branch;
}

// 列出分支
async function listBranches(projectId) {
  const branches = await neon.branches.list({
    project_id: projectId
  });

  return branches;
}

// 删除分支
async function deleteBranch(projectId, branchId) {
  await neon.branches.delete({
    project_id: projectId,
    branch_id: branchId
  });
}

// 合并分支
async function mergeBranch(projectId, sourceBranch, targetBranch) {
  await neon.branches.merge({
    project_id: projectId,
    source_branch_id: sourceBranch,
    target_branch_id: targetBranch
  });
}
```

### 3. LangChain 集成

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from neon import NeonClient

# 创建 Neon 客户端
client = NeonClient(api_key=os.getenv("NEON_API_KEY"))

# 创建实验分支
branch = client.branches.create(
    project_id="project-id",
    name="rag-experiment-v2",
    parent_branch="main"
)

# 初始化向量存储
embeddings = OpenAIEmbeddings()
vectorstore = PGVector(
    connection_string=branch.connection_string,
    embedding_function=embeddings,
    table_name="documents"
)

# 使用向量存储
vectorstore.add_texts(["文档1", "文档2"])
results = vectorstore.similarity_search("查询", k=5)

# 实验完成后删除分支
client.branches.delete(
    project_id="project-id",
    branch_id=branch.id
)
```

## 📊 性能指标

### Scale-to-Zero 性能

| 操作     | 时间   | 成本     |
| -------- | ------ | -------- |
| 冷启动   | <2s    | 正常计费 |
| 热启动   | <100ms | 正常计费 |
| 暂停     | <1s    | 存储费用 |
| 完全停止 | <5s    | **0**    |

### 分支操作性能

| 操作     | 时间           | 成本              |
| -------- | -------------- | ----------------- |
| 创建分支 | <1s            | **0**（仅元数据） |
| 切换分支 | <100ms         | **0**             |
| 删除分支 | <500ms         | **0**             |
| 合并分支 | 取决于差异大小 | 0.001$/GB         |

### 实际应用场景

- **AI Agent 实验**: 1.2 万次/小时分支创建
- **RAG 测试**: 每次测试创建独立分支，成本为零
- **A/B 测试**: 不同 embedding 模型测试，快速切换

## 🎯 最佳实践

### 1. 分支命名规范

```javascript
// 推荐命名格式
const branchNames = {
  experiment: "experiment-{timestamp}-{purpose}",
  feature: "feature/{feature-name}",
  test: "test/{test-name}",
  backup: "backup-{timestamp}"
};
```

### 2. 自动清理旧分支

```javascript
// 清理7天前的实验分支
async function cleanupOldBranches(projectId, olderThanDays = 7) {
  const branches = await neon.branches.list({ project_id: projectId });
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - olderThanDays);

  for (const branch of branches) {
    if (branch.created_at < cutoffDate && branch.name.startsWith("experiment-")) {
      await neon.branches.delete({
        project_id: projectId,
        branch_id: branch.id
      });
      console.log(`Deleted branch: ${branch.name}`);
    }
  }
}
```

### 3. 成本优化策略

```javascript
// 监控分支使用情况
async function monitorBranchUsage(projectId) {
  const branches = await neon.branches.list({ project_id: projectId });

  for (const branch of branches) {
    const stats = await neon.branches.stats({
      project_id: projectId,
      branch_id: branch.id
    });

    // 如果分支长时间未使用，建议删除
    if (stats.last_accessed < Date.now() - 7 * 24 * 60 * 60 * 1000) {
      console.warn(`Branch ${branch.name} has not been used for 7 days`);
    }
  }
}
```

## 📚 参考资料

- [Neon 官方文档](https://neon.tech/docs)
- [Neon API 文档](https://neon.tech/api-reference)
- [Neon GitHub](https://github.com/neondatabase/neon)

---

**最后更新**: 2025 年 11 月 1 日  
**维护者**: PostgreSQL Modern Team
