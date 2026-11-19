"""
GNANOVA CA PRACTICE OS - Excel Export Service
Phase 4 Enhancement: Export data to Excel files
"""

from typing import List
from datetime import datetime
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter


class ExcelExporter:
    """Export data to Excel files"""
    
    def __init__(self):
        # GNANOVA brand colors
        self.header_fill = PatternFill(start_color="C9A227", end_color="C9A227", fill_type="solid")
        self.header_font = Font(bold=True, color="FFFFFF", size=11)
        self.total_fill = PatternFill(start_color="0B1D33", end_color="0B1D33", fill_type="solid")
        self.total_font = Font(bold=True, color="FFFFFF", size=10)
        self.border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    def _style_header(self, ws, row=1):
        """Apply header styling to worksheet"""
        for cell in ws[row]:
            cell.fill = self.header_fill
            cell.font = self.header_font
            cell.border = self.border
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths"""
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
    
    def export_trial_balance(
        self,
        entries: List[dict],
        client_name: str,
        period_date: str
    ) -> BytesIO:
        """Export trial balance to Excel"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Trial Balance"
        
        # Title rows
        ws['A1'] = 'TRIAL BALANCE'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f'Client: {client_name}'
        ws['A3'] = f'As at: {period_date}'
        ws['A4'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Headers
        headers = ['Account Code', 'Account Name', 'Account Group', 'Opening Balance', 'Debit', 'Credit', 'Closing Balance', 'Reconciled']
        ws.append([])  # Empty row
        ws.append(headers)
        self._style_header(ws, row=6)
        
        # Data
        total_opening = 0
        total_debit = 0
        total_credit = 0
        total_closing = 0
        
        for entry in entries:
            opening = float(entry.get('opening_balance', 0))
            debit = float(entry.get('debit_amount', 0))
            credit = float(entry.get('credit_amount', 0))
            closing = float(entry.get('closing_balance', 0))
            
            total_opening += opening
            total_debit += debit
            total_credit += credit
            total_closing += closing
            
            ws.append([
                entry.get('account_code', ''),
                entry.get('account_name', ''),
                entry.get('account_group', ''),
                opening,
                debit,
                credit,
                closing,
                'Yes' if entry.get('is_reconciled') else 'No'
            ])
        
        # Totals row
        total_row = ['', 'TOTAL', '', total_opening, total_debit, total_credit, total_closing, '']
        ws.append(total_row)
        
        # Style totals
        last_row = ws.max_row
        for cell in ws[last_row]:
            cell.fill = self.total_fill
            cell.font = self.total_font
            cell.border = self.border
        
        # Number formatting
        for row in ws.iter_rows(min_row=7, max_row=ws.max_row, min_col=4, max_col=7):
            for cell in row:
                cell.number_format = '₹#,##0.00'
                cell.border = self.border
        
        self._auto_adjust_columns(ws)
        
        # Save to buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def export_ledger(
        self,
        entries: List[dict],
        client_name: str,
        account_code: str = None,
        start_date: str = None,
        end_date: str = None
    ) -> BytesIO:
        """Export ledger entries to Excel"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Ledger"
        
        # Title
        ws['A1'] = 'GENERAL LEDGER'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f'Client: {client_name}'
        if account_code:
            ws['A3'] = f'Account: {account_code}'
        if start_date and end_date:
            ws['A4'] = f'Period: {start_date} to {end_date}'
        ws[f'A{5 if account_code or (start_date and end_date) else 4}'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Headers
        headers = ['Date', 'Voucher #', 'Voucher Type', 'Account Code', 'Account Name', 'Debit', 'Credit', 'Narration']
        ws.append([])
        ws.append(headers)
        header_row = ws.max_row
        self._style_header(ws, row=header_row)
        
        # Data
        total_debit = 0
        total_credit = 0
        
        for entry in entries:
            debit = float(entry.get('debit_amount', 0))
            credit = float(entry.get('credit_amount', 0))
            
            total_debit += debit
            total_credit += credit
            
            ws.append([
                entry.get('entry_date', ''),
                entry.get('voucher_number', ''),
                entry.get('voucher_type', ''),
                entry.get('account_code', ''),
                entry.get('account_name', ''),
                debit if debit > 0 else '',
                credit if credit > 0 else '',
                entry.get('narration', ''),
            ])
        
        # Totals
        ws.append(['', '', '', '', 'TOTAL', total_debit, total_credit, ''])
        last_row = ws.max_row
        for cell in ws[last_row]:
            cell.fill = self.total_fill
            cell.font = self.total_font
            cell.border = self.border
        
        # Number formatting
        for row in ws.iter_rows(min_row=header_row+1, max_row=ws.max_row, min_col=6, max_col=7):
            for cell in row:
                if cell.value:
                    cell.number_format = '₹#,##0.00'
                cell.border = self.border
        
        self._auto_adjust_columns(ws)
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def export_gst_reconciliation(
        self,
        reconciliations: List[dict],
        client_name: str
    ) -> BytesIO:
        """Export GST reconciliation to Excel"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "GST Reconciliation"
        
        # Title
        ws['A1'] = 'GST RECONCILIATION REPORT'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f'Client: {client_name}'
        ws['A3'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Headers
        headers = [
            'Month', 'GSTIN',
            'Books Sales', 'Books GST',
            'GSTR-1 Sales', 'GSTR-1 GST',
            'GSTR-3B Sales', 'GSTR-3B GST',
            'Variance (Sales)', 'Variance (GST)',
            'Reconciled'
        ]
        ws.append([])
        ws.append(headers)
        self._style_header(ws, row=5)
        
        # Data
        for reco in reconciliations:
            ws.append([
                reco.get('month', ''),
                reco.get('gstin', ''),
                float(reco.get('books_taxable_sales', 0)),
                float(reco.get('books_total_gst', 0)),
                float(reco.get('gstr1_taxable_sales', 0)),
                float(reco.get('gstr1_total_gst', 0)),
                float(reco.get('gstr3b_taxable_sales', 0)),
                float(reco.get('gstr3b_total_gst', 0)),
                float(reco.get('variance_taxable', 0)),
                float(reco.get('variance_gst', 0)),
                'Yes' if reco.get('is_reconciled') else 'No'
            ])
        
        # Number formatting
        for row in ws.iter_rows(min_row=6, max_row=ws.max_row, min_col=3, max_col=10):
            for cell in row:
                cell.number_format = '₹#,##0.00'
                cell.border = self.border
        
        # Conditional formatting for variances
        for row in range(6, ws.max_row + 1):
            variance_cell = ws.cell(row=row, column=10)  # Variance GST column
            if variance_cell.value and abs(float(variance_cell.value)) > 0.01:
                variance_cell.fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
        
        self._auto_adjust_columns(ws)
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
    
    def export_bank_reconciliation(
        self,
        reconciliations: List[dict],
        client_name: str
    ) -> BytesIO:
        """Export bank reconciliation to Excel"""
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Bank Reconciliation"
        
        # Title
        ws['A1'] = 'BANK RECONCILIATION REPORT'
        ws['A1'].font = Font(bold=True, size=14)
        ws['A2'] = f'Client: {client_name}'
        ws['A3'] = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Headers
        headers = [
            'Date', 'Bank Name', 'Account #',
            'Book Balance', 'Bank Balance',
            'Cheques Issued', 'Deposits Not Cleared',
            'Bank Charges', 'Interest',
            'Difference', 'Reconciled'
        ]
        ws.append([])
        ws.append(headers)
        self._style_header(ws, row=5)
        
        # Data
        for reco in reconciliations:
            ws.append([
                reco.get('reconciliation_date', ''),
                reco.get('bank_name', ''),
                reco.get('account_number', ''),
                float(reco.get('book_balance', 0)),
                float(reco.get('bank_balance', 0)),
                float(reco.get('cheques_issued_not_presented', 0)),
                float(reco.get('deposits_not_cleared', 0)),
                float(reco.get('bank_charges', 0)),
                float(reco.get('interest_credited', 0)),
                float(reco.get('difference', 0)),
                'Yes' if reco.get('is_reconciled') else 'No'
            ])
        
        # Number formatting
        for row in ws.iter_rows(min_row=6, max_row=ws.max_row, min_col=4, max_col=10):
            for cell in row:
                cell.number_format = '₹#,##0.00'
                cell.border = self.border
        
        # Highlight unreconciled
        for row in range(6, ws.max_row + 1):
            diff_cell = ws.cell(row=row, column=10)
            if diff_cell.value and abs(float(diff_cell.value)) > 0.01:
                diff_cell.fill = PatternFill(start_color="FFE6E6", end_color="FFE6E6", fill_type="solid")
        
        self._auto_adjust_columns(ws)
        
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer


# Singleton instance
excel_exporter = ExcelExporter()
