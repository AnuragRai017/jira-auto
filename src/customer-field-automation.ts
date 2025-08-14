#!/usr/bin/env node

import axios, { AxiosResponse } from 'axios';
import * as dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

// Load environment variables
dotenv.config();

// Configuration interfaces
interface CustomerMappings {
    emailToCustomer: { [email: string]: string };
    nameToCustomer: { [name: string]: string };
    domainToCustomer: { [domain: string]: string };
}

interface JiraReporter {
    emailAddress?: string;
    displayName?: string;
    name?: string;
}

interface JiraIssue {
    key: string;
    fields: {
        reporter: JiraReporter;
        created: string;
        updated: string;
        summary: string;
        [customFieldId: string]: any;
    };
}

interface JiraSearchResponse {
    issues: JiraIssue[];
    total: number;
}

interface ProcessingState {
    lastRunTimestamp: string;
    processedTickets: string[];
}

class CustomerFieldAutomation {
    private jiraUrl: string;
    private auth: { username: string; password: string };
    private projectKey: string;
    private customerFieldId: string;
    private customerMappings: CustomerMappings;
    private stateFilePath: string;

    constructor() {
        // Environment validation
        const jiraUrl = process.env.JIRA_URL;
        const email = process.env.JIRA_EMAIL;
        const apiToken = process.env.JIRA_API_TOKEN;

        if (!jiraUrl || !email || !apiToken) {
            throw new Error('Missing required environment variables: JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN');
        }

        this.jiraUrl = jiraUrl;
        this.auth = { username: email, password: apiToken };
        this.projectKey = process.env.PROJECT_KEY || 'TS';
        this.customerFieldId = process.env.CUSTOMER_FIELD_ID || 'customfield_10485';
        this.stateFilePath = path.join(process.cwd(), 'customer-automation-state.json');

        // Customer mappings
        this.customerMappings = {
            emailToCustomer: {
                'kelli-ann.bailey@carelon.com': 'Elevance-Carelon',
                'edna.villareal@findheadway.com': 'Headway',
                'luis.valdez@findheadway.com': 'Headway',
                'katie.cassidy@findheadway.com': 'Headway',
                'stephani.vasquez@findheadway.com': 'Headway',
                'gavin.green@findheadway.com': 'Headway',
                'valorie.reyes@findheadway.com': 'Headway',
                'amy.huh@findheadway.com': 'Headway',
                'c.smith@scanhealthplan.com': 'SCAN',
                'b.chan@scanhealthplan.com': 'SCAN',
                'li.lopez@scanhealthplan.com': 'SCAN',
                'a.liu@scanhealthplan.com': 'SCAN',
                'evo@scanhealthplan.com': 'SCAN',
                'a.vuc@scanhealthplan.com': 'SCAN',
                'mo.davila@scanhealthplan.com': 'SCAN',
                'aimee.kulp@hsc.utah.edu': 'UUHP (University of Utah)'
            },
            nameToCustomer: {
                'cindy bergley': 'FCHN',
                'abby fuller': 'FCHN',
                'tanya ramirez': 'FCHN',
                'steffany taylor': 'FCHN',
                'zara aghajanyan': 'Headway',
                'carrie black': 'SCAN',
                'charlene frail-mcgeever': 'UUHP (University of Utah)',
                'charlene frail mcgeever': 'UUHP (University of Utah)'
            },
            domainToCustomer: {
                'carelon.com': 'Elevance-Carelon',
                'findheadway.com': 'Headway',
                'scanhealthplan.com': 'SCAN',
                'hsc.utah.edu': 'UUHP (University of Utah)',
                'utah.edu': 'UUHP (University of Utah)'
            }
        };
    }

