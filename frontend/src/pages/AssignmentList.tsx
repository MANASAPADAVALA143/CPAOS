import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Plus, Search, Filter } from 'lucide-react'
import api from '../lib/api'
import type { Assignment } from '../types/assignment'
import { AssignmentStatusBadge } from '../components/AssignmentStatusBadge'
import { AssignmentPriorityBadge } from '../components/AssignmentPriorityBadge'
import { CreateAssignmentModal } from '../components/CreateAssignmentModal'

export default function AssignmentList() {
  const navigate = useNavigate()
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [serviceCategoryFilter, setServiceCategoryFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const loadAssignments = useCallback(async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (search) params.search = search
      if (statusFilter !== 'all') params.status = statusFilter
      if (serviceCategoryFilter !== 'all') params.service_category = serviceCategoryFilter
      
      const res = await api.get('/api/assignments', { params })
      setAssignments(res.data)
    } catch (error) {
      console.error('Failed to load assignments:', error)
      setAssignments([])
    } finally {
      setLoading(false)
    }
  }, [search, statusFilter, serviceCategoryFilter])

  useEffect(() => {
    void loadAssignments()
  }, [loadAssignments])

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date() && !['completed', 'approved'].includes(statusFilter)
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-slate-400">Loading assignments...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Assignments</h1>
            <p className="text-sm text-slate-400 mt-1">Manage client assignments and tasks</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-[#C9A227] px-4 py-2 text-sm font-medium text-white hover:bg-[#D4B03A] transition-colors"
          >
            <Plus className="h-4 w-4" />
            New Assignment
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="border-b border-border bg-[#0B1D33]/30 px-6 py-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search assignments..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-border bg-[#0B1D33] pl-10 pr-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-border bg-[#0B1D33] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
          >
            <option value="all">All Status</option>
            <option value="in_progress">In Progress</option>
            <option value="submitted">Submitted</option>
            <option value="manager_review">Manager Review</option>
            <option value="partner_review">Partner Review</option>
            <option value="approved">Approved</option>
            <option value="completed">Completed</option>
          </select>

          {/* Service Category Filter */}
          <select
            value={serviceCategoryFilter}
            onChange={(e) => setServiceCategoryFilter(e.target.value)}
            className="rounded-lg border border-border bg-[#0B1D33] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
          >
            <option value="all">All Services</option>
            <option value="GST">GST</option>
            <option value="Income Tax">Income Tax</option>
            <option value="TDS">TDS</option>
            <option value="MCA">MCA</option>
            <option value="Audit">Audit</option>
            <option value="Accounting">Accounting</option>
          </select>
        </div>
      </div>

      {/* Assignments Table */}
      <div className="p-6">
        <div className="rounded-xl border border-border bg-[#0B1D33] overflow-hidden">
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
                  Service
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Due Date
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Priority
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Status
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Assigned To
                </th>
                <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                  Progress
                </th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {assignments.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-12 text-center">
                    <div className="text-slate-500">
                      {search || statusFilter !== 'all' || serviceCategoryFilter !== 'all'
                        ? 'No assignments match your filters.'
                        : 'No assignments yet. Create your first assignment to get started.'}
                    </div>
                  </td>
                </tr>
              ) : (
                assignments.map((assignment) => (
                  <tr
                    key={assignment.id}
                    className="hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div>
                        <Link
                          to={`/assignments/${assignment.id}`}
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
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center rounded border border-border px-2 py-0.5 text-xs text-slate-400">
                        {assignment.service_category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm">
                      <span className={isOverdue(assignment.due_date) ? 'text-red-400 font-medium' : 'text-slate-300'}>
                        {new Date(assignment.due_date).toLocaleDateString()}
                      </span>
                      {isOverdue(assignment.due_date) && (
                        <div className="text-xs text-red-400 mt-0.5">Overdue</div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <AssignmentPriorityBadge priority={assignment.priority} />
                    </td>
                    <td className="px-4 py-3">
                      <AssignmentStatusBadge status={assignment.status} />
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-300">
                      {assignment.assigned_staff_name || assignment.assigned_manager_name || assignment.assigned_partner_name || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 rounded-full bg-slate-700 overflow-hidden">
                          <div
                            className={`h-full ${
                              assignment.completion_pct >= 80
                                ? 'bg-emerald-500'
                                : assignment.completion_pct >= 30
                                  ? 'bg-blue-500'
                                  : 'bg-slate-500'
                            }`}
                            style={{ width: `${assignment.completion_pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-500 font-mono">
                          {assignment.completion_pct}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        to={`/assignments/${assignment.id}`}
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
        
        {assignments.length > 0 && (
          <div className="mt-4 text-sm text-slate-500">
            Showing {assignments.length} assignment{assignments.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Create Assignment Modal */}
      <CreateAssignmentModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={(assignmentId) => {
          void loadAssignments()
          navigate(`/assignments/${assignmentId}`)
        }}
      />
    </div>
  )
}
