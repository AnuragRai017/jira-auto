#!/usr/bin/env python3
"""Find Support Tickets matching specific criteria - With multiple query options"""

import os
import json
import argparse
from atlassian import Jira
from dotenv import load_dotenv

load_dotenv()

def display_issue_details(issue):
    """Display details for a single issue"""
    key = issue.get('key', 'N/A')
    fields = issue.get('fields', {})
    
    status = fields.get('status', {}).get('name', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'Unknown')
    
    # Get Request Type value - customfield_10617
    request_type = fields.get('customfield_10617', {})
    request_type_value = request_type.get('value', 'Not specified') if request_type else 'Not specified'
    
    reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
    summary = fields.get('summary', 'No summary')
    
    if len(summary) > 47:
        summary = summary[:47] + "..."
        
    print(f"{key:<10} {status:<15} {priority:<10} {request_type_value:<25} {reporter:<25} {summary:<50}")

def process_query(jira, query, query_name, limit):
    """Process a JQL query and display results"""
    print(f"\n{'='*80}")
    print(f"Searching for eligible Support Tickets using {query_name} query...\n")
    
    try:
        # Max results parameter to avoid excessive results
        search_results = jira.jql(query, limit=limit)
        
        # Extract issues
        issues = []
        if search_results is not None:
            issues = search_results.get('issues', [])
        
        print(f"Found {len(issues)} eligible Support Tickets:\n")
        print(f"{'Key':<10} {'Status':<15} {'Priority':<10} {'Type of Request':<25} {'Reporter':<25} {'Summary':<50}")
        print("-" * 135)
        
        for issue in issues:
            display_issue_details(issue)
        
        if issues:
            print("\nDetails for the first eligible ticket:")
            first_issue = issues[0]
            first_key = first_issue.get('key')
            fields = first_issue.get('fields', {})
            
            print(f"\nKey: {first_key}")
            print(f"Summary: {fields.get('summary', 'N/A')}")
            print(f"Status: {fields.get('status', {}).get('name', 'Unknown')}")
            print(f"Priority: {fields.get('priority', {}).get('name', 'Unknown')}")
            
            # Get reporter info
            reporter = fields.get('reporter', {})
            print(f"Reporter: {reporter.get('displayName', 'Unknown')} ({reporter.get('emailAddress', 'N/A')})")
            
            # Get Customer value - customfield_10485
            customer = fields.get('customfield_10485', [])
            customer_values = []
            if isinstance(customer, list):
                customer_values = [item.get('value', str(item)) for item in customer if isinstance(item, dict)]
            customer_str = ', '.join(customer_values) if customer_values else 'Not specified'
            print(f"Customer: {customer_str}")
            
            # Get Request Type value - customfield_10617
            request_type = fields.get('customfield_10617', {})
            request_type_value = request_type.get('value', 'Not specified') if request_type else 'Not specified'
            print(f"Type of Request: {request_type_value}")
            
            # Get Ops Team Designation - customfield_10249
            ops_team = fields.get('customfield_10249', {})
            ops_team_value = ops_team.get('value', 'Not specified') if ops_team else 'Not specified'
            print(f"Ops Team Designation: {ops_team_value}")
            
            print("\nTo process this ticket with auto-fill:")
            print(f"python simple_ts_automation.py --issue-key {first_key} --auto-fill")
        
        return len(issues)
    
    except Exception as e:
        print(f"Error searching for tickets with {query_name} query: {str(e)}")
        return 0

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Find eligible Support Tickets with multiple query options')
    parser.add_argument('--query-type', '-q', choices=['approved-reporters', 'original', 'both'], 
                        default='both', help='Query type to run (default: both)')
    parser.add_argument('--limit', '-l', type=int, default=20,
                        help='Maximum number of results to return (default: 20)')
    args = parser.parse_args()
    
    # Connect to Jira
    jira = Jira(
        url=os.getenv('JIRA_URL', 'https://certifyos.atlassian.net'),
        username=os.getenv('JIRA_USERNAME', 'anurag.rai@certifyos.com'),
        password=os.getenv('JIRA_API_TOKEN', '')
    )
    
    # JQL query to find eligible Support Tickets - Only from specific reporters
    approved_reporters_jql = """
    project = TS 
    AND resolution = Unresolved 
    AND status != Done 
    AND "issuetype" = "Support Ticket" 
    AND (
        reporter = "cbergley"
        OR reporter = "Cindy Bergley" 
        OR reporter = "Abby Fuller"
        OR reporter = "Tanya Ramirez"
        OR reporter = "Steffany Taylor"
        OR reporter = "Kelli-Ann.Bailey@carelon.com"
        OR reporter = "edna.villareal@findheadway.com"
        OR reporter = "luis.valdez@findheadway.com"
        OR reporter = "katie.cassidy@findheadway.com"
        OR reporter = "stephani.vasquez@findheadway.com"
        OR reporter = "gavin.green@findheadway.com"
        OR reporter = "valorie.reyes@findheadway.com"
        OR reporter = "amy.huh@findheadway.com"
        OR reporter = "Zara Aghajanyan"
        OR reporter = "c.smith@scanhealthplan.com"
        OR reporter = "b.chan@scanhealthplan.com"
        OR reporter = "li.lopez@scanhealthplan.com"
        OR reporter = "a.liu@scanhealthplan.com"
        OR reporter = "EVo@scanhealthplan.com"
        OR reporter = "a.vuc@scanhealthplan.com"
        OR reporter = "mo.davila@scanhealthplan.com"
        OR reporter = "Carrie Black"
        OR reporter = "Charlene Frail-McGeever"
        OR reporter = "Aimee.Kulp@hsc.utah.edu"
        OR reporter = "credentialing.updates@premera.com"
    )
    ORDER BY status ASC, created ASC
    """
    
    # Original JQL query
    original_jql = """
    project = TS 
    AND assignee is EMPTY 
    AND resolution = Unresolved 
    AND status != Done 
    AND "issuetype" = "Support Ticket" 
    AND "Request Type" NOT IN ("Outreach Inbox Emailed request (TS)","Credentialing Inbox Emailed request (TS)") 
    AND reporter NOT IN (712020:c4251a09-b587-4064-a3a7-de4aa398d604, 712020:af1ed9b3-297b-4057-8ae1-d9edb22b8b2a) 
    ORDER BY status ASC, created ASC
    """
    
    # Determine which queries to run based on arguments
    queries_to_run = []
    
    if args.query_type == 'approved-reporters' or args.query_type == 'both':
        queries_to_run.append(('APPROVED REPORTERS', approved_reporters_jql))
    
    if args.query_type == 'original' or args.query_type == 'both':
        queries_to_run.append(('ORIGINAL', original_jql))
    
    total_found = 0
    # Process each query
    for query_name, query in queries_to_run:
        found = process_query(jira, query, query_name, args.limit)
        total_found += found

    if total_found == 0:
        print("\nNo eligible tickets found with the specified queries.")
        
if __name__ == "__main__":
    main()
