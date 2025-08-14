#!/usr/bin/env python3
"""
Test if a specific reporter is in the allowed list
Usage: python check_reporter_allowed.py <email or name>
"""

import sys
from allowed_reporters import is_allowed_reporter, ALLOWED_REPORTERS, ALLOWED_DOMAINS

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_reporter_allowed.py <email or name>")
        print("Example: python check_reporter_allowed.py Kelli-Ann.Bailey@carelon.com")
        return
    
    # Get the email or name from command line
    email_or_name = sys.argv[1]
    
    # Check if it looks like an email
    is_email = '@' in email_or_name
    
    if is_email:
        is_allowed = is_allowed_reporter(email=email_or_name)
        print(f"\nChecking email: {email_or_name}")
    else:
        is_allowed = is_allowed_reporter(name=email_or_name)
        print(f"\nChecking name: {email_or_name}")
    
    if is_allowed:
        print(f"✅ {email_or_name} IS in the allowed list")
    else:
        print(f"❌ {email_or_name} is NOT in the allowed list")
    
    # Print the full allowed list for reference
    print("\nAllowed Reporter List:")
    for i, reporter in enumerate(ALLOWED_REPORTERS, 1):
        print(f"{i}. {reporter}")
    
    print("\nAllowed Domain List:")
    for i, domain in enumerate(ALLOWED_DOMAINS, 1):
        print(f"{i}. {domain}")

if __name__ == "__main__":
    main()
