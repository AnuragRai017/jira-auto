@echo off
echo.
echo ========================================
echo   JIRA AUTOMATION DEPLOYMENT OPTIONS
echo ========================================
echo.
echo Choose your deployment method:
echo.
echo 1. Windows Service (Recommended for servers)
echo    - Runs automatically on startup
echo    - Background service
echo    - Automatic restart on failure
echo.
echo 2. Scheduled Task (Good for shared computers)
echo    - Runs every 5 minutes
echo    - No console window
echo    - Easy to manage
echo.
echo 3. Docker Container (For containerized environments)
echo    - Portable and isolated
echo    - Easy scaling
echo    - Cross-platform
echo.
echo 4. Manual Testing (For development/testing)
echo    - Run once manually
echo    - See immediate output
echo    - Good for troubleshooting
echo.
echo ========================================
echo.

choice /c 1234 /m "Select deployment option"

if errorlevel 4 goto manual
if errorlevel 3 goto docker
if errorlevel 2 goto scheduled
if errorlevel 1 goto service

:service
echo.
echo Installing as Windows Service...
echo.
echo This requires Administrator privileges.
echo Please run this script as Administrator if you haven't already.
echo.
pause
npm run service:install
goto end

:scheduled
echo.
echo Creating Scheduled Task...
echo.
echo This requires Administrator privileges.
echo Please ensure you're running as Administrator.
echo.
pause
powershell -ExecutionPolicy Bypass -File create-scheduled-task.ps1
goto end

:docker
echo.
echo Building Docker container...
echo.
echo Make sure Docker is installed and running.
echo.
pause
npm run docker:build
npm run docker:run
echo.
echo Container started! Use 'npm run docker:logs' to view logs.
goto end

:manual
echo.
echo Running manual test...
echo.
echo This will process tickets once and exit.
echo.
pause
npm run start customer-fields process
goto end

:end
echo.
echo ========================================
echo   DEPLOYMENT COMPLETED
echo ========================================
echo.
echo Useful commands:
echo   npm run start customer-fields status     - Check automation status
echo   npm run start customer-fields process    - Run once manually
echo   npm run start test-config                - Test configuration
echo.
echo For Windows Service:
echo   npm run service:start    - Start service
echo   npm run service:stop     - Stop service
echo   npm run service:uninstall - Remove service
echo.
echo For Docker:
echo   npm run docker:logs      - View logs
echo   npm run docker:stop      - Stop containers
echo.
echo See DEPLOYMENT.md for detailed instructions.
echo.
pause
