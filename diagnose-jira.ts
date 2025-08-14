#!/usr/bin/env node

// Jira Configuration Diagnostic Tool
import axios from 'axios';
import * as dotenv from 'dotenv';

dotenv.config();

const JIRA_URL = process.env.JIRA_URL || 'https://your-domain.atlassian.net';
const JIRA_EMAIL = process.env.JIRA_EMAIL || 'your-email@domain.com';
const JIRA_API_TOKEN = process.env.JIRA_API_TOKEN || 'your-api-token';

const auth = {
    username: JIRA_EMAIL,
    password: JIRA_API_TOKEN
};

console.log('🔍 Jira Configuration Diagnostic');
console.log('================================');
console.log(`🌐 Jira URL: ${JIRA_URL}`);
console.log(`👤 Email: ${JIRA_EMAIL}`);
console.log(`🔑 API Token: ${JIRA_API_TOKEN ? '*'.repeat(20) : 'NOT SET'}`);
console.log('');

async function checkJiraConnection() {
    try {
        console.log('1️⃣ Testing connection and authentication...');
        
        const response = await axios.get(`${JIRA_URL}/rest/api/3/myself`, {
            auth: auth
        });
        
        console.log(`✅ Authentication successful!`);
        console.log(`   User: ${response.data.displayName} (${response.data.emailAddress})`);
        console.log('');
        
        return true;
    } catch (error: any) {
        console.log('❌ Authentication failed!');
        console.log(`   Error: ${error.response?.status} - ${error.response?.statusText}`);
        if (error.response?.data) {
            console.log(`   Details: ${JSON.stringify(error.response.data)}`);
        }
        console.log('');
        return false;
    }
}

async function getProjects() {
    try {
        console.log('2️⃣ Getting available projects...');
        
        const response = await axios.get(`${JIRA_URL}/rest/api/3/project`, {
            auth: auth
        });
        
        console.log(`✅ Found ${response.data.length} projects:`);
        response.data.slice(0, 10).forEach((project: any) => {
            console.log(`   📁 ${project.key} - ${project.name}`);
        });
        
        if (response.data.length > 10) {
            console.log(`   ... and ${response.data.length - 10} more`);
        }
        console.log('');
        
        return response.data;
    } catch (error: any) {
        console.log('❌ Failed to get projects!');
        console.log(`   Error: ${error.response?.status} - ${error.response?.statusText}`);
        console.log('');
        return [];
    }
}

async function getIssueTypes(projectKey: string) {
    try {
        console.log(`3️⃣ Getting issue types for project ${projectKey}...`);
        
        const response = await axios.get(`${JIRA_URL}/rest/api/3/project/${projectKey}`, {
            auth: auth
        });
        
        const issueTypes = response.data.issueTypes || [];
        console.log(`✅ Found ${issueTypes.length} issue types:`);
        issueTypes.forEach((type: any) => {
            console.log(`   🎫 ${type.name} (ID: ${type.id})`);
        });
        console.log('');
        
        return issueTypes;
    } catch (error: any) {
        console.log(`❌ Failed to get issue types for ${projectKey}!`);
        console.log(`   Error: ${error.response?.status} - ${error.response?.statusText}`);
        console.log('');
        return [];
    }
}

async function testSimpleQuery(projectKey: string) {
    try {
        console.log(`4️⃣ Testing simple query for project ${projectKey}...`);
        
        const jql = `project = "${projectKey}" ORDER BY created DESC`;
        
        const response = await axios.post(`${JIRA_URL}/rest/api/3/search`, {
            jql: jql,
            maxResults: 5,
            fields: ['key', 'summary', 'issuetype', 'created', 'reporter']
        }, {
            auth: auth,
            headers: { 'Content-Type': 'application/json' }
        });
        
        console.log(`✅ Query successful! Found ${response.data.total} total issues`);
        console.log(`   Recent issues:`);
        response.data.issues.slice(0, 3).forEach((issue: any) => {
            console.log(`   📋 ${issue.key} - ${issue.fields.summary.substring(0, 50)}...`);
            console.log(`      Type: ${issue.fields.issuetype.name}, Created: ${issue.fields.created}`);
        });
        console.log('');
        
        return true;
    } catch (error: any) {
        console.log(`❌ Query failed for ${projectKey}!`);
        console.log(`   Error: ${error.response?.status} - ${error.response?.statusText}`);
        if (error.response?.data) {
            console.log(`   Details: ${JSON.stringify(error.response.data, null, 2)}`);
        }
        console.log('');
        return false;
    }
}

async function main() {
    // Test authentication
    const authSuccess = await checkJiraConnection();
    if (!authSuccess) {
        console.log('🚨 Fix authentication first before proceeding!');
        return;
    }
    
    // Get projects
    const projects = await getProjects();
    if (projects.length === 0) {
        return;
    }
    
    // Test with first few projects
    const testProjects = projects.slice(0, 3);
    for (const project of testProjects) {
        await getIssueTypes(project.key);
        await testSimpleQuery(project.key);
    }
    
    console.log('🎯 RECOMMENDATIONS:');
    console.log('==================');
    console.log('1. Use one of the project keys listed above');
    console.log('2. Update your environment variables in Render.com:');
    console.log('   - PROJECT_KEY=<correct-project-key>');
    console.log('3. Verify issue type names match what\'s available');
    console.log('4. Check custom field names in Jira admin');
}

main().catch(console.error);
