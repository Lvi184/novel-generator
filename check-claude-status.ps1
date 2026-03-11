# check-claude-status.ps1 - 每 2 分钟检查 Claude Code 运行状态
# 用法：schtasks /create /tn "ClaudeCodeMonitor" /tr "powershell.exe -File D:\openclaw\workspace\case1\check-claude-status.ps1" /sc minute /mo 2 /f

$ErrorActionPreference = "Continue"
$projectRoot = "D:\openclaw\workspace\case1"
$configPath = Join-Path $projectRoot "config.json"
$stateFile = Join-Path $projectRoot "data\output\claude_state.json"
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

# 获取 Claude Code 状态
function Get-ClaudeState {
    if (Test-Path $stateFile) {
        return Get-Content $stateFile | ConvertFrom-Json
    }
    return $null
}

# 保存 Claude Code 状态
function Save-ClaudeState {
    param([object]$State)
    $stateDir = Split-Path $stateFile -Parent
    if (-not (Test-Path $stateDir)) {
        New-Item -ItemType Directory -Path $stateDir | Out-Null
    }
    $State | ConvertTo-Json | Out-File $stateFile -Encoding UTF8
}

# 检查是否有正在运行的 Claude Code 进程
function Get-RunningClaudeProcess {
    $processes = Get-Process | Where-Object {
        $_.ProcessName -like "*claude*" -or $_.CommandLine -like "*claude*"
    }
    return $processes
}

# 主逻辑
try {
    Write-Log "=== Claude Code 状态检查 ===" "MONITOR"
    
    # 1. 读取配置
    $config = Get-Content $configPath | ConvertFrom-Json
    $claudeConfig = $config.claude
    
    if (-not $claudeConfig.enabled) {
        Write-Log "Claude Code 未启用，跳过检查" "SKIP"
        exit 0
    }
    
    # 2. 获取当前状态
    $currentState = Get-ClaudeState
    $now = Get-Date
    $nowStr = $now.ToString("yyyy-MM-dd HH:mm:ss")
    
    # 3. 检查 Claude Code 进程
    $claudeProcesses = Get-RunningClaudeProcess
    $isRunning = $claudeProcesses.Count -gt 0
    
    Write-Log "发现 $($claudeProcesses.Count) 个 Claude 相关进程" "INFO"
    
    # 4. 更新状态
    $newState = [PSCustomObject]@{
        last_check = $nowStr
        is_running = $isRunning
        process_count = $claudeProcesses.Count
        last_known_state = if ($currentState) { $currentState.last_known_state } else { "unknown" }
        last_state_change = if ($currentState) { $currentState.last_state_change } else { $nowStr }
        chapters_generated = if ($currentState) { $currentState.chapters_generated } else { 0 }
        current_chapter = if ($currentState) { $currentState.current_chapter } else { 0 }
        errors = if ($currentState) { $currentState.errors } else { @() }
    }
    
    # 检测状态变化
    if ($currentState) {
        if ($currentState.is_running -ne $isRunning) {
            $newState.last_state_change = $nowStr
            $newState.last_known_state = if ($isRunning) { "running" } else { "stopped" }
            
            if ($isRunning) {
                Write-Log "Claude Code 已启动" "STATE_CHANGE"
            } else {
                Write-Log "Claude Code 已停止" "STATE_CHANGE"
            }
        }
    } else {
        $newState.last_known_state = if ($isRunning) { "running" } else { "stopped" }
        $newState.last_state_change = $nowStr
    }
    
    # 5. 保存状态
    Save-ClaudeState -State $newState
    
    # 6. 输出状态摘要
    Write-Log "当前状态：$($newState.last_known_state)" "STATUS"
    Write-Log "进程数：$($newState.process_count)" "STATUS"
    Write-Log "已生成章节：$($newState.chapters_generated)" "STATUS"
    
    # 7. 如果有错误，记录
    if ($newState.errors.Count -gt 0) {
        Write-Log "未解决错误：$($newState.errors.Count)" "WARNING"
    }
    
    Write-Log "状态已更新：$stateFile" "SUCCESS"
    
} catch {
    Write-Log "检查失败：$($_.Exception.Message)" "ERROR"
    
    # 记录错误到状态
    $currentState = Get-ClaudeState
    if ($currentState) {
        $currentState.errors += [PSCustomObject]@{
            time = $nowStr
            message = $_.Exception.Message
        }
        Save-ClaudeState -State $currentState
    }
}
