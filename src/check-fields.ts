/**
 * Check fields for a specific issue to verify the Ops Team Designation field.
 * This is useful for debugging issues with field values.
 * 
 * Usage:
 *   ts-node src/check-fields.ts --issue-key TS-24130
 */

import * as dotenv from 'dotenv';
import axios from 'axios';
import * as yargs from 'yargs';

dotenv.config();

interface FieldMapping {
  [fieldName: string]: string;
}

interface CliArguments {
  'issue-key': string;
}

const fieldIds: FieldMapping = {
  'Ops Team Designation': 'customfield_10249',
  'Customer(s)': 'customfield_10485',
  'Type of Request': 'customfield_10617'
};

function extractTextFromADF(adfDoc: any): string {
  const text: string[] = [];
  
  const processContent = (content: any): void => {
    if (Array.isArray(content)) {
      content.forEach(item => processContent(item));
    } else if (content && typeof content === 'object') {
      if (content.type === 'text') {
        text.push(content.text || '');
      }
      if (content.content) {
        processContent(content.content);
      }
    }
  };
  
  processContent(adfDoc.content || []);
  return text.join('');
}

async function main(): Promise<void> {
  const argv = yargs
    .option('issue-key', {
      type: 'string',
      required: true,
      description: 'Issue key to check'
    })
    .help()
    .argv as CliArguments;

  // Initialize axios with authentication
  const axiosInstance = axios.create({
    baseURL: process.env.JIRA_URL || 'https://your-domain.atlassian.net',
    auth: {
      username: process.env.JIRA_USERNAME || '',
      password: process.env.JIRA_API_TOKEN || ''
    },
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });

  try {
    // Get issue details
    const response = await axiosInstance.get(`/rest/api/3/issue/${argv['issue-key']}`);
    const issue = response.data;

    if (!issue) {
      console.log(`Issue ${argv['issue-key']} not found`);
      return;
    }

    const fields = issue.fields || {};

    // Print basic issue info
    console.log(`\n=== Issue Details for ${argv['issue-key']} ===`);
    console.log(`Summary: ${fields.summary || 'N/A'}`);
    console.log(`Status: ${fields.status?.name || 'N/A'}`);
    console.log(`Issue Type: ${fields.issuetype?.name || 'N/A'}`);
    console.log(`Reporter: ${fields.reporter?.displayName || 'N/A'}`);
    console.log(`Reporter Email: ${fields.reporter?.emailAddress || 'N/A'}`);

    // Print specific fields we care about
    console.log('\n=== Required Fields ===');
    for (const [fieldName, fieldId] of Object.entries(fieldIds)) {
      const fieldValue = fields[fieldId];
      console.log(`${fieldName}: `, { endLine: false });

      if (fieldValue === null || fieldValue === undefined) {
        console.log('NOT SET');
      } else if (Array.isArray(fieldValue)) {
        const values = fieldValue.map(item => {
          if (typeof item === 'object' && item !== null && 'value' in item) {
            return item.value;
          }
          return String(item);
        });
        console.log(values.join(', '));
      } else if (typeof fieldValue === 'object' && fieldValue !== null && 'value' in fieldValue) {
        console.log(fieldValue.value);
      } else {
        console.log(fieldValue);
      }
    }

    // Print description (first 200 chars) for keyword analysis
    const description = fields.description;
    if (description) {
      let descText = '';
      
      if (typeof description === 'string') {
        // Handle plain text description
        descText = description;
      } else if (typeof description === 'object' && description.content) {
        // Handle Atlassian Document Format
        descText = extractTextFromADF(description);
      }
      
      if (descText) {
        console.log(`\nDescription (first 200 chars): ${descText.substring(0, 200)}...`);
      }
    }

    // Print raw field values for debugging
    console.log('\n=== Raw Field Values ===');
    for (const [fieldName, fieldId] of Object.entries(fieldIds)) {
      const fieldValue = fields[fieldId];
      console.log(`${fieldName} (${fieldId}): ${JSON.stringify(fieldValue, null, 2)}`);
    }

  } catch (error: any) {
    console.error('Error:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

function console_log_no_newline(text: string): void {
  process.stdout.write(text);
}

// Extend console with a method to print without newline
declare global {
  interface Console {
    log(message?: any, options?: { endLine: boolean }): void;
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}
