"""
GNANOVA CA PRACTICE OS - PDF Generation Service
Phase 4 Enhancement: Generate PDF reports for audit engagements and working papers
"""

from typing import Optional
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class PDFGenerator:
    """Generate PDF reports for audit and accounting"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0B1D33'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#C9A227'),
            spaceAfter=12,
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
        ))
    
    def generate_audit_engagement_report(
        self,
        engagement: dict,
        client: dict,
        firm: dict,
        working_papers: list[dict],
        pbc_items: list[dict],
        risk_assessments: list[dict],
    ) -> BytesIO:
        """Generate comprehensive audit engagement PDF report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Header
        story.append(Paragraph(firm.get('name', 'GNANOVA CA PRACTICE'), self.styles['CustomTitle']))
        story.append(Paragraph('AUDIT ENGAGEMENT REPORT', self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Engagement Details
        story.append(Paragraph('ENGAGEMENT DETAILS', self.styles['CustomSubtitle']))
        
        engagement_data = [
            ['Engagement Code:', engagement.get('engagement_code', 'N/A')],
            ['Engagement Name:', engagement.get('engagement_name', 'N/A')],
            ['Client:', client.get('name', 'N/A')],
            ['Engagement Type:', engagement.get('engagement_type', 'N/A').replace('_', ' ').title()],
            ['Financial Year:', engagement.get('financial_year', 'N/A')],
            ['Period:', f"{engagement.get('period_start', 'N/A')} to {engagement.get('period_end', 'N/A')}"],
            ['Status:', engagement.get('status', 'N/A').title()],
            ['Overall Risk Rating:', engagement.get('overall_risk_rating', 'Not Assessed').upper()],
            ['Materiality Amount:', f"₹ {engagement.get('materiality_amount', 0):,.2f}" if engagement.get('materiality_amount') else 'Not Set'],
        ]
        
        engagement_table = Table(engagement_data, colWidths=[2*inch, 4*inch])
        engagement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0B1D33')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#F8F9FA')),
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(engagement_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Assessments
        if risk_assessments:
            story.append(Paragraph('RISK ASSESSMENT SUMMARY', self.styles['CustomSubtitle']))
            
            risk_data = [['Risk Area', 'Risk Description', 'Overall Risk']]
            for risk in risk_assessments[:10]:  # Limit to 10
                risk_data.append([
                    risk.get('risk_area', 'N/A')[:30],
                    risk.get('risk_description', 'N/A')[:50],
                    risk.get('overall_risk', 'N/A').upper(),
                ])
            
            risk_table = Table(risk_data, colWidths=[1.8*inch, 2.7*inch, 1*inch])
            risk_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C9A227')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))
            story.append(risk_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Working Papers Summary
        if working_papers:
            story.append(Paragraph('WORKING PAPERS SUMMARY', self.styles['CustomSubtitle']))
            
            wp_data = [['Ref #', 'Title', 'Section', 'Status', 'Prepared By']]
            for wp in working_papers[:15]:  # Limit to 15
                wp_data.append([
                    wp.get('reference_number', 'N/A'),
                    wp.get('title', 'N/A')[:35],
                    wp.get('section', 'N/A')[:15],
                    wp.get('status', 'N/A').title(),
                    wp.get('prepared_by', 'N/A')[:15],
                ])
            
            wp_table = Table(wp_data, colWidths=[0.7*inch, 2*inch, 1*inch, 0.9*inch, 1*inch])
            wp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C9A227')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))
            story.append(wp_table)
            story.append(Spacer(1, 0.3*inch))
        
        # PBC Checklist Status
        if pbc_items:
            story.append(Paragraph('PBC CHECKLIST STATUS', self.styles['CustomSubtitle']))
            
            pbc_data = [['Item Name', 'Category', 'Status', 'Due Date']]
            for pbc in pbc_items[:12]:  # Limit to 12
                pbc_data.append([
                    pbc.get('item_name', 'N/A')[:35],
                    pbc.get('item_category', 'N/A')[:15],
                    pbc.get('status', 'N/A').title(),
                    pbc.get('due_date', 'N/A'),
                ])
            
            pbc_table = Table(pbc_data, colWidths=[2.2*inch, 1.3*inch, 1*inch, 1*inch])
            pbc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C9A227')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
            ]))
            story.append(pbc_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        story.append(Paragraph(
            'GNANOVA CA PRACTICE OS - Confidential Report',
            ParagraphStyle('Footer2', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_trial_balance_pdf(
        self,
        client: dict,
        firm: dict,
        entries: list[dict],
        period_date: str,
    ) -> BytesIO:
        """Generate trial balance PDF report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Header
        story.append(Paragraph(firm.get('name', 'GNANOVA CA PRACTICE'), self.styles['CustomTitle']))
        story.append(Paragraph('TRIAL BALANCE', self.styles['CustomTitle']))
        story.append(Paragraph(f'As at {period_date}', self.styles['CustomSubtitle']))
        story.append(Paragraph(f'Client: {client.get("name", "N/A")}', self.styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # Trial Balance Table
        tb_data = [['Account Code', 'Account Name', 'Debit', 'Credit']]
        total_debit = 0
        total_credit = 0
        
        for entry in entries:
            debit = float(entry.get('debit_amount', 0))
            credit = float(entry.get('credit_amount', 0))
            total_debit += debit
            total_credit += credit
            
            tb_data.append([
                entry.get('account_code', 'N/A'),
                entry.get('account_name', 'N/A')[:30],
                f"₹ {debit:,.2f}" if debit > 0 else '-',
                f"₹ {credit:,.2f}" if credit > 0 else '-',
            ])
        
        # Add totals row
        tb_data.append(['', 'TOTAL', f"₹ {total_debit:,.2f}", f"₹ {total_credit:,.2f}"])
        
        tb_table = Table(tb_data, colWidths=[1.2*inch, 2.5*inch, 1.3*inch, 1.3*inch])
        tb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C9A227')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#0B1D33')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        story.append(tb_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            f'Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
            ParagraphStyle('Footer', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer


# Singleton instance
pdf_generator = PDFGenerator()
