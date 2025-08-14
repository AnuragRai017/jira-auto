# PowerShell script to remove the scheduled task for Jira automation
# Run as Administrator

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as administrator:" -ForegroundColor Yellow
    Write-Host "1. Open PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host "2. Navigate to this directory" -ForegroundColor Yellow
    Write-Host "3. Run: .\remove-scheduled-task.ps1" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "🛑 Removing Windows Scheduled Task for Jira Customer Field Automation..." -ForegroundColor Yellow
Write-Host ""

$TaskName = "Jira Customer Field Automation"

try {
    # Check if task exists
    $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if ($Task) {
        # Remove the task
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "✅ Scheduled task removed successfully!" -ForegroundColor Green
        Write-Host "The '$TaskName' task has been deleted." -ForegroundColor White
    } else {
        Write-Host "⚠️  Task '$TaskName' not found." -ForegroundColor Yellow
        Write-Host "The task may have already been removed or never existed." -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Failed to remove scheduled task!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""
Read-Host "Press Enter to exit"
