# 高频交易数据分析平台

> **行业**: 金融 (证券/期货) | **场景**: 量化交易实时行情分析与策略回测 | **规模**: 纳秒级延迟，百万TPS，PB级历史数据

---

## 📋 目录

- [高频交易数据分析平台](#高频交易数据分析平台)
  - [📋 目录](#-目录)
  - [一、业务背景](#一业务背景)
    - [1.1 量化交易业务介绍](#11-量化交易业务介绍)
      - [1.1.1 什么是量化交易](#111-什么是量化交易)
      - [1.1.2 核心数据类型](#112-核心数据类型)
      - [1.1.3 量化交易策略分类](#113-量化交易策略分类)
    - [1.2 核心挑战](#12-核心挑战)
      - [1.2.1 纳秒级延迟要求](#121-纳秒级延迟要求)
      - [1.2.2 数据完整性保障](#122-数据完整性保障)
      - [1.2.3 回测准确性](#123-回测准确性)
    - [1.3 技术栈选型](#13-技术栈选型)
      - [1.3.1 数据库选型对比](#131-数据库选型对比)
      - [1.3.2 完整技术栈](#132-完整技术栈)
      - [1.3.3 硬件配置建议](#133-硬件配置建议)
  - [二、技术架构](#二技术架构)
    - [2.1 系统架构图](#21-系统架构图)
    - [2.2 数据流架构](#22-数据流架构)
    - [2.3 分层存储架构](#23-分层存储架构)
  - [三、数据模型设计](#三数据模型设计)
    - [3.1 核心表结构概览](#31-核心表结构概览)
    - [3.2 实时行情表](#32-实时行情表)
    - [3.3 K线聚合表](#33-k线聚合表)
    - [3.4 订单簿快照表](#34-订单簿快照表)
    - [3.5 交易信号表](#35-交易信号表)
    - [3.6 策略绩效表](#36-策略绩效表)
    - [4.2 K线实时聚合引擎](#42-k线实时聚合引擎)
    - [4.3 订单簿重建算法](#43-订单簿重建算法)
    - [4.4 技术指标计算](#44-技术指标计算)
    - [4.5 策略回测框架](#45-策略回测框架)
  - [五、性能优化](#五性能优化)
    - [5.1 内存表配置](#51-内存表配置)
    - [5.2 分区策略](#52-分区策略)
    - [5.3 连续聚合策略](#53-连续聚合策略)
    - [5.4 并行查询优化](#54-并行查询优化)
  - [六、部署配置](#六部署配置)
    - [6.1 Docker Compose配置](#61-docker-compose配置)
    - [6.2 PostgreSQL配置](#62-postgresql配置)
    - [6.3 Redis配置](#63-redis配置)
    - [6.4 监控告警](#64-监控告警)
  - [七、生产检查清单](#七生产检查清单)
    - [7.1 部署前检查](#71-部署前检查)
    - [7.2 性能基准测试](#72-性能基准测试)
  - [八、参考资源](#八参考资源)
    - [8.1 技术文档](#81-技术文档)
    - [8.2 学术论文](#82-学术论文)
    - [8.3 开源项目](#83-开源项目)
    - [8.4 行业最佳实践](#84-行业最佳实践)
  - [总结](#总结)
    - [关键特性](#关键特性)
    - [性能指标](#性能指标)
    - [后续优化方向](#后续优化方向)
  - [附录A: 高级查询示例](#附录a-高级查询示例)
    - [A.1 复杂分析查询](#a1-复杂分析查询)
    - [A.2 性能优化查询](#a2-性能优化查询)
  - [附录B: 系统运维脚本](#附录b-系统运维脚本)
  - [附录C: Python工具类库](#附录c-python工具类库)
  - [附录D: 交易所接口规范](#附录d-交易所接口规范)
    - [D.1 上海证券交易所行情接口](#d1-上海证券交易所行情接口)
    - [D.2 FIX协议适配器](#d2-fix协议适配器)

---

## 一、业务背景

### 1.1 量化交易业务介绍

#### 1.1.1 什么是量化交易

量化交易（Quantitative Trading）是指利用数学模型、统计分析和计算机算法来制定交易决策的交易方式。与传统的主观交易不同，量化交易通过系统化的方法识别市场中的交易机会，并自动执行交易指令。

在现代金融市场中，量化交易已经成为机构投资者的标配。根据行业统计，全球超过70%的股票交易量由量化策略产生，而在高频交易（HFT）领域，这一比例更是高达90%以上。

#### 1.1.2 核心数据类型

**Tick数据（逐笔数据）**

Tick数据是金融市场中最细粒度的数据，记录了每一笔交易和每一个报价变化。它是量化交易的基础数据源，具有以下特征：

- **时间精度**: 纳秒级（ns）时间戳，现代交易所如NASDAQ、CME、上海期货交易所等都提供微秒甚至纳秒级的时间戳
- **数据密度**: 活跃品种每秒可产生数千条Tick数据，极端行情下可达数万条/秒
- **数据结构**: 包含成交时间、成交价格、成交量、买卖方向、委托号等字段

Tick数据示例结构：

```
┌─────────────────┬─────────┬─────────┬────────┬──────┬──────────┐
│  timestamp      │ symbol  │  price  │ volume │ side │ order_id │
├─────────────────┼─────────┼─────────┼────────┼──────┼──────────┤
│ 169912345678901 │ AAPL    │ 185.50  │ 100    │ B    │ 12345678 │
│ 169912345678902 │ AAPL    │ 185.51  │ 200    │ A    │ 12345679 │
└─────────────────┴─────────┴─────────┴────────┴──────┴──────────┘
```

**K线数据（Candlestick/OHLCV）**

K线数据是对Tick数据的时间维度聚合，是技术分析的基础。常见的K线周期包括：

- **高频周期**: 1秒、5秒、15秒、30秒、1分钟、5分钟
- **中频周期**: 15分钟、30分钟、1小时、4小时
- **低频周期**: 日线、周线、月线

K线数据结构：

```
┌─────────────────┬─────────┬────────┬────────┬────────┬────────┬────────┐
│  timestamp      │ symbol  │ open   │ high   │ low    │ close  │ volume │
├─────────────────┼─────────┼────────┼────────┼────────┼────────┼────────┤
│ 2024-01-01 09:30│ AAPL    │ 185.00 │ 186.50 │ 184.80 │ 185.50 │ 150000 │
└─────────────────┴─────────┴────────┴────────┴────────┴────────┴────────┘
```

K线的每个字段都有明确的金融含义：

- **Open（开盘价）**: 该时间周期内的第一笔成交价
- **High（最高价）**: 该时间周期内的最高成交价
- **Low（最低价）**: 该时间周期内的最低成交价
- **Close（收盘价）**: 该时间周期内的最后一笔成交价
- **Volume（成交量）**: 该时间周期内的总成交量

**订单簿数据（Order Book/市场深度）**

订单簿是交易所撮合引擎的核心数据结构，记录了所有未成交的买入和卖出委托。它是理解市场微观结构的关键：

- **L1数据（最优报价）**: 只包含买一价、买一量、卖一价、卖一量
- **L2数据（五档行情）**: 包含前5个价格档位的委托信息
- **L3数据（完整委托簿）**: 包含所有价格档位的完整委托信息

订单簿示例（L2五档）：

```
┌──────────────┬──────────┬──────────────┬──────────┐
│ Bid Price    │ Bid Size │ Ask Price    │ Ask Size │
├──────────────┼──────────┼──────────────┼──────────┤
│ 185.48       │ 500      │ 185.50       │ 300      │ ← Level 1
│ 185.47       │ 800      │ 185.51       │ 600      │ ← Level 2
│ 185.46       │ 1200     │ 185.52       │ 900      │ ← Level 3
│ 185.45       │ 1500     │ 185.53       │ 1100     │ ← Level 4
│ 185.44       │ 2000     │ 185.54       │ 1500     │ ← Level 5
└──────────────┴──────────┴──────────────┴──────────┘
```

#### 1.1.3 量化交易策略分类

**按持仓时间分类**：

1. **高频交易（HFT）**: 持仓时间毫秒级到秒级，依赖极低的延迟和大量的交易次数获取微小利润
2. **日内交易（Day Trading）**: 日内开仓平仓，不持仓过夜
3. **短线交易**: 持仓数天到数周
4. **中长线交易**: 持仓数月到数年

**按策略逻辑分类**：

1. **趋势跟踪**: 识别并跟随市场趋势，如双均线策略、海龟交易法则
2. **均值回归**: 假设价格会回归长期均值，如布林带策略、统计套利
3. **市场中性**: 同时做多和做空相关资产，获取Alpha收益
4. **事件驱动**: 基于新闻、财报、宏观经济数据等事件进行交易
5. **做市策略**: 同时在买卖双边报单，赚取买卖价差

### 1.2 核心挑战

#### 1.2.1 纳秒级延迟要求

在高频交易中，延迟就是金钱。每微秒的延迟优势都可能转化为可观的利润：

**延迟构成分析**：

| 延迟环节 | 典型延迟 | 优化目标 |
|---------|---------|---------|
| 交易所行情传输 | 100-500μs | 专线接入，共置托管 |
| 行情解析 | 1-10μs | 零拷贝解析，FPGA加速 |
| 策略计算 | 1-100μs | C++/Rust，向量化计算 |
| 订单生成 | 0.1-1μs | 预生成订单模板 |
| 网络传输 | 10-100μs | Kernel Bypass，DPDK |
| 交易所撮合 | 50-500μs | 无法优化 |

**端到端延迟要求**：

- **顶级HFT**: 亚微秒级（<1μs）端到端延迟
- **普通HFT**: 微秒级（1-100μs）延迟
- **中低频**: 毫秒级（1-10ms）延迟可接受

**PostgreSQL在延迟优化中的角色**：

- 使用UNLOGGED表存储热数据，减少WAL写入开销
- 内存表（RAM-only tables）实现微秒级查询
- 流复制（Streaming Replication）实现读写分离
- 连接池（PgBouncer）减少连接建立开销

#### 1.2.2 数据完整性保障

金融数据不允许丢失任何一条记录，数据完整性是量化系统的生命线：

**数据完整性挑战**：

1. **网络抖动**: 行情推送可能出现丢包或乱序
2. **系统故障**: 服务器宕机可能导致内存中数据丢失
3. **时间同步**: 多台服务器之间的时间同步精度要求
4. **数据回补**: 交易时段外的数据回补机制

**数据完整性保障措施**：

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  行情源      │────▶│  消息队列   │────▶│  持久化存储  │
│ (交易所)    │     │ (Kafka/    │     │ (PostgreSQL)│
└─────────────┘     │  Pulsar)    │     └─────────────┘
                    └─────────────┘            │
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  实时计算   │     │  冷存储     │
                    │ (Flink/    │     │ (对象存储)  │
                    │  内存DB)    │     └─────────────┘
                    └─────────────┘
```

**PostgreSQL数据完整性特性**：

- **ACID事务**: 确保每笔写入的原子性和持久性
- **WAL（预写日志）**: 保证数据不丢失
- **流复制**: 实时同步到备库，实现高可用
- **时间点恢复（PITR）**: 支持任意时间点的数据恢复

#### 1.2.3 回测准确性

策略回测是量化交易的核心环节，回测结果的准确性直接决定策略能否在实盘盈利：

**回测挑战**：

1. **未来函数**: 使用未来数据导致回测结果过于乐观
2. **滑点估计**: 实际成交价格与信号价格的差异
3. **冲击成本**: 大额订单对市场价格的影响
4. **市场冲击**: 策略本身对市场的影响
5. **幸存者偏差**: 只使用存活至今的股票数据

**回测数据质量要求**：

| 质量指标 | 要求 | 说明 |
|---------|------|------|
| 时间精度 | 纳秒级 | 确保事件顺序正确 |
| 数据完整性 | 100% | 不能有任何缺失数据 |
| 数据准确性 | 99.99% | 价格、成交量必须准确 |
| 历史覆盖 | 10年+ | 覆盖各种市场环境 |

### 1.3 技术栈选型

#### 1.3.1 数据库选型对比

在高频交易数据存储领域，主流的数据库选择包括：

| 数据库 | 延迟 | 吞吐量 | 查询能力 | 成本 | 适用场景 |
|-------|------|--------|---------|------|---------|
| **kdb+** | <1μs | 极高 | q语言 | 极高($) | 顶级HFT |
| **TimescaleDB** | 1-10ms | 高 | SQL | 低 | 中高频交易 |
| **QuestDB** | 0.1-1ms | 极高 | SQL | 低 | 高频交易 |
| **ClickHouse** | 10-100ms | 极高 | SQL | 低 | 离线分析 |
| **InfluxDB** | 1-10ms | 中 | InfluxQL | 中 | 监控数据 |

**为什么选择PostgreSQL + TimescaleDB**：

1. **成熟稳定**: PostgreSQL拥有30+年历史，经过生产环境验证
2. **SQL标准**: 使用标准SQL，团队学习成本低
3. **生态丰富**: 丰富的工具链和社区支持
4. **扩展能力**: TimescaleDB提供时序数据专用优化
5. **成本效益**: 开源免费，部署成本低
6. **混合负载**: 支持实时写入和复杂分析查询

#### 1.3.2 完整技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
├─────────────┬─────────────┬─────────────┬─────────────────────┤
│  策略回测   │  实时信号   │  风险管理   │     绩效分析        │
│  (Python)   │  (Python)   │  (Python)   │     (Python)        │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                        服务层                                │
├─────────────┬─────────────┬─┴───────────┬─────────────────────┤
│  行情服务   │  计算服务   │  策略引擎   │     报表服务        │
│  (FastAPI)  │  (Celery)   │  (自定义)   │     (定时任务)      │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                        数据层                                │
├─────────────┬─────────────┬─┴───────────┬─────────────────────┤
│  热数据     │  温数据     │  冷数据     │     缓存层          │
│  (内存表)   │  TimescaleDB│  (S3/OSS)   │     (Redis)         │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                        接入层                                │
├─────────────┬─────────────┬─┴───────────┬─────────────────────┤
│  行情接入   │  订单接入   │  数据回补   │     监控日志        │
│ (WebSocket) │  (FIX API)  │  (REST API) │     (Prometheus)    │
└─────────────┴─────────────┴─────────────┴─────────────────────┘
```

**核心组件说明**：

1. **PostgreSQL 15+**: 主数据库，存储温数据和历史数据
2. **TimescaleDB 2.11+**: 时序数据库扩展，提供hypertable和continuous aggregates
3. **Redis 7+**: 缓存层，存储实时行情和计算结果
4. **Python 3.11+**: 主要开发语言，策略开发和数据分析
5. **FastAPI**: 高性能API框架，提供RESTful接口
6. **Celery**: 分布式任务队列，处理批量计算任务
7. **Prometheus + Grafana**: 监控告警和可视化

#### 1.3.3 硬件配置建议

**生产环境推荐配置**：

| 组件 | 配置 | 说明 |
|-----|------|------|
| CPU | 32核+ | Intel Xeon或AMD EPYC，高频优先 |
| 内存 | 256GB+ | 高频DDR4/DDR5 ECC内存 |
| 热数据存储 | 2TB NVMe SSD | 三星PM1733/Intel Optane |
| 温数据存储 | 10TB+ SATA SSD | 历史数据存储 |
| 冷数据存储 | 对象存储 | S3/MinIO，PB级扩展 |
| 网络 | 10Gbps+ | 低延迟网卡，RDMA支持 |

---

## 二、技术架构

### 2.1 系统架构图

```mermaid
flowchart TB
    subgraph 交易所层["📊 交易所层 Exchange Layer"]
        EX1[("上交所/深交所")]
        EX2[("上期所/大商所")]
        EX3[("港交所/NASDAQ")]
    end

    subgraph 行情接入层["📡 行情接入层 Feed Handler Layer"]
        FH1[行情网关A<br/>Gateway A]
        FH2[行情网关B<br/>Gateway B]
        FH3[行情网关C<br/>Gateway C]
        LB[负载均衡器<br/>Load Balancer]
    end

    subgraph 实时计算层["⚡ 实时计算层 Real-time Compute"]
        subgraph 内存计算["内存计算集群"]
            MC1[(内存表<br/>Hot Data)]
            MC2[(Redis<br/>Cache)]
        end
        CE[计算引擎<br/>Compute Engine]
        SE[策略引擎<br/>Strategy Engine]
    end

    subgraph 存储层["💾 存储层 Storage Layer"]
        subgraph 热存储["热存储 Hot Storage<br/>RAM"]
            RAM1[(UNLOGGED表<br/>实时行情)]
            RAM2[(内存表<br/>订单簿)]
        end
        subgraph 温存储["温存储 Warm Storage<br/>NVMe SSD"]
            TS[(TimescaleDB<br/>Hypertables)]
            PG[(PostgreSQL<br/>关系数据)]
        end
        subgraph 冷存储["冷存储 Cold Storage<br/>对象存储"]
            S3[(S3/OSS<br/>历史归档)]
        end
    end

    subgraph 分析层["📈 分析层 Analytics Layer"]
        BT[回测引擎<br/>Backtest Engine]
        TA[技术分析<br/>Technical Analysis]
        RA[风险分析<br/>Risk Analysis]
        PA[绩效分析<br/>Performance Analysis]
    end

    subgraph 应用层["🖥️ 应用层 Application Layer"]
        WEB[Web交易终端]
        API[REST API]
        ALERT[告警系统]
        REPORT[报表系统]
    end

    EX1 -->|TCP/UDP| FH1
    EX2 -->|TCP/UDP| FH2
    EX3 -->|TCP/UDP| FH3
    FH1 -->|ZeroMQ| LB
    FH2 -->|ZeroMQ| LB
    FH3 -->|ZeroMQ| LB
    LB -->|Pub/Sub| CE
    LB -->|Pub/Sub| SE

    CE -->|写入| MC1
    CE -->|写入| MC2
    SE -->|读取| MC1

    MC1 -->|批量写入| TS
    MC1 -->|归档| RAM1
    TS -->|历史查询| BT
    TS -->|历史查询| TA

    BT -->|结果| API
    TA -->|信号| ALERT
    SE -->|订单| WEB

    TS -.->|自动归档| S3

    style 交易所层 fill:#e1f5fe
    style 行情接入层 fill:#fff3e0
    style 实时计算层 fill:#f3e5f5
    style 存储层 fill:#e8f5e9
    style 分析层 fill:#fce4ec
    style 应用层 fill:#f5f5f5
```

### 2.2 数据流架构

```mermaid
sequenceDiagram
    participant EX as 交易所
    participant FH as 行情网关
    participant RAM as 内存表
    participant REDIS as Redis
    participant TSDB as TimescaleDB
    participant COLD as 对象存储
    participant STRATEGY as 策略引擎

    rect rgb(230, 245, 255)
        Note over EX,STRATEGY: 实时数据流 (Real-time Flow)
        loop 每秒百万级消息
            EX->>FH: Tick数据 (UDP/TCP)
            FH->>FH: 协议解析+时间戳
            par 并行写入
                FH->>RAM: 写入内存表 (亚毫秒)
                FH->>REDIS: 发布Pub/Sub (微秒)
            end
            REDIS->>STRATEGY: 推送实时行情
            STRATEGY->>STRATEGY: 策略计算
        end
    end

    rect rgb(255, 243, 224)
        Note over RAM,TSDB: 批量持久化 (Batch Persistence)
        loop 每秒执行
            RAM->>TSDB: 批量INSERT (1000条/批)
            TSDB->>TSDB: Hypertable自动分区
        end
    end

    rect rgb(243, 229, 245)
        Note over TSDB,COLD: 数据生命周期 (Data Lifecycle)
        TSDB->>TSDB: Continuous Aggregates (K线)
        TSDB->>COLD: 7天后自动归档
        COLD->>TSDB: 按需查询(查询下推)
    end
```

### 2.3 分层存储架构

```mermaid
flowchart LR
    subgraph 分层存储["三层存储架构 Tiered Storage"]
        direction TB

        subgraph Layer1["Layer 1: 热数据层<br/>Hot Tier<br/>RAM + NVMe"]
            direction LR
            H1[(内存表<br/>unlogged)]
            H2[(Redis<br/>Stream)]
            H3[(NVMe SSD<br/>WAL Buffer)]

            H1 -->|今日数据| USE1[实时查询]
            H2 -->|订阅推送| USE2[策略计算]
        end

        subgraph Layer2["Layer 2: 温数据层<br/>Warm Tier<br/>SSD Storage"]
            direction LR
            W1[(TimescaleDB<br/>Hypertables)]
            W2[(连续聚合<br/>K线数据)]
            W3[(索引数据<br/>BRIN/B-tree)]

            W1 -->|近7天数据| USE3[日内分析]
            W2 -->|预聚合| USE4[快速查询]
        end

        subgraph Layer3["Layer 3: 冷数据层<br/>Cold Tier<br/>Object Storage"]
            direction LR
            C1[(S3/OSS<br/>Parquet)]
            C2[(压缩归档<br/>gzip/zstd)]

            C1 -->|历史数据| USE5[策略回测]
            C2 -->|压缩存储| USE6[合规存档]
        end
    end

    Layer1 -.->|自动迁移| Layer2
    Layer2 -.->|自动归档| Layer3

    style Layer1 fill:#ffebee
    style Layer2 fill:#e3f2fd
    style Layer3 fill:#f3e5f5
```

**分层存储策略详解**：

| 层级 | 存储介质 | 保留时间 | 查询延迟 | 使用场景 |
|-----|---------|---------|---------|---------|
| 热数据 | RAM + NVMe | 1天 | <1ms | 实时行情、订单簿、策略计算 |
| 温数据 | SSD | 7-30天 | 10-100ms | 日内分析、K线查询、技术指标 |
| 冷数据 | 对象存储 | 永久 | 1-10s | 历史回测、合规审计、数据挖掘 |

**自动迁移策略**：

```sql
-- TimescaleDB 自动数据分层策略
-- 1. 设置数据保留策略
SELECT add_retention_policy('tick_data', INTERVAL '30 days');

-- 2. 配置连续聚合策略
SELECT add_continuous_aggregate_policy('candle_1min',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 minute'
);

-- 3. 配置分层存储 (TimescaleDB 2.11+)
SELECT add_tiering_policy('tick_data',
    INTERVAL '7 days',
    's3_tiering_server'
);
```

---

## 三、数据模型设计

### 3.1 核心表结构概览

```mermaid
erDiagram
    TICK_DATA ||--o{ CANDLE_1MIN : aggregates_to
    TICK_DATA ||--o{ ORDER_BOOK : updates
    CANDLE_1MIN ||--o{ CANDLE_5MIN : aggregates_to
    CANDLE_5MIN ||--o{ CANDLE_1HOUR : aggregates_to
    CANDLE_1HOUR ||--o{ CANDLE_1DAY : aggregates_to
    TICK_DATA ||--o{ TRADING_SIGNALS : generates
    TRADING_SIGNALS ||--|| STRATEGY_PERFORMANCE : measures

    TICK_DATA {
        timestamptz ts timestamp_6
        varchar symbol "股票代码"
        decimal price "成交价格"
        bigint volume "成交量"
        char side "买卖方向"
        bigint order_id "委托号"
    }

    CANDLE_1MIN {
        timestamptz bucket "时间桶"
        varchar symbol "股票代码"
        decimal open "开盘价"
        decimal high "最高价"
        decimal low "最低价"
        decimal close "收盘价"
        bigint volume "成交量"
        bigint trades "成交笔数"
    }

    ORDER_BOOK {
        timestamptz ts "时间戳"
        varchar symbol "股票代码"
        int level "档位"
        decimal bid_price "买价"
        bigint bid_size "买量"
        decimal ask_price "卖价"
        bigint ask_size "卖量"
    }

    TRADING_SIGNALS {
        timestamptz ts "信号时间"
        varchar symbol "股票代码"
        varchar strategy "策略名"
        varchar signal_type "信号类型"
        decimal price "触发价格"
        int quantity "建议数量"
        jsonb metadata "元数据"
    }

    STRATEGY_PERFORMANCE {
        varchar strategy_id "策略ID"
        date trade_date "交易日期"
        decimal total_return "总收益"
        decimal sharpe_ratio "夏普比率"
        decimal max_drawdown "最大回撤"
        int total_trades "总交易次数"
        decimal win_rate "胜率"
    }
```

### 3.2 实时行情表

```sql
-- =====================================================
-- 实时Tick数据表 - 逐笔成交数据
-- 特点: 纳秒级时间戳、超高速写入、自动分区
-- 参考: kdb+ trade表设计
-- =====================================================

-- 创建主表 (PostgreSQL原生表)
CREATE TABLE IF NOT EXISTS tick_data (
    -- 主键: 纳秒级时间戳 + 交易所 + 股票代码
    ts TIMESTAMP(6) WITH TIME ZONE NOT NULL,  -- 成交时间 (微秒级)
    ns_offset INTEGER DEFAULT 0,               -- 纳秒偏移量 (0-999)
    exchange VARCHAR(10) NOT NULL,             -- 交易所代码: SSE/SZSE/SHFE
    symbol VARCHAR(20) NOT NULL,               -- 股票代码: 000001.SZ

    -- 成交信息
    price DECIMAL(18, 8) NOT NULL,             -- 成交价格
    volume BIGINT NOT NULL,                    -- 成交量(股/手)
    amount DECIMAL(24, 8),                     -- 成交金额

    -- 买卖方向
    side CHAR(1) NOT NULL CHECK (side IN ('B', 'S', 'N')), -- B=买 S=卖 N=中性

    -- 委托信息
    bid_order_id BIGINT,                       -- 买方委托号
    ask_order_id BIGINT,                       -- 卖方委托号

    -- 订单簿信息 (L1快照)
    bid_price DECIMAL(18, 8),                  -- 买一价
    bid_size BIGINT,                           -- 买一量
    ask_price DECIMAL(18, 8),                  -- 卖一价
    ask_size BIGINT,                           -- 卖一量

    -- 行情指标
    trade_type SMALLINT DEFAULT 0,             -- 成交类型: 0=普通 1=大单 2=竞价

    -- 元数据
    received_at TIMESTAMP(6) WITH TIME ZONE DEFAULT NOW(), -- 接收时间
    source VARCHAR(50),                        -- 数据源

    -- 主键约束
    PRIMARY KEY (ts, exchange, symbol, bid_order_id, ask_order_id)
) PARTITION BY RANGE (ts);

-- 转换为Hypertable (TimescaleDB扩展)
SELECT create_hypertable(
    'tick_data',           -- 表名
    'ts',                  -- 时间列
    chunk_time_interval => INTERVAL '1 day',  -- 每天一个分区
    if_not_exists => TRUE
);

-- 添加额外维度分区 (按交易所+股票代码)
-- 注意: TimescaleDB 2.0+ 支持多维分区
-- 这有助于提高特定股票的查询性能

-- 创建复合索引
CREATE INDEX idx_tick_symbol_ts ON tick_data (symbol, ts DESC);
CREATE INDEX idx_tick_exchange_symbol ON tick_data (exchange, symbol, ts DESC);

-- 创建BRIN索引 (适合时序数据的块范围索引，空间效率高)
-- BRIN索引特别适合时间序列数据，因为它只存储每个数据块的最小/最大值
CREATE INDEX idx_tick_ts_brin ON tick_data USING BRIN (ts)
    WITH (pages_per_range = 128);

-- 创建部分索引 (只索引特定条件的数据，如大单交易)
CREATE INDEX idx_tick_large ON tick_data (symbol, ts DESC)
    WHERE volume >= 100000;  -- 大单阈值: 10万股

-- 添加表注释
COMMENT ON TABLE tick_data IS '逐笔成交数据表 - 存储交易所推送的每笔成交记录';
COMMENT ON COLUMN tick_data.ts IS '成交时间戳，精确到微秒';
COMMENT ON COLUMN tick_data.ns_offset IS '纳秒偏移量，用于纳秒级精度';
COMMENT ON COLUMN tick_data.side IS '买卖方向: B=主动性买入 S=主动性卖出 N=中性';

-- =====================================================
-- 内存表版本 - 用于实时计算 (数据丢失风险!)
-- 特点: 无WAL日志，写入速度提升10倍+
-- 用途: 仅存储当日热数据，系统重启后数据丢失
-- =====================================================

CREATE UNLOGGED TABLE IF NOT EXISTS tick_data_hot (
    LIKE tick_data INCLUDING ALL
);

-- 内存表不需要BRIN索引，因为数据量小且在内存中
CREATE INDEX idx_tick_hot_symbol ON tick_data_hot (symbol, ts DESC);

COMMENT ON TABLE tick_data_hot IS '热数据内存表 - 无持久化，仅存储当日数据用于实时计算';

-- =====================================================
-- 创建压缩策略 (TimescaleDB企业版功能)
-- 7天前的数据自动压缩，节省90%+存储空间
-- =====================================================

-- 添加压缩策略
ALTER TABLE tick_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'exchange, symbol',
    timescaledb.compress_orderby = 'ts DESC'
);

-- 7天后自动压缩
SELECT add_compression_policy('tick_data', INTERVAL '7 days');

-- 添加数据保留策略 (可选)
-- SELECT add_retention_policy('tick_data', INTERVAL '2 years');
```

### 3.3 K线聚合表

```sql
-- =====================================================
-- K线数据表 - 多时间周期OHLCV数据
-- 使用TimescaleDB Continuous Aggregates自动维护
-- =====================================================

-- -------------------------------------------------
-- 1分钟K线 (基础周期，其他周期由此聚合)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS candle_1min (
    bucket TIMESTAMP WITH TIME ZONE NOT NULL,  -- 时间桶
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    -- OHLCV数据
    open DECIMAL(18, 8) NOT NULL,              -- 开盘价
    high DECIMAL(18, 8) NOT NULL,              -- 最高价
    low DECIMAL(18, 8) NOT NULL,               -- 最低价
    close DECIMAL(18, 8) NOT NULL,             -- 收盘价
    volume BIGINT NOT NULL,                    -- 成交量
    amount DECIMAL(24, 8),                     -- 成交金额
    trades BIGINT,                             -- 成交笔数

    -- 额外统计
    vwap DECIMAL(18, 8),                       -- 成交量加权平均价

    PRIMARY KEY (bucket, exchange, symbol)
);

SELECT create_hypertable('candle_1min', 'bucket', chunk_time_interval => INTERVAL '7 days');

-- -------------------------------------------------
-- 连续聚合视图: 从Tick数据自动生成1分钟K线
-- -------------------------------------------------
CREATE MATERIALIZED VIEW candle_1min_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', ts) AS bucket,
    exchange,
    symbol,
    first(price, ts) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, ts) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    count(*) AS trades,
    sum(price * volume) / NULLIF(sum(volume), 0) AS vwap
FROM tick_data
GROUP BY bucket, exchange, symbol
WITH NO DATA;

-- 配置连续聚合刷新策略
SELECT add_continuous_aggregate_policy('candle_1min_continuous',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    if_not_exists => TRUE
);

-- 创建索引
CREATE INDEX idx_candle_1min_symbol ON candle_1min (symbol, bucket DESC);

-- -------------------------------------------------
-- 5分钟K线
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS candle_5min (
    bucket TIMESTAMP WITH TIME ZONE NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(18, 8) NOT NULL,
    high DECIMAL(18, 8) NOT NULL,
    low DECIMAL(18, 8) NOT NULL,
    close DECIMAL(18, 8) NOT NULL,
    volume BIGINT NOT NULL,
    amount DECIMAL(24, 8),
    trades BIGINT,
    PRIMARY KEY (bucket, exchange, symbol)
);

SELECT create_hypertable('candle_5min', 'bucket', chunk_time_interval => INTERVAL '30 days');

-- 从1分钟K线聚合到5分钟
CREATE MATERIALIZED VIEW candle_5min_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', bucket) AS bucket,
    exchange,
    symbol,
    first(open, bucket) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, bucket) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    sum(trades) AS trades
FROM candle_1min
GROUP BY bucket, exchange, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('candle_5min_continuous',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

-- -------------------------------------------------
-- 1小时K线
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS candle_1hour (
    bucket TIMESTAMP WITH TIME ZONE NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(18, 8) NOT NULL,
    high DECIMAL(18, 8) NOT NULL,
    low DECIMAL(18, 8) NOT NULL,
    close DECIMAL(18, 8) NOT NULL,
    volume BIGINT NOT NULL,
    amount DECIMAL(24, 8),
    trades BIGINT,
    PRIMARY KEY (bucket, exchange, symbol)
);

SELECT create_hypertable('candle_1hour', 'bucket', chunk_time_interval => INTERVAL '90 days');

CREATE MATERIALIZED VIEW candle_1hour_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', bucket) AS bucket,
    exchange,
    symbol,
    first(open, bucket) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, bucket) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    sum(trades) AS trades
FROM candle_1min
GROUP BY bucket, exchange, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('candle_1hour_continuous',
    start_offset => INTERVAL '6 months',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour'
);

-- -------------------------------------------------
-- 日线K线
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS candle_1day (
    bucket DATE NOT NULL,                      -- 日线使用DATE类型
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(18, 8) NOT NULL,
    high DECIMAL(18, 8) NOT NULL,
    low DECIMAL(18, 8) NOT NULL,
    close DECIMAL(18, 8) NOT NULL,
    volume BIGINT NOT NULL,
    amount DECIMAL(24, 8),
    trades BIGINT,
    pre_close DECIMAL(18, 8),                  -- 昨收
    change_pct DECIMAL(8, 4),                  -- 涨跌幅
    PRIMARY KEY (bucket, exchange, symbol)
);

SELECT create_hypertable('candle_1day', 'bucket', chunk_time_interval => INTERVAL '1 year');

CREATE MATERIALIZED VIEW candle_1day_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', bucket)::DATE AS bucket,
    exchange,
    symbol,
    first(open, bucket) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, bucket) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    sum(trades) AS trades,
    NULL::DECIMAL AS pre_close,                -- 需要后续更新
    NULL::DECIMAL AS change_pct
FROM candle_1min
GROUP BY time_bucket('1 day', bucket), exchange, symbol
WITH NO DATA;

SELECT add_continuous_aggregate_policy('candle_1day_continuous',
    start_offset => INTERVAL '2 years',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day'
);

-- 索引
CREATE INDEX idx_candle_5min_symbol ON candle_5min (symbol, bucket DESC);
CREATE INDEX idx_candle_1hour_symbol ON candle_1hour (symbol, bucket DESC);
CREATE INDEX idx_candle_1day_symbol ON candle_1day (symbol, bucket DESC);

-- -------------------------------------------------
-- K线数据手动维护函数 (处理缺失数据、复权等)
-- -------------------------------------------------

-- 函数: 补充缺失的K线数据 (停牌等情况)
CREATE OR REPLACE FUNCTION fill_missing_candles(
    p_symbol VARCHAR,
    p_start_date TIMESTAMP WITH TIME ZONE,
    p_end_date TIMESTAMP WITH TIME ZONE,
    p_interval INTERVAL DEFAULT '1 minute'
)
RETURNS TABLE (
    missing_bucket TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    WITH time_series AS (
        SELECT generate_series(
            p_start_date,
            p_end_date,
            p_interval
        ) AS bucket
    )
    SELECT ts.bucket
    FROM time_series ts
    LEFT JOIN candle_1min c ON c.bucket = ts.bucket AND c.symbol = p_symbol
    WHERE c.bucket IS NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION fill_missing_candles IS '查找指定时间段内缺失的K线数据';
```

### 3.4 订单簿快照表

```sql
-- =====================================================
-- 订单簿快照表 - Level 2/L3 市场深度数据
-- 存储每个时间点的完整买卖队列
-- =====================================================

-- -------------------------------------------------
-- 订单簿档位表 (每个时间点存储10档深度)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS order_book (
    ts TIMESTAMP(6) WITH TIME ZONE NOT NULL,   -- 快照时间
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    level SMALLINT NOT NULL CHECK (level > 0 AND level <= 20),  -- 档位 1-20

    -- 买方信息
    bid_price DECIMAL(18, 8),                  -- 买价
    bid_size BIGINT,                           -- 买量
    bid_orders INTEGER,                        -- 买委托笔数

    -- 卖方信息
    ask_price DECIMAL(18, 8),                  -- 卖价
    ask_size BIGINT,                           -- 卖量
    ask_orders INTEGER,                        -- 卖委托笔数

    -- 衍生指标
    spread DECIMAL(18, 8) GENERATED ALWAYS AS (
        COALESCE(ask_price, 0) - COALESCE(bid_price, 0)
    ) STORED,                                   -- 买卖价差

    mid_price DECIMAL(18, 8) GENERATED ALWAYS AS (
        (COALESCE(bid_price, 0) + COALESCE(ask_price, 0)) / 2
    ) STORED,                                   -- 中间价

    PRIMARY KEY (ts, exchange, symbol, level)
);

SELECT create_hypertable('order_book', 'ts', chunk_time_interval => INTERVAL '1 day');

-- 索引
CREATE INDEX idx_ob_symbol_ts ON order_book (symbol, ts DESC);
CREATE INDEX idx_ob_ts_brin ON order_book USING BRIN (ts);

-- 注释
COMMENT ON TABLE order_book IS '订单簿快照表 - 存储L2/L3市场深度数据';
COMMENT ON COLUMN order_book.level IS '档位: 1=最优 数值越大档位越深';
COMMENT ON COLUMN order_book.bid_orders IS '该价位委托笔数 (部分交易所提供)';

-- -------------------------------------------------
-- 订单簿增量更新表 (用于快速重建)
-- 存储订单簿的增量变化，而非完整快照
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS order_book_delta (
    seq_id BIGSERIAL PRIMARY KEY,              -- 序列号，保证顺序
    ts TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    side CHAR(1) NOT NULL CHECK (side IN ('B', 'A')),  -- B=Buy A=Ask
    price DECIMAL(18, 8) NOT NULL,
    delta_size BIGINT NOT NULL,                -- 变化量: 正=增加 负=减少
    new_size BIGINT,                           -- 变化后的新量 (0表示删除)

    -- 事件类型
    event_type SMALLINT DEFAULT 0,             -- 0=修改 1=新增 2=删除

    -- 性能优化
    received_at TIMESTAMP(6) WITH TIME ZONE DEFAULT NOW()
);

SELECT create_hypertable('order_book_delta', 'ts', chunk_time_interval => INTERVAL '1 day');

CREATE INDEX idx_ob_delta_symbol ON order_book_delta (symbol, ts DESC);
CREATE INDEX idx_ob_delta_seq ON order_book_delta (seq_id);

COMMENT ON TABLE order_book_delta IS '订单簿增量更新表 - 记录订单簿变化事件';

-- -------------------------------------------------
-- 订单簿统计摘要表 (降低查询复杂度)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS order_book_stats (
    ts TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    symbol VARCHAR(20) NOT NULL,

    -- 基础统计
    best_bid DECIMAL(18, 8),                   -- 最优买价
    best_ask DECIMAL(18, 8),                   -- 最优卖价
    spread DECIMAL(18, 8),                     -- 价差
    mid_price DECIMAL(18, 8),                  -- 中间价

    -- 深度统计
    total_bid_size BIGINT,                     -- 买方总挂单量
    total_ask_size BIGINT,                     -- 卖方总挂单量
    imbalance DECIMAL(8, 4),                   -- 买卖失衡度: (bid-ask)/(bid+ask)

    -- 5档统计
    bid_depth_5 BIGINT,                        -- 前5档买量
    ask_depth_5 BIGINT,                        -- 前5档卖量
    weighted_spread_5 DECIMAL(18, 8),          -- 5档加权价差

    -- 流动性指标
    bid_slope DECIMAL(18, 8),                  -- 买方斜率 (价格弹性)
    ask_slope DECIMAL(18, 8),                  -- 卖方斜率

    PRIMARY KEY (ts, exchange, symbol)
);

SELECT create_hypertable('order_book_stats', 'ts', chunk_time_interval => INTERVAL '1 day');

CREATE INDEX idx_ob_stats_symbol ON order_book_stats (symbol, ts DESC);

-- 连续聚合生成统计摘要
CREATE MATERIALIZED VIEW order_book_stats_continuous
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 second', ts) AS ts,
    exchange,
    symbol,
    MAX(CASE WHEN level = 1 THEN bid_price END) AS best_bid,
    MAX(CASE WHEN level = 1 THEN ask_price END) AS best_ask,
    SUM(CASE WHEN side = 'B' THEN bid_size ELSE 0 END) AS total_bid_size,
    SUM(CASE WHEN side = 'A' THEN ask_size ELSE 0 END) AS total_ask_size
FROM order_book
GROUP BY time_bucket('1 second', ts), exchange, symbol
WITH NO DATA;

-- -------------------------------------------------
-- 订单簿重建函数
-- -------------------------------------------------

-- 函数: 重建指定时间点的订单簿
CREATE OR REPLACE FUNCTION rebuild_order_book(
    p_symbol VARCHAR,
    p_ts TIMESTAMP WITH TIME ZONE,
    p_levels INTEGER DEFAULT 10
)
RETURNS TABLE (
    level INTEGER,
    bid_price DECIMAL,
    bid_size BIGINT,
    ask_price DECIMAL,
    ask_size BIGINT
) AS $$
DECLARE
    v_last_snapshot_ts TIMESTAMP WITH TIME ZONE;
BEGIN
    -- 找到最近的完整快照时间
    SELECT MAX(ts) INTO v_last_snapshot_ts
    FROM order_book
    WHERE symbol = p_symbol AND ts <= p_ts;

    -- 基于快照应用增量更新
    RETURN QUERY
    WITH base_snapshot AS (
        SELECT * FROM order_book
        WHERE symbol = p_symbol AND ts = v_last_snapshot_ts
    ),
    deltas AS (
        SELECT * FROM order_book_delta
        WHERE symbol = p_symbol
          AND ts > v_last_snapshot_ts
          AND ts <= p_ts
        ORDER BY seq_id
    ),
    reconstructed AS (
        -- 应用增量更新逻辑 (简化版)
        SELECT
            ROW_NUMBER() OVER (ORDER BY price DESC) as lvl,
            price,
            SUM(delta_size) as size,
            side
        FROM (
            SELECT price, bid_size as size, 'B'::CHAR as side FROM base_snapshot
            UNION ALL
            SELECT price, delta_size, side FROM deltas
        ) combined
        WHERE size > 0
        GROUP BY price, side
    )
    SELECT
        r.lvl::INTEGER,
        CASE WHEN r.side = 'B' THEN r.price END as bid_price,
        CASE WHEN r.side = 'B' THEN r.size END as bid_size,
        CASE WHEN r.side = 'A' THEN r.price END as ask_price,
        CASE WHEN r.side = 'A' THEN r.size END as ask_size
    FROM reconstructed r
    WHERE r.lvl <= p_levels
    ORDER BY r.side, r.lvl;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION rebuild_order_book IS '基于快照和增量更新重建指定时间点的订单簿';
```

### 3.5 交易信号表

```sql
-- =====================================================
-- 交易信号表 - 策略产生的交易信号
-- =====================================================

CREATE TABLE IF NOT EXISTS trading_signals (
    signal_id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP(6) WITH TIME ZONE NOT NULL,   -- 信号产生时间

    -- 标识信息
    strategy_id VARCHAR(50) NOT NULL,          -- 策略ID
    strategy_version VARCHAR(20),              -- 策略版本
    symbol VARCHAR(20) NOT NULL,               -- 标的代码
    exchange VARCHAR(10) NOT NULL,

    -- 信号内容
    signal_type VARCHAR(20) NOT NULL CHECK (signal_type IN (
        'BUY', 'SELL', 'COVER', 'SHORT',      -- 基础信号
        'ENTER_LONG', 'EXIT_LONG',             -- 多头
        'ENTER_SHORT', 'EXIT_SHORT',           -- 空头
        'HOLD', 'CANCEL'                       -- 其他
    )),

    -- 价格数量
    trigger_price DECIMAL(18, 8) NOT NULL,     -- 触发价格
    suggested_quantity BIGINT,                 -- 建议数量
    suggested_price DECIMAL(18, 8),            -- 建议价格

    -- 信号强度
    confidence DECIMAL(5, 4) CHECK (confidence >= 0 AND confidence <= 1),  -- 置信度 0-1
    urgency SMALLINT DEFAULT 1 CHECK (urgency IN (0, 1, 2)),  -- 0=低 1=中 2=高

    -- 信号原因
    signal_reason TEXT,                        -- 信号产生原因描述
    indicators JSONB,                          -- 相关指标值

    -- 上下文信息
    market_data JSONB,                         -- 当时的市场数据快照
    position_before JSONB,                     -- 信号前持仓

    -- 执行状态
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN (
        'PENDING', 'ACKNOWLEDGED', 'EXECUTED', 'CANCELLED', 'EXPIRED'
    )),
    executed_at TIMESTAMP WITH TIME ZONE,
    execution_price DECIMAL(18, 8),
    execution_quantity BIGINT,

    -- 性能追踪
    latency_ms DECIMAL(10, 3),                 -- 从信号到执行的延迟
    slippage DECIMAL(10, 4),                   -- 滑点

    -- 元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    source_ip INET,                            -- 产生信号的IP
    trace_id VARCHAR(100)                      -- 分布式追踪ID
);

SELECT create_hypertable('trading_signals', 'ts', chunk_time_interval => INTERVAL '7 days');

-- 索引
CREATE INDEX idx_signals_strategy ON trading_signals (strategy_id, ts DESC);
CREATE INDEX idx_signals_symbol ON trading_signals (symbol, ts DESC);
CREATE INDEX idx_signals_status ON trading_signals (status) WHERE status = 'PENDING';
CREATE INDEX idx_signals_type ON trading_signals (signal_type, ts DESC);

-- JSONB索引 (用于灵活查询)
CREATE INDEX idx_signals_indicators ON trading_signals USING GIN (indicators);

COMMENT ON TABLE trading_signals IS '交易信号表 - 记录所有策略产生的交易信号';
COMMENT ON COLUMN trading_signals.confidence IS '信号置信度 0.0-1.0';
COMMENT ON COLUMN trading_signals.urgency IS '紧急程度: 0=低优先级 1=普通 2=立即执行';

-- -------------------------------------------------
-- 信号触发器: 状态变更时自动更新时间戳
-- -------------------------------------------------
CREATE OR REPLACE FUNCTION update_signal_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_signals_update
    BEFORE UPDATE ON trading_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_signal_timestamp();

-- -------------------------------------------------
-- 信号统计视图
-- -------------------------------------------------
CREATE OR REPLACE VIEW signal_statistics AS
SELECT
    strategy_id,
    DATE(ts) as trade_date,
    signal_type,
    COUNT(*) as signal_count,
    AVG(confidence) as avg_confidence,
    AVG(latency_ms) as avg_latency,
    AVG(slippage) as avg_slippage,
    SUM(CASE WHEN status = 'EXECUTED' THEN 1 ELSE 0 END) as executed_count,
    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled_count
FROM trading_signals
GROUP BY strategy_id, DATE(ts), signal_type;
```

### 3.6 策略绩效表

```sql
-- =====================================================
-- 策略绩效表 - 策略回测和实盘绩效
-- =====================================================

-- -------------------------------------------------
-- 策略基本信息表
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS strategies (
    strategy_id VARCHAR(50) PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    strategy_type VARCHAR(30) CHECK (strategy_type IN (
        'TREND_FOLLOWING', 'MEAN_REVERSION', 'ARBITRAGE',
        'MARKET_MAKING', 'EVENT_DRIVEN', 'STATISTICAL',
        'MACHINE_LEARNING', 'MULTI_FACTOR'
    )),
    description TEXT,
    symbols TEXT[],                            -- 适用标的列表
    timeframes VARCHAR[],                      -- 适用时间周期

    -- 参数配置
    parameters JSONB,                          -- 策略参数
    risk_limits JSONB,                         -- 风险控制参数

    -- 版本控制
    version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    -- 元数据
    author VARCHAR(50),
    tags TEXT[]
);

-- -------------------------------------------------
-- 策略绩效统计表 (按日统计)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy_id VARCHAR(50) NOT NULL,
    trade_date DATE NOT NULL,

    -- 收益指标
    daily_pnl DECIMAL(18, 4) DEFAULT 0,        -- 日盈亏
    cumulative_pnl DECIMAL(18, 4) DEFAULT 0,   -- 累计盈亏
    daily_return DECIMAL(10, 6),               -- 日收益率
    cumulative_return DECIMAL(10, 6),          -- 累计收益率

    -- 交易统计
    total_trades INTEGER DEFAULT 0,            -- 总交易次数
    winning_trades INTEGER DEFAULT 0,          -- 盈利次数
    losing_trades INTEGER DEFAULT 0,           -- 亏损次数
    win_rate DECIMAL(6, 4),                    -- 胜率

    -- 盈亏指标
    avg_profit DECIMAL(18, 4),                 -- 平均盈利
    avg_loss DECIMAL(18, 4),                   -- 平均亏损
    profit_factor DECIMAL(10, 4),              -- 盈亏比
    expectancy DECIMAL(18, 4),                 -- 期望值

    -- 风险指标
    max_drawdown DECIMAL(10, 6),               -- 当日最大回撤
    max_drawdown_pct DECIMAL(10, 6),           -- 当日最大回撤百分比
    volatility DECIMAL(10, 6),                 -- 日波动率

    -- 综合指标
    sharpe_ratio DECIMAL(10, 4),               -- 夏普比率
    sortino_ratio DECIMAL(10, 4),              -- 索提诺比率
    calmar_ratio DECIMAL(10, 4),               -- 卡尔马比率

    -- 持仓统计
    avg_position_size DECIMAL(18, 4),          -- 平均持仓
    max_position_size DECIMAL(18, 4),          -- 最大持仓
    turnover_rate DECIMAL(10, 4),              -- 换手率

    -- 成本分析
    total_commission DECIMAL(18, 4) DEFAULT 0, -- 总手续费
    total_slippage DECIMAL(18, 4) DEFAULT 0,   -- 总滑点

    -- 元数据
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_backtest BOOLEAN DEFAULT FALSE,         -- 是否回测数据

    PRIMARY KEY (strategy_id, trade_date)
);

-- 索引
CREATE INDEX idx_perf_strategy ON strategy_performance (strategy_id, trade_date DESC);
CREATE INDEX idx_perf_date ON strategy_performance (trade_date);
CREATE INDEX idx_perf_pnl ON strategy_performance (daily_pnl DESC) WHERE daily_pnl > 0;

COMMENT ON TABLE strategy_performance IS '策略绩效表 - 按日统计策略表现';

-- -------------------------------------------------
-- 策略交易明细表 (每笔交易的详细记录)
-- -------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_trades (
    trade_id BIGSERIAL PRIMARY KEY,
    strategy_id VARCHAR(50) NOT NULL,
    signal_id BIGINT REFERENCES trading_signals(signal_id),

    -- 交易信息
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(10) CHECK (trade_type IN ('BUY', 'SELL', 'SHORT', 'COVER')),
    entry_time TIMESTAMP(6) WITH TIME ZONE,    -- 开仓时间
    exit_time TIMESTAMP(6) WITH TIME ZONE,     -- 平仓时间

    -- 价格
    entry_price DECIMAL(18, 8),                -- 开仓价格
    exit_price DECIMAL(18, 8),                 -- 平仓价格
    quantity BIGINT,                           -- 数量

    -- 盈亏
    gross_pnl DECIMAL(18, 4),                  -- 毛盈亏
    commission DECIMAL(18, 4) DEFAULT 0,       -- 手续费
    slippage DECIMAL(18, 4) DEFAULT 0,         -- 滑点
    net_pnl DECIMAL(18, 4),                    -- 净盈亏
    return_pct DECIMAL(10, 6),                 -- 收益率

    -- 风险
    max_favorable DECIMAL(18, 4),              -- 最大有利偏移
    max_adverse DECIMAL(18, 4),                -- 最大不利偏移
    mae DECIMAL(18, 4),                        -- 最大回撤(入场后)
    mfe DECIMAL(18, 4),                        -- 最大盈利(入场后)

    -- 标签
    tags TEXT[],                               -- 标签: 如"止损","止盈"等
    notes TEXT,                                -- 备注

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

SELECT create_hypertable('strategy_trades', 'entry_time', chunk_time_interval => INTERVAL '30 days');

CREATE INDEX idx_trades_strategy ON strategy_trades (strategy_id, entry_time DESC);
CREATE INDEX idx_trades_symbol ON strategy_trades (symbol, entry_time DESC);
CREATE INDEX idx_trades_pnl ON strategy_trades (net_pnl) WHERE net_pnl < 0;

-- -------------------------------------------------
-- 绩效计算函数
-- -------------------------------------------------

-- 函数: 计算策略夏普比率
CREATE OR REPLACE FUNCTION calculate_sharpe_ratio(
    p_strategy_id VARCHAR,
    p_start_date DATE,
    p_end_date DATE,
    p_risk_free_rate DECIMAL DEFAULT 0.02  -- 年化无风险利率2%
)
RETURNS DECIMAL AS $$
DECLARE
    v_avg_return DECIMAL;
    v_std_return DECIMAL;
    v_trading_days INTEGER;
BEGIN
    -- 计算日平均收益率和标准差
    SELECT
        AVG(daily_return),
        STDDEV(daily_return),
        COUNT(*)
    INTO v_avg_return, v_std_return, v_trading_days
    FROM strategy_performance
    WHERE strategy_id = p_strategy_id
      AND trade_date BETWEEN p_start_date AND p_end_date
      AND daily_return IS NOT NULL;

    -- 避免除零
    IF v_std_return IS NULL OR v_std_return = 0 THEN
        RETURN 0;
    END IF;

    -- 夏普比率 = (平均收益率 - 无风险利率/252) / 标准差 * sqrt(252)
    RETURN ((v_avg_return - p_risk_free_rate / 252) / v_std_return) * SQRT(252);
END;
$$ LANGUAGE plpgsql;

-- 函数: 计算最大回撤
CREATE OR REPLACE FUNCTION calculate_max_drawdown(
    p_strategy_id VARCHAR,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    max_drawdown DECIMAL,
    max_drawdown_pct DECIMAL,
    drawdown_start DATE,
    drawdown_end DATE
) AS $$
BEGIN
    RETURN QUERY
    WITH daily_cumulative AS (
        SELECT
            trade_date,
            cumulative_pnl,
            MAX(cumulative_pnl) OVER (ORDER BY trade_date) as running_max
        FROM strategy_performance
        WHERE strategy_id = p_strategy_id
          AND trade_date BETWEEN p_start_date AND p_end_date
    ),
    drawdowns AS (
        SELECT
            trade_date,
            cumulative_pnl,
            running_max,
            running_max - cumulative_pnl as drawdown,
            CASE WHEN running_max > 0
                 THEN (running_max - cumulative_pnl) / running_max
                 ELSE 0
            END as drawdown_pct
        FROM daily_cumulative
    )
    SELECT
        MAX(drawdown),
        MAX(drawdown_pct),
        MIN(trade_date) FILTER (WHERE drawdown = (SELECT MAX(drawdown) FROM drawdowns)),
        MAX(trade_date) FILTER (WHERE drawdown = (SELECT MAX(drawdown) FROM drawdowns))
    FROM drawdowns;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------
-- 绩效报告视图
-- -------------------------------------------------
CREATE OR REPLACE VIEW strategy_summary AS
SELECT
    sp.strategy_id,
    s.strategy_name,
    s.strategy_type,
    MIN(sp.trade_date) as start_date,
    MAX(sp.trade_date) as end_date,
    COUNT(*) as trading_days,
    SUM(sp.daily_pnl) as total_pnl,
    SUM(sp.total_trades) as total_trades,
    AVG(sp.win_rate) as avg_win_rate,
    MAX(sp.max_drawdown_pct) as max_drawdown,
    STDDEV(sp.daily_return) * SQRT(252) as annualized_volatility,
    (SUM(sp.daily_return) / NULLIF(STDDEV(sp.daily_return), 0)) * SQRT(252) as sharpe_ratio
FROM strategy_performance sp
JOIN strategies s ON sp.strategy_id = s.strategy_id
WHERE sp.is_backtest = FALSE
GROUP BY sp.strategy_id, s.strategy_name, s.strategy_type;
```

```python
    async def insert_to_postgres(self, tick: TickData) -> None:
        """写入PostgreSQL"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO tick_data_hot
                    (ts, ns_offset, exchange, symbol, price, volume, amount,
                     side, bid_order_id, ask_order_id, bid_price, bid_size,
                     ask_price, ask_size, received_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (ts, exchange, symbol, bid_order_id, ask_order_id) DO NOTHING
                    """,
                    tick.ts,
                    tick.ns_offset,
                    tick.exchange,
                    tick.symbol,
                    tick.price,
                    tick.volume,
                    tick.amount,
                    tick.side,
                    tick.bid_order_id,
                    tick.ask_order_id,
                    tick.bid_price,
                    tick.bid_size,
                    tick.ask_price,
                    tick.ask_size,
                    tick.received_at
                )
                self.stats['inserted_db'] += 1
        except Exception as e:
            logger.error(f"[{self.exchange}] PostgreSQL insert error: {e}")

    async def publish_to_redis(self, tick: TickData) -> None:
        """发布到Redis"""
        try:
            # 发布到Stream
            await self.redis.xadd(
                f"ticks:{tick.exchange}:{tick.symbol}",
                tick.to_dict(),
                maxlen=10000
            )

            # 更新最新行情
            await self.redis.hset(
                f"quote:{tick.exchange}:{tick.symbol}",
                mapping={
                    'price': str(tick.price),
                    'volume': tick.volume,
                    'ts': tick.ts.isoformat(),
                    'bid': str(tick.bid_price) if tick.bid_price else '',
                    'ask': str(tick.ask_price) if tick.ask_price else ''
                }
            )

            self.stats['inserted_redis'] += 1
        except Exception as e:
            logger.error(f"[{self.exchange}] Redis publish error: {e}")

    def add_tick_callback(self, callback: Callable[[TickData], None]) -> None:
        """添加Tick回调"""
        self.on_tick_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """添加错误回调"""
        self.on_error_callbacks.append(callback)

    async def batch_insert_task(self) -> None:
        """批量插入任务 - 定期将缓冲数据写入持久化存储"""
        while self.is_connected:
            await asyncio.sleep(1)

            if len(self.tick_buffer) >= 1000:
                await self.flush_buffer()

    async def flush_buffer(self) -> None:
        """刷新缓冲到数据库"""
        if not self.tick_buffer:
            return

        # 复制并清空缓冲
        buffer_copy = list(self.tick_buffer)
        self.tick_buffer.clear()

        try:
            async with self.db_pool.acquire() as conn:
                # 使用COPY进行批量插入
                records = [
                    (
                        t.ts, t.ns_offset, t.exchange, t.symbol, t.price,
                        t.volume, t.amount, t.side, t.bid_order_id, t.ask_order_id,
                        t.bid_price, t.bid_size, t.ask_price, t.ask_size, t.received_at
                    )
                    for t in buffer_copy
                ]

                await conn.copy_records_to_table(
                    'tick_data',
                    records=records,
                    columns=['ts', 'ns_offset', 'exchange', 'symbol', 'price',
                             'volume', 'amount', 'side', 'bid_order_id', 'ask_order_id',
                             'bid_price', 'bid_size', 'ask_price', 'ask_size', 'received_at']
                )
                logger.info(f"[{self.exchange}] Batch inserted {len(records)} records")
        except Exception as e:
            logger.error(f"[{self.exchange}] Batch insert error: {e}")

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.stats.copy()

class SSEFeed(ExchangeFeed):
    """上海证券交易所行情接入"""

    def __init__(self, symbols: List[str], db_pool: asyncpg.Pool, redis: aioredis.Redis):
        super().__init__(
            exchange='SSE',
            ws_url='wss://hq.sinajs.cn/ws',  # 示例地址
            symbols=symbols,
            db_pool=db_pool,
            redis=redis
        )

    async def subscribe(self) -> None:
        """订阅SSE行情"""
        subscribe_msg = {
            'action': 'subscribe',
            'symbols': self.symbols,
            'data_type': 'tick'
        }
        await self.websocket.send(json.dumps(subscribe_msg))
        logger.info(f"[{self.exchange}] Subscribed to {len(self.symbols)} symbols")

    def parse_message(self, message: str) -> Optional[TickData]:
        """解析SSE行情消息"""
        try:
            data = json.loads(message)

            # SSE格式示例
            tick = TickData(
                ts=datetime.fromtimestamp(data['time'] / 1000),
                ns_offset=data.get('ns', 0),
                exchange='SSE',
                symbol=data['code'],
                price=Decimal(str(data['price'])),
                volume=data['volume'],
                amount=Decimal(str(data.get('amount', 0))),
                side='B' if data.get('side') == 0 else 'S',
                bid_order_id=data.get('bid_order'),
                ask_order_id=data.get('ask_order'),
                bid_price=Decimal(str(data.get('bid1', 0))) if data.get('bid1') else None,
                bid_size=data.get('bid1_volume'),
                ask_price=Decimal(str(data.get('ask1', 0))) if data.get('ask1') else None,
                ask_size=data.get('ask1_volume')
            )
            return tick
        except Exception as e:
            logger.error(f"[{self.exchange}] Parse error: {e}, message: {message[:200]}")
            return None

    def parse_heartbeat(self, message: str) -> bool:
        """检查心跳"""
        try:
            data = json.loads(message)
            return data.get('type') == 'heartbeat'
        except:
            return False

class MarketDataManager:
    """行情管理器 - 管理多个交易所接入"""

    def __init__(self, db_config: Dict, redis_config: Dict):
        self.db_config = db_config
        self.redis_config = redis_config
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis: Optional[aioredis.Redis] = None
        self.feeds: Dict[str, ExchangeFeed] = {}
        self.running = False

    async def initialize(self) -> None:
        """初始化连接池"""
        # PostgreSQL连接池
        self.db_pool = await asyncpg.create_pool(
            host=self.db_config['host'],
            port=self.db_config['port'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            database=self.db_config['database'],
            min_size=10,
            max_size=50,
            command_timeout=60
        )

        # Redis连接
        self.redis = aioredis.Redis(
            host=self.redis_config['host'],
            port=self.redis_config['port'],
            db=self.redis_config['db'],
            decode_responses=True
        )

        logger.info("MarketDataManager initialized")

    async def add_feed(self, feed: ExchangeFeed) -> None:
        """添加行情源"""
        self.feeds[feed.exchange] = feed

    async def start(self) -> None:
        """启动所有行情源"""
        self.running = True

        tasks = []
        for feed in self.feeds.values():
            await feed.connect()
            tasks.append(asyncio.create_task(feed.receive_loop()))
            tasks.append(asyncio.create_task(feed.batch_insert_task()))

        # 监控任务
        tasks.append(asyncio.create_task(self.monitor_task()))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def stop(self) -> None:
        """停止所有行情源"""
        self.running = False
        for feed in self.feeds.values():
            await feed.disconnect()

        if self.db_pool:
            await self.db_pool.close()
        if self.redis:
            await self.redis.close()

        logger.info("MarketDataManager stopped")

    async def monitor_task(self) -> None:
        """监控任务 - 定期输出统计信息"""
        while self.running:
            await asyncio.sleep(60)

            for exchange, feed in self.feeds.items():
                stats = feed.get_stats()
                logger.info(
                    f"[{exchange}] Stats: received={stats['received']}, "
                    f"inserted_db={stats['inserted_db']}, "
                    f"inserted_redis={stats['inserted_redis']}, "
                    f"deduped={stats['deduped']}, errors={stats['errors']}"
                )

# ==================== 使用示例 ====================

async def main():
    """主函数示例"""
    # 配置
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'user': 'quant',
        'password': 'quant123',
        'database': 'trading'
    }

    redis_config = {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }

    # 初始化管理器
    manager = MarketDataManager(db_config, redis_config)
    await manager.initialize()

    # 添加上交所行情
    sse_symbols = ['600000', '600001', '600002']  # 浦发银行、邯郸钢铁等
    sse_feed = SSEFeed(sse_symbols, manager.db_pool, manager.redis)

    # 添加回调示例
    def on_tick(tick: TickData):
        if tick.volume > 100000:  # 大单提醒
            print(f"[ALERT] Large trade: {tick.symbol} @ {tick.price} vol={tick.volume}")

    sse_feed.add_tick_callback(on_tick)
    await manager.add_feed(sse_feed)

    # 启动
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("Received stop signal")
    finally:
        await manager.stop()

if **name** == '**main**':
    asyncio.run(main())

```

### 4.2 K线实时聚合引擎

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线实时聚合引擎 (Real-time Candle Aggregator)

功能:
- 从Redis Stream消费Tick数据
- 实时计算1分钟/5分钟/1小时K线
- 使用滑动窗口算法
- 支持多品种并发处理
- 自动检测缺失K线并补充

设计:
- 生产者-消费者模式
- 异步流水线处理
- 内存聚合 + 批量写入
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

import aioredis
import asyncpg

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """时间周期枚举"""
    MINUTE_1 = ("1m", 60)
    MINUTE_5 = ("5m", 300)
    MINUTE_15 = ("15m", 900)
    MINUTE_30 = ("30m", 1800)
    HOUR_1 = ("1h", 3600)
    HOUR_4 = ("4h", 14400)
    DAY_1 = ("1d", 86400)

    def __init__(self, code: str, seconds: int):
        self.code = code
        self.seconds = seconds

    @classmethod
    def from_code(cls, code: str) -> 'TimeFrame':
        for tf in cls:
            if tf.code == code:
                return tf
        raise ValueError(f"Unknown timeframe: {code}")


@dataclass
class Candle:
    """K线数据结构"""
    bucket: datetime
    exchange: str
    symbol: str
    timeframe: str
    open: Decimal = Decimal('0')
    high: Decimal = Decimal('0')
    low: Decimal = Decimal('999999999')
    close: Decimal = Decimal('0')
    volume: int = 0
    amount: Decimal = Decimal('0')
    trades: int = 0

    def update(self, price: Decimal, volume: int, amount: Decimal) -> None:
        """更新K线数据"""
        if self.trades == 0:
            self.open = price
            self.high = price
            self.low = price

        self.close = price
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.volume += volume
        self.amount += amount
        self.trades += 1

    def to_tuple(self) -> Tuple:
        """转换为数据库插入格式"""
        return (
            self.bucket,
            self.exchange,
            self.symbol,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume,
            self.amount,
            self.trades
        )


class CandleAggregator:
    """K线聚合器"""

    def __init__(
        self,
        redis: aioredis.Redis,
        db_pool: asyncpg.Pool,
        timeframes: List[TimeFrame] = None,
        flush_interval: int = 5
    ):
        self.redis = redis
        self.db_pool = db_pool
        self.timeframes = timeframes or [TimeFrame.MINUTE_1, TimeFrame.MINUTE_5, TimeFrame.HOUR_1]
        self.flush_interval = flush_interval

        # 内存聚合状态
        # key: (symbol, timeframe) -> current_candle
        self.current_candles: Dict[Tuple[str, str], Candle] = {}

        # 待写入缓冲
        self.pending_candles: List[Candle] = []

        # 消费组配置
        self.consumer_group = "candle_aggregator"
        self.consumer_name = f"consumer_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def get_bucket(self, ts: datetime, timeframe: TimeFrame) -> datetime:
        """计算时间桶"""
        seconds = timeframe.seconds
        timestamp = ts.timestamp()
        bucket_ts = (int(timestamp) // seconds) * seconds
        return datetime.fromtimestamp(bucket_ts)

    def process_tick(
        self,
        symbol: str,
        exchange: str,
        ts: datetime,
        price: Decimal,
        volume: int,
        amount: Decimal
    ) -> List[Candle]:
        """处理单条Tick，返回已完成的K线"""
        completed_candles = []

        for tf in self.timeframes:
            bucket = self.get_bucket(ts, tf)
            key = (symbol, tf.code)

            # 检查是否需要新开K线
            if key in self.current_candles:
                current = self.current_candles[key]
                if current.bucket != bucket:
                    # K线完成，加入待写入列表
                    completed_candles.append(current)
                    # 新开K线
                    self.current_candles[key] = Candle(
                        bucket=bucket,
                        exchange=exchange,
                        symbol=symbol,
                        timeframe=tf.code
                    )
            else:
                # 首次初始化
                self.current_candles[key] = Candle(
                    bucket=bucket,
                    exchange=exchange,
                    symbol=symbol,
                    timeframe=tf.code
                )

            # 更新当前K线
            self.current_candles[key].update(price, volume, amount)

        return completed_candles

    async def consume_from_redis(self, stream_pattern: str = "ticks:*") -> None:
        """从Redis Stream消费数据"""
        # 获取所有匹配的stream
        streams = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=stream_pattern, count=100)
            streams.extend(keys)
            if cursor == 0:
                break

        if not streams:
            logger.warning(f"No streams found matching pattern: {stream_pattern}")
            return

        logger.info(f"Found {len(streams)} streams to consume")

        # 创建消费组
        for stream in streams:
            try:
                await self.redis.xgroup_create(stream, self.consumer_group, id='0', mkstream=True)
            except aioredis.ResponseError as e:
                if "already exists" not in str(e):
                    raise

        # 消费循环
        while True:
            try:
                # 从多个stream读取
                streams_dict = {s: '>' for s in streams}
                messages = await self.redis.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams=streams_dict,
                    count=100,
                    block=1000
                )

                if not messages:
                    continue

                for stream_name, msgs in messages:
                    for msg_id, fields in msgs:
                        await self.process_message(stream_name, msg_id, fields)

            except Exception as e:
                logger.error(f"Error consuming from Redis: {e}")
                await asyncio.sleep(1)

    async def process_message(
        self,
        stream: bytes,
        msg_id: bytes,
        fields: Dict[bytes, bytes]
    ) -> None:
        """处理单条消息"""
        try:
            # 解析消息
            symbol = stream.decode().split(':')[-1]
            exchange = stream.decode().split(':')[1]

            data = {k.decode(): v.decode() for k, v in fields.items()}

            ts = datetime.fromisoformat(data['ts'])
            price = Decimal(data['price'])
            volume = int(data['volume'])
            amount = Decimal(data.get('amount', 0))

            # 聚合K线
            completed = self.process_tick(symbol, exchange, ts, price, volume, amount)

            if completed:
                self.pending_candles.extend(completed)
                logger.debug(f"Completed {len(completed)} candles for {symbol}")

            # 确认消息
            await self.redis.xack(stream, self.consumer_group, msg_id)

        except Exception as e:
            logger.error(f"Error processing message: {e}, fields: {fields}")

    async def flush_task(self) -> None:
        """定期刷新缓冲"""
        while True:
            await asyncio.sleep(self.flush_interval)

            if self.pending_candles:
                await self.flush_to_database()

    async def flush_to_database(self) -> None:
        """将缓冲写入数据库"""
        if not self.pending_candles:
            return

        # 复制并清空缓冲
        candles_to_flush = self.pending_candles.copy()
        self.pending_candles.clear()

        # 按表分组
        table_candles: Dict[str, List[Candle]] = defaultdict(list)
        for candle in candles_to_flush:
            table_name = f"candle_{candle.timeframe.replace('m', 'min').replace('h', 'hour').replace('d', 'day')}"
            table_candles[table_name].append(candle)

        # 批量写入
        for table_name, candles in table_candles.items():
            try:
                records = [c.to_tuple() for c in candles]

                async with self.db_pool.acquire() as conn:
                    # 使用INSERT ON CONFLICT实现upsert
                    await conn.executemany(
                        f"""
                        INSERT INTO {table_name}
                        (bucket, exchange, symbol, open, high, low, close, volume, amount, trades)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        ON CONFLICT (bucket, exchange, symbol)
                        DO UPDATE SET
                            high = GREATEST(EXCLUDED.high, {table_name}.high),
                            low = LEAST(EXCLUDED.low, {table_name}.low),
                            close = EXCLUDED.close,
                            volume = {table_name}.volume + EXCLUDED.volume,
                            amount = {table_name}.amount + EXCLUDED.amount,
                            trades = {table_name}.trades + EXCLUDED.trades
                        """,
                        records
                    )

                logger.info(f"Flushed {len(records)} candles to {table_name}")

            except Exception as e:
                logger.error(f"Error flushing to {table_name}: {e}")
                # 失败时重新放回缓冲
                self.pending_candles.extend(candles)

    async def close_all_candles(self) -> None:
        """关闭所有当前K线 (用于程序退出时)"""
        for candle in self.current_candles.values():
            self.pending_candles.append(candle)
        self.current_candles.clear()
        await self.flush_to_database()


class GapDetector:
    """缺失K线检测器"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def detect_gaps(
        self,
        symbol: str,
        exchange: str,
        timeframe: TimeFrame,
        start: datetime,
        end: datetime
    ) -> List[datetime]:
        """检测缺失的K线"""
        table_name = f"candle_{timeframe.code.replace('m', 'min').replace('h', 'hour').replace('d', 'day')}"

        async with self.db_pool.acquire() as conn:
            # 使用TimescaleDB的时间桶函数
            rows = await conn.fetch(
                f"""
                WITH expected_buckets AS (
                    SELECT generate_series(
                        time_bucket($1::interval, $2::timestamptz),
                        time_bucket($1::interval, $3::timestamptz),
                        $1::interval
                    ) AS bucket
                )
                SELECT e.bucket
                FROM expected_buckets e
                LEFT JOIN {table_name} c ON e.bucket = c.bucket
                    AND c.symbol = $4 AND c.exchange = $5
                WHERE c.bucket IS NULL
                ORDER BY e.bucket
                """,
                f"{timeframe.seconds} seconds",
                start,
                end,
                symbol,
                exchange
            )

        return [row['bucket'] for row in rows]

    async def fill_gap(
        self,
        symbol: str,
        exchange: str,
        bucket: datetime,
        timeframe: TimeFrame
    ) -> Optional[Candle]:
        """从Tick数据填充缺失的K线"""
        end_time = bucket + timedelta(seconds=timeframe.seconds)

        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    first(price, ts) as open,
                    max(price) as high,
                    min(price) as low,
                    last(price, ts) as close,
                    sum(volume) as volume,
                    sum(amount) as amount,
                    count(*) as trades
                FROM tick_data
                WHERE symbol = $1
                  AND exchange = $2
                  AND ts >= $3
                  AND ts < $4
                """,
                symbol,
                exchange,
                bucket,
                end_time
            )

        if row and row['open']:
            return Candle(
                bucket=bucket,
                exchange=exchange,
                symbol=symbol,
                timeframe=timeframe.code,
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume'],
                amount=row['amount'],
                trades=row['trades']
            )
        return None


# ==================== 使用示例 ====================

async def main():
    """主函数示例"""
    # 初始化连接
    redis = aioredis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    db_pool = await asyncpg.create_pool(
        host='localhost',
        port=5432,
        user='quant',
        password='quant123',
        database='trading'
    )

    # 创建聚合器
    aggregator = CandleAggregator(
        redis=redis,
        db_pool=db_pool,
        timeframes=[TimeFrame.MINUTE_1, TimeFrame.MINUTE_5, TimeFrame.HOUR_1],
        flush_interval=5
    )

    # 启动任务
    await asyncio.gather(
        aggregator.consume_from_redis(),
        aggregator.flush_task()
    )


if __name__ == '__main__':
    asyncio.run(main())
```

### 4.3 订单簿重建算法

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单簿重建算法 (Order Book Reconstruction)

功能:
- 从增量更新重建完整订单簿
- 支持L2/L3级别深度
- 实现高效的内存数据结构
- 计算订单簿衍生指标

算法:
- 使用SortedDict维护价格排序
- 增量更新避免全量重建
- 快照+增量模式保证一致性
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Set
from sortedcontainers import SortedDict
import logging

logger = logging.getLogger(__name__)


@dataclass
class OrderLevel:
    """订单簿档位"""
    price: Decimal
    size: int = 0
    orders: int = 0  # 委托笔数 (L3)
    order_ids: Set[str] = field(default_factory=set)  # L3使用

    def update(self, delta_size: int, delta_orders: int = 0) -> None:
        """更新档位"""
        self.size += delta_size
        self.orders += delta_orders
        if self.size <= 0:
            self.size = 0
            self.orders = 0

    def is_empty(self) -> bool:
        return self.size <= 0


@dataclass
class OrderBookSnapshot:
    """订单簿快照"""
    ts: float  # 纳秒级时间戳
    symbol: str
    bids: SortedDict  # price -> OrderLevel (降序)
    asks: SortedDict  # price -> OrderLevel (升序)

    def __post_init__(self):
        if not isinstance(self.bids, SortedDict):
            self.bids = SortedDict(lambda x: -x)  # 降序
        if not isinstance(self.asks, SortedDict):
            self.asks = SortedDict()  # 升序

    def best_bid(self) -> Optional[Tuple[Decimal, OrderLevel]]:
        """最优买价"""
        if self.bids:
            price = self.bids.keys()[0]
            return price, self.bids[price]
        return None

    def best_ask(self) -> Optional[Tuple[Decimal, OrderLevel]]:
        """最优卖价"""
        if self.asks:
            price = self.asks.keys()[0]
            return price, self.asks[price]
        return None

    def spread(self) -> Optional[Decimal]:
        """买卖价差"""
        best_bid = self.best_bid()
        best_ask = self.best_ask()
        if best_bid and best_ask:
            return best_ask[0] - best_bid[0]
        return None

    def mid_price(self) -> Optional[Decimal]:
        """中间价"""
        best_bid = self.best_bid()
        best_ask = self.best_ask()
        if best_bid and best_ask:
            return (best_bid[0] + best_ask[0]) / 2
        return None

    def depth(self, side: str, levels: int = 5) -> List[Tuple[Decimal, int]]:
        """获取指定深度的订单簿"""
        result = []
        data = self.bids if side == 'B' else self.asks
        for i, (price, level) in enumerate(data.items()):
            if i >= levels:
                break
            result.append((price, level.size))
        return result

    def total_size(self, side: str) -> int:
        """总挂单量"""
        data = self.bids if side == 'B' else self.asks
        return sum(level.size for level in data.values())

    def imbalance(self) -> Optional[Decimal]:
        """买卖失衡度"""
        bid_size = self.total_size('B')
        ask_size = self.total_size('A')
        total = bid_size + ask_size
        if total > 0:
            return Decimal(bid_size - ask_size) / Decimal(total)
        return None

    def weighted_price(self, side: str, quantity: int) -> Optional[Decimal]:
        """获取执行指定数量的加权平均价格"""
        data = self.bids if side == 'B' else self.asks
        remaining = quantity
        total_cost = Decimal('0')

        for price, level in data.items():
            if remaining <= 0:
                break
            take = min(remaining, level.size)
            total_cost += price * take
            remaining -= take

        if remaining > 0:
            return None  # 深度不足
        return total_cost / quantity


class OrderBookReconstructor:
    """订单簿重建器"""

    def __init__(self, symbol: str, max_depth: int = 20):
        self.symbol = symbol
        self.max_depth = max_depth

        # 当前订单簿状态
        self.current_book: Optional[OrderBookSnapshot] = None
        self.last_update_ts = 0

        # 增量缓存 (用于从快照重建)
        self.delta_buffer: List[Dict] = []
        self.max_buffer_size = 10000

        # 统计
        self.update_count = 0
        self.snapshot_count = 0

    def apply_snapshot(self, ts: float, bids: List[Tuple[Decimal, int]], asks: List[Tuple[Decimal, int]]) -> None:
        """应用完整快照"""
        book = OrderBookSnapshot(ts=ts, symbol=self.symbol, bids=SortedDict(lambda x: -x), asks=SortedDict())

        for price, size in bids[:self.max_depth]:
            book.bids[price] = OrderLevel(price, size)

        for price, size in asks[:self.max_depth]:
            book.asks[price] = OrderLevel(price, size)

        self.current_book = book
        self.last_update_ts = ts
        self.snapshot_count += 1

        # 清空增量缓存
        self.delta_buffer.clear()

        logger.debug(f"[{self.symbol}] Applied snapshot at ts={ts}")

    def apply_delta(
        self,
        ts: float,
        side: str,
        price: Decimal,
        delta_size: int,
        new_size: Optional[int] = None,
        order_id: Optional[str] = None
    ) -> None:
        """应用增量更新"""
        if self.current_book is None:
            # 缓存增量，等待快照
            self.delta_buffer.append({
                'ts': ts,
                'side': side,
                'price': price,
                'delta_size': delta_size,
                'new_size': new_size,
                'order_id': order_id
            })

            if len(self.delta_buffer) > self.max_buffer_size:
                self.delta_buffer.pop(0)
            return

        # 选择对应的订单簿
        book_side = self.current_book.bids if side == 'B' else self.current_book.asks

        # 更新或删除档位
        if price in book_side:
            level = book_side[price]

            if new_size is not None:
                # 绝对更新
                level.size = new_size
            else:
                # 相对更新
                level.update(delta_size)

            # L3: 更新委托ID
            if order_id:
                if delta_size > 0:
                    level.order_ids.add(order_id)
                else:
                    level.order_ids.discard(order_id)

            # 清理空档位
            if level.is_empty():
                del book_side[price]
        else:
            # 新增档位
            if (new_size is not None and new_size > 0) or delta_size > 0:
                size = new_size if new_size is not None else delta_size
                level = OrderLevel(price, size)
                if order_id:
                    level.order_ids.add(order_id)
                    level.orders = 1
                book_side[price] = level

        # 限制深度
        while len(book_side) > self.max_depth:
            book_side.popitem()

        self.current_book.ts = ts
        self.last_update_ts = ts
        self.update_count += 1

    def apply_deltas_from_buffer(self) -> None:
        """从缓存应用增量更新 (收到快照后调用)"""
        if not self.current_book or not self.delta_buffer:
            return

        for delta in self.delta_buffer:
            if delta['ts'] > self.current_book.ts:
                self.apply_delta(
                    ts=delta['ts'],
                    side=delta['side'],
                    price=delta['price'],
                    delta_size=delta['delta_size'],
                    new_size=delta['new_size'],
                    order_id=delta.get('order_id')
                )

        self.delta_buffer.clear()
        logger.info(f"[{self.symbol}] Applied {len(self.delta_buffer)} buffered deltas")

    def get_book(self) -> Optional[OrderBookSnapshot]:
        """获取当前订单簿"""
        return self.current_book

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'symbol': self.symbol,
            'update_count': self.update_count,
            'snapshot_count': self.snapshot_count,
            'last_update_ts': self.last_update_ts,
            'buffered_deltas': len(self.delta_buffer),
            'bid_levels': len(self.current_book.bids) if self.current_book else 0,
            'ask_levels': len(self.current_book.asks) if self.current_book else 0
        }


class MultiSymbolOrderBookManager:
    """多品种订单簿管理器"""

    def __init__(self, max_depth: int = 20):
        self.max_depth = max_depth
        self.books: Dict[str, OrderBookReconstructor] = {}

    def get_book(self, symbol: str) -> OrderBookReconstructor:
        """获取或创建订单簿重建器"""
        if symbol not in self.books:
            self.books[symbol] = OrderBookReconstructor(symbol, self.max_depth)
        return self.books[symbol]

    def remove_book(self, symbol: str) -> None:
        """删除订单簿"""
        if symbol in self.books:
            del self.books[symbol]

    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有订单簿统计"""
        return {symbol: book.get_stats() for symbol, book in self.books.items()}


# ==================== 使用示例 ====================

def example():
    """使用示例"""
    # 创建重建器
    recon = OrderBookReconstructor("AAPL", max_depth=10)

    # 应用初始快照
    recon.apply_snapshot(
        ts=1000.0,
        bids=[
            (Decimal("150.00"), 100),
            (Decimal("149.99"), 200),
            (Decimal("149.98"), 150),
        ],
        asks=[
            (Decimal("150.01"), 50),
            (Decimal("150.02"), 100),
            (Decimal("150.03"), 200),
        ]
    )

    # 应用增量更新
    recon.apply_delta(ts=1001.0, side='B', price=Decimal("150.00"), delta_size=50)
    recon.apply_delta(ts=1002.0, side='A', price=Decimal("150.01"), delta_size=-20)
    recon.apply_delta(ts=1003.0, side='B', price=Decimal("150.05"), delta_size=300)  # 新增档位

    # 获取当前订单簿
    book = recon.get_book()

    print(f"Best Bid: {book.best_bid()}")
    print(f"Best Ask: {book.best_ask()}")
    print(f"Spread: {book.spread()}")
    print(f"Mid Price: {book.mid_price()}")
    print(f"Imbalance: {book.imbalance()}")

    # 获取5档深度
    print(f"\nBid Depth: {book.depth('B', 5)}")
    print(f"Ask Depth: {book.depth('A', 5)}")

    # 计算执行价格
    exec_price = book.weighted_price('B', quantity=120)
    print(f"\nExecution price for 120 shares: {exec_price}")


if __name__ == '__main__':
    example()
```

### 4.4 技术指标计算

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块 (Technical Indicators)

支持指标:
- 移动平均线: SMA, EMA, WMA, VWMA
- 趋势指标: MACD, ADX, ATR
- 动量指标: RSI, Stochastic, CCI
- 波动率指标: Bollinger Bands, Keltner Channels
- 成交量指标: OBV, MFI, VWAP

特性:
- 向量化计算 (NumPy/Pandas)
- 增量更新支持 (流式计算)
- 高效的循环队列实现
"""

import numpy as np
import pandas as pd
from collections import deque
from decimal import Decimal
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class OHLCV:
    """K线数据结构"""
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: Optional[int] = None


class Indicator(ABC):
    """技术指标基类"""

    def __init__(self, period: int):
        self.period = period
        self.values: deque = deque(maxlen=period * 2)
        self.result: Optional[float] = None

    @abstractmethod
    def update(self, data: OHLCV) -> Optional[float]:
        """更新指标值"""
        pass

    @abstractmethod
    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算"""
        pass


class SMA(Indicator):
    """简单移动平均线 (Simple Moving Average)"""

    def __init__(self, period: int = 20):
        super().__init__(period)
        self.window: deque = deque(maxlen=period)
        self.sum = 0.0

    def update(self, data: OHLCV) -> Optional[float]:
        """增量更新SMA"""
        value = data.close

        if len(self.window) == self.period:
            self.sum -= self.window[0]

        self.window.append(value)
        self.sum += value

        if len(self.window) == self.period:
            self.result = self.sum / self.period
            return self.result
        return None

    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算SMA"""
        closes = [d.close for d in data]
        return pd.Series(closes).rolling(window=self.period).mean().tolist()


class EMA(Indicator):
    """指数移动平均线 (Exponential Moving Average)"""

    def __init__(self, period: int = 20):
        super().__init__(period)
        self.multiplier = 2.0 / (period + 1)
        self.ema = None

    def update(self, data: OHLCV) -> Optional[float]:
        """增量更新EMA"""
        value = data.close

        if self.ema is None:
            # 初始化使用SMA
            self.values.append(value)
            if len(self.values) >= self.period:
                self.ema = sum(self.values) / len(self.values)
        else:
            self.ema = (value - self.ema) * self.multiplier + self.ema

        self.result = self.ema
        return self.ema

    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算EMA"""
        closes = pd.Series([d.close for d in data])
        return closes.ewm(span=self.period, adjust=False).mean().tolist()


class RSI(Indicator):
    """相对强弱指标 (Relative Strength Index)"""

    def __init__(self, period: int = 14):
        super().__init__(period)
        self.prev_close = None
        self.gains: deque = deque(maxlen=period)
        self.losses: deque = deque(maxlen=period)
        self.avg_gain = 0.0
        self.avg_loss = 0.0

    def update(self, data: OHLCV) -> Optional[float]:
        """增量更新RSI"""
        if self.prev_close is None:
            self.prev_close = data.close
            return None

        change = data.close - self.prev_close
        gain = max(change, 0)
        loss = abs(min(change, 0))

        self.prev_close = data.close

        if len(self.gains) < self.period:
            self.gains.append(gain)
            self.losses.append(loss)

            if len(self.gains) == self.period:
                self.avg_gain = sum(self.gains) / self.period
                self.avg_loss = sum(self.losses) / self.period
        else:
            # Wilder's smoothing
            self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
            self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period

        if self.avg_loss == 0:
            self.result = 100.0
            return 100.0

        rs = self.avg_gain / self.avg_loss
        self.result = 100.0 - (100.0 / (1.0 + rs))
        return self.result

    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算RSI"""
        closes = pd.Series([d.close for d in data])
        delta = closes.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        return (100 - (100 / (1 + rs))).tolist()


class MACD:
    """MACD指标"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast_ema = EMA(fast)
        self.slow_ema = EMA(slow)
        self.signal_ema = EMA(signal)
        self.macd_line = None
        self.signal_line = None
        self.histogram = None

    def update(self, data: OHLCV) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """更新MACD"""
        fast_val = self.fast_ema.update(data)
        slow_val = self.slow_ema.update(data)

        if fast_val is None or slow_val is None:
            return None, None, None

        self.macd_line = fast_val - slow_val

        # 使用MACD线作为信号线的输入
        signal_data = OHLCV(self.macd_line, self.macd_line, self.macd_line, self.macd_line, 0)
        self.signal_line = self.signal_ema.update(signal_data)

        if self.signal_line is not None:
            self.histogram = self.macd_line - self.signal_line

        return self.macd_line, self.signal_line, self.histogram

    def calculate(self, data: List[OHLCV]) -> pd.DataFrame:
        """批量计算MACD"""
        closes = pd.Series([d.close for d in data])
        ema_fast = closes.ewm(span=self.fast_ema.period).mean()
        ema_slow = closes.ewm(span=self.slow_ema.period).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=self.signal_ema.period).mean()
        histogram = macd - signal

        return pd.DataFrame({
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        })


class BollingerBands:
    """布林带 (Bollinger Bands)"""

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.sma = SMA(period)
        self.window: deque = deque(maxlen=period)

    def update(self, data: OHLCV) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """更新布林带"""
        middle = self.sma.update(data)
        self.window.append(data.close)

        if middle is None:
            return None, None, None

        std = np.std(list(self.window))
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std

        return upper, middle, lower

    def calculate(self, data: List[OHLCV]) -> pd.DataFrame:
        """批量计算布林带"""
        closes = pd.Series([d.close for d in data])
        middle = closes.rolling(window=self.period).mean()
        std = closes.rolling(window=self.period).std()
        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std

        return pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })


class ATR(Indicator):
    """真实波动幅度均值 (Average True Range)"""

    def __init__(self, period: int = 14):
        super().__init__(period)
        self.prev_close = None
        self.true_ranges: deque = deque(maxlen=period)

    def update(self, data: OHLCV) -> Optional[float]:
        """更新ATR"""
        high = data.high
        low = data.low
        close = data.close

        if self.prev_close is None:
            self.prev_close = close
            tr = high - low
        else:
            tr1 = high - low
            tr2 = abs(high - self.prev_close)
            tr3 = abs(low - self.prev_close)
            tr = max(tr1, tr2, tr3)

        self.prev_close = close
        self.true_ranges.append(tr)

        if len(self.true_ranges) == self.period:
            self.result = sum(self.true_ranges) / self.period
            return self.result
        return None

    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算ATR"""
        df = pd.DataFrame([{'high': d.high, 'low': d.low, 'close': d.close} for d in data])
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        return df['tr'].rolling(window=self.period).mean().tolist()


class VWAP:
    """成交量加权平均价 (Volume Weighted Average Price)"""

    def __init__(self):
        self.cum_typical_volume = 0.0
        self.cum_volume = 0.0
        self.daily_reset = True
        self.prev_date = None

    def update(self, data: OHLCV) -> float:
        """更新VWAP"""
        typical_price = (data.high + data.low + data.close) / 3

        self.cum_typical_volume += typical_price * data.volume
        self.cum_volume += data.volume

        self.result = self.cum_typical_volume / self.cum_volume if self.cum_volume > 0 else typical_price
        return self.result

    def reset(self):
        """重置VWAP计算 (每日开盘时)"""
        self.cum_typical_volume = 0.0
        self.cum_volume = 0.0

    def calculate(self, data: List[OHLCV]) -> List[float]:
        """批量计算VWAP"""
        df = pd.DataFrame([{
            'high': d.high, 'low': d.low, 'close': d.close, 'volume': d.volume
        } for d in data])
        df['typical'] = (df['high'] + df['low'] + df['close']) / 3
        df['cum_vol'] = df['volume'].cumsum()
        df['cum_typical_vol'] = (df['typical'] * df['volume']).cumsum()
        return (df['cum_typical_vol'] / df['cum_vol']).tolist()


class TechnicalIndicatorEngine:
    """技术指标引擎 - 管理多个指标的并行计算"""

    def __init__(self):
        self.indicators: Dict[str, Indicator] = {}

    def register(self, name: str, indicator: Indicator) -> 'TechnicalIndicatorEngine':
        """注册指标"""
        self.indicators[name] = indicator
        return self

    def update(self, data: OHLCV) -> Dict[str, float]:
        """更新所有指标"""
        results = {}
        for name, indicator in self.indicators.items():
            result = indicator.update(data)
            if result is not None:
                results[name] = result
        return results

    def get(self, name: str) -> Optional[float]:
        """获取指定指标值"""
        indicator = self.indicators.get(name)
        return indicator.result if indicator else None


# ==================== 使用示例 ====================

def example():
    """使用示例"""
    # 模拟K线数据
    data = [
        OHLCV(100, 105, 98, 102, 1000),
        OHLCV(102, 106, 101, 104, 1200),
        OHLCV(104, 108, 103, 107, 800),
        OHLCV(107, 110, 106, 109, 1500),
        OHLCV(109, 112, 108, 111, 2000),
        # ... 更多数据
    ]

    # 创建指标
    sma = SMA(period=5)
    ema = EMA(period=5)
    rsi = RSI(period=5)
    macd = MACD(fast=3, slow=5, signal=3)
    bb = BollingerBands(period=5)

    # 增量计算
    print("Incremental Calculation:")
    for i, bar in enumerate(data):
        sma_val = sma.update(bar)
        ema_val = ema.update(bar)
        rsi_val = rsi.update(bar)
        macd_vals = macd.update(bar)
        bb_vals = bb.update(bar)

        print(f"Bar {i+1}: Close={bar.close:.2f}, SMA={sma_val}, EMA={ema_val:.2f}, RSI={rsi_val}")

    # 批量计算
    print("\nBatch Calculation:")
    sma_vals = sma.calculate(data)
    ema_vals = ema.calculate(data)
    rsi_vals = rsi.calculate(data)
    macd_df = macd.calculate(data)
    bb_df = bb.calculate(data)

    print(f"SMA: {sma_vals}")
    print(f"EMA: {[f'{v:.2f}' if v else None for v in ema_vals]}")
    print(f"RSI: {[f'{v:.2f}' if v else None for v in rsi_vals]}")


if __name__ == '__main__':
    example()
```

### 4.5 策略回测框架

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略回测框架 (Strategy Backtesting Framework)

功能:
- 基于事件驱动的回测引擎
- 支持多种订单类型: 市价单、限价单、止损单
- 滑点和手续费模拟
- 绩效评估和风险指标计算
- 向量化回测加速

架构:
- Event-driven引擎
- DataHandler抽象接口
- Strategy基类
- Portfolio管理
- Execution模拟
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple
from collections import defaultdict
import pandas as pd
import numpy as np


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"           # 市价单
    LIMIT = "limit"             # 限价单
    STOP = "stop"               # 止损单
    STOP_LIMIT = "stop_limit"   # 限价止损单


class OrderSide(Enum):
    """买卖方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """订单"""
    order_id: str
    timestamp: datetime
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[Decimal] = None       # 限价单价格
    stop_price: Optional[Decimal] = None  # 止损单触发价
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    filled_price: Optional[Decimal] = None
    commission: Decimal = Decimal('0')
    slippage: Decimal = Decimal('0')


@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: int = 0
    avg_price: Decimal = Decimal('0')

    @property
    def market_value(self, current_price: Decimal) -> Decimal:
        return Decimal(self.quantity) * current_price

    @property
    def unrealized_pnl(self, current_price: Decimal) -> Decimal:
        return Decimal(self.quantity) * (current_price - self.avg_price)


@dataclass
class Fill:
    """成交记录"""
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: int
    price: Decimal
    commission: Decimal
    slippage: Decimal


@dataclass
class MarketEvent:
    """市场事件"""
    timestamp: datetime
    symbol: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class Signal:
    """交易信号"""
    timestamp: datetime
    symbol: str
    signal_type: str  # LONG, SHORT, EXIT_LONG, EXIT_SHORT
    strength: float = 1.0
    metadata: Dict = field(default_factory=dict)


class DataHandler(ABC):
    """数据处理器基类"""

    @abstractmethod
    def get_latest_bar(self, symbol: str) -> MarketEvent:
        """获取最新K线"""
        pass

    @abstractmethod
    def get_latest_bars(self, symbol: str, n: int = 1) -> List[MarketEvent]:
        """获取最近N根K线"""
        pass

    @abstractmethod
    def update_bars(self) -> bool:
        """更新K线，返回是否还有数据"""
        pass


class HistoricDataHandler(DataHandler):
    """历史数据处理器"""

    def __init__(self, data: Dict[str, pd.DataFrame]):
        """
        data: {symbol: DataFrame with columns [open, high, low, close, volume]}
        """
        self.data = data
        self.symbols = list(data.keys())
        self.current_idx = 0
        self.latest_data: Dict[str, MarketEvent] = {}

        # 对齐所有品种的时间索引
        self._align_data()

    def _align_data(self):
        """对齐多品种数据的时间索引"""
        # 获取所有时间索引的并集
        all_dates = None
        for df in self.data.values():
            if all_dates is None:
                all_dates = df.index
            else:
                all_dates = all_dates.union(df.index)

        # 重新索引并填充
        for symbol in self.symbols:
            self.data[symbol] = self.data[symbol].reindex(all_dates, method='ffill')

        self.date_index = all_dates

    def get_latest_bar(self, symbol: str) -> MarketEvent:
        return self.latest_data.get(symbol)

    def get_latest_bars(self, symbol: str, n: int = 1) -> List[MarketEvent]:
        if symbol not in self.data:
            return []

        start_idx = max(0, self.current_idx - n)
        df = self.data[symbol].iloc[start_idx:self.current_idx]

        events = []
        for ts, row in df.iterrows():
            events.append(MarketEvent(
                timestamp=ts,
                symbol=symbol,
                open=Decimal(str(row['open'])),
                high=Decimal(str(row['high'])),
                low=Decimal(str(row['low'])),
                close=Decimal(str(row['close'])),
                volume=int(row['volume'])
            ))
        return events

    def update_bars(self) -> bool:
        if self.current_idx >= len(self.date_index):
            return False

        current_date = self.date_index[self.current_idx]

        for symbol in self.symbols:
            row = self.data[symbol].loc[current_date]
            self.latest_data[symbol] = MarketEvent(
                timestamp=current_date,
                symbol=symbol,
                open=Decimal(str(row['open'])),
                high=Decimal(str(row['high'])),
                low=Decimal(str(row['low'])),
                close=Decimal(str(row['close'])),
                volume=int(row['volume'])
            )

        self.current_idx += 1
        return True


class Strategy(ABC):
    """策略基类"""

    def __init__(self, data_handler: DataHandler):
        self.data_handler = data_handler
        self.signals: List[Signal] = []

    @abstractmethod
    def generate_signals(self, event: MarketEvent) -> List[Signal]:
        """生成交易信号"""
        pass


class MovingAverageCrossStrategy(Strategy):
    """双均线交叉策略"""

    def __init__(self, data_handler: DataHandler, short_window: int = 10, long_window: int = 30):
        super().__init__(data_handler)
        self.short_window = short_window
        self.long_window = long_window
        self.bought = defaultdict(lambda: False)

    def generate_signals(self, event: MarketEvent) -> List[Signal]:
        signals = []
        symbol = event.symbol

        # 获取历史数据计算均线
        bars = self.data_handler.get_latest_bars(symbol, self.long_window)
        if len(bars) < self.long_window:
            return signals

        closes = [bar.close for bar in bars]
        short_sma = sum(closes[-self.short_window:]) / self.short_window
        long_sma = sum(closes) / self.long_window

        # 生成信号
        if short_sma > long_sma and not self.bought[symbol]:
            signals.append(Signal(
                timestamp=event.timestamp,
                symbol=symbol,
                signal_type='LONG',
                strength=1.0
            ))
            self.bought[symbol] = True
        elif short_sma < long_sma and self.bought[symbol]:
            signals.append(Signal(
                timestamp=event.timestamp,
                symbol=symbol,
                signal_type='EXIT_LONG',
                strength=1.0
            ))
            self.bought[symbol] = False

        return signals


class Portfolio:
    """投资组合管理"""

    def __init__(
        self,
        data_handler: DataHandler,
        initial_capital: Decimal = Decimal('100000'),
        commission_rate: Decimal = Decimal('0.001'),
        slippage_model: str = 'fixed',
        slippage_value: Decimal = Decimal('0.01')
    ):
        self.data_handler = data_handler
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.slippage_model = slippage_model
        self.slippage_value = slippage_value

        self.positions: Dict[str, Position] = defaultdict(lambda: Position(""))
        self.orders: List[Order] = []
        self.fills: List[Fill] = []
        self.equity_curve: List[Tuple[datetime, Decimal]] = []

    def update_signal(self, signal: Signal) -> None:
        """处理信号，生成订单"""
        if signal.signal_type == 'LONG':
            self._place_order(signal.symbol, OrderSide.BUY, signal)
        elif signal.signal_type == 'EXIT_LONG':
            position = self.positions[signal.symbol]
            if position.quantity > 0:
                self._place_order(signal.symbol, OrderSide.SELL, signal, position.quantity)

    def _place_order(
        self,
        symbol: str,
        side: OrderSide,
        signal: Signal,
        quantity: Optional[int] = None
    ) -> None:
        """下单"""
        bar = self.data_handler.get_latest_bar(symbol)
        if not bar:
            return

        # 默认使用所有资金
        if quantity is None:
            current_price = bar.close
            quantity = int(self.cash / current_price * Decimal('0.95'))  # 留5%缓冲

        if quantity <= 0:
            return

        order = Order(
            order_id=f"{signal.timestamp.timestamp()}_{symbol}",
            timestamp=signal.timestamp,
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity
        )

        self.orders.append(order)
        self._execute_order(order, bar)

    def _execute_order(self, order: Order, bar: MarketEvent) -> None:
        """执行订单"""
        # 计算成交价格 (加入滑点)
        if self.slippage_model == 'fixed':
            if order.side == OrderSide.BUY:
                fill_price = bar.close + self.slippage_value
            else:
                fill_price = bar.close - self.slippage_value
        else:  # percentage
            slip_pct = self.slippage_value
            if order.side == OrderSide.BUY:
                fill_price = bar.close * (1 + slip_pct)
            else:
                fill_price = bar.close * (1 - slip_pct)

        # 计算手续费
        fill_value = fill_price * order.quantity
        commission = fill_value * self.commission_rate

        # 更新持仓
        position = self.positions[order.symbol]

        if order.side == OrderSide.BUY:
            # 买入
            total_cost = position.avg_price * position.quantity + fill_price * order.quantity
            position.quantity += order.quantity
            if position.quantity > 0:
                position.avg_price = total_cost / position.quantity
            self.cash -= fill_value + commission
        else:
            # 卖出
            position.quantity -= order.quantity
            self.cash += fill_value - commission

        # 记录成交
        fill = Fill(
            timestamp=order.timestamp,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=fill_price,
            commission=commission,
            slippage=abs(fill_price - bar.close) * order.quantity
        )
        self.fills.append(fill)

        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.filled_price = fill_price
        order.commission = commission
        order.slippage = fill.slippage

    def update_timeindex(self, timestamp: datetime) -> None:
        """更新权益曲线"""
        total_equity = self.cash

        for symbol, position in self.positions.items():
            bar = self.data_handler.get_latest_bar(symbol)
            if bar and position.quantity != 0:
                total_equity += position.unrealized_pnl(bar.close)

        self.equity_curve.append((timestamp, total_equity))


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        data_handler: DataHandler,
        strategy: Strategy,
        portfolio: Portfolio
    ):
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio

    def run(self) -> pd.DataFrame:
        """运行回测"""
        print("Starting backtest...")

        while self.data_handler.update_bars():
            # 获取当前时间
            latest_bar = list(self.data_handler.latest_data.values())[0]
            timestamp = latest_bar.timestamp

            # 策略生成信号
            for symbol in self.data_handler.symbols:
                bar = self.data_handler.get_latest_bar(symbol)
                if bar:
                    signals = self.strategy.generate_signals(bar)
                    for signal in signals:
                        self.portfolio.update_signal(signal)

            # 更新权益曲线
            self.portfolio.update_timeindex(timestamp)

        print("Backtest completed.")
        return self._generate_performance()

    def _generate_performance(self) -> pd.DataFrame:
        """生成绩效报告"""
        equity_df = pd.DataFrame(
            self.portfolio.equity_curve,
            columns=['timestamp', 'equity']
        )
        equity_df.set_index('timestamp', inplace=True)

        # 计算收益率
        equity_df['returns'] = equity_df['equity'].pct_change()
        equity_df['cum_returns'] = (1 + equity_df['returns']).cumprod()

        return equity_df

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计指标"""
        equity_df = self._generate_performance()
        returns = equity_df['returns'].dropna()

        # 计算各项指标
        total_return = (equity_df['equity'].iloc[-1] / self.portfolio.initial_capital - 1) * 100

        # 年化收益率
        num_years = len(equity_df) / 252  # 假设日数据
        annual_return = ((1 + total_return/100) ** (1/num_years) - 1) * 100 if num_years > 0 else 0

        # 波动率
        volatility = returns.std() * np.sqrt(252) * 100

        # 夏普比率 (假设无风险利率2%)
        risk_free_rate = 0.02
        sharpe_ratio = ((annual_return/100 - risk_free_rate) / (volatility/100)) if volatility > 0 else 0

        # 最大回撤
        cummax = equity_df['equity'].cummax()
        drawdown = (equity_df['equity'] - cummax) / cummax
        max_drawdown = drawdown.min() * 100

        # 交易统计
        trades = self.portfolio.fills
        winning_trades = [t for t in trades if
            (t.side == OrderSide.SELL and t.price > self.portfolio.positions[t.symbol].avg_price) or
            (t.side == OrderSide.BUY and t.price < self.portfolio.positions[t.symbol].avg_price)]

        return {
            'initial_capital': float(self.portfolio.initial_capital),
            'final_equity': float(equity_df['equity'].iloc[-1]),
            'total_return_pct': total_return,
            'annual_return_pct': annual_return,
            'volatility_pct': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'win_rate': len(winning_trades) / len(trades) * 100 if trades else 0,
            'total_commission': sum(float(t.commission) for t in trades),
            'total_slippage': sum(float(t.slippage) for t in trades)
        }


# ==================== 使用示例 ====================

def example_backtest():
    """回测示例"""
    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')

    # 随机游走生成价格
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = 100 * (1 + returns).cumprod()

    df = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
        'high': prices * (1 + abs(np.random.normal(0, 0.01, len(dates)))),
        'low': prices * (1 - abs(np.random.normal(0, 0.01, len(dates)))),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)

    # 创建组件
    data_handler = HistoricDataHandler({'AAPL': df})
    strategy = MovingAverageCrossStrategy(data_handler, short_window=10, long_window=30)
    portfolio = Portfolio(
        data_handler,
        initial_capital=Decimal('100000'),
        commission_rate=Decimal('0.001'),
        slippage_model='fixed',
        slippage_value=Decimal('0.01')
    )

    # 运行回测
    engine = BacktestEngine(data_handler, strategy, portfolio)
    equity_curve = engine.run()

    # 输出结果
    stats = engine.get_statistics()
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    for key, value in stats.items():
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

    return equity_curve


if __name__ == '__main__':
    example_backtest()
```

---

## 五、性能优化

### 5.1 内存表配置

```sql
-- =====================================================
-- 内存表优化配置
-- 目标: 最小化写入延迟，最大化查询性能
-- =====================================================

-- -------------------------------------------------
-- 1. UNLOGGED表配置 (无WAL日志，写入速度提升10倍)
-- -------------------------------------------------

-- 创建UNLOGGED表用于热数据
-- 注意: 数据不持久化，重启后丢失，仅用于实时计算
CREATE UNLOGGED TABLE IF NOT EXISTS tick_data_hot (
    LIKE tick_data INCLUDING ALL
);

-- UNLOGGED表专用索引 (更轻量)
CREATE INDEX idx_tick_hot_symbol_ts ON tick_data_hot (symbol, ts DESC);

-- -------------------------------------------------
-- 2. 内存表分区策略
-- -------------------------------------------------

-- 按交易日分区，便于日终清理
CREATE OR REPLACE FUNCTION create_daily_hot_table(trade_date DATE)
RETURNS TEXT AS $$
DECLARE
    table_name TEXT;
BEGIN
    table_name := 'tick_data_hot_' || TO_CHAR(trade_date, 'YYYYMMDD');

    EXECUTE format('
        CREATE UNLOGGED TABLE IF NOT EXISTS %I (
            LIKE tick_data INCLUDING ALL
        )', table_name);

    EXECUTE format('
        CREATE INDEX IF NOT EXISTS idx_%s_symbol ON %I (symbol, ts DESC)',
            table_name, table_name);

    RETURN table_name;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------
-- 3. 内存表数据迁移函数 (日终归档)
-- -------------------------------------------------

CREATE OR REPLACE FUNCTION archive_hot_data(trade_date DATE)
RETURNS TABLE (
    archived_count BIGINT,
    duration_ms NUMERIC
) AS $$
DECLARE
    v_start_time TIMESTAMP;
    v_count BIGINT;
    v_source_table TEXT;
BEGIN
    v_start_time := clock_timestamp();
    v_source_table := 'tick_data_hot_' || TO_CHAR(trade_date, 'YYYYMMDD');

    -- 迁移数据到持久化表
    EXECUTE format('
        INSERT INTO tick_data
        SELECT * FROM %I
        ON CONFLICT (ts, exchange, symbol, bid_order_id, ask_order_id) DO NOTHING',
        v_source_table);

    GET DIAGNOSTICS v_count = ROW_COUNT;

    -- 删除内存表
    EXECUTE format('DROP TABLE IF EXISTS %I', v_source_table);

    RETURN QUERY SELECT
        v_count,
        EXTRACT(EPOCH FROM (clock_timestamp() - v_start_time)) * 1000;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------
-- 4. 表空间优化 (将热数据表放在SSD上)
-- -------------------------------------------------

-- 创建SSD表空间
-- CREATE TABLESPACE hot_data LOCATION '/mnt/nvme/postgres/hot';

-- 将热数据表移动到高速存储
-- ALTER TABLE tick_data_hot SET TABLESPACE hot_data;
```

### 5.2 分区策略

```sql
-- =====================================================
-- 分区策略优化
-- TimescaleDB自动分区 + 自定义分区管理
-- =====================================================

-- -------------------------------------------------
-- 1. Hypertable基础配置
-- -------------------------------------------------

-- 创建按月分区的Hypertable (适用于低频访问历史数据)
SELECT create_hypertable(
    'tick_data',
    'ts',
    chunk_time_interval => INTERVAL '1 month',
    if_not_exists => TRUE
);

-- 使用空间分区 (按交易所分区，提高查询效率)
SELECT add_dimension('tick_data', 'exchange', 4);

-- -------------------------------------------------
-- 2. 自适应分区策略
-- -------------------------------------------------

-- 根据数据密度动态调整分区大小
CREATE OR REPLACE FUNCTION optimize_chunk_size(
    p_table_name TEXT,
    target_chunk_rows BIGINT DEFAULT 1000000
)
RETURNS TABLE (
    chunk_name TEXT,
    row_count BIGINT,
    recommended_interval INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.chunk_name,
        (SELECT COUNT(*) FROM c.chunk_name::regclass) as row_count,
        CASE
            WHEN (SELECT COUNT(*) FROM c.chunk_name::regclass) > target_chunk_rows * 2 THEN
                -- 数据量过大，缩小分区
                c.range_end - c.range_start / 2
            WHEN (SELECT COUNT(*) FROM c.chunk_name::regclass) < target_chunk_rows / 2 THEN
                -- 数据量过小，扩大分区
                (c.range_end - c.range_start) * 2
            ELSE
                c.range_end - c.range_start
        END as recommended_interval
    FROM timescaledb_information.chunks c
    WHERE c.hypertable_name = p_table_name;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------
-- 3. 分区维护任务
-- -------------------------------------------------

-- 压缩旧分区
SELECT add_compression_policy('tick_data', INTERVAL '7 days');

-- 删除/归档极旧数据
SELECT add_retention_policy('tick_data', INTERVAL '2 years');

-- -------------------------------------------------
-- 4. 手动分区管理
-- -------------------------------------------------

-- 查看所有分区
SELECT
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(d.total_bytes) as size
FROM timescaledb_information.chunks c
JOIN (
    SELECT relid, pg_total_relation_size(relid) as total_bytes
    FROM pg_stat_user_tables
) d ON c.chunk_name = d.relid::regclass::text
WHERE hypertable_name = 'tick_data'
ORDER BY range_start;

-- 压缩指定分区
SELECT compress_chunk(i)
FROM show_chunks('tick_data', older_than => INTERVAL '1 month') i;

-- 解压缩分区 (需要查询历史数据时)
SELECT decompress_chunk(i)
FROM show_chunks('tick_data', older_than => INTERVAL '1 month') i;
```

### 5.3 连续聚合策略

```sql
-- =====================================================
-- 连续聚合优化 (Real-time Aggregation)
-- 预计算K线数据，减少实时查询负载
-- =====================================================

-- -------------------------------------------------
-- 1. 1分钟K线实时聚合
-- -------------------------------------------------

CREATE MATERIALIZED VIEW candle_1min_realtime
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', ts) AS bucket,
    exchange,
    symbol,
    first(price, ts) AS open,
    max(price) AS high,
    min(price) AS low,
    last(price, ts) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    count(*) AS trades,
    -- VWAP计算
    sum(price * volume) / NULLIF(sum(volume), 0) AS vwap,
    -- 主动买卖量
    sum(volume) FILTER (WHERE side = 'B') AS buy_volume,
    sum(volume) FILTER (WHERE side = 'S') AS sell_volume
FROM tick_data
GROUP BY bucket, exchange, symbol
WITH NO DATA;

-- 配置实时聚合策略
SELECT add_continuous_aggregate_policy('candle_1min_realtime',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 minute',
    schedule_interval => INTERVAL '1 minute',
    initial_start => NOW()
);

-- -------------------------------------------------
-- 2. 多周期K线聚合 (级联聚合优化)
-- 使用1分钟K线聚合更高级别K线，避免重复扫描原始数据
-- -------------------------------------------------

-- 5分钟K线 (从1分钟聚合)
CREATE MATERIALIZED VIEW candle_5min_realtime
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('5 minutes', bucket) AS bucket,
    exchange,
    symbol,
    first(open, bucket) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, bucket) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    sum(trades) AS trades
FROM candle_1min_realtime
GROUP BY bucket, exchange, symbol
WITH NO DATA;

-- 设置级联刷新策略
SELECT add_continuous_aggregate_policy('candle_5min_realtime',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '5 minutes',
    schedule_interval => INTERVAL '5 minutes'
);

-- -------------------------------------------------
-- 3. 实时聚合物化视图优化
-- -------------------------------------------------

-- 为物化视图创建索引
CREATE INDEX idx_candle_1min_rt_symbol ON candle_1min_realtime (symbol, bucket DESC);
CREATE INDEX idx_candle_5min_rt_symbol ON candle_5min_realtime (symbol, bucket DESC);

-- -------------------------------------------------
-- 4. 查询实时聚合数据
-- -------------------------------------------------

-- 查看最新K线 (自动结合物化视图和实时数据)
SELECT * FROM candle_1min_realtime
WHERE symbol = 'AAPL'
  AND bucket >= NOW() - INTERVAL '1 hour'
ORDER BY bucket DESC;
```

### 5.4 并行查询优化

```sql
-- =====================================================
-- 并行查询优化
-- PostgreSQL并行查询 + 自定义并行策略
-- =====================================================

-- -------------------------------------------------
-- 1. 数据库级并行配置
-- -------------------------------------------------

-- 查看当前并行配置
SELECT name, setting FROM pg_settings WHERE name LIKE '%parallel%';

-- 推荐配置 (根据CPU核心数调整)
ALTER SYSTEM SET max_parallel_workers_per_gather = 8;
ALTER SYSTEM SET max_parallel_workers = 16;
ALTER SYSTEM SET parallel_tuple_cost = 0.01;
ALTER SYSTEM SET parallel_setup_cost = 10;
ALTER SYSTEM SET min_parallel_table_scan_size = '8MB';
ALTER SYSTEM SET min_parallel_index_scan_size = '512kB';

-- 重载配置
SELECT pg_reload_conf();

-- -------------------------------------------------
-- 2. 表级并行提示
-- -------------------------------------------------

-- 强制使用并行查询
SET max_parallel_workers_per_gather = 8;

-- 大查询示例: 并行聚合历史数据
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    symbol,
    DATE(ts) as trade_date,
    COUNT(*) as tick_count,
    AVG(price) as avg_price,
    STDDEV(price) as price_std
FROM tick_data
WHERE ts >= '2023-01-01' AND ts < '2024-01-01'
GROUP BY symbol, DATE(ts);

-- -------------------------------------------------
-- 3. 分区并行扫描
-- -------------------------------------------------

-- 创建并行查询友好的聚合函数
CREATE OR REPLACE FUNCTION parallel_backtest(
    p_strategy_id TEXT,
    p_start_date DATE,
    p_end_date DATE,
    p_symbols TEXT[]
)
RETURNS TABLE (
    symbol TEXT,
    total_return NUMERIC,
    sharpe_ratio NUMERIC
) AS $$
BEGIN
    -- 使用并行workers扫描不同分区
    SET LOCAL max_parallel_workers_per_gather = 8;

    RETURN QUERY
    SELECT
        t.symbol,
        (last(t.close, t.ts) / first(t.open, t.ts) - 1) as total_return,
        (AVG(t.close) / STDDEV(t.close)) * SQRT(252) as sharpe_ratio
    FROM tick_data t
    WHERE t.symbol = ANY(p_symbols)
      AND t.ts BETWEEN p_start_date AND p_end_date
    GROUP BY t.symbol;
END;
$$ LANGUAGE plpgsql;

-- -------------------------------------------------
-- 4. 查询优化提示
-- -------------------------------------------------

-- 使用并行顺序扫描
SET enable_parallel_seqscan = ON;

-- 使用并行索引扫描
SET enable_parallel_indexscan = ON;

-- 使用并行位图扫描
SET enable_parallel_bitmapscan = ON;

-- 使用并行Hash Join
SET enable_parallel_hash = ON;
```

---

## 六、部署配置

### 6.1 Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL + TimescaleDB
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: trading_postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-quant}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-quant123}
      POSTGRES_DB: ${POSTGRES_DB:-trading}
      TZ: Asia/Shanghai
      PGTZ: Asia/Shanghai
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
    ports:
      - "5432:5432"
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
      -c shared_preload_libraries=timescaledb
    shm_size: 2gb
    ulimits:
      memlock:
        soft: -1
        hard: -1
    networks:
      - trading_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quant -d trading"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - 缓存和消息队列
  redis:
    image: redis:7-alpine
    container_name: trading_redis
    restart: unless-stopped
    command: redis-server /usr/local/etc/redis/redis.conf
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    sysctls:
      - net.core.somaxconn=65535
    networks:
      - trading_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # 行情接入服务
  market_data:
    build:
      context: ./market_data
      dockerfile: Dockerfile
    container_name: trading_market_data
    restart: unless-stopped
    environment:
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
      POSTGRES_USER: quant
      POSTGRES_PASSWORD: quant123
      POSTGRES_DB: trading
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - trading_network
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G

  # K线聚合服务
  candle_aggregator:
    build:
      context: ./candle_aggregator
      dockerfile: Dockerfile
    container_name: trading_candle_aggregator
    restart: unless-stopped
    environment:
      POSTGRES_HOST: postgres
      REDIS_HOST: redis
    depends_on:
      - market_data
    networks:
      - trading_network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # Grafana - 监控可视化
  grafana:
    image: grafana/grafana:latest
    container_name: trading_grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin123
      GF_INSTALL_PLUGINS: grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3000:3000"
    networks:
      - trading_network

  # Prometheus - 指标收集
  prometheus:
    image: prom/prometheus:latest
    container_name: trading_prometheus
    restart: unless-stopped
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - trading_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  grafana_data:
    driver: local
  prometheus_data:
    driver: local

networks:
  trading_network:
    driver: bridge
```

### 6.2 PostgreSQL配置

```ini
# postgresql.conf - 高频交易优化配置

# ===================================================================
# 连接配置
# ===================================================================
max_connections = 500
superuser_reserved_connections = 10
listen_addresses = '*'
port = 5432

# ===================================================================
# 内存配置 (根据服务器内存调整)
# ===================================================================
# 总内存: 256GB 推荐配置
shared_buffers = 64GB                    # 25% of RAM
effective_cache_size = 192GB             # 75% of RAM
maintenance_work_mem = 4GB               # 用于维护操作
work_mem = 256MB                         # 每个查询操作内存

# ===================================================================
# 写入优化 (高频写入场景)
# ===================================================================
wal_level = replica                      # 允许流复制
wal_buffers = 1GB
max_wal_size = 16GB
min_wal_size = 4GB
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min
synchronous_commit = off                 # 异步提交提高写入性能
fsync = on                               # 保持数据安全
full_page_writes = on

# ===================================================================
# 并发和并行
# ===================================================================
max_worker_processes = 32
max_parallel_workers_per_gather = 16
max_parallel_workers = 32
max_parallel_maintenance_workers = 8

# ===================================================================
# 查询优化器
# ===================================================================
random_page_cost = 1.1                   # SSD优化
effective_io_concurrency = 200           # SSD并发
default_statistics_target = 500          # 更准确的统计信息

# ===================================================================
# 日志配置
# ===================================================================
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 1GB
log_min_duration_statement = 1000        # 慢查询阈值1秒
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# ===================================================================
# 自动清理
# ===================================================================
autovacuum = on
autovacuum_max_workers = 6
autovacuum_naptime = 10s
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50

# ===================================================================
# TimescaleDB特定配置
# ===================================================================
timescaledb.max_background_workers = 16
timescaledb.telemetry_level = off

# ===================================================================
# 时区
# ===================================================================
log_timezone = 'Asia/Shanghai'
timezone = 'Asia/Shanghai'
```

### 6.3 Redis配置

```ini
# redis.conf - 高频交易优化

# ===================================================================
# 基础配置
# ===================================================================
bind 0.0.0.0
port 6379
tcp-backlog 65535
timeout 0
tcp-keepalive 300

# ===================================================================
# 内存配置
# ===================================================================
maxmemory 16gb
maxmemory-policy allkeys-lru

# ===================================================================
# 持久化配置 (降低频率，优先性能)
# ===================================================================
save ""                              # 禁用RDB自动保存
# save 900 1
# save 300 10
# save 60 10000

appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec                  # 每秒同步，平衡性能和安全
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# ===================================================================
# 性能优化
# ===================================================================
databases 16
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# ===================================================================
# Stream配置 (用于消息队列)
# ===================================================================
stream-node-max-bytes 4096
stream-node-max-entries 100

# ===================================================================
# 客户端输出缓冲
# ===================================================================
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# ===================================================================
# 内核优化参数 (需要在宿主机上设置)
# ===================================================================
# echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
# echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
# sysctl -p
```

### 6.4 监控告警

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'market_data'
    static_configs:
      - targets: ['market_data:8000']
```

```yaml
# prometheus/rules/trading_alerts.yml
groups:
  - name: trading_alerts
    rules:
      # PostgreSQL连接数告警
      - alert: PostgreSQLHighConnections
        expr: pg_stat_activity_count > 400
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL连接数过高"
          description: "当前连接数: {{ $value }}"

      # PostgreSQL慢查询告警
      - alert: PostgreSQLSlowQueries
        expr: pg_stat_statements_mean_time > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL存在慢查询"
          description: "平均查询时间: {{ $value }}ms"

      # Redis内存告警
      - alert: RedisHighMemoryUsage
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Redis内存使用过高"
          description: "内存使用率: {{ $value | humanizePercentage }}"

      # 行情延迟告警
      - alert: MarketDataDelay
        expr: market_data_latency_seconds > 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "行情数据延迟过高"
          description: "当前延迟: {{ $value }}s"

      # 服务不可用告警
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务不可用"
          description: "{{ $labels.job }} 服务已停止"
```

---

## 七、生产检查清单

### 7.1 部署前检查

```markdown
## 基础设施检查

### 硬件
- [ ] CPU: 32核+，主频3.0GHz+
- [ ] 内存: 256GB+ DDR4/DDR5 ECC
- [ ] 热存储: 2TB+ NVMe SSD (三星PM1733/Intel Optane)
- [ ] 网络: 10Gbps+，延迟<100μs

### 操作系统
- [ ] Linux内核参数优化 (tcp, memory, file descriptors)
- [ ] 关闭NUMA (或正确配置)
- [ ] CPU性能模式设置为performance
- [ ] 禁用swap或设置swappiness=1

### 网络
- [ ] 交易所专线接入配置
- [ ] 防火墙规则配置
- [ ] 时间同步 (NTP/chrony，精度<1ms)

## 数据库检查

### PostgreSQL
- [ ] 版本15+，TimescaleDB 2.11+
- [ ] 配置文件优化 (postgresql.conf)
- [ ] 扩展安装: timescaledb, pg_stat_statements
- [ ] 连接池配置 (PgBouncer)
- [ ] 备份策略配置 (WAL归档，PITR)
- [ ] 主从复制配置 (流复制)

### 表结构
- [ ] Hypertable创建和分区策略
- [ ] 索引创建 (BRIN, B-tree)
- [ ] 连续聚合策略配置
- [ ] 数据保留和压缩策略

### Redis
- [ ] 版本7+
- [ ] 持久化策略配置
- [ ] 内存限制和淘汰策略
- [ ] Cluster配置 (高可用)

## 应用检查

### 代码
- [ ] 单元测试覆盖率>80%
- [ ] 性能测试通过 (延迟、吞吐量)
- [ ] 内存泄漏检查
- [ ] 异常处理完善

### 配置
- [ ] 环境变量配置正确
- [ ] 日志级别设置
- [ ] 监控指标暴露
- [ ] 健康检查端点

### 安全
- [ ] 数据库密码强度
- [ ] 网络隔离配置
- [ ] SSL/TLS配置
- [ ] 敏感信息加密

## 监控告警

### 监控
- [ ] Prometheus部署和配置
- [ ] Grafana仪表板导入
- [ ] 关键指标采集正常
- [ ] 日志收集 (Loki/ELK)

### 告警
- [ ] 告警规则配置
- [ ] 告警渠道配置 (邮件/短信/钉钉)
- [ ] 告警阈值合理性检查
- [ ] 告警测试

## 数据检查

### 历史数据
- [ ] 历史数据完整性检查
- [ ] 数据质量校验
- [ ] 复权因子应用
- [ ] 缺失数据回补

### 实时数据
- [ ] 行情接入测试
- [ ] 数据延迟监控
- [ ] 去重机制验证
- [ ] 数据完整性检查

## 灾备检查

### 备份
- [ ] 数据库自动备份配置
- [ ] 备份恢复测试
- [ ] 异地备份配置

### 故障切换
- [ ] 主从切换测试
- [ ] 服务自动重启配置
- [ ] 数据回补机制验证
```

### 7.2 性能基准测试

```python
#!/usr/bin/env python3
"""
性能基准测试脚本

测试项目:
1. 写入性能: Tick数据写入吞吐量
2. 查询性能: K线查询延迟
3. 聚合性能: 连续聚合计算时间
4. 并发性能: 多客户端并发测试
"""

import asyncio
import asyncpg
import time
from datetime import datetime, timedelta
import numpy as np
from typing import List


class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.results = {}

    async def run_all(self):
        """运行所有测试"""
        print("="*60)
        print("PostgreSQL TimescaleDB 性能基准测试")
        print("="*60)

        # 连接池
        pool = await asyncpg.create_pool(self.dsn, min_size=10, max_size=50)

        # 测试写入性能
        await self.test_insert_throughput(pool)

        # 测试查询性能
        await self.test_query_latency(pool)

        # 测试聚合性能
        await self.test_aggregation_performance(pool)

        # 测试并发性能
        await self.test_concurrent_performance(pool)

        await pool.close()

        # 输出结果
        self.print_results()

    async def test_insert_throughput(self, pool: asyncpg.Pool):
        """测试写入吞吐量"""
        print("\n[测试] 写入吞吐量")

        batch_sizes = [100, 1000, 5000]

        for batch_size in batch_sizes:
            # 准备测试数据
            test_data = [
                (
                    datetime.now() - timedelta(seconds=i),
                    0,
                    'TEST',
                    'AAPL',
                    150.0 + np.random.randn(),
                    100,
                    15000.0,
                    'B',
                    i,
                    i+1,
                    149.99,
                    1000,
                    150.01,
                    500,
                    datetime.now()
                )
                for i in range(batch_size)
            ]

            # 预热
            async with pool.acquire() as conn:
                await conn.copy_records_to_table(
                    'tick_data',
                    records=test_data[:10],
                    columns=['ts', 'ns_offset', 'exchange', 'symbol', 'price',
                             'volume', 'amount', 'side', 'bid_order_id', 'ask_order_id',
                             'bid_price', 'bid_size', 'ask_price', 'ask_size', 'received_at']
                )

            # 正式测试
            start = time.time()
            async with pool.acquire() as conn:
                await conn.copy_records_to_table(
                    'tick_data',
                    records=test_data,
                    columns=['ts', 'ns_offset', 'exchange', 'symbol', 'price',
                             'volume', 'amount', 'side', 'bid_order_id', 'ask_order_id',
                             'bid_price', 'bid_size', 'ask_price', 'ask_size', 'received_at']
                )
            elapsed = time.time() - start

            throughput = batch_size / elapsed
            print(f"  Batch size {batch_size}: {throughput:.0f} records/sec")

            self.results[f'insert_throughput_{batch_size}'] = throughput

    async def test_query_latency(self, pool: asyncpg.Pool):
        """测试查询延迟"""
        print("\n[测试] 查询延迟")

        queries = {
            'latest_tick': "SELECT * FROM tick_data WHERE symbol='AAPL' ORDER BY ts DESC LIMIT 1",
            'candle_1min': "SELECT * FROM candle_1min WHERE symbol='AAPL' AND bucket > NOW() - INTERVAL '1 hour'",
            'agg_stats': """
                SELECT symbol, COUNT(*), AVG(price), MAX(price), MIN(price)
                FROM tick_data
                WHERE ts > NOW() - INTERVAL '1 minute'
                GROUP BY symbol
            """
        }

        for name, sql in queries.items():
            latencies = []

            async with pool.acquire() as conn:
                # 预热
                for _ in range(5):
                    await conn.fetch(sql)

                # 测试100次
                for _ in range(100):
                    start = time.time()
                    await conn.fetch(sql)
                    latencies.append((time.time() - start) * 1000)  # ms

            avg_latency = np.mean(latencies)
            p99_latency = np.percentile(latencies, 99)

            print(f"  {name}: avg={avg_latency:.2f}ms, p99={p99_latency:.2f}ms")

            self.results[f'query_{name}_avg'] = avg_latency
            self.results[f'query_{name}_p99'] = p99_latency

    async def test_aggregation_performance(self, pool: asyncpg.Pool):
        """测试聚合性能"""
        print("\n[测试] 聚合性能")

        # 测试K线聚合查询
        sql = """
        SELECT
            time_bucket('1 minute', ts) as bucket,
            first(price, ts) as open,
            max(price) as high,
            min(price) as low,
            last(price, ts) as close,
            sum(volume) as volume
        FROM tick_data
        WHERE ts > NOW() - INTERVAL '1 hour'
        GROUP BY bucket
        ORDER BY bucket
        """

        async with pool.acquire() as conn:
            start = time.time()
            result = await conn.fetch(sql)
            elapsed = time.time() - start

        print(f"  1小时K线聚合: {elapsed*1000:.2f}ms ({len(result)} bars)")
        self.results['aggregation_1hour_ms'] = elapsed * 1000

    async def test_concurrent_performance(self, pool: asyncpg.Pool):
        """测试并发性能"""
        print("\n[测试] 并发性能")

        async def worker(worker_id: int, iterations: int):
            async with pool.acquire() as conn:
                for i in range(iterations):
                    await conn.fetch(
                        "SELECT * FROM tick_data WHERE symbol=$1 ORDER BY ts DESC LIMIT 10",
                        f"SYM{i % 10}"
                    )

        concurrency_levels = [10, 50, 100]

        for concurrency in concurrency_levels:
            start = time.time()

            tasks = [worker(i, 100) for i in range(concurrency)]
            await asyncio.gather(*tasks)

            elapsed = time.time() - start
            total_queries = concurrency * 100
            qps = total_queries / elapsed

            print(f"  {concurrency}并发: {qps:.0f} QPS")
            self.results[f'concurrent_{concurrency}_qps'] = qps

    def print_results(self):
        """打印测试结果"""
        print("\n" + "="*60)
        print("测试结果汇总")
        print("="*60)
        for key, value in self.results.items():
            print(f"{key}: {value:.2f}")


# 运行测试
if __name__ == '__main__':
    DSN = "postgresql://quant:quant123@localhost:5432/trading"
    benchmark = PerformanceBenchmark(DSN)
    asyncio.run(benchmark.run_all())
```

---

## 八、参考资源

### 8.1 技术文档

| 资源 | 链接 |
|-----|------|
| PostgreSQL官方文档 | <https://www.postgresql.org/docs/> |
| TimescaleDB文档 | <https://docs.timescale.com/> |
| kdb+文档 | <https://code.kx.com/q/> |
| QuestDB文档 | <https://questdb.io/docs/> |
| ClickHouse文档 | <https://clickhouse.com/docs/> |

### 8.2 学术论文

1. "High-Frequency Trading and Price Discovery" - Hasbrouck & Saar (2013)
2. "Market Microstructure in Practice" - Lehalle & Laruelle (2013)
3. "The Financial Mathematics of Market Liquidity" - Guéant (2016)

### 8.3 开源项目

| 项目 | 说明 |
|-----|------|
| QuantConnect | 开源量化平台 |
| Zipline | Python回测框架 |
| Backtrader | Python回测库 |
| vn.py | 开源量化交易框架 |

### 8.4 行业最佳实践

1. **kdb+/q最佳实践**
   - 使用splayed tables存储时序数据
   - 利用parted属性优化查询
   - 内存映射文件管理大数据

2. **TimescaleDB优化**
   - 合理使用hypertable分区
   - 配置连续聚合减少实时计算
   - 利用压缩节省存储空间

3. **高频交易系统设计**
   - 内存优先架构
   - 无锁数据结构设计
   - 内核旁路网络 (DPDK/RDMA)

---

## 总结

本文档完整介绍了基于PostgreSQL + TimescaleDB的高频交易数据分析平台的架构设计、数据模型、核心代码实现和生产部署方案。

### 关键特性

- **纳秒级时间戳**: 支持微秒甚至纳秒级的时间精度
- **三层存储架构**: 热数据内存表 + 温数据TimescaleDB + 冷数据对象存储
- **实时K线聚合**: 利用Continuous Aggregates自动维护多周期K线
- **高性能接入**: asyncio + 批量写入 + 连接池优化
- **完整回测框架**: 事件驱动架构，支持滑点和成本模拟

### 性能指标

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| 写入吞吐量 | 100,000+ TPS | 批量COPY写入 |
| 查询延迟 | <10ms | 单品种K线查询 |
| 数据延迟 | <100ms | 端到端行情延迟 |
| 存储压缩比 | 10:1 | TimescaleDB压缩 |

### 后续优化方向

1. 引入ClickHouse进行离线分析
2. 集成Flink进行流处理
3. 支持多交易所、多品种并发接入
4. 开发可视化的策略回测平台

---

*文档版本: v1.0*
*最后更新: 2024-01-01*
*作者: Quant Development Team*

## 附录A: 高级查询示例

### A.1 复杂分析查询

```sql
-- =====================================================
-- 高级分析查询示例
-- =====================================================

-- -------------------------------------------------
-- 1. 成交量分布分析 (Volume Profile)
-- 分析在不同价格区间的成交量分布，识别支撑阻力位
-- -------------------------------------------------

WITH price_levels AS (
    SELECT
        symbol,
        date_trunc('day', ts) as trading_day,
        width_bucket(
            price::numeric,
            MIN(price::numeric) OVER (PARTITION BY symbol, date_trunc('day', ts)),
            MAX(price::numeric) OVER (PARTITION BY symbol, date_trunc('day', ts)),
            20  -- 分20个价格区间
        ) as price_bucket,
        price,
        volume
    FROM tick_data
    WHERE ts >= CURRENT_DATE - INTERVAL '7 days'
),
volume_by_level AS (
    SELECT
        symbol,
        trading_day,
        price_bucket,
        AVG(price) as avg_price,
        SUM(volume) as total_volume,
        COUNT(*) as trade_count
    FROM price_levels
    GROUP BY symbol, trading_day, price_bucket
)
SELECT
    symbol,
    trading_day,
    price_bucket,
    round(avg_price::numeric, 2) as price_level,
    total_volume,
    round(100.0 * total_volume / SUM(total_volume) OVER (PARTITION BY symbol, trading_day), 2) as volume_pct
FROM volume_by_level
WHERE total_volume > 0
ORDER BY symbol, trading_day, price_bucket;

-- -------------------------------------------------
-- 2. 订单流分析 (Order Flow Analysis)
-- 分析主动买卖压力，识别大单动向
-- -------------------------------------------------

WITH order_flow AS (
    SELECT
        ts,
        symbol,
        price,
        volume,
        side,
        -- 估算主动买卖
        CASE
            WHEN side = 'B' AND price >= COALESCE(ask_price, price) THEN 'ACTIVE_BUY'
            WHEN side = 'S' AND price <= COALESCE(bid_price, price) THEN 'ACTIVE_SELL'
            ELSE 'PASSIVE'
        END as flow_type,
        -- 大单标识
        CASE WHEN volume >= 10000 THEN 'LARGE' ELSE 'SMALL' END as order_size
    FROM tick_data
    WHERE ts >= NOW() - INTERVAL '1 hour'
),
flow_summary AS (
    SELECT
        date_trunc('minute', ts) as minute,
        symbol,
        flow_type,
        order_size,
        COUNT(*) as order_count,
        SUM(volume) as total_volume,
        AVG(price) as avg_price
    FROM order_flow
    GROUP BY date_trunc('minute', ts), symbol, flow_type, order_size
)
SELECT
    minute,
    symbol,
    SUM(CASE WHEN flow_type = 'ACTIVE_BUY' THEN total_volume ELSE 0 END) as active_buy_vol,
    SUM(CASE WHEN flow_type = 'ACTIVE_SELL' THEN total_volume ELSE 0 END) as active_sell_vol,
    SUM(CASE WHEN order_size = 'LARGE' AND flow_type = 'ACTIVE_BUY' THEN total_volume ELSE 0 END) as large_buy_vol,
    SUM(CASE WHEN order_size = 'LARGE' AND flow_type = 'ACTIVE_SELL' THEN total_volume ELSE 0 END) as large_sell_vol
FROM flow_summary
GROUP BY minute, symbol
ORDER BY minute DESC;

-- -------------------------------------------------
-- 3. 波动率锥 (Volatility Cone)
-- 分析不同时间周期的波动率分布
-- -------------------------------------------------

WITH returns AS (
    SELECT
        symbol,
        bucket,
        close,
        LAG(close) OVER (PARTITION BY symbol ORDER BY bucket) as prev_close,
        close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY bucket), 0) - 1 as daily_return
    FROM candle_1day
    WHERE bucket >= CURRENT_DATE - INTERVAL '1 year'
),
volatility_stats AS (
    SELECT
        symbol,
        -- 20日波动率
        STDDEV(daily_return) FILTER (WHERE bucket >= CURRENT_DATE - INTERVAL '20 days') * SQRT(252) as vol_20d,
        -- 60日波动率
        STDDEV(daily_return) FILTER (WHERE bucket >= CURRENT_DATE - INTERVAL '60 days') * SQRT(252) as vol_60d,
        -- 120日波动率
        STDDEV(daily_return) FILTER (WHERE bucket >= CURRENT_DATE - INTERVAL '120 days') * SQRT(252) as vol_120d,
        -- 250日波动率
        STDDEV(daily_return) * SQRT(252) as vol_250d,
        -- 历史分位数
        PERCENTILE_CONT(0.1) WITHIN GROUP (ORDER BY STDDEV(daily_return)) OVER (PARTITION BY symbol) as vol_p10,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY STDDEV(daily_return)) OVER (PARTITION BY symbol) as vol_p25,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY STDDEV(daily_return)) OVER (PARTITION BY symbol) as vol_p50,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY STDDEV(daily_return)) OVER (PARTITION BY symbol) as vol_p75,
        PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY STDDEV(daily_return)) OVER (PARTITION BY symbol) as vol_p90
    FROM returns
    WHERE daily_return IS NOT NULL
    GROUP BY symbol
)
SELECT * FROM volatility_stats;

-- -------------------------------------------------
-- 4. 相关性矩阵计算
-- 计算多品种之间的价格相关性
-- -------------------------------------------------

WITH daily_returns AS (
    SELECT
        symbol,
        bucket,
        close / NULLIF(LAG(close) OVER (PARTITION BY symbol ORDER BY bucket), 0) - 1 as daily_return
    FROM candle_1day
    WHERE bucket >= CURRENT_DATE - INTERVAL '90 days'
),
pivoted_returns AS (
    SELECT
        bucket,
        MAX(CASE WHEN symbol = 'AAPL' THEN daily_return END) as AAPL_ret,
        MAX(CASE WHEN symbol = 'GOOGL' THEN daily_return END) as GOOGL_ret,
        MAX(CASE WHEN symbol = 'MSFT' THEN daily_return END) as MSFT_ret,
        MAX(CASE WHEN symbol = 'AMZN' THEN daily_return END) as AMZN_ret
    FROM daily_returns
    WHERE daily_return IS NOT NULL
    GROUP BY bucket
)
SELECT
    round(CORR(AAPL_ret, GOOGL_ret)::numeric, 3) as aapl_googl,
    round(CORR(AAPL_ret, MSFT_ret)::numeric, 3) as aapl_msft,
    round(CORR(AAPL_ret, AMZN_ret)::numeric, 3) as aapl_amzn,
    round(CORR(GOOGL_ret, MSFT_ret)::numeric, 3) as googl_msft,
    round(CORR(GOOGL_ret, AMZN_ret)::numeric, 3) as googl_amzn,
    round(CORR(MSFT_ret, AMZN_ret)::numeric, 3) as msft_amzn
FROM pivoted_returns;

-- -------------------------------------------------
-- 5. 资金流向分析
-- 基于Tick数据估算主力资金流向
-- -------------------------------------------------

WITH tick_classified AS (
    SELECT
        ts,
        symbol,
        price,
        volume,
        amount,
        -- 根据价格和订单簿判断主动买卖
        CASE
            WHEN side = 'B' AND price >= COALESCE(ask_price, price * 1.001) THEN 'INFLOW'
            WHEN side = 'S' AND price <= COALESCE(bid_price, price * 0.999) THEN 'OUTFLOW'
            ELSE 'NEUTRAL'
        END as capital_direction,
        -- 根据成交量分级
        CASE
            WHEN volume >= 100000 THEN 'LARGE'
            WHEN volume >= 10000 THEN 'MEDIUM'
            ELSE 'SMALL'
        END as trade_category
    FROM tick_data
    WHERE ts >= date_trunc('day', NOW())
),
intraday_flow AS (
    SELECT
        date_trunc('hour', ts) as hour,
        symbol,
        capital_direction,
        trade_category,
        SUM(amount) as flow_amount,
        COUNT(*) as trade_count
    FROM tick_classified
    GROUP BY date_trunc('hour', ts), symbol, capital_direction, trade_category
)
SELECT
    hour,
    symbol,
    SUM(CASE WHEN capital_direction = 'INFLOW' THEN flow_amount ELSE 0 END) as inflow,
    SUM(CASE WHEN capital_direction = 'OUTFLOW' THEN flow_amount ELSE 0 END) as outflow,
    SUM(CASE WHEN capital_direction = 'INFLOW' THEN flow_amount ELSE 0 END) -
    SUM(CASE WHEN capital_direction = 'OUTFLOW' THEN flow_amount ELSE 0 END) as net_flow,
    SUM(flow_amount) as total_amount
FROM intraday_flow
GROUP BY hour, symbol
ORDER BY hour DESC, net_flow DESC;
```

### A.2 性能优化查询

```sql
-- =====================================================
-- 性能优化查询示例
-- =====================================================

-- -------------------------------------------------
-- 1. 使用BRIN索引的范围查询
-- -------------------------------------------------

EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM tick_data
WHERE ts >= '2024-01-01' AND ts < '2024-01-02'
  AND symbol = 'AAPL';

-- -------------------------------------------------
-- 2. 分区裁剪效果验证
-- -------------------------------------------------

EXPLAIN (ANALYZE, VERBOSE)
SELECT symbol, COUNT(*)
FROM tick_data
WHERE ts >= '2024-01-01' AND ts < '2024-01-02'
GROUP BY symbol;

-- -------------------------------------------------
-- 3. 并行查询计划
-- -------------------------------------------------

SET max_parallel_workers_per_gather = 8;

EXPLAIN (ANALYZE, VERBOSE)
SELECT
    symbol,
    date_trunc('hour', ts) as hour,
    AVG(price) as avg_price,
    STDDEV(price) as price_std,
    SUM(volume) as total_volume
FROM tick_data
WHERE ts >= NOW() - INTERVAL '7 days'
GROUP BY symbol, date_trunc('hour', ts);

-- -------------------------------------------------
-- 4. 增量聚合查询优化
-- -------------------------------------------------

-- 使用连续聚合物化视图代替实时计算
SELECT * FROM candle_1min_continuous
WHERE symbol = 'AAPL'
  AND bucket >= NOW() - INTERVAL '1 day'
ORDER BY bucket DESC
LIMIT 100;
```

## 附录B: 系统运维脚本

```bash
#!/bin/bash
# =====================================================
# PostgreSQL运维脚本集
# =====================================================

# 配置
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="quant"
PG_DB="trading"
BACKUP_DIR="/backup/postgres"
RETENTION_DAYS=30

# -------------------------------------------------
# 1. 每日备份脚本
# -------------------------------------------------

backup_daily() {
    local backup_file="${BACKUP_DIR}/trading_$(date +%Y%m%d_%H%M%S).dump"

    echo "Starting daily backup: ${backup_file}"

    # 使用pg_dump进行逻辑备份
    pg_dump -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} \
        -Fc -Z9 -f "${backup_file}" \
        --verbose --no-owner --no-acl

    if [ $? -eq 0 ]; then
        echo "Backup completed: ${backup_file}"

        # 上传到对象存储
        aws s3 cp "${backup_file}" s3://trading-backups/postgres/

        # 删除本地旧备份
        find ${BACKUP_DIR} -name "trading_*.dump" -mtime +3 -delete
    else
        echo "Backup failed!"
        exit 1
    fi
}

# -------------------------------------------------
# 2. 数据保留策略执行
# -------------------------------------------------

data_retention() {
    echo "Executing data retention policy..."

    psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} <<EOF
        -- 删除超期数据
        SELECT drop_chunks(
            'tick_data',
            older_than => INTERVAL '${RETENTION_DAYS} days'
        );

        -- 压缩旧数据
        SELECT compress_chunk(i)
        FROM show_chunks('tick_data', older_than => INTERVAL '7 days') i
        WHERE NOT is_compressed(i);
EOF

    echo "Data retention completed"
}

# -------------------------------------------------
# 3. 性能统计收集
# -------------------------------------------------

collect_stats() {
    local stats_file="/var/log/postgres/stats_$(date +%Y%m%d).log"

    echo "Collecting performance statistics..."

    psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} <<EOF >> ${stats_file}
        \echo '=== Database Size ==='
        SELECT pg_size_pretty(pg_database_size('${PG_DB}'));

        \echo '=== Table Sizes ==='
        SELECT
            schemaname,
            relname,
            pg_size_pretty(pg_total_relation_size(relid)) as size,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(relid) DESC
        LIMIT 20;

        \echo '=== Chunk Statistics ==='
        SELECT
            chunk_name,
            range_start,
            range_end,
            pg_size_pretty(d.total_bytes) as size,
            is_compressed
        FROM timescaledb_information.chunks c
        JOIN LATERAL (
            SELECT pg_total_relation_size(c.chunk_name::regclass) as total_bytes
        ) d ON true
        ORDER BY range_start DESC
        LIMIT 20;

        \echo '=== Slow Queries ==='
        SELECT
            query,
            calls,
            round(total_exec_time::numeric, 2) as total_time,
            round(mean_exec_time::numeric, 2) as avg_time,
            rows as total_rows
        FROM pg_stat_statements
        ORDER BY total_exec_time DESC
        LIMIT 10;
EOF

    echo "Statistics collected: ${stats_file}"
}

# -------------------------------------------------
# 4. 健康检查
# -------------------------------------------------

health_check() {
    echo "Performing health check..."

    local errors=0

    # 检查连接数
    local conn_count=$(psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -t -c "SELECT count(*) FROM pg_stat_activity;")
    if [ ${conn_count} -gt 400 ]; then
        echo "WARNING: High connection count: ${conn_count}"
        ((errors++))
    fi

    # 检查复制延迟
    local lag=$(psql -h ${PG_HOST} -p ${PG_PORT} -U ${PG_USER} -d ${PG_DB} -t -c "SELECT extract(epoch from (now() - pg_last_xact_replay_timestamp()));")
    if [ $(echo "${lag} > 10" | bc) -eq 1 ]; then
        echo "WARNING: Replication lag: ${lag} seconds"
        ((errors++))
    fi

    # 检查磁盘空间
    local disk_usage=$(df -h /var/lib/postgresql | tail -1 | awk '{print $5}' | tr -d '%')
    if [ ${disk_usage} -gt 80 ]; then
        echo "WARNING: Disk usage: ${disk_usage}%"
        ((errors++))
    fi

    if [ ${errors} -eq 0 ]; then
        echo "Health check PASSED"
        return 0
    else
        echo "Health check FAILED with ${errors} errors"
        return 1
    fi
}

# -------------------------------------------------
# 主执行逻辑
# -------------------------------------------------

case "$1" in
    backup)
        backup_daily
        ;;
    retention)
        data_retention
        ;;
    stats)
        collect_stats
        ;;
    health)
        health_check
        ;;
    all)
        health_check && backup_daily && data_retention && collect_stats
        ;;
    *)
        echo "Usage: $0 {backup|retention|stats|health|all}"
        exit 1
        ;;
esac
```

## 附录C: Python工具类库

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高频交易工具类库
提供常用的数据处理和计算功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Optional, Union, Dict
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json


class TimeUtils:
    """时间处理工具"""

    @staticmethod
    def ns_to_datetime(ns_timestamp: int) -> datetime:
        """纳秒时间戳转datetime"""
        seconds = ns_timestamp // 1_000_000_000
        nanoseconds = ns_timestamp % 1_000_000_000
        dt = datetime.fromtimestamp(seconds)
        return dt.replace(microsecond=nanoseconds // 1000)

    @staticmethod
    def datetime_to_ns(dt: datetime) -> int:
        """datetime转纳秒时间戳"""
        seconds = int(dt.timestamp())
        microseconds = dt.microsecond
        return seconds * 1_000_000_000 + microseconds * 1000

    @staticmethod
    def get_trading_days(start: datetime, end: datetime) -> List[datetime]:
        """获取交易日列表 (简化版，实际需要对接交易所日历)"""
        days = []
        current = start
        while current <= end:
            # 跳过周末
            if current.weekday() < 5:
                days.append(current)
            current += timedelta(days=1)
        return days

    @staticmethod
    def is_trading_time(dt: datetime, market: str = 'CN') -> bool:
        """检查是否在交易时段"""
        if market == 'CN':
            # A股交易时间: 9:30-11:30, 13:00-15:00
            time_str = dt.strftime('%H:%M')
            return ('09:30' <= time_str <= '11:30') or ('13:00' <= time_str <= '15:00')
        return True


class MathUtils:
    """数学计算工具"""

    @staticmethod
    def round_decimal(value: Decimal, precision: int = 2) -> Decimal:
        """Decimal四舍五入"""
        quantize_str = '0.' + '0' * precision
        return value.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_vwap(prices: List[Decimal], volumes: List[int]) -> Decimal:
        """计算VWAP"""
        total_value = sum(p * v for p, v in zip(prices, volumes))
        total_volume = sum(volumes)
        return total_value / total_volume if total_volume > 0 else Decimal('0')

    @staticmethod
    def calculate_returns(prices: List[Decimal]) -> List[Decimal]:
        """计算收益率序列"""
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        return returns

    @staticmethod
    def annualized_return(daily_returns: List[float], trading_days: int = 252) -> float:
        """年化收益率"""
        if not daily_returns:
            return 0.0
        avg_daily_return = np.mean(daily_returns)
        return avg_daily_return * trading_days

    @staticmethod
    def annualized_volatility(daily_returns: List[float], trading_days: int = 252) -> float:
        """年化波动率"""
        if len(daily_returns) < 2:
            return 0.0
        return np.std(daily_returns, ddof=1) * np.sqrt(trading_days)

    @staticmethod
    def sharpe_ratio(daily_returns: List[float], risk_free_rate: float = 0.02) -> float:
        """夏普比率"""
        if len(daily_returns) < 2:
            return 0.0
        excess_returns = np.mean(daily_returns) - risk_free_rate / 252
        volatility = np.std(daily_returns, ddof=1)
        return (excess_returns / volatility) * np.sqrt(252) if volatility > 0 else 0.0

    @staticmethod
    def max_drawdown(equity_curve: List[float]) -> Tuple[float, int, int]:
        """计算最大回撤及起止位置"""
        peak = equity_curve[0]
        max_dd = 0.0
        peak_idx = 0
        dd_start = 0
        dd_end = 0

        for i, value in enumerate(equity_curve):
            if value > peak:
                peak = value
                peak_idx = i

            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
                dd_start = peak_idx
                dd_end = i

        return max_dd, dd_start, dd_end


class DataUtils:
    """数据处理工具"""

    @staticmethod
    @lru_cache(maxsize=1024)
    def normalize_symbol(symbol: str, exchange: str) -> str:
        """标准化股票代码"""
        symbol = symbol.upper().strip()

        # A股代码标准化
        if exchange in ['SSE', 'SH']:
            if not symbol.endswith('.SH'):
                symbol = f"{symbol}.SH"
        elif exchange in ['SZSE', 'SZ']:
            if not symbol.endswith('.SZ'):
                symbol = f"{symbol}.SZ"

        return symbol

    @staticmethod
    def resample_ohlcv(
        df: pd.DataFrame,
        rule: str,
        price_cols: List[str] = ['open', 'high', 'low', 'close'],
        volume_col: str = 'volume'
    ) -> pd.DataFrame:
        """重采样OHLCV数据"""
        resampled = pd.DataFrame()

        if 'open' in price_cols:
            resampled['open'] = df['open'].resample(rule).first()
        if 'high' in price_cols:
            resampled['high'] = df['high'].resample(rule).max()
        if 'low' in price_cols:
            resampled['low'] = df['low'].resample(rule).min()
        if 'close' in price_cols:
            resampled['close'] = df['close'].resample(rule).last()

        resampled[volume_col] = df[volume_col].resample(rule).sum()

        return resampled.dropna()

    @staticmethod
    def detect_outliers(
        data: List[float],
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> List[int]:
        """检测异常值索引"""
        if method == 'iqr':
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr
            return [i for i, v in enumerate(data) if v < lower_bound or v > upper_bound]

        elif method == 'zscore':
            mean = np.mean(data)
            std = np.std(data)
            return [i for i, v in enumerate(data) if abs((v - mean) / std) > threshold]

        return []

    @staticmethod
    def fill_missing_timestamps(
        df: pd.DataFrame,
        freq: str,
        method: str = 'ffill'
    ) -> pd.DataFrame:
        """填充缺失时间戳"""
        # 重新索引到完整时间序列
        full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq=freq)
        df_reindexed = df.reindex(full_range)

        # 填充
        if method == 'ffill':
            df_reindexed = df_reindexed.fillna(method='ffill')
        elif method == 'bfill':
            df_reindexed = df_reindexed.fillna(method='bfill')
        elif method == 'interpolate':
            df_reindexed = df_reindexed.interpolate()

        return df_reindexed


class CacheUtils:
    """缓存工具"""

    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    @staticmethod
    def serialize_for_cache(obj: any) -> str:
        """序列化对象为缓存字符串"""
        if isinstance(obj, (list, dict, tuple)):
            return json.dumps(obj, sort_keys=True, default=str)
        return str(obj)


class ValidationUtils:
    """数据验证工具"""

    @staticmethod
    def validate_tick_data(tick: Dict) -> Tuple[bool, Optional[str]]:
        """验证Tick数据有效性"""
        required_fields = ['ts', 'symbol', 'price', 'volume']

        for field in required_fields:
            if field not in tick:
                return False, f"Missing required field: {field}"

        if tick['price'] <= 0:
            return False, "Price must be positive"

        if tick['volume'] <= 0:
            return False, "Volume must be positive"

        return True, None

    @staticmethod
    def validate_ohlcv(ohlcv: Dict) -> Tuple[bool, Optional[str]]:
        """验证OHLCV数据有效性"""
        required_fields = ['open', 'high', 'low', 'close', 'volume']

        for field in required_fields:
            if field not in ohlcv:
                return False, f"Missing required field: {field}"

        if not (ohlcv['low'] <= ohlcv['open'] <= ohlcv['high']):
            return False, "Invalid open price"

        if not (ohlcv['low'] <= ohlcv['close'] <= ohlcv['high']):
            return False, "Invalid close price"

        if ohlcv['volume'] < 0:
            return False, "Volume cannot be negative"

        return True, None


# 使用示例
if __name__ == '__main__':
    # 时间工具示例
    ns_ts = 1704067200000000000  # 2024-01-01 00:00:00 UTC
    dt = TimeUtils.ns_to_datetime(ns_ts)
    print(f"NS to datetime: {dt}")

    # 数学工具示例
    prices = [Decimal('100'), Decimal('101'), Decimal('102'), Decimal('101')]
    volumes = [1000, 2000, 1500, 1200]
    vwap = MathUtils.calculate_vwap(prices, volumes)
    print(f"VWAP: {vwap}")

    returns = MathUtils.calculate_returns(prices)
    print(f"Returns: {returns}")

    # 数据工具示例
    symbol = DataUtils.normalize_symbol('600000', 'SSE')
    print(f"Normalized symbol: {symbol}")

    # 缓存工具示例
    cache_key = CacheUtils.generate_cache_key('AAPL', '1m', date='2024-01-01')
    print(f"Cache key: {cache_key}")
```

---

*文档结束*

## 附录D: 交易所接口规范

### D.1 上海证券交易所行情接口

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上海证券交易所行情接口适配器

文档参考:
- 《上海证券交易所行情网关Binary接口规范》
- 《上海证券交易所Fast行情接口规范》

接口类型:
- Binary接口: UDP组播，二进制协议
- STEP接口: TCP，基于FIX协议
- FAST接口: UDP组播，FAST编码
"""

import asyncio
import struct
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Callable
import logging

logger = logging.getLogger(__name__)


@dataclass
class SSETickMessage:
    """上交所逐笔成交消息结构"""
    msg_type: int              # 消息类型: 3=逐笔成交
    security_id: str           # 证券代码 (6位)
    channel_no: int            # 频道代码
    appl_seq_num: int          # 应用序列号
    md_stream_id: str          # 行情类别: 1=现货 2=期权
    bid_appl_seq_num: int      # 买方委托序号
    offer_appl_seq_num: int    # 卖方委托序号
    security_price: Decimal    # 价格 (4位小数)
    trade_qty: int             # 成交量
    exec_type: str             # 成交类型: 0=成交 1=撤单
    trade_time: int            # 成交时间 (HHMMSSsss)

    @classmethod
    def from_binary(cls, data: bytes) -> 'SSETickMessage':
        """从二进制数据解析"""
        # 消息头: 4字节长度 + 2字节消息类型
        msg_len = struct.unpack('>H', data[0:2])[0]
        msg_type = struct.unpack('>H', data[2:4])[0]

        if msg_type != 3:
            raise ValueError(f"Unexpected message type: {msg_type}")

        # 解析消息体
        offset = 4

        # SecurityID (8字节, 右对齐，左补空格)
        security_id = data[offset:offset+8].decode('ascii').strip()
        offset += 8

        # ChannelNo (2字节)
        channel_no = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2

        # ApplSeqNum (8字节)
        appl_seq_num = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        # MDStreamID (3字节)
        md_stream_id = data[offset:offset+3].decode('ascii').strip()
        offset += 3

        # BidApplSeqNum (8字节)
        bid_appl_seq_num = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        # OfferApplSeqNum (8字节)
        offer_appl_seq_num = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        # SecurityPrice (8字节, 4位小数)
        price_raw = struct.unpack('>q', data[offset:offset+8])[0]
        security_price = Decimal(price_raw) / Decimal('10000')
        offset += 8

        # TradeQty (8字节)
        trade_qty = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        # ExecType (4字节)
        exec_type = data[offset:offset+4].decode('ascii').strip()
        offset += 4

        # TradeTime (6字节 HHMMSS)
        trade_time = struct.unpack('>I', b'\x00' + data[offset:offset+3])[0]

        return cls(
            msg_type=msg_type,
            security_id=security_id,
            channel_no=channel_no,
            appl_seq_num=appl_seq_num,
            md_stream_id=md_stream_id,
            bid_appl_seq_num=bid_appl_seq_num,
            offer_appl_seq_num=offer_appl_seq_num,
            security_price=security_price,
            trade_qty=trade_qty,
            exec_type=exec_type,
            trade_time=trade_time
        )


@dataclass
class SSEOrderBookMessage:
    """上交所订单簿快照消息结构"""
    msg_type: int
    security_id: str
    channel_no: int
    appl_seq_num: int
    md_stream_id: str
    security_price: Decimal
    order_qty: int
    side: str              # 1=买 2=卖
    md_entry_type: str     # 0=买入 1=卖出
    trade_time: int

    @classmethod
    def from_binary(cls, data: bytes) -> 'SSEOrderBookMessage':
        """从二进制数据解析订单簿消息"""
        msg_type = struct.unpack('>H', data[2:4])[0]

        if msg_type not in [1, 2]:  # 1=委托 2=成交
            raise ValueError(f"Unexpected message type: {msg_type}")

        offset = 4

        security_id = data[offset:offset+8].decode('ascii').strip()
        offset += 8

        channel_no = struct.unpack('>H', data[offset:offset+2])[0]
        offset += 2

        appl_seq_num = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        md_stream_id = data[offset:offset+3].decode('ascii').strip()
        offset += 3

        # PriceLevel (1字节)
        price_level = data[offset]
        offset += 1

        # Price (8字节)
        price_raw = struct.unpack('>q', data[offset:offset+8])[0]
        security_price = Decimal(price_raw) / Decimal('10000')
        offset += 8

        # OrderQty (8字节)
        order_qty = struct.unpack('>Q', data[offset:offset+8])[0]
        offset += 8

        # Side (1字节)
        side = chr(data[offset])
        offset += 1

        # MDEntryType (2字节)
        md_entry_type = data[offset:offset+2].decode('ascii').strip()

        return cls(
            msg_type=msg_type,
            security_id=security_id,
            channel_no=channel_no,
            appl_seq_num=appl_seq_num,
            md_stream_id=md_stream_id,
            security_price=security_price,
            order_qty=order_qty,
            side=side,
            md_entry_type=md_entry_type,
            trade_time=0
        )


class SSEGateway:
    """上交所行情网关"""

    def __init__(
        self,
        multicast_group: str,
        multicast_port: int,
        local_ip: str,
        heartbeat_interval: int = 5
    ):
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.local_ip = local_ip
        self.heartbeat_interval = heartbeat_interval

        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional[asyncio.DatagramProtocol] = None

        self.on_tick: Optional[Callable[[SSETickMessage], None]] = None
        self.on_order_book: Optional[Callable[[SSEOrderBookMessage], None]] = None

    async def connect(self):
        """连接组播行情"""
        loop = asyncio.get_event_loop()

        # 创建UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定到本地地址
        sock.bind(('', self.multicast_port))

        # 加入组播组
        mreq = struct.pack(
            '4s4s',
            socket.inet_aton(self.multicast_group),
            socket.inet_aton(self.local_ip)
        )
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # 创建asyncio transport
        self.transport, self.protocol = await loop.create_datagram_endpoint(
            lambda: SSEProtocol(self),
            sock=sock
        )

        logger.info(f"Connected to SSE multicast: {self.multicast_group}:{self.multicast_port}")

    async def disconnect(self):
        """断开连接"""
        if self.transport:
            self.transport.close()
            logger.info("Disconnected from SSE multicast")


class SSEProtocol(asyncio.DatagramProtocol):
    """上交所行情协议处理器"""

    def __init__(self, gateway: SSEGateway):
        self.gateway = gateway
        self.buffer = bytearray()

    def datagram_received(self, data: bytes, addr: tuple):
        """接收数据报"""
        try:
            # 解析消息头
            if len(data) < 4:
                return

            msg_type = struct.unpack('>H', data[2:4])[0]

            if msg_type == 3:  # 逐笔成交
                tick = SSETickMessage.from_binary(data)
                if self.gateway.on_tick:
                    self.gateway.on_tick(tick)

            elif msg_type in [1, 2]:  # 委托/成交
                order_book = SSEOrderBookMessage.from_binary(data)
                if self.gateway.on_order_book:
                    self.gateway.on_order_book(order_book)

        except Exception as e:
            logger.error(f"Error parsing SSE message: {e}")


# 使用示例
if __name__ == '__main__':
    import socket

    async def main():
        gateway = SSEGateway(
            multicast_group='224.0.100.1',
            multicast_port=30001,
            local_ip='192.168.1.100'
        )

        def on_tick(tick: SSETickMessage):
            print(f"Tick: {tick.security_id} @ {tick.security_price} x {tick.trade_qty}")

        gateway.on_tick = on_tick

        await gateway.connect()

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await gateway.disconnect()

    asyncio.run(main())
```

### D.2 FIX协议适配器

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIX协议适配器

FIX (Financial Information eXchange) 协议
是金融行业的标准通信协议，用于订单路由、市场数据等。

版本支持:
- FIX.4.2
- FIX.4.4
- FIXT.1.1 / FIX.5.0
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Callable, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FIXMsgType(Enum):
    """FIX消息类型"""
    HEARTBEAT = '0'
    TEST_REQUEST = '1'
    RESEND_REQUEST = '2'
    REJECT = '3'
    SEQUENCE_RESET = '4'
    LOGOUT = '5'
    INDICATION_OF_INTEREST = '6'
    ADVERTISEMENT = '7'
    EXECUTION_REPORT = '8'
    ORDER_CANCEL_REJECT = '9'
    LOGON = 'A'
    NEWS = 'B'
    EMAIL = 'C'
    NEW_ORDER_SINGLE = 'D'
    NEW_ORDER_LIST = 'E'
    ORDER_CANCEL_REQUEST = 'F'
    ORDER_CANCEL_REPLACE_REQUEST = 'G'
    ORDER_STATUS_REQUEST = 'H'
    ALLOCATION_INSTRUCTION = 'J'
    LIST_CANCEL_REQUEST = 'K'
    LIST_EXECUTE = 'L'
    LIST_STATUS_REQUEST = 'M'
    LIST_STATUS = 'N'
    ALLOCATION_INSTRUCTION_ACK = 'P'
    DONT_KNOW_TRADE = 'Q'
    QUOTE_REQUEST = 'R'
    QUOTE = 'S'
    SETTLEMENT_INSTRUCTIONS = 'T'
    MARKET_DATA_REQUEST = 'V'
    MARKET_DATA_SNAPSHOT_FULL_REFRESH = 'W'
    MARKET_DATA_INCREMENTAL_REFRESH = 'X'
    MARKET_DATA_REQUEST_REJECT = 'Y'


class FIXSide(Enum):
    """FIX买卖方向"""
    BUY = '1'
    SELL = '2'
    BUY_MINUS = '3'
    SELL_PLUS = '4'
    SELL_SHORT = '5'
    SELL_SHORT_EXEMPT = '6'
    UNDISCLOSED = '7'
    CROSS = '8'


class FIXOrdType(Enum):
    """FIX订单类型"""
    MARKET = '1'
    LIMIT = '2'
    STOP = '3'
    STOP_LIMIT = '4'
    MARKET_ON_CLOSE = '5'
    WITH_OR_WITHOUT = '6'
    LIMIT_OR_BETTER = '7'
    LIMIT_WITH_OR_WITHOUT = '8'
    ON_BASIS = '9'
    ON_CLOSE = 'A'
    LIMIT_ON_CLOSE = 'B'
    FOREX_MARKET = 'C'
    PREVIOUSLY_QUOTED = 'D'
    PREVIOUSLY_INDICATED = 'E'
    FOREX_LIMIT = 'F'
    FOREX_SWAP = 'G'
    FOREX_PREVIOUSLY_QUOTED = 'H'
    FUNARI = 'I'
    MARKET_IF_TOUCHED = 'J'
    MARKET_WITH_LEFT_OVER_AS_LIMIT = 'K'
    PREVIOUS_FUND_VALUATION_POINT = 'L'
    NEXT_FUND_VALUATION_POINT = 'M'
    PEGGED = 'P'


class FIXMessage:
    """FIX消息"""

    SOH = '\x01'  # 分隔符

    def __init__(self, msg_type: FIXMsgType):
        self.msg_type = msg_type
        self.fields: Dict[int, str] = {}
        self.set_field(35, msg_type.value)  # MsgType

    def set_field(self, tag: int, value: str) -> 'FIXMessage':
        """设置字段"""
        self.fields[tag] = str(value)
        return self

    def get_field(self, tag: int) -> Optional[str]:
        """获取字段"""
        return self.fields.get(tag)

    def encode(self, begin_string: str, sender_comp_id: str, target_comp_id: str, seq_num: int) -> bytes:
        """编码为FIX字符串"""
        # 构建消息体
        body_parts = []

        # 必须字段
        self.set_field(8, begin_string)           # BeginString
        self.set_field(49, sender_comp_id)        # SenderCompID
        self.set_field(56, target_comp_id)        # TargetCompID
        self.set_field(34, str(seq_num))          # MsgSeqNum
        self.set_field(52, datetime.utcnow().strftime('%Y%m%d-%H:%M:%S.%f')[:-3])  # SendingTime

        # 按标签排序 (除了8,9,10)
        for tag in sorted(self.fields.keys()):
            if tag not in [8, 9, 10]:  # 排除头部和尾部字段
                body_parts.append(f"{tag}={self.fields[tag]}")

        body = self.SOH.join(body_parts)

        # 计算BodyLength
        body_length = len(body) + 1  # +1 for trailing SOH

        # 构建完整消息
        header = f"8={begin_string}{self.SOH}9={body_length}{self.SOH}"
        full_msg = header + body + self.SOH

        # 计算Checksum
        checksum = sum(full_msg.encode()) % 256
        full_msg += f"10={checksum:03d}"

        return full_msg.encode()

    @classmethod
    def decode(cls, data: bytes) -> 'FIXMessage':
        """解码FIX消息"""
        msg_str = data.decode()
        fields = msg_str.split(cls.SOH)

        message = cls(FIXMsgType.HEARTBEAT)
        message.fields = {}

        for field in fields:
            if '=' in field:
                tag, value = field.split('=', 1)
                message.fields[int(tag)] = value

        # 设置消息类型
        msg_type_value = message.fields.get(35)
        if msg_type_value:
            for mt in FIXMsgType:
                if mt.value == msg_type_value:
                    message.msg_type = mt
                    break

        return message


class FIXSession:
    """FIX会话管理"""

    def __init__(
        self,
        host: str,
        port: int,
        sender_comp_id: str,
        target_comp_id: str,
        begin_string: str = 'FIX.4.4',
        heartbeat_interval: int = 30
    ):
        self.host = host
        self.port = port
        self.sender_comp_id = sender_comp_id
        self.target_comp_id = target_comp_id
        self.begin_string = begin_string
        self.heartbeat_interval = heartbeat_interval

        self.seq_num_out = 1
        self.seq_num_in = 1
        self.connected = False

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.on_message: Optional[Callable[[FIXMessage], None]] = None

    async def connect(self):
        """建立连接"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        # 发送Logon消息
        logon_msg = FIXMessage(FIXMsgType.LOGON)
        logon_msg.set_field(98, '0')  # EncryptMethod = None
        logon_msg.set_field(108, str(self.heartbeat_interval))  # HeartBtInt

        await self.send_message(logon_msg)

        # 启动心跳和接收任务
        asyncio.create_task(self.heartbeat_loop())
        asyncio.create_task(self.receive_loop())

        self.connected = True
        logger.info(f"FIX session connected: {self.sender_comp_id} -> {self.target_comp_id}")

    async def disconnect(self):
        """断开连接"""
        if self.connected:
            logout_msg = FIXMessage(FIXMsgType.LOGOUT)
            await self.send_message(logout_msg)

            self.writer.close()
            await self.writer.wait_closed()
            self.connected = False
            logger.info("FIX session disconnected")

    async def send_message(self, message: FIXMessage):
        """发送消息"""
        data = message.encode(
            self.begin_string,
            self.sender_comp_id,
            self.target_comp_id,
            self.seq_num_out
        )

        self.writer.write(data)
        await self.writer.drain()

        self.seq_num_out += 1

        logger.debug(f"Sent: {data.decode()}")

    async def heartbeat_loop(self):
        """心跳循环"""
        while self.connected:
            await asyncio.sleep(self.heartbeat_interval)

            heartbeat = FIXMessage(FIXMsgType.HEARTBEAT)
            await self.send_message(heartbeat)

    async def receive_loop(self):
        """接收循环"""
        buffer = b''

        while self.connected:
            try:
                data = await self.reader.read(4096)
                if not data:
                    break

                buffer += data

                # 解析消息 (以SOH+10=结尾)
                while b'\x0110=' in buffer:
                    # 找到消息结束位置
                    end_idx = buffer.find(b'\x0110=')
                    if end_idx == -1:
                        break

                    # 找到完整消息 (包括checksum)
                    msg_end = buffer.find(self.FIXMessage.SOH.encode(), end_idx + 4)
                    if msg_end == -1:
                        break

                    msg_data = buffer[:msg_end]
                    buffer = buffer[msg_end:]

                    # 解析消息
                    message = FIXMessage.decode(msg_data)

                    # 处理消息
                    await self.handle_message(message)

            except Exception as e:
                logger.error(f"Error in receive loop: {e}")

    async def handle_message(self, message: FIXMessage):
        """处理收到的消息"""
        msg_type = message.fields.get(35)

        if msg_type == FIXMsgType.HEARTBEAT.value:
            pass  # 心跳回复，无需处理

        elif msg_type == FIXMsgType.TEST_REQUEST.value:
            # 回复心跳
            test_req_id = message.get_field(112)
            heartbeat = FIXMessage(FIXMsgType.HEARTBEAT)
            if test_req_id:
                heartbeat.set_field(112, test_req_id)
            await self.send_message(heartbeat)

        elif msg_type == FIXMsgType.LOGON.value:
            logger.info("Logon confirmed")

        elif msg_type == FIXMsgType.LOGOUT.value:
            logger.info("Logout received")
            self.connected = False

        else:
            # 调用用户回调
            if self.on_message:
                self.on_message(message)

        # 更新入站序列号
        seq_num = message.get_field(34)
        if seq_num:
            self.seq_num_in = int(seq_num)

    def create_new_order(
        self,
        cl_ord_id: str,
        symbol: str,
        side: FIXSide,
        ord_type: FIXOrdType,
        quantity: int,
        price: Optional[Decimal] = None
    ) -> FIXMessage:
        """创建新订单消息"""
        msg = FIXMessage(FIXMsgType.NEW_ORDER_SINGLE)

        msg.set_field(11, cl_ord_id)           # ClOrdID
        msg.set_field(55, symbol)              # Symbol
        msg.set_field(54, side.value)          # Side
        msg.set_field(40, ord_type.value)      # OrdType
        msg.set_field(38, str(quantity))       # OrderQty
        msg.set_field(59, '0')                 # TimeInForce = Day

        if price and ord_type in [FIXOrdType.LIMIT, FIXOrdType.STOP_LIMIT]:
            msg.set_field(44, str(price))      # Price

        return msg


# 使用示例
async def fix_example():
    """FIX协议使用示例"""
    session = FIXSession(
        host='fix.example.com',
        port=5001,
        sender_comp_id='QUANT_CLIENT',
        target_comp_id='BROKER_SERVER',
        begin_string='FIX.4.4',
        heartbeat_interval=30
    )

    def on_message(msg: FIXMessage):
        print(f"Received: {msg.msg_type}")

    session.on_message = on_message

    await session.connect()

    # 发送订单
    order = session.create_new_order(
        cl_ord_id='ORDER001',
        symbol='AAPL',
        side=FIXSide.BUY,
        ord_type=FIXOrdType.LIMIT,
        quantity=100,
        price=Decimal('150.50')
    )

    await session.send_message(order)

    # 保持运行
    await asyncio.sleep(60)

    await session.disconnect()


if __name__ == '__main__':
    asyncio.run(fix_example())
```

---

*完整文档版本: v1.0*
*文档字数: 25,000+*
*代码行数: 800+*


## 附录E: 风险管理系统

### E.1 实时风险监控

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时风险管理系统

功能:
- 实时仓位监控
- 风险限额检查
- 熔断机制
- 预警通知
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Callable, Set
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    NORMAL = "normal"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int = 0
    avg_price: Decimal = Decimal('0')
    market_price: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')
    
    @property
    def market_value(self) -> Decimal:
        return Decimal(self.quantity) * self.market_price
    
    @property
    def exposure(self) -> Decimal:
        return abs(self.market_value)


@dataclass
class RiskEvent:
    """风险事件"""
    timestamp: datetime
    risk_type: str
    level: RiskLevel
    message: str
    details: Dict = field(default_factory=dict)


class RiskLimit:
    """风险限额配置"""
    
    def __init__(
        self,
        max_position_value: Decimal = Decimal('1000000'),
        max_position_pct: Decimal = Decimal('0.2'),
        max_drawdown_pct: Decimal = Decimal('0.05'),
        max_daily_loss: Decimal = Decimal('50000'),
        max_concentration: Decimal = Decimal('0.3'),
        max_leverage: Decimal = Decimal('2.0'),
        max_order_size: int = 10000,
        max_open_orders: int = 100
    ):
        self.max_position_value = max_position_value
        self.max_position_pct = max_position_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_daily_loss = max_daily_loss
        self.max_concentration = max_concentration
        self.max_leverage = max_leverage
        self.max_order_size = max_order_size
        self.max_open_orders = max_open_orders


class RiskManager:
    """风险管理器"""
    
    def __init__(
        self,
        limits: RiskLimit,
        initial_capital: Decimal = Decimal('1000000')
    ):
        self.limits = limits
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        
        self.positions: Dict[str, Position] = {}
        self.open_orders: Dict[str, Dict] = {}
        self.daily_pnl = Decimal('0')
        self.last_reset_date = datetime.now().date()
        
        self.circuit_breaker_triggered = False
        self.trading_enabled = True
        
        self.on_risk_event: Optional[Callable[[RiskEvent], None]] = None
    
    def update_position(self, symbol: str, quantity: int, avg_price: Decimal, market_price: Decimal):
        """更新持仓"""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)
        
        pos = self.positions[symbol]
        pos.quantity = quantity
        pos.avg_price = avg_price
        pos.market_price = market_price
        pos.unrealized_pnl = Decimal(quantity) * (market_price - avg_price)
    
    def check_all_limits(self) -> List[RiskEvent]:
        """检查所有风险限额"""
        events = []
        
        # 检查每日重置
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.daily_pnl = Decimal('0')
            self.last_reset_date = today
        
        # 1. 检查总仓位
        total_position = sum(pos.exposure for pos in self.positions.values())
        if total_position > self.limits.max_position_value:
            events.append(RiskEvent(
                timestamp=datetime.now(),
                risk_type="TOTAL_POSITION_LIMIT",
                level=RiskLevel.DANGER,
                message=f"Total position {total_position} exceeds limit {self.limits.max_position_value}",
                details={'current': float(total_position), 'limit': float(self.limits.max_position_value)}
            ))
        
        # 2. 检查单一品种集中度
        if total_position > 0:
            for symbol, pos in self.positions.items():
                concentration = pos.exposure / total_position
                if concentration > self.limits.max_concentration:
                    events.append(RiskEvent(
                        timestamp=datetime.now(),
                        risk_type="CONCENTRATION_LIMIT",
                        level=RiskLevel.WARNING,
                        message=f"{symbol} concentration {concentration:.2%} exceeds limit",
                        details={'symbol': symbol, 'concentration': float(concentration)}
                    ))
        
        # 3. 检查回撤
        current_equity = self.current_capital + sum(pos.unrealized_pnl for pos in self.positions.values())
        if current_equity > self.peak_capital:
            self.peak_capital = current_equity
        
        drawdown = (self.peak_capital - current_equity) / self.peak_capital if self.peak_capital > 0 else Decimal('0')
        if drawdown > self.limits.max_drawdown_pct:
            events.append(RiskEvent(
                timestamp=datetime.now(),
                risk_type="DRAWDOWN_LIMIT",
                level=RiskLevel.CRITICAL,
                message=f"Drawdown {drawdown:.2%} exceeds limit {self.limits.max_drawdown_pct:.2%}",
                details={'drawdown': float(drawdown), 'peak': float(self.peak_capital)}
            ))
            self.trigger_circuit_breaker("Excessive drawdown")
        
        # 4. 检查日亏损
        if self.daily_pnl < -self.limits.max_daily_loss:
            events.append(RiskEvent(
                timestamp=datetime.now(),
                risk_type="DAILY_LOSS_LIMIT",
                level=RiskLevel.CRITICAL,
                message=f"Daily loss {self.daily_pnl} exceeds limit {self.limits.max_daily_loss}",
                details={'daily_pnl': float(self.daily_pnl)}
            ))
            self.trigger_circuit_breaker("Daily loss limit exceeded")
        
        # 5. 检查杠杆
        if total_position > 0:
            leverage = total_position / self.current_capital
            if leverage > self.limits.max_leverage:
                events.append(RiskEvent(
                    timestamp=datetime.now(),
                    risk_type="LEVERAGE_LIMIT",
                    level=RiskLevel.DANGER,
                    message=f"Leverage {leverage:.2f}x exceeds limit {self.limits.max_leverage}x",
                    details={'leverage': float(leverage)}
                ))
        
        # 触发回调
        for event in events:
            if self.on_risk_event:
                self.on_risk_event(event)
            logger.warning(f"Risk event: {event.risk_type} - {event.message}")
        
        return events
    
    def check_order(self, symbol: str, side: str, quantity: int, price: Decimal) -> Optional[RiskEvent]:
        """检查订单是否违反风险限额"""
        if not self.trading_enabled:
            return RiskEvent(
                timestamp=datetime.now(),
                risk_type="TRADING_DISABLED",
                level=RiskLevel.CRITICAL,
                message="Trading is currently disabled"
            )
        
        # 检查订单大小
        if quantity > self.limits.max_order_size:
            return RiskEvent(
                timestamp=datetime.now(),
                risk_type="ORDER_SIZE_LIMIT",
                level=RiskLevel.WARNING,
                message=f"Order size {quantity} exceeds limit {self.limits.max_order_size}",
                details={'quantity': quantity, 'limit': self.limits.max_order_size}
            )
        
        # 检查未结订单数
        if len(self.open_orders) >= self.limits.max_open_orders:
            return RiskEvent(
                timestamp=datetime.now(),
                risk_type="MAX_ORDERS_LIMIT",
                level=RiskLevel.WARNING,
                message=f"Open orders {len(self.open_orders)} exceeds limit {self.limits.max_open_orders}"
            )
        
        return None
    
    def trigger_circuit_breaker(self, reason: str):
        """触发熔断机制"""
        self.circuit_breaker_triggered = True
        self.trading_enabled = False
        
        logger.critical(f"Circuit breaker triggered: {reason}")
        
        if self.on_risk_event:
            self.on_risk_event(RiskEvent(
                timestamp=datetime.now(),
                risk_type="CIRCUIT_BREAKER",
                level=RiskLevel.CRITICAL,
                message=f"Trading halted: {reason}"
            ))
    
    def reset_circuit_breaker(self):
        """重置熔断"""
        self.circuit_breaker_triggered = False
        self.trading_enabled = True
        logger.info("Circuit breaker reset, trading resumed")
    
    def add_order(self, order_id: str, order_details: Dict):
        """添加未结订单"""
        self.open_orders[order_id] = order_details
    
    def remove_order(self, order_id: str):
        """移除未结订单"""
        self.open_orders.pop(order_id, None)
    
    def get_risk_report(self) -> Dict:
        """获取风险报告"""
        total_position = sum(pos.exposure for pos in self.positions.values())
        current_equity = self.current_capital + sum(pos.unrealized_pnl for pos in self.positions.values())
        drawdown = (self.peak_capital - current_equity) / self.peak_capital if self.peak_capital > 0 else Decimal('0')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'capital': {
                'initial': float(self.initial_capital),
                'current': float(self.current_capital),
                'equity': float(current_equity),
                'peak': float(self.peak_capital)
            },
            'risk_metrics': {
                'drawdown': float(drawdown),
                'daily_pnl': float(self.daily_pnl),
                'total_position': float(total_position),
                'leverage': float(total_position / self.current_capital) if self.current_capital > 0 else 0,
                'open_orders': len(self.open_orders)
            },
            'positions': [
                {
                    'symbol': pos.symbol,
                    'quantity': pos.quantity,
                    'avg_price': float(pos.avg_price),
                    'market_price': float(pos.market_price),
                    'unrealized_pnl': float(pos.unrealized_pnl)
                }
                for pos in self.positions.values()
            ],
            'status': {
                'trading_enabled': self.trading_enabled,
                'circuit_breaker_triggered': self.circuit_breaker_triggered
            }
        }


# 使用示例
if __name__ == '__main__':
    limits = RiskLimit(
        max_position_value=Decimal('100000'),
        max_drawdown_pct=Decimal('0.05'),
        max_daily_loss=Decimal('10000')
    )
    
    risk_mgr = RiskManager(limits, initial_capital=Decimal('100000'))
    
    def on_risk(event: RiskEvent):
        print(f"[{event.level.value.upper()}] {event.risk_type}: {event.message}")
    
    risk_mgr.on_risk_event = on_risk
    
    # 模拟持仓更新
    risk_mgr.update_position('AAPL', 100, Decimal('150'), Decimal('155'))
    risk_mgr.update_position('GOOGL', 50, Decimal('2800'), Decimal('2750'))
    
    # 检查风险
    events = risk_mgr.check_all_limits()
    
    # 获取报告
    report = risk_mgr.get_risk_report()
    print("\nRisk Report:")
    print(report)
```

### E.2 压力测试框架

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压力测试框架

场景:
- 市场闪崩 (Flash Crash)
- 流动性枯竭
- 连锁爆仓
- 极端波动
"""

import numpy as np
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Tuple
import pandas as pd


@dataclass
class StressScenario:
    """压力测试场景"""
    name: str
    description: str
    price_shock: float          # 价格冲击幅度 (-0.1 = -10%)
    volatility_multiplier: float
    correlation_spike: float
    liquidity_factor: float     # 流动性因子 (0.5 = 流动性减半)


class StressTester:
    """压力测试器"""
    
    SCENARIOS = [
        StressScenario(
            name="Flash Crash",
            description="市场闪崩，价格在短时间内急剧下跌",
            price_shock=-0.1,
            volatility_multiplier=3.0,
            correlation_spike=0.8,
            liquidity_factor=0.3
        ),
        StressScenario(
            name="Liquidity Crisis",
            description="流动性枯竭，买卖价差急剧扩大",
            price_shock=-0.05,
            volatility_multiplier=2.0,
            correlation_spike=0.6,
            liquidity_factor=0.1
        ),
        StressScenario(
            name="Volatility Spike",
            description="波动率突然飙升",
            price_shock=0.0,
            volatility_multiplier=4.0,
            correlation_spike=0.5,
            liquidity_factor=0.5
        ),
        StressScenario(
            name="Correlation Breakdown",
            description="资产相关性突然上升",
            price_shock=-0.03,
            volatility_multiplier=1.5,
            correlation_spike=0.95,
            liquidity_factor=0.7
        )
    ]
    
    def __init__(self, positions: Dict[str, Dict], current_prices: Dict[str, Decimal]):
        self.positions = positions
        self.current_prices = current_prices
        self.historical_returns = {}  # 历史收益率数据
    
    def run_stress_test(self, scenario: StressScenario) -> Dict:
        """运行单一压力测试场景"""
        results = {
            'scenario': scenario.name,
            'description': scenario.description,
            'positions': [],
            'total_pnl': Decimal('0'),
            'var_95': 0.0,
            'max_drawdown': 0.0
        }
        
        total_exposure = Decimal('0')
        
        for symbol, pos in self.positions.items():
            current_price = self.current_prices.get(symbol, Decimal('0'))
            quantity = pos.get('quantity', 0)
            
            # 应用价格冲击
            shocked_price = current_price * Decimal(1 + scenario.price_shock)
            
            # 计算P&L
            pnl = Decimal(quantity) * (shocked_price - current_price)
            
            # 应用流动性折扣 (难以平仓)
            liquidity_discount = Decimal(1 - scenario.liquidity_factor)
            realized_pnl = pnl * liquidity_discount
            
            position_result = {
                'symbol': symbol,
                'quantity': quantity,
                'current_price': float(current_price),
                'shocked_price': float(shocked_price),
                'unrealized_pnl': float(pnl),
                'realized_pnl': float(realized_pnl),
                'liquidity_discount': float(liquidity_discount)
            }
            
            results['positions'].append(position_result)
            results['total_pnl'] += realized_pnl
            total_exposure += abs(Decimal(quantity) * current_price)
        
        # 计算风险指标
        if total_exposure > 0:
            results['max_drawdown'] = float(-results['total_pnl'] / total_exposure)
        
        return results
    
    def run_all_scenarios(self) -> List[Dict]:
        """运行所有压力测试场景"""
        return [self.run_stress_test(scenario) for scenario in self.SCENARIOS]
    
    def calculate_var(self, confidence: float = 0.95) -> Dict[str, float]:
        """计算VaR (风险价值)"""
        var_results = {}
        
        for symbol, returns in self.historical_returns.items():
            if len(returns) > 0:
                var = np.percentile(returns, (1 - confidence) * 100)
                var_results[symbol] = var
        
        return var_results
    
    def generate_report(self) -> str:
        """生成压力测试报告"""
        results = self.run_all_scenarios()
        
        report = []
        report.append("=" * 60)
        report.append("STRESS TEST REPORT")
        report.append("=" * 60)
        
        for result in results:
            report.append(f"\nScenario: {result['scenario']}")
            report.append(f"Description: {result['description']}")
            report.append(f"Total P&L: ${result['total_pnl']:,.2f}")
            report.append(f"Max Drawdown: {result['max_drawdown']:.2%}")
            report.append("-" * 40)
        
        return "\n".join(report)


# 使用示例
if __name__ == '__main__':
    positions = {
        'AAPL': {'quantity': 100},
        'GOOGL': {'quantity': 50},
        'MSFT': {'quantity': 200}
    }
    
    prices = {
        'AAPL': Decimal('150'),
        'GOOGL': Decimal('2800'),
        'MSFT': Decimal('300')
    }
    
    tester = StressTester(positions, prices)
    
    # 运行压力测试
    report = tester.generate_report()
    print(report)
```

---

## 附录F: 常见问题解答 (FAQ)

### F.1 性能相关问题

**Q: TimescaleDB与原生PostgreSQL的性能差异有多大？**

A: 在时序数据场景下，TimescaleDB相比原生PostgreSQL有以下优势：
- 写入性能提升10-100倍（通过批量插入和分区优化）
- 查询性能提升1000倍+（通过分区裁剪和BRIN索引）
- 存储空间节省90%+（通过数据压缩）

**Q: 如何处理每秒百万级的写入压力？**

A: 建议采用以下策略：
1. 使用UNLOGGED表存储热数据，减少WAL写入开销
2. 批量COPY插入代替单条INSERT
3. 异步写入 + 内存缓冲
4. 分区策略：按天分区，避免单表过大
5. 使用连接池，避免频繁创建连接

**Q: 查询历史数据时响应慢怎么办？**

A: 优化建议：
1. 使用BRIN索引代替B-tree索引（时序数据）
2. 启用TimescaleDB的continuous aggregates预计算K线
3. 压缩历史数据（7天前自动压缩）
4. 将极冷数据归档到对象存储
5. 使用并行查询

### F.2 数据质量问题

**Q: 如何处理行情数据中的异常值？**

A: 数据清洗策略：
```python
# 价格异常检测
def detect_price_anomaly(price, prev_price, max_change_pct=0.1):
    if prev_price == 0:
        return False
    change_pct = abs(price - prev_price) / prev_price
    return change_pct > max_change_pct

# 成交量异常检测
def detect_volume_anomaly(volume, avg_volume, threshold=5):
    return volume > avg_volume * threshold
```

**Q: 如何处理交易所数据延迟或丢失？**

A: 数据回补机制：
1. 实时检测序列号断层
2. 自动请求历史数据回补
3. 使用多个行情源冗余备份
4. 本地缓存最近1小时数据用于回补

### F.3 部署运维问题

**Q: 如何保证7x24小时不间断服务？**

A: 高可用架构：
```
主库 (Master) --同步复制--> 备库 (Standby)
   |                               |
   +---- 自动故障切换 (Patroni) ---+
```

**Q: 数据库备份策略应该如何设计？**

A: 推荐策略：
- 实时：WAL归档到对象存储
- 每日：逻辑备份 (pg_dump)
- 每周：全量物理备份
- 保留期：本地3天，云端30天

### F.4 策略开发问题

**Q: 如何避免策略回测中的未来函数？**

A: 注意事项：
1. 只在当前K线收盘后使用当前K线数据
2. 使用shift(1)获取上一周期数据
3. 避免在计算中使用当前周期的未来信息
4. 回测时严格模拟实盘延迟

**Q: 滑点如何合理估计？**

A: 滑点模型：
```python
def estimate_slippage(order_size, avg_daily_volume, volatility):
    # 基于订单规模和市场冲击
    participation_rate = order_size / avg_daily_volume
    base_slippage = 0.001  # 1个基点
    
    # 规模因子
    size_factor = 1 + participation_rate * 10
    
    # 波动率因子
    vol_factor = 1 + volatility * 100
    
    return base_slippage * size_factor * vol_factor
```

---

## 附录G: 术语表

| 术语 | 英文 | 说明 |
|-----|------|------|
| 逐笔成交 | Tick Data | 每一笔成交的详细记录 |
| 订单簿 | Order Book | 所有未成交委托的集合 |
| K线 | Candlestick | 时间序列的价格聚合数据 |
| 限价单 | Limit Order | 指定价格的委托单 |
| 市价单 | Market Order | 以当前最优价成交的委托单 |
| 滑点 | Slippage | 预期成交价与实际成交价的差异 |
| 回撤 | Drawdown | 从峰值到谷底的资金回落 |
| 夏普比率 | Sharpe Ratio | 风险调整后收益指标 |
| 波动率 | Volatility | 价格变动的标准差 |
| 流动性 | Liquidity | 资产买卖的难易程度 |
| 熔断 | Circuit Breaker | 市场剧烈波动时的暂停交易机制 |
| 对冲 | Hedge | 降低风险的交易策略 |
| 杠杆 | Leverage | 借入资金进行投资的比例 |
| 保证金 | Margin | 维持头寸所需的抵押资金 |
| 强平 | Liquidation | 强制平仓 |
| 连续聚合 | Continuous Aggregate | TimescaleDB的实时预计算功能 |
| 超表 | Hypertable | TimescaleDB的分区表 |
| 块范围索引 | BRIN Index | 适合时序数据的轻量索引 |

---

## 附录H: 参考架构对比

### H.1 TimescaleDB vs kdb+

| 特性 | TimescaleDB | kdb+ |
|-----|-------------|------|
| 许可证 | Apache 2.0 (开源) | 商业软件 |
| 学习曲线 | 低 (标准SQL) | 高 (q语言) |
| 写入延迟 | 1-10ms | <100μs |
| 查询延迟 | 10-100ms | <1ms |
| 压缩比 | 10:1 | 20:1 |
| 社区生态 | 丰富 | 专业 |
| 成本 | 低 | 高 |

### H.2 不同数据库选型建议

| 场景 | 推荐方案 |
|-----|---------|
| 超高频交易 (<10μs) | kdb+, FPGA |
| 高频交易 (10μs-1ms) | QuestDB, ClickHouse |
| 中频交易 (1ms-10ms) | TimescaleDB |
| 低频分析 (10ms+) | PostgreSQL + TimescaleDB |
| 大数据离线分析 | ClickHouse, Apache Doris |

---

## 总结与展望

本文档全面介绍了基于PostgreSQL + TimescaleDB的高频交易数据分析平台的构建方法。从架构设计到代码实现，从性能优化到生产部署，覆盖了量化交易系统的全生命周期。

### 核心优势

1. **开源免费**: 基于PostgreSQL生态，无商业授权费用
2. **标准SQL**: 降低团队学习成本，易于维护
3. **成熟稳定**: 经过生产环境验证的数据库内核
4. **生态丰富**: 丰富的工具链和社区支持
5. **扩展灵活**: 支持从单机到分布式集群的平滑扩展

### 未来演进方向

1. **实时计算增强**: 集成Flink/Kafka Streams进行流处理
2. **AI/ML集成**: 引入机器学习模型进行预测和策略优化
3. **云原生部署**: Kubernetes + 云存储的弹性架构
4. **多模态数据**: 支持新闻、社交媒体等非结构化数据
5. **全球化部署**: 多Region数据同步和就近访问

### 资源汇总

- 源代码仓库: https://github.com/example/hft-platform
- 问题反馈: https://github.com/example/hft-platform/issues
- 技术讨论: Discord社区
- 商业支持: support@example.com

---

**文档信息**  
版本: v1.0  
最后更新: 2024-01-01  
作者: Quant Development Team  
许可: MIT License

**文档统计**  
总字数: 25,000+  
总代码行: 1,500+  
示例数量: 30+  
图表数量: 10+

---

*本文档采用知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议进行许可。*
