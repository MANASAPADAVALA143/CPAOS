import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { FileCheck, Calendar, User, AlertCircle } from 'lucide-react'
import api from '../lib/api'
import type { Assignment } from '../types/assignment'
import { AssignmentStatusBadge } from '../components/AssignmentStatusBadge'
import { AssignmentPriorityBadge } from '../components/AssignmentPriorityBadge'
import { useFirm } from '../hooks/useFirm'

export default function ReviewQueue() {
  const { data: firmCtx } = useFirm()
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [loading, setLoading] = useState(true)

  const loadReviewQueue = useCallback(async () => {
    try {
      setLoading(true)
      const res = await api.get('/api/assignments/review-queue')
      setAssignments(res.data)
    } catch (error) {
      console.error('Failed to load review queue:', error)
      setAssignments([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadReviewQueue()
  }, [loadReviewQueue])

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date()
  }

  const managerReviews = assignments.filter((a) => a.status === 'manager_review')
  const partnerReviews = assignments.filter((a) => a.status === 'partner_review')

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading review queue...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Review Queue</h1>
            <p className="text-sm text-slate-400 mt-1">Assignments pending your review</p>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <div className="rounded-lg bg-[#0B1D33] border border-border px-3 py-1.5">
              <span className="text-slate-400">Total Pending: </span>
              <span className="font-medium text-white">{assignments.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {assignments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-[#0B1D33] p-6 mb-4">
              <FileCheck className="h-12 w-12 text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">No pending reviews</h3>
            <p className="text-sm text-slate-500 max-w-sm">
              You're all caught up! There are no assignments waiting for your review.
            </p>
          </div>
        ) : (
          <div className="space-y-8 max-w-6xl">
            {/* Manager Reviews Section */}
            {managerReviews.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <h2 className="text-lg font-semibold text-white">Manager Reviews</h2>
                  <span className="rounded-full bg-[#C9A227]/20 px-2.5 py-0.5 text-xs font-medium text-[#C9A227]">
                    {managerReviews.length} pending
                  </span>
                </div>

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
                          Staff
                        </th>
                        <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                          Due Date
                        </th>
                        <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                          Priority
                        </th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {managerReviews.map((assignment) => {
                        const overdue = isOverdue(assignment.due_date)
                        
                        return (
                          <tr key={assignment.id} className="hover:bg-white/[0.02] transition-colors">
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
                            <td className="px-4 py-3 text-sm text-slate-300">
                              {assignment.assigned_staff_name || '—'}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={overdue ? 'text-red-400 font-medium' : 'text-slate-300'}>
                                {new Date(assignment.due_date).toLocaleDateString()}
                              </span>
                              {overdue && (
                                <div className="text-xs text-red-400 mt-0.5">Overdue</div>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <AssignmentPriorityBadge priority={assignment.priority} />
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Link
                                to={`/assignments/${assignment.id}`}
                                className="inline-flex items-center gap-1.5 rounded-lg bg-[#C9A227] px-3 py-1.5 text-xs font-medium text-white hover:bg-[#D4B03A] transition-colors"
                              >
                                Review
                              </Link>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Partner Reviews Section */}
            {partnerReviews.length > 0 && (
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <h2 className="text-lg font-semibold text-white">Partner Reviews</h2>
                  <span className="rounded-full bg-[#C9A227]/20 px-2.5 py-0.5 text-xs font-medium text-[#C9A227]">
                    {partnerReviews.length} pending
                  </span>
                </div>

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
                          Manager
                        </th>
                        <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                          Due Date
                        </th>
                        <th className="px-4 py-3 text-xs font-medium uppercase tracking-wider text-slate-500">
                          Priority
                        </th>
                        <th className="px-4 py-3"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {partnerReviews.map((assignment) => {
                        const overdue = isOverdue(assignment.due_date)
                        
                        return (
                          <tr key={assignment.id} className="hover:bg-white/[0.02] transition-colors">
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
                            <td className="px-4 py-3 text-sm text-slate-300">
                              {assignment.assigned_manager_name || '—'}
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={overdue ? 'text-red-400 font-medium' : 'text-slate-300'}>
                                {new Date(assignment.due_date).toLocaleDateString()}
                              </span>
                              {overdue && (
                                <div className="text-xs text-red-400 mt-0.5">Overdue</div>
                              )}
                            </td>
                            <td className="px-4 py-3">
                              <AssignmentPriorityBadge priority={assignment.priority} />
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Link
                                to={`/assignments/${assignment.id}`}
                                className="inline-flex items-center gap-1.5 rounded-lg bg-[#C9A227] px-3 py-1.5 text-xs font-medium text-white hover:bg-[#D4B03A] transition-colors"
                              >
                                Review
                              </Link>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
