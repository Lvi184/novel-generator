# init-scheduler.ps1 - 初始化定时任务
# 设置两个定时任务：
# 1. 每 2 分钟检查 Claude Code 状态
# 2. 执行 Claude Code 生成内容（手动触发或通过其他条件触发）

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  网络小说叙事技法仿写系统" -ForegroundColor Cyan
Write-Host "  定时任务初始化" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = "D:\openclaw\workspace\case1"
$checkScript = Join-Path $projectRoot "check-claude-status.ps1"
$runScript = Join-Path $projectRoot "run-claude-code.ps1"
$checkTaskName = "ClaudeCodeMonitor"
$runTaskName = "ClaudeCodeRunner"

# 1. 检查配置文件
Write-Host "[1/4] 检查配置文件..." -ForegroundColor Yellow
$configPath = Join-Path $projectRoot "config.json"
if (-not (Test-Path $configPath)) {
    Write-Host "  → 错误：config.json 不存在！" -ForegroundColor Red
    exit 1
}
Write-Host "  → 配置文件存在" -ForegroundColor Green

# 2. 检查目标小说
Write-Host "[2/4] 检查目标小说..." -ForegroundColor Yellow
$config = Get-Content $configPath | ConvertFrom-Json
if (Test-Path $config.target_novel_path) {
    $novelSize = (Get-Item $config.target_novel_path).Length
    Write-Host "  → 找到目标小说：$($config.target_novel_path)" -ForegroundColor Green
    Write-Host "  → 文件大小：$([math]::Round($novelSize/1024/1024, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "  → 警告：未找到目标小说！" -ForegroundColor Yellow
    Write-Host "  路径：$($config.target_novel_path)" -ForegroundColor Yellow
    Write-Host "  请确认小说文件已放置到正确位置" -ForegroundColor Yellow
}

# 3. 设置状态监控任务（每 2 分钟）
Write-Host "[3/4] 设置状态监控任务（每 2 分钟）..." -ForegroundColor Yellow

# 删除旧任务
schtasks /query /tn $checkTaskName > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    schtasks /delete /tn $checkTaskName /f > $null
    Write-Host "  → 删除旧监控任务" -ForegroundColor Gray
}

# 创建新任务
$checkCommand = "powershell.exe -ExecutionPolicy Bypass -File `"$checkScript`""
schtasks /create /tn $checkTaskName /tr $checkCommand /sc minute /mo 2 /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "  → 监控任务创建成功！" -ForegroundColor Green
    Write-Host "  → 任务名称：$checkTaskName" -ForegroundColor Gray
    Write-Host "  → 执行频率：每 2 分钟" -ForegroundColor Gray
} else {
    Write-Host "  → 监控任务创建失败！" -ForegroundColor Red
    Write-Host "  可能需要管理员权限" -ForegroundColor Yellow
}

# 4. 设置执行任务（手动触发）
Write-Host "[4/4] 设置执行任务（手动触发）..." -ForegroundColor Yellow

# 删除旧任务
schtasks /query /tn $runTaskName > $null 2>&1
if ($LASTEXITCODE -eq 0) {
    schtasks /delete /tn $runTaskName /f > $null
    Write-Host "  → 删除旧执行任务" -ForegroundColor Gray
}

# 创建新任务（手动触发）
$runCommand = "powershell.exe -ExecutionPolicy Bypass -File `"$runScript`""
schtasks /create /tn $runTaskName /tr $runCommand /sc once /st 00:00 /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "  → 执行任务创建成功！" -ForegroundColor Green
    Write-Host "  → 任务名称：$runTaskName" -ForegroundColor Gray
    Write-Host "  → 触发方式：手动" -ForegroundColor Gray
} else {
    Write-Host "  → 执行任务创建失败！" -ForegroundColor Red
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  初始化完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已创建的任务：" -ForegroundColor Yellow
Write-Host "  1. $checkTaskName - 每 2 分钟检查 Claude Code 状态" -ForegroundColor Cyan
Write-Host "  2. $runTaskName - 执行 Claude Code 生成内容（手动触发）" -ForegroundColor Cyan
Write-Host ""
Write-Host "常用命令：" -ForegroundColor Yellow
Write-Host "  查看监控任务状态：schtasks /query /tn $checkTaskName" -ForegroundColor Gray
Write-Host "  查看执行任务状态：schtasks /query /tn $runTaskName" -ForegroundColor Gray
Write-Host "  手动运行一次：schtasks /run /tn $runTaskName" -ForegroundColor Gray
Write-Host "  删除所有任务：schtasks /delete /tn $checkTaskName /f; schtasks /delete /tn $runTaskName /f" -ForegroundColor Gray
Write-Host ""
Write-Host "查看状态文件：" -ForegroundColor Yellow
Write-Host "  notepad D:\openclaw\workspace\case1\data\output\claude_state.json" -ForegroundColor Gray
Write-Host ""
Write-Host "查看日志：" -ForegroundColor Yellow
Write-Host "  notepad D:\openclaw\workspace\case1\logs\$(Get-Date -Format 'yyyy-MM-dd').log" -ForegroundColor Gray
Write-Host ""

# 询问是否立即测试
$runNow = Read-Host "是否立即运行一次测试？(y/n)"
if ($runNow -eq "y") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  开始测试运行..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    & $runScript
}
