#!/bin/bash

# Deployment script for Jira Customer Field Automation
# This script sets up the automation on a Linux server

set -e

echo "🚀 Deploying Jira Customer Field Automation..."
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm found: $(npm --version)"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
else
    echo "✅ Dependencies already installed"
fi

# Build TypeScript if dist folder doesn't exist or is empty
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
    echo "🔨 Building TypeScript..."
    npm run build
else
    echo "✅ TypeScript already compiled"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your configuration:"
        echo "   - JIRA_URL"
        echo "   - JIRA_EMAIL" 
        echo "   - JIRA_API_TOKEN"
        echo "   - PROJECT_KEY"
        echo "   - CUSTOMER_FIELD_ID"
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file found"
fi

# Test configuration
echo "🧪 Testing configuration..."
if node dist/cli.js test-config; then
    echo "✅ Configuration test passed"
else
    echo "❌ Configuration test failed. Please check your .env file."
    exit 1
fi

# Create systemd service file
echo "📋 Creating systemd service..."
sudo tee /etc/systemd/system/jira-customer-automation.service > /dev/null <<EOF
[Unit]
Description=Jira Customer Field Automation
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$(pwd)
Environment=NODE_ENV=production
ExecStart=$(which node) $(pwd)/dist/customer-field-automation.js continuous 1440 60000
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=jira-customer-automation

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
echo "🔄 Configuring systemd service..."
sudo systemctl daemon-reload
sudo systemctl enable jira-customer-automation.service

# Start the service
echo "▶️  Starting service..."
sudo systemctl start jira-customer-automation.service

# Check service status
echo "📊 Checking service status..."
sudo systemctl status jira-customer-automation.service --no-pager

echo
echo "✅ Deployment completed successfully!"
echo
echo "Service management commands:"
echo "  Start:   sudo systemctl start jira-customer-automation"
echo "  Stop:    sudo systemctl stop jira-customer-automation"
echo "  Restart: sudo systemctl restart jira-customer-automation"
echo "  Status:  sudo systemctl status jira-customer-automation"
echo "  Logs:    sudo journalctl -u jira-customer-automation -f"
echo
echo "The service will automatically start on system boot."
echo "State file will be created at: $(pwd)/customer-automation-state.json"
