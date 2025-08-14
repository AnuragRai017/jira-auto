# 🚀 Deployment Guide for Jira Customer Field Automation

This guide provides multiple deployment options for automating your Jira customer field automation system.

## 📋 Prerequisites

Before deploying, ensure you have:

1. ✅ **Built the application**: Run `npm run build`
2. ✅ **Configured environment**: Copy `.env.example` to `.env` and configure
3. ✅ **Tested configuration**: Run `npm run start test-config`

## 🖥️ Windows Deployment Options

### Option 1: Windows Service (Recommended)

**Best for**: Production servers, always-on automation

```powershell
# Install node-windows dependency
npm install

# Install as Windows Service (Run as Administrator)
npm run service:install

# Manage the service
npm run service:start    # Start service
npm run service:stop     # Stop service  
npm run service:uninstall # Remove service
```

**Features**:
- ✅ Runs automatically on system startup
- ✅ Runs in background (no console window)
- ✅ Automatic restart on failure
- ✅ Managed through Windows Services

### Option 2: Scheduled Task

**Best for**: Periodic execution, shared computers

#### PowerShell Method (Recommended):
```powershell
# Run as Administrator
.\create-scheduled-task.ps1

# To remove
.\remove-scheduled-task.ps1
```

#### Batch File Method:
```cmd
REM Run as Administrator
create-scheduled-task.bat

REM To remove
remove-scheduled-task.bat
```

**Features**:
- ✅ Runs every 5 minutes automatically
- ✅ Runs as SYSTEM user
- ✅ Managed through Task Scheduler
- ✅ No console window

## 🐧 Linux Deployment

### Systemd Service (Recommended)

```bash
# Make deployment script executable
chmod +x deploy-linux.sh

# Deploy (requires sudo)
./deploy-linux.sh

# Manage the service
sudo systemctl start jira-customer-automation
sudo systemctl stop jira-customer-automation
sudo systemctl restart jira-customer-automation
sudo systemctl status jira-customer-automation

# View logs
sudo journalctl -u jira-customer-automation -f

# Uninstall
chmod +x uninstall-linux.sh
./uninstall-linux.sh
```

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended)

```bash
# Build and start containers
npm run docker:build
npm run docker:run

# View logs
npm run docker:logs

# Stop containers
npm run docker:stop

# Run backup scan
npm run docker:backup
```

### Option 2: Direct Docker

```bash
# Build image
docker build -t jira-customer-automation .

# Run container with environment file
docker run -d \
  --name jira-customer-automation \
  --env-file .env \
  --restart unless-stopped \
  -v $(pwd)/customer-automation-state.json:/app/customer-automation-state.json \
  jira-customer-automation

# View logs
docker logs -f jira-customer-automation

# Stop container
docker stop jira-customer-automation
```

## ☁️ Cloud Deployment Options

### AWS ECS/Fargate

1. **Push image to ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t jira-automation .
   docker tag jira-automation:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/jira-automation:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/jira-automation:latest
   ```

2. **Create ECS Task Definition** with environment variables from Parameter Store

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name jira-automation \
  --image jira-customer-automation:latest \
  --restart-policy Always \
  --environment-variables JIRA_URL=<url> JIRA_EMAIL=<email> \
  --secure-environment-variables JIRA_API_TOKEN=<token>
```

### Google Cloud Run

```bash
gcloud run deploy jira-automation \
  --image gcr.io/PROJECT-ID/jira-automation \
  --platform managed \
  --set-env-vars JIRA_URL=<url>,JIRA_EMAIL=<email> \
  --set-secrets JIRA_API_TOKEN=jira-token:latest
```

## 🔧 Configuration Management

### Environment Variables

Required variables for all deployment methods:

```env
# Jira Configuration
JIRA_URL=https://certifyos.atlassian.net
JIRA_EMAIL=anurag.rai@certifyos.com
JIRA_API_TOKEN=your-api-token-here

# Project Configuration  
PROJECT_KEY=TS
CUSTOMER_FIELD_ID=customfield_10485
```

### Automation Settings

You can customize the automation behavior:

| Setting | Environment Variable | Default | Description |
|---------|---------------------|---------|-------------|
| Iterations | - | 1440 | How many cycles to run (1440 = 24 hours at 1 minute intervals) |
| Interval | - | 60000 | Milliseconds between cycles (60000 = 1 minute) |
| Log Level | `LOG_LEVEL` | info | Logging verbosity (error, warn, info, debug) |
| Max Results | `MAX_RESULTS` | 50 | Maximum tickets to process per cycle |

## 📊 Monitoring and Maintenance

### Health Checks

All deployment methods include health monitoring:

- **Windows Service**: Automatic restart on failure
- **Scheduled Task**: Task Scheduler monitoring
- **Linux Systemd**: Service status monitoring
- **Docker**: Built-in healthcheck

### Log Monitoring

**Windows Service**:
- Event Viewer → Windows Logs → Application
- Filter by Source: "jira-customer-automation"

**Scheduled Task**:
- Task Scheduler → Task History
- Event Viewer → Applications and Services Logs

**Linux Systemd**:
```bash
# Real-time logs
sudo journalctl -u jira-customer-automation -f

# Recent logs
sudo journalctl -u jira-customer-automation --since "1 hour ago"
```

**Docker**:
```bash
# Container logs
docker logs -f jira-customer-automation

# Docker Compose logs
docker-compose logs -f
```

### State File Management

The automation maintains state in `customer-automation-state.json`:

- **Location**: Same directory as the application
- **Purpose**: Tracks last run time and processed tickets
- **Backup**: Consider backing up this file periodically
- **Reset**: Delete file to reset automation state

## 🚨 Troubleshooting

### Common Issues

1. **"Missing environment variables"**:
   - Ensure `.env` file exists and is properly configured
   - For services, ensure environment variables are accessible

2. **"Permission denied"**:
   - Windows: Run as Administrator
   - Linux: Use `sudo` for system service operations

3. **"Port already in use"**:
   - Check for existing instances
   - Stop conflicting services

4. **"Authentication failed"**:
   - Verify JIRA API token is valid
   - Check JIRA URL format (include https://)

### Getting Help

1. **Test configuration**: `npm run start test-config`
2. **Check status**: `npm run start customer-fields status`
3. **Manual run**: `npm run start customer-fields process`
4. **View logs**: Use appropriate log viewing method for your deployment

## 📈 Scaling Considerations

### High Volume Environments

For organizations processing many tickets:

1. **Increase polling frequency**: Reduce interval (e.g., 30 seconds)
2. **Horizontal scaling**: Deploy multiple instances with different JQL filters
3. **Database optimization**: Consider external state storage for multiple instances
4. **Rate limiting**: Respect Jira API rate limits

### Load Balancing

For multiple instances:
- Use different PROJECT_KEY values
- Implement instance-specific JQL queries
- Consider Redis for shared state management

## 🔄 Updates and Maintenance

### Updating the Application

1. **Stop the service**
2. **Pull latest changes**
3. **Run `npm install` and `npm run build`**
4. **Restart the service**

### Backup Strategy

Important files to backup:
- `.env` - Configuration
- `customer-automation-state.json` - Processing state
- `src/customer-field-automation.ts` - Custom mappings

## 📞 Support

For deployment issues:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Test with manual execution first
4. Check service logs for specific errors
