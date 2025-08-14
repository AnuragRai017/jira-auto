#!/bin/bash

echo "========================================"
echo "  JIRA AUTOMATION DEPLOYMENT OPTIONS"
echo "========================================"
echo
echo "Choose your deployment method:"
echo
echo "1. Systemd Service (Recommended for Linux servers)"
echo "   - Runs automatically on startup"
echo "   - Background daemon"
echo "   - Automatic restart on failure"
echo
echo "2. Docker Container (For containerized environments)"
echo "   - Portable and isolated"
echo "   - Easy scaling"
echo "   - Cross-platform"
echo
echo "3. Manual Testing (For development/testing)"
echo "   - Run once manually"
echo "   - See immediate output"
echo "   - Good for troubleshooting"
echo
echo "========================================"
echo

read -p "Select deployment option (1-3): " choice

case $choice in
    1)
        echo
        echo "Installing as Systemd Service..."
        echo
        echo "This requires sudo privileges."
        echo
        read -p "Press Enter to continue..."
        ./deploy-linux.sh
        ;;
    2)
        echo
        echo "Building Docker container..."
        echo
        echo "Make sure Docker is installed and running."
        echo
        read -p "Press Enter to continue..."
        npm run docker:build
        npm run docker:run
        echo
        echo "Container started! Use 'npm run docker:logs' to view logs."
        ;;
    3)
        echo
        echo "Running manual test..."
        echo
        echo "This will process tickets once and exit."
        echo
        read -p "Press Enter to continue..."
        npm run start customer-fields process
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo
echo "========================================"
echo "  DEPLOYMENT COMPLETED"
echo "========================================"
echo
echo "Useful commands:"
echo "  npm run start customer-fields status     - Check automation status"
echo "  npm run start customer-fields process    - Run once manually"
echo "  npm run start test-config                - Test configuration"
echo
echo "For Systemd Service:"
echo "  sudo systemctl start jira-customer-automation    - Start service"
echo "  sudo systemctl stop jira-customer-automation     - Stop service"
echo "  sudo systemctl status jira-customer-automation   - Check status"
echo "  sudo journalctl -u jira-customer-automation -f   - View logs"
echo
echo "For Docker:"
echo "  npm run docker:logs      - View logs"
echo "  npm run docker:stop      - Stop containers"
echo
echo "See DEPLOYMENT.md for detailed instructions."
echo
