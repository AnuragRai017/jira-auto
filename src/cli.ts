#!/usr/bin/env node

import * as yargs from 'yargs';
import { SimpleTSAutomation } from './simple-ts-automation';
import { CustomerFieldAutomation } from './customer-field-automation';

async function main(): Promise<void> {
    const argv = await yargs
        .usage('Usage: $0 <command> [options]')
        .command('transition <issue-key>', 'Transition a specific issue', (yargs) => {
            return yargs
                .positional('issue-key', {
                    type: 'string',
                    description: 'Jira issue key (e.g., SUP-123)'
                })
                .option('dry-run', {
                    type: 'boolean',
                    description: 'Validate only, do not execute',
                    default: false
                })
                .option('auto-fill', {
                    type: 'boolean',
                    description: 'Automatically fill missing required fields with defaults',
                    default: false
                })
                .option('skip-issue-type-change', {
                    type: 'boolean',
                    description: 'Skip issue type change (useful for workflow restrictions)',
                    default: false
                });
        })
        .command('customer-fields <action>', 'Manage customer field automation', (yargs) => {
            return yargs
                .positional('action', {
                    type: 'string',
                    choices: ['process', 'continuous', 'backup-scan', 'status', 'reset'],
                    description: 'Action to perform'
                })
                .option('iterations', {
                    type: 'number',
                    description: 'Number of iterations for continuous mode',
                    default: 60
                })
                .option('interval', {
                    type: 'number',
                    description: 'Interval in milliseconds for continuous mode',
                    default: 5000
                });
        })
        .command('test-config', 'Test configuration', () => {})
        .demandCommand(1, 'You must specify a command')
        .help()
        .argv;

    try {
        const command = argv._[0] as string;

        switch (command) {
            case 'transition': {
                const issueKey = argv['issue-key'] as string;
                const dryRun = argv['dry-run'] as boolean;
                const autoFill = argv['auto-fill'] as boolean;
                const skipIssueTypeChange = argv['skip-issue-type-change'] as boolean;
                
                if (!issueKey) {
                    console.error('Issue key is required');
                    process.exit(1);
                }
                
                const automation = new SimpleTSAutomation();
                const result = await automation.transitionTicket(issueKey, dryRun, autoFill, skipIssueTypeChange);
                
                console.log(JSON.stringify(result, null, 2));
                
                if (result.success) {
                    console.log(`\n[SUCCESS] Successfully processed ${issueKey}`);
                    if (dryRun) {
                        console.log('   (Dry run - no actual changes made)');
                    }
                    if (autoFill) {
                        console.log('   (Auto-fill enabled - missing fields populated with defaults)');
                    }
                    if (skipIssueTypeChange) {
                        console.log('   (Issue type change was skipped - manual change required)');
                    }
                    process.exit(0);
                } else {
                    console.log(`\n[ERROR] Failed to process ${issueKey}`);
                    process.exit(1);
                }
                break;
            }

            case 'customer-fields': {
                const action = argv.action as string;
                const customerAutomation = new CustomerFieldAutomation();
                
                switch (action) {
                    case 'process':
                        await customerAutomation.processNewTickets();
                        break;
                    case 'continuous':
                        const iterations = argv.iterations as number;
                        const interval = argv.interval as number;
                        await customerAutomation.runContinuous(iterations, interval);
                        break;
                    case 'backup-scan':
                        await customerAutomation.dailyBackupScan();
                        break;
                    case 'status':
                        await customerAutomation.checkStatus();
                        break;
                    case 'reset':
                        await customerAutomation.resetEverything();
                        break;
                    default:
                        console.error('Invalid customer-fields action');
                        process.exit(1);
                }
                break;
            }

            case 'test-config': {
                const automation = new SimpleTSAutomation();
                const configOk = await automation.testConfig();
                if (configOk) {
                    console.log('\n[SUCCESS] Configuration test passed');
                    process.exit(0);
                } else {
                    console.log('\n[ERROR] Configuration test failed');
                    process.exit(1);
                }
                break;
            }

            default:
                console.error(`Unknown command: ${command}`);
                yargs.showHelp();
                process.exit(1);
        }
    } catch (error) {
        console.error('Command failed:', error);
        process.exit(1);
    }
}

// Run if called directly
if (require.main === module) {
    main();
}
