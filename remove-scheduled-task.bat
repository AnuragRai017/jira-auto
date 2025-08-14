@echo off
echo Removing Windows Scheduled Task for Jira Customer Field Automation...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo.
    echo To run as administrator:
    echo 1. Right-click on Command Prompt or PowerShell
    echo 2. Select "Run as administrator"
    echo 3. Navigate to this directory and run this script again
    echo.
    pause
    exit /b 1
)

REM Remove scheduled task
schtasks /delete /tn "Jira Customer Field Automation" /f

if %errorLevel% equ 0 (
    echo.
    echo ✅ Scheduled task removed successfully!
    echo The "Jira Customer Field Automation" task has been deleted.
    echo.
) else (
    echo.
    echo ❌ Failed to remove scheduled task!
    echo The task may not exist or you may not have sufficient permissions.
    echo.
)

pause
