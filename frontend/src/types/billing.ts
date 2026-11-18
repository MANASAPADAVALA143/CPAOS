/**
 * Billing and invoicing types for GNANOVA CA Practice OS - Phase 3
 */

export type InvoiceStatus = 'draft' | 'sent' | 'viewed' | 'partially_paid' | 'paid' | 'overdue' | 'cancelled'

export type PaymentMethod = 'bank_transfer' | 'cheque' | 'cash' | 'card' | 'upi' | 'online'

export interface Invoice {
  id: string
  firm_id: string
  client_id: string
  invoice_number: string
  invoice_date: string
  due_date: string
  currency: string
  subtotal: number
  discount_amount: number
  tax_amount: number
  total_amount: number
  paid_amount: number
  balance_due: number
  status: InvoiceStatus
  sent_at?: string
  paid_at?: string
  description?: string
  created_at: string
  
  // Joined/calculated fields
  client_name?: string
  days_overdue?: number
  is_overdue?: boolean
}

export interface InvoiceItem {
  id: string
  description: string
  quantity: number
  unit: string
  rate: number
  amount: number
  tax_amount: number
  total_amount: number
}

export interface Payment {
  id: string
  invoice_id?: string
  payment_date: string
  amount: number
  payment_method: PaymentMethod
  payment_reference?: string
  status: string
  notes?: string
  created_at: string
  
  // Joined fields
  client_name?: string
  invoice_number?: string
}

export interface TimesheetEntry {
  id: string
  entry_date: string
  duration_hours: number
  client_id?: string
  assignment_id?: string
  activity_type?: string
  description?: string
  is_billable: boolean
  billable_amount?: number
  is_invoiced: boolean
  created_at: string
  
  // Joined fields
  client_name?: string
  assignment_name?: string
  user_name?: string
}

export interface BillingDashboardStats {
  total_revenue: number
  revenue_this_month: number
  outstanding_amount: number
  overdue_amount: number
  invoices_sent: number
  invoices_paid: number
  invoices_overdue: number
  unbilled_hours: number
  unbilled_amount: number
}

export interface ReceivablesAgeing {
  client_id: string
  client_name: string
  total_outstanding: number
  current: number  // 0-30 days
  days_31_60: number
  days_61_90: number
  days_over_90: number
}
