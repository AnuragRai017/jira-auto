import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

# JIRA Configuration
JIRA_DOMAIN = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@domain.com"
JIRA_API_TOKEN = "your-api-token-here"
JIRA_PROJECT_KEY = "TS"

class JIRADataExtractor:
    def __init__(self, domain: str, email: str, api_token: str):
        self.domain = domain
        self.auth = (email, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth

    def discover_project_issues(self, project_key: str, start_at: int = 0, max_results: int = 50) -> Dict:
        """
        Discover all issues in a project to see what actually exists.
        """
        url = f"{self.domain}/rest/api/3/search"
        params = {
            'jql': f'project = {project_key} ORDER BY key ASC',
            'startAt': start_at,
            'maxResults': max_results,
            'fields': 'key,summary,status,assignee,reporter,created,updated,issuetype'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            print(f"Found {result.get('total', 0)} issues in project {project_key}")
            if result.get('issues'):
                print("Available issue keys:")
                for issue in result['issues']:
                    print(f"  - {issue['key']}: {issue['fields']['summary']}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Error discovering project issues: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return {}

    def get_issue_with_history(self, issue_key: str) -> Optional[Dict]:
        """
        Get issue details including changelog/history with better error handling.
        """
        url = f"{self.domain}/rest/api/3/issue/{issue_key}"
        params = {
            'expand': 'changelog'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Issue {issue_key} not found. It may not exist or you don't have permission to access it.")
            elif e.response.status_code == 403:
                print(f"Access denied to issue {issue_key}. Check your permissions.")
            else:
                print(f"HTTP Error {e.response.status_code} retrieving issue {issue_key}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving issue {issue_key}: {e}")
            return None

    def get_project_issues_with_history(self, project_key: str, max_results: int = 50) -> List[Dict]:
        """
        Get multiple issues from a project with their history.
        """
        url = f"{self.domain}/rest/api/3/search"
        params = {
            'jql': f'project = {project_key} ORDER BY updated DESC',
            'expand': 'changelog',
            'maxResults': max_results,
            'fields': '*all'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            issues = result.get('issues', [])
            
            print(f"Successfully retrieved {len(issues)} issues with history from project {project_key}")
            return issues
            
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving project issues: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            return []

    def test_connection(self) -> bool:
        """
        Test JIRA connection and permissions.
        """
        url = f"{self.domain}/rest/api/3/myself"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            user_info = response.json()
            print(f"✓ Connected successfully as: {user_info.get('displayName', 'Unknown')} ({user_info.get('emailAddress', 'No email')})")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection failed: {e}")
            return False

    def extract_status_changes(self, issue_data: Dict) -> List[Dict]:
        """
        Extract status change history from issue changelog.
        """
        status_changes = []
        changelog = issue_data.get('changelog', {})
        
        for history_item in changelog.get('histories', []):
            author = history_item.get('author', {})
            created = history_item.get('created', '')
            
            for item in history_item.get('items', []):
                if item.get('field') == 'status':
                    status_change = {
                        'issue_key': issue_data['key'],
                        'issue_summary': issue_data['fields'].get('summary', ''),
                        'changed_by': author.get('displayName', 'Unknown'),
                        'changed_by_email': author.get('emailAddress', ''),
                        'changed_by_account_id': author.get('accountId', ''),
                        'changed_at': created,
                        'changed_at_formatted': self.format_datetime(created),
                        'field_name': 'status',
                        'from_status': item.get('fromString', ''),
                        'to_status': item.get('toString', ''),
                        'from_status_id': item.get('from', ''),
                        'to_status_id': item.get('to', '')
                    }
                    status_changes.append(status_change)
        
        return status_changes

    def extract_all_field_changes(self, issue_data: Dict) -> List[Dict]:
        """
        Extract all field changes from issue changelog.
        """
        field_changes = []
        changelog = issue_data.get('changelog', {})
        
        for history_item in changelog.get('histories', []):
            author = history_item.get('author', {})
            created = history_item.get('created', '')
            
            for item in history_item.get('items', []):
                field_change = {
                    'issue_key': issue_data['key'],
                    'issue_summary': issue_data['fields'].get('summary', ''),
                    'changed_by': author.get('displayName', 'Unknown'),
                    'changed_by_email': author.get('emailAddress', ''),
                    'changed_by_account_id': author.get('accountId', ''),
                    'changed_at': created,
                    'changed_at_formatted': self.format_datetime(created),
                    'field_name': item.get('field', ''),
                    'field_type': item.get('fieldtype', ''),
                    'field_id': item.get('fieldId', ''),
                    'from_value': item.get('fromString', ''),
                    'to_value': item.get('toString', ''),
                    'from_value_id': item.get('from', ''),
                    'to_value_id': item.get('to', '')
                }
                field_changes.append(field_change)
        
        return field_changes

    def format_datetime(self, datetime_str: str) -> str:
        """
        Format JIRA datetime string to readable format.
        """
        try:
            # Handle different datetime formats
            if datetime_str.endswith('Z'):
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(datetime_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except:
            return datetime_str

    def save_to_json(self, data: Any, filename: str):
        """Save data to JSON file with error handling."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Data saved to: {filename}")
        except Exception as e:
            print(f"✗ Error saving to {filename}: {e}")

def main():
    """Main function to extract JIRA data with improved error handling."""
    extractor = JIRADataExtractor(JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN)
    
    print("="*60)
    print("JIRA DATA EXTRACTION TOOL")
    print("="*60)
    
    # Test connection first
    if not extractor.test_connection():
        print("Cannot proceed without valid connection. Please check your credentials.")
        return
    
    # Discover what issues exist in the project
    print(f"\n{'='*60}")
    print(f"DISCOVERING ISSUES IN PROJECT {JIRA_PROJECT_KEY}")
    print(f"{'='*60}")
    
    discovery_result = extractor.discover_project_issues(JIRA_PROJECT_KEY, max_results=100)
    
    if not discovery_result.get('issues'):
        print(f"No issues found in project {JIRA_PROJECT_KEY}. Please check:")
        print("1. Project key is correct")
        print("2. You have permission to view issues in this project")
        print("3. Issues exist in this project")
        return
    
    available_issues = discovery_result['issues']
    
    # Get detailed history for all discovered issues
    print(f"\n{'='*60}")
    print("EXTRACTING DETAILED HISTORY")
    print(f"{'='*60}")
    
    all_status_changes = []
    all_field_changes = []
    processed_issues = []
    
    for issue in available_issues[:10]:  # Process first 10 issues to avoid overwhelming output
        issue_key = issue['key']
        print(f"Processing {issue_key}...")
        
        # Get detailed issue with history
        detailed_issue = extractor.get_issue_with_history(issue_key)
        
        if detailed_issue:
            # Extract status changes
            status_changes = extractor.extract_status_changes(detailed_issue)
            all_status_changes.extend(status_changes)
            
            # Extract all field changes
            field_changes = extractor.extract_all_field_changes(detailed_issue)
            all_field_changes.extend(field_changes)
            
            processed_issues.append({
                'issue_key': issue_key,
                'summary': detailed_issue['fields'].get('summary', ''),
                'status': detailed_issue['fields'].get('status', {}).get('name', 'Unknown'),
                'assignee': detailed_issue['fields'].get('assignee', {}).get('displayName', 'Unassigned') if detailed_issue['fields'].get('assignee') else 'Unassigned',
                'created': extractor.format_datetime(detailed_issue['fields'].get('created', '')),
                'updated': extractor.format_datetime(detailed_issue['fields'].get('updated', ''))
            })
    
    # Save results
    print(f"\n{'='*60}")
    print("SAVING RESULTS")
    print(f"{'='*60}")
    
    extractor.save_to_json(all_status_changes, 'jira_status_changes.json')
    extractor.save_to_json(all_field_changes, 'jira_field_changes.json')
    extractor.save_to_json(processed_issues, 'jira_processed_issues.json')
    extractor.save_to_json(available_issues, 'jira_discovered_issues.json')
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total issues found: {len(available_issues)}")
    print(f"Issues processed: {len(processed_issues)}")
    print(f"Status changes found: {len(all_status_changes)}")
    print(f"Total field changes: {len(all_field_changes)}")
    
    # Show recent status changes
    if all_status_changes:
        print(f"\n{'='*60}")
        print("RECENT STATUS CHANGES")
        print(f"{'='*60}")
        
        recent_changes = sorted(all_status_changes, 
                              key=lambda x: x['changed_at'], 
                              reverse=True)[:5]
        
        for change in recent_changes:
            print(f"Issue: {change['issue_key']}")
            print(f"  Change: {change['from_status']} → {change['to_status']}")
            print(f"  Changed by: {change['changed_by']}")
            print(f"  When: {change['changed_at_formatted']}")
            print()

if __name__ == "__main__":
    main()
