# PowerShell script to create a scheduled task for Jira automation
# Run as Administrator

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as administrator:" -ForegroundColor Yellow
    Write-Host "1. Open PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host "2. Navigate to this directory" -ForegroundColor Yellow
    Write-Host "3. Run: .\create-scheduled-task.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🚀 Creating Windows Scheduled Task for Jira Customer Field Automation..." -ForegroundColor Green
Write-Host ""

# Get current directory
$CurrentDir = Get-Location

# Define task settings
$TaskName = "Jira Customer Field Automation"
$TaskDescription = "Automatically processes Jira tickets to fill customer fields based on reporter information"
$ScriptPath = Join-Path $CurrentDir "dist\customer-field-automation.js"
$NodePath = (Get-Command node).Source

# Create action
$Action = New-ScheduledTaskAction -Execute $NodePath -Argument "`"$ScriptPath`" process" -WorkingDirectory $CurrentDir

# Create trigger (every 5 minutes)
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as SYSTEM)
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $TaskDescription -Force
    
    Write-Host "✅ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Every 5 minutes" -ForegroundColor White
    Write-Host "  Command: node `"$ScriptPath`" process" -ForegroundColor White
    Write-Host "  User: SYSTEM" -ForegroundColor White
    Write-Host "  Working Directory: $CurrentDir" -ForegroundColor White
    Write-Host ""
    Write-Host "The task will start automatically and run every 5 minutes." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To view/manage the task:" -ForegroundColor Cyan
    Write-Host "  1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
    Write-Host "  2. Look for 'Jira Customer Field Automation' in the task library" -ForegroundColor White
    Write-Host ""
    Write-Host "To remove the task: run .\remove-scheduled-task.ps1 as Administrator" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Failed to create scheduled task!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to exit"
