# 并发控制决策助手 - 开发指南

> **项目状态**: 🚀 开发中
> **版本**: 0.1.0-alpha

---

## 📋 项目概述

并发控制决策助手是一个Web应用 + CLI工具，帮助架构师和开发者快速选择合适的并发控制方案。

### 核心功能

- ✅ 交互式问答收集需求
- ✅ 基于决策树的方案推荐
- ✅ 性能预测
- ✅ 代码模板生成
- ✅ 方案对比分析

---

## 🚀 快速开始

### 前置要求

- Node.js 18+
- Rust 1.75+ (如果使用Rust后端)
- PostgreSQL 16+ (可选，用于性能数据)
- Redis 7+ (可选，用于缓存)

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/concurrency-decision-assistant.git
cd concurrency-decision-assistant

# 安装前端依赖
cd frontend
npm install

# 安装后端依赖 (Rust)
cd ../backend
cargo build

# 或安装后端依赖 (Node.js)
cd ../backend-js
npm install
```

### 运行

```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 启动后端服务器 (Rust)
cd backend
cargo run

# 或启动后端服务器 (Node.js)
cd backend-js
npm run dev
```

访问 <http://localhost:5173> 查看应用。

---

## 📁 项目结构

```
concurrency-decision-assistant/
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── components/       # React组件
│   │   ├── pages/            # 页面
│   │   ├── services/         # API服务
│   │   ├── store/            # 状态管理
│   │   └── utils/            # 工具函数
│   ├── public/               # 静态资源
│   └── package.json
│
├── backend/                  # 后端服务 (Rust)
│   ├── src/
│   │   ├── api/              # API路由
│   │   ├── engine/           # 决策引擎
│   │   ├── predictor/        # 性能预测器
│   │   └── generator/         # 代码生成器
│   ├── Cargo.toml
│   └── README.md
│
├── backend-js/               # 后端服务 (Node.js，备选)
│   ├── src/
│   ├── package.json
│   └── README.md
│
├── cli/                      # CLI工具
│   ├── src/
│   └── Cargo.toml
│
├── data/                     # 数据文件
│   ├── decision-trees/       # 决策树规则
│   ├── templates/           # 代码模板
│   └── benchmarks/          # 性能基准数据
│
├── docs/                     # 文档
│   ├── ARCHITECTURE.md      # 架构设计
│   ├── API.md               # API文档
│   └── DEVELOPMENT.md       # 开发指南
│
└── scripts/                  # 脚本工具
    ├── setup.sh             # 环境设置
    └── test.sh              # 测试脚本
```

---

## 🛠️ 开发指南

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建
npm run build

# 测试
npm run test

# 代码检查
npm run lint
```

### 后端开发

**Rust后端**:

```bash
cd backend

# 运行
cargo run

# 测试
cargo test

# 代码格式化
cargo fmt

# 代码检查
cargo clippy
```

**Node.js后端**:

```bash
cd backend-js

# 开发模式
npm run dev

# 构建
npm run build

# 测试
npm run test
```

---

## 📝 贡献指南

请参考 [CONTRIBUTING.md](../github-repo-setup/CONTRIBUTING.md)

---

## 📄 许可证

MIT License - 查看 [LICENSE](../github-repo-setup/LICENSE) 了解详情

---

**文档版本**: 0.1.0
**创建日期**: 2025-12-05
