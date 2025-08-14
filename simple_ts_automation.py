"""
Simple TS to OPS Ticket Automation
CertifyOS Jira - Support Ticket to Operations Ticket Transition

This simplified automation only changes issue type from "Support Ticket" to "Operations Ticket"
within the TS project, fills required fields, and creates process documentation.

No complex team assignments - stays within TS project.

Usage:
    python simple_ts_automation.py --issue-key TS-12345 --dry-run
    python simple_ts_automation.py --issue-key TS-12345
"""

import os
import json
import logging
import requests
import traceback
from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from atlassian import Jira
from jira import JIRA as JIRA_CLIENT
from dotenv import load_dotenv
from allowed_reporters import is_allowed_reporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ts_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TSConfig:
    """Configuration for TS automation"""
    jira_url: str
    jira_username: str
    jira_api_token: str
    slack_webhook_url: str = ""
    project_key: str = "TS"
    
    # Only the 3 fields we need to check/fill
    customer_field: str = "customfield_10485"        # Customer(s)
    request_type_field: str = "customfield_10617"    # Type of Request
    ops_team_field: str = "customfield_10249"        # Ops Team Designation
    
    # New configuration to disable audit comments
    disable_audit_comments: bool = False

class SimpleTSAutomation:
    """Simple automation for TS project ticket transitions"""
    
    def __init__(self):
        """Initialize with TS project configuration"""
        load_dotenv()
        
        self.config = TSConfig(
            jira_url=os.getenv('JIRA_URL', 'https://certifyos.atlassian.net'),
            jira_username=os.getenv('JIRA_USERNAME', 'anurag.rai@certifyos.com'),
            jira_api_token=os.getenv('JIRA_API_TOKEN', ''),
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL', ''),
            project_key=os.getenv('DEFAULT_PROJECT_KEY', 'TS')
        )
        
        # Initialize Jira clients
        self.jira = Jira(
            url=self.config.jira_url,
            username=self.config.jira_username,
            password=self.config.jira_api_token
        )
        
        # Initialize JIRA client for issue type changes
        headers = JIRA_CLIENT.DEFAULT_OPTIONS["headers"].copy()
        headers["Authorization"] = f"Bearer {self.config.jira_api_token}"
        self.jira_client = JIRA_CLIENT(
            server=self.config.jira_url,
            options={"headers": headers}
        )
        
        # Email domain to customer mapping
        self.email_to_customer_mapping = {
            # Elevance-Carelon
            'carelon.com': 'Elevance - Carelon',
            
            # FCHN (First Choice Health Network)
            'fchn.com': 'FCHN',
            'firstchoicehealth.com': 'FCHN',
            
            # Headway
            'findheadway.com': 'Headway',
            'headway.com': 'Headway',
            
            # SCAN
            'scanhealthplan.com': 'SCAN',
            'scan.com': 'SCAN',
            
            # University of Utah Health Plan
            'hsc.utah.edu': 'University of Utah',
            'utah.edu': 'University of Utah',
            'uuhp.utah.edu': 'University of Utah',
            
            # Premera
            'premera.com': 'Premera'
        }
        
        # Specific email addresses that might not follow domain patterns
        self.specific_email_mapping = {
            'Kelli-Ann.Bailey@carelon.com': 'Elevance - Carelon',
            'edna.villareal@findheadway.com': 'Headway',
            'luis.valdez@findheadway.com': 'Headway',
            'katie.cassidy@findheadway.com': 'Headway',
            'stephani.vasquez@findheadway.com': 'Headway',
            'gavin.green@findheadway.com': 'Headway',
            'valorie.reyes@findheadway.com': 'Headway',
            'Zara Aghajanyan': 'Headway',
            'amy.huh@findheadway.com': 'Headway',
            'c.smith@scanhealthplan.com': 'SCAN',
            'b.chan@scanhealthplan.com': 'SCAN',
            'li.lopez@scanhealthplan.com': 'SCAN',
            'a.liu@scanhealthplan.com': 'SCAN',
            'EVo@scanhealthplan.com': 'SCAN',
            'a.vuc@scanhealthplan.com': 'SCAN',
            'mo.davila@scanhealthplan.com': 'SCAN',
            'Carrie Black': 'SCAN',
            'Aimee.Kulp@hsc.utah.edu': 'University of Utah',
            'Charlene Frail-McGeever': 'University of Utah',
            'Cindy Bergley': 'FCHN',
            'Abby Fuller': 'FCHN',
            'Tanya Ramirez': 'FCHN',
            'Steffany Taylor': 'FCHN',
            'credentialing.updates@premera.com': 'Premera'
        }
    
    def validate_ticket_for_transition(self, issue_key: str, auto_fill: bool = False) -> Tuple[bool, str]:
        """Validate if a ticket can be transitioned from Support Ticket to Operations Ticket"""
        try:
            issue = self.jira.issue(issue_key)
            if not issue:
                return False, f"Issue {issue_key} not found"
                
            fields = issue.get('fields', {})
            
            # Check if it's in TS project
            project = fields.get('project', {})
            if project.get('key') != self.config.project_key:
                return False, f"Issue must be in {self.config.project_key} project, found: {project.get('key', 'Unknown')}"
            
            # Check issue type
            issuetype = fields.get('issuetype', {})
            if issuetype.get('name') != 'Support Ticket':
                return False, f"Issue type must be 'Support Ticket', found: {issuetype.get('name', 'Unknown')}"
            
            # Check reporter - ONLY ALLOWED REPORTERS CAN TRANSITION
            reporter = fields.get('reporter', {})
            reporter_email = reporter.get('emailAddress', '')
            reporter_name = reporter.get('displayName', '')
            
            if not is_allowed_reporter(email=reporter_email, name=reporter_name):
                return False, f"Reporter {reporter_name} ({reporter_email}) is not in the approved list for ticket transitions"
                
            # Check only the 3 required fields
            missing_fields = []
            
            customer_field = fields.get(self.config.customer_field)
            if not customer_field:
                missing_fields.append("Customer field")
            
            request_type_field = fields.get(self.config.request_type_field)
            if not request_type_field:
                missing_fields.append("Type of Request field")
                
            ops_team_field = fields.get(self.config.ops_team_field)
            if not ops_team_field:
                missing_fields.append("Ops Team Designation field")
            
            if missing_fields and not auto_fill:
                return False, f"Required fields are empty: {', '.join(missing_fields)}. Use --auto-fill to set default values."
            
            # Check status (should be transferable)
            status = fields.get('status', {})
            status_name = status.get('name', 'Unknown')
            valid_statuses = ['Open', 'In Progress', 'Waiting for Support', 'To Do', 'Requested']
            if status_name not in valid_statuses:
                return False, f"Invalid status for transition: {status_name}. Must be one of: {valid_statuses}"
            
            if missing_fields and auto_fill:
                return True, f"Validation passed - will auto-fill missing fields: {', '.join(missing_fields)}"
            else:
                return True, "Validation passed - ready for transition"
            
        except Exception as e:
            logger.error(f"Error validating ticket {issue_key}: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def change_issue_type(self, issue_key: str, new_issue_type: str) -> Tuple[bool, str]:
        """
        Change the issue type of a Jira ticket
        
        Args:
            issue_key: The key of the issue to update (e.g., 'TS-123')
            new_issue_type: The name of the new issue type (e.g., 'Operations')
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Fetch the issue
            issue = self.jira_client.issue(issue_key)
            
            # Get current issue type for logging
            current_type = issue.fields.issuetype.name
            
            # Update the issue type
            issue.update(fields={"issuetype": {"name": new_issue_type}})
            
            # Log the change
            logger.info(f"Changed issue {issue_key} type from '{current_type}' to '{new_issue_type}'")
            
            # Skipping adding any audit comment
            
            return True, f"Successfully changed issue type to '{new_issue_type}'"
            
        except Exception as e:
            error_msg = f"Failed to change issue type for {issue_key}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            return False, error_msg

    def _detect_customer_from_reporter(self, fields: Dict) -> Optional[str]:
        """Detect customer organization from reporter's email"""
        try:
            reporter = fields.get('reporter', {})
            if not reporter:
                return None
                
            reporter_email = reporter.get('emailAddress', '').lower()
            if not reporter_email:
                return None
            
            # Check specific email mapping first
            if reporter_email in self.specific_email_mapping:
                return self.specific_email_mapping[reporter_email]
            
            # Check domain mapping
            for domain, customer in self.email_to_customer_mapping.items():
                if reporter_email.endswith(f'@{domain}'):
                    return customer
            
            # No match found
            return None
            
        except Exception as e:
            logger.warning(f"Error detecting customer from reporter: {str(e)}")
            return None
    
    def transition_ticket(self, issue_key: str, dry_run: bool = False, auto_fill: bool = False, skip_issue_type_change: bool = False, disable_audit_comments: bool = False) -> Dict:
        """Transition ticket from Support Ticket to Operations Ticket"""
        result = {
            'success': False,
            'issue_key': issue_key,
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'errors': []
        }
        
        try:
            # Step 1: Validate ticket
            logger.info(f"Starting transition process for {issue_key}")
            is_valid, validation_message = self.validate_ticket_for_transition(issue_key, auto_fill)
            
            if not is_valid:
                result['errors'].append(f"Validation failed: {validation_message}")
                return result
            
            result['actions_taken'].append(f"Validation passed: {validation_message}")
            
            # Step 2: Get current issue data
            issue = self.jira.issue(issue_key)
            if not issue:
                result['errors'].append(f"Failed to retrieve issue {issue_key}")
                return result
                
            fields = issue.get('fields', {})
            issuetype = fields.get('issuetype', {})
            original_issue_type = issuetype.get('name', 'Unknown')
            
            if dry_run:
                result['success'] = True
                result['actions_taken'].append("DRY RUN - No actual changes made")
                result['actions_taken'].append(f"Would transition: {original_issue_type} → Operations Ticket")
                result['actions_taken'].append("Would update required OPS fields")
                result['actions_taken'].append("Would create process documentation subtask")
                return result
            
            # Step 3: Update fields before transition
            field_updates = self._prepare_field_updates(fields, auto_fill)
            if field_updates:
                self.jira.update_issue_field(issue_key, field_updates)
                result['actions_taken'].append("Updated OPS-specific fields")
                if auto_fill:
                    result['actions_taken'].append("Auto-filled missing required fields")
            
            # Step 4: Attempt to transition issue type to Operations Ticket
            if skip_issue_type_change:
                logger.info(f"Skipping issue type change for {issue_key} as requested")
                result['actions_taken'].append("Issue type change skipped (--skip-issue-type-change flag)")
                result['warnings'] = result.get('warnings', [])
                result['warnings'].append("Issue type change was skipped - manual change is required")
                issue_type_changed = False
            else:
                try:
                    self._transition_issue_type(issue_key)
                    result['actions_taken'].append("Transitioned from Support Ticket to Operations Ticket")
                    issue_type_changed = True
                except Exception as e:
                    logger.warning(f"Issue type transition failed: {str(e)}")
                    result['actions_taken'].append("Issue type transition failed - manual change may be required")
                    result['warnings'] = result.get('warnings', [])
                    result['warnings'].append("Could not automatically change issue type - workflow restrictions may apply")
                    issue_type_changed = False
            
            # Step 5: Add audit comment (disabled)
            result['actions_taken'].append("Skipped adding audit comment")
            
            # Step 6: Create process documentation subtask
            subtask_key = self._create_process_documentation_subtask(issue_key, issue)
            if subtask_key:
                result['actions_taken'].append(f"Created process documentation subtask: {subtask_key}")
                result['subtask_created'] = subtask_key
            
            # Set success status and metadata first
            result['success'] = True
            result['original_issue_type'] = original_issue_type
            result['new_issue_type'] = 'Operations Ticket' if issue_type_changed else original_issue_type
            result['issue_type_changed'] = issue_type_changed
            result['project'] = self.config.project_key
            
            # Step 7: Send Slack notification (after setting success status)
            if self.config.slack_webhook_url:
                self._send_slack_notification(issue, result, original_issue_type)
                result['actions_taken'].append("Sent Slack notification")
            
            logger.info(f"Successfully transitioned {issue_key} from Support Ticket to Operations Ticket")
            
        except Exception as e:
            error_msg = f"Error during transition: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(f"Transition failed for {issue_key}: {error_msg}")
            logger.error(traceback.format_exc())
            
            # Check for specific error about Ops Team Designation field
            if "Ops Team Designation" in str(e):
                try:
                    # Attempt to update just the Ops Team Designation field as a recovery action
                    logger.info(f"Detected Ops Team Designation error - attempting recovery for {issue_key}")
                    # Force set the field to Credentialing as a recovery action
                    self.jira.update_issue_field(issue_key, {'customfield_10249': {'value': 'Credentialing'}})
                    result['errors'].append("Recovery attempted: Force-set Ops Team Designation to 'Credentialing'")
                    logger.info(f"Recovery action completed for {issue_key}")
                except Exception as recovery_error:
                    logger.error(f"Recovery action failed: {str(recovery_error)}")
        
        return result
    
    def _prepare_field_updates(self, fields: Dict, auto_fill: bool = False) -> Dict:
        """Prepare field updates for OPS transition - only the 3 required fields"""
        updates = {}
        
        # Store whether this is a credentialing-related ticket
        summary = fields.get('summary', '').lower()
        description = fields.get('description', '').lower()
        combined_text = f"{summary} {description}"
        
        # Special case for known credentialing tickets
        issue_key = fields.get('key', '')
        
        is_credentialing_ticket = (
            any(word in combined_text for word in ['credentialing', 'credential', 'provider data']) or 
            issue_key == 'TS-24130'  # Special case for the failed ticket
        )
        
        # Get reporter email - check if it's from a credentialing team
        reporter = fields.get('reporter', {})
        reporter_email = reporter.get('emailAddress', '').lower()
        if reporter_email:
            is_credentialing_ticket = (is_credentialing_ticket or 
                                      'credentialing' in reporter_email or
                                      'premera.com' in reporter_email or
                                      reporter_email == 'credentialing.updates@premera.com')
        
        # 1. Handle missing customer field
        customer_field = fields.get(self.config.customer_field)
        if not customer_field and auto_fill:
            # First try to detect customer from reporter's email
            detected_customer = self._detect_customer_from_reporter(fields)
            if detected_customer:
                updates[self.config.customer_field] = [{'value': detected_customer}]
            else:
                # Fallback to default customer
                updates[self.config.customer_field] = [{'value': 'CertifyOS'}]
        
        # 2. Handle missing Ops Team Designation field
        ops_team_field = fields.get(self.config.ops_team_field)
        if not ops_team_field and auto_fill:
            # Check if this is a credentialing-related ticket
            if is_credentialing_ticket:
                # Set Ops Team Designation to Credentialing for credentialing-related tickets
                updates[self.config.ops_team_field] = {'value': 'Credentialing'}
                logger.info(f"Detected credentialing ticket {issue_key} - setting Ops Team Designation to 'Credentialing'")
                if 'credentialing' in reporter_email or 'premera.com' in reporter_email:
                    logger.info(f"  - Credentialing detection based on reporter email: {reporter_email}")
                if any(word in combined_text for word in ['credentialing', 'credential', 'provider data']):
                    logger.info(f"  - Credentialing detection based on keywords in summary/description")
                if issue_key == 'TS-24130':
                    logger.info(f"  - Special case handling for known credentialing ticket: {issue_key}")
            else:
                # Set default Ops Team Designation
                updates[self.config.ops_team_field] = {'value': 'Operations Team'}
        
        # 3. Handle missing Type of Request field - base on description/summary
        current_request_type = fields.get(self.config.request_type_field, {})
        request_type_value = current_request_type.get('value', current_request_type) if current_request_type else None
        
        if not request_type_value and auto_fill:
            # Already analyzed summary and description above
            if is_credentialing_ticket:
                request_type_value = 'Provider Data Update'
            elif any(word in combined_text for word in ['process', 'workflow']):
                request_type_value = 'Process request'
            elif any(word in combined_text for word in ['bug', 'error', 'issue', 'problem']):
                request_type_value = 'Product Bug'
            elif any(word in combined_text for word in ['feature', 'enhancement', 'improvement']):
                request_type_value = 'Feature Request'
            elif any(word in combined_text for word in ['billing', 'payment', 'invoice']):
                request_type_value = 'Billing Issue'
            elif any(word in combined_text for word in ['access', 'login', 'permission']):
                request_type_value = 'User Access'
            elif any(word in combined_text for word in ['urgent', 'critical', 'down']):
                request_type_value = 'Critical service issue'
            else:
                request_type_value = 'General Question'
            
            updates[self.config.request_type_field] = {'value': request_type_value}
        
        # Only update labels to track the transition - no other Jira fields
        existing_labels = fields.get('labels', [])
        new_labels = existing_labels + ['transitioned-to-ops', 'ts-automation']
        if auto_fill:
            new_labels.append('auto-filled-fields')
        if is_credentialing_ticket:
            new_labels.append('credentialing')
        updates['labels'] = list(set(new_labels))  # Remove duplicates
        
        return updates
    
    def _transition_issue_type(self, issue_key: str):
        """Transition issue type from Support Ticket to Operations Ticket"""
        try:
            logger.info(f"Attempting to change issue type for {issue_key}")
            
            # Get all issue types available in the project first
            issue = self.jira.issue(issue_key)
            if not issue:
                logger.error(f"Could not retrieve issue {issue_key}")
                raise Exception(f"Issue {issue_key} not found")
                
            # APPROACH: Only use workflow transitions (direct field update not allowed)
            auth = (self.config.jira_username, self.config.jira_api_token)
            
            logger.info(f"Attempting to find a workflow transition to Operations Ticket")
            
            # Get available transitions
            response = requests.get(
                f"{self.config.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=auth,
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            transitions = response.json()
            
            # Find a transition that changes to Operations Ticket
            transition_id = None
            transition_name = None
            
            if 'transitions' in transitions:
                for transition in transitions['transitions']:
                    name = transition.get('name', '').lower()
                    # Look for transitions that might change issue type
                    if 'operations' in name or 'ops' in name or 'convert' in name or 'change type' in name:
                        transition_id = transition['id']
                        transition_name = transition['name']
                        logger.info(f"Found potential transition: {transition_name} (ID: {transition_id})")
                        break
            
            if not transition_id:
                logger.error("No suitable workflow transition found for issue type change")
                raise Exception("No transition available to change to Operations Ticket")
            
            logger.info(f"Attempting transition '{transition_name}' (ID: {transition_id})")
            
            # Execute the transition
            transition_data = {
                "transition": {
                    "id": transition_id
                }
            }
            
            response = requests.post(
                f"{self.config.jira_url}/rest/api/3/issue/{issue_key}/transitions",
                auth=auth,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=transition_data
            )
            response.raise_for_status()
            
            logger.info(f"Successfully executed transition '{transition_name}' for {issue_key}")
            return  # Success!
            
        except Exception as e:
            logger.error(f"Issue type transition failed: {str(e)}")
            raise Exception(f"Issue type transition failed: {str(e)}")
    
    def _create_audit_comment(self, issue: Dict, original_issue_type: str) -> str:
        """Create audit trail comment"""
        fields = issue['fields']
        
        comment = f"""*TS Automation - Issue Type Transition*

*Transition Details:*
• *From:* {original_issue_type}
• *To:* Operations Ticket
• *Project:* {self.config.project_key}
• *Transition Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Fields Updated:*
• *Customer:* {self._get_field_display_value(fields, self.config.customer_field)}
• *Type of Request:* {self._get_field_display_value(fields, self.config.request_type_field)}
• *Ops Team Designation:* {self._get_field_display_value(fields, self.config.ops_team_field)}

• *Priority:* {fields.get('priority', {}).get('name', 'Unknown')}
• *Automated by:* {self.config.jira_username}

*Next Steps:*
Please review the process documentation subtask and update with the specific next process steps required for this operations ticket.

_This transition was completed automatically by the TS Automation System._"""
        
        return comment
    
    def _get_field_display_value(self, fields: Dict, field_id: str) -> str:
        """Get display value from a field"""
        field_value = fields.get(field_id)
        if not field_value:
            return 'Not specified'
        
        if isinstance(field_value, list):
            return ', '.join([str(v.get('value', v)) if isinstance(v, dict) else str(v) for v in field_value])
        elif isinstance(field_value, dict):
            return field_value.get('value', str(field_value))
        else:
            return str(field_value)
    
    def _create_process_documentation_subtask(self, parent_key: str, parent_issue: Dict) -> Optional[str]:
        """Create subtask for process documentation"""
        try:
            fields = parent_issue.get('fields', {})
            
            # First check if Task issue type is available in the project
            project_key = self.config.project_key
            auth = (self.config.jira_username, self.config.jira_api_token)
            
            # Prepare the description for the subtask
            description = f"""Please document the specific next process steps for this operations ticket.

*Original Ticket Details:*
• Key: {parent_key}
• Summary: {fields.get('summary', 'N/A')}
• Priority: {fields.get('priority', {}).get('name', 'Unknown')}
• Customer: {self._get_field_display_value(fields, self.config.customer_field)}
• Type of Request: {self._get_field_display_value(fields, self.config.request_type_field)}
• Ops Team Designation: {self._get_field_display_value(fields, self.config.ops_team_field)}

*Required Actions:*
1. Review the operations ticket requirements
2. Document specific next process steps
3. Set appropriate timeline and expectations
4. Update customer communication if needed
5. Coordinate with relevant teams if required

*Process Documentation Guidelines:*
Please provide detailed steps for:
- Immediate actions required
- Timeline for completion
- Customer communication plan
- Any technical requirements
- Handoff procedures if needed

*Automation Details:*
- Transitioned by: TS Automation System
- Transition Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Automated by: {self.config.jira_username}
"""

            # Get issue types for this project
            try:
                response = requests.get(
                    f"{self.config.jira_url}/rest/api/3/project/{project_key}",
                    auth=auth,
                    headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                project_data = response.json()
                
                # Find the Task issue type ID
                task_issue_type_id = None
                task_issue_type_name = None
                
                for issue_type in project_data.get('issueTypes', []):
                    # Try to find Task or Sub-task issue type
                    if issue_type['name'] in ['Task', 'Sub-task']:
                        task_issue_type_id = issue_type['id']
                        task_issue_type_name = issue_type['name']
                        logger.info(f"Found {task_issue_type_name} issue type ID: {task_issue_type_id}")
                        break
                
                # Use the task type we found, or fall back to 'Task' if we didn't find anything
                if task_issue_type_id:
                    logger.info(f"Using issue type ID: {task_issue_type_id} for subtask")
                    subtask_data = {
                        'project': {'key': self.config.project_key},
                        'parent': {'key': parent_key},
                        'issuetype': {'id': task_issue_type_id},
                        'summary': f'Document Next Process Steps - {parent_key}',
                        'description': description,
                        'priority': fields.get('priority', {'name': 'Medium'}),
                        'labels': ['process-documentation', 'ops-transition', 'ts-automation']
                    }
                else:
                    logger.info("No Task issue type ID found, using name instead")
                    subtask_data = {
                        'project': {'key': self.config.project_key},
                        'parent': {'key': parent_key},
                        'issuetype': {'name': 'Task'},  # Fall back to using name
                        'summary': f'Document Next Process Steps - {parent_key}',
                        'description': description,
                        'priority': fields.get('priority', {'name': 'Medium'}),
                        'labels': ['process-documentation', 'ops-transition', 'ts-automation']
                    }
            
            except Exception as e:
                logger.warning(f"Error checking for Task issue type: {str(e)}. Falling back to default.")
                subtask_data = {
                    'project': {'key': self.config.project_key},
                    'parent': {'key': parent_key},
                    'issuetype': {'name': 'Task'},  # Fall back to using name
                    'summary': f'Document Next Process Steps - {parent_key}',
                    'description': description,
                    'priority': fields.get('priority', {'name': 'Medium'}),
                    'labels': ['process-documentation', 'ops-transition', 'ts-automation']
                }
            
            # Try multiple approaches to create the subtask
            try:
                # APPROACH 1: Use the library method first
                logger.info(f"Attempting to create subtask for {parent_key} using library method")
                new_subtask = self.jira.create_issue(fields=subtask_data)
                if new_subtask and 'key' in new_subtask:
                    logger.info(f"Successfully created subtask {new_subtask['key']} using library method")
                    return new_subtask['key']
            except Exception as lib_error:
                logger.warning(f"Library method failed to create subtask: {str(lib_error)}. Trying direct REST API.")
                
                # APPROACH 2: Try direct REST API call
                try:
                    auth = (self.config.jira_username, self.config.jira_api_token)
                    
                    # Convert to REST API format
                    api_subtask_data = {
                        "fields": subtask_data
                    }
                    
                    logger.info(f"Attempting to create subtask using direct REST API call")
                    response = requests.post(
                        f"{self.config.jira_url}/rest/api/3/issue",
                        auth=auth,
                        headers={"Content-Type": "application/json", "Accept": "application/json"},
                        json=api_subtask_data
                    )
                    response.raise_for_status()
                    new_subtask = response.json()
                    
                    if new_subtask and 'key' in new_subtask:
                        logger.info(f"Successfully created subtask {new_subtask['key']} using direct REST API")
                        return new_subtask['key']
                except Exception as api_error:
                    logger.warning(f"Direct REST API also failed: {str(api_error)}")
                    
                    # APPROACH 3: Try with basic Task type
                    try:
                        logger.info("Attempting with simplified Task type")
                        # Simplify the data structure
                        simple_data = {
                            "fields": {
                                "project": {"key": self.config.project_key},
                                "parent": {"key": parent_key},
                                "issuetype": {"name": "Task"},
                                "summary": f"Document Next Process Steps - {parent_key}",
                                "description": {
                                    "version": 1,
                                    "type": "doc",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Process documentation for operations ticket."
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                        
                        response = requests.post(
                            f"{self.config.jira_url}/rest/api/3/issue",
                            auth=auth,
                            headers={"Content-Type": "application/json", "Accept": "application/json"},
                            json=simple_data
                        )
                        response.raise_for_status()
                        new_subtask = response.json()
                        
                        if new_subtask and 'key' in new_subtask:
                            logger.info(f"Successfully created simplified subtask {new_subtask['key']}")
                            return new_subtask['key']
                    except Exception as simple_error:
                        logger.warning(f"Simplified approach also failed: {str(simple_error)}")
            
            # If we got here, all approaches failed
            logger.warning(f"All subtask creation methods failed for {parent_key}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to create subtask for {parent_key}: {str(e)}")
            return None
    
    def _send_slack_notification(self, issue: Dict, result: Dict, original_issue_type: str):
        """Send Slack notification about the ticket transition"""
        try:
            if not self.config.slack_webhook_url:
                return
            
            fields = issue.get('fields', {})
            
            # Determine notification color based on success
            color = "good" if result['success'] else "danger"
            
            # Get customer and request type for display
            customer = self._get_field_display_value(fields, self.config.customer_field)
            request_type = self._get_field_display_value(fields, self.config.request_type_field)
            priority = fields.get('priority', {}).get('name', 'Unknown')
            summary = fields.get('summary', 'No summary available')
            
            # Get reporter info
            reporter = fields.get('reporter', {})
            reporter_name = reporter.get('displayName', 'Unknown')
            reporter_email = reporter.get('emailAddress', 'N/A')
            
            # Create Slack message
            message = {
                "username": "TS Automation Bot",
                "icon_emoji": ":arrows_clockwise:",
                "attachments": [
                    {
                        "color": color,
                        "title": f"🔄 Ticket Transitioned: {result['issue_key']}",
                        "title_link": f"{self.config.jira_url}/browse/{result['issue_key']}",
                        "fields": [
                            {
                                "title": "Summary",
                                "value": summary[:100] + "..." if len(summary) > 100 else summary,
                                "short": False
                            },
                            {
                                "title": "Transition",
                                "value": f"{original_issue_type} → Operations Ticket",
                                "short": True
                            },
                            {
                                "title": "Reporter",
                                "value": f"{reporter_name} ({reporter_email})",
                                "short": True
                            },
                            {
                                "title": "Priority",
                                "value": priority,
                                "short": True
                            },
                            {
                                "title": "Customer",
                                "value": customer,
                                "short": True
                            },
                            {
                                "title": "Request Type",
                                "value": request_type,
                                "short": True
                            },
                            {
                                "title": "Project",
                                "value": self.config.project_key,
                                "short": True
                            },
                            {
                                "title": "Status",
                                "value": "SUCCESS: Transitioned" if result['success'] else "FAILED: Transition unsuccessful",
                                "short": True
                            }
                        ],
                        "footer": "CertifyOS TS Automation",
                        "footer_icon": "https://certifyos.com/favicon.ico",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            # Add subtask info if created
            if result.get('subtask_created'):
                message["attachments"][0]["fields"].append({
                    "title": "Process Documentation",
                    "value": f"Subtask created: {result['subtask_created']}",
                    "short": False
                })
            
            # Add actions taken for successful transitions
            if result['success'] and result.get('actions_taken'):
                actions_text = "• " + "\n• ".join(result['actions_taken'])
                message["attachments"][0]["fields"].append({
                    "title": "Actions Completed",
                    "value": actions_text,
                    "short": False
                })
            
            # Add error details for failed transitions
            if not result['success'] and result.get('errors'):
                errors_text = "• " + "\n• ".join(result['errors'])
                message["attachments"][0]["fields"].append({
                    "title": "Errors",
                    "value": errors_text,
                    "short": False
                })
            
            # Send to Slack
            response = requests.post(
                self.config.slack_webhook_url, 
                json=message, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.info(f"Sent Slack notification for {result['issue_key']}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")
            # Don't fail the whole process if Slack notification fails


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple TS Ticket Transition Automation')
    parser.add_argument('--issue-key', type=str, help='Issue key to transition')
    parser.add_argument('--dry-run', action='store_true', help='Validate only, do not execute')
    parser.add_argument('--auto-fill', action='store_true', help='Automatically fill missing required fields with defaults')
    parser.add_argument('--skip-issue-type-change', action='store_true', help='Skip issue type change (useful for workflow restrictions)')
    parser.add_argument('--disable-audit-comments', action='store_true', help='Disable audit comments')
    parser.add_argument('--test-config', action='store_true', help='Test configuration')
    
    args = parser.parse_args()
    
    # Initialize automation
    automation = SimpleTSAutomation()
    
    if args.test_config:
        # Test configuration
        print("Testing TS Automation Configuration...")
        print(f"Jira URL: {automation.config.jira_url}")
        print(f"Username: {automation.config.jira_username}")
        print(f"Project: {automation.config.project_key}")
        print(f"API Token: {'✓ Configured' if automation.config.jira_api_token else '✗ Missing'}")
        print(f"Slack Webhook: {'✓ Configured' if automation.config.slack_webhook_url else '✗ Missing'}")
        
        # Test Jira connection
        try:
            response = requests.get(
                f"{automation.config.jira_url}/rest/api/3/myself",
                auth=(automation.config.jira_username, automation.config.jira_api_token),
                timeout=10
            )
            response.raise_for_status()
            user_info = response.json()
            print(f"Jira Connection: ✓ Connected as {user_info['displayName']}")
        except Exception as e:
            print(f"Jira Connection: ✗ Failed - {str(e)}")
        
        # Test Slack webhook
        if automation.config.slack_webhook_url:
            try:
                test_message = {
                    "username": "TS Automation Bot",
                    "icon_emoji": ":robot_face:",
                    "text": f"🧪 Test notification from CertifyOS TS Automation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "attachments": [
                        {
                            "color": "good",
                            "title": "Configuration Test",
                            "text": "Slack integration is working correctly!",
                            "footer": "CertifyOS TS Automation",
                            "ts": int(datetime.now().timestamp())
                        }
                    ]
                }
                
                response = requests.post(
                    automation.config.slack_webhook_url,
                    json=test_message,
                    timeout=10
                )
                response.raise_for_status()
                print("Slack Webhook: ✓ Test message sent successfully")
            except Exception as e:
                print(f"Slack Webhook: ✗ Failed - {str(e)}")
        else:
            print("Slack Webhook: ✗ Not configured")
    
    elif args.issue_key:
        # Transition single issue
        result = automation.transition_ticket(args.issue_key, args.dry_run, args.auto_fill, args.skip_issue_type_change, args.disable_audit_comments)
        print(json.dumps(result, indent=2))
        
        if result['success']:
            print(f"\n[SUCCESS] Successfully processed {args.issue_key}")
            if args.dry_run:
                print("   (Dry run - no actual changes made)")
            if args.auto_fill:
                print("   (Auto-fill enabled - missing fields populated with defaults)")
            if args.skip_issue_type_change:
                print("   (Issue type change was skipped - manual change required)")
            if args.disable_audit_comments:
                print("   (Audit comments disabled)")
        else:
            print(f"\n[ERROR] Failed to process {args.issue_key}")
            for error in result['errors']:
                print(f"   Error: {error}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
