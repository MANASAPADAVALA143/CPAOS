/**
 * GNANOVA CA PRACTICE OS - Audit Types
 * Phase 4: Audit engagements, working papers, PBC, risk assessment
 */

export type EngagementType = 
  | 'statutory_audit'
  | 'tax_audit'
  | 'internal_audit'
  | 'review'
  | 'agreed_upon_procedures';

export type EngagementStatus = 
  | 'planning'
  | 'fieldwork'
  | 'review'
  | 'reporting'
  | 'completed'
  | 'archived';

export type WorkingPaperStatus = 
  | 'draft'
  | 'in_progress'
  | 'review'
  | 'approved';

export type RiskRating = 'low' | 'medium' | 'high';

export type PBCStatus =
  | 'pending'
  | 'requested'
  | 'received'
  | 'reviewed'
  | 'accepted'
  | 'rejected';

export type ReviewNoteStatus =
  | 'open'
  | 'addressed'
  | 'cleared'
  | 'deferred';

export interface AuditEngagement {
  id: string;
  firm_id: string;
  client_id: string;
  
  engagement_name: string;
  engagement_code: string;
  engagement_type: EngagementType;
  
  financial_year: string;
  period_start: string;
  period_end: string;
  
  engagement_partner?: string;
  audit_manager?: string;
  audit_senior?: string;
  team_members?: string[];
  
  status: EngagementStatus;
  
  planned_start_date?: string;
  planned_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  report_date?: string;
  
  budgeted_hours?: number;
  actual_hours: number;
  
  overall_risk_rating?: RiskRating;
  materiality_amount?: number;
  
  description?: string;
  scope?: string;
  notes?: string;
  
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface PBCChecklistItem {
  id: string;
  firm_id: string;
  engagement_id: string;
  
  item_name: string;
  item_category?: string;
  description?: string;
  
  is_mandatory: boolean;
  status: PBCStatus;
  
  requested_date?: string;
  due_date?: string;
  received_date?: string;
  reviewed_by?: string;
  reviewed_date?: string;
  
  document_id?: string;
  notes?: string;
  
  created_at: string;
  updated_at: string;
}

export interface WorkingPaper {
  id: string;
  firm_id: string;
  engagement_id: string;
  
  reference_number: string;
  title: string;
  section?: string;
  
  description?: string;
  procedure_performed?: string;
  findings?: string;
  conclusion?: string;
  
  status: WorkingPaperStatus;
  
  prepared_by?: string;
  prepared_date?: string;
  reviewed_by?: string;
  reviewed_date?: string;
  approved_by?: string;
  approved_date?: string;
  
  document_ids?: string[];
  
  created_at: string;
  updated_at: string;
}

export interface RiskAssessment {
  id: string;
  firm_id: string;
  engagement_id: string;
  
  risk_area: string;
  risk_description: string;
  
  inherent_risk?: RiskRating;
  control_risk?: RiskRating;
  detection_risk?: RiskRating;
  overall_risk?: RiskRating;
  
  controls_identified?: string;
  audit_procedures?: string;
  
  assessed_by?: string;
  assessed_date?: string;
  
  created_at: string;
  updated_at: string;
}

export interface ReviewNote {
  id: string;
  firm_id: string;
  engagement_id: string;
  working_paper_id?: string;
  
  note_type: string;
  note_text: string;
  
  raised_by?: string;
  raised_date?: string;
  
  assigned_to?: string;
  
  status: ReviewNoteStatus;
  
  response_text?: string;
  responded_by?: string;
  responded_date?: string;
  
  cleared_by?: string;
  cleared_date?: string;
  
  created_at: string;
  updated_at: string;
}

export interface AuditDashboardStats {
  total_engagements: number;
  active_engagements: number;
  planning_phase: number;
  fieldwork_phase: number;
  review_phase: number;
  reporting_phase: number;
  completed: number;
  
  total_working_papers: number;
  draft_papers: number;
  approved_papers: number;
  
  total_pbc_items: number;
  pending_pbc: number;
  received_pbc: number;
  
  open_review_notes: number;
  high_risk_areas: number;
}

// Request payloads
export interface CreateAuditEngagementPayload {
  client_id: string;
  engagement_name: string;
  engagement_type: EngagementType;
  financial_year: string;
  period_start: string;
  period_end: string;
  engagement_partner?: string;
  audit_manager?: string;
  audit_senior?: string;
  description?: string;
  scope?: string;
  budgeted_hours?: number;
  materiality_amount?: number;
}

export interface UpdateAuditEngagementPayload {
  engagement_name?: string;
  status?: EngagementStatus;
  engagement_partner?: string;
  audit_manager?: string;
  audit_senior?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  report_date?: string;
  overall_risk_rating?: RiskRating;
  description?: string;
  scope?: string;
  notes?: string;
}

export interface CreateWorkingPaperPayload {
  engagement_id: string;
  reference_number: string;
  title: string;
  section?: string;
  description?: string;
}

export interface CreatePBCItemPayload {
  engagement_id: string;
  item_name: string;
  item_category?: string;
  description?: string;
  is_mandatory: boolean;
  due_date?: string;
}

export interface CreateRiskAssessmentPayload {
  engagement_id: string;
  risk_area: string;
  risk_description: string;
  inherent_risk?: RiskRating;
  control_risk?: RiskRating;
  detection_risk?: RiskRating;
  overall_risk?: RiskRating;
  controls_identified?: string;
  audit_procedures?: string;
}

export interface CreateReviewNotePayload {
  engagement_id: string;
  working_paper_id?: string;
  note_type: string;
  note_text: string;
  assigned_to?: string;
  raised_date: string;
}
