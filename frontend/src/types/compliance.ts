/**
 * Compliance management types for GNANOVA CA Practice OS - Phase 2
 */

export type ComplianceFrequency = 'monthly' | 'quarterly' | 'half_yearly' | 'annual' | 'event_based'

export type ComplianceStatus = 'pending' | 'in_progress' | 'completed' | 'overdue' | 'not_applicable'

export type ReminderType = 'notification' | 'email' | 'whatsapp' | 'escalation'

export type AlertType = 'reminder' | 'overdue' | 'escalation' | 'completed' | 'due_soon'

export type AlertSeverity = 'info' | 'warning' | 'critical'

export type DocumentRequirementStatus = 'pending' | 'uploaded' | 'verified' | 'rejected'

export interface ComplianceTemplate {
  id: string
  firm_id?: string
  country: string
  service_category: string
  compliance_name: string
  compliance_code?: string
  description?: string
  frequency: ComplianceFrequency
  due_day_of_month?: number
  due_month?: number
  due_days_after_period_end?: number
  applies_to_entity_types: string[]
  is_active: boolean
  is_system_template: boolean
  documents_required: string[]
  auto_create_assignment: boolean
  priority: string
  estimated_hours?: number
  penalty_info?: string
  created_at: string
  updated_at?: string
}

export interface ComplianceRequirement {
  id: string
  firm_id: string
  client_id: string
  template_id?: string
  compliance_name: string
  service_category: string
  financial_year: string
  period_start?: string
  period_end?: string
  due_date: string
  status: ComplianceStatus
  completion_date?: string
  assignment_id?: string
  assigned_to?: string
  priority: string
  is_enabled: boolean
  notes?: string
  created_by?: string
  created_at: string
  updated_at?: string
  
  // Joined/calculated fields
  client_name?: string
  assigned_to_name?: string
  template_code?: string
  days_until_due?: number
  is_overdue?: boolean
}

export interface ComplianceReminder {
  id: string
  firm_id: string
  template_id?: string
  reminder_name: string
  days_before_due: number
  reminder_type: ReminderType
  escalate_to_role?: string
  is_active: boolean
  message_template?: string
  created_at: string
  updated_at?: string
}

export interface ComplianceAlert {
  id: string
  firm_id: string
  requirement_id: string
  reminder_id?: string
  alert_type: AlertType
  severity: AlertSeverity
  recipient_id: string
  message: string
  sent_at: string
  read_at?: string
  dismissed_at?: string
  notification_sent: boolean
  created_at: string
  
  // Joined fields
  requirement_name?: string
  client_name?: string
  due_date?: string
  recipient_name?: string
}

export interface DocumentRequirement {
  id: string
  firm_id: string
  requirement_id: string
  document_name: string
  document_type?: string
  is_mandatory: boolean
  status: DocumentRequirementStatus
  document_id?: string
  uploaded_at?: string
  verified_by?: string
  verified_at?: string
  rejection_reason?: string
  created_at: string
  
  // Joined fields
  document_filename?: string
  verified_by_name?: string
}

export interface CreateComplianceRequirementPayload {
  client_id: string
  template_id?: string
  compliance_name: string
  service_category: string
  financial_year: string
  period_start?: string
  period_end?: string
  due_date: string
  priority: string
  assigned_to?: string
  notes?: string
}

export interface UpdateComplianceRequirementPayload {
  status?: ComplianceStatus
  assigned_to?: string
  priority?: string
  due_date?: string
  completion_date?: string
  notes?: string
  is_enabled?: boolean
}

export interface GenerateCompliancePayload {
  client_id: string
  financial_year: string
}

export interface ComplianceDashboardStats {
  total_requirements: number
  pending: number
  in_progress: number
  completed: number
  overdue: number
  due_this_week: number
  due_this_month: number
  total_alerts: number
  unread_alerts: number
  upcoming_deadlines?: ComplianceRequirement[]
}