    /**
     * Format date for JIRA API queries
     */
    private formatDateForJIRA(date: Date): string {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    /**
     * Load processing state from file
     */
    private loadState(): ProcessingState {
        try {
            if (fs.existsSync(this.stateFilePath)) {
                const data = fs.readFileSync(this.stateFilePath, 'utf8');
                return JSON.parse(data);
            }
        } catch (error) {
            console.warn('Could not load state file, using defaults:', error);
        }

        // Default state - last 24 hours
        return {
            lastRunTimestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            processedTickets: []
        };
    }

    /**
     * Save processing state to file
     */
    private saveState(state: ProcessingState): void {
        try {
            fs.writeFileSync(this.stateFilePath, JSON.stringify(state, null, 2));
        } catch (error) {
            console.error('Could not save state file:', error);
        }
    }

    /**
     * Get customer name from reporter information
     */
    private getCustomerFromReporter(reporter: JiraReporter): string | null {
        if (!reporter) return null;

        const reporterEmail = reporter.emailAddress?.toLowerCase() || '';
        const reporterDisplayName = reporter.displayName?.toLowerCase() || '';
        const reporterName = reporter.name?.toLowerCase() || '';

        // Check specific email mapping
        if (reporterEmail && this.customerMappings.emailToCustomer[reporterEmail]) {
            return this.customerMappings.emailToCustomer[reporterEmail];
        }

        // Check display name mapping
        if (reporterDisplayName && this.customerMappings.nameToCustomer[reporterDisplayName]) {
            return this.customerMappings.nameToCustomer[reporterDisplayName];
        }

        // Check name mapping
        if (reporterName && this.customerMappings.nameToCustomer[reporterName]) {
            return this.customerMappings.nameToCustomer[reporterName];
        }

        // Check domain mapping
        if (reporterEmail) {
            const domain = reporterEmail.split('@')[1];
            if (this.customerMappings.domainToCustomer[domain]) {
                return this.customerMappings.domainToCustomer[domain];
            }
        }

        return null;
    }

    /**
     * Get newly created tickets from JIRA
     */
    async getNewlyCreatedTickets(lastRunTime: Date): Promise<JiraIssue[]> {
        const formattedTime = this.formatDateForJIRA(lastRunTime);
        
        const jql = `project = ${this.projectKey} AND assignee is EMPTY AND resolution = Unresolved AND status != Done AND "issuetype" = "Support Ticket" AND "Request Type" NOT IN ("Outreach Inbox Emailed request (TS)","Credentialing Inbox Emailed request (TS)") AND created >= "${formattedTime}" ORDER BY created DESC`;
        
        try {
            console.log(`🔍 Looking for tickets created since: ${formattedTime}`);
            
            const response: AxiosResponse<JiraSearchResponse> = await axios.post(
                `${this.jiraUrl}/rest/api/2/search`,
                {
                    jql: jql,
                    fields: ['reporter', this.customerFieldId, 'summary', 'key', 'created', 'updated'],
                    maxResults: 50
                },
                {
                    auth: this.auth,
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                }
            );

            const issues = response.data.issues || [];
            console.log(`Found ${issues.length} newly created tickets`);
            return issues;

        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error(`❌ Error getting newly created tickets: ${error.response?.status} ${error.response?.statusText}`);
                console.error(`Response: ${JSON.stringify(error.response?.data, null, 2)}`);
            } else {
                console.error('❌ Error getting newly created tickets:', error);
            }
            return [];
        }
    }

    /**
     * Update customer field for an issue
     */
    async updateCustomerField(issueKey: string, customerNames: string[]): Promise<boolean> {
        try {
            const updateData = {
                fields: {
                    [this.customerFieldId]: customerNames.map(name => ({ value: name }))
                }
            };

            const response = await axios.put(
                `${this.jiraUrl}/rest/api/2/issue/${issueKey}`,
                updateData,
                {
                    auth: this.auth,
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                }
            );

            return response.status === 204;

        } catch (error) {
            if (axios.isAxiosError(error)) {
                console.error(`❌ Failed to update ${issueKey}: ${error.response?.status} ${error.response?.statusText}`);
                console.error(`Response: ${JSON.stringify(error.response?.data, null, 2)}`);
            } else {
                console.error(`❌ Error updating ${issueKey}:`, error);
            }
            return false;
        }
    }

    /**
     * Process new tickets and update customer fields
     */
    async processNewTickets(): Promise<void> {
        try {
            console.log(`🔍 [${new Date().toLocaleTimeString()}] Scanning for new tickets...`);
            
            const state = this.loadState();
            const lastRunTime = new Date(state.lastRunTimestamp);
            
            const tickets = await this.getNewlyCreatedTickets(lastRunTime);
            
            if (tickets.length === 0) {
                console.log('✅ No new tickets found');
                state.lastRunTimestamp = new Date().toISOString();
                this.saveState(state);
                return;
            }
            
            console.log(`🎫 Found ${tickets.length} NEW tickets to process`);
            
            let updatedCount = 0;
            let skippedCount = 0;
            
            for (const ticket of tickets) {
                const issueKey = ticket.key;
                const reporter = ticket.fields.reporter;
                const currentCustomerField = ticket.fields[this.customerFieldId];
                const createdTime = new Date(ticket.fields.created);
                
                console.log(`\n📋 NEW TICKET: ${issueKey} | Created: ${createdTime.toLocaleString()}`);
                
                // Skip if already processed
                if (state.processedTickets.includes(issueKey)) {
                    console.log(`   ⚠️  Already processed - skipping`);
                    skippedCount++;
                    continue;
                }

                if (!reporter) {
                    console.log(`   ⚠️  No reporter - skipping`);
                    state.processedTickets.push(issueKey);
                    skippedCount++;
                    continue;
                }
                
                const detectedCustomer = this.getCustomerFromReporter(reporter);
                
                if (!detectedCustomer) {
                    console.log(`   ⚠️  No customer mapping for: ${reporter.displayName || reporter.emailAddress}`);
                    state.processedTickets.push(issueKey);
                    skippedCount++;
                    continue;
                }
                
                const currentCustomerValues = currentCustomerField || [];
                const hasCustomer = currentCustomerValues.some((val: any) => val.value === detectedCustomer);
                
                if (hasCustomer) {
                    console.log(`   ✅ Already has customer: ${detectedCustomer}`);
                    state.processedTickets.push(issueKey);
                    skippedCount++;
                    continue;
                }
                
                console.log(`   🎯 Setting customer: ${detectedCustomer}`);
                
                const existingCustomers = currentCustomerValues.map((val: any) => val.value);
                const newCustomers = [...existingCustomers, detectedCustomer];
                
                if (await this.updateCustomerField(issueKey, newCustomers)) {
                    console.log(`   ✅ SUCCESS: Updated ${issueKey}`);
                    state.processedTickets.push(issueKey);
                    updatedCount++;
                } else {
                    console.log(`   ❌ FAILED: Could not update ${issueKey}`);
                }
            }
            
            // Update state
            state.lastRunTimestamp = new Date().toISOString();
            
            // Keep only last 1000 processed tickets
            if (state.processedTickets.length > 1000) {
                state.processedTickets = state.processedTickets.slice(-1000);
            }
            
            this.saveState(state);
            
            console.log(`\n📊 SUMMARY: ${updatedCount} updated, ${skippedCount} skipped`);
            
        } catch (error) {
            console.error('❌ Critical error in processNewTickets:', error);
        }
    }

