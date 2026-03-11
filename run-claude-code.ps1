# run-claude-code.ps1 - 使用本地 Claude Code CLI 执行项目
# 此脚本调用你电脑上已配置的 Claude Code

$ErrorActionPreference = "Stop"
$projectRoot = "D:\openclaw\workspace\case1"
$configPath = Join-Path $projectRoot "config.json"
$outputDir = "D:\openclaw\workspace\case1\data\output"
$stateFile = Join-Path $outputDir "claude_state.json"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  使用 Claude Code CLI 执行项目" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Claude Code 是否可用
Write-Host "[1/3] 检查 Claude Code..." -ForegroundColor Yellow
try {
    $claudeVersion = claude --version 2>&1
    Write-Host "  → Claude Code 已安装：$claudeVersion" -ForegroundColor Green
} catch {
    Write-Host "  → 错误：未找到 Claude Code！" -ForegroundColor Red
    Write-Host "  请确保 Claude Code 已正确安装并可访问" -ForegroundColor Yellow
    exit 1
}

# 2. 读取配置
Write-Host "[2/3] 读取配置..." -ForegroundColor Yellow
$config = Get-Content $configPath | ConvertFrom-Json

# 3. 准备提示词
Write-Host "[3/3] 准备执行..." -ForegroundColor Yellow

# 检查现有状态
$existingChapters = Get-ChildItem $outputDir -Filter "chapter_*.txt" 2>$null | Measure-Object | Select-Object -ExpandProperty Count
$nextChapter = $existingChapters + 1

# 检查是否有叙事技法档案
$narrativeProfilePath = Join-Path $outputDir "narrative_profile.json"
$settingPath = Join-Path $outputDir "Novel_setting.txt"
$directoryPath = Join-Path $outputDir "Novel_directory.txt"

Write-Host ""
Write-Host "当前状态：" -ForegroundColor Cyan
Write-Host "  已生成章节：$existingChapters" -ForegroundColor Gray
Write-Host "  下一章节：$nextChapter" -ForegroundColor Gray
Write-Host "  叙事技法档案：$(if (Test-Path $narrativeProfilePath) { '✓' } else { '✗' })" -ForegroundColor $(if (Test-Path $narrativeProfilePath) { 'Green' } else { 'Yellow' })
Write-Host "  故事设定：$(if (Test-Path $settingPath) { '✓' } else { '✗' })" -ForegroundColor $(if (Test-Path $settingPath) { 'Green' } else { 'Yellow' })
Write-Host "  章节目录：$(if (Test-Path $directoryPath) { '✓' } else { '✗' })" -ForegroundColor $(if (Test-Path $directoryPath) { 'Green' } else { 'Yellow' })
Write-Host ""

# 构建提示词
$prompt = @"
# 网络小说叙事技法仿写系统

## 项目说明
基于 AI_NovelGenerator 框架，分析目标小说的叙事技法，迁移到新题材创作。

## 配置信息
- 目标小说：$($config.target_novel_path)
- 新题材：$($config.new_story.genre)
- 核心想法：$($config.new_story.core_idea)
- 主角：$($config.new_story.protagonist.name)，$($config.new_story.protagonist.occupation)

## 当前任务
@(
    if (-not (Test-Path $narrativeProfilePath)) {
        "1. 分析目标小说，提取叙事技法（节奏、钩子、对话风格等）"
        "2. 输出：$narrativeProfilePath"
    } elseif (-not (Test-Path $settingPath)) {
        "1. 根据叙事技法档案和用户新想法，创作新故事设定"
        "2. 输出：$settingPath"
    } elseif (-not (Test-Path $directoryPath)) {
        "1. 根据设定生成 120 章目录"
        "2. 输出：$directoryPath"
    } else {
        "1. 生成第 $nextChapter 章正文（约 $($config.word_number) 字）"
        "2. 保持古龙风格（对话占比高、短句、章末悬念）"
        "3. 输出：$outputDir\chapter_$nextChapter.txt"
    }
) | ForEach-Object { Write-Host "  → $_" -ForegroundColor Cyan }

## 执行要求
1. 严格按照配置文件中的参数执行
2. 保持叙事风格一致性
3. 输出文件到指定目录

开始执行...
"@

# 执行 Claude Code
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动 Claude Code..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 使用 claude 命令执行
claude --prompt "$prompt" --working-directory $projectRoot

# 检查结果
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  执行完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # 更新状态
    $state = @{
        last_run = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        last_action = "chapter_generation"
        chapters_generated = (Get-ChildItem $outputDir -Filter "chapter_*.txt" 2>$null | Measure-Object | Select-Object -ExpandProperty Count)
        status = "success"
    }
    $state | ConvertTo-Json | Out-File $stateFile -Encoding UTF8
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  执行失败！" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    
    # 记录错误
    $state = @{
        last_run = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        last_action = "chapter_generation"
        status = "error"
        error_message = "Claude Code 执行失败"
    }
    $state | ConvertTo-Json | Out-File $stateFile -Encoding UTF8
    exit 1
}
