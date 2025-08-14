const Service = require('node-windows').Service;
const path = require('path');

// Create a service object
const svc = new Service({
  name: 'Jira Customer Field Automation',
  script: path.join(__dirname, 'dist', 'customer-field-automation.js')
});

svc.on('stop', function() {
  console.log('✅ Jira Customer Field Automation service stopped successfully!');
});

svc.on('error', function(err) {
  console.error('❌ Service error:', err);
});

console.log('🛑 Stopping Jira Customer Field Automation service...');
svc.stop();