    /**
     * Run a backup scan for the last 24 hours
     */
    async dailyBackupScan(): Promise<void> {
        console.log('🔍 BACKUP SCAN: Checking for any missed tickets from last 24 hours');
        
        const state = this.loadState();
        state.lastRunTimestamp = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        this.saveState(state);
        
        await this.processNewTickets();
    }

    /**
     * Check automation status
     */
    async checkStatus(): Promise<void> {
        const state = this.loadState();
        const lastRun = new Date(state.lastRunTimestamp);
        const processedCount = state.processedTickets.length;
        
        console.log('📊 AUTOMATION STATUS:');
        console.log(`   🕐 Last run: ${lastRun.toLocaleString()}`);
        console.log(`   📋 Processed tickets: ${processedCount}`);
        console.log(`   💾 State file: ${this.stateFilePath}`);
        console.log(`   📁 Project: ${this.projectKey}`);
        console.log(`   🏷️  Customer field: ${this.customerFieldId}`);
    }

    /**
     * Reset all data
     */
    async resetEverything(): Promise<void> {
        console.log('🔄 RESETTING ALL DATA');
        
        try {
            if (fs.existsSync(this.stateFilePath)) {
                fs.unlinkSync(this.stateFilePath);
            }
            console.log('✅ Reset complete. Run processNewTickets() to restart.');
        } catch (error) {
            console.error('Error during reset:', error);
        }
    }

    /**
     * Run continuous monitoring (for manual execution)
     */
    async runContinuous(maxIterations: number = 60, intervalMs: number = 5000): Promise<void> {
        console.log(`🚀 STARTING CONTINUOUS JIRA CUSTOMER FIELD AUTOMATION`);
        console.log(`📅 Starting: ${new Date().toLocaleString()}`);
        console.log(`🔄 Will run ${maxIterations} iterations with ${intervalMs}ms intervals`);
        
        for (let i = 0; i < maxIterations; i++) {
            console.log(`\n🔄 Cycle ${i + 1}/${maxIterations}`);
            await this.processNewTickets();
            
            if (i < maxIterations - 1) {
                console.log(`⏳ Waiting ${intervalMs}ms before next cycle...`);
                await new Promise(resolve => setTimeout(resolve, intervalMs));
            }
        }
        
        console.log('\n🏁 Continuous monitoring completed');
    }
}

// CLI functionality
async function main(): Promise<void> {
    const args = process.argv.slice(2);
    const command = args[0] || 'help';

    try {
        const automation = new CustomerFieldAutomation();

        switch (command) {
            case 'process':
                await automation.processNewTickets();
                break;

            case 'continuous':
                const iterations = parseInt(args[1]) || 60;
                const interval = parseInt(args[2]) || 5000;
                await automation.runContinuous(iterations, interval);
                break;

            case 'backup-scan':
                await automation.dailyBackupScan();
                break;

            case 'status':
                await automation.checkStatus();
                break;

            case 'reset':
                await automation.resetEverything();
                break;

            case 'help':
            default:
                console.log('🔧 Jira Customer Field Automation - Available Commands:');
                console.log('');
                console.log('  process              - Process new tickets once');
                console.log('  continuous [n] [ms]  - Run continuous monitoring (default: 60 cycles, 5000ms interval)');
                console.log('  backup-scan          - Scan last 24 hours for missed tickets');
                console.log('  status               - Show current status');
                console.log('  reset                - Reset all stored data');
                console.log('  help                 - Show this help');
                console.log('');
                console.log('Examples:');
                console.log('  npm run customer-automation process');
                console.log('  npm run customer-automation continuous 30 3000');
                console.log('  npm run customer-automation status');
                break;
        }

    } catch (error) {
        console.error('❌ Command failed:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}

export { CustomerFieldAutomation };
