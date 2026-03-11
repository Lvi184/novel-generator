# Simple check script - avoids encoding issues
$ErrorActionPreference = "Continue"
$projectRoot = "D:\openclaw\workspace\case1"
$stateFile = Join-Path $projectRoot "data\output\claude_state.json"
$logFile = Join-Path $projectRoot "logs\check.log"

# Create log directory
$logDir = Join-Path $projectRoot "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

# Log function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry
}

Write-Log "=== Claude Code Check ===" "MONITOR"

# Check for Claude processes
$processes = Get-Process | Where-Object { $_.ProcessName -like "*claude*" }
$isRunning = $processes.Count -gt 0

Write-Log "Found $($processes.Count) Claude processes" "INFO"

# Create state
$state = @{
    last_check = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    is_running = $isRunning
    process_count = $processes.Count
}

# Save state
$stateDir = Split-Path $stateFile -Parent
if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir | Out-Null
}
$state | ConvertTo-Json | Out-File $stateFile -Encoding UTF8

Write-Log "State saved to $stateFile" "SUCCESS"
