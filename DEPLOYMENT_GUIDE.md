# Free Cloud Deployment Guide for Jira Automation

This automation can be deployed on several free cloud platforms with weekend scheduling. Here are the best options:

## 🚀 Recommended: Railway (Best Free Option)

**Free Tier**: 512MB RAM, $5 monthly credit (usually enough for 24/7 operation)
**Weekend Handling**: Environment-based scheduling

### Deployment Steps:
1. Create account at [railway.app](https://railway.app)
2. Install Railway CLI: `npm install -g @railway/cli`
3. Deploy:
   ```bash
   railway login
   railway init
   railway up
   ```
4. Set environment variables in Railway dashboard:
   - `JIRA_URL=https://your-domain.atlassian.net`
   - `JIRA_EMAIL=your-email@domain.com`
   - `JIRA_API_TOKEN=your-api-token`
   - `NODE_ENV=production`

## 🌐 Render.com (Reliable Free Option)

**Free Tier**: 512MB RAM, sleeps after 15 minutes of inactivity
**Weekend Handling**: Built-in cron job keeps it alive Mon-Fri only

### Deployment Steps:
1. Connect your GitHub repo to [render.com](https://render.com)
2. Use the provided `render.yaml` configuration
3. Set environment variables in Render dashboard
4. Automatic deploys on code push

## ⚡ Fly.io (Developer Friendly)

**Free Tier**: 256MB shared CPU, 3 VMs included
**Weekend Handling**: Auto-scaling with weekend pause

### Deployment Steps:
1. Install flyctl: `iwr https://fly.io/install.ps1 -useb | iex`
2. Login: `flyctl auth login`
3. Deploy: `flyctl deploy`

## 🟣 Heroku (Classic Option)

**Free Tier**: Discontinued, but has low-cost options ($7/month)
**Weekend Handling**: Scheduler add-on for time-based control

### Deployment Steps:
1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`
5. Add scheduler: `heroku addons:create scheduler:standard`

## ☁️ Google Cloud Run (Pay-per-use)

**Free Tier**: 2 million requests per month, 400,000 GB-seconds
**Weekend Handling**: Cloud Scheduler integration

### Deployment Steps:
1. Enable Cloud Run API in Google Cloud Console
2. Build: `gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jira-automation`
3. Deploy: `gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/jira-automation`

## 📅 Weekend Scheduling Options

### Method 1: Environment Variables (All Platforms)
The server.js automatically detects weekends and pauses automation.

### Method 2: Cron Jobs (Render, Heroku)
- **Render**: Uses built-in cron job in `render.yaml`
- **Heroku**: Configure Scheduler add-on to run only Mon-Fri

### Method 3: Platform Schedulers
- **Google Cloud**: Cloud Scheduler with weekend exclusion
- **Railway**: Environment variable + restart scheduling

## 🎯 Quick Start Recommendations

### For Beginners: Railway
- Easiest setup
- Most generous free tier
- Automatic scaling

### For Developers: Fly.io
- Best performance
- Great CLI tools
- Good documentation

### For Enterprise: Google Cloud Run
- Most reliable
- Pay only for usage
- Advanced scheduling options

## 💡 Cost Optimization Tips

1. **Monitor Usage**: All platforms provide usage dashboards
2. **Weekend Shutdown**: Automatic via server.js weekend detection
3. **Health Checks**: `/health` endpoint prevents unnecessary restarts
4. **Batch Processing**: Customer automation runs in batches to reduce CPU usage

## 🔧 Environment Variables Required

```
JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@domain.com
JIRA_API_TOKEN=your-jira-api-token
NODE_ENV=production
PORT=3000 (usually auto-set by platform)
```

## 📊 Monitoring

Each deployment includes:
- `/health` - Health check endpoint
- `/status` - Automation status
- `/trigger` - Manual trigger for testing
- Console logging for debugging

Choose the platform that best fits your needs and follow the specific deployment steps above!
