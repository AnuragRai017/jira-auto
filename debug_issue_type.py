#!/usr/bin/env python3
"""Test issue type change for TS-23961"""

from atlassian import Jira
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')

    if not jira_url or not jira_username or not jira_api_token:
        raise ValueError("JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables must be set.")

    jira = Jira(
        url=jira_url,
        username=jira_username,
        password=jira_api_token
    )

    issue_key = 'TS-23961'
    
    print(f"Current state of {issue_key}:")
    issue = jira.issue(issue_key)
    if issue is None:
        print(f"Error: Issue {issue_key} not found or could not be retrieved.")
        return
    fields = issue['fields']
    print(f"Current Issue Type: {fields['issuetype']['name']}")
    print(f"Current Status: {fields['status']['name']}")
    
    # Check if we can edit the issue type
    try:
        edit_meta = jira.get(f'rest/api/3/issue/{issue_key}/editmeta')
        
        if edit_meta and 'fields' in edit_meta and edit_meta['fields'] is not None and 'issuetype' in edit_meta['fields']:
            issuetype_field = edit_meta['fields']['issuetype']
            print("\nIssue type field is editable!")
            
            allowed_values = issuetype_field.get('allowedValues', [])
            print(f"Allowed issue types ({len(allowed_values)}):")
            for issue_type in allowed_values:
                print(f"  - {issue_type['name']} (ID: {issue_type['id']})")
        else:
            print("\nIssue type field is NOT editable for this issue.")
            if edit_meta and 'fields' in edit_meta and edit_meta['fields'] is not None:
                print("Available fields for editing:")
                for field_name in edit_meta['fields'].keys():
                    print(f"  - {field_name}")
            else:
                print("No editable fields metadata available.")
                
    except Exception as e:
        print(f"Error checking edit metadata: {e}")

    # Try to change the issue type manually to see the exact error
    print(f"\nAttempting to change issue type...")
    try:
        update_data = {
            'issuetype': {'id': '10845'}  # Operations Ticket ID
        }
        
        response = jira.update_issue_field(issue_key, update_data)
        print("✅ Issue type change succeeded!")
        
    except Exception as e:
        print(f"❌ Issue type change failed: {str(e)}")

if __name__ == "__main__":
    main()
