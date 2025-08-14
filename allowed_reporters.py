"""
Allowed reporters for ticket transitions
This file contains the list of reporter emails and names that are allowed
to have their tickets transitioned from Support Ticket to Operations Ticket.
"""

# List of allowed reporter email addresses and names
ALLOWED_REPORTERS = [
    # Elevance-Carelon
    'Kelli-Ann.Bailey@carelon.com',
    
    # FCHN (First Choice Health Network)
    'Cindy Bergley',
    'cbergley',  # Jira username for Cindy Bergley
    'Abby Fuller',
    'Tanya Ramirez',
    'Steffany Taylor',
    
    # Premera
    'credentialing.updates@premera.com',
    
    # Headway
    'edna.villareal@findheadway.com',
    'luis.valdez@findheadway.com',
    'katie.cassidy@findheadway.com',
    'stephani.vasquez@findheadway.com',
    'gavin.green@findheadway.com',
    'valorie.reyes@findheadway.com',
    'amy.huh@findheadway.com',
    'Zara Aghajanyan',
    
    # SCAN
    'c.smith@scanhealthplan.com',
    'b.chan@scanhealthplan.com',
    'li.lopez@scanhealthplan.com',
    'a.liu@scanhealthplan.com',
    'EVo@scanhealthplan.com',
    'a.vuc@scanhealthplan.com',
    'mo.davila@scanhealthplan.com',
    'Carrie Black',
    
    # University of Utah Health Plan
    'Charlene Frail-McGeever',
    'Aimee.Kulp@hsc.utah.edu'
]

# Email domain allowlist - emails from these domains are allowed
ALLOWED_DOMAINS = [
    'carelon.com',
    'findheadway.com',
    'headway.com',
    'scanhealthplan.com',
    'scan.com',
    'hsc.utah.edu',
    'utah.edu',
    'fchn.com',
    'firstchoicehealth.com',
    'premera.com',
]

def is_allowed_reporter(email=None, name=None):
    """
    Check if a reporter is allowed based on email or name
    
    Args:
        email: Reporter's email address
        name: Reporter's display name
    
    Returns:
        bool: True if the reporter is allowed, False otherwise
    """
    # Check if either email or name is in the allowed list
    if email and email.lower() in [r.lower() for r in ALLOWED_REPORTERS]:
        return True
        
    if name and name.lower() in [r.lower() for r in ALLOWED_REPORTERS]:
        return True
        
    # Check if email domain is allowed
    if email:
        for domain in ALLOWED_DOMAINS:
            if email.lower().endswith('@' + domain.lower()):
                return True
                
    return False
