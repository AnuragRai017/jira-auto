@echo off
echo Installing Jira Automation TypeScript Project...
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js found: 
node --version

echo.
echo Installing npm dependencies...
npm install

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Compiling TypeScript...
npx tsc

if %errorlevel% neq 0 (
    echo ERROR: Failed to compile TypeScript
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure your settings
echo 2. Run: npm run start --help to see available commands
echo 3. Test with: npm run start check-fields
echo.

pause
