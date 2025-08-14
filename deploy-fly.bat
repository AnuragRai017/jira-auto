# Deploy to Fly.io
flyctl auth login
flyctl launch --no-deploy
flyctl secrets set JIRA_URL=https://your-domain.atlassian.net
flyctl secrets set JIRA_EMAIL=your-email@domain.com
flyctl secrets set JIRA_API_TOKEN=your-jira-api-token
flyctl secrets set NODE_ENV=production
flyctl deploy

echo "✅ Deployed to Fly.io! Your app is now running."
