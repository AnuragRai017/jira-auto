"""
Test script to run both the issue type check and automation for TS-24130.
This will help         # Step 5: Try the main automation with auto-fill
    print("\nDo you want to run the main automation script now?")
    print("1. Run with auto-fill only")
    print("2. Run with auto-fill AND skip issue type change")
    print("3. Skip this step")
    response = input("Enter your choice (1-3): ")
    
    if response == '1':
        success, _ = run_command(
            f"python simple_ts_automation.py --issue-key {issue_key} --auto-fill",
            f"Running full automation on {issue_key} with auto-fill"
        )
    elif response == '2':
        success, _ = run_command(
            f"python simple_ts_automation.py --issue-key {issue_key} --auto-fill --skip-issue-type-change",
            f"Running full automation on {issue_key} with auto-fill and skipping issue type change"
        ) our fixes work properly.

Usage:
    python test_full_process.py
"""

import os
import sys
import logging
import subprocess
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('full_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()

def run_command(command, description):
    """Run a command and return its output"""
    logger.info(f"Running: {description}")
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        logger.info(f"Command successful: {description}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        print(e.stdout)
        print(e.stderr)
        logger.error(f"Command failed: {description}\n{e.stderr}")
        return False, e.stderr

def main():
    # Load environment variables
    load_dotenv()
    
    # Test issue key
    issue_key = 'TS-24130'
    
    print(f"Running full test process for {issue_key}")
    
    # Step 1: Check issue fields
    success, _ = run_command(
        f"python check_fields.py --issue-key {issue_key}", 
        "Checking fields before any changes"
    )
    if not success:
        print("Failed to check issue fields. Aborting test.")
        return
    
    # Step 2: Check available issue types
    success, _ = run_command(
        f"python check_issue_types.py",
        "Checking available issue types in the project"
    )
    if not success:
        print("Failed to check issue types. Proceeding with caution.")
    
    # Step 3: Run test for specific issue
    success, _ = run_command(
        f"python test_ts24130.py",
        f"Running test for {issue_key} with verbose logging"
    )
    if not success:
        print("Test failed. Check the logs for details.")
        return
    
    # Step 4: Check if issue was updated correctly
    success, _ = run_command(
        f"python check_fields.py --issue-key {issue_key}",
        "Checking fields after attempted changes"
    )
    if not success:
        print("Failed to check issue fields after update.")
        return
    
    # Step 5: Try the main automation with auto-fill
    print("\nDo you want to run the main automation script now?")
    response = input("Enter 'yes' to proceed or any other key to skip: ")
    
    if response.lower() == 'yes':
        success, _ = run_command(
            f"python simple_ts_automation.py --issue-key {issue_key} --auto-fill",
            f"Running full automation on {issue_key} with auto-fill"
        )
        if not success:
            print("Main automation failed. Check the logs for details.")
            return
        
        # Final check
        success, _ = run_command(
            f"python check_fields.py --issue-key {issue_key}",
            "Final check of fields after automation"
        )
        if not success:
            print("Failed to perform final field check.")
            return
    
    print("\nTest process completed!")

if __name__ == "__main__":
    main()
