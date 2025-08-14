/**
 * TypeScript interfaces and types for Jira Automation
 */

export interface JiraField {
  id: string;
  value?: string;
  self?: string;
  [key: string]: any;
}

export interface JiraIssue {
  key: string;
  id: string;
  self: string;
  fields: {
    summary: string;
    description?: string | JiraContent;
    status: {
      name: string;
      id: string;
    };
    issuetype: {
      name: string;
      id: string;
    };
    project: {
      key: string;
      name: string;
    };
    reporter: {
      displayName: string;
      emailAddress: string;
      accountId: string;
    };
    priority?: {
      name: string;
      id: string;
    };
    labels?: string[];
    [key: string]: any;
  };
}

export interface JiraContent {
  version: number;
  type: string;
  content: any[];
}

export interface JiraTransition {
  id: string;
  name: string;
  to: {
    name: string;
    id: string;
  };
  fields?: { [key: string]: any };
}

export interface JiraIssueType {
  id: string;
  name: string;
  description?: string;
  subtask?: boolean;
}

export interface JiraProject {
  key: string;
  name: string;
  id: string;
  issueTypes: JiraIssueType[];
}

export interface TSConfig {
  jiraUrl: string;
  jiraUsername: string;
  jiraApiToken: string;
  slackWebhookUrl?: string;
  projectKey: string;
  
  // Required fields
  customerField: string;        // Customer(s)
  requestTypeField: string;     // Type of Request  
  opsTeamField: string;         // Ops Team Designation
  
  // Configuration options
  disableAuditComments: boolean;
}

export interface TransitionResult {
  success: boolean;
  issueKey: string;
  timestamp: string;
  actionsTaken: string[];
  errors: string[];
  warnings?: string[];
  originalIssueType: string;
  newIssueType: string;
  issueTypeChanged: boolean;
  project: string;
}

export interface ValidationResult {
  isValid: boolean;
  message: string;
  missingFields?: string[];
  errors?: string[];
}

export interface SlackAttachment {
  color: string;
  title: string;
  fields: Array<{
    title: string;
    value: string;
    short: boolean;
  }>;
  footer: string;
  ts: number;
}

export interface SlackMessage {
  text: string;
  attachments: SlackAttachment[];
}

export interface EmailDomainMapping {
  [domain: string]: string;
}

export interface AllowedReporter {
  email: string;
  name: string;
  department?: string;
}

export interface CreateIssueData {
  fields: {
    project: { key: string };
    parent?: { key: string };
    issuetype: { id?: string; name?: string };
    summary: string;
    description?: string | JiraContent;
    priority?: { name: string };
    labels?: string[];
    [key: string]: any;
  };
}

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';
