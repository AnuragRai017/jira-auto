# Jira Automation TypeScript Migration

This directory contains the TypeScript version of the Jira automation scripts.

## Installation

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Install development dependencies:**
   ```bash
   npm install --save-dev @types/node
   ```

3. **Create environment file:**
   Copy your `.env` file from the Python version to this directory.

4. **Build the TypeScript code:**
   ```bash
   npm run build
   ```

5. **Run the automation:**
   ```bash
   npm start -- --issue-key TS-24130 --auto-fill
   ```
   
   Or using ts-node for development:
   ```bash
   npx ts-node src/cli.ts --issue-key TS-24130 --auto-fill
   ```

## Available Scripts

### Main Automation
```bash
# Run with auto-fill
npx ts-node src/cli.ts --issue-key TS-24130 --auto-fill

# Dry run (validation only)
npx ts-node src/cli.ts --issue-key TS-24130 --dry-run

# Skip issue type change (useful for workflow restrictions)
npx ts-node src/cli.ts --issue-key TS-24130 --auto-fill --skip-issue-type-change

# Test configuration
npx ts-node src/cli.ts --test-config
```

### Utility Scripts
```bash
# Check fields on an issue
npx ts-node src/check-fields.ts --issue-key TS-24130

# Check available issue types
npx ts-node src/check-issue-types.ts

# Test specific issue type transitions
npx ts-node src/test-issue-type-change.ts --issue-key TS-24130
```

## Key Features

1. **Type Safety**: Full TypeScript type definitions for all Jira API interactions
2. **Error Handling**: Comprehensive error handling and logging
3. **Modular Design**: Separated concerns with clear interfaces
4. **CLI Interface**: Easy-to-use command line interface with yargs
5. **Configuration Testing**: Built-in configuration validation
6. **Multiple Fallbacks**: Multiple approaches for issue type transitions and subtask creation

## Configuration

The automation uses the same environment variables as the Python version:

- `JIRA_URL`: Your Jira instance URL
- `JIRA_USERNAME`: Your Jira username  
- `JIRA_API_TOKEN`: Your Jira API token
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications (optional)
- `DEFAULT_PROJECT_KEY`: Default project key (defaults to "TS")

## Project Structure

```
src/
├── types.ts                    # TypeScript type definitions
├── allowed-reporters.ts        # Reporter validation logic
├── simple-ts-automation.ts     # Main automation class
├── cli.ts                      # Command line interface
├── check-fields.ts            # Field checking utility
├── check-issue-types.ts       # Issue type checking utility
└── test-issue-type-change.ts  # Issue type transition testing
```

## Migration from Python

The TypeScript version maintains the same functionality as the Python version but with additional benefits:

1. **Better IDE support** with autocomplete and type checking
2. **Compile-time error detection** to catch issues before runtime
3. **Modern async/await** patterns for cleaner asynchronous code
4. **Comprehensive interfaces** for all data structures
5. **Improved error handling** with typed exceptions

## Known Issues & Workarounds

1. **Issue Type Changes**: Some Jira instances have workflow restrictions that prevent direct issue type changes. Use the `--skip-issue-type-change` flag to bypass this.

2. **Subtask Creation**: If subtask creation fails due to issue type restrictions, the script will attempt multiple fallback approaches.

3. **Unicode Characters**: Removed problematic Unicode characters that caused encoding issues in Windows environments.

## Development

To contribute or modify the code:

1. **Install dependencies**: `npm install`
2. **Run in development mode**: `npm run dev`
3. **Build for production**: `npm run build`
4. **Run tests**: `npm test` (when tests are added)
5. **Lint code**: `npm run lint`
6. **Format code**: `npm run format`

## Troubleshooting

### TypeScript Compilation Issues
If you encounter TypeScript compilation errors:

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Ensure @types/node is installed
npm install --save-dev @types/node

# Try building with verbose output
npx tsc --verbose
```

### Runtime Issues
1. Check that all environment variables are properly set
2. Verify Jira API credentials and permissions
3. Test configuration with: `npx ts-node src/cli.ts --test-config`

### Jira API Issues
1. Verify the issue key exists and you have access
2. Check that the reporter is in the allowed list
3. Ensure required custom fields exist in your Jira instance
