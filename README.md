# Simple TS Automation - Support Ticket to Operations Ticket

This automation simply transitions tickets from "Support Ticket" to "Operations Ticket" within the TS project, fills required fields, and creates process documentation.

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
# Test a single ticket (dry run)
python simple_ts_automation.py --issue-key TS-12345 --dry-run

# Actually transition a ticket
python simple_ts_automation.py --issue-key TS-12345
```

## 📋 What It Does

### Simple Transition Process
1. ✅ **Validates** ticket is a Support Ticket in TS project
2. ✅ **Updates** required OPS fields 
3. ✅ **Transitions** from "Support Ticket" to "Operations Ticket"
4. ✅ **Creates** process documentation subtask
5. ✅ **Adds** audit trail comment

### Field Updates
- **Request Type**: Transforms to operations equivalent
- **Team**: Updates to "OPS" 
- **OPS Team Designation**: Sets to "Operations Team"
- **Task Type**: Sets appropriate operations task type
- **Labels**: Adds transition tracking labels

### Requirements
- Issue must be in TS project
- Issue type must be "Support Ticket"
- Customer field must have value
- Type of Request field must have value
- Status must be Open/In Progress/etc.

## 📁 Files

```
automation_jira/
├── simple_ts_automation.py  # Main automation script
├── test_certifyos.py        # Connection test utility
├── requirements.txt         # Python dependencies
├── .env                     # Your credentials
└── README.md               # This file
```

## 🔧 Configuration

Your `.env` file contains your CertifyOS credentials:
- Jira URL: https://certifyos.atlassian.net
- Project: TS
- All your actual custom field IDs

## 📖 Usage Examples

### Command Line
```bash
# Test configuration
python simple_ts_automation.py --test-config

# Dry run (no changes)
python simple_ts_automation.py --issue-key TS-12345 --dry-run

# Actually transition
python simple_ts_automation.py --issue-key TS-12345
```

### Python Code
```python
from simple_ts_automation import SimpleTSAutomation

automation = SimpleTSAutomation()
result = automation.transition_ticket('TS-12345', dry_run=False)
print(f"Success: {result['success']}")
```

## 🧪 Testing

Always test with `--dry-run` first:
```bash
python simple_ts_automation.py --issue-key TS-12345 --dry-run
```

This will validate the ticket and show what changes would be made without actually making them.

---

**Simple and focused TS automation!** 🎉

No complex team assignments - just transitions Support Tickets to Operations Tickets within your TS project.

## Setup Instructions
1. Import the automation rule in Jira
2. Configure field mappings
3. Test the automation with sample tickets
4. Deploy to production

## Notes
- Ensure all required fields are mapped correctly
- Test thoroughly before production deployment
- Monitor automation logs for any issues
