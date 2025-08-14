# Simple TS Automation - Support Ticket to Operations Ticket

This automation transitions tickets from "Support Ticket" to "Operations Ticket" within the TS project, fills required fields, and creates process documentation.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Test Configuration
```bash
# Test your Jira connection
python test_certifyos.py

# Test automation configuration
python simple_ts_automation.py --test-config
```

### 3. Run Automation
```bash
# Find eligible tickets
python find_tickets_multi_query.py

# Test a single ticket (dry run)
python simple_ts_automation.py --issue-key TS-12345 --dry-run

# Actually transition a ticket with auto-fill
python simple_ts_automation.py --issue-key TS-12345 --auto-fill
```

## 📋 What It Does

### Simple Transition Process
1. ✅ **Validates** ticket is a Support Ticket in TS project
2. ✅ **Checks** if reporter is in allowed list
3. ✅ **Updates** required OPS fields 
4. ✅ **Transitions** from "Support Ticket" to "Operations Ticket"
5. ✅ **Creates** process documentation subtask
6. ✅ **Adds** audit trail comment
7. ✅ **Sends** Slack notification

### Field Updates
- **Customer**: Auto-detects from reporter email domain
- **Request Type**: Transforms to operations equivalent
- **Ops Team Designation**: Sets to "Operations Team"
- **Labels**: Adds transition tracking labels

### Requirements
- Issue must be in TS project
- Issue type must be "Support Ticket"
- Reporter must be in approved list
- Status must be Open/In Progress/etc.

## 📁 Files

```
automation_jira/
├── simple_ts_automation.py      # Main automation script
├── find_tickets_multi_query.py  # Find eligible tickets with multi-query support
├── find_eligible_tickets.py     # Find eligible tickets (original)
├── check_ticket.py              # Check ticket values and eligibility
├── check_reporter_allowed.py    # Check if a reporter is in allowed list
├── allowed_reporters.py         # List of allowed reporters
├── debug_issue_type.py          # Debug tool for issue type changes
├── test_certifyos.py            # Connection test utility
├── find_tickets.bat             # Easy launcher for Windows
├── requirements.txt             # Python dependencies
├── .env                         # Your credentials
└── README.md                    # This file
```

## 🔧 Configuration

Your `.env` file contains your CertifyOS credentials:
- Jira URL: https://certifyos.atlassian.net
- Project: TS
- Slack webhook URL for notifications

## 📖 Usage Examples

### Finding Eligible Tickets
```bash
# Run the batch file for menu options
find_tickets.bat

# Or run the script directly:
# Find tickets from approved reporters only
python find_tickets_multi_query.py --query-type approved-reporters

# Find tickets using original JQL query
python find_tickets_multi_query.py --query-type original

# Find tickets using both queries
python find_tickets_multi_query.py --query-type both
```

### Transitioning Tickets
```bash
# Test configuration
python simple_ts_automation.py --test-config

# Dry run (no changes)
python simple_ts_automation.py --issue-key TS-12345 --dry-run

# Actually transition with auto-fill
python simple_ts_automation.py --issue-key TS-12345 --auto-fill
```

### Checking Reporters & Tickets
```bash
# Check if a specific reporter is allowed
python check_reporter_allowed.py "reporter@example.com"

# Check a specific ticket's fields and eligibility
python check_ticket.py TS-12345
```

## 🔒 Reporter Restrictions

Only tickets from specific approved reporters will be transitioned:
- Elevance-Carelon reporters
- FCHN (First Choice Health Network) reporters
- Headway reporters
- SCAN reporters
- University of Utah Health Plan reporters

The full list is maintained in `allowed_reporters.py`.

## 🧪 Testing

Always test with `--dry-run` first:
```bash
python simple_ts_automation.py --issue-key TS-12345 --dry-run
```

This will validate the ticket and show what changes would be made without actually making them.

---

**Simple and focused TS automation!** 🎉

No complex team assignments - just transitions Support Tickets to Operations Tickets within your TS project for approved reporters.
