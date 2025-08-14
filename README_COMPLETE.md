# Jira Automation - TypeScript Version

A comprehensive TypeScript-based automation system for managing Jira tickets, including:

1. **Ticket Transition Automation**: Converts Support Tickets to Operations Tickets
2. **Customer Field Automation**: Automatically fills customer fields based on reporter information
3. **Comprehensive Utilities**: Field checking, issue type validation, and testing tools

## Features

### Core Automation
- **Automated Ticket Processing**: Converts Support Tickets to Operations Tickets based on configurable criteria
- **Reporter Validation**: Validates ticket reporters against allowed email addresses and domains
- **Multiple Fallback Strategies**: Tries different approaches to ensure successful ticket transitions
- **Comprehensive Logging**: Detailed audit trail of all automation activities

### Customer Field Management
- **Automatic Customer Detection**: Maps reporters to customers based on email addresses, names, and domains
- **Continuous Monitoring**: Monitors for new tickets and automatically fills customer fields
- **Configurable Mappings**: Easy-to-configure customer mappings for emails, names, and domains
- **State Management**: Tracks processed tickets to avoid duplicate processing

### Utility Tools
- **Field Inspection**: Check available Jira fields and their configurations
- **Issue Type Analysis**: Examine issue types and available transitions
- **Transition Testing**: Test specific ticket transitions before execution
- **CLI Interface**: Unified command-line interface for all operations

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Jira Server/Cloud instance with API access
- Environment variables configured

## Installation

1. **Clone or extract the project**
   ```bash
   cd automation_jira
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your settings:
   ```env
   # Jira Configuration
   JIRA_URL=https://certifyos.atlassian.net
   JIRA_EMAIL=anurag.rai@certifyos.com
   JIRA_API_TOKEN=your-jira-api-token
   
   # Project Configuration  
   PROJECT_KEY=TS
   CUSTOMER_FIELD_ID=customfield_10485
   ```

## Building

Compile TypeScript to JavaScript:
```bash
npm run build
```

## Usage

### Customer Field Automation

The customer field automation automatically detects customers based on reporter information and fills the customer field in new tickets.

#### Process New Tickets Once
```bash
npm run start customer-fields process
```

#### Run Continuous Monitoring
```bash
# Default: 60 iterations, 5 second intervals
npm run start customer-fields continuous

# Custom: 30 iterations, 3 second intervals  
npm run start customer-fields continuous --iterations 30 --interval 3000
```

#### Backup Scan (Last 24 Hours)
```bash
npm run start customer-fields backup-scan
```

#### Check Status
```bash
npm run start customer-fields status
```

#### Reset All Data
```bash
npm run start customer-fields reset
```

### Ticket Transition Automation

#### Transition Specific Issue
```bash
# Dry run (no changes made)
npm run start transition TS-12345 --dry-run

# Execute transition
npm run start transition TS-12345

# With auto-fill for missing fields
npm run start transition TS-12345 --auto-fill

# Skip issue type change (workflow only)
npm run start transition TS-12345 --skip-issue-type-change
```

#### Test Configuration
```bash
npm run start test-config
```

### Standalone Scripts

You can also run individual scripts directly:

#### Customer Field Automation
```bash
# Process new tickets
node dist/customer-field-automation.js process

# Continuous monitoring
node dist/customer-field-automation.js continuous 60 5000

# Check status
node dist/customer-field-automation.js status
```

#### Field and Issue Type Utilities
```bash
# Check available fields
node dist/check-fields.js

# Check issue types
node dist/check-issue-types.js

