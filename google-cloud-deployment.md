# Google Cloud Run Deployment Guide

## 🚀 Complete Google Cloud Deployment Steps

### Step 1: Prerequisites Setup

1. **Create Google Cloud Account**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Sign up/login with your Google account
   - You get $300 free credits for new accounts

2. **Create a New Project**
   - Click "Select a Project" → "New Project"
   - Name: `jira-automation` (or your choice)
   - Note your PROJECT_ID (you'll need this)

3. **Enable Required APIs**
   ```bash
   # Enable Cloud Run API
   gcloud services enable run.googleapis.com
   
   # Enable Cloud Build API (for building Docker images)
   gcloud services enable cloudbuild.googleapis.com
   
   # Enable Container Registry API
   gcloud services enable containerregistry.googleapis.com
   ```

### Step 2: Install Google Cloud SDK

**For Windows:**
1. Download from: https://cloud.google.com/sdk/docs/install
2. Run the installer
3. Restart PowerShell
4. Login: `gcloud auth login`
5. Set project: `gcloud config set project YOUR_PROJECT_ID`

### Step 3: Build and Deploy

1. **Build the Docker image:**
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jira-automation
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy jira-automation \
     --image gcr.io/YOUR_PROJECT_ID/jira-automation \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --timeout 900s \
     --max-instances 1 \
     --min-instances 0
   ```

3. **Set Environment Variables:**
   ```bash
   gcloud run services update jira-automation \
     --set-env-vars JIRA_URL=https://your-domain.atlassian.net,JIRA_EMAIL=your-email@domain.com,JIRA_API_TOKEN=your-api-token,NODE_ENV=production \
     --region us-central1
   ```

### Step 4: Weekend Scheduling with Cloud Scheduler

1. **Enable Cloud Scheduler API:**
   ```bash
   gcloud services enable cloudscheduler.googleapis.com
   ```

2. **Create Weekend Pause Job (Runs Friday 6 PM):**
   ```bash
   gcloud scheduler jobs create http weekend-pause \
     --schedule="0 18 * * 5" \
     --uri=https://YOUR_CLOUD_RUN_URL/pause \
     --http-method=POST \
     --time-zone="America/New_York"
   ```

3. **Create Monday Resume Job (Runs Monday 9 AM):**
   ```bash
   gcloud scheduler jobs create http monday-resume \
     --schedule="0 9 * * 1" \
     --uri=https://YOUR_CLOUD_RUN_URL/resume \
     --http-method=POST \
     --time-zone="America/New_York"
   ```

### Step 5: Monitoring & Logging

1. **View Logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```

2. **Check Service Status:**
   ```bash
   gcloud run services describe jira-automation --region us-central1
   ```

3. **Monitor in Console:**
   - Go to Cloud Run console
   - Click on your service
   - View metrics, logs, and revisions

## 📊 Cost Estimation

**Free Tier Includes:**
- 2 million requests per month
- 400,000 GB-seconds of memory
- 200,000 vCPU-seconds

**Estimated Monthly Cost for Your Automation:**
- Running 8 hours/day × 22 weekdays = 176 hours/month
- With 512MB and minimal CPU usage = **Under $2/month**
- First few months likely **FREE** with credits

## 🔧 Configuration Files Created

The deployment uses these files:
- `cloudbuild.yaml` - Build configuration
- `Dockerfile` - Container definition  
- `server.js` - Main application with weekend detection

## 🎯 Testing Your Deployment

1. **Health Check:**
   ```bash
   curl https://YOUR_CLOUD_RUN_URL/health
   ```

2. **Manual Trigger:**
   ```bash
   curl https://YOUR_CLOUD_RUN_URL/trigger
   ```

3. **Check Status:**
   ```bash
   curl https://YOUR_CLOUD_RUN_URL/status
   ```

## 🔄 Updates and Maintenance

**To Update Code:**
```bash
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jira-automation
gcloud run deploy jira-automation --image gcr.io/YOUR_PROJECT_ID/jira-automation --region us-central1
```

**To View Recent Logs:**
```bash
gcloud run services logs tail jira-automation --region us-central1
```

## 🚨 Important Notes

1. **Replace placeholders** with your actual values:
   - `YOUR_PROJECT_ID` - Your Google Cloud project ID
   - `YOUR_CLOUD_RUN_URL` - Your deployed service URL
   - Jira credentials in environment variables

2. **Service automatically scales** from 0 to 1 instance based on requests

3. **Weekend detection** is built into the server.js code

4. **Logs are retained** for 30 days in Cloud Logging

Ready to deploy? Start with Step 1 and work through each step! 🚀
