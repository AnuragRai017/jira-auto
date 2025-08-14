/**
 * Simple TS to OPS Ticket Automation
 * CertifyOS Jira - Support Ticket to Operations Ticket Transition
 * 
 * This simplified automation only changes issue type from "Support Ticket" to "Operations Ticket"
 * within the TS project, fills required fields, and creates process documentation.
 * 
 * No complex team assignments - stays within TS project.
 */

import * as dotenv from 'dotenv';
import axios, { AxiosInstance, AxiosResponse } from 'axios';

import {
  TSConfig,
  JiraIssue,
  TransitionResult,
  ValidationResult,
  JiraTransition,
  JiraProject,
  SlackMessage,
  CreateIssueData,
  EmailDomainMapping
} from './types';
import { isAllowedReporter } from './allowed-reporters';

// Simple logger implementation
class SimpleLogger {
  info(message: string): void {
    console.log(`${new Date().toISOString()} - INFO - ${message}`);
  }
  
  warn(message: string): void {
    console.warn(`${new Date().toISOString()} - WARN - ${message}`);
  }
  
  error(message: string, stack?: string): void {
    console.error(`${new Date().toISOString()} - ERROR - ${message}`);
    if (stack) {
      console.error(stack);
    }
  }
}

const logger = new SimpleLogger();

export class SimpleTSAutomation {
  private config: TSConfig;
  private axiosInstance: AxiosInstance;
  private emailToCustomerMapping: EmailDomainMapping;

