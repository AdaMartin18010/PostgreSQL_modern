param(
  [string]$DbUrl = "postgresql://postgres:postgres@localhost:5432/postgres",
  [int]$DurationSec = 60,
  [int]$Clients = 16,
  [int]$Threads = 4,
  [string]$OutCsv = "pgbench_result.csv"
)

$tempReport = Join-Path $PSScriptRoot "pgbench_raw.txt"

Write-Host "运行 pgbench..."
pgbench -n -M prepared -T $DurationSec -c $Clients -j $Threads -f (Join-Path $PSScriptRoot "pgbench_hotkeys.sql") $DbUrl | Tee-Object -FilePath $tempReport | Out-Host

Write-Host "解析结果到 CSV..."
$content = Get-Content $tempReport
$tps = ($content | Select-String -Pattern "excluding connections establishing" | ForEach-Object { ($_ -split " ")[-2] })
$lat99 = ($content | Select-String -Pattern "99th percentile" | ForEach-Object { ($_ -split " ")[-2] })
$lat95 = ($content | Select-String -Pattern "95th percentile" | ForEach-Object { ($_ -split " ")[-2] })
$lat50 = ($content | Select-String -Pattern "50th percentile" | ForEach-Object { ($_ -split " ")[-2] })

"scenario,tps,p50_ms,p95_ms,p99_ms,start_ts,end_ts,notes" | Out-File -Encoding utf8 $OutCsv
"hotkeys,$tps,$lat50,$lat95,$lat99,$(Get-Date -Format o),$(Get-Date -Format o),clients=$Clients;threads=$Threads;dur=$DurationSec" | Add-Content -Encoding utf8 $OutCsv

Write-Host "完成：$OutCsv"

