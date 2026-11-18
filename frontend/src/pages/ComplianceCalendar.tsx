import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Plus, Filter, AlertTriangle, CheckCircle2, Clock } from 'lucide-react'
import api from '../lib/api'
import type { ComplianceRequirement, ComplianceTemplate } from '../types/compliance'
import { ComplianceStatusBadge } from '../components/ComplianceStatusBadge'
import { AssignmentPriorityBadge } from '../components/AssignmentPriorityBadge'

type FilterStatus = 'all' | 'pending' | 'in_progress' | 'overdue' | 'completed'

export default function ComplianceCalendar() {
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [showGenerateModal, setShowGenerateModal] = useState(false)

  const loadRequirements = useCallback(async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (statusFilter !== 'all') params.status = statusFilter
      if (categoryFilter !== 'all') params.service_category = categoryFilter
      
      const res = await api.get('/api/compliance/requirements', { params })
      setRequirements(res.data)
    } catch (error) {
      console.error('Failed to load compliance requirements:', error)
      setRequirements([])
    } finally {
      setLoading(false)
    }
  }, [statusFilter, categoryFilter])

  useEffect(() => {
    void loadRequirements()
  }, [loadRequirements])

  const pendingCount = requirements.filter(r => r.status === 'pending').length
  const overdueCount = requirements.filter(r => r.is_overdue).length
  const completedCount = requirements.filter(r => r.status === 'completed').length

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading compliance calendar...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Compliance Calendar</h1>
            <p className="text-sm text-slate-400 mt-1">Track statutory compliance deadlines</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowGenerateModal(true)}
              className="inline-flex items-center gap-2 rounded-lg border border-border bg-[#0B1D33] px-4 py-2 text-sm font-medium text-white hover:bg-white/5 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Generate Calendar
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="border-b border-border bg-[#0B1D33]/30 px-6 py-4">
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="rounded-lg bg-[#0B1D33] border border-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">Total Requirements</p>
                <p className="text-2xl font-bold text-white mt-1">{requirements.length}</p>
              </div>
              <Calendar className="h-8 w-8 text-slate-500" />
            </div>
          </div>
          
          <div className="rounded-lg bg-[#0B1D33] border border-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">Pending</p>
                <p className="text-2xl font-bold text-blue-400 mt-1">{pendingCount}</p>
              </div>
              <Clock className="h-8 w-8 text-blue-400" />
            </div>
          </div>

          <div className="rounded-lg bg-[#0B1D33] border border-red-500/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">Overdue</p>
                <p className="text-2xl font-bold text-red-400 mt-1">{overdueCount}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-400" />
            </div>
          </div>

          <div className="rounded-lg bg-[#0B1D33] border border-border p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500">Completed</p>
                <p className="text-2xl font-bold text-emerald-400 mt-1">{completedCount}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-emerald-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="border-b border-border bg-[#0B1D33]/30 px-6 py-4">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-slate-500" />
            <span className="text-sm text-slate-400">Filters:</span>
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
            className="rounded-lg border border-border bg-[#0B1D33] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="overdue">Overdue</option>
            <option value="completed">Completed</option>
          </select>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="rounded-lg border border-border bg-[#0B1D33] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="GST">GST</option>
            <option value="Income Tax">Income Tax</option>
            <option value="TDS">TDS</option>
            <option value="VAT">VAT</option>
            <option value="Corporate Tax">Corporate Tax</option>
            <option value="Audit">Audit</option>
            <option value="ESR">ESR</option>
          </select>
        </div>
      </div>

      {/* Requirements Table */}
      <div className="p-6">
        <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
          <table className="w-full">
            <thead className="border-b border-border bg-[#0B1D33]">
              <tr className="text-left">
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Compliance
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Client
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Category
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  FY
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Due Date
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Status
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Assigned To
                </th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {requirements.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center">
                    <div className="text-slate-500">
                      No compliance requirements found. Generate a compliance calendar to get started.
                    </div>
                  </td>
                </tr>
              ) : (
                requirements.map((req) => (
                  <tr key={req.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <Link
                          to={`/compliance/${req.id}`}
                          className="font-medium text-white hover:text-[#C9A227]"
                        >
                          {req.compliance_name}
                        </Link>
                        <div className="text-xs text-slate-500 mt-0.5">
                          {req.template_code || ''}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {req.client_name || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded border border-border px-2 py-0.5 text-xs text-slate-400">
                        {req.service_category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {req.financial_year}
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <div className={req.is_overdue ? 'text-red-400 font-medium' : 'text-slate-300'}>
                        {new Date(req.due_date).toLocaleDateString()}
                      </div>
                      {req.days_until_due !== undefined && (
                        <div className={`text-xs mt-0.5 ${
                          req.is_overdue
                            ? 'text-red-400'
                            : req.days_until_due <= 7
                              ? 'text-amber-400'
                              : 'text-slate-500'
                        }`}>
                          {req.is_overdue
                            ? `${Math.abs(req.days_until_due)} days overdue`
                            : req.days_until_due === 0
                              ? 'Due today'
                              : `${req.days_until_due} days left`}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <ComplianceStatusBadge status={req.status} />
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {req.assigned_to_name || '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/compliance/${req.id}`}
                        className="text-sm text-[#C9A227] hover:text-[#D4B03A]"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {requirements.length > 0 && (
          <div className="mt-4 text-sm text-slate-500">
            Showing {requirements.length} compliance requirement{requirements.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Generate Calendar Modal - Placeholder */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-xl border border-border bg-[#0B1D33] p-6">
            <h2 className="text-xl font-bold text-white mb-4">Generate Compliance Calendar</h2>
            <p className="text-sm text-slate-400 mb-4">
              This feature will auto-generate compliance requirements for a client based on applicable templates.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowGenerateModal(false)}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/5"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
