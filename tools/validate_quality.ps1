# PostgreSQL_modern 项目质量验证脚本 (PowerShell 版本)
# 用于 Windows 环境快速执行质量验证

param(
    [switch]$All,
    [switch]$Links,
    [switch]$Versions,
    [switch]$Refs,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "============================================================" -ForegroundColor Blue
    Write-Host ""
}

# 显示帮助信息
if ($Help) {
    Write-Host @"
PostgreSQL_modern 项目质量验证脚本

用法:
    .\tools\validate_quality.ps1 -All         # 运行所有验证
    .\tools\validate_quality.ps1 -Links       # 仅检查链接
    .\tools\validate_quality.ps1 -Versions    # 仅检查版本信息
    .\tools\validate_quality.ps1 -Refs        # 仅检查内部引用
    .\tools\validate_quality.ps1 -Help        # 显示帮助

示例:
    # 运行完整验证
    .\tools\validate_quality.ps1 -All

    # 仅检查外部链接
    .\tools\validate_quality.ps1 -Links
"@
    exit 0
}

# 获取项目根目录
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Header "PostgreSQL_modern 项目质量验证"
Write-Info "项目根目录: $ProjectRoot"

# 如果没有指定任何选项，默认运行所有
if (-not ($All -or $Links -or $Versions -or $Refs)) {
    $All = $true
}

# 检查 Python 环境
Write-Info "检查 Python 环境..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python 已安装: $pythonVersion"
} catch {
    Write-Error-Custom "Python 未安装或不在 PATH 中"
    Write-Info "请安装 Python 3.8+ 并添加到 PATH"
    exit 1
}

# 检查必要的 Python 包
Write-Info "检查 Python 依赖..."
$requiredPackages = @("requests")
foreach ($package in $requiredPackages) {
    $installed = python -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warning-Custom "$package 未安装，正在安装..."
        pip install $package
    }
}

# 调用 Python 脚本
$pythonScript = Join-Path $PSScriptRoot "validate_quality.py"

if (-not (Test-Path $pythonScript)) {
    Write-Error-Custom "找不到 validate_quality.py 脚本"
    exit 1
}

# 构建命令行参数
$args = @()
if ($All) { $args += "--all" }
if ($Links) { $args += "--links" }
if ($Versions) { $args += "--versions" }
if ($Refs) { $args += "--refs" }

Write-Info "执行验证脚本..."
Write-Host ""

# 切换到项目根目录并执行 Python 脚本
Push-Location $ProjectRoot
try {
    python $pythonScript @args
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Success "验证完成！"
    } else {
        Write-Host ""
        Write-Error-Custom "验证过程中出现错误"
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Info "查看详细报告: QUALITY_VALIDATION_REPORT.md"

