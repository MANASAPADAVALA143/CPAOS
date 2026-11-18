import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { DollarSign, FileText, AlertTriangle, TrendingUp, Clock, CheckCircle2 } from 'lucide-react'
import api from '../lib/api'
import type { BillingDashboardStats, Invoice, ReceivablesAgeing } from '../types/billing'

export default function BillingDashboard() {
  const [stats, setStats] = useState<BillingDashboardStats | null>(null)
  const [recentInvoices, setRecentInvoices] = useState<Invoice[]>([])
  const [ageing, setAgeing] = useState<ReceivablesAgeing[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void loadDashboard()
  }, [])

  async function loadDashboard() {
    try {
      setLoading(true)
      const [statsRes, invoicesRes, ageingRes] = await Promise.all([
        api.get('/api/billing/dashboard'),
        api.get('/api/billing/invoices', { params: { limit: 10 } }),
        api.get('/api/billing/receivables-ageing'),
      ])
      setStats(statsRes.data)
      setRecentInvoices(invoicesRes.data)
      setAgeing(ageingRes.data.slice(0, 10))
    } catch (error) {
      console.error('Failed to load billing dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    }).format(amount)
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: 'bg-slate-500/15 text-slate-300',
      sent: 'bg-blue-500/15 text-blue-300',
      viewed: 'bg-indigo-500/15 text-indigo-300',
      partially_paid: 'bg-amber-500/15 text-amber-300',
      paid: 'bg-emerald-500/15 text-emerald-300',
      overdue: 'bg-red-500/15 text-red-400',
      cancelled: 'bg-gray-500/15 text-gray-400',
    }
    return (
      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${styles[status] || styles.draft}`}>
        {status.replace(/_/g, ' ')}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading billing dashboard...</div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Failed to load dashboard</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Billing & Invoicing</h1>
          <p className="text-sm text-slate-400 mt-1">Manage invoices, payments, and revenue</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Revenue</p>
                <p className="text-3xl font-bold text-white mt-1">{formatCurrency(stats.total_revenue)}</p>
                <p className="text-xs text-slate-400 mt-1">All time</p>
              </div>
              <div className="rounded-full bg-emerald-500/10 p-3">
                <DollarSign className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">This Month</p>
                <p className="text-3xl font-bold text-blue-400 mt-1">{formatCurrency(stats.revenue_this_month)}</p>
                <p className="text-xs text-slate-400 mt-1">Revenue</p>
              </div>
              <div className="rounded-full bg-blue-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-amber-500/20 bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Outstanding</p>
                <p className="text-3xl font-bold text-amber-400 mt-1">{formatCurrency(stats.outstanding_amount)}</p>
                <p className="text-xs text-slate-400 mt-1">Receivables</p>
              </div>
              <div className="rounded-full bg-amber-500/10 p-3">
                <FileText className="h-6 w-6 text-amber-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-red-500/20 bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Overdue</p>
                <p className="text-3xl font-bold text-red-400 mt-1">{formatCurrency(stats.overdue_amount)}</p>
                <p className="text-xs text-red-400 mt-1">{stats.invoices_overdue} invoices</p>
              </div>
              <div className="rounded-full bg-red-500/10 p-3">
                <AlertTriangle className="h-6 w-6 text-red-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Invoices Sent</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.invoices_sent}</p>
              </div>
              <div className="rounded-full bg-indigo-500/10 p-3">
                <FileText className="h-6 w-6 text-indigo-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Invoices Paid</p>
                <p className="text-3xl font-bold text-emerald-400 mt-1">{stats.invoices_paid}</p>
              </div>
              <div className="rounded-full bg-emerald-500/10 p-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Unbilled Hours</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.unbilled_hours.toFixed(1)}</p>
                <p className="text-xs text-slate-400 mt-1">{formatCurrency(stats.unbilled_amount)}</p>
              </div>
              <div className="rounded-full bg-purple-500/10 p-3">
                <Clock className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Collection Rate</p>
                <p className="text-3xl font-bold text-white mt-1">
                  {stats.total_revenue > 0 ? ((stats.invoices_paid / (stats.invoices_sent + stats.invoices_paid)) * 100).toFixed(0) : 0}%
                </p>
              </div>
              <div className="rounded-full bg-teal-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-teal-400" />
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Recent Invoices */}
          <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-white">Recent Invoices</h2>
            </div>
            <div className="divide-y divide-border">
              {recentInvoices.length === 0 ? (
                <div className="px-6 py-8 text-center text-sm text-slate-500">
                  No invoices yet
                </div>
              ) : (
                recentInvoices.map((invoice) => (
                  <div key={invoice.id} className="px-6 py-4 hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-white">{invoice.invoice_number}</p>
                        <p className="text-sm text-slate-400">{invoice.client_name}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-medium text-white">{formatCurrency(invoice.total_amount)}</p>
                        {getStatusBadge(invoice.status)}
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                      <span>Due: {new Date(invoice.due_date).toLocaleDateString()}</span>
                      {invoice.is_overdue && (
                        <span className="text-red-400">{invoice.days_overdue} days overdue</span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Receivables Ageing */}
          <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-white">Receivables Ageing</h2>
            </div>
            <div className="divide-y divide-border max-h-96 overflow-y-auto">
              {ageing.length === 0 ? (
                <div className="px-6 py-8 text-center text-sm text-slate-500">
                  No outstanding receivables
                </div>
              ) : (
                ageing.map((client) => (
                  <div key={client.client_id} className="px-6 py-4">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-medium text-white">{client.client_name}</p>
                      <p className="font-medium text-white">{formatCurrency(client.total_outstanding)}</p>
                    </div>
                    <div className="grid grid-cols-4 gap-2 text-xs">
                      <div>
                        <p className="text-slate-500">0-30</p>
                        <p className="text-slate-300">{formatCurrency(client.current)}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">31-60</p>
                        <p className="text-amber-400">{formatCurrency(client.days_31_60)}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">61-90</p>
                        <p className="text-orange-400">{formatCurrency(client.days_61_90)}</p>
                      </div>
                      <div>
                        <p className="text-slate-500">90+</p>
                        <p className="text-red-400">{formatCurrency(client.days_over_90)}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
