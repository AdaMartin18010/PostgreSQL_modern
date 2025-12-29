# PowerShell脚本：系统性地修复所有文档
# 1. 添加目录
# 2. 完善主题与子主题的序号编号
# 3. 检查内容充实度
# 4. 修复导航链接

$basePath = "E:\_src\PostgreSQL_modern\Integrate\07-多模型数据库\PostgreSQL-18新特性\异步I-O机制"
Set-Location $basePath

# 获取所有章节文件夹（排除归档、脚本等）
$chapterFolders = Get-ChildItem -Directory | Where-Object { 
    $_.Name -match "^\d{2}-" -and 
    $_.Name -notmatch "归档|split|fix" 
} | Sort-Object Name

Write-Host "找到 $($chapterFolders.Count) 个章节文件夹需要处理`n" -ForegroundColor Green

$processedCount = 0
$fixedCount = 0
$needsContentCount = 0

foreach ($folder in $chapterFolders) {
    $readmePath = Join-Path $folder.FullName "README.md"
    
    if (-not (Test-Path $readmePath)) {
        Write-Host "⚠️  跳过: $($folder.Name) (无README.md)" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "处理: $($folder.Name)" -ForegroundColor Cyan
    
    $content = Get-Content $readmePath -Raw -Encoding UTF8
    $lines = Get-Content $readmePath -Encoding UTF8
    $originalContent = $content
    $modified = $false
    
    # 1. 检查并添加目录
    if ($content -notmatch "##\s*📑\s*目录|##\s*目录|##\s*Contents") {
        Write-Host "  → 添加目录..." -ForegroundColor Yellow
        
        # 提取所有三级标题（###）
        $tocItems = @()
        $lineNum = 0
        foreach ($line in $lines) {
            $lineNum++
            if ($line -match "^###\s+(.+)$") {
                $fullTitle = $matches[1].Trim()
                # 保留完整标题用于显示
                $displayTitle = $fullTitle
                # 生成锚点（基于完整标题，Markdown会自动处理）
                # GitHub风格的锚点：小写、空格变横线、移除特殊字符
                $anchor = $fullTitle -replace "\s+", "-" -replace "[^\w\u4e00-\u9fa5-]", ""
                $anchor = $anchor.ToLower()
                # 移除序号部分用于锚点（如果存在）
                $anchor = $anchor -replace "^\d+-\d+(-\d+)?-", ""
                $tocItems += "  - [$displayTitle](#$anchor)"
            }
        }
        
        if ($tocItems.Count -gt 0) {
            # 找到章节标题后的位置插入目录
            $tocMarkdown = "## 📑 目录`n`n" + ($tocItems -join "`n") + "`n`n---`n`n"
            
            # 在章节标题后插入目录
            if ($content -match "(^##\s+\d+\.\s+.+?\n\n---)") {
                $content = $content -replace "(^##\s+\d+\.\s+.+?\n\n---)", "`$1`n`n$tocMarkdown"
                $modified = $true
            } elseif ($content -match "(^##\s+\d+\.\s+.+?\n)") {
                $content = $content -replace "(^##\s+\d+\.\d+\.\s+.+?\n)", "`$1`n$tocMarkdown"
                $modified = $true
            }
        }
    }
    
    # 2. 统一子标题编号格式
    # 提取章节号
    $chapterNum = 0
    if ($content -match "(?m)^##\s+(\d+)\.\s+") {
        $chapterNum = [int]$matches[1]
    }
    
    if ($chapterNum -gt 0) {
        # 重新编号所有子标题
        $newLines = @()
        $subSectionNum = 0
        $subSubSectionNum = 0
        $lastWasSubSubSection = $false
        
        foreach ($line in $lines) {
            if ($line -match "^###\s+(.+)$") {
                $title = $matches[1].Trim()
                
                # 检查是否已有正确的章节编号
                if ($title -match "^$chapterNum\.(\d+)(\.(\d+))?\s+(.+)$") {
                    # 已有正确章节号，检查格式是否标准
                    $existingSub = [int]$matches[1]
                    if ($matches[2]) {
                        $existingSubSub = [int]$matches[3]
                        $titleText = $matches[4]
                        $newLines += "### $chapterNum.$existingSub.$existingSubSub $titleText"
                        $subSectionNum = $existingSub
                        $subSubSectionNum = $existingSubSub
                        $lastWasSubSubSection = $true
                    } else {
                        $titleText = $matches[4]
                        $newLines += "### $chapterNum.$existingSub $titleText"
                        $subSectionNum = $existingSub
                        $subSubSectionNum = 0
                        $lastWasSubSubSection = $false
                    }
                } elseif ($title -match "^(\d+)\.(\d+)(\.(\d+))?\s+(.+)$") {
                    # 有其他章节号，需要修正
                    $wrongChapter = [int]$matches[1]
                    $sub = [int]$matches[2]
                    if ($matches[3]) {
                        $subSub = [int]$matches[3]
                        $titleText = $matches[5]
                        $newLines += "### $chapterNum.$sub.$subSub $titleText"
                        $subSectionNum = $sub
                        $subSubSectionNum = $subSub
                        $lastWasSubSubSection = $true
                    } else {
                        $titleText = $matches[5]
                        $newLines += "### $chapterNum.$sub $titleText"
                        $subSectionNum = $sub
                        $subSubSectionNum = 0
                        $lastWasSubSubSection = $false
                    }
                    $modified = $true
                } else {
                    # 无编号，需要添加
                    # 判断是否是子子标题（通过检查前一行是否是子标题）
                    if ($lastWasSubSubSection -or ($subSubSectionNum -gt 0)) {
                        # 继续子子标题编号
                        $subSubSectionNum++
                        $newLines += "### $chapterNum.$subSectionNum.$subSubSectionNum $title"
                        $lastWasSubSubSection = $true
                    } else {
                        # 新的子标题
                        $subSectionNum++
                        $subSubSectionNum = 0
                        $newLines += "### $chapterNum.$subSectionNum $title"
                        $lastWasSubSubSection = $false
                    }
                    $modified = $true
                }
            } else {
                $newLines += $line
            }
        }
        
        if ($modified) {
            $content = ($newLines -join "`n")
            Write-Host "  → 统一子标题编号..." -ForegroundColor Yellow
        }
    }
    
    # 3. 检查内容充实度
    $lineCount = $lines.Count
    $codeBlockCount = ($content | Select-String -Pattern "```" -AllMatches).Matches.Count / 2
    $hasSubsections = ($content | Select-String -Pattern "^###" -AllMatches).Matches.Count
    
    if ($lineCount -lt 100 -and $codeBlockCount -lt 2 -and $hasSubsections -lt 3) {
        Write-Host "  ⚠️  内容较少: $lineCount 行, $codeBlockCount 代码块, $hasSubsections 子章节" -ForegroundColor Yellow
        $needsContentCount++
    }
    
    # 4. 添加导航链接（如果不存在）- 暂时跳过，后续手动处理
    # 导航链接功能暂时禁用，避免PowerShell编码问题
    
    # 保存修改
    if ($modified) {
        Set-Content -Path $readmePath -Value $content -Encoding UTF8 -NoNewline
        $fixedCount++
        Write-Host "  [OK] Fixed" -ForegroundColor Green
    } else {
        Write-Host "  [OK] No changes needed" -ForegroundColor Gray
    }
    
    $processedCount++
}

Write-Host ""
$separator = "=" * 60
Write-Host $separator -ForegroundColor Green
Write-Host "处理完成统计" -ForegroundColor Green
Write-Host $separator -ForegroundColor Green
Write-Host "总处理数: $processedCount" -ForegroundColor Cyan
Write-Host "已修复数: $fixedCount" -ForegroundColor Green
Write-Host "需要补充内容: $needsContentCount" -ForegroundColor Yellow
Write-Host $separator -ForegroundColor Green
