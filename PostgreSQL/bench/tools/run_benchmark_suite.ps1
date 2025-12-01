# 基准测试套件自动化脚本 (PowerShell 版本)
# 使用方法: .\run_benchmark_suite.ps1 -DatabaseName "pgbench_test" [options]

param(
    [string]$DatabaseName = "pgbench_test",
    [int]$ScaleFactor = 100,
    [int]$Duration = 300,
    [int]$Clients = 32,
    [int]$Threads = 32,
    [string]$OutputDir = ".\results"
)

$ErrorActionPreference = "Stop"

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultDir = Join-Path $OutputDir $Timestamp

Write-Host "=== 基准测试套件 ===" -ForegroundColor Green
Write-Host "数据库: $DatabaseName"
Write-Host "Scale Factor: $ScaleFactor"
Write-Host "持续时间: $Duration 秒"
Write-Host "并发数: $Clients"
Write-Host "输出目录: $ResultDir"
Write-Host ""

# 创建输出目录
New-Item -ItemType Directory -Force -Path $ResultDir | Out-Null

# 检查数据库是否存在
$dbExists = psql -lqt 2>$null | Select-String -Pattern "^\s*$DatabaseName\s"
if (-not $dbExists) {
    Write-Host "数据库 $DatabaseName 不存在，正在创建..." -ForegroundColor Yellow
    createdb $DatabaseName
}

# 检查数据是否已初始化
$null = psql -d $DatabaseName -c "\d pgbench_accounts" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "初始化测试数据..." -ForegroundColor Yellow
    pgbench -i -s $ScaleFactor $DatabaseName
} else {
    Write-Host "测试数据已存在" -ForegroundColor Green
}

# 测试 1: 基线测试
Write-Host "运行基线测试..." -ForegroundColor Green
$baselineLog = Join-Path $ResultDir "baseline.log"
pgbench -c $Clients -j $Threads -T $Duration -r -l $DatabaseName *> $baselineLog

# 移动延迟日志
Get-ChildItem -Filter "pgbench_log.*" -ErrorAction SilentlyContinue | 
    Move-Item -Destination $ResultDir -ErrorAction SilentlyContinue

# 测试 2: 只读测试
Write-Host "运行只读测试..." -ForegroundColor Green
$readonlyLog = Join-Path $ResultDir "readonly.log"
pgbench -S -c $Clients -j $Threads -T $Duration -r -l $DatabaseName *> $readonlyLog

# 测试 3: 只写测试
Write-Host "运行只写测试..." -ForegroundColor Green
$writeonlyLog = Join-Path $ResultDir "writeonly.log"
pgbench -N -c $Clients -j $Threads -T $Duration -r -l $DatabaseName *> $writeonlyLog

# 分析结果
Write-Host "分析测试结果..." -ForegroundColor Green
$toolsDir = Join-Path $PSScriptRoot "."

foreach ($logfile in Get-ChildItem -Path $ResultDir -Filter "*.log") {
    $basename = [System.IO.Path]::GetFileNameWithoutExtension($logfile.Name)
    $metricsFile = Join-Path $ResultDir "${basename}_metrics.txt"
    
    & (Join-Path $toolsDir "extract_pgbench_metrics.ps1") -InputFile $logfile.FullName *> $metricsFile
}

# 分析延迟日志
$logFiles = Get-ChildItem -Path $ResultDir -Filter "pgbench_log.*" -ErrorAction SilentlyContinue
if ($logFiles) {
    $latencyFile = Join-Path $ResultDir "latency_analysis.txt"
    $logFileNames = $logFiles | ForEach-Object { $_.FullName }
    & (Join-Path $toolsDir "analyze_pgbench_log.ps1") -LogFiles $logFileNames *> $latencyFile
}

# 生成摘要报告
Write-Host "生成摘要报告..." -ForegroundColor Green
$summaryFile = Join-Path $ResultDir "summary.txt"
@"
=== 基准测试摘要 ===
测试时间: $(Get-Date)
数据库: $DatabaseName
Scale Factor: $ScaleFactor
测试持续时间: $Duration 秒
并发数: $Clients
工作线程数: $Threads

测试结果文件:
- baseline.log: 基线测试
- readonly.log: 只读测试
- writeonly.log: 只写测试
- latency_analysis.txt: 延迟分析

"@ | Out-File -FilePath $summaryFile -Encoding UTF8

Write-Host "=== 测试完成 ===" -ForegroundColor Green
Write-Host "结果保存在: $ResultDir"
Write-Host "查看摘要: Get-Content $summaryFile"
