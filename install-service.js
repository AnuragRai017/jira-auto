const Service = require('node-windows').Service;
const path = require('path');

// Create a new service object
const svc = new Service({
  name: 'Jira Customer Field Automation',
  description: 'Automatically fills customer fields in Jira Support Tickets based on reporter information',
  script: path.join(__dirname, 'dist', 'customer-field-automation.js'),
  scriptOptions: 'continuous 1440 60000', // Run for 24 hours (1440 minutes) with 1 minute intervals
  nodeOptions: [
    '--harmony',
    '--max_old_space_size=4096'
  ],
  env: [
    {
      name: "NODE_ENV",
      value: "production"
    }
  ],
  workingDirectory: __dirname,
  allowServiceLogon: true
});

// Listen for the "install" event, which indicates the
// process is available as a service.
svc.on('install', function() {
  console.log('✅ Jira Customer Field Automation service installed successfully!');
  console.log('Starting service...');
  svc.start();
});

svc.on('start', function() {
  console.log('✅ Service started successfully!');
  console.log('Service details:');
  console.log(`  Name: ${svc.name}`);
  console.log(`  Description: ${svc.description}`);
  console.log(`  Script: ${svc.script}`);
  console.log(`  Working Directory: ${svc.workingDirectory}`);
  console.log('\nThe service is now running and will automatically start on system boot.');
  console.log('To stop the service: npm run service:stop');
  console.log('To uninstall the service: npm run service:uninstall');
});

svc.on('error', function(err) {
  console.error('❌ Service error:', err);
});

// Check if running as administrator
function isAdmin() {
  try {
    require('child_process').execSync('net session', { stdio: 'ignore' });
    return true;
  } catch (e) {
    return false;
  }
}

if (!isAdmin()) {
  console.error('❌ This script must be run as Administrator!');
  console.log('\nTo run as administrator:');
  console.log('1. Open PowerShell as Administrator');
  console.log('2. Navigate to this directory');
  console.log('3. Run: npm run service:install');
  process.exit(1);
}

console.log('🚀 Installing Jira Customer Field Automation as Windows Service...');
console.log('This may take a few moments...');

// Install the service
svc.install();
