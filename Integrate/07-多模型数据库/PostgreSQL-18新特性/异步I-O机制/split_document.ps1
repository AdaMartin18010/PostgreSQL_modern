# PowerShell脚本：拆分PostgreSQL异步I/O文档
# 将大文档按章节拆分为独立文件

$sourceFile = "..\异步I-O机制.md"
$lines = Get-Content $sourceFile

# 找到所有章节
$chapters = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match "^##\s+(\d+)\.\s+(.+)$") {
        $chapters += [PSCustomObject]@{
            Line = $i + 1
            Number = [int]$matches[1]
            Title = $matches[2].Trim()
        }
    }
}

# 添加文档结束标记
$chapters += [PSCustomObject]@{
    Line = $lines.Count + 1
    Number = 999
    Title = "文档结束"
}

Write-Host "找到 $($chapters.Count - 1) 个章节"

# 章节文件夹映射
$folderMap = @{
    1 = "01-概述"
    2 = "02-技术原理"
    3 = "03-核心特性"
    4 = "04-架构设计"
    5 = "05-使用指南"
    6 = "06-性能分析"
    7 = "07-配置优化"
    8 = "08-实际应用场景"
    9 = "09-最佳实践"
    10 = "10-监控和诊断"
    11 = "11-迁移指南"
    12 = "12-性能调优检查清单"
    13 = "13-与其他特性集成"
    14 = "14-常见问题FAQ"
    15 = "15-安全与高可用"
    16 = "16-性能测试工具"
    17 = "17-容器化部署"
    18 = "18-CICD集成"
    19 = "19-高级性能优化"
    20 = "20-生产环境案例"
    21 = "21-数据库对比"
    22 = "22-未来发展趋势"
    23 = "23-快速参考指南"
    24 = "24-文档总结索引"
    25 = "25-性能模型理论"
    26 = "26-社区案例"
    27 = "27-版本兼容性"
    28 = "28-实战技巧"
    29 = "29-实用工具"
    30 = "30-可视化图表"
    31 = "31-实战演练"
    32 = "32-错误解决方案"
    33 = "33-源码分析"
    34 = "34-深度集成"
    35 = "35-成熟案例"
    36 = "36-参考资料"
}

# 提取并保存每个章节
for ($i = 0; $i -lt $chapters.Count - 1; $i++) {
    $chapter = $chapters[$i]
    $nextChapter = $chapters[$i + 1]
    
    $folderName = if ($folderMap.ContainsKey($chapter.Number)) {
        $folderMap[$chapter.Number]
    } else {
        "$($chapter.Number.ToString('00'))-$($chapter.Title)"
    }
    
    $folderPath = Join-Path "." $folderName
    if (-not (Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath -Force | Out-Null
    }
    
    # 提取章节内容
    $startLine = $chapter.Line - 1  # 转换为0-based索引
    $endLine = $nextChapter.Line - 2  # 不包含下一章节标题
    
    $chapterContent = $lines[$startLine..$endLine]
    
    # 创建README.md文件
    $readmePath = Join-Path $folderPath "README.md"
    
    # 构建内容
    $header = "# $($chapter.Number). $($chapter.Title)`n`n> **章节编号**: $($chapter.Number)`n> **章节标题**: $($chapter.Title)`n> **来源文档**: PostgreSQL 18 异步 I/O 机制`n`n---`n`n"
    $footer = "`n`n---`n`n**返回**: [文档首页](../README.md)"
    
    $fullContent = $header + ($chapterContent -join "`n") + $footer
    
    # 写入文件
    $fullContent | Out-File -FilePath $readmePath -Encoding UTF8 -NoNewline
    
    Write-Host "已创建章节 $($chapter.Number): $($chapter.Title) -> $folderName"
}

Write-Host "`n文档拆分完成！"
