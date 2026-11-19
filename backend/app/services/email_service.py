"""
GNANOVA CA PRACTICE OS - Email Notification Service
Phase 4 Enhancement: Send email notifications for assignments, compliance, and audit
"""

import os
from typing import List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailService:
    """Email notification service"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@gnanova.com')
        self.from_name = 'GNANOVA CA Practice OS'
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        attachments: Optional[List[tuple]] = None
    ) -> bool:
        """Send email via SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Add attachments
            if attachments:
                for filename, file_data in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file_data)
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={filename}')
                    msg.attach(part)
            
            # Send email
            if self.smtp_user and self.smtp_password:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
                return True
            else:
                # Log email (development mode)
                print(f"[EMAIL] Would send to {to_email}: {subject}")
                return True
                
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email: {str(e)}")
            return False
    
    def _get_email_template(self, body_content: str) -> str:
        """Get HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #0B1D33; color: white; padding: 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header .subtitle {{ color: #C9A227; font-size: 14px; margin-top: 5px; }}
                .content {{ background-color: #f8f9fa; padding: 30px; }}
                .button {{ 
                    display: inline-block; 
                    background-color: #C9A227; 
                    color: white; 
                    padding: 12px 30px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>GNANOVA</h1>
                    <div class="subtitle">CA PRACTICE OS</div>
                </div>
                <div class="content">
                    {body_content}
                </div>
                <div class="footer">
                    <p>This is an automated notification from GNANOVA CA Practice OS.</p>
                    <p>&copy; {datetime.now().year} GNANOVA. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_assignment_notification(
        self,
        to_email: str,
        assignment_name: str,
        assignment_code: str,
        due_date: str,
        assigned_by: str,
        dashboard_link: str = None
    ) -> bool:
        """Send assignment notification"""
        
        body = f"""
        <h2>New Assignment</h2>
        <p>You have been assigned a new task:</p>
        <ul>
            <li><strong>Assignment:</strong> {assignment_name}</li>
            <li><strong>Code:</strong> {assignment_code}</li>
            <li><strong>Due Date:</strong> {due_date}</li>
            <li><strong>Assigned By:</strong> {assigned_by}</li>
        </ul>
        <p>Please review and start working on this assignment.</p>
        {f'<a href="{dashboard_link}" class="button">View Assignment</a>' if dashboard_link else ''}
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'New Assignment: {assignment_name}',
            html_body=html
        )
    
    def send_compliance_reminder(
        self,
        to_email: str,
        compliance_name: str,
        due_date: str,
        days_until_due: int,
        client_name: str
    ) -> bool:
        """Send compliance deadline reminder"""
        
        urgency = 'URGENT' if days_until_due <= 3 else 'REMINDER'
        
        body = f"""
        <h2 style="color: {'#dc3545' if days_until_due <= 3 else '#C9A227'};">{urgency}: Compliance Deadline Approaching</h2>
        <p>A compliance deadline is approaching:</p>
        <ul>
            <li><strong>Compliance:</strong> {compliance_name}</li>
            <li><strong>Client:</strong> {client_name}</li>
            <li><strong>Due Date:</strong> {due_date}</li>
            <li><strong>Days Until Due:</strong> {days_until_due}</li>
        </ul>
        <p>Please ensure timely completion to avoid penalties.</p>
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'{urgency}: {compliance_name} due in {days_until_due} days',
            html_body=html
        )
    
    def send_review_notification(
        self,
        to_email: str,
        assignment_name: str,
        submitted_by: str,
        review_level: str
    ) -> bool:
        """Send review request notification"""
        
        body = f"""
        <h2>Review Request</h2>
        <p>An assignment has been submitted for your review:</p>
        <ul>
            <li><strong>Assignment:</strong> {assignment_name}</li>
            <li><strong>Submitted By:</strong> {submitted_by}</li>
            <li><strong>Review Level:</strong> {review_level}</li>
        </ul>
        <p>Please review and provide your feedback.</p>
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'Review Request: {assignment_name}',
            html_body=html
        )
    
    def send_audit_engagement_notification(
        self,
        to_email: str,
        engagement_name: str,
        engagement_code: str,
        role: str,
        start_date: str
    ) -> bool:
        """Send audit engagement notification"""
        
        body = f"""
        <h2>Audit Engagement Assignment</h2>
        <p>You have been assigned to an audit engagement:</p>
        <ul>
            <li><strong>Engagement:</strong> {engagement_name}</li>
            <li><strong>Code:</strong> {engagement_code}</li>
            <li><strong>Your Role:</strong> {role}</li>
            <li><strong>Start Date:</strong> {start_date}</li>
        </ul>
        <p>Please review the engagement details and begin planning.</p>
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'Audit Engagement: {engagement_name}',
            html_body=html
        )
    
    def send_pbc_request(
        self,
        to_email: str,
        client_name: str,
        pbc_items: List[str],
        due_date: str,
        engagement_name: str
    ) -> bool:
        """Send PBC (Provided By Client) request"""
        
        items_html = ''.join([f'<li>{item}</li>' for item in pbc_items])
        
        body = f"""
        <h2>Document Request - Audit Engagement</h2>
        <p>Dear {client_name},</p>
        <p>As part of our audit engagement <strong>{engagement_name}</strong>, we require the following documents:</p>
        <ul>
            {items_html}
        </ul>
        <p><strong>Due Date:</strong> {due_date}</p>
        <p>Please provide these documents at your earliest convenience.</p>
        <p>Thank you for your cooperation.</p>
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'Document Request: {engagement_name}',
            html_body=html
        )
    
    def send_invoice_notification(
        self,
        to_email: str,
        client_name: str,
        invoice_number: str,
        invoice_amount: float,
        due_date: str,
        pdf_attachment: Optional[bytes] = None
    ) -> bool:
        """Send invoice notification with PDF"""
        
        body = f"""
        <h2>New Invoice</h2>
        <p>Dear {client_name},</p>
        <p>Please find your invoice details below:</p>
        <ul>
            <li><strong>Invoice Number:</strong> {invoice_number}</li>
            <li><strong>Amount:</strong> ₹ {invoice_amount:,.2f}</li>
            <li><strong>Due Date:</strong> {due_date}</li>
        </ul>
        <p>The invoice is attached to this email for your reference.</p>
        <p>Thank you for your business.</p>
        """
        
        html = self._get_email_template(body)
        
        attachments = []
        if pdf_attachment:
            attachments.append((f'{invoice_number}.pdf', pdf_attachment))
        
        return self._send_email(
            to_email=to_email,
            subject=f'Invoice {invoice_number}',
            html_body=html,
            attachments=attachments if attachments else None
        )
    
    def send_welcome_email(
        self,
        to_email: str,
        user_name: str,
        firm_name: str,
        role: str,
        login_link: str = None
    ) -> bool:
        """Send welcome email to new user"""
        
        body = f"""
        <h2>Welcome to GNANOVA CA Practice OS!</h2>
        <p>Dear {user_name},</p>
        <p>Welcome to <strong>{firm_name}</strong>!</p>
        <p>Your account has been created with the role of <strong>{role}</strong>.</p>
        <p>You can now access the platform and start managing your assignments, clients, and compliance tasks.</p>
        {f'<a href="{login_link}" class="button">Login to Dashboard</a>' if login_link else ''}
        <p>If you have any questions, please contact your firm administrator.</p>
        """
        
        html = self._get_email_template(body)
        
        return self._send_email(
            to_email=to_email,
            subject=f'Welcome to {firm_name} - GNANOVA CA Practice OS',
            html_body=html
        )


# Singleton instance
email_service = EmailService()
