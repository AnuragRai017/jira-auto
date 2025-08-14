# 🔧 Jira Configuration Fix Guide

## ❌ Current Issues:
1. Project "TS" doesn't exist in your Jira
2. Custom field "Request Type" doesn't exist or isn't accessible
3. Complex JQL query with hardcoded values

## ✅ Solutions:

### Step 1: Find Correct Project Key
In your Jira instance (https://certifyos.atlassian.net):
1. Go to Projects
2. Find your support project
3. Note the project KEY (usually 2-4 letters)

Common project keys to try:
- `CERTIFYOS`
- `CS`
- `SUPPORT`
- `HELP`
- `DESK`

### Step 2: Update Render.com Environment Variables
Go to Render.com → Your Service → Environment → Edit:

```
PROJECT_KEY=CERTIFYOS        # Replace with actual project key
CUSTOMER_FIELD_ID=customfield_10001  # Replace with actual field ID  
```

### Step 3: Simplified JQL Query (Temporary Fix)

Replace the complex query with a simple one to test:

**Current (Complex):**
```
project = TS AND assignee is EMPTY AND resolution = Unresolved AND status != Done AND "issuetype" = "Support Ticket" AND "Request Type" NOT IN (...)
```

**Simplified (For Testing):**
```
project = CERTIFYOS AND created >= -2d ORDER BY created DESC
```

### Step 4: Test the Fix

Once you update the environment variables in Render.com:
1. The service will automatically restart
2. Check logs to see if queries work
3. Test the endpoint: https://jira-auto-mh0g.onrender.com/trigger

### Step 5: Find Custom Field IDs

To find the correct custom field IDs:
1. Go to Jira → Settings → Issues → Custom Fields
2. Find "Customer" or similar field
3. Note the field ID (usually like "customfield_10001")

## 🎯 Quick Fix Commands:

**For Render.com Environment Variables:**
```
PROJECT_KEY=CERTIFYOS
CUSTOMER_FIELD_ID=customfield_10001
JIRA_URL=https://certifyos.atlassian.net
JIRA_EMAIL=anurag.rai@certifyos.com
JIRA_API_TOKEN=ATATT3xFfGF0BK0DPRifn8dXP3AnH0fS8TKfH-QCU5Ah_h3JxSqxKo0QryD1A0B37gydyLp4QMMPLejMxVbQj9IcsObdIPyF3v8t3y4mTX07XQuCH7B0uBSQFUlkGUMj3IzbUsFx21yBGL-6w0bzXfm2D_XJvsQFBe8a-AF-5epvchUeCMpmAL8=47A52710
NODE_ENV=production
```

This should resolve the "project TS not found" and "Request Type field not found" errors!
