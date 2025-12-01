# 分析 pgbench 日志文件，提取延迟分位数 (PowerShell 版本)
# 使用方法: .\analyze_pgbench_log.ps1 -LogFiles "pgbench_log.*"

param(
    [Parameter(Mandatory=$true)]
    [string[]]$LogFiles
)

Write-Host "=== pgbench 日志分析 ===" -ForegroundColor Cyan
Write-Host ""

foreach ($logfile in $LogFiles) {
    if (-not (Test-Path $logfile)) {
        Write-Host "警告: 文件不存在: $logfile" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "文件: $logfile" -ForegroundColor Green
    Write-Host "----------------------------------------"
    
    # 读取文件并提取延迟值（最后一列）
    $delays = Get-Content $logfile | ForEach-Object {
        $parts = $_ -split '\s+'
        if ($parts.Count -gt 0) {
            $last = $parts[-1]
            if ($last -match '^\d+(\.\d+)?$') {
                [double]$last
            }
        }
    } | Where-Object { $_ -ne $null } | Sort-Object
    
    if ($delays.Count -eq 0) {
        Write-Host "未找到有效的延迟数据" -ForegroundColor Yellow
        Write-Host ""
        continue
    }
    
    $total = $delays.Count
    
    # 计算分位数
    $tp50 = $delays[[Math]::Floor($total * 0.5)]
    $tp95 = $delays[[Math]::Floor($total * 0.95)]
    $tp99 = $delays[[Math]::Floor($total * 0.99)]
    $tp999 = $delays[[Math]::Floor($total * 0.999)]
    
    # 计算平均值
    $avg = ($delays | Measure-Object -Average).Average
    
    # 最小值和最大值
    $min = $delays[0]
    $max = $delays[-1]
    
    Write-Host "总事务数: $total"
    Write-Host "平均延迟: $([Math]::Round($avg, 2)) ms"
    Write-Host "最小延迟: $min ms"
    Write-Host "最大延迟: $max ms"
    Write-Host "TP50: $tp50 ms"
    Write-Host "TP95: $tp95 ms"
    Write-Host "TP99: $tp99 ms"
    Write-Host "TP99.9: $tp999 ms"
    Write-Host ""
}

Write-Host "=== 分析完成 ===" -ForegroundColor Cyan
