const Service = require('node-windows').Service;
const path = require('path');

// Create a service object with the same configuration as install
const svc = new Service({
  name: 'Jira Customer Field Automation',
  script: path.join(__dirname, 'dist', 'customer-field-automation.js')
});

// Listen for the "uninstall" event
svc.on('uninstall', function() {
  console.log('✅ Jira Customer Field Automation service uninstalled successfully!');
  console.log('The service has been removed from Windows Services.');
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
  console.log('3. Run: npm run service:uninstall');
  process.exit(1);
}

console.log('🛑 Uninstalling Jira Customer Field Automation Windows Service...');

// First stop the service if it's running
try {
  svc.stop();
  console.log('Service stopped.');
} catch (e) {
  console.log('Service was not running.');
}

// Then uninstall it
svc.uninstall();
