# 从 pgbench 输出中提取关键指标 (PowerShell 版本)
# 使用方法: .\extract_pgbench_metrics.ps1 -InputFile "result.log"

param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile
)

if (-not (Test-Path $InputFile)) {
    Write-Host "错误: 文件不存在: $InputFile" -ForegroundColor Red
    exit 1
}

Write-Host "=== pgbench 指标提取 ===" -ForegroundColor Cyan
Write-Host "文件: $InputFile"
Write-Host "----------------------------------------"

$content = Get-Content $InputFile -Raw

# 提取 TPS
$tpsMatch = $content | Select-String -Pattern "tps = ([\d.]+)" | Where-Object { $_.Line -notmatch "including connections" }
$tps = if ($tpsMatch) { $tpsMatch.Matches[0].Groups[1].Value } else { "N/A" }

# 提取平均延迟
$latencyAvgMatch = $content | Select-String -Pattern "latency average = ([\d.]+)"
$latencyAvg = if ($latencyAvgMatch) { $latencyAvgMatch.Matches[0].Groups[1].Value } else { "N/A" }

# 提取延迟标准差
$latencyStddevMatch = $content | Select-String -Pattern "latency stddev = ([\d.]+)"
$latencyStddev = if ($latencyStddevMatch) { $latencyStddevMatch.Matches[0].Groups[1].Value } else { "N/A" }

# 提取事务数
$transactionsMatch = $content | Select-String -Pattern "transactions actually processed: (\d+)"
$transactions = if ($transactionsMatch) { $transactionsMatch.Matches[0].Groups[1].Value } else { "N/A" }

# 提取连接时间
$connTimeMatch = $content | Select-String -Pattern "initial connection time = ([\d.]+)"
$connTime = if ($connTimeMatch) { $connTimeMatch.Matches[0].Groups[1].Value } else { "N/A" }

Write-Host "TPS: $tps"
Write-Host "平均延迟: $latencyAvg ms"
Write-Host "延迟标准差: $latencyStddev ms"
Write-Host "事务数: $transactions"
Write-Host "连接时间: $connTime ms"
Write-Host ""

# 生成 CSV 格式输出
Write-Host "=== CSV 格式 ===" -ForegroundColor Cyan
Write-Host "TPS,平均延迟(ms),延迟标准差(ms),事务数,连接时间(ms)"
Write-Host "$tps,$latencyAvg,$latencyStddev,$transactions,$connTime"
