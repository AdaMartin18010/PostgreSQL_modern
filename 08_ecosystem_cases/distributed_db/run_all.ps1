param(
  [ValidateSet("citus","skew","all")]
  [string]$Target = "all"
)

Write-Host "[0/4] 环境检查..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Error "未检测到 docker，请安装 Docker Desktop 并重试。"
  exit 1
}
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
  Write-Host "提示：未检测到 psql，某些本地初始化将跳过（容器内仍可执行）。"
}

function Invoke-CitusDemo {
  Write-Host "[1/4] 启动 Citus 演示..."
  Push-Location (Join-Path $PSScriptRoot "citus_demo")
  try {
    ./run.ps1
  } finally {
    Pop-Location
  }
}

function Invoke-SkewLoadgen {
  Write-Host "[2/4] 启动倾斜负载演示（pgbench hotkeys）..."
  Push-Location (Join-Path $PSScriptRoot "skew_loadgen")
  try {
    $dbUrl = "postgresql://postgres:postgres@localhost:5432/postgres"
    $duration = 30
    $clients = 16
    $threads = 4
    $outCsv = "pgbench_result.csv"
    ./run_pgbench.ps1 -DbUrl $dbUrl -DurationSec $duration -Clients $clients -Threads $threads -OutCsv $outCsv
  } finally {
    Pop-Location
  }
}

switch ($Target) {
  "citus" { Invoke-CitusDemo }
  "skew" { Invoke-SkewLoadgen }
  Default {
    Invoke-CitusDemo
    Invoke-SkewLoadgen
  }
}

Write-Host "[3/4] 如需多区域网络条件仿真，请在 Linux/WSL 运行："
Write-Host "  ./multi_region_demo/tc_setup.sh   # 注入延迟/抖动/丢包"
Write-Host "  ./multi_region_demo/tc_teardown.sh # 恢复网络"

Write-Host "[4/4] 完成。"


