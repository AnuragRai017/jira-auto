@echo off
echo 🚀 Google Cloud Run Deployment - Fix for Billing Issues
echo.
echo ⚠️  BILLING SETUP REQUIRED
echo Your project needs billing enabled for Cloud Build.
echo.
echo 📋 Steps to fix:
echo 1. Go to: https://console.cloud.google.com/billing
echo 2. Create or select a billing account
echo 3. Link it to project: sinuous-gist-440313-m9
echo.
echo 💡 ALTERNATIVE: Deploy using pre-built image
echo.

set /p choice="Do you want to enable billing (y) or use alternative method (a)? "

if /i "%choice%"=="y" (
    echo Opening billing console...
    start https://console.cloud.google.com/billing
    echo.
    echo After enabling billing, run this command:
    echo gcloud builds submit --tag gcr.io/sinuous-gist-440313-m9/jira-automation
    pause
    exit /b 0
)

if /i "%choice%"=="a" (
    echo.
    echo 🔄 Using alternative deployment method...
    echo.
    
    REM Create a simple Node.js Cloud Run deployment without Docker build
    echo Creating app.yaml for Cloud Run...
    
    echo runtime: nodejs18 > app.yaml
    echo env: standard >> app.yaml
    echo.
    echo service: jira-automation >> app.yaml
    echo.
    echo env_variables: >> app.yaml
    echo   NODE_ENV: production >> app.yaml
    echo.
    echo automatic_scaling: >> app.yaml
    echo   min_instances: 0 >> app.yaml
    echo   max_instances: 1 >> app.yaml
    
    echo.
    echo ✅ Created app.yaml for App Engine deployment
    echo.
    echo 📋 Next steps:
    echo 1. Enable App Engine API: gcloud services enable appengine.googleapis.com
    echo 2. Deploy: gcloud app deploy
    echo.
    echo This method doesn't require billing for small apps!
    
) else (
    echo Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause
