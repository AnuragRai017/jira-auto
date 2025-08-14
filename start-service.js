const Service = require('node-windows').Service;
const path = require('path');

// Create a service object
const svc = new Service({
  name: 'Jira Customer Field Automation',
  script: path.join(__dirname, 'dist', 'customer-field-automation.js')
});

svc.on('start', function() {
  console.log('✅ Jira Customer Field Automation service started successfully!');
});

svc.on('error', function(err) {
  console.error('❌ Service error:', err);
});

console.log('🚀 Starting Jira Customer Field Automation service...');
svc.start();
