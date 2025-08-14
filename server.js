const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const app = express();
const port = process.env.PORT || 8080; // Cloud Run uses port 8080

// Middleware for JSON parsing
app.use(express.json());

// State management for weekend scheduling
let isAutomationPaused = false;
const stateFile = 'automation-state.json';

// Load state on startup
try {
  if (fs.existsSync(stateFile)) {
    const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    isAutomationPaused = state.isPaused || false;
  }
} catch (error) {
  console.error('Error loading state:', error);
}

// Save state function
const saveState = () => {
  try {
    fs.writeFileSync(stateFile, JSON.stringify({
      isPaused: isAutomationPaused,
      lastUpdated: new Date().toISOString()
    }));
  } catch (error) {
    console.error('Error saving state:', error);
  }
};

// Check if it's weekend
const isWeekend = () => {
  const day = new Date().getDay();
  return day === 0 || day === 6; // Sunday or Saturday
};

// Health check endpoint (required for Cloud Run)
app.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    message: 'Jira automation service is running',
    isPaused: isAutomationPaused,
    isWeekend: isWeekend()
  });
});

// Root endpoint for Cloud Run health checks
app.get('/', (req, res) => {
  res.status(200).json({
    service: 'Jira Automation',
    status: 'running',
    endpoints: {
      health: '/health',
      trigger: '/trigger',
      status: '/status',
      pause: '/pause',
      resume: '/resume'
    }
  });
});

// Manual trigger endpoint
app.post('/trigger', async (req, res) => {
  if (isAutomationPaused) {
    return res.status(400).json({ 
      error: 'Automation is paused',
      reason: 'Manual pause or weekend mode'
    });
  }

  if (isWeekend()) {
    return res.status(400).json({ 
      error: 'Automation paused for weekend',
      message: 'Automation runs Monday-Friday only'
    });
  }

  try {
    console.log('Manual trigger received');
    const child = spawn('node', ['dist/customer-field-automation.js', 'process'], {
      stdio: 'pipe'
    });
    
    let output = '';
    let errorOutput = '';
    
    child.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      console.log(text);
    });
    
    child.stderr.on('data', (data) => {
      const text = data.toString();
      errorOutput += text;
      console.error(text);
    });
    
    child.on('close', (code) => {
      res.status(code === 0 ? 200 : 500).json({ 
        message: code === 0 ? 'Automation completed successfully' : 'Automation completed with errors',
        exitCode: code,
        output: output.substring(0, 1000), // Limit output size
        errors: errorOutput.substring(0, 500)
      });
    });
    
  } catch (error) {
    console.error('Trigger error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Pause endpoint (called by Cloud Scheduler on Friday evening)
app.post('/pause', (req, res) => {
  isAutomationPaused = true;
  saveState();
  console.log('Automation paused for weekend');
  res.json({ 
    message: 'Automation paused for weekend',
    timestamp: new Date().toISOString()
  });
});

// Resume endpoint (called by Cloud Scheduler on Monday morning)
app.post('/resume', (req, res) => {
  isAutomationPaused = false;
  saveState();
  console.log('Automation resumed for weekday');
  res.json({ 
    message: 'Automation resumed for weekday',
    timestamp: new Date().toISOString()
  });
});

// Status endpoint
app.get('/status', (req, res) => {
  try {
    const customerStateFile = 'customer-automation-state.json';
    let customerState = null;
    
    if (fs.existsSync(customerStateFile)) {
      customerState = JSON.parse(fs.readFileSync(customerStateFile, 'utf8'));
    }
    
    res.json({
      service: 'Jira Customer Field Automation',
      isPaused: isAutomationPaused,
      isWeekend: isWeekend(),
      currentTime: new Date().toISOString(),
      lastRun: customerState ? customerState.lastRunTimestamp : 'Never',
      processedTickets: customerState ? customerState.processedTickets.length : 0,
      status: isAutomationPaused ? 'paused' : (isWeekend() ? 'weekend_pause' : 'active'),
      environment: process.env.NODE_ENV || 'development'
    });
  } catch (error) {
    console.error('Status error:', error);
    res.status(500).json({ error: error.message });
  }
});

// Start the main automation if in production and not weekend
if (process.env.NODE_ENV === 'production') {
  console.log('🚀 Starting Jira automation service...');
  console.log(`📅 Current time: ${new Date().toISOString()}`);
  console.log(`🏃 Is weekend: ${isWeekend()}`);
  console.log(`⏸️ Is paused: ${isAutomationPaused}`);
  
  if (!isWeekend() && !isAutomationPaused) {
    console.log('✅ Starting automation in continuous mode for 8 hours...');
    
    const automation = spawn('node', ['dist/customer-field-automation.js', 'continuous', '480', '300000'], {
      stdio: 'inherit'
    });
    
    automation.on('close', (code) => {
      console.log(`📊 Automation process exited with code ${code}`);
    });
    
    automation.on('error', (error) => {
      console.error('❌ Automation process error:', error);
    });
  } else {
    console.log('⏸️ Automation not started - Weekend or manually paused');
  }
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('📤 SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('📤 SIGINT received, shutting down gracefully');
  process.exit(0);
});

app.listen(port, '0.0.0.0', () => {
  console.log(`🌐 Health check server running on port ${port}`);
  console.log(`📡 Endpoints available:`);
  console.log(`   GET  /health - Health check`);
  console.log(`   POST /trigger - Manual trigger`);
  console.log(`   GET  /status - Status info`);
  console.log(`   POST /pause - Pause automation`);
  console.log(`   POST /resume - Resume automation`);
});
