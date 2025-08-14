#!/bin/bash

echo "Installing Jira Automation TypeScript Project..."
echo

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "Node.js found: $(node --version)"

echo
echo "Installing npm dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "Compiling TypeScript..."
npx tsc

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to compile TypeScript"
    exit 1
fi

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Run: npm run start -- --help to see available commands"  
echo "3. Test with: npm run start check-fields"
echo
