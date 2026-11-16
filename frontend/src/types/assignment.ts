/**
 * Assignment management types for GNANOVA CA Practice OS
 */

export type ServiceCategory =
  | 'GST'
  | 'Income Tax'
  | 'TDS'
  | 'TCS'
  | 'MCA'
  | 'ROC'
  | 'Audit'
  | 'Accounting'
  | 'Payroll'
  | 'Advisory'
  | 'Other'

export type AssignmentStatus =
  | 'created'
  | 'assigned'
  | 'in_progress'
  | 'submitted'
  | 'manager_review'
  | 'partner_review'
  | 'approved'
  | 'completed'
  | 'on_hold'
  | 'cancelled'

export type AssignmentPriority = 'low' | 'medium' | 'high' | 'urgent'

export type ReviewLevel = 'manager' | 'partner'

export type ReviewStatus = 'pending' | 'approved' | 'rejected' | 'changes_requested'

export interface Assignment {
  id: string
  assignment_code: string
  assignment_name: string
  client_id: string
  client_name: string
  service_category: ServiceCategory
  assignment_type: string
  financial_year: string
  period_start?: string
  period_end?: string
  start_date?: string
  due_date: string
  completed_date?: string
  priority: AssignmentPriority
  status: AssignmentStatus
  completion_pct: number
  estimated_hours?: number
  actual_hours?: number
  description?: string
  internal_notes?: string
  assigned_partner?: string
  assigned_partner_name?: string
  assigned_manager?: string
  assigned_manager_name?: string
  assigned_staff?: string
  assigned_staff_name?: string
  created_at: string
  updated_at?: string
}

export interface AssignmentReview {
  id: string
  review_level: ReviewLevel
  reviewer_name: string
  submitted_at: string
  reviewed_at?: string
  status: ReviewStatus
  comments?: string
  rejection_reason?: string
}

export interface CreateAssignmentPayload {
  client_id: string
  assignment_name: string
  service_category: ServiceCategory
  assignment_type: string
  financial_year: string
  period_start?: string
  period_end?: string
  assigned_partner?: string
  assigned_manager?: string
  assigned_staff?: string
  start_date?: string
  due_date: string
  priority: AssignmentPriority
  estimated_hours?: number
  description?: string
}

export interface UpdateAssignmentPayload {
  assignment_name?: string
  status?: AssignmentStatus
  assigned_partner?: string
  assigned_manager?: string
  assigned_staff?: string
  due_date?: string
  priority?: AssignmentPriority
  estimated_hours?: number
  actual_hours?: number
  description?: string
  internal_notes?: string
}

export interface PracticeDashboardKPIs {
  total_clients: number
  active_clients: number
  active_assignments: number
  overdue_assignments: number
  completed_assignments_month: number
  pending_manager_reviews: number
  pending_partner_reviews: number
  pending_reviews: number
  docs_pending_review: number
  staff_utilization: number
}

export interface PracticeDashboardData {
  kpis: PracticeDashboardKPIs
  assignments_by_status: Array<{ status: string; count: number }>
  overdue_assignments: Array<{
    assignment_id: string
    assignment_code: string
    assignment_name: string
    client_name: string
    due_date: string
    days_overdue: number
    assigned_staff?: string
  }>
  staff_workload: Array<{
    staff_id: string
    staff_name: string
    designation: string
    department: string
    assignments_count: number
    estimated_hours: number
    actual_hours: number
    utilization_pct: number
  }>
}
