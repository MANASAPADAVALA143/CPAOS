import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, AlertTriangle, CheckCircle2, Clock, TrendingUp } from 'lucide-react'
import api from '../lib/api'
import type { ComplianceDashboardStats } from '../types/compliance'
import { ComplianceStatusBadge } from '../components/ComplianceStatusBadge'

export default function ComplianceDashboard() {
  const [stats, setStats] = useState<ComplianceDashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void loadDashboard()
  }, [])

  async function loadDashboard() {
    try {
      setLoading(true)
      const res = await api.get('/api/compliance/dashboard')
      setStats(res.data)
    } catch (error) {
      console.error('Failed to load compliance dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading dashboard...</div>
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
          <h1 className="text-2xl font-bold text-white">Compliance Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Overview of statutory compliance status</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Requirements</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.total_requirements}</p>
              </div>
              <div className="rounded-full bg-blue-500/10 p-3">
                <Calendar className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <Link
            to="/compliance?status=overdue"
            className="rounded-xl border border-red-500/20 bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Overdue</p>
                <p className="text-3xl font-bold text-red-400 mt-1">{stats.overdue}</p>
                <p className="text-xs text-red-400 mt-1">Needs immediate attention</p>
              </div>
              <div className="rounded-full bg-red-500/10 p-3">
                <AlertTriangle className="h-6 w-6 text-red-400" />
              </div>
            </div>
          </Link>

          <Link
            to="/compliance?status=pending"
            className="rounded-xl border border-border bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Pending</p>
                <p className="text-3xl font-bold text-amber-400 mt-1">{stats.pending}</p>
                <p className="text-xs text-slate-400 mt-1">Awaiting action</p>
              </div>
              <div className="rounded-full bg-amber-500/10 p-3">
                <Clock className="h-6 w-6 text-amber-400" />
              </div>
            </div>
          </Link>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Completed</p>
                <p className="text-3xl font-bold text-emerald-400 mt-1">{stats.completed}</p>
                <p className="text-xs text-slate-400 mt-1">This period</p>
              </div>
              <div className="rounded-full bg-emerald-500/10 p-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Due This Week</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.due_this_week}</p>
              </div>
              <div className="rounded-full bg-purple-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Due This Month</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.due_this_month}</p>
              </div>
              <div className="rounded-full bg-indigo-500/10 p-3">
                <Calendar className="h-6 w-6 text-indigo-400" />
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">In Progress</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.in_progress}</p>
              </div>
              <div className="rounded-full bg-blue-500/10 p-3">
                <Clock className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          <Link
            to="/compliance/alerts"
            className="rounded-xl border border-border bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Unread Alerts</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.unread_alerts}</p>
                <p className="text-xs text-slate-400 mt-1">of {stats.total_alerts} total</p>
              </div>
              <div className="rounded-full bg-orange-500/10 p-3">
                <AlertTriangle className="h-6 w-6 text-orange-400" />
              </div>
            </div>
          </Link>
        </div>

        {/* Upcoming Deadlines */}
        {stats.upcoming_deadlines && stats.upcoming_deadlines.length > 0 && (
          <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-white">Upcoming Deadlines (Next 30 Days)</h2>
            </div>

            <div className="overflow-x-auto">
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
                      Due Date
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Days Left
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Status
                    </th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {stats.upcoming_deadlines.map((req) => (
                    <tr key={req.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3">
                        <Link
                          to={`/compliance/${req.id}`}
                          className="font-medium text-white hover:text-[#C9A227]"
                        >
                          {req.compliance_name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {req.client_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {new Date(req.due_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-sm ${
                          req.days_until_due && req.days_until_due <= 3
                            ? 'text-red-400 font-medium'
                            : req.days_until_due && req.days_until_due <= 7
                              ? 'text-amber-400'
                              : 'text-slate-300'
                        }`}>
                          {req.days_until_due} days
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <ComplianceStatusBadge status={req.status} />
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
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div className="flex justify-center">
          <Link
            to="/compliance"
            className="inline-flex items-center gap-2 rounded-lg bg-[#C9A227] px-6 py-3 text-sm font-medium text-white hover:bg-[#D4B03A] transition-colors"
          >
            <Calendar className="h-4 w-4" />
            View Full Compliance Calendar
          </Link>
        </div>
      </div>
    </div>
  )
}
