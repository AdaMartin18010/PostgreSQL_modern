# PostgreSQL测试环境配置脚本
# 使用方法: .\setup_test_environment.ps1

Write-Host "🚀 PostgreSQL测试环境配置工具" -ForegroundColor Cyan
Write-Host "=" * 60

# 配置
$PGHOST = "localhost"
$PGPORT = "5432"
$PGUSER = "postgres"
$PGPASSWORD = "666110"
$TEST_DB = "testdb"

# 设置环境变量
$env:PGPASSWORD = $PGPASSWORD

# 查找psql
$psqlPath = $null
$searchPaths = @(
    "C:\Program Files\PostgreSQL\17\bin\psql.exe",
    "C:\Program Files\PostgreSQL\16\bin\psql.exe",
    "C:\PostgreSQL\bin\psql.exe"
)

Write-Host "🔍 Searching for psql.exe..." -ForegroundColor Cyan
foreach ($path in $searchPaths) {
    if (Test-Path $path) {
        $psqlPath = $path
        Write-Host "✅ Found psql: $psqlPath" -ForegroundColor Green
        break
    }
}

if (-not $psqlPath) {
    Write-Host "❌ psql not found in common locations" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔎 Trying to find psql.exe..." -ForegroundColor Yellow
    
    # 搜索Program Files
    $found = Get-ChildItem "C:\Program Files" -Filter "psql.exe" -Recurse -ErrorAction SilentlyContinue | 
             Where-Object {$_.FullName -like "*PostgreSQL*"} | 
             Select-Object -First 1
    
    if ($found) {
        $psqlPath = $found.FullName
        Write-Host "✅ Found psql: $psqlPath" -ForegroundColor Green
    } else {
        Write-Host "❌ Cannot find psql.exe" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please manually locate psql.exe and add it to PATH" -ForegroundColor Yellow
        exit 1
    }
}

# 测试连接
Write-Host ""
Write-Host "🔌 Testing PostgreSQL connection..." -ForegroundColor Cyan
$testResult = & $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "SELECT version();" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cannot connect to PostgreSQL" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Connected to PostgreSQL successfully" -ForegroundColor Green

# 检查testdb是否已存在
Write-Host ""
Write-Host "📦 Checking if test database exists..." -ForegroundColor Cyan
$dbExists = & $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='$TEST_DB';" 2>&1

if ($dbExists -match "1") {
    Write-Host "⚠️  Database '$TEST_DB' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/N)"
    
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host "🗑️  Dropping database '$TEST_DB'..." -ForegroundColor Yellow
        & $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "DROP DATABASE $TEST_DB;" 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database dropped" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to drop database" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✅ Using existing database" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Test environment is ready!" -ForegroundColor Green
        exit 0
    }
}

# 创建testdb
Write-Host ""
Write-Host "📦 Creating test database '$TEST_DB'..." -ForegroundColor Cyan
& $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d postgres -c "CREATE DATABASE $TEST_DB;" 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create database" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Database '$TEST_DB' created successfully" -ForegroundColor Green

# 创建测试配置文件
Write-Host ""
Write-Host "📝 Creating test configuration..." -ForegroundColor Cyan

$configDir = "tests\config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$configFile = "$configDir\database.yml"
$configContent = @"
# PostgreSQL Test Database Configuration
host: $PGHOST
port: $PGPORT
database: $TEST_DB
user: $PGUSER
password: "$PGPASSWORD"
sslmode: disable
"@

Set-Content -Path $configFile -Value $configContent -Encoding UTF8
Write-Host "✅ Configuration file created: $configFile" -ForegroundColor Green

# 测试连接到testdb
Write-Host ""
Write-Host "🔌 Testing connection to test database..." -ForegroundColor Cyan
$testConn = & $psqlPath -h $PGHOST -p $PGPORT -U $PGUSER -d $TEST_DB -c "SELECT 'Test connection successful' AS status;" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Test database connection successful" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot connect to test database" -ForegroundColor Red
    Write-Host "Error: $testConn" -ForegroundColor Red
    exit 1
}

# 总结
Write-Host ""
Write-Host "=" * 60
Write-Host "🎉 Test Environment Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "Database Details:" -ForegroundColor Cyan
Write-Host "  Host:     $PGHOST"
Write-Host "  Port:     $PGPORT"
Write-Host "  Database: $TEST_DB"
Write-Host "  User:     $PGUSER"
Write-Host "  Config:   $configFile"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run tests: cd tests && python scripts\run_all_tests.py"
Write-Host "  2. Or use validate_monitoring_sql.ps1 to test monitoring queries"
Write-Host ""

