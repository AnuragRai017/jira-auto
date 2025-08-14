# Deploy to Railway
railway login
railway init
railway add
railway up

# Set environment variables
railway variables set JIRA_URL=https://your-domain.atlassian.net
railway variables set JIRA_EMAIL=your-email@domain.com  
railway variables set JIRA_API_TOKEN=your-jira-api-token
railway variables set NODE_ENV=production

echo "✅ Deployed to Railway! Check your dashboard for the live URL."
