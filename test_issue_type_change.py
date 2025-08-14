"""
Test script focused specifically on changing issue type.

Usage:
    python test_issue_type_change.py --issue-key TS-24130
"""

import os
import sys
import argparse
import requests
import logging
from dotenv import load_dotenv
from atlassian import Jira

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('issue_type_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Test issue type transition methods')
    parser.add_argument('--issue-key', type=str, required=True, help='Issue key to test')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Jira client
    jira_url = os.getenv('JIRA_URL', 'https://certifyos.atlassian.net')
    jira_username = os.getenv('JIRA_USERNAME', '')
    jira_api_token = os.getenv('JIRA_API_TOKEN', '')
    
    jira = Jira(
        url=jira_url,
        username=jira_username,
        password=jira_api_token
    )
    
    # Get issue details first
    print(f"Getting details for issue {args.issue_key}...")
    issue = jira.issue(args.issue_key)
    if not issue:
        print(f"Could not retrieve issue {args.issue_key}")
        return
    
    project_key = issue.get('fields', {}).get('project', {}).get('key')
    issue_type = issue.get('fields', {}).get('issuetype', {}).get('name')
    
    print(f"Issue: {args.issue_key}, Project: {project_key}, Current Type: {issue_type}")
    
    # Authentication for direct API calls
    auth = (jira_username, jira_api_token)
    
    # METHOD 1: Check available issue types in the project
    print("\n=== METHOD 1: Get available issue types for project ===")
    try:
        response = requests.get(
            f"{jira_url}/rest/api/3/project/{project_key}",
            auth=auth,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        project_data = response.json()
        
        print("Available issue types in project:")
        for issue_type in project_data.get('issueTypes', []):
            print(f"ID: {issue_type['id']}, Name: {issue_type['name']}")
        
        # Find Operations Ticket issue type
        operations_ticket_id = None
        for issue_type in project_data.get('issueTypes', []):
            if issue_type['name'] == 'Operations Ticket':
                operations_ticket_id = issue_type['id']
                print(f"\nOperations Ticket ID: {operations_ticket_id}")
                break
        
        if not operations_ticket_id:
            print("Operations Ticket issue type not found in project!")
            return
    except Exception as e:
        print(f"Error getting issue types: {str(e)}")
        return
    
    # METHOD 2: Check available transitions
    print("\n=== METHOD 2: Check available transitions ===")
    try:
        response = requests.get(
            f"{jira_url}/rest/api/3/issue/{args.issue_key}/transitions",
            auth=auth,
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        transitions = response.json()
        
        if 'transitions' in transitions:
            print("Available transitions:")
            for transition in transitions['transitions']:
                print(f"ID: {transition['id']}, Name: {transition['name']}, To Status: {transition['to']['name']}")
                
            print("\nDo you want to try a specific transition? (y/n)")
            if input().lower() == 'y':
                print("Enter the transition ID to try:")
                transition_id = input().strip()
                
                transition_data = {
                    "transition": {
                        "id": transition_id
                    }
                }
                
                print(f"Attempting transition {transition_id}...")
                
                response = requests.post(
                    f"{jira_url}/rest/api/3/issue/{args.issue_key}/transitions",
                    auth=auth,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    json=transition_data
                )
                
                if response.status_code >= 200 and response.status_code < 300:
                    print(f"Transition {transition_id} executed successfully!")
                else:
                    print(f"Transition failed with status {response.status_code}")
                    print(f"Response: {response.text}")
        else:
            print("No transitions found")
    except Exception as e:
        print(f"Error checking transitions: {str(e)}")
    
    # METHOD 3: Try direct issue update
    print("\n=== METHOD 3: Try direct issue update via REST API ===")
    print("Do you want to try direct issue type update? (y/n)")
    if input().lower() == 'y':
        try:
            update_data = {
                "fields": {
                    "issuetype": {"id": operations_ticket_id}
                }
            }
            
            print(f"Attempting to update issue type to Operations Ticket (ID: {operations_ticket_id})...")
            
            response = requests.put(
                f"{jira_url}/rest/api/3/issue/{args.issue_key}",
                auth=auth,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=update_data
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                print("Issue type updated successfully!")
            else:
                print(f"Update failed with status {response.status_code}")
                print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error updating issue type: {str(e)}")
    
    # METHOD 4: Try library method
    print("\n=== METHOD 4: Try library method ===")
    print("Do you want to try the library method? (y/n)")
    if input().lower() == 'y':
        try:
            update_data = {
                'issuetype': {'id': operations_ticket_id}
            }
            
            print(f"Attempting to update issue type using library method...")
            
            result = jira.update_issue_field(args.issue_key, update_data)
            print(f"Result: {result}")
            print("Issue type update attempted. Check the issue to verify.")
        except Exception as e:
            print(f"Error using library method: {str(e)}")
    
    print("\nScript execution completed.")

if __name__ == "__main__":
    main()
