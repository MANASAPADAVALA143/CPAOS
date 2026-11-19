"""
GNANOVA CA PRACTICE OS - Auto-Assignment Rules Engine
Intelligent assignment distribution based on workload, skills, and rules
"""

from typing import Optional, List, Dict
from uuid import UUID
from supabase import Client
from collections import Counter

from app.db import repo


class AssignmentRulesEngine:
    """Auto-assignment engine with load balancing and skill matching"""
    
    def __init__(self):
        # Service category to designation mapping
        self.service_category_skills = {
            "income_tax": ["Tax Manager", "Tax Senior", "Tax Associate"],
            "gst": ["GST Specialist", "Tax Manager", "Tax Senior"],
            "audit": ["Audit Manager", "Audit Senior", "Audit Associate"],
            "accounting": ["Accounts Manager", "Accounts Senior", "Accounts Associate"],
            "company_law": ["Company Secretary", "Legal Advisor", "Manager"],
            "payroll": ["Payroll Specialist", "HR Manager", "Accounts Manager"],
            "other": ["Manager", "Senior", "Associate"],
        }
    
    def get_staff_workload(self, sb: Client, firm_id: UUID, user_id: UUID) -> int:
        """Get current workload (number of active assignments) for a user"""
        
        assignments = repo.list_assignments_filtered(
            sb,
            firm_id,
            assigned_to=user_id,
            status=None,
        )
        
        # Count only active assignments
        active_statuses = ["created", "assigned", "in_progress", "submitted", "manager_review", "partner_review"]
        active_count = sum(1 for a in assignments if a.get('status') in active_statuses)
        
        return active_count
    
    def get_staff_by_skills(
        self,
        sb: Client,
        firm_id: UUID,
        service_category: str,
        required_role: Optional[str] = None,
    ) -> List[dict]:
        """Get staff members who have skills for the service category"""
        
        # Get all active staff
        all_staff = repo.list_firm_users(sb, firm_id)
        
        # Filter by role if specified
        if required_role:
            all_staff = [s for s in all_staff if s.get('role') == required_role]
        
        # Get preferred designations for this service category
        preferred_designations = self.service_category_skills.get(
            service_category,
            self.service_category_skills["other"]
        )
        
        # Score and filter staff
        scored_staff = []
        for staff in all_staff:
            designation = staff.get('designation', '')
            
            # Check if designation matches any preferred designation
            score = 0
            for i, pref in enumerate(preferred_designations):
                if pref.lower() in designation.lower():
                    score = len(preferred_designations) - i  # Higher score for better match
                    break
            
            if score > 0 or not preferred_designations:
                scored_staff.append({
                    "staff": staff,
                    "score": score,
                    "workload": self.get_staff_workload(sb, firm_id, UUID(staff['id'])),
                })
        
        # Sort by score (desc) then workload (asc)
        scored_staff.sort(key=lambda x: (-x['score'], x['workload']))
        
        return [s['staff'] for s in scored_staff]
    
    def auto_assign_staff(
        self,
        sb: Client,
        firm_id: UUID,
        service_category: str,
        priority: str = "medium",
        client_id: Optional[UUID] = None,
    ) -> Optional[dict]:
        """Automatically assign staff member based on rules"""
        
        # Get suitable staff
        suitable_staff = self.get_staff_by_skills(
            sb,
            firm_id,
            service_category,
            required_role="staff",
        )
        
        if not suitable_staff:
            return None
        
        # Apply load balancing - select staff with lowest workload
        staff_with_workload = []
        for staff in suitable_staff[:5]:  # Consider top 5 skilled staff
            workload = self.get_staff_workload(sb, firm_id, UUID(staff['id']))
            staff_with_workload.append({
                "staff": staff,
                "workload": workload,
            })
        
        # Sort by workload
        staff_with_workload.sort(key=lambda x: x['workload'])
        
        # Return staff with lowest workload
        selected = staff_with_workload[0]['staff']
        
        return {
            "assigned_to": selected['id'],
            "assigned_to_name": selected.get('full_name', 'Staff'),
            "workload": staff_with_workload[0]['workload'],
            "reason": "Auto-assigned based on skills and workload",
        }
    
    def auto_assign_reviewer(
        self,
        sb: Client,
        firm_id: UUID,
        service_category: str,
        review_level: str,  # "manager" or "partner"
    ) -> Optional[dict]:
        """Automatically assign reviewer (manager or partner)"""
        
        required_role = review_level  # "manager" or "partner"
        
        # Get suitable reviewers
        suitable_reviewers = self.get_staff_by_skills(
            sb,
            firm_id,
            service_category,
            required_role=required_role,
        )
        
        if not suitable_reviewers:
            return None
        
        # Get review workload (pending reviews)
        reviewer_workload = []
        for reviewer in suitable_reviewers:
            # Count pending reviews
            reviews = repo.get_pending_reviews(sb, UUID(reviewer['id']), firm_id, review_level)
            reviewer_workload.append({
                "reviewer": reviewer,
                "pending_reviews": len(reviews),
            })
        
        # Sort by pending reviews (ascending)
        reviewer_workload.sort(key=lambda x: x['pending_reviews'])
        
        # Return reviewer with fewest pending reviews
        selected = reviewer_workload[0]['reviewer']
        
        return {
            "reviewer_id": selected['id'],
            "reviewer_name": selected.get('full_name', 'Reviewer'),
            "pending_reviews": reviewer_workload[0]['pending_reviews'],
            "reason": f"Auto-assigned {review_level} with least pending reviews",
        }
    
    def auto_assign_audit_team(
        self,
        sb: Client,
        firm_id: UUID,
        engagement_type: str,
        client_size: str = "medium",  # small, medium, large
    ) -> dict:
        """Automatically assign audit engagement team"""
        
        team = {
            "engagement_partner": None,
            "audit_manager": None,
            "audit_senior": None,
            "team_members": [],
        }
        
        # Get all staff
        all_staff = repo.list_firm_users(sb, firm_id)
        
        # Assign partner (required for all engagements)
        partners = [s for s in all_staff if s.get('role') == 'partner']
        if partners:
            # Select partner with fewest active engagements
            partner_workloads = []
            for partner in partners:
                engagements = repo.list_audit_engagements(sb, firm_id)
                active_as_partner = sum(1 for e in engagements if e.get('engagement_partner') == partner['id'] and e.get('status') not in ['completed', 'archived'])
                partner_workloads.append((partner, active_as_partner))
            
            partner_workloads.sort(key=lambda x: x[1])
            team['engagement_partner'] = partner_workloads[0][0]['id']
        
        # Assign manager (required for medium and large engagements)
        if client_size in ["medium", "large"]:
            managers = [s for s in all_staff if s.get('role') == 'manager']
            if managers:
                manager_workloads = []
                for manager in managers:
                    engagements = repo.list_audit_engagements(sb, firm_id)
                    active_as_manager = sum(1 for e in engagements if e.get('audit_manager') == manager['id'] and e.get('status') not in ['completed', 'archived'])
                    manager_workloads.append((manager, active_as_manager))
                
                manager_workloads.sort(key=lambda x: x[1])
                team['audit_manager'] = manager_workloads[0][0]['id']
        
        # Assign senior (required for all engagements)
        seniors = [s for s in all_staff if 'senior' in s.get('designation', '').lower() or s.get('role') == 'staff']
        if seniors:
            # Select senior with lowest workload
            senior_workloads = []
            for senior in seniors:
                workload = self.get_staff_workload(sb, firm_id, UUID(senior['id']))
                senior_workloads.append((senior, workload))
            
            senior_workloads.sort(key=lambda x: x[1])
            team['audit_senior'] = senior_workloads[0][0]['id']
        
        # Assign team members (1 for small, 2 for medium, 3+ for large)
        team_size = {"small": 1, "medium": 2, "large": 3}.get(client_size, 2)
        staff_members = [s for s in all_staff if s.get('role') == 'staff' and s['id'] not in [team['engagement_partner'], team['audit_manager'], team['audit_senior']]]
        
        if staff_members:
            # Select staff with lowest workloads
            staff_workloads = []
            for staff in staff_members:
                workload = self.get_staff_workload(sb, firm_id, UUID(staff['id']))
                staff_workloads.append((staff, workload))
            
            staff_workloads.sort(key=lambda x: x[1])
            team['team_members'] = [s[0]['id'] for s in staff_workloads[:team_size]]
        
        return team
    
    def redistribute_workload(
        self,
        sb: Client,
        firm_id: UUID,
        overloaded_threshold: int = 10,
    ) -> dict:
        """Redistribute assignments when staff is overloaded"""
        
        results = {
            "redistributions": 0,
            "staff_affected": [],
        }
        
        # Get all staff with their workloads
        all_staff = repo.list_firm_users(sb, firm_id)
        staff_workloads = []
        
        for staff in all_staff:
            workload = self.get_staff_workload(sb, firm_id, UUID(staff['id']))
            staff_workloads.append({
                "staff": staff,
                "workload": workload,
            })
        
        # Find overloaded staff
        overloaded = [s for s in staff_workloads if s['workload'] >= overloaded_threshold]
        underloaded = [s for s in staff_workloads if s['workload'] < overloaded_threshold / 2]
        
        # Redistribute from overloaded to underloaded
        for overloaded_staff in overloaded:
            # Get their assignments
            assignments = repo.list_assignments_filtered(
                sb,
                firm_id,
                assigned_to=UUID(overloaded_staff['staff']['id']),
                status="created",  # Only reassign newly created assignments
            )
            
            # Reassign some to underloaded staff
            for assignment in assignments[:2]:  # Reassign up to 2
                if underloaded:
                    new_assignee = underloaded[0]
                    
                    # Update assignment
                    repo.update_assignment(
                        sb,
                        UUID(assignment['id']),
                        firm_id,
                        {"assigned_to": new_assignee['staff']['id']}
                    )
                    
                    results['redistributions'] += 1
                    if overloaded_staff['staff']['full_name'] not in results['staff_affected']:
                        results['staff_affected'].append(overloaded_staff['staff']['full_name'])
                    
                    # Update workload
                    new_assignee['workload'] += 1
                    overloaded_staff['workload'] -= 1
        
        return results


# Singleton instance
assignment_rules = AssignmentRulesEngine()
