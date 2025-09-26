# 分布式数据库演示集（Citus / 多区域 / 倾斜负载）

## 环境要求

- Windows 10/11 或 Linux（WSL 亦可）
- Docker Desktop（或兼容的 Docker 环境）
- PowerShell 7+（Windows 已内置；或安装 `pwsh`）
- 可选：`psql` 客户端（便于在宿主机直接执行 SQL）

## 一键运行

使用 PowerShell 一键启动常用演示：

```powershell
.\08_ecosystem_cases\distributed_db\run_all.ps1            # 启动 Citus + 倾斜负载
.\08_ecosystem_cases\distributed_db\run_all.ps1 -Target citus  # 仅 Citus
.\08_ecosystem_cases\distributed_db\run_all.ps1 -Target skew   # 仅 倾斜负载（pgbench hotkeys）
```

- 如需模拟跨 Region 网络：在 Linux/WSL 执行：

```bash
./08_ecosystem_cases/distributed_db/multi_region_demo/tc_setup.sh
./08_ecosystem_cases/distributed_db/multi_region_demo/tc_teardown.sh
```

## Citus 演示

- 位置：`08_ecosystem_cases/distributed_db/citus_demo`
- 启动：

  ```powershell
  .\08_ecosystem_cases\distributed_db\citus_demo\run.ps1
  ```

- 内容：
  - `docker-compose.yml` 启动 1 协调 + 2 工作
  - `init.sql` 创建扩展、分布表与示例数据
  - 观察执行计划（路由 vs 重分布）参见目录内 `README.md`

## 倾斜负载演示（pgbench hotkeys）

- 位置：`08_ecosystem_cases/distributed_db/skew_loadgen`
- 运行：

  ```powershell
  .\08_ecosystem_cases\distributed_db\skew_loadgen\run_pgbench.ps1
  ```

- 输出：在当前目录生成 `pgbench_result.csv`，包含 TPS 与分位延迟

## 多区域网络条件仿真

- 位置：`08_ecosystem_cases/distributed_db/multi_region_demo`
- 用途：通过 `tc` 注入延迟/抖动/丢包，验证跨 Region 影响
- 执行（Linux/WSL）：

  ```bash
  ./tc_setup.sh   # 注入网络条件
  ./tc_teardown.sh# 恢复网络
  ```

## 故障排查

- Docker 未启动：请先启动 Docker Desktop，再重试脚本
- 端口冲突（5432）：修改 `docker-compose.yml` 中映射端口，或停止占用进程
- `psql` 不存在：可在容器内执行初始化，或安装客户端工具
- PowerShell 执行策略限制：使用管理员打开 PowerShell，执行：

  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

- WSL 缺少 `tc`：安装 `iproute2`（如 `sudo apt install iproute2`）

## 清理

- 停止并清理容器与网络（在 `citus_demo` 目录内）：

  ```powershell
  docker compose down -v
  ```
