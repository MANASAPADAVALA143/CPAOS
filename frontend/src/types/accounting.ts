/**
 * GNANOVA CA PRACTICE OS - Accounting Types
 * Phase 4: Trial balance, ledger, reconciliations, imports
 */

export type ImportType = 
  | 'trial_balance'
  | 'ledger'
  | 'bank_statement'
  | 'gst'
  | 'tds';

export type AccountGroup = 
  | 'assets'
  | 'liabilities'
  | 'equity'
  | 'income'
  | 'expenses';

export interface AccountingImport {
  id: string;
  firm_id: string;
  client_id: string;
  engagement_id?: string;
  
  import_type: ImportType;
  file_name: string;
  file_size?: number;
  
  period_start?: string;
  period_end?: string;
  
  status: string;
  rows_imported: number;
  rows_failed: number;
  
  error_log?: string;
  
  imported_by?: string;
  imported_at?: string;
  created_at: string;
}

export interface TrialBalanceEntry {
  id: string;
  firm_id: string;
  client_id: string;
  import_id?: string;
  
  account_code: string;
  account_name: string;
  account_group?: AccountGroup;
  account_type?: string;
  
  period_date: string;
  
  opening_balance: number;
  debit_amount: number;
  credit_amount: number;
  closing_balance: number;
  
  is_reconciled: boolean;
  has_variance: boolean;
  
  notes?: string;
  created_at: string;
}

export interface LedgerEntry {
  id: string;
  firm_id: string;
  client_id: string;
  import_id?: string;
  
  entry_date: string;
  voucher_number?: string;
  voucher_type?: string;
  
  account_code: string;
  account_name?: string;
  
  debit_amount: number;
  credit_amount: number;
  
  narration?: string;
  reference?: string;
  
  created_at: string;
}

export interface BankReconciliation {
  id: string;
  firm_id: string;
  client_id: string;
  
  bank_name: string;
  account_number: string;
  
  reconciliation_date: string;
  
  book_balance: number;
  bank_balance: number;
  
  cheques_issued_not_presented: number;
  deposits_not_cleared: number;
  bank_charges: number;
  interest_credited: number;
  other_adjustments: number;
  
  adjusted_book_balance?: number;
  adjusted_bank_balance?: number;
  difference?: number;
  
  is_reconciled: boolean;
  
  notes?: string;
  
  prepared_by?: string;
  reviewed_by?: string;
  
  created_at: string;
  updated_at: string;
}

export interface GSTReconciliation {
  id: string;
  firm_id: string;
  client_id: string;
  
  month: string;
  gstin?: string;
  
  books_taxable_sales: number;
  books_cgst: number;
  books_sgst: number;
  books_igst: number;
  books_total_gst: number;
  
  gstr1_taxable_sales: number;
  gstr1_cgst: number;
  gstr1_sgst: number;
  gstr1_igst: number;
  gstr1_total_gst: number;
  
  gstr3b_taxable_sales: number;
  gstr3b_cgst: number;
  gstr3b_sgst: number;
  gstr3b_igst: number;
  gstr3b_total_gst: number;
  
  variance_taxable?: number;
  variance_gst?: number;
  
  is_reconciled: boolean;
  
  notes?: string;
  
  prepared_by?: string;
  created_at: string;
  updated_at: string;
}

export interface TDSReconciliation {
  id: string;
  firm_id: string;
  client_id: string;
  
  quarter: string;
  tan?: string;
  
  books_tds_deducted: number;
  books_tds_deposited: number;
  
  form26as_tds: number;
  
  tds_return_amount: number;
  
  variance_amount?: number;
  
  is_reconciled: boolean;
  
  notes?: string;
  
  prepared_by?: string;
  created_at: string;
  updated_at: string;
}

export interface AccountingDashboardStats {
  total_imports: number;
  pending_imports: number;
  completed_imports: number;
  
  trial_balance_entries: number;
  unreconciled_accounts: number;
  
  bank_reconciliations: number;
  unreconciled_banks: number;
  
  gst_reconciliations: number;
  gst_variances: number;
  
  tds_reconciliations: number;
  tds_variances: number;
  
  total_variance_amount: number;
}

// Request payloads
export interface CreateBankReconciliationPayload {
  client_id: string;
  bank_name: string;
  account_number: string;
  reconciliation_date: string;
  book_balance: number;
  bank_balance: number;
  cheques_issued_not_presented?: number;
  deposits_not_cleared?: number;
  bank_charges?: number;
  interest_credited?: number;
  other_adjustments?: number;
  notes?: string;
}

export interface CreateGSTReconciliationPayload {
  client_id: string;
  month: string;
  gstin?: string;
  books_taxable_sales: number;
  books_cgst: number;
  books_sgst: number;
  books_igst: number;
  books_total_gst: number;
  gstr1_taxable_sales: number;
  gstr1_cgst: number;
  gstr1_sgst: number;
  gstr1_igst: number;
  gstr1_total_gst: number;
  gstr3b_taxable_sales: number;
  gstr3b_cgst: number;
  gstr3b_sgst: number;
  gstr3b_igst: number;
  gstr3b_total_gst: number;
  notes?: string;
}

export interface CreateTDSReconciliationPayload {
  client_id: string;
  quarter: string;
  tan?: string;
  books_tds_deducted: number;
  books_tds_deposited: number;
  form26as_tds: number;
  tds_return_amount: number;
  notes?: string;
}
