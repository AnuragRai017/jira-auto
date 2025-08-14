#!/usr/bin/env node

import axios, { AxiosResponse } from 'axios';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config();

interface JiraTransition {
    id: string;
    name: string;
    to: {
        id: string;
        name: string;
        statusCategory: {
            id: number;
            name: string;
            colorName: string;
        };
    };
}

interface JiraTransitionsResponse {
    transitions: JiraTransition[];
}

interface JiraIssue {
    key: string;
    fields: {
        issuetype: {
            id: string;
            name: string;
        };
        status: {
            id: string;
            name: string;
        };
        summary: string;
        reporter: {
            displayName: string;
            emailAddress: string;
        };
    };
}

class IssueTypeTester {
    private jiraUrl: string;
    private auth: { username: string; password: string };

    constructor() {
        const jiraUrl = process.env.JIRA_URL;
        const email = process.env.JIRA_EMAIL;
        const apiToken = process.env.JIRA_API_TOKEN;

        if (!jiraUrl || !email || !apiToken) {
            throw new Error('Missing required environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN');
        }

        this.jiraUrl = jiraUrl;
        this.auth = { username: email, password: apiToken };
    }

    async getIssue(issueKey: string): Promise<JiraIssue> {
        try {
            const response: AxiosResponse<JiraIssue> = await axios.get(
                `${this.jiraUrl}/rest/api/2/issue/${issueKey}`,
                {
                    auth: this.auth,
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            return response.data;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error(`HTTP Error fetching issue: ${error.response?.status} ${error.response?.statusText}`);
                console.error(`Response: ${JSON.stringify(error.response?.data, null, 2)}`);
            } else {
                console.error(`Error fetching issue: ${error}`);
            }
            throw error;
        }
    }

    async getTransitions(issueKey: string): Promise<JiraTransition[]> {
        try {
            const response: AxiosResponse<JiraTransitionsResponse> = await axios.get(
                `${this.jiraUrl}/rest/api/2/issue/${issueKey}/transitions`,
                {
                    auth: this.auth,
                    headers: {
                        'Accept': 'application/json'
                    }
                }
            );

            return response.data.transitions;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error(`HTTP Error fetching transitions: ${error.response?.status} ${error.response?.statusText}`);
                console.error(`Response: ${JSON.stringify(error.response?.data, null, 2)}`);
            } else {
                console.error(`Error fetching transitions: ${error}`);
            }
            throw error;
        }
    }

    async testIssueTypeChange(issueKey: string, dryRun: boolean = true): Promise<void> {
        console.log(`Testing issue type change for ${issueKey}...`);
        console.log(`Dry run: ${dryRun ? 'YES' : 'NO'}`);
        console.log('=' .repeat(50));

        // Get current issue details
        const issue = await this.getIssue(issueKey);
        
        console.log(`Current Issue Details:`);
        console.log(`  Key: ${issue.key}`);
        console.log(`  Summary: ${issue.fields.summary}`);
        console.log(`  Type: ${issue.fields.issuetype.name} (ID: ${issue.fields.issuetype.id})`);
        console.log(`  Status: ${issue.fields.status.name} (ID: ${issue.fields.status.id})`);
        console.log(`  Reporter: ${issue.fields.reporter.displayName} (${issue.fields.reporter.emailAddress})`);

        // Get available transitions
        const transitions = await this.getTransitions(issueKey);
        
        console.log(`\nAvailable Transitions (${transitions.length}):`);
        transitions.forEach(transition => {
            console.log(`  ID: ${transition.id.padEnd(3)} | ${transition.name} → ${transition.to.name}`);
        });

        // Look for specific transitions we care about
        const targetTransitions = [
            'To Operations Ticket',
            'Operations Ticket',
            'Move to Operations',
            'Convert to Operations'
        ];

        console.log(`\nLooking for target transitions:`);
        const foundTransitions = transitions.filter(t => 
            targetTransitions.some(target => 
                t.name.toLowerCase().includes(target.toLowerCase()) ||
                t.to.name.toLowerCase().includes('operation')
            )
        );

        if (foundTransitions.length > 0) {
            console.log('✓ Found potential transitions:');
            foundTransitions.forEach(t => {
                console.log(`  ${t.name} (ID: ${t.id}) → ${t.to.name}`);
            });

            if (!dryRun && foundTransitions.length > 0) {
                const firstTransition = foundTransitions[0];
                console.log(`\n⚠️  Would execute transition: ${firstTransition.name}`);
                console.log('   (Set dryRun=false in code to actually execute)');
            }
        } else {
            console.log('✗ No matching transitions found');
        }

        // Check if current status allows transitions
        if (transitions.length === 0) {
            console.log('\n⚠️  Warning: No transitions available from current status');
        }
    }
}

async function main(): Promise<void> {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('Usage: node test-issue-type-change.js <ISSUE-KEY> [--execute]');
        console.log('Example: node test-issue-type-change.js SUP-123');
        console.log('Example: node test-issue-type-change.js SUP-123 --execute');
        process.exit(1);
    }

    const issueKey = args[0];
    const dryRun = !args.includes('--execute');

    try {
        const tester = new IssueTypeTester();
        await tester.testIssueTypeChange(issueKey, dryRun);
    } catch (error) {
        console.error('Failed to test issue type change:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

export { IssueTypeTester };
