# Markdown链接格式修复脚本
# 使用方法: .\fix_markdown_links.ps1

Write-Host "🔧 Markdown链接格式修复工具" -ForegroundColor Cyan
Write-Host "=" * 60

# 常见的链接格式问题及修复规则
$linkPatterns = @(
    # 规则1: 裸URL应该用尖括号包裹
    @{
        Pattern = '(?<!\[)(?<!<)(https?://[^\s\)\]]+)(?!>)(?!\))'
        Replacement = '<$1>'
        Description = "裸URL添加尖括号"
    },
    # 规则2: 修复空格问题
    @{
        Pattern = '\[([^\]]+)\]\s+\(([^\)]+)\)'
        Replacement = '[$1]($2)'
        Description = "移除]和(之间的空格"
    },
    # 规则3: 修复多余的尖括号
    @{
        Pattern = '\[([^\]]+)\]\(<(https?://[^>]+)>\)'
        Replacement = '[$1]($2)'
        Description = "移除URL周围的尖括号（在链接内）"
    }
)

# 获取所有markdown文件
$mdFiles = Get-ChildItem -Path . -Filter "*.md" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*\.venv\*" -and $_.FullName -notlike "*\node_modules\*" }

$totalFiles = $mdFiles.Count
$processedFiles = 0
$modifiedFiles = 0
$totalChanges = 0

Write-Host ""
Write-Host "📁 找到 $totalFiles 个Markdown文件" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $mdFiles) {
    $processedFiles++
    $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "")

    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        $originalContent = $content
        $fileChanges = 0

        # 应用所有修复规则
        foreach ($rule in $linkPatterns) {
            $matches = [regex]::Matches($content, $rule.Pattern)
            if ($matches.Count -gt 0) {
                $content = [regex]::Replace($content, $rule.Pattern, $rule.Replacement)
                $fileChanges += $matches.Count
            }
        }

        # 如果内容有变化，保存文件
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -NoNewline -Encoding UTF8 -ErrorAction Stop
            $modifiedFiles++
            $totalChanges += $fileChanges
            Write-Host "  ✅ $relativePath ($fileChanges 处修复)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ⚠️  跳过: $relativePath (错误: $_)" -ForegroundColor Yellow
    }

    # 显示进度
    if ($processedFiles % 10 -eq 0) {
        $percent = [math]::Round(($processedFiles / $totalFiles) * 100)
        Write-Host "  进度: $processedFiles/$totalFiles ($percent%)" -ForegroundColor Gray
    }
}

# 总结
Write-Host ""
Write-Host "=" * 60
Write-Host "📊 修复总结" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host "总文件数:   $totalFiles"
Write-Host "修改文件数: $modifiedFiles" -ForegroundColor $(if ($modifiedFiles -gt 0) { "Green" } else { "Gray" })
Write-Host "总修复次数: $totalChanges" -ForegroundColor $(if ($totalChanges -gt 0) { "Green" } else { "Gray" })

if ($modifiedFiles -eq 0) {
    Write-Host ""
    Write-Host "✨ 所有文件的链接格式都正确！" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "🎉 链接格式修复完成！" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 提示：修复的主要问题包括：" -ForegroundColor Yellow
Write-Host "  - 为裸URL添加尖括号"
Write-Host "  - 移除链接中的多余空格"
Write-Host "  - 清理不必要的尖括号"

