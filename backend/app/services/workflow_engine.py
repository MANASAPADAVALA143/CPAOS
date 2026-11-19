"""
GNANOVA CA PRACTICE OS - Workflow Automation Engine
Automatic triggers, escalations, and rule-based workflows
"""

from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from supabase import Client

from app.services.email_service import email_service
from app.db import repo


class WorkflowEngine:
    """Automated workflow engine for assignments, compliance, and audit"""
    
    def __init__(self):
        self.rules = []
    
    # ========================================================================
    # ASSIGNMENT WORKFLOWS
    # ========================================================================
    
    def trigger_assignment_created(
        self,
        sb: Client,
        firm_id: UUID,
        assignment: dict,
        assigned_to: dict,
        assigned_by: dict,
    ):
        """Auto-trigger when assignment is created"""
        
        # Send email notification to assigned staff
        if assigned_to.get('email'):
            email_service.send_assignment_notification(
                to_email=assigned_to['email'],
                assignment_name=assignment['assignment_name'],
                assignment_code=assignment['assignment_code'],
                due_date=assignment.get('due_date', 'Not set'),
                assigned_by=assigned_by.get('full_name', 'System'),
            )
        
        # Create activity log
        repo.create_activity_log(
            sb,
            firm_id,
            {
                "entity_type": "assignment",
                "entity_id": assignment['id'],
                "action": "created",
                "description": f"Assignment {assignment['assignment_code']} created",
                "performed_by": assigned_by['id'],
            }
        )
        
        return {"status": "triggered", "notifications_sent": 1}
    
    def trigger_assignment_overdue(
        self,
        sb: Client,
        firm_id: UUID,
        assignment: dict,
    ):
        """Auto-trigger when assignment becomes overdue"""
        
        # Update assignment status to overdue
        repo.update_assignment(
            sb,
            UUID(assignment['id']),
            firm_id,
            {"status": "overdue"}
        )
        
        # Get assigned staff
        if assignment.get('assigned_to'):
            staff = repo.firm_user_by_id(sb, UUID(assignment['assigned_to']), firm_id)
            if staff and staff.get('email'):
                # Send overdue notification
                from app.services.email_service import MIMEMultipart, MIMEText
                # Using email service for now
                pass
        
        # Escalate to manager
        if assignment.get('manager_id'):
            manager = repo.firm_user_by_id(sb, UUID(assignment['manager_id']), firm_id)
            if manager and manager.get('email'):
                # Send escalation email
                pass
        
        return {"status": "escalated"}
    
    def trigger_assignment_submitted(
        self,
        sb: Client,
        firm_id: UUID,
        assignment: dict,
        submitted_by: dict,
    ):
        """Auto-trigger when assignment is submitted for review"""
        
        # Determine reviewer based on review level
        reviewer_id = None
        if assignment['status'] == 'submitted':
            # First review - manager
            reviewer_id = assignment.get('manager_id')
            review_level = 'manager'
        elif assignment['status'] == 'manager_review':
            # Second review - partner
            reviewer_id = assignment.get('partner_id')
            review_level = 'partner'
        
        if reviewer_id:
            reviewer = repo.firm_user_by_id(sb, UUID(reviewer_id), firm_id)
            if reviewer and reviewer.get('email'):
                email_service.send_review_notification(
                    to_email=reviewer['email'],
                    assignment_name=assignment['assignment_name'],
                    submitted_by=submitted_by.get('full_name', 'Staff'),
                    review_level=review_level,
                )
        
        return {"status": "triggered", "reviewer_notified": True}
    
    # ========================================================================
    # COMPLIANCE WORKFLOWS
    # ========================================================================
    
    def trigger_compliance_due_soon(
        self,
        sb: Client,
        firm_id: UUID,
        compliance: dict,
        days_until_due: int,
    ):
        """Auto-trigger compliance reminders based on days until due"""
        
        # Get client
        client = repo.client_by_id(sb, UUID(compliance['client_id']), firm_id)
        
        # Get assigned staff
        if compliance.get('assigned_to'):
            staff = repo.firm_user_by_id(sb, UUID(compliance['assigned_to']), firm_id)
            if staff and staff.get('email'):
                email_service.send_compliance_reminder(
                    to_email=staff['email'],
                    compliance_name=compliance['compliance_name'],
                    due_date=compliance['due_date'],
                    days_until_due=days_until_due,
                    client_name=client.get('name', 'Client'),
                )
        
        # Create alert if urgent (3 days or less)
        if days_until_due <= 3:
            repo.create_compliance_alert(
                sb,
                firm_id,
                {
                    "requirement_id": compliance['id'],
                    "alert_type": "overdue_warning",
                    "severity": "high",
                    "message": f"Compliance {compliance['compliance_name']} due in {days_until_due} days",
                    "due_date": compliance['due_date'],
                }
            )
        
        return {"status": "triggered", "alert_created": days_until_due <= 3}
    
    def trigger_compliance_completed(
        self,
        sb: Client,
        firm_id: UUID,
        compliance: dict,
        completed_by: dict,
    ):
        """Auto-trigger when compliance is completed"""
        
        # Create activity log
        repo.create_activity_log(
            sb,
            firm_id,
            {
                "entity_type": "compliance",
                "entity_id": compliance['id'],
                "action": "completed",
                "description": f"Compliance {compliance['compliance_name']} completed",
                "performed_by": completed_by['id'],
            }
        )
        
        # Notify client (if email exists)
        client = repo.client_by_id(sb, UUID(compliance['client_id']), firm_id)
        if client and client.get('contact_email'):
            # Send completion notification to client
            pass
        
        return {"status": "triggered"}
    
    # ========================================================================
    # AUDIT WORKFLOWS
    # ========================================================================
    
    def trigger_audit_engagement_created(
        self,
        sb: Client,
        firm_id: UUID,
        engagement: dict,
        created_by: dict,
    ):
        """Auto-trigger when audit engagement is created"""
        
        # Notify engagement team
        team_members = []
        
        if engagement.get('engagement_partner'):
            team_members.append((engagement['engagement_partner'], 'Engagement Partner'))
        if engagement.get('audit_manager'):
            team_members.append((engagement['audit_manager'], 'Audit Manager'))
        if engagement.get('audit_senior'):
            team_members.append((engagement['audit_senior'], 'Audit Senior'))
        
        for member_id, role in team_members:
            member = repo.firm_user_by_id(sb, UUID(member_id), firm_id)
            if member and member.get('email'):
                email_service.send_audit_engagement_notification(
                    to_email=member['email'],
                    engagement_name=engagement['engagement_name'],
                    engagement_code=engagement['engagement_code'],
                    role=role,
                    start_date=engagement.get('planned_start_date', 'TBD'),
                )
        
        return {"status": "triggered", "notifications_sent": len(team_members)}
    
    def trigger_pbc_due_soon(
        self,
        sb: Client,
        firm_id: UUID,
        pbc_item: dict,
        days_until_due: int,
    ):
        """Auto-trigger PBC item reminders"""
        
        # Get engagement
        engagement_res = sb.table("audit_engagements").select("*").eq("id", pbc_item['engagement_id']).single().execute()
        engagement = engagement_res.data
        
        # Get client
        client = repo.client_by_id(sb, UUID(engagement['client_id']), firm_id)
        
        # Send reminder to client
        if client and client.get('contact_email'):
            email_service.send_pbc_request(
                to_email=client['contact_email'],
                client_name=client['name'],
                pbc_items=[pbc_item['item_name']],
                due_date=pbc_item['due_date'],
                engagement_name=engagement['engagement_name'],
            )
        
        return {"status": "triggered"}
    
    # ========================================================================
    # INVOICE WORKFLOWS
    # ========================================================================
    
    def trigger_invoice_created(
        self,
        sb: Client,
        firm_id: UUID,
        invoice: dict,
        client: dict,
    ):
        """Auto-trigger when invoice is created"""
        
        # Send invoice to client
        if client.get('contact_email'):
            email_service.send_invoice_notification(
                to_email=client['contact_email'],
                client_name=client['name'],
                invoice_number=invoice['invoice_number'],
                invoice_amount=invoice['total_amount'],
                due_date=invoice['due_date'],
            )
        
        return {"status": "triggered"}
    
    def trigger_invoice_overdue(
        self,
        sb: Client,
        firm_id: UUID,
        invoice: dict,
        days_overdue: int,
    ):
        """Auto-trigger when invoice becomes overdue"""
        
        # Update invoice status
        repo.update_invoice_status(sb, UUID(invoice['id']), firm_id, "overdue")
        
        # Send overdue reminder
        client = repo.client_by_id(sb, UUID(invoice['client_id']), firm_id)
        if client and client.get('contact_email'):
            # Send overdue reminder email
            pass
        
        # Escalate to partner if very overdue (30+ days)
        if days_overdue >= 30:
            # Notify partner
            pass
        
        return {"status": "triggered", "escalated": days_overdue >= 30}
    
    # ========================================================================
    # SCHEDULED JOBS
    # ========================================================================
    
    def run_daily_workflow_checks(self, sb: Client, firm_id: UUID):
        """Run daily workflow checks (called by scheduler)"""
        
        today = date.today()
        results = {
            "assignments_overdue_checked": 0,
            "compliance_reminders_sent": 0,
            "pbc_reminders_sent": 0,
            "invoices_overdue_checked": 0,
        }
        
        # Check overdue assignments
        assignments = repo.list_assignments_filtered(sb, firm_id, status="in_progress")
        for assignment in assignments:
            if assignment.get('due_date'):
                due_date = datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
                if due_date < today:
                    self.trigger_assignment_overdue(sb, firm_id, assignment)
                    results['assignments_overdue_checked'] += 1
        
        # Check upcoming compliance deadlines
        compliance_items = repo.list_compliance_requirements(sb, firm_id, status="pending")
        for item in compliance_items:
            if item.get('due_date'):
                due_date = datetime.strptime(item['due_date'], '%Y-%m-%d').date()
                days_until = (due_date - today).days
                
                # Send reminders at 7, 3, and 1 day before due
                if days_until in [7, 3, 1]:
                    self.trigger_compliance_due_soon(sb, firm_id, item, days_until)
                    results['compliance_reminders_sent'] += 1
        
        # Check PBC items due soon
        pbc_items_res = sb.table("pbc_checklists").select("*").eq("firm_id", str(firm_id)).eq("status", "pending").execute()
        for pbc in (pbc_items_res.data or []):
            if pbc.get('due_date'):
                due_date = datetime.strptime(pbc['due_date'], '%Y-%m-%d').date()
                days_until = (due_date - today).days
                
                if days_until in [5, 2]:
                    self.trigger_pbc_due_soon(sb, firm_id, pbc, days_until)
                    results['pbc_reminders_sent'] += 1
        
        # Check overdue invoices
        invoices_res = sb.table("invoices").select("*").eq("firm_id", str(firm_id)).in_("status", ["sent", "viewed"]).execute()
        for invoice in (invoices_res.data or []):
            if invoice.get('due_date'):
                due_date = datetime.strptime(invoice['due_date'], '%Y-%m-%d').date()
                if due_date < today:
                    days_overdue = (today - due_date).days
                    self.trigger_invoice_overdue(sb, firm_id, invoice, days_overdue)
                    results['invoices_overdue_checked'] += 1
        
        return results


# Singleton instance
workflow_engine = WorkflowEngine()
