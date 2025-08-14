/**
 * Check available issue types for the TS project.
 * This will help identify the correct issue type ID for Operations Ticket.
 */

import * as https from 'https';
import * as url from 'url';

// Simple HTTP client for Node.js without external dependencies
function makeRequest(options: https.RequestOptions, data?: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (error) {
          reject(new Error(`Failed to parse JSON: ${error}`));
        }
      });
    });

    req.on('error', reject);
    
    if (data) {
      req.write(data);
    }
    
    req.end();
  });
}

async function main(): Promise<void> {
  const jiraUrl = process.env.JIRA_URL || 'https://your-domain.atlassian.net';
  const jiraUsername = process.env.JIRA_USERNAME || '';
  const jiraApiToken = process.env.JIRA_API_TOKEN || '';
  const projectKey = process.env.DEFAULT_PROJECT_KEY || 'TS';

  console.log(`Fetching issue types for project ${projectKey}...`);

  const auth = Buffer.from(`${jiraUsername}:${jiraApiToken}`).toString('base64');
  const baseUrl = new URL(jiraUrl);

  const options: https.RequestOptions = {
    hostname: baseUrl.hostname,
    port: baseUrl.port || 443,
    method: 'GET',
    headers: {
      'Authorization': `Basic ${auth}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  };

  try {
    // Method 1: Get project metadata
    console.log('\n=== Issue Type Method 1: Project Metadata ===');
    
    const projectOptions = { ...options, path: `/rest/api/3/project/${projectKey}` };
    const projectData = await makeRequest(projectOptions);
    
    if (projectData.issueTypes) {
      console.log(`Available issue types for ${projectKey}:`);
      for (const issueType of projectData.issueTypes) {
        console.log(`ID: ${issueType.id}, Name: ${issueType.name}`);
      }
    } else {
      console.log('No issue types found in project data');
    }

    // Method 2: Get all issue types
    console.log('\n=== Issue Type Method 2: All Issue Types ===');
    
    const allTypesOptions = { ...options, path: '/rest/api/3/issuetype' };
    const allTypes = await makeRequest(allTypesOptions);
    
    console.log('All available issue types in the Jira instance:');
    for (const issueType of allTypes) {
      console.log(`ID: ${issueType.id}, Name: ${issueType.name}`);
    }

    // Method 3: Get create metadata
    console.log('\n=== Issue Type Method 3: Create Meta for Project ===');
    
    const createMetaOptions = { ...options, path: `/rest/api/3/issue/createmeta?projectKeys=${projectKey}&expand=projects.issuetypes` };
    const createMeta = await makeRequest(createMetaOptions);
    
    if (createMeta.projects) {
      for (const project of createMeta.projects) {
        if (project.key === projectKey) {
          console.log(`Available issue types for ${projectKey} from create meta:`);
          for (const issueType of project.issuetypes || []) {
            console.log(`ID: ${issueType.id}, Name: ${issueType.name}`);
          }
        }
      }
    } else {
      console.log('No projects found in create meta');
    }

    // Method 4: Get transitions for sample issue
    console.log('\n=== Available Transitions Method ===');
    const sampleIssueKey = 'TS-24130';
    
    try {
      const transitionsOptions = { ...options, path: `/rest/api/3/issue/${sampleIssueKey}/transitions` };
      const transitions = await makeRequest(transitionsOptions);
      
      console.log(`Available transitions for ${sampleIssueKey}:`);
      if (transitions.transitions) {
        for (const transition of transitions.transitions) {
          console.log(`ID: ${transition.id}, Name: ${transition.name}, To Status: ${transition.to.name}`);
        }
      } else {
        console.log('No transitions found');
      }
    } catch (error) {
      console.log(`Error getting transitions: ${error}`);
    }

  } catch (error: any) {
    console.error('Error:', error.message);
  }
}

if (require.main === module) {
  // Load environment variables manually
  try {
    const fs = require('fs');
    const path = require('path');
    const envPath = path.join(__dirname, '..', '.env');
    
    if (fs.existsSync(envPath)) {
      const envFile = fs.readFileSync(envPath, 'utf8');
      const envLines = envFile.split('\n');
      
      for (const line of envLines) {
        const trimmedLine = line.trim();
        if (trimmedLine && !trimmedLine.startsWith('#')) {
          const [key, ...valueParts] = trimmedLine.split('=');
          if (key && valueParts.length > 0) {
            process.env[key.trim()] = valueParts.join('=').trim();
          }
        }
      }
    }
  } catch (error) {
    console.log('Could not load .env file, using environment variables');
  }

  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
