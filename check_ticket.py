#!/usr/bin/env python3
"""Check the updated ticket values and verify reporter eligibility"""

from atlassian import Jira
import os
import sys
from dotenv import load_dotenv
from allowed_reporters import is_allowed_reporter

load_dotenv()

def main():
    # Parse command line arguments
    issue_key = 'TS-23961'  # Default issue key
    if len(sys.argv) > 1:
        issue_key = sys.argv[1]

    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')

    if jira_url is None or jira_username is None or jira_api_token is None:
        raise ValueError("JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables must be set.")

    jira = Jira(
        url=jira_url,
        username=jira_username,
        password=jira_api_token
    )

    # Check the ticket
    issue = jira.issue(issue_key)
    if issue is None:
        raise ValueError(f"Issue '{issue_key}' not found or returned None.")
    fields = issue['fields']

    print(f'{issue_key} Field Values:')
    print(f'Issue Type: {fields["issuetype"]["name"]}')
    
    customer_field = fields.get('customfield_10485')
    if customer_field:
        if isinstance(customer_field, list):
            customer_value = ', '.join([item.get('value', str(item)) for item in customer_field])
        else:
            customer_value = customer_field.get('value', str(customer_field))
        print(f'Customer: {customer_value}')
    else:
        print('Customer: Not set')
    
    request_type_field = fields.get('customfield_10617')
    if request_type_field:
        print(f'Type of Request: {request_type_field.get("value", str(request_type_field))}')
    else:
        print('Type of Request: Not set')
    
    ops_team_field = fields.get('customfield_10249')
    if ops_team_field:
        print(f'Ops Team Designation: {ops_team_field.get("value", str(ops_team_field))}')
    else:
        print('Ops Team Designation: Not set')
    
    reporter = fields.get('reporter', {})
    reporter_email = reporter.get("emailAddress", "N/A")
    reporter_name = reporter.get("displayName", "N/A")
    
    print(f'Reporter Email: {reporter_email}')
    print(f'Reporter Name: {reporter_name}')
    print(f'Labels: {fields.get("labels", [])}')
    
    # Check if reporter is in the allowed list
    allowed = is_allowed_reporter(email=reporter_email, name=reporter_name)
    print(f'\nEligibility Check:')
    if allowed:
        print(f'✅ Reporter "{reporter_name}" ({reporter_email}) IS ELIGIBLE for automatic transition')
    else:
        print(f'❌ Reporter "{reporter_name}" ({reporter_email}) is NOT eligible for automatic transition')

if __name__ == "__main__":
    main()