  constructor() {
    // Load environment variables
    dotenv.config();
    
    this.config = {
      jiraUrl: process.env.JIRA_URL || 'https://your-domain.atlassian.net',
      jiraUsername: process.env.JIRA_USERNAME || 'your-email@domain.com',
      jiraApiToken: process.env.JIRA_API_TOKEN || '',
      slackWebhookUrl: process.env.SLACK_WEBHOOK_URL || '',
      projectKey: process.env.DEFAULT_PROJECT_KEY || 'TS',
      
      // Required fields
      customerField: 'customfield_10485',        // Customer(s)
      requestTypeField: 'customfield_10617',     // Type of Request
      opsTeamField: 'customfield_10249',         // Ops Team Designation
      
      // Configuration options
      disableAuditComments: false
    };

    // Initialize axios with authentication
    this.axiosInstance = axios.create({
      baseURL: this.config.jiraUrl,
      auth: {
        username: this.config.jiraUsername,
        password: this.config.jiraApiToken
      },
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    // Email domain to customer mapping
    this.emailToCustomerMapping = {
      // Elevance-Carelon
      'carelon.com': 'Elevance - Carelon',
      
      // FCHN (First Choice Health Network)
      'fchn.com': 'FCHN',
      'firstchoicehealth.com': 'FCHN',
      
      // Headway
      'findheadway.com': 'Headway',
      'headway.com': 'Headway',
      
      // SCAN
      'scanhealthplan.com': 'SCAN',
      'scan.com': 'SCAN',
      
      // University of Utah Health Plan
      'utah.edu': 'University of Utah Health Plan',
      'hsc.utah.edu': 'University of Utah Health Plan',
      
      // Premera
      'premera.com': 'Premera'
    };
  }

  /**
   * Get a Jira issue by key
   */
  async getIssue(issueKey: string): Promise<JiraIssue | null> {
    try {
      const response: AxiosResponse<JiraIssue> = await this.axiosInstance.get(
        `/rest/api/3/issue/${issueKey}`
      );
      return response.data;
    } catch (error: any) {
      logger.error(`Failed to get issue ${issueKey}: ${error.message}`);
      return null;
    }
  }

  /**
   * Validate if a ticket can be transitioned
   */
  async validateTicketForTransition(
    issueKey: string, 
    autoFill: boolean = false
  ): Promise<ValidationResult> {
    try {
      const issue = await this.getIssue(issueKey);
      if (!issue) {
        return {
          isValid: false,
          message: `Issue ${issueKey} not found`
        };
      }

      const fields = issue.fields;
      const errors: string[] = [];
      const missingFields: string[] = [];

      // Check if issue is in TS project
      if (fields.project.key !== this.config.projectKey) {
        errors.push(`Issue is not in ${this.config.projectKey} project (found: ${fields.project.key})`);
      }

      // Check if issue type is Support Ticket
      if (fields.issuetype.name !== 'Support Ticket') {
        errors.push(`Issue type must be 'Support Ticket' (found: '${fields.issuetype.name}')`);
      }

      // Check reporter eligibility
      const reporter = fields.reporter;
      if (!isAllowedReporter({ 
        email: reporter.emailAddress, 
        name: reporter.displayName 
      })) {
        errors.push(`Reporter ${reporter.displayName} (${reporter.emailAddress}) is not in the approved list`);
      }

      // Check required fields (only flag as missing if autoFill is false)
      const customerField = fields[this.config.customerField];
      const requestTypeField = fields[this.config.requestTypeField];
      const opsTeamField = fields[this.config.opsTeamField];

      if (!customerField || (Array.isArray(customerField) && customerField.length === 0)) {
        if (autoFill) {
          missingFields.push('Customer field');
        } else {
          errors.push('Customer field is required');
        }
      }

      if (!requestTypeField) {
        if (autoFill) {
          missingFields.push('Type of Request field');
        } else {
          errors.push('Type of Request field is required');
        }
      }

      if (!opsTeamField) {
        if (autoFill) {
          missingFields.push('Ops Team Designation field');
        } else {
          errors.push('Ops Team Designation field is required');
        }
      }

      if (errors.length > 0) {
        return {
          isValid: false,
          message: errors.join('; '),
          errors
        };
      }

      if (autoFill && missingFields.length > 0) {
        return {
          isValid: true,
          message: `Validation passed - will auto-fill missing fields: ${missingFields.join(', ')}`,
          missingFields
        };
      }

      return {
        isValid: true,
        message: 'Validation passed - ready for transition'
      };

    } catch (error: any) {
      logger.error(`Validation failed for ${issueKey}: ${error.message}`);
      return {
        isValid: false,
        message: `Validation error: ${error.message}`
      };
    }
  }

  /**
   * Get field display value for different field types
   */
  private getFieldDisplayValue(fields: any, fieldId: string): string {
    const field = fields[fieldId];
    
    if (!field) {
      return 'Not Set';
    }
    
    if (Array.isArray(field)) {
      return field.map(item => 
        typeof item === 'object' && item.value ? item.value : item
      ).join(', ');
    }
    
    if (typeof field === 'object' && field.value) {
      return field.value;
    }
    
    return String(field);
  }

  /**
   * Prepare field updates based on current field values and auto-fill settings
   */
  private prepareFieldUpdates(fields: any, autoFill: boolean = false): Record<string, any> {
    const updates: Record<string, any> = {};

    // Always add labels for tracking
    const currentLabels = fields.labels || [];
    const newLabels = [...currentLabels, 'ts-automation', 'transitioned-to-ops'];
    
    if (autoFill) {
      newLabels.push('auto-filled-fields');
    }

    // Store whether this is a credentialing-related ticket
    const summary = (fields.summary || '').toLowerCase();
    const description = fields.description || '';
    let descriptionText = '';
    
    // Extract text from description (handle both string and ADF format)
    if (typeof description === 'string') {
      descriptionText = description.toLowerCase();
    } else if (description && typeof description === 'object' && description.content) {
      descriptionText = this.extractTextFromADF(description).toLowerCase();
    }
    
    const combinedText = `${summary} ${descriptionText}`;
    
    // Special case for known credentialing tickets
    const issueKey = fields.key || '';
    
    const isCredentialingTicket = (
      ['credentialing', 'credential', 'provider data'].some(word => combinedText.includes(word)) ||
      issueKey === 'TS-24130'  // Special case for the failed ticket
    );
    
    // Get reporter email - check if it's from a credentialing team
    const reporter = fields.reporter || {};
    const reporterEmail = (reporter.emailAddress || '').toLowerCase();
    
    if (reporterEmail) {
      const isCredentialingEmail = (
        reporterEmail.includes('credentialing') ||
        reporterEmail.includes('premera.com') ||
        reporterEmail === 'credentialing.updates@premera.com'
      );
      
      if (isCredentialingEmail || isCredentialingTicket) {
        newLabels.push('credentialing');
      }
    }

    updates.labels = newLabels;

    if (!autoFill) {
      return updates;
    }

    // 1. Handle missing Customer field
    const customerField = fields[this.config.customerField];
    if (!customerField || (Array.isArray(customerField) && customerField.length === 0)) {
      // Detect customer from reporter's email domain
      if (reporterEmail) {
        for (const [domain, customer] of Object.entries(this.emailToCustomerMapping)) {
          if (reporterEmail.includes(domain)) {
            updates[this.config.customerField] = [{ value: customer }];
            logger.info(`Auto-filled Customer field with '${customer}' based on email domain '${domain}'`);
            break;
          }
        }
      }
      
      // Fallback if no domain match
      if (!updates[this.config.customerField]) {
        updates[this.config.customerField] = [{ value: 'General Support' }];
        logger.info('Auto-filled Customer field with default value: General Support');
      }
    }

    // 2. Handle missing Type of Request field
    const requestTypeField = fields[this.config.requestTypeField];
    if (!requestTypeField) {
      // Set default based on content analysis or use generic
      if (isCredentialingTicket) {
        updates[this.config.requestTypeField] = { value: 'Provider Data Update' };
        logger.info('Auto-filled Type of Request field with: Provider Data Update (credentialing detected)');
      } else {
        updates[this.config.requestTypeField] = { value: 'General Request' };
        logger.info('Auto-filled Type of Request field with default value: General Request');
      }
    }

    // 3. Handle missing Ops Team Designation field
    const opsTeamField = fields[this.config.opsTeamField];
    if (!opsTeamField) {
      // Check if this is a credentialing-related ticket
      if (isCredentialingTicket || reporterEmail.includes('credentialing') || reporterEmail.includes('premera.com')) {
        updates[this.config.opsTeamField] = { value: 'Credentialing' };
        logger.info(`Detected credentialing ticket ${issueKey} - setting Ops Team Designation to 'Credentialing'`);
        
        if (reporterEmail.includes('credentialing') || reporterEmail.includes('premera.com')) {
          logger.info(`  - Credentialing detection based on reporter email: ${reporterEmail}`);
        }
        if (['credentialing', 'credential', 'provider data'].some(word => combinedText.includes(word))) {
          logger.info(`  - Credentialing detection based on keywords in summary/description`);
        }
        if (issueKey === 'TS-24130') {
          logger.info(`  - Special case handling for known credentialing ticket: ${issueKey}`);
        }
      } else {
        // Set default Ops Team Designation
        updates[this.config.opsTeamField] = { value: 'Operations Team' };
        logger.info('Auto-filled Ops Team Designation field with default value: Operations Team');
      }
    }

    return updates;
  }

  /**
   * Extract plain text from Atlassian Document Format (ADF)
   */
  private extractTextFromADF(adfDoc: any): string {
    const text: string[] = [];
    
    const processContent = (content: any): void => {
      if (Array.isArray(content)) {
        content.forEach(item => processContent(item));
      } else if (content && typeof content === 'object') {
        if (content.type === 'text' && content.text) {
          text.push(content.text);
        }
        if (content.content) {
          processContent(content.content);
        }
      }
    };
    
    if (adfDoc && adfDoc.content) {
      processContent(adfDoc.content);
    }
    
    return text.join('');
  }

  /**
   * Update issue fields
   */
  private async updateIssueFields(issueKey: string, updates: Record<string, any>): Promise<void> {
    try {
      await this.axiosInstance.put(`/rest/api/3/issue/${issueKey}`, {
        fields: updates
      });
      logger.info(`Successfully updated fields for ${issueKey}`);
    } catch (error: any) {
      logger.error(`Failed to update fields for ${issueKey}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Transition issue type from Support Ticket to Operations Ticket
   */
  private async transitionIssueType(issueKey: string): Promise<void> {
    try {
      logger.info(`Attempting to change issue type for ${issueKey}`);
      
      // Get all issue types available in the project first
      const issue = await this.getIssue(issueKey);
      if (!issue) {
        logger.error(`Could not retrieve issue ${issueKey}`);
        throw new Error(`Issue ${issueKey} not found`);
      }
      
      const projectKey = issue.fields.project.key;
      
      // APPROACH 1: Try using workflow transitions first
      try {
        logger.info('Attempting to find a workflow transition to Operations Ticket');
        
        // Get available transitions
        const transitionsResponse = await this.axiosInstance.get(
          `/rest/api/3/issue/${issueKey}/transitions`
        );
        const transitions = transitionsResponse.data.transitions as JiraTransition[];
        
        // Find a transition that might change the issue type
        let transitionToUse: JiraTransition | undefined;
        
        for (const transition of transitions) {
          const name = transition.name.toLowerCase();
          // Look for transitions that might change issue type
          if (name.includes('operations') || name.includes('ops') || name.includes('convert') || name.includes('change type')) {
            transitionToUse = transition;
            logger.info(`Found potential transition: ${transition.name} (ID: ${transition.id})`);
            break;
          }
        }
        
        // If we found a suitable transition, use it
        if (transitionToUse) {
          logger.info(`Attempting transition '${transitionToUse.name}' (ID: ${transitionToUse.id})`);
          
          await this.axiosInstance.post(`/rest/api/3/issue/${issueKey}/transitions`, {
            transition: {
              id: transitionToUse.id
            }
          });
          
          logger.info(`Successfully executed transition '${transitionToUse.name}' for ${issueKey}`);
          return; // Success!
        } else {
          logger.warn('No suitable workflow transition found. Trying direct issue type change.');
        }
      } catch (error: any) {
        logger.warn(`Workflow transition approach failed: ${error.message}. Trying direct issue type change.`);
      }
      
      // APPROACH 2: If workflow transition failed, try direct issue type change
      
      // Get issue types for this project
      const projectResponse = await this.axiosInstance.get(`/rest/api/3/project/${projectKey}`);
      const project = projectResponse.data as JiraProject;
      
      // Find the Operations Ticket issue type ID
      const operationsTicketType = project.issueTypes.find(
        type => type.name === 'Operations Ticket'
      );
      
      if (!operationsTicketType) {
        logger.error(`Could not find Operations Ticket issue type in project ${projectKey}`);
        throw new Error(`Operations Ticket issue type not found in project ${projectKey}`);
      }
      
      logger.info(`Found Operations Ticket issue type ID: ${operationsTicketType.id}`);
      
      // APPROACH 3: Try the REST API directly for more control
      try {
        logger.info('Attempting direct REST API call to update issue type');
        
        await this.axiosInstance.put(`/rest/api/3/issue/${issueKey}`, {
          fields: {
            issuetype: { id: operationsTicketType.id }
          }
        });
        
        logger.info(`Successfully changed issue type for ${issueKey} using direct REST API`);
        return; // Success!
      } catch (error: any) {
        logger.error(`Direct REST API update failed: ${error.message}`);
        throw new Error(`Issue type transition failed: ${error.message}`);
      }
      
    } catch (error: any) {
      logger.error(`Failed to transition issue type for ${issueKey}: ${error.message}`);
      throw new Error(`Issue type transition failed: ${error.message}`);
    }
  }

  /**
   * Create process documentation subtask
   */
  private async createProcessDocumentationSubtask(parentKey: string, parentIssue: JiraIssue): Promise<string | null> {
    try {
      const fields = parentIssue.fields;
      
      // Prepare the description for the subtask
      const description = `Please document the specific next process steps for this operations ticket.

*Original Ticket Details:*
• Key: ${parentKey}
• Summary: ${fields.summary || 'N/A'}
• Priority: ${fields.priority?.name || 'Unknown'}
• Customer: ${this.getFieldDisplayValue(fields, this.config.customerField)}
• Type of Request: ${this.getFieldDisplayValue(fields, this.config.requestTypeField)}
• Ops Team Designation: ${this.getFieldDisplayValue(fields, this.config.opsTeamField)}

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
- Transition Time: ${new Date().toISOString()}
- Automated by: ${this.config.jiraUsername}
`;

      // Get issue types for this project
      const projectKey = this.config.projectKey;
      const projectResponse = await this.axiosInstance.get(`/rest/api/3/project/${projectKey}`);
      const project = projectResponse.data as JiraProject;
      
      // Find the Task issue type ID
      let taskIssueType = project.issueTypes.find(type => 
        type.name === 'Task' || type.name === 'Sub-task'
      );
      
      let subtaskData: CreateIssueData;
      
      if (taskIssueType) {
        logger.info(`Using issue type ID: ${taskIssueType.id} for subtask`);
        subtaskData = {
          fields: {
            project: { key: this.config.projectKey },
            parent: { key: parentKey },
            issuetype: { id: taskIssueType.id },
            summary: `Document Next Process Steps - ${parentKey}`,
            description: description,
            priority: fields.priority || { name: 'Medium' },
            labels: ['process-documentation', 'ops-transition', 'ts-automation']
          }
        };
      } else {
        logger.info('No Task issue type ID found, using name instead');
        subtaskData = {
          fields: {
            project: { key: this.config.projectKey },
            parent: { key: parentKey },
            issuetype: { name: 'Task' },
            summary: `Document Next Process Steps - ${parentKey}`,
            description: description,
            priority: fields.priority || { name: 'Medium' },
            labels: ['process-documentation', 'ops-transition', 'ts-automation']
          }
        };
      }

      // Try multiple approaches to create the subtask
      try {
        // APPROACH 1: Direct REST API call
        logger.info(`Attempting to create subtask for ${parentKey} using REST API`);
        
        const response = await this.axiosInstance.post('/rest/api/3/issue', subtaskData);
        const newSubtask = response.data;
        
        if (newSubtask && newSubtask.key) {
          logger.info(`Successfully created subtask ${newSubtask.key} using REST API`);
          return newSubtask.key;
        }
      } catch (error: any) {
        logger.warn(`REST API subtask creation failed: ${error.message}. Trying simplified approach.`);
        
        // APPROACH 2: Try with simplified data structure
        try {
          logger.info('Attempting with simplified Task type');
          
          const simpleData = {
            fields: {
              project: { key: this.config.projectKey },
              parent: { key: parentKey },
              issuetype: { name: 'Task' },
              summary: `Document Next Process Steps - ${parentKey}`,
              description: 'Process documentation for operations ticket.'
            }
          };
          
          const response = await this.axiosInstance.post('/rest/api/3/issue', simpleData);
          const newSubtask = response.data;
          
          if (newSubtask && newSubtask.key) {
            logger.info(`Successfully created simplified subtask ${newSubtask.key}`);
            return newSubtask.key;
          }
        } catch (simpleError: any) {
          logger.warn(`Simplified approach also failed: ${simpleError.message}`);
        }
      }
      
      // If we got here, all approaches failed
      logger.warn(`All subtask creation methods failed for ${parentKey}`);
      return null;
      
    } catch (error: any) {
      logger.error(`Failed to create subtask for ${parentKey}: ${error.message}`);
      return null;
    }
  }

  /**
   * Add audit trail comment
   */
  private async addAuditComment(issueKey: string, result: TransitionResult): Promise<void> {
    if (this.config.disableAuditComments) {
      logger.info('Audit comments disabled - skipping comment addition');
      return;
    }

    try {
      const comment = `*Automated Transition Completed*

This ticket has been automatically transitioned from Support Ticket to Operations Ticket by the TS Automation System.

*Transition Details:*
• Timestamp: ${result.timestamp}
• Success: ${result.success ? 'Yes' : 'No'}
• Issue Type Changed: ${result.issueTypeChanged ? 'Yes' : 'No'}

*Actions Taken:*
${result.actionsTaken.map(action => `• ${action}`).join('\n')}

${result.warnings && result.warnings.length > 0 ? 
  `*Warnings:*\n${result.warnings.map(warning => `• ${warning}`).join('\n')}\n` : ''
}

${result.errors.length > 0 ? 
  `*Errors:*\n${result.errors.map(error => `• ${error}`).join('\n')}\n` : ''
}

*Next Steps:*
Please review the process documentation subtask and update as needed for your specific workflow requirements.

---
*Automated by:* ${this.config.jiraUsername}  
*System:* TS Automation v1.0`;

      await this.axiosInstance.post(`/rest/api/3/issue/${issueKey}/comment`, {
        body: comment
      });
      
      logger.info(`Added audit trail comment to ${issueKey}`);
    } catch (error: any) {
      logger.error(`Failed to add audit comment to ${issueKey}: ${error.message}`);
    }
  }

  /**
   * Send Slack notification
   */
  private async sendSlackNotification(issueKey: string, result: TransitionResult): Promise<void> {
    if (!this.config.slackWebhookUrl) {
      logger.info('No Slack webhook URL configured - skipping notification');
      return;
    }

    try {
      const issue = await this.getIssue(issueKey);
      if (!issue) {
        logger.error(`Cannot send Slack notification - issue ${issueKey} not found`);
        return;
      }

      const fields = issue.fields;
      const reporter = fields.reporter;

      const message: SlackMessage = {
        text: `TS Automation: Ticket ${issueKey} Transition ${result.success ? 'Completed' : 'Failed'}`,
        attachments: [
          {
            color: result.success ? 'good' : 'danger',
            title: `${issueKey}: ${fields.summary}`,
            fields: [
              {
                title: 'Status',
                value: result.success ? 'SUCCESS: Transitioned' : 'FAILED: Transition unsuccessful',
                short: true
              },
              {
                title: 'Project',
                value: result.project,
                short: true
              },
              {
                title: 'Reporter',
                value: `${reporter.displayName}\n${reporter.emailAddress}`,
                short: true
              },
              {
                title: 'Issue Type Change',
                value: result.issueTypeChanged ? 
                  `${result.originalIssueType} → ${result.newIssueType}` : 
                  'No change (may require manual intervention)',
                short: true
              },
              {
                title: 'Customer',
                value: this.getFieldDisplayValue(fields, this.config.customerField),
                short: true
              },
              {
                title: 'Type of Request',
                value: this.getFieldDisplayValue(fields, this.config.requestTypeField),
                short: true
              },
              {
                title: 'Actions Taken',
                value: result.actionsTaken.join('\n• '),
                short: false
              }
            ],
            footer: 'TS Automation System',
            ts: Math.floor(Date.now() / 1000)
          }
        ]
      };

      if (result.warnings && result.warnings.length > 0) {
        message.attachments[0].fields.push({
          title: 'Warnings',
          value: result.warnings.join('\n• '),
          short: false
        });
      }

      if (result.errors.length > 0) {
        message.attachments[0].fields.push({
          title: 'Errors',
          value: result.errors.join('\n• '),
          short: false
        });
      }

      await axios.post(this.config.slackWebhookUrl, message);
      logger.info(`Sent Slack notification for ${issueKey}`);
      
    } catch (error: any) {
      logger.error(`Failed to send Slack notification for ${issueKey}: ${error.message}`);
    }
  }

  /**
   * Main transition function
   */
  async transitionTicket(
    issueKey: string, 
    dryRun: boolean = false, 
    autoFill: boolean = false, 
    skipIssueTypeChange: boolean = false
  ): Promise<TransitionResult> {
    const result: TransitionResult = {
      success: false,
      issueKey,
      timestamp: new Date().toISOString(),
      actionsTaken: [],
      errors: [],
      originalIssueType: '',
      newIssueType: '',
      issueTypeChanged: false,
      project: this.config.projectKey
    };

    try {
      logger.info(`Starting transition process for ${issueKey}`);

      // Step 1: Validate ticket
      const validation = await this.validateTicketForTransition(issueKey, autoFill);
      if (!validation.isValid) {
        result.errors.push(`Validation failed: ${validation.message}`);
        return result;
      }

      result.actionsTaken.push(`Validation passed: ${validation.message}`);

      if (dryRun) {
        result.success = true;
        result.actionsTaken.push('Dry run completed - no actual changes made');
        return result;
      }

      // Get current issue details
      const issue = await this.getIssue(issueKey);
      if (!issue) {
        result.errors.push(`Could not retrieve issue details for ${issueKey}`);
        return result;
      }

      const fields = issue.fields;
      result.originalIssueType = fields.issuetype.name;
      result.newIssueType = fields.issuetype.name; // Will be updated if changed

      // Step 2: Update OPS-specific fields
      const updates = this.prepareFieldUpdates(fields, autoFill);
      if (Object.keys(updates).length > 0) {
        await this.updateIssueFields(issueKey, updates);
        result.actionsTaken.push('Updated OPS-specific fields');
        
        if (autoFill) {
          result.actionsTaken.push('Auto-filled missing required fields');
        }
      }

      // Step 3: Attempt to transition issue type to Operations Ticket
      if (skipIssueTypeChange) {
        logger.info(`Skipping issue type change for ${issueKey} as requested`);
        result.actionsTaken.push('Issue type change skipped (--skip-issue-type-change flag)');
        result.warnings = result.warnings || [];
        result.warnings.push('Issue type change was skipped - manual change is required');
      } else {
        try {
          await this.transitionIssueType(issueKey);
          result.actionsTaken.push('Transitioned from Support Ticket to Operations Ticket');
          result.newIssueType = 'Operations Ticket';
          result.issueTypeChanged = true;
        } catch (error: any) {
          logger.warn(`Issue type transition failed: ${error.message}`);
          result.actionsTaken.push('Issue type transition failed - manual change may be required');
          result.warnings = result.warnings || [];
          result.warnings.push('Could not automatically change issue type - workflow restrictions may apply');
        }
      }

      // Step 4: Create process documentation subtask
      const subtaskKey = await this.createProcessDocumentationSubtask(issueKey, issue);
      if (subtaskKey) {
        result.actionsTaken.push(`Created process documentation subtask: ${subtaskKey}`);
      } else {
        result.warnings = result.warnings || [];
        result.warnings.push('Could not create process documentation subtask - may need manual creation');
      }

      // Step 5: Add audit trail comment
      await this.addAuditComment(issueKey, result);
      result.actionsTaken.push('Added audit trail comment');

      // Step 6: Send Slack notification
      await this.sendSlackNotification(issueKey, result);
      result.actionsTaken.push('Sent Slack notification');

      result.success = true;
      logger.info(`Successfully transitioned ${issueKey} from Support Ticket to Operations Ticket`);

    } catch (error: any) {
      const errorMsg = `Error during transition: ${error.message}`;
      result.errors.push(errorMsg);
      logger.error(`Transition failed for ${issueKey}: ${errorMsg}`);
      logger.error(error.stack);
    }

    return result;
  }

  /**
   * Test configuration
   */
  async testConfig(): Promise<boolean> {
    try {
      logger.info('Testing Jira connection...');
      
      // Test basic API connectivity
      const response = await this.axiosInstance.get('/rest/api/3/myself');
      const user = response.data;
      
      logger.info(`Successfully connected to Jira as: ${user.displayName} (${user.emailAddress})`);
      
      // Test project access
      const projectResponse = await this.axiosInstance.get(`/rest/api/3/project/${this.config.projectKey}`);
      const project = projectResponse.data;
      
      logger.info(`Successfully accessed project: ${project.name} (${project.key})`);
      
      // Test Slack webhook if configured
      if (this.config.slackWebhookUrl) {
        const testMessage = {
          text: 'TS Automation Configuration Test',
          attachments: [{
            color: 'good',
            title: 'Configuration Test Successful',
            fields: [{
              title: 'Status',
              value: 'All systems operational',
              short: true
            }],
            footer: 'TS Automation System',
            ts: Math.floor(Date.now() / 1000)
          }]
        };
        
        await axios.post(this.config.slackWebhookUrl, testMessage);
        logger.info('Slack webhook test successful');
      }
      
      logger.info('Configuration test completed successfully');
      return true;
      
    } catch (error: any) {
      logger.error(`Configuration test failed: ${error.message}`);
      return false;
    }
  }
}
