/**
 * GNANOVA CA PRACTICE OS - Accounting Dashboard
 * Phase 4: Accounting workbench overview and statistics
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Calculator,
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertCircle,
  DollarSign,
  TrendingUp,
  FileBarChart,
} from 'lucide-react'
import { api } from '../lib/api'
import type { AccountingDashboardStats } from '../types/accounting'

export function AccountingDashboard() {
  const [stats, setStats] = useState<AccountingDashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  async function fetchDashboardData() {
    try {
      const res = await api.get('/api/accounting/dashboard/stats')
      setStats(res.data)
    } catch (error) {
      console.error('Failed to fetch accounting dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#C9A227] border-r-transparent"></div>
          <p className="mt-2 text-sm text-slate-600">Loading accounting dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Accounting Workbench</h1>
        <p className="mt-1 text-sm text-slate-600">
          Trial balance, ledger review, and reconciliations
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {/* Imports */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Imports</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{stats.total_imports}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.completed_imports} completed
                </p>
              </div>
              <div className="rounded-lg bg-blue-50 p-3">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Trial Balance */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">TB Entries</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.trial_balance_entries}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.unreconciled_accounts} unreconciled
                </p>
              </div>
              <div className="rounded-lg bg-green-50 p-3">
                <FileSpreadsheet className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* Bank Reco */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Bank Reco</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.bank_reconciliations}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.unreconciled_banks} unreconciled
                </p>
              </div>
              <div className="rounded-lg bg-yellow-50 p-3">
                <DollarSign className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>

          {/* GST + TDS */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">GST + TDS</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.gst_reconciliations + stats.tds_reconciliations}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.gst_variances + stats.tds_variances} variances
                </p>
              </div>
              <div className="rounded-lg bg-red-50 p-3">
                <AlertCircle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="mb-8 grid gap-6 md:grid-cols-3">
        <Link
          to="/accounting/trial-balance"
          className="rounded-lg border-2 border-dashed border-slate-300 bg-white p-6 transition-colors hover:border-[#C9A227] hover:bg-slate-50"
        >
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-blue-50 p-3">
              <FileSpreadsheet className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Trial Balance</h3>
              <p className="mt-1 text-sm text-slate-600">
                Import and review trial balance data
              </p>
            </div>
          </div>
        </Link>

        <Link
          to="/accounting/reconciliations"
          className="rounded-lg border-2 border-dashed border-slate-300 bg-white p-6 transition-colors hover:border-[#C9A227] hover:bg-slate-50"
        >
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-green-50 p-3">
              <CheckCircle2 className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Reconciliations</h3>
              <p className="mt-1 text-sm text-slate-600">
                Bank, GST, and TDS reconciliations
              </p>
            </div>
          </div>
        </Link>

        <Link
          to="/accounting/ledger"
          className="rounded-lg border-2 border-dashed border-slate-300 bg-white p-6 transition-colors hover:border-[#C9A227] hover:bg-slate-50"
        >
          <div className="flex items-start gap-4">
            <div className="rounded-lg bg-purple-50 p-3">
              <FileBarChart className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900">Ledger Review</h3>
              <p className="mt-1 text-sm text-slate-600">
                Review general ledger entries
              </p>
            </div>
          </div>
        </Link>
      </div>

      {/* Reconciliation Summary */}
      {stats && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* GST Reconciliation */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">GST Reconciliation</h2>
              <Link
                to="/accounting/reconciliations/gst"
                className="text-sm font-medium text-[#C9A227] hover:text-[#D4B03A]"
              >
                View all →
              </Link>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-slate-600">Total Reconciliations</span>
                </div>
                <span className="text-lg font-semibold text-slate-900">
                  {stats.gst_reconciliations}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                  <span className="text-sm text-slate-600">Variances Detected</span>
                </div>
                <span className="text-lg font-semibold text-slate-900">
                  {stats.gst_variances}
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-200">
                <div
                  className="h-2 rounded-full bg-green-500"
                  style={{
                    width: `${
                      stats.gst_reconciliations
                        ? ((stats.gst_reconciliations - stats.gst_variances) /
                            stats.gst_reconciliations) *
                          100
                        : 0
                    }%`,
                  }}
                />
              </div>
              <p className="text-xs text-slate-500">
                {stats.gst_reconciliations - stats.gst_variances} reconciled
              </p>
            </div>
          </div>

          {/* TDS Reconciliation */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">TDS Reconciliation</h2>
              <Link
                to="/accounting/reconciliations/tds"
                className="text-sm font-medium text-[#C9A227] hover:text-[#D4B03A]"
              >
                View all →
              </Link>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span className="text-sm text-slate-600">Total Reconciliations</span>
                </div>
                <span className="text-lg font-semibold text-slate-900">
                  {stats.tds_reconciliations}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600" />
                  <span className="text-sm text-slate-600">Variances Detected</span>
                </div>
                <span className="text-lg font-semibold text-slate-900">
                  {stats.tds_variances}
                </span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-200">
                <div
                  className="h-2 rounded-full bg-green-500"
                  style={{
                    width: `${
                      stats.tds_reconciliations
                        ? ((stats.tds_reconciliations - stats.tds_variances) /
                            stats.tds_reconciliations) *
                          100
                        : 0
                    }%`,
                  }}
                />
              </div>
              <p className="text-xs text-slate-500">
                {stats.tds_reconciliations - stats.tds_variances} reconciled
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
