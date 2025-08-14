@echo off
echo Creating Windows Scheduled Task for Jira Customer Field Automation...
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

REM Get current directory
set "CURRENT_DIR=%~dp0"

REM Create scheduled task that runs every 5 minutes
schtasks /create ^
    /tn "Jira Customer Field Automation" ^
    /tr "node \"%CURRENT_DIR%dist\customer-field-automation.js\" process" ^
    /sc minute ^
    /mo 5 ^
    /ru "SYSTEM" ^
    /f

if %errorLevel% equ 0 (
    echo.
    echo ✅ Scheduled task created successfully!
    echo.
    echo Task details:
    echo   Name: Jira Customer Field Automation
    echo   Schedule: Every 5 minutes
    echo   Command: node customer-field-automation.js process
    echo   User: SYSTEM
    echo.
    echo The task will start automatically and run every 5 minutes.
    echo.
    echo To view/manage the task:
    echo   1. Open Task Scheduler Windows App
    echo   2. Look for "Jira Customer Field Automation" in the task library
    echo.
    echo To remove the task: run remove-scheduled-task.bat as Administrator
    echo.
) else (
    echo.
    echo ❌ Failed to create scheduled task!
    echo Please check that you're running as Administrator and try again.
    echo.
)

pause
