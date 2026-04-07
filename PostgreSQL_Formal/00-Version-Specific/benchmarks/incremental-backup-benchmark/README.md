# 增量备份基准测试 (PG17)

## 测试目标

验证 PostgreSQL 17 中增量备份 (Incremental Backup) 特性的性能和存储效率，对比全量备份与增量备份在时间、空间和恢复速度方面的差异。

## PG17 新特性

PostgreSQL 17 引入了原生增量备份支持：

- 基于 WAL summarization 的增量备份
- 只备份变化的数据块，大幅减少备份时间和存储需求
- 支持基于任意先前备份的增量备份
- 简化的备份和恢复工作流

## 测试环境要求

### 硬件配置

- CPU: 4核+
- RAM: 16GB+
- 磁盘:
  - 数据盘: 2TB+ SSD
  - 备份盘: 500GB+ (用于存储备份)

### 软件要求

- Docker 20.10+
- PostgreSQL 17 镜像
- pgBackRest 或内置增量备份工具

## 测试场景

### 场景 1: 1TB 数据库备份对比

- 全量备份 vs 增量备份时间对比
- 存储空间占用对比
- 备份期间对数据库性能的影响

### 场景 2: 不同变化量的增量备份

- 5% 数据变化
- 10% 数据变化
- 20% 数据变化
- 对比各场景下的备份效率

### 场景 3: 恢复性能测试

- 全量备份恢复时间
- 增量备份恢复时间
- 多层级增量备份恢复

### 场景 4: WAL Summarization 影响

- 启用/禁用 WAL summarization 的对比
- WAL 生成量监控
- 对正常业务的影响

## 预期结果

| 指标 | 全量备份 | 5% 增量 | 10% 增量 | 20% 增量 |
|------|----------|---------|----------|----------|
| 备份时间 (1TB) | ~2小时 | ~6分钟 | ~12分钟 | ~24分钟 |
| 存储空间 | 1TB | 50GB | 100GB | 200GB |
| 恢复时间 | ~2小时 | ~2小时10分 | ~2小时15分 | ~2小时25分 |

## 目录结构

```
incremental-backup-benchmark/
├── README.md              # 本文件
├── docker-compose.yml     # Docker 环境配置
├── setup.sql             # 测试数据准备
├── test-backup.sh        # 主测试脚本
├── pgbackrest.conf       # pgBackRest 配置
└── results-template.md   # 结果记录模板
```

## 快速开始

```bash
# 1. 启动测试环境
docker-compose up -d

# 2. 准备测试数据
./prepare-data.sh

# 3. 运行基准测试
./test-backup.sh

# 4. 查看结果
cat results/backup-benchmark-report.md
```

## 测试参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| DB_SIZE_GB | 测试数据库大小 | 100 |
| CHANGE_PERCENT | 数据变化百分比 | 5,10,20 |
| BACKUP_TOOL | 备份工具选择 | pgbackrest / builtin |
| COMPRESSION | 压缩算法 | zstd |

## 注意事项

1. **磁盘空间**: 确保有足够的磁盘空间存储备份
2. **网络带宽**: 如果测试远程备份，考虑网络因素
3. **WAL 保留**: 增量备份需要保留足够的 WAL 文件
4. **权限设置**: 确保 PostgreSQL 用户有备份目录的写权限
