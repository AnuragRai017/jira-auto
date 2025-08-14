"""
CertifyOS Jira Automation - Quick Test Script

This script validates your Jira configuration and tests basic functionality.
Run this first to ensure your credentials and setup are working correctly.
"""

import os
import sys
import requests
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

def test_jira_connection():
    """Test basic Jira API connection"""
    print("🔍 Testing CertifyOS Jira Connection...")
    
    # Load environment variables
    load_dotenv()
    
    domain = os.getenv('JIRA_DOMAIN', 'certifyos.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'anurag.rai@certifyos.com')
    api_token = os.getenv('JIRA_API_TOKEN', '')
    
    if not api_token:
        print("❌ JIRA_API_TOKEN not found in environment variables")
        return False
    
    # Create auth header
    auth_string = f"{email}:{api_token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test connection with user info
        url = f"https://{domain}/rest/api/3/myself"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        user_info = response.json()
        print(f"✅ Connected successfully!")
        print(f"   User: {user_info.get('displayName', 'Unknown')}")
        print(f"   Email: {user_info.get('emailAddress', 'Unknown')}")
        print(f"   Account ID: {user_info.get('accountId', 'Unknown')}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_project_access():
    """Test access to projects"""
    print("\n🔍 Testing Project Access...")
    
    load_dotenv()
    domain = os.getenv('JIRA_DOMAIN', 'certifyos.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'anurag.rai@certifyos.com')
    api_token = os.getenv('JIRA_API_TOKEN', '')
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json'
    }
    
    try:
        url = f"https://{domain}/rest/api/3/project"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        projects = response.json()
        print(f"✅ Found {len(projects)} accessible projects:")
        
        for project in projects[:10]:  # Show first 10 projects
            print(f"   • {project['key']}: {project['name']}")
        
        if len(projects) > 10:
            print(f"   ... and {len(projects) - 10} more projects")
        
        return projects
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Project access test failed: {str(e)}")
        return []

def test_issue_search():
    """Test searching for Support Tickets"""
    print("\n🔍 Testing Issue Search (Support Tickets)...")
    
    load_dotenv()
    domain = os.getenv('JIRA_DOMAIN', 'certifyos.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'anurag.rai@certifyos.com')
    api_token = os.getenv('JIRA_API_TOKEN', '')
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json'
    }
    
    try:
        # Search for Support Tickets
        jql = 'issuetype = "Support Ticket" ORDER BY created DESC'
        url = f"https://{domain}/rest/api/3/search"
        
        params = {
            'jql': jql,
            'maxResults': 5,
            'fields': 'summary,issuetype,status,assignee,priority,created'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        search_results = response.json()
        issues = search_results.get('issues', [])
        
        print(f"✅ Found {search_results.get('total', 0)} Support Tickets")
        print(f"   Showing first {len(issues)} issues:")
        
        for issue in issues:
            fields = issue['fields']
            assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
            print(f"   • {issue['key']}: {fields['summary'][:50]}...")
            print(f"     Status: {fields['status']['name']}, Assignee: {assignee}")
        
        return issues
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Issue search test failed: {str(e)}")
        return []

def test_custom_fields():
    """Test custom field access"""
    print("\n🔍 Testing Custom Field Access...")
    
    load_dotenv()
    domain = os.getenv('JIRA_DOMAIN', 'certifyos.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'anurag.rai@certifyos.com')
    api_token = os.getenv('JIRA_API_TOKEN', '')
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json'
    }
    
    # Field mappings from your configuration
    field_mapping = {
        'customer_field': 'customfield_10485',        # Customer(s)
        'request_type_field': 'customfield_10617',    # Type of Request
        'ops_team_field': 'customfield_10249',        # Ops Team Designation
        'team_field': 'customfield_10162',            # Team
        'ops_analyst_field': 'customfield_10324',     # Ops Analyst
        'support_category_field': 'customfield_10166', # Support Category
        'task_type_field': 'customfield_10242',       # Task Type
        'ts_source_field': 'customfield_11409',       # TS Source
        'escalation_field': 'customfield_10240',      # Ops Ticket Escalation
        'client_field': 'customfield_10237'           # Client
    }
    
    try:
        # Get field information
        url = f"https://{domain}/rest/api/3/field"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        all_fields = response.json()
        field_dict = {field['id']: field for field in all_fields}
        
        print("✅ Custom Field Validation:")
        
        for field_name, field_id in field_mapping.items():
            if field_id in field_dict:
                field_info = field_dict[field_id]
                print(f"   ✅ {field_name}: {field_info['name']} ({field_id})")
            else:
                print(f"   ❌ {field_name}: Field {field_id} not found")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Custom field test failed: {str(e)}")
        return False

def test_slack_webhook():
    """Test Slack webhook connection"""
    print("\n🔍 Testing Slack Webhook...")
    
    load_dotenv()
    webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
    
    if not webhook_url:
        print("❌ SLACK_WEBHOOK_URL not configured")
        return False
    
    test_message = {
        "text": "🤖 CertifyOS Jira Automation Test",
        "username": "CertifyOS Test Bot",
        "channel": "#general",
        "attachments": [
            {
                "color": "good",
                "title": "Configuration Test",
                "text": f"Slack integration test from CertifyOS Jira Automation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "footer": "CertifyOS Automation",
                "ts": int(datetime.now().timestamp())
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=test_message, timeout=10)
        response.raise_for_status()
        
        print("✅ Slack webhook test successful!")
        print("   Check your Slack channel for the test message")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Slack webhook test failed: {str(e)}")
        return False

def validate_specific_issue(issue_key):
    """Validate a specific issue for transfer eligibility"""
    print(f"\n🔍 Validating Issue: {issue_key}")
    
    load_dotenv()
    domain = os.getenv('JIRA_DOMAIN', 'certifyos.atlassian.net')
    email = os.getenv('JIRA_EMAIL', 'anurag.rai@certifyos.com')
    api_token = os.getenv('JIRA_API_TOKEN', '')
    
    auth_string = f"{email}:{api_token}"
    auth_bytes = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_bytes}',
        'Accept': 'application/json'
    }
    
    try:
        url = f"https://{domain}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        issue = response.json()
        fields = issue['fields']
        
        print(f"✅ Issue found: {fields['summary']}")
        print(f"   Issue Type: {fields['issuetype']['name']}")
        print(f"   Status: {fields['status']['name']}")
        print(f"   Priority: {fields.get('priority', {}).get('name', 'Unknown')}")
        
        assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
        print(f"   Assignee: {assignee}")
        
        # Check custom fields
        customer_field = fields.get('customfield_10485')
        request_type_field = fields.get('customfield_10617')
        team_field = fields.get('customfield_10162')
        
        print(f"   Customer: {customer_field}")
        print(f"   Request Type: {request_type_field}")
        print(f"   Team: {team_field}")
        
        # Validation checks
        validations = []
        
        if fields['issuetype']['name'] == 'Support Ticket':
            validations.append("✅ Issue type is Support Ticket")
        else:
            validations.append(f"❌ Issue type is {fields['issuetype']['name']}, expected Support Ticket")
        
        if customer_field:
            validations.append("✅ Customer field has value")
        else:
            validations.append("❌ Customer field is empty")
        
        if request_type_field:
            validations.append("✅ Request Type field has value")
        else:
            validations.append("❌ Request Type field is empty")
        
        # Check if assigned to TS team
        if team_field:
            team_str = str(team_field)
            if 'TS' in team_str or 'Technical Support' in team_str:
                validations.append("✅ Issue is assigned to TS team")
            else:
                validations.append(f"❌ Issue is not assigned to TS team (current: {team_str})")
        else:
            validations.append("❌ Team field is empty")
        
        print("\n   Validation Results:")
        for validation in validations:
            print(f"   {validation}")
        
        return issue
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Issue validation failed: {str(e)}")
        return None

def main():
    """Main test execution"""
    print("🚀 CertifyOS Jira Automation - Configuration Test")
    print("=" * 50)
    
    # Test basic connection
    if not test_jira_connection():
        print("\n❌ Basic connection failed. Please check your credentials.")
        sys.exit(1)
    
    # Test project access
    projects = test_project_access()
    if not projects:
        print("\n❌ No projects accessible. Please check permissions.")
        sys.exit(1)
    
    # Test issue search
    issues = test_issue_search()
    
    # Test custom fields
    test_custom_fields()
    
    # Test Slack webhook
    test_slack_webhook()
    
    # Interactive issue validation
    print("\n" + "=" * 50)
    print("✅ Configuration tests completed!")
    print("\nYou can now test specific issues:")
    
    while True:
        issue_key = input("\nEnter an issue key to validate (or 'quit' to exit): ").strip()
        if issue_key.lower() in ['quit', 'exit', 'q']:
            break
        
        if issue_key:
            validate_specific_issue(issue_key)
    
    print("\n🎉 Testing completed! Your CertifyOS Jira automation is ready to use.")
    print("\nNext steps:")
    print("1. Install required packages: pip install -r requirements.txt")
    print("2. Run the automation: python certifyos_automation.py --issue-key YOUR_ISSUE_KEY --dry-run")
    print("3. For bulk operations, modify the script as needed")

if __name__ == "__main__":
    main()
