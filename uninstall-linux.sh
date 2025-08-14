#!/bin/bash

# Uninstall script for Jira Customer Field Automation on Linux

echo "🛑 Uninstalling Jira Customer Field Automation..."
echo

# Stop the service
echo "Stopping service..."
sudo systemctl stop jira-customer-automation.service || echo "Service was not running"

# Disable the service
echo "Disabling service..."
sudo systemctl disable jira-customer-automation.service || echo "Service was not enabled"

# Remove service file
echo "Removing service file..."
sudo rm -f /etc/systemd/system/jira-customer-automation.service

# Reload systemd
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo
echo "✅ Service uninstalled successfully!"
echo
echo "Note: Application files are still present in $(pwd)"
echo "To completely remove, delete this directory manually."
