"""
Compliance management service for GNANOVA CA Practice OS
Handles compliance calendar generation, reminders, and escalations
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import Any

from supabase import Client

from app.db import repo
from app.db.dates import utc_now_iso


def calculate_due_date(
    template: dict[str, Any],
    period_start: date | None,
    period_end: date | None,
    financial_year: str,
) -> date:
    """
    Calculate due date based on compliance template rules
    
    Rules:
    - monthly: due_day_of_month of next month after period_end
    - quarterly: due_days_after_period_end after period_end
    - annual: due_month and due_day_of_month of the FY
    - event_based: provided manually
    """
    frequency = template["frequency"]
    
    if frequency == "monthly":
        # Due on specific day of next month
        if not period_end:
            raise ValueError("period_end required for monthly compliance")
        next_month = period_end + timedelta(days=31)
        due_day = template.get("due_day_of_month") or 20
        return date(next_month.year, next_month.month, min(due_day, 28))
    
    elif frequency == "quarterly":
        # Due N days after quarter end
        if not period_end:
            raise ValueError("period_end required for quarterly compliance")
        days_after = template.get("due_days_after_period_end") or 30
        return period_end + timedelta(days=days_after)
    
    elif frequency == "annual":
        # Due on specific month and day
        # Extract year from FY (e.g., "FY 2024-25" -> 2024 for first year, 2025 for second)
        fy_parts = financial_year.split("-")
        if len(fy_parts) == 2:
            # Get second year from FY
            year_str = fy_parts[1].strip()
            if len(year_str) == 2:
                year = 2000 + int(year_str)
            else:
                year = int(year_str)
        else:
            year = datetime.now().year
        
        due_month = template.get("due_month") or 7
        due_day = template.get("due_day_of_month") or 31
        return date(year, due_month, min(due_day, 28))
    
    else:
        # event_based or custom
        return date.today() + timedelta(days=30)


def generate_compliance_requirements_for_client(
    sb: Client,
    firm_id: uuid.UUID,
    client_id: uuid.UUID,
    financial_year: str,
    created_by: uuid.UUID,
) -> list[dict[str, Any]]:
    """
    Generate compliance requirements for a client based on applicable templates
    
    Steps:
    1. Get client details (country, entity_type)
    2. Find applicable templates
    3. Generate requirements for the FY
    4. Create requirement records
    """
    # Get client
    client = repo.client_by_id(sb, client_id, firm_id)
    if not client:
        raise ValueError("Client not found")
    
    country_code = "IN" if client["country"] == "India" else "AE" if client["country"] == "UAE" else "IN"
    entity_type = client.get("entity_type") or "company"
    
    # Get applicable templates
    templates = repo.list_compliance_templates(
        sb,
        firm_id=firm_id,
        country=country_code,
        is_active=True,
    )
    
    # Filter templates by entity type
    applicable_templates = [
        t for t in templates
        if not t.get("applies_to_entity_types") or entity_type.lower() in [e.lower() for e in t["applies_to_entity_types"]]
    ]
    
    requirements = []
    
    for template in applicable_templates:
        # Generate requirements based on frequency
        frequency = template["frequency"]
        
        if frequency == "monthly":
            # Generate 12 monthly requirements
            for month_num in range(1, 13):
                period_start_date = date(2024, month_num, 1)  # TODO: Use actual FY dates
                period_end_date = date(2024, month_num, 28)  # Simplified
                
                due = calculate_due_date(template, period_start_date, period_end_date, financial_year)
                
                req_data = {
                    "firm_id": str(firm_id),
                    "client_id": str(client_id),
                    "template_id": template["id"],
                    "compliance_name": f"{template['compliance_name']} - {month_num:02d}/{financial_year}",
                    "service_category": template["service_category"],
                    "financial_year": financial_year,
                    "period_start": period_start_date.isoformat(),
                    "period_end": period_end_date.isoformat(),
                    "due_date": due.isoformat(),
                    "status": "pending",
                    "priority": template.get("priority") or "medium",
                    "created_by": str(created_by),
                }
                
                req = repo.create_compliance_requirement(sb, req_data)
                if req:
                    requirements.append(req)
                    
                    # Create document requirements
                    if template.get("documents_required"):
                        create_document_requirements_for_compliance(
                            sb, firm_id, uuid.UUID(req["id"]), template["documents_required"]
                        )
        
        elif frequency == "quarterly":
            # Generate 4 quarterly requirements
            quarters = [
                ("Q1", date(2024, 4, 1), date(2024, 6, 30)),
                ("Q2", date(2024, 7, 1), date(2024, 9, 30)),
                ("Q3", date(2024, 10, 1), date(2024, 12, 31)),
                ("Q4", date(2025, 1, 1), date(2025, 3, 31)),
            ]
            
            for quarter_name, period_start_date, period_end_date in quarters:
                due = calculate_due_date(template, period_start_date, period_end_date, financial_year)
                
                req_data = {
                    "firm_id": str(firm_id),
                    "client_id": str(client_id),
                    "template_id": template["id"],
                    "compliance_name": f"{template['compliance_name']} - {quarter_name} {financial_year}",
                    "service_category": template["service_category"],
                    "financial_year": financial_year,
                    "period_start": period_start_date.isoformat(),
                    "period_end": period_end_date.isoformat(),
                    "due_date": due.isoformat(),
                    "status": "pending",
                    "priority": template.get("priority") or "medium",
                    "created_by": str(created_by),
                }
                
                req = repo.create_compliance_requirement(sb, req_data)
                if req:
                    requirements.append(req)
                    
                    if template.get("documents_required"):
                        create_document_requirements_for_compliance(
                            sb, firm_id, uuid.UUID(req["id"]), template["documents_required"]
                        )
        
        elif frequency == "annual":
            # Generate 1 annual requirement
            period_start_date = date(2024, 4, 1)  # FY start
            period_end_date = date(2025, 3, 31)  # FY end
            
            due = calculate_due_date(template, period_start_date, period_end_date, financial_year)
            
            req_data = {
                "firm_id": str(firm_id),
                "client_id": str(client_id),
                "template_id": template["id"],
                "compliance_name": f"{template['compliance_name']} - {financial_year}",
                "service_category": template["service_category"],
                "financial_year": financial_year,
                "period_start": period_start_date.isoformat(),
                "period_end": period_end_date.isoformat(),
                "due_date": due.isoformat(),
                "status": "pending",
                "priority": template.get("priority") or "medium",
                "created_by": str(created_by),
            }
            
            req = repo.create_compliance_requirement(sb, req_data)
            if req:
                requirements.append(req)
                
                if template.get("documents_required"):
                    create_document_requirements_for_compliance(
                        sb, firm_id, uuid.UUID(req["id"]), template["documents_required"]
                    )
    
    return requirements


def create_document_requirements_for_compliance(
    sb: Client,
    firm_id: uuid.UUID,
    requirement_id: uuid.UUID,
    document_types: list[str],
) -> list[dict[str, Any]]:
    """Create document requirements for a compliance requirement"""
    doc_reqs = []
    
    for doc_type in document_types:
        data = {
            "firm_id": str(firm_id),
            "requirement_id": str(requirement_id),
            "document_name": doc_type,
            "document_type": doc_type,
            "is_mandatory": True,
            "status": "pending",
        }
        
        doc_req = repo.create_document_requirement(sb, data)
        if doc_req:
            doc_reqs.append(doc_req)
    
    return doc_reqs


def generate_reminders_and_alerts(
    sb: Client,
    firm_id: uuid.UUID,
) -> list[dict[str, Any]]:
    """
    Generate alerts for upcoming and overdue compliance requirements
    
    Logic:
    - Check all pending compliance requirements
    - For each, check if reminders should be sent based on days_before_due
    - Create alerts if not already sent
    - Handle escalations for overdue items
    """
    today = date.today()
    alerts_created = []
    
    # Get all pending/in-progress requirements
    requirements = repo.list_compliance_requirements(
        sb,
        firm_id=firm_id,
        limit=1000,
    )
    
    for req in requirements:
        if req["status"] in ["completed", "not_applicable"]:
            continue
        
        due_date_str = req["due_date"]
        due_date_obj = datetime.fromisoformat(due_date_str.replace("Z", "+00:00")).date()
        days_until_due = (due_date_obj - today).days
        
        # Get reminders for this template
        template_id = req.get("template_id")
        reminders = []
        if template_id:
            reminders = repo.list_compliance_reminders(
                sb,
                firm_id=firm_id,
                template_id=uuid.UUID(template_id),
                is_active=True,
            )
        
        for reminder in reminders:
            days_before = reminder["days_before_due"]
            
            # Check if reminder should be sent
            # Negative days_before means overdue reminders
            if days_before >= 0:
                # Pre-due reminder
                if days_until_due == days_before:
                    # Send reminder
                    alert = create_alert_for_requirement(
                        sb,
                        firm_id,
                        req,
                        reminder,
                        alert_type="reminder",
                        severity="warning" if days_before <= 3 else "info",
                    )
                    if alert:
                        alerts_created.append(alert)
            else:
                # Overdue reminder
                if days_until_due < 0 and abs(days_until_due) == abs(days_before):
                    # Send overdue alert
                    alert = create_alert_for_requirement(
                        sb,
                        firm_id,
                        req,
                        reminder,
                        alert_type="overdue",
                        severity="critical",
                    )
                    if alert:
                        alerts_created.append(alert)
        
        # Auto-generate alerts for overdue without specific reminders
        if days_until_due < 0 and req["status"] != "overdue":
            # Update status to overdue
            repo.update_compliance_requirement(
                sb,
                uuid.UUID(req["id"]),
                {"status": "overdue"},
            )
            
            # Create overdue alert if no reminders exist
            if not reminders:
                alert = create_alert_for_requirement(
                    sb,
                    firm_id,
                    req,
                    None,
                    alert_type="overdue",
                    severity="critical",
                )
                if alert:
                    alerts_created.append(alert)
    
    return alerts_created


def create_alert_for_requirement(
    sb: Client,
    firm_id: uuid.UUID,
    requirement: dict[str, Any],
    reminder: dict[str, Any] | None,
    alert_type: str,
    severity: str,
) -> dict[str, Any] | None:
    """Create an alert for a compliance requirement"""
    # Determine recipient
    recipient_id = requirement.get("assigned_to")
    if not recipient_id:
        # Default to client manager or partner
        client_id = requirement["client_id"]
        client = repo.client_by_id(sb, uuid.UUID(client_id), firm_id)
        if client:
            recipient_id = client.get("manager_in_charge") or client.get("partner_in_charge")
    
    if not recipient_id:
        # No recipient, skip
        return None
    
    # Generate message
    compliance_name = requirement["compliance_name"]
    due_date = requirement["due_date"]
    client_name = requirement.get("clients", {}).get("company_name") or "Client"
    
    if alert_type == "overdue":
        message = f"⚠️ OVERDUE: {compliance_name} for {client_name} was due on {due_date}"
    elif alert_type == "reminder":
        message = f"📅 Reminder: {compliance_name} for {client_name} is due on {due_date}"
    else:
        message = f"{compliance_name} for {client_name} - {alert_type}"
    
    # Check if alert already sent recently (avoid duplicates)
    existing_alerts = repo.list_compliance_alerts(
        sb,
        firm_id=firm_id,
        recipient_id=uuid.UUID(recipient_id),
        limit=100,
    )
    
    # Check if same alert sent in last 24 hours
    cutoff = datetime.now() - timedelta(hours=24)
    for alert in existing_alerts:
        if (
            alert["requirement_id"] == requirement["id"]
            and alert["alert_type"] == alert_type
            and datetime.fromisoformat(alert["sent_at"].replace("Z", "+00:00")) > cutoff
        ):
            # Already sent, skip
            return None
    
    # Create alert
    alert_data = {
        "firm_id": str(firm_id),
        "requirement_id": requirement["id"],
        "reminder_id": reminder["id"] if reminder else None,
        "alert_type": alert_type,
        "severity": severity,
        "recipient_id": str(recipient_id),
        "message": message,
        "notification_sent": False,
    }
    
    return repo.create_compliance_alert(sb, alert_data)


def link_compliance_to_assignment(
    sb: Client,
    requirement_id: uuid.UUID,
    assignment_id: uuid.UUID,
) -> bool:
    """Link a compliance requirement to an assignment"""
    # Update requirement with assignment_id
    repo.update_compliance_requirement(
        sb,
        requirement_id,
        {"assignment_id": str(assignment_id)},
    )
    
    # Update assignment with compliance_requirement_id
    repo.update_assignment(
        sb,
        assignment_id,
        {"compliance_requirement_id": str(requirement_id)},
    )
    
    return True


def get_compliance_dashboard_stats(sb: Client, firm_id: uuid.UUID) -> dict[str, Any]:
    """Get compliance dashboard statistics"""
    today = date.today()
    week_from_now = today + timedelta(days=7)
    month_from_now = today + timedelta(days=30)
    
    # Counts by status
    total = repo.count_compliance_requirements(sb, firm_id)
    pending = repo.count_compliance_requirements(sb, firm_id, status="pending")
    in_progress = repo.count_compliance_requirements(sb, firm_id, status="in_progress")
    completed = repo.count_compliance_requirements(sb, firm_id, status="completed")
    overdue = repo.count_overdue_compliance(sb, firm_id, today.isoformat())
    due_this_week = repo.count_due_soon(sb, firm_id, today.isoformat(), week_from_now.isoformat())
    due_this_month = repo.count_due_soon(sb, firm_id, today.isoformat(), month_from_now.isoformat())
    
    # Alerts
    alerts = repo.list_compliance_alerts(sb, firm_id, limit=1000)
    total_alerts = len(alerts)
    unread_alerts = len([a for a in alerts if not a.get("read_at")])
    
    return {
        "total_requirements": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "due_this_week": due_this_week,
        "due_this_month": due_this_month,
        "total_alerts": total_alerts,
        "unread_alerts": unread_alerts,
    }