# Test specific issue transition
node dist/test-issue-type-change.js TS-12345
```

## Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `JIRA_URL` | Your Jira instance URL | Yes | https://certifyos.atlassian.net |
| `JIRA_EMAIL` | Your Jira email/username | Yes | anurag.rai@certifyos.com |
| `JIRA_API_TOKEN` | Your Jira API token | Yes | ATATT3x... |
| `PROJECT_KEY` | Project key for tickets | No | TS |
| `CUSTOMER_FIELD_ID` | Customer field ID | No | customfield_10485 |

### Customer Mappings

The customer field automation uses three types of mappings configured in `src/customer-field-automation.ts`:

1. **Email-to-Customer Mappings**: Exact email address matches
2. **Name-to-Customer Mappings**: Display name matches
3. **Domain-to-Customer Mappings**: Email domain matches

Example configuration:
```typescript
emailToCustomer: {
    'kelli-ann.bailey@carelon.com': 'Elevance-Carelon',
    'edna.villareal@findheadway.com': 'Headway',
    // ... more mappings
},
nameToCustomer: {
    'cindy bergley': 'FCHN',
    'abby fuller': 'FCHN',
    // ... more mappings  
},
domainToCustomer: {
    'carelon.com': 'Elevance-Carelon',
    'findheadway.com': 'Headway',
    // ... more mappings
}
```

## Project Structure

```
automation_jira/
├── src/
│   ├── types.ts                         # TypeScript type definitions
│   ├── simple-ts-automation.ts          # Main ticket transition logic
│   ├── customer-field-automation.ts     # Customer field automation
│   ├── allowed-reporters.ts             # Reporter validation
│   ├── check-fields.ts                  # Field checking utility
│   ├── check-issue-types.ts             # Issue type checking utility
│   ├── test-issue-type-change.ts        # Transition testing utility
│   └── cli.ts                          # Unified command-line interface
├── dist/                               # Compiled JavaScript (after build)
├── package.json                        # Project configuration
├── tsconfig.json                       # TypeScript configuration
├── .env.example                        # Environment template
├── customer-automation-state.json      # State file (created automatically)
└── README.md                           # This file
```

## Key Classes

### CustomerFieldAutomation
Main customer field automation class that handles:
- **Customer Detection**: Maps reporters to customers using configurable rules
- **New Ticket Processing**: Scans for newly created tickets and fills customer fields
- **Continuous Monitoring**: Runs in continuous mode with configurable intervals
- **State Management**: Tracks processed tickets and last run timestamps
- **Backup Scanning**: Scans for missed tickets in the last 24 hours

### SimpleTSAutomation  
Main ticket transition automation class that handles:
- **Ticket Querying and Processing**: Finds and processes tickets for transition
- **Reporter Validation**: Validates tickets against allowed reporters
- **Issue Type Transitions**: Handles complex issue type changes
- **Error Handling and Retries**: Comprehensive error handling with fallback strategies
- **Audit Logging**: Detailed logging of all operations

## Customer Field Automation Details

### How It Works

1. **Ticket Discovery**: Scans for newly created Support Tickets in project TS
2. **Reporter Analysis**: Extracts reporter email, name, and domain information
3. **Customer Mapping**: Applies mapping rules to determine customer
4. **Field Updates**: Updates the customer field if not already set
5. **State Tracking**: Records processed tickets to avoid duplicates

### Mapping Priority

1. **Exact Email Match**: Highest priority - matches specific email addresses
2. **Display Name Match**: Second priority - matches reporter display names
3. **Domain Match**: Lowest priority - matches email domains

### Continuous Operation

The automation can run in continuous mode:
- Configurable number of iterations and intervals
- State persistence between runs
- Automatic cleanup of old processed ticket records
- Backup scanning capability for missed tickets

## Development

### Scripts

- `npm run build` - Compile TypeScript
- `npm run start` - Run compiled CLI interface
- `npm run dev` - Run with ts-node (development)
- `npm run customer-automation` - Run customer automation directly
- `npm run test` - Run tests (when implemented)
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Adding New Customer Mappings

1. Edit `src/customer-field-automation.ts`
2. Add entries to the appropriate mapping object:
   - `emailToCustomer` for specific email addresses
   - `nameToCustomer` for display names  
   - `domainToCustomer` for email domains
3. Rebuild: `npm run build`
4. Test: `npm run start customer-fields process --dry-run`

## Troubleshooting

### Common Issues

1. **"Missing environment variables" errors**
   - Ensure `.env` file exists and contains required variables
   - Check variable names match exactly (case-sensitive)

2. **"Unauthorized" errors**
   - Verify JIRA_EMAIL and JIRA_API_TOKEN are correct
   - Ensure API token has required permissions in Jira

3. **"No customer mapping found" messages**
   - Check if reporter email/name/domain exists in mapping configuration
   - Add new mappings as needed in `src/customer-field-automation.ts`

4. **"Issue not found" errors**
   - Verify issue key format (e.g., TS-123)
   - Check if you have permission to view the issue

### Debug Mode

Set environment variable for detailed logging:
```bash
DEBUG=true npm run start customer-fields process
```

### State Management

The customer field automation maintains state in `customer-automation-state.json`:
- **lastRunTimestamp**: When automation last ran
- **processedTickets**: List of already-processed ticket keys

To reset state:
```bash
npm run start customer-fields reset
```

## Migration from Google Apps Script

This TypeScript version converts the Google Apps Script functionality with these improvements:

- **File-based State**: Uses JSON file instead of PropertiesService
- **Environment Variables**: Uses .env instead of hardcoded values  
- **Type Safety**: Full TypeScript type definitions prevent runtime errors
- **Modern HTTP**: Uses axios instead of UrlFetchApp
- **CLI Interface**: Unified command-line interface for all operations
- **Better Error Handling**: Comprehensive error handling and recovery

### Command Equivalents

| Google Apps Script Function | TypeScript Command |
|------------------------------|-------------------|
| `processNewTickets()` | `npm run start customer-fields process` |
| `continuousNewTicketMonitoring()` | `npm run start customer-fields continuous` |
| `dailyBackupScan()` | `npm run start customer-fields backup-scan` |
| `checkStatus()` | `npm run start customer-fields status` |
| `resetEverything()` | `npm run start customer-fields reset` |

## License

MIT License - see LICENSE file for details.
