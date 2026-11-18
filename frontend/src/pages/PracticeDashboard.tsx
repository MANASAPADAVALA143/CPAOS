import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Users,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  BarChart3,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import api from '../lib/api'
import type { PracticeDashboardData } from '../types/assignment'
import { AssignmentStatusBadge } from '../components/AssignmentStatusBadge'

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']

export default function PracticeDashboard() {
  const [data, setData] = useState<PracticeDashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void loadDashboard()
  }, [])

  async function loadDashboard() {
    try {
      setLoading(true)
      const res = await api.get('/api/analytics/practice-dashboard')
      setData(res.data)
    } catch (error) {
      console.error('Failed to load practice dashboard:', error)
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

  if (!data) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Failed to load dashboard</div>
      </div>
    )
  }

  const { kpis, assignments_by_status, overdue_assignments, staff_workload } = data

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Practice Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Overview of your CA practice operations</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {/* Total Clients */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total Clients</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.total_clients}</p>
                <p className="text-xs text-emerald-400 mt-1">
                  {kpis.active_clients} active
                </p>
              </div>
              <div className="rounded-full bg-blue-500/10 p-3">
                <Users className="h-6 w-6 text-blue-400" />
              </div>
            </div>
          </div>

          {/* Active Assignments */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Active Assignments</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.active_assignments}</p>
                <p className="text-xs text-blue-400 mt-1">In progress</p>
              </div>
              <div className="rounded-full bg-indigo-500/10 p-3">
                <FileText className="h-6 w-6 text-indigo-400" />
              </div>
            </div>
          </div>

          {/* Overdue Assignments */}
          <Link
            to="/assignments?filter=overdue"
            className="rounded-xl border border-border bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Overdue</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.overdue_assignments}</p>
                <p className="text-xs text-red-400 mt-1">Needs attention</p>
              </div>
              <div className="rounded-full bg-red-500/10 p-3">
                <AlertTriangle className="h-6 w-6 text-red-400" />
              </div>
            </div>
          </Link>

          {/* Completed This Month */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Completed (Month)</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.completed_assignments_month}</p>
                <p className="text-xs text-emerald-400 mt-1">This month</p>
              </div>
              <div className="rounded-full bg-emerald-500/10 p-3">
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              </div>
            </div>
          </div>

          {/* Pending Reviews */}
          <Link
            to="/review-queue"
            className="rounded-xl border border-border bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Pending Reviews</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.pending_reviews}</p>
                <p className="text-xs text-amber-400 mt-1">
                  Manager: {kpis.pending_manager_reviews}, Partner: {kpis.pending_partner_reviews}
                </p>
              </div>
              <div className="rounded-full bg-amber-500/10 p-3">
                <Clock className="h-6 w-6 text-amber-400" />
              </div>
            </div>
          </Link>

          {/* Staff Utilization */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Staff Utilization</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.staff_utilization.toFixed(0)}%</p>
                <p className="text-xs text-slate-400 mt-1">Average capacity</p>
              </div>
              <div className="rounded-full bg-purple-500/10 p-3">
                <TrendingUp className="h-6 w-6 text-purple-400" />
              </div>
            </div>
          </div>

          {/* Documents Pending */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Docs Pending Review</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.docs_pending_review}</p>
                <p className="text-xs text-slate-400 mt-1">Awaiting action</p>
              </div>
              <div className="rounded-full bg-orange-500/10 p-3">
                <FileText className="h-6 w-6 text-orange-400" />
              </div>
            </div>
          </div>

          {/* Active Clients */}
          <Link
            to="/clients"
            className="rounded-xl border border-border bg-[#0B1D33] p-6 hover:bg-white/[0.02] transition-colors"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Active Clients</p>
                <p className="text-3xl font-bold text-white mt-1">{kpis.active_clients}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {((kpis.active_clients / kpis.total_clients) * 100).toFixed(0)}% of total
                </p>
              </div>
              <div className="rounded-full bg-teal-500/10 p-3">
                <Users className="h-6 w-6 text-teal-400" />
              </div>
            </div>
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Assignments by Status */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[#C9A227]" />
              Assignments by Status
            </h2>

            {assignments_by_status.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={assignments_by_status}
                    dataKey="count"
                    nameKey="status"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ status, count }) => `${status.replace(/_/g, ' ')}: ${count}`}
                    labelLine={false}
                  >
                    {assignments_by_status.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: '#0B1D33',
                      border: '1px solid #1E2A3B',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-sm text-slate-500">
                No assignment data available
              </div>
            )}
          </div>

          {/* Staff Workload */}
          <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-[#C9A227]" />
              Staff Workload
            </h2>

            {staff_workload.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={staff_workload.slice(0, 10)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1E2A3B" />
                  <XAxis
                    dataKey="staff_name"
                    stroke="#94A3B8"
                    fontSize={11}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis stroke="#94A3B8" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      background: '#0B1D33',
                      border: '1px solid #1E2A3B',
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="assignments_count" fill="#C9A227" name="Assignments" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-sm text-slate-500">
                No staff workload data available
              </div>
            )}
          </div>
        </div>

        {/* Overdue Assignments Table */}
        {overdue_assignments.length > 0 && (
          <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
            <div className="px-6 py-4 border-b border-border">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                Overdue Assignments
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-border bg-[#0B1D33]">
                  <tr className="text-left">
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Assignment
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Client
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Due Date
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Days Overdue
                    </th>
                    <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                      Assigned To
                    </th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {overdue_assignments.map((assignment) => (
                    <tr key={assignment.assignment_id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-4 py-3">
                        <div>
                          <Link
                            to={`/assignments/${assignment.assignment_id}`}
                            className="font-medium text-white hover:text-[#C9A227]"
                          >
                            {assignment.assignment_name}
                          </Link>
                          <div className="text-xs text-slate-500 mt-0.5">
                            {assignment.assignment_code}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {assignment.client_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-red-400">
                        {new Date(assignment.due_date).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3">
                        <span className="inline-flex items-center rounded-full bg-red-500/10 px-2 py-1 text-xs font-medium text-red-400">
                          {assignment.days_overdue} days
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {assignment.assigned_staff || '—'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/assignments/${assignment.assignment_id}`}
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
      </div>
    </div>
  )
}
