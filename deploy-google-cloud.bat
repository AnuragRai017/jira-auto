@echo off
echo 🚀 Deploying Jira Automation to Google Cloud Run...
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Google Cloud SDK not found. Please install it first:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Prompt for project ID if not set
set /p PROJECT_ID="Enter your Google Cloud Project ID: "
if "%PROJECT_ID%"=="" (
    echo ❌ Project ID is required
    pause
    exit /b 1
)

REM Set the project
echo 📋 Setting project to %PROJECT_ID%...
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔧 Enabling required APIs...
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudscheduler.googleapis.com

REM Build the Docker image
echo 🏗️ Building Docker image...
gcloud builds submit --tag gcr.io/%PROJECT_ID%/jira-automation

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)

REM Deploy to Cloud Run
echo 🚀 Deploying to Cloud Run...
gcloud run deploy jira-automation --image gcr.io/%PROJECT_ID%/jira-automation --platform managed --region us-central1 --allow-unauthenticated --memory 512Mi --cpu 1 --timeout 900s --max-instances 1 --min-instances 0

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

REM Get the service URL
echo 📡 Getting service URL...
for /f "tokens=2 delims= " %%i in ('gcloud run services describe jira-automation --region us-central1 --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ✅ Deployment successful!
echo 🔗 Your service URL: %SERVICE_URL%
echo.
echo 🔧 Next steps:
echo 1. Set environment variables in Google Cloud Console
echo 2. Test the health endpoint: %SERVICE_URL%/health
echo 3. Configure weekend scheduling (see google-cloud-deployment.md)
echo.
echo 📖 Full instructions in: google-cloud-deployment.md
echo.
pause
