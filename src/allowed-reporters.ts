/**
 * Allowed reporters for ticket transitions
 * This module contains the list of reporter emails and names that are allowed
 * to have their tickets transitioned from Support Ticket to Operations Ticket.
 */

// List of allowed reporter email addresses and names
export const ALLOWED_REPORTERS: string[] = [
  // Elevance-Carelon
  'Kelli-Ann.Bailey@carelon.com',
  
  // FCHN (First Choice Health Network)
  'Cindy Bergley',
  'cbergley',  // Jira username for Cindy Bergley
  'Abby Fuller',
  'Tanya Ramirez',
  'Steffany Taylor',
  
  // Premera
  'credentialing.updates@premera.com',
  
  // Headway
  'edna.villareal@findheadway.com',
  'luis.valdez@findheadway.com',
  'katie.cassidy@findheadway.com',
  'stephani.vasquez@findheadway.com',
  'gavin.green@findheadway.com',
  'valorie.reyes@findheadway.com',
  'amy.huh@findheadway.com',
  'Zara Aghajanyan',
  
  // SCAN
  'c.smith@scanhealthplan.com',
  'b.chan@scanhealthplan.com',
  'li.lopez@scanhealthplan.com',
  'a.liu@scanhealthplan.com',
  'EVo@scanhealthplan.com',
  'a.vuc@scanhealthplan.com',
  'mo.davila@scanhealthplan.com',
  'Carrie Black',
  
  // University of Utah Health Plan
  'Charlene Frail-McGeever',
  'Aimee.Kulp@hsc.utah.edu'
];

// Email domain allowlist - emails from these domains are allowed
export const ALLOWED_DOMAINS: string[] = [
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
];

/**
 * Check if a reporter is allowed based on email or name
 * 
 * @param options - Object containing email and/or name
 * @returns True if the reporter is allowed, false otherwise
 */
export function isAllowedReporter(options: { email?: string; name?: string }): boolean {
  const { email, name } = options;
  
  // Check if either email or name is in the allowed list
  if (email && ALLOWED_REPORTERS.some(r => r.toLowerCase() === email.toLowerCase())) {
    return true;
  }
  
  if (name && ALLOWED_REPORTERS.some(r => r.toLowerCase() === name.toLowerCase())) {
    return true;
  }
  
  // Check if email domain is allowed
  if (email) {
    for (const domain of ALLOWED_DOMAINS) {
      if (email.toLowerCase().endsWith(`@${domain.toLowerCase()}`)) {
        return true;
      }
    }
  }
  
  return false;
}
