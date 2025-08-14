"""
Test script to process TS-24130 ticket with debug logging enabled.
This script will help diagnose the specific issue with the credentialing detection logic.

Usage:
    python test_ts24130.py
"""

import logging
import os
from simple_ts_automation import SimpleTSAutomation
from dotenv import load_dotenv

# Configure DEBUG level logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ts24130_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

def main():
    # Load environment variables
    load_dotenv()
    
    # Test issue key
    issue_key = 'TS-24130'
    
    print(f"Running test for {issue_key} with debug logging enabled...")
    
    # Initialize automation
    automation = SimpleTSAutomation()
    
    # First, validate the ticket (dry run)
    is_valid, validation_message = automation.validate_ticket_for_transition(issue_key, auto_fill=True)
    print(f"\nValidation: {'PASSED' if is_valid else 'FAILED'}")
    print(f"Message: {validation_message}")
    
    if not is_valid:
        print("Validation failed - cannot proceed with test.")
        return
    
    # Check fields before
    print("\nChecking fields BEFORE transition...")
    issue = automation.jira.issue(issue_key)
    if not issue:
        print(f"Could not retrieve issue {issue_key}")
        return
    fields = issue.get('fields', {})
    
    # Check Ops Team Designation
    ops_team_field = fields.get('customfield_10249')
    print(f"Ops Team Designation before: {ops_team_field}")
    
    # Run the prepare_field_updates function to see what would be set
    print("\nTesting field preparation logic...")
    updates = automation._prepare_field_updates(fields, auto_fill=True)
    print(f"Field updates that would be applied: {updates}")
    
    # Check if Ops Team Designation would be set
    if 'customfield_10249' in updates:
        print(f"Ops Team Designation would be set to: {updates['customfield_10249']}")
    else:
        print("Ops Team Designation would NOT be updated")
    
    # Ask for confirmation before proceeding
    print("\n******************************************************")
    print("*                   CONFIRMATION                     *")
    print("******************************************************")
    print("WARNING: This will attempt to transition the real ticket.")
    proceed = input("Do you want to proceed with the actual transition? (yes/no): ")
    
    if proceed.lower() != 'yes':
        print("Test canceled. No changes were made.")
        return
    
    # Run the actual transition with auto_fill=True
    print(f"\nRunning transition for {issue_key} with auto_fill enabled...")
    result = automation.transition_ticket(issue_key, dry_run=False, auto_fill=True)
    
    print("\nTransition results:")
    for key, value in result.items():
        print(f"{key}: {value}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
