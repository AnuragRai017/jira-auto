"""
Check fields for a specific issue to verify the Ops Team Designation field.
This is useful for debugging issues with field values.

Usage:
    python check_fields.py --issue-key TS-24130
"""

import os
import argparse
import json
from atlassian import Jira
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser(description='Check specific fields of an issue')
    parser.add_argument('--issue-key', type=str, required=True, help='Issue key to check')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Jira client
    jira = Jira(
        url=os.getenv('JIRA_URL', 'https://certifyos.atlassian.net'),
        username=os.getenv('JIRA_USERNAME', ''),
        password=os.getenv('JIRA_API_TOKEN', '')
    )
    
    # Get issue details
    issue = jira.issue(args.issue_key)
    if not issue:
        print(f"Issue {args.issue_key} not found")
        return
    
    # Get fields
    fields = issue.get('fields', {})
    
    # Field IDs to check
    field_ids = {
        'Ops Team Designation': 'customfield_10249',
        'Customer(s)': 'customfield_10485',
        'Type of Request': 'customfield_10617'
    }
    
    # Print basic issue info
    print(f"\n=== Issue Details for {args.issue_key} ===")
    print(f"Summary: {fields.get('summary', 'N/A')}")
    print(f"Status: {fields.get('status', {}).get('name', 'N/A')}")
    print(f"Issue Type: {fields.get('issuetype', {}).get('name', 'N/A')}")
    print(f"Reporter: {fields.get('reporter', {}).get('displayName', 'N/A')}")
    print(f"Reporter Email: {fields.get('reporter', {}).get('emailAddress', 'N/A')}")
    
    # Print specific fields we care about
    print("\n=== Required Fields ===")
    for field_name, field_id in field_ids.items():
        field_value = fields.get(field_id)
        print(f"{field_name}: ", end="")
        
        if field_value is None:
            print("NOT SET")
        elif isinstance(field_value, list):
            values = []
            for item in field_value:
                if isinstance(item, dict) and 'value' in item:
                    values.append(item['value'])
                else:
                    values.append(str(item))
            print(', '.join(values))
        elif isinstance(field_value, dict) and 'value' in field_value:
            print(field_value['value'])
        else:
            print(field_value)
    
    # Print description (first 200 chars) for keyword analysis
    description = fields.get('description', 'N/A')
    if isinstance(description, dict) and 'content' in description:
        # Handle Atlassian Document Format
        desc_text = extract_text_from_adf(description)
        if desc_text:
            print(f"\nDescription (first 200 chars): {desc_text[:200]}...")
    elif isinstance(description, str):
        # Handle plain text description
        print(f"\nDescription (first 200 chars): {description[:200]}...")
    
    # Print raw field values for debugging
    print("\n=== Raw Field Values ===")
    for field_name, field_id in field_ids.items():
        field_value = fields.get(field_id)
        print(f"{field_name} ({field_id}): {json.dumps(field_value, indent=2)}")

def extract_text_from_adf(adf_doc):
    """Extract plain text from Atlassian Document Format"""
    text = []
    
    def process_content(content):
        if isinstance(content, list):
            for item in content:
                process_content(item)
        elif isinstance(content, dict):
            if content.get('type') == 'text':
                text.append(content.get('text', ''))
            if 'content' in content:
                process_content(content['content'])
    
    process_content(adf_doc.get('content', []))
    return ''.join(text)

if __name__ == "__main__":
    main()
