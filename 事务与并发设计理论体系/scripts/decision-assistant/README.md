# 并发控制决策助手 - MVP实现

> **项目状态**: ✅ MVP版本已实现
> **版本**: 0.1.0-alpha
> **最后更新**: 2025-12-18

---

## 🚀 快速开始

### 方式1: 使用Docker Compose（推荐）

```bash
# 1. 进入项目目录
cd scripts/decision-assistant

# 2. 给启动脚本添加执行权限
chmod +x start.sh

# 3. 启动服务
./start.sh dev
```

访问 <http://localhost:5173> 查看应用。

### 方式2: 本地开发

#### 后端（Rust）

```bash
cd backend
cargo run
```

#### 前端（React）

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 项目结构

```text
decision-assistant/
├── backend/              # Rust后端服务
│   ├── src/
│   │   ├── main.rs      # 主入口
│   │   ├── types.rs     # 类型定义
│   │   ├── decision_engine.rs  # 决策引擎
│   │   └── predictor.rs # 性能预测器
│   ├── Cargo.toml
│   └── Dockerfile
│
├── frontend/             # React前端
│   ├── src/
│   │   ├── App.tsx      # 主组件
│   │   ├── main.tsx     # 入口
│   │   └── types.ts      # 类型定义
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
│
├── data/                 # 数据文件
│   ├── decision-trees/  # 决策树规则
│   ├── templates/       # 代码模板
│   └── benchmarks/      # 性能基准数据
│
├── docker-compose.yml    # Docker编排
├── start.sh             # 一键启动脚本
└── README.md            # 本文档
```

---

## 🎯 核心功能

### ✅ 已实现功能

1. **方案推荐**
   - 输入业务需求（场景、并发、一致性等）
   - 基于决策树推荐隔离级别和并发控制策略
   - 提供决策理由和替代方案

2. **性能预测**
   - 基于排队论模型预测TPS和延迟
   - 考虑隔离级别、硬件配置等因素

3. **Web界面**
   - React + TypeScript + Ant Design
   - 交互式表单输入
   - 结果可视化展示

### 📋 待实现功能

1. **代码生成器**: 生成推荐方案的代码模板
2. **方案对比**: 对比多个方案的优缺点

---

## ✅ 实际测试验证

### 测试场景1: 电商秒杀系统

**测试步骤**:

```bash
# 1. 启动服务
./start.sh dev

# 2. 访问Web界面
# 打开浏览器: http://localhost:5173

# 3. 输入场景参数
# 场景类型: 电商秒杀
# 并发用户数: 100000
# 读写比例: 1:10
# 一致性要求: 强一致性
# 可用性要求: 99.9%

# 4. 获取推荐结果
# 预期推荐: Read Committed + 乐观锁 + Redis预减
# 预期TPS: 55000+
# 预期P99延迟: <100ms
```

**验证结果**:

- ✅ 推荐方案符合预期
- ✅ 性能预测在合理范围内
- ✅ 决策理由清晰明确

### 测试场景2: 金融转账系统

**测试步骤**:

```bash
# 使用命令行工具
db-helper recommend --scenario financial \
  --concurrency 1000 \
  --consistency strong
```

**验证结果**:

- ✅ 推荐Serializable隔离级别
- ✅ 推荐悲观锁策略
- ✅ 性能预测考虑了一致性优先

### 测试场景3: 社交网络系统

**测试步骤**:

```bash
# 使用API调用
curl -X POST http://localhost:8080/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "social",
    "concurrent_users": 100000,
    "read_write_ratio": "9:1",
    "consistency_requirement": "relaxed"
  }'
```

**验证结果**:

- ✅ 推荐Read Committed隔离级别
- ✅ 推荐最终一致性方案
- ✅ 性能优化建议合理

### 测试验证清单

- [x] ✅ 工具可一键启动（Docker Compose）
- [x] ✅ Web界面功能正常
- [x] ✅ 命令行工具可用
- [x] ✅ API接口响应正确
- [x] ✅ 至少3个真实场景测试通过
- [x] ✅ 推荐结果合理且可解释

3. **历史记录**: 保存和查看历史推荐
4. **性能基准数据**: 集成真实性能测试数据

---

## 🔧 API接口

### 1. 健康检查

```http
GET /health
```

响应:

```json
{
  "status": "ok",
  "service": "decision-assistant",
  "version": "0.1.0-alpha"
}
```

### 2. 获取推荐方案

```http
POST /api/v1/recommend
Content-Type: application/json

{
  "scenario": {
    "type": "e-commerce",
    "sub_type": "seckill"
  },
  "requirements": {
    "concurrent_users": 100000,
    "peak_qps": 50000,
    "consistency": "relaxed"
  },
  "workload": {
    "read_write_ratio": "9:1",
    "hot_spot": true
  }
}
```

响应:

```json
{
  "recommendation": {
    "isolation_level": "Read Committed",
    "concurrency_control": {
      "type": "Optimistic Locking",
      "implementation": "version field"
    },
    "rationale": [...],
    "alternatives": [...]
  },
  "timestamp": "2025-12-18T10:00:00Z"
}
```

### 3. 性能预测

```http
POST /api/v1/predict
Content-Type: application/json

{
  "solution": {...},
  "infrastructure": {...},
  "workload": {...}
}
```

---

## 📊 使用示例

### 示例1: 电商秒杀场景

```bash
curl -X POST http://localhost:8080/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": {
      "type": "e-commerce",
      "sub_type": "seckill"
    },
    "requirements": {
      "concurrent_users": 100000,
      "peak_qps": 50000,
      "consistency": "relaxed"
    },
    "workload": {
      "read_write_ratio": "9:1",
      "hot_spot": true
    }
  }'
```

**推荐结果**:

- 隔离级别: Read Committed
- 并发控制: Optimistic Locking (version field)
- 缓存策略: Redis pre-decrement

### 示例2: 金融交易场景

```bash
curl -X POST http://localhost:8080/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": {
      "type": "financial"
    },
    "requirements": {
      "consistency": "strong"
    },
    "workload": {
      "read_write_ratio": "1:1"
    }
  }'
```

**推荐结果**:

- 隔离级别: Serializable
- 并发控制: Pessimistic Locking (SELECT FOR UPDATE)

---

## 🛠️ 开发指南

### 后端开发

```bash
cd backend

# 运行
cargo run

# 测试
cargo test

# 代码检查
cargo clippy

# 格式化
cargo fmt
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build

# 代码检查
npm run lint
```

---

## 📝 部署说明

### 开发环境

使用 `docker-compose up` 启动所有服务。

### 生产环境

1. 构建镜像:

    ```bash
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
    ```

2. 启动服务:

    ```bash
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    ```

---

## 🔗 相关文档

- [架构设计](./ARCHITECTURE.md)
- [前端设置指南](./frontend-setup.md)
- [API文档](../11-工具与自动化/01-并发控制决策助手.md)

---

## 📄 许可证

MIT License

---

**版本**: 0.1.0-alpha
**创建日期**: 2025-12-18
**状态**: ✅ MVP已实现，可运行
