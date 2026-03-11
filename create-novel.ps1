# create-novel.ps1 - 定时任务脚本
# 功能：每天自动生成一章都市小说（古龙风格）
# 用法：schtasks /create /tn "NovelGenerator" /tr "powershell.exe -File D:\openclaw\workspace\case1\create-novel.ps1" /sc daily /st 09:00 /f

$ErrorActionPreference = "Stop"
$projectRoot = "D:\openclaw\workspace\case1"
$configPath = Join-Path $projectRoot "config.json"
$logFile = Join-Path $projectRoot "logs\$(Get-Date -Format 'yyyy-MM-dd').log"

# 创建日志目录
$logDir = Join-Path $projectRoot "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# 日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

try {
    Write-Log "========================================" "START"
    Write-Log "网络小说叙事技法仿写系统 - 古龙风格" "INFO"
    Write-Log "========================================" "INFO"

    # 1. 读取配置
    Write-Log "[1/4] 读取配置..." "INFO"
    if (-not (Test-Path $configPath)) {
        Write-Log "错误：config.json 不存在！" "ERROR"
        exit 1
    }
    $config = Get-Content $configPath -Encoding UTF8 | ConvertFrom-Json
    $outputDir = $config.filepath

    # 确保输出目录存在
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir | Out-Null
        Write-Log "创建输出目录：$outputDir" "INFO"
    }

    # 2. 检查叙事技法档案
    Write-Log "[2/4] 检查叙事技法档案..." "INFO"
    $narrativeProfilePath = Join-Path $outputDir "narrative_profile.json"
    if (-not (Test-Path $narrativeProfilePath)) {
        Write-Log "叙事技法档案不存在，执行分析..." "INFO"
        Write-Log "目标小说：$($config.target_novel_path)" "INFO"
        
        # 调用 Claude 进行分析
        $claudePrompt = @"
请分析以下小说的叙事技法，输出 JSON 格式的叙事技法档案。

目标小说：$($config.target_novel_path)

分析维度：
1. 剧情节奏（紧张度曲线、章节长度分布）
2. 钩子设计（章末悬念频率、类型）
3. 对话风格（对话占比、句式特点）
4. 冲突模式（冲突类型、升级方式）
5. 人物弧线（主角成长阶段、关系变化）

输出格式：JSON，保存到 $narrativeProfilePath
"@
        
        # 使用 Claude Code 执行分析
        $analysisScript = Join-Path $projectRoot "src\style_analyzer.py"
        if (Test-Path $analysisScript) {
            python $analysisScript --config $configPath
        } else {
            # 如果没有 Python 脚本，直接用 Claude
            Write-Log "使用 Claude 直接分析..." "INFO"
            claude --prompt "$claudePrompt" --working-directory $projectRoot
        }
        
        if (Test-Path $narrativeProfilePath) {
            Write-Log "分析完成！" "SUCCESS"
        } else {
            Write-Log "分析失败：未生成叙事技法档案" "ERROR"
            exit 1
        }
    } else {
        Write-Log "叙事技法档案已存在，跳过分析" "INFO"
    }

    # 3. 检查设定和目录
    Write-Log "[3/4] 检查故事设定和目录..." "INFO"
    $settingPath = Join-Path $outputDir "Novel_setting.txt"
    $directoryPath = Join-Path $outputDir "Novel_directory.txt"

    if (-not (Test-Path $settingPath) -or -not (Test-Path $directoryPath)) {
        Write-Log "设定/目录不存在，执行迁移..." "INFO"
        
        $migrationPrompt = @"
请根据以下叙事技法档案和用户新想法，创作新故事的设定和目录。

叙事技法档案：$narrativeProfilePath
用户新想法：
- 题材：$($config.new_story.genre)
- 核心想法：$($config.new_story.core_idea)
- 主角：$($config.new_story.protagonist.name)，$($config.new_story.protagonist.occupation)

要求：
1. 完全复用原作的叙事节奏和钩子设计
2. 设定和人物根据用户新想法原创
3. 输出两个文件：
   - Novel_setting.txt：故事设定（世界观、主角、核心冲突）
   - Novel_directory.txt：120 章目录（含每章简述）

输出目录：$outputDir
"@
        
        $migrationScript = Join-Path $projectRoot "src\narrative_migrator.py"
        if (Test-Path $migrationScript) {
            python $migrationScript --config $configPath
        } else {
            Write-Log "使用 Claude 直接迁移..." "INFO"
            claude --prompt "$migrationPrompt" --working-directory $projectRoot
        }
        
        if ((Test-Path $settingPath) -and (Test-Path $directoryPath)) {
            Write-Log "迁移完成！" "SUCCESS"
        } else {
            Write-Log "迁移失败：未生成设定/目录" "ERROR"
            exit 1
        }
    } else {
        Write-Log "设定和目录已存在，跳过迁移" "INFO"
    }

    # 4. 生成下一章
    Write-Log "[4/4] 生成下一章..." "INFO"
    $existingChapters = Get-ChildItem $outputDir -Filter "chapter_*.txt" 2>$null | Measure-Object | Select-Object -ExpandProperty Count
    $nextChapter = $existingChapters + 1

    Write-Log "已生成 $existingChapters 章，正在生成第 $nextChapter 章..." "INFO"

    $chapterPrompt = @"
请根据以下信息生成第 $nextChapter 章：

设定文件：$settingPath
目录文件：$directoryPath
叙事技法档案：$narrativeProfilePath

要求：
1. 严格按照目录中的第 $nextChapter 章简述创作
2. 复用叙事技法档案中的节奏和钩子设计
3. 保持古龙风格（对话占比高、短句、章末悬念）
4. 字数：4000 字左右
5. 输出文件：$outputDir\chapter_$nextChapter.txt
"@

    $generatorScript = Join-Path $projectRoot "novel_generator\chapter_generator.py"
    if (Test-Path $generatorScript) {
        python $generatorScript --config $configPath --chapter $nextChapter
    } else {
        Write-Log "使用 Claude 直接生成章节..." "INFO"
        claude --prompt "$chapterPrompt" --working-directory $projectRoot
    }

    $chapterPath = Join-Path $outputDir "chapter_$nextChapter.txt"
    if (Test-Path $chapterPath) {
        $chapterSize = (Get-Item $chapterPath).Length
        Write-Log "第 $nextChapter 章生成成功！文件大小：$([math]::Round($chapterSize/1024, 2)) KB" "SUCCESS"
    } else {
        Write-Log "第 $nextChapter 章生成失败！" "ERROR"
        exit 1
    }

    Write-Log "========================================" "END"
    Write-Log "任务完成！" "SUCCESS"
    Write-Log "========================================" "SUCCESS"

} catch {
    Write-Log "发生错误：$($_.Exception.Message)" "ERROR"
    exit 1
}
