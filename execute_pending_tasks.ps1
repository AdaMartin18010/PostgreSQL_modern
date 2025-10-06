# 待执行任务一键执行脚本
# PostgreSQL_modern Project - v1.0
# 创建日期：2025年10月4日

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║         🚀 PostgreSQL_modern 待执行任务向导 🚀                ║" -ForegroundColor Green
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 待执行任务清单：" -ForegroundColor Yellow
Write-Host "  1. 启动PostgreSQL服务 (1分钟)"
Write-Host "  2. 验证监控SQL (5分钟)"
Write-Host "  3. 配置测试数据库 (3分钟)"
Write-Host "  4. 运行测试套件 (10分钟)"
Write-Host "  5. 部署Grafana Dashboard (15分钟)"
Write-Host ""
Write-Host "⏱️  预计总时间：30-40分钟" -ForegroundColor Cyan
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "README.md")) {
    Write-Host "❌ 错误：请在项目根目录运行此脚本" -ForegroundColor Red
    Write-Host "   当前目录：$(Get-Location)" -ForegroundColor Yellow
    Write-Host "   正确目录：E:\_src\PostgreSQL_modern" -ForegroundColor Yellow
    exit 1
}

# 显示详细指南
Write-Host "📚 详细执行指南：" -ForegroundColor Cyan
Write-Host "   code PENDING_TASKS_EXECUTION_GUIDE.md" -ForegroundColor White
Write-Host ""

