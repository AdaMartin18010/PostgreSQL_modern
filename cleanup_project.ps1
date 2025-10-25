# PostgreSQL_modern 项目清理脚本
# 执行日期：2025-10-25
# 用途：清理根目录的临时文件，保持项目整洁

param(
    [switch]$DryRun,      # 仅显示将要执行的操作，不实际执行
    [switch]$Archive,     # 归档而不是删除
    [switch]$DeleteAll    # 直接删除（谨慎使用）
)

Write-Host "=" -ForegroundColor Cyan
Write-Host "PostgreSQL_modern 项目清理工具" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在正确的目录
if (-not (Test-Path "README.md")) {
    Write-Host "错误：请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 定义要清理的文件列表
$filesToClean = @{
    "进度报告" = @(
        "CONTINUOUS_IMPROVEMENT_PROGRESS_2025_10_03.md",
        "CONTINUOUS_PROGRESS_2025_10_25.md",
        "CONTINUOUS_PROGRESS_FINAL_DELIVERABLES.md",
        "CONTINUOUS_PROGRESS_FINAL_SUMMARY_2025_10_03.md",
        "CONTINUOUS_PROGRESS_ROUND_10_COMPLETE.md",
        "CONTINUOUS_PROGRESS_ROUND_8_COMPLETE.md",
        "EXECUTION_SUMMARY_2025_10_25.md",
        "FINAL_EXECUTION_SUMMARY.md",
        "FINAL_PROGRESS_COMPLETE.md",
        "FINAL_PUSH_SUMMARY_2025_10_25.md",
        "LATEST_PROGRESS_SUMMARY.md",
        "PUSH_COMPLETE_2025_10_25.md",
        "WEEK_2_COMPLETED_SUMMARY.md",
        "WEEK_3_ACTION_PLAN.md",
        "WEEK_3_CONTINUOUS_PROGRESS_SUMMARY.md",
        "WEEK_3_FINAL_SUMMARY.md",
        "WEEK_3_PROGRESS_UPDATE.md",
        "PROJECT_STATUS_2025_10_25.md",
        "PROJECT_FINAL_SUMMARY_2025_10_04.md",
        "LINK_FIXES_2025_10_25.md",
        "FIX_SUMMARY.md",
        "FIXES_COMPLETED_2025_10_03.md"
    )
    "验证报告" = @(
        "EXECUTE_VALIDATION_NOW.md",
        "QUALITY_CHECK_RESULTS_2025_10_25.md",
        "QUALITY_SUMMARY_2025_10_25.md",
        "QUALITY_VALIDATION_PLAN.md",
        "QUALITY_VALIDATION_QUICK_START.md",
        "QUALITY_VALIDATION_REPORT_UPDATED.md",
        "QUALITY_VALIDATION_REPORT.md",
        "QUICK_START_VALIDATION.md",
        "VALIDATION_EXECUTION_COMPLETE.md",
        "VALIDATION_EXECUTION_PROGRESS.md",
        "VALIDATION_REPORT_2025_10_03.md",
        "VALIDATION_RESULTS_FINAL.md"
    )
    "完成庆祝" = @(
        "PROJECT_100_PERCENT_COMPLETE.md",
        "PROJECT_COMPLETION_CERTIFICATE.md",
        "PROJECT_COMPLETION_REPORT.md",
        "PROJECT_DELIVERABLES_CHECKLIST.md",
        "PROJECT_EXCELLENCE_BADGE.md",
        "WEEK_3_BADGE.md",
        "WEEK_3_COMPLETION_CERTIFICATE.md",
        "PROJECT_IMPROVEMENT_REPORT.md"
    )
    "临时输出" = @(
        "link_check_output.txt",
        "validation_output.txt"
    )
    "过渡文档" = @(
        "ACTIONABLE_IMPROVEMENT_PLAN_2025_10.md",
        "CRITICAL_EVALUATION_SUMMARY_2025_10.md",
        "HANDOVER_DOCUMENT.md",
        "NEXT_STEPS_QUICK_GUIDE.md",
        "PENDING_TASKS_EXECUTION_GUIDE.md",
        "PROJECT_ROADMAP.md",
        "PROJECT_STATUS_DASHBOARD.md",
        "SETUP_PYTHON_ENVIRONMENT.md"
    )
}

# 维护脚本（移动到tools目录）
$scriptsToMove = @(
    "execute_pending_tasks.ps1",
    "fix_markdown_links.ps1",
    "setup_test_environment.ps1",
    "validate_monitoring_sql.ps1"
)

# 统计
$totalFiles = 0
$existingFiles = 0
$movedFiles = 0
$deletedFiles = 0

# 创建归档目录（如果需要）
if ($Archive -and -not $DryRun) {
    $archiveDir = "archive_2025_10"
    if (-not (Test-Path $archiveDir)) {
        New-Item -ItemType Directory -Path $archiveDir | Out-Null
        Write-Host "✓ 创建归档目录: $archiveDir" -ForegroundColor Green
    }
}

# 创建tools/maintenance目录
if (-not $DryRun) {
    $toolsMaintenanceDir = "tools/maintenance"
    if (-not (Test-Path $toolsMaintenanceDir)) {
        New-Item -ItemType Directory -Path $toolsMaintenanceDir -Force | Out-Null
        Write-Host "✓ 创建目录: $toolsMaintenanceDir" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "扫描要清理的文件..." -ForegroundColor Yellow
Write-Host ""

# 处理文件
foreach ($category in $filesToClean.Keys) {
    Write-Host "[$category]" -ForegroundColor Cyan
    foreach ($file in $filesToClean[$category]) {
        $totalFiles++
        if (Test-Path $file) {
            $existingFiles++
            if ($DryRun) {
                Write-Host "  [预览] $file" -ForegroundColor Yellow
            }
            elseif ($DeleteAll) {
                Remove-Item $file -Force
                Write-Host "  [删除] $file" -ForegroundColor Red
                $deletedFiles++
            }
            elseif ($Archive) {
                Move-Item $file "archive_2025_10/" -Force
                Write-Host "  [归档] $file" -ForegroundColor Green
                $movedFiles++
            }
            else {
                Write-Host "  [存在] $file" -ForegroundColor White
            }
        }
    }
    Write-Host ""
}

# 处理脚本文件
Write-Host "[维护脚本]" -ForegroundColor Cyan
foreach ($script in $scriptsToMove) {
    if (Test-Path $script) {
        $totalFiles++
        $existingFiles++
        if ($DryRun) {
            Write-Host "  [预览] $script -> tools/maintenance/" -ForegroundColor Yellow
        }
        else {
            Move-Item $script "tools/maintenance/" -Force
            Write-Host "  [移动] $script -> tools/maintenance/" -ForegroundColor Green
            $movedFiles++
        }
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "统计信息" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "扫描文件总数: $totalFiles"
Write-Host "实际存在文件: $existingFiles" -ForegroundColor $(if ($existingFiles -gt 0) { "Yellow" } else { "Green" })
if (-not $DryRun) {
    Write-Host "已归档文件: $movedFiles" -ForegroundColor Green
    Write-Host "已删除文件: $deletedFiles" -ForegroundColor Red
}
Write-Host ""

# 显示建议
if ($DryRun) {
    Write-Host "这是预览模式。要执行清理，请运行：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .\cleanup_project.ps1 -Archive    # 归档文件（推荐）" -ForegroundColor Cyan
    Write-Host "  .\cleanup_project.ps1 -DeleteAll  # 直接删除（谨慎）" -ForegroundColor Red
    Write-Host ""
}
elseif ($Archive) {
    Write-Host "✓ 清理完成！文件已归档到 archive_2025_10/" -ForegroundColor Green
    Write-Host ""
    Write-Host "后续步骤：" -ForegroundColor Yellow
    Write-Host "1. 检查项目是否正常" 
    Write-Host "2. 如果确认无误，可以删除归档目录：" 
    Write-Host "   Remove-Item archive_2025_10 -Recurse -Force" -ForegroundColor Gray
}
elseif ($DeleteAll) {
    Write-Host "✓ 清理完成！文件已删除" -ForegroundColor Green
}
else {
    Write-Host "请选择执行模式：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .\cleanup_project.ps1 -DryRun     # 预览模式" -ForegroundColor Cyan
    Write-Host "  .\cleanup_project.ps1 -Archive    # 归档模式（推荐）" -ForegroundColor Green
    Write-Host "  .\cleanup_project.ps1 -DeleteAll  # 删除模式（谨慎）" -ForegroundColor Red
}

Write-Host ""
Write-Host "清理分析报告: PROJECT_CLEANUP_ANALYSIS.md" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

