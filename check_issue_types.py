"""
Check available issue types for the TS project.
This will help us identify the correct issue type ID for Operations Ticket.

Usage:
    python check_issue_types.py
"""

import os
import json
import requests
from atlassian import Jira
from dotenv import load_dotenv

def main():
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
    
    # Get project key from env or use default
    project_key = os.getenv('DEFAULT_PROJECT_KEY', 'TS')
    
    print(f"Fetching issue types for project {project_key}...")
    
    # Get direct REST API access for methods not in the library
    auth = (jira_username, jira_api_token)
    
    # Method 1: Get project metadata via direct API call
    try:
        print("\n=== Issue Type Method 1: Project Metadata ===")
        response = requests.get(
            f"{jira_url}/rest/api/3/project/{project_key}",
            auth=auth
        )
        response.raise_for_status()
        project_data = response.json()
        
        if 'issueTypes' in project_data:
            print(f"Available issue types for {project_key}:")
            for issue_type in project_data['issueTypes']:
                print(f"ID: {issue_type['id']}, Name: {issue_type['name']}")
        else:
            print("No issue types found in project data")
    except Exception as e:
        print(f"Error getting project metadata: {str(e)}")
    
    # Method 2: Get all issue types via direct API call
    try:
        print("\n=== Issue Type Method 2: All Issue Types ===")
        response = requests.get(
            f"{jira_url}/rest/api/3/issuetype",
            auth=auth
        )
        response.raise_for_status()
        issue_types = response.json()
        
        print("All available issue types in the Jira instance:")
        for issue_type in issue_types:
            print(f"ID: {issue_type['id']}, Name: {issue_type['name']}")
    except Exception as e:
        print(f"Error getting all issue types: {str(e)}")
    
    # Method 3: Get create metadata via direct API call
    try:
        print("\n=== Issue Type Method 3: Create Meta for Project ===")
        response = requests.get(
            f"{jira_url}/rest/api/3/issue/createmeta?projectKeys={project_key}&expand=projects.issuetypes",
            auth=auth
        )
        response.raise_for_status()
        create_meta = response.json()
        
        if 'projects' in create_meta:
            for project in create_meta['projects']:
                if project['key'] == project_key:
                    print(f"Available issue types for {project_key} from create meta:")
                    for issue_type in project.get('issuetypes', []):
                        print(f"ID: {issue_type['id']}, Name: {issue_type['name']}")
        else:
            print("No projects found in create meta")
    except Exception as e:
        print(f"Error getting create meta: {str(e)}")
    
    # Method 4: Get transitions via direct API call
    try:
        print("\n=== Available Transitions Method ===")
        # You can replace this with a valid issue key from the TS project
        sample_issue_key = "TS-24130"
        response = requests.get(
            f"{jira_url}/rest/api/3/issue/{sample_issue_key}/transitions",
            auth=auth
        )
        response.raise_for_status()
        transitions = response.json()
        
        print(f"Available transitions for {sample_issue_key}:")
        if 'transitions' in transitions:
            for transition in transitions['transitions']:
                print(f"ID: {transition['id']}, Name: {transition['name']}, "
                      f"To Status: {transition['to']['name']}")
        else:
            print("No transitions found")
    except Exception as e:
        print(f"Error getting transitions: {str(e)}")

if __name__ == "__main__":
    main()
