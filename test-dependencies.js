#!/usr/bin/env node
// Quick deployment test for dependencies
console.log('🧪 Testing deployment dependencies...');

try {
  console.log('✅ Testing Express...');
  const express = require('express');
  console.log(`   Express version: ${express.version || 'loaded successfully'}`);
  
  console.log('✅ Testing Axios...');
  const axios = require('axios');
  console.log(`   Axios version: ${axios.VERSION || 'loaded successfully'}`);
  
  console.log('✅ Testing Winston...');
  const winston = require('winston');
  console.log(`   Winston version: ${winston.version || 'loaded successfully'}`);
  
  console.log('✅ Testing dotenv...');
  const dotenv = require('dotenv');
  console.log(`   Dotenv loaded successfully`);
  
  console.log('✅ Testing yargs...');
  const yargs = require('yargs');
  console.log(`   Yargs loaded successfully`);
  
  console.log('\n🎉 All dependencies loaded successfully!');
  console.log('🚀 Ready for deployment!');
  
} catch (error) {
  console.error('❌ Dependency test failed:', error.message);
  process.exit(1);
}