$choice = Read-Host "是否查看详细执行指南? (y/n)"
if ($choice -eq 'y') {
    code PENDING_TASKS_EXECUTION_GUIDE.md
    Write-Host ""
    Write-Host "✅ 已打开执行指南，请按照指南逐步执行" -ForegroundColor Green
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 任务1：启动PostgreSQL服务
# ============================================================
Write-Host "📌 任务1：启动PostgreSQL服务" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "是否启动PostgreSQL服务? (y/n/skip)"
if ($confirm -eq 'y') {
    Write-Host "🔍 检查PostgreSQL服务..." -ForegroundColor Cyan
    
    # 查找PostgreSQL服务
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($pgService) {
        Write-Host "✅ 找到服务：$($pgService.Name)" -ForegroundColor Green
        
        if ($pgService.Status -eq "Running") {
            Write-Host "✅ PostgreSQL服务已在运行中" -ForegroundColor Green
        } else {
            Write-Host "🔄 正在启动PostgreSQL服务..." -ForegroundColor Cyan
            try {
                Start-Service $pgService.Name -ErrorAction Stop
                Write-Host "✅ PostgreSQL服务启动成功" -ForegroundColor Green
            } catch {
                Write-Host "❌ 启动失败：$($_.Exception.Message)" -ForegroundColor Red
                Write-Host "💡 请尝试手动启动：services.msc" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "⚠️ 未找到PostgreSQL服务" -ForegroundColor Yellow
        Write-Host "💡 请手动启动PostgreSQL服务：" -ForegroundColor Cyan
        Write-Host "   1. 打开服务管理器：services.msc" -ForegroundColor White
        Write-Host "   2. 找到PostgreSQL服务并启动" -ForegroundColor White
    }
} elseif ($confirm -eq 'skip') {
    Write-Host "⏭️  跳过任务1" -ForegroundColor Yellow
} else {
    Write-Host "❌ 取消执行" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 任务2：验证监控SQL
# ============================================================
Write-Host "📌 任务2：验证监控SQL" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "是否验证监控SQL? (y/n/skip)"
if ($confirm -eq 'y') {
    Write-Host "🔍 检查psql可用性..." -ForegroundColor Cyan
    
    # 检查psql是否在PATH中
    $psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
    
    if (-not $psqlCmd) {
        Write-Host "⚠️ psql不在PATH中，正在搜索..." -ForegroundColor Yellow
        
        # 搜索常见路径
        $commonPaths = @(
            "C:\Program Files\PostgreSQL\17\bin",
            "C:\Program Files\PostgreSQL\16\bin",
            "C:\PostgreSQL\17\bin"
        )
        
        $psqlPath = $null
        foreach ($path in $commonPaths) {
            if (Test-Path "$path\psql.exe") {
                $psqlPath = $path
                break
            }
        }
        
        if ($psqlPath) {
            Write-Host "✅ 找到psql：$psqlPath" -ForegroundColor Green
            Write-Host "🔄 添加到PATH..." -ForegroundColor Cyan
            $env:PATH += ";$psqlPath"
        } else {
            Write-Host "❌ 未找到psql" -ForegroundColor Red
            Write-Host "💡 请手动添加PostgreSQL bin目录到PATH" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "⏭️  跳过任务2" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host ""
            # 继续下一个任务
            $confirm = 'skip'
        }
    }
    
    if ($confirm -eq 'y') {
        Write-Host "🔄 设置数据库密码..." -ForegroundColor Cyan
        $env:PGPASSWORD = "666110"
        
        Write-Host "🚀 运行监控SQL验证脚本..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path ".\validate_monitoring_sql.ps1") {
            .\validate_monitoring_sql.ps1
        } else {
            Write-Host "⚠️ 验证脚本不存在：validate_monitoring_sql.ps1" -ForegroundColor Yellow
            Write-Host "💡 请手动验证监控SQL" -ForegroundColor Cyan
        }
    }
} elseif ($confirm -eq 'skip') {
    Write-Host "⏭️  跳过任务2" -ForegroundColor Yellow
} else {
    Write-Host "❌ 取消执行" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 任务3：配置测试数据库
# ============================================================
Write-Host "📌 任务3：配置测试数据库" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "是否配置测试数据库? (y/n/skip)"
if ($confirm -eq 'y') {
    Write-Host "🔍 检查配置文件..." -ForegroundColor Cyan
    
    if (Test-Path "tests\config\database.yml") {
        Write-Host "✅ 配置文件已存在" -ForegroundColor Green
        $overwrite = Read-Host "是否重新配置? (y/n)"
        if ($overwrite -ne 'y') {
            Write-Host "⏭️  使用现有配置" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host ""
            # 继续下一个任务
            $confirm = 'skip'
        }
    }
    
    if ($confirm -eq 'y') {
        Write-Host "🚀 运行配置脚本..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path ".\setup_test_environment.ps1") {
            $env:PGPASSWORD = "666110"
            .\setup_test_environment.ps1
        } else {
            Write-Host "⚠️ 配置脚本不存在：setup_test_environment.ps1" -ForegroundColor Yellow
            Write-Host "💡 配置文件已存在，可以继续下一步" -ForegroundColor Cyan
        }
    }
} elseif ($confirm -eq 'skip') {
    Write-Host "⏭️  跳过任务3" -ForegroundColor Yellow
} else {
    Write-Host "❌ 取消执行" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 任务4：运行测试套件
# ============================================================
Write-Host "📌 任务4：运行测试套件" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "是否运行测试套件? (y/n/skip)"
if ($confirm -eq 'y') {
    Write-Host "🔍 检查Python环境..." -ForegroundColor Cyan
    
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        Write-Host "✅ Python虚拟环境存在" -ForegroundColor Green
        Write-Host "🔄 激活虚拟环境..." -ForegroundColor Cyan
        .\.venv\Scripts\Activate.ps1
        
        Write-Host "🚀 运行测试套件..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path "tests\scripts\run_all_tests.py") {
            Push-Location tests
            python scripts/run_all_tests.py --verbose
            Pop-Location
            
            Write-Host ""
            Write-Host "📊 测试报告位置：tests\reports\test_results.html" -ForegroundColor Cyan
            $openReport = Read-Host "是否打开测试报告? (y/n)"
            if ($openReport -eq 'y') {
                Start-Process "tests\reports\test_results.html"
            }
        } else {
            Write-Host "⚠️ 测试脚本不存在：tests\scripts\run_all_tests.py" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Python虚拟环境不存在" -ForegroundColor Red
        Write-Host "💡 请先配置Python环境" -ForegroundColor Yellow
    }
} elseif ($confirm -eq 'skip') {
    Write-Host "⏭️  跳过任务4" -ForegroundColor Yellow
} else {
    Write-Host "❌ 取消执行" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 任务5：部署Grafana Dashboard
# ============================================================
Write-Host "📌 任务5：部署Grafana Dashboard" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Grafana Dashboard部署需要手动执行以下步骤：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  安装Grafana" -ForegroundColor Yellow
Write-Host "   choco install grafana" -ForegroundColor White
Write-Host "   或访问：https://grafana.com/grafana/download" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  启动Grafana服务" -ForegroundColor Yellow
Write-Host "   Start-Service Grafana" -ForegroundColor White
Write-Host ""
Write-Host "3️⃣  访问Grafana" -ForegroundColor Yellow
Write-Host "   浏览器打开：http://localhost:3000" -ForegroundColor White
Write-Host "   默认账号：admin / admin" -ForegroundColor White
Write-Host ""
Write-Host "4️⃣  配置PostgreSQL数据源" -ForegroundColor Yellow
Write-Host "   Host: localhost:5432" -ForegroundColor White
Write-Host "   Database: postgres" -ForegroundColor White
Write-Host "   User: postgres" -ForegroundColor White
Write-Host "   Password: 666110" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  导入Dashboard" -ForegroundColor Yellow
Write-Host "   导入文件：09_deployment_ops\grafana_dashboard.json" -ForegroundColor White
Write-Host ""

$openGuide = Read-Host "是否打开Grafana快速启动指南? (y/n)"
if ($openGuide -eq 'y') {
    code 09_deployment_ops\GRAFANA_QUICK_START.md
    Write-Host "✅ 已打开快速启动指南" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# 执行完成总结
# ============================================================
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║              🎉 任务执行向导完成！🎉                          ║" -ForegroundColor Green
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "📊 执行总结：" -ForegroundColor Yellow
Write-Host ""

# 检查各项任务状态
$pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "  ✅ PostgreSQL服务运行中" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  PostgreSQL服务未运行" -ForegroundColor Yellow
}

if (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "  ✅ psql可用" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  psql不在PATH中" -ForegroundColor Yellow
}

if (Test-Path "tests\config\database.yml") {
    Write-Host "  ✅ 测试数据库配置完成" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  测试数据库配置缺失" -ForegroundColor Yellow
}

$grafanaService = Get-Service -Name "Grafana" -ErrorAction SilentlyContinue
if ($grafanaService -and $grafanaService.Status -eq "Running") {
    Write-Host "  ✅ Grafana服务运行中" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Grafana未安装或未运行" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 相关文档：" -ForegroundColor Cyan
Write-Host "  • 详细执行指南：PENDING_TASKS_EXECUTION_GUIDE.md" -ForegroundColor White
Write-Host "  • 项目完成报告：PROJECT_100_PERCENT_COMPLETE.md" -ForegroundColor White
Write-Host "  • 快速使用指南：QUICK_USE_GUIDE.md" -ForegroundColor White
Write-Host ""

Write-Host "🎯 下一步：" -ForegroundColor Yellow
Write-Host "  1. 完成未完成的任务" -ForegroundColor White
Write-Host "  2. 查看测试报告：tests\reports\test_results.html" -ForegroundColor White
Write-Host "  3. 访问Grafana Dashboard：http://localhost:3000" -ForegroundColor White
Write-Host "  4. 开始学习PostgreSQL 17：code 00_overview\README.md" -ForegroundColor White
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎊 感谢使用PostgreSQL_modern项目！" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
