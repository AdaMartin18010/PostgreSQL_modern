# 监控SQL验证脚本
# 使用方法: .\validate_monitoring_sql.ps1

Write-Host "🔍 PostgreSQL监控SQL验证工具" -ForegroundColor Cyan
Write-Host "=" * 60

# 配置
$PGHOST = "localhost"
$PGPORT = "5432"
$PGUSER = "postgres"
$PGPASSWORD = "666110"
$PGDATABASE = "postgres"

# 设置环境变量
$env:PGPASSWORD = $PGPASSWORD

# 查找psql
$psqlPath = $null
$searchPaths = @(
    "C:\Program Files\PostgreSQL\17\bin\psql.exe",
    "C:\Program Files\PostgreSQL\16\bin\psql.exe",
    "C:\PostgreSQL\bin\psql.exe"
)

foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $psqlPath = $path
        Write-Host "✅ Found psql: $psqlPath" -ForegroundColor Green
        break
    }
}

if (-not $psqlPath) {
    Write-Host "❌ psql not found. Please add PostgreSQL bin directory to PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "手动查找psql.exe:" -ForegroundColor Yellow
    Write-Host 'Get-ChildItem "C:\Program Files" -Recurse -Filter "psql.exe" -ErrorAction SilentlyContinue'
    exit 1
}

# 测试连接
Write-Host ""
Write-Host "🔌 Testing PostgreSQL connection..." -ForegroundColor Cyan
& $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -c "SELECT version();" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cannot connect to PostgreSQL" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Connected to PostgreSQL" -ForegroundColor Green

# 读取监控SQL文件
$sqlFile = "09_deployment_ops\monitoring_queries.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Host "❌ SQL file not found: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📊 Validating monitoring queries from $sqlFile" -ForegroundColor Cyan
Write-Host "=" * 60

# 提取并验证SQL查询
$content = Get-Content $sqlFile -Raw
$queries = $content -split '-- (?=\d+\.)' | Where-Object { $_ -match '^\d+\.' }

$totalQueries = 0
$successQueries = 0
$failedQueries = 0

foreach ($query in $queries) {
    # 提取查询标题
    if ($query -match '^(\d+\.\s+[^\n]+)') {
        $title = $matches[1].Trim()
        $totalQueries++
        
        # 提取SQL语句 (在SELECT和;之间)
        if ($query -match '(SELECT[\s\S]+?;)') {
            $sql = $matches[1].Trim()
            
            Write-Host ""
            Write-Host "[$totalQueries] $title" -ForegroundColor Yellow
            
            # 执行查询（限制返回1行以加速）
            try {
                $result = & $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d $PGDATABASE -t -c "$sql LIMIT 1" 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✅ Success" -ForegroundColor Green
                    $successQueries++
                } else {
                    Write-Host "  ❌ Failed: $result" -ForegroundColor Red
                    $failedQueries++
                }
            } catch {
                Write-Host "  ❌ Error: $_" -ForegroundColor Red
                $failedQueries++
            }
        }
    }
}

# 总结
Write-Host ""
Write-Host "=" * 60
Write-Host "📊 Validation Summary" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host "Total queries:   $totalQueries"
Write-Host "✅ Success:      $successQueries ($([math]::Round($successQueries/$totalQueries*100, 1))%)" -ForegroundColor Green
Write-Host "❌ Failed:       $failedQueries ($([math]::Round($failedQueries/$totalQueries*100, 1))%)" -ForegroundColor Red

if ($failedQueries -eq 0) {
    Write-Host ""
    Write-Host "🎉 All monitoring queries validated successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some queries failed. Please check the errors above." -ForegroundColor Yellow
}

