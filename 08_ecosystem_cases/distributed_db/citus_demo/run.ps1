param(
  [string]$DbUrl = "postgresql://postgres:postgres@localhost:5432/postgres"
)

Write-Host "[1/3] 启动容器..."
docker compose up -d | Out-Host

Write-Host "[2/3] 等待协调节点就绪..."
for ($i=0; $i -lt 60; $i++) {
  $null = docker compose exec -T coordinator pg_isready -h localhost -p 5432 2>$null
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 2
}

Write-Host "[3/3] 执行初始化脚本..."
psql $DbUrl -f .\init.sql | Out-Host

Write-Host "完成。可运行示例查询验证路由与重分布。"

