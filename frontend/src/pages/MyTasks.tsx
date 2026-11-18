import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Calendar, Clock, AlertTriangle } from 'lucide-react'
import api from '../lib/api'
import type { Assignment } from '../types/assignment'
import { AssignmentStatusBadge } from '../components/AssignmentStatusBadge'
import { AssignmentPriorityBadge } from '../components/AssignmentPriorityBadge'

type FilterType = 'all' | 'due_today' | 'due_week' | 'overdue'

export default function MyTasks() {
  const [assignments, setAssignments] = useState<Assignment[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<FilterType>('all')

  const loadMyTasks = useCallback(async () => {
    try {
      setLoading(true)
      const res = await api.get('/api/assignments/my/tasks')
      setAssignments(res.data)
    } catch (error) {
      console.error('Failed to load my tasks:', error)
      setAssignments([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadMyTasks()
  }, [loadMyTasks])

  const isOverdue = (dueDate: string) => {
    return new Date(dueDate) < new Date()
  }

  const isDueToday = (dueDate: string) => {
    const today = new Date()
    const due = new Date(dueDate)
    return (
      due.getFullYear() === today.getFullYear() &&
      due.getMonth() === today.getMonth() &&
      due.getDate() === today.getDate()
    )
  }

  const isDueThisWeek = (dueDate: string) => {
    const today = new Date()
    const due = new Date(dueDate)
    const weekFromNow = new Date(today)
    weekFromNow.setDate(today.getDate() + 7)
    return due >= today && due <= weekFromNow
  }

  const filteredAssignments = assignments.filter((assignment) => {
    if (filter === 'all') return true
    if (filter === 'due_today') return isDueToday(assignment.due_date)
    if (filter === 'due_week') return isDueThisWeek(assignment.due_date)
    if (filter === 'overdue') return isOverdue(assignment.due_date) && !['completed', 'approved'].includes(assignment.status)
    return true
  })

  const overdueCount = assignments.filter(
    (a) => isOverdue(a.due_date) && !['completed', 'approved'].includes(a.status)
  ).length
  const dueTodayCount = assignments.filter((a) => isDueToday(a.due_date)).length
  const dueWeekCount = assignments.filter((a) => isDueThisWeek(a.due_date)).length

  const groupedByStatus = filteredAssignments.reduce(
    (acc, assignment) => {
      const status = assignment.status
      if (!acc[status]) acc[status] = []
      acc[status].push(assignment)
      return acc
    },
    {} as Record<string, Assignment[]>
  )

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading your tasks...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">My Tasks</h1>
            <p className="text-sm text-slate-400 mt-1">Assignments assigned to you</p>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <div className="rounded-lg bg-[#0B1D33] border border-border px-3 py-1.5">
              <span className="text-slate-400">Total: </span>
              <span className="font-medium text-white">{assignments.length}</span>
            </div>
            {overdueCount > 0 && (
              <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-1.5">
                <span className="text-red-400">Overdue: </span>
                <span className="font-medium text-red-400">{overdueCount}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Filters */}
      <div className="border-b border-border bg-[#0B1D33]/30 px-6 py-4">
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => setFilter('all')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-[#C9A227] text-white'
                : 'bg-[#0B1D33] border border-border text-slate-300 hover:bg-white/5'
            }`}
          >
            All Tasks ({assignments.length})
          </button>
          <button
            onClick={() => setFilter('due_today')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === 'due_today'
                ? 'bg-[#C9A227] text-white'
                : 'bg-[#0B1D33] border border-border text-slate-300 hover:bg-white/5'
            }`}
          >
            <Calendar className="inline h-4 w-4 mr-1.5" />
            Due Today ({dueTodayCount})
          </button>
          <button
            onClick={() => setFilter('due_week')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === 'due_week'
                ? 'bg-[#C9A227] text-white'
                : 'bg-[#0B1D33] border border-border text-slate-300 hover:bg-white/5'
            }`}
          >
            <Clock className="inline h-4 w-4 mr-1.5" />
            Due This Week ({dueWeekCount})
          </button>
          <button
            onClick={() => setFilter('overdue')}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              filter === 'overdue'
                ? 'bg-red-600 text-white'
                : overdueCount > 0
                  ? 'bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20'
                  : 'bg-[#0B1D33] border border-border text-slate-300 hover:bg-white/5'
            }`}
          >
            <AlertTriangle className="inline h-4 w-4 mr-1.5" />
            Overdue ({overdueCount})
          </button>
        </div>
      </div>

      {/* Tasks Content */}
      <div className="p-6">
        {filteredAssignments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="rounded-full bg-[#0B1D33] p-6 mb-4">
              <Clock className="h-12 w-12 text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-white mb-2">No tasks found</h3>
            <p className="text-sm text-slate-500 max-w-sm">
              {filter === 'all'
                ? "You don't have any assignments yet."
                : `You don't have any ${filter === 'due_today' ? 'tasks due today' : filter === 'due_week' ? 'tasks due this week' : 'overdue tasks'}.`}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(groupedByStatus).map(([status, statusAssignments]) => (
              <div key={status}>
                <div className="flex items-center gap-3 mb-3">
                  <h2 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
                    {status.replace(/_/g, ' ')}
                  </h2>
                  <span className="text-xs text-slate-600">({statusAssignments.length})</span>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {statusAssignments.map((assignment) => {
                    const overdue = isOverdue(assignment.due_date) && !['completed', 'approved'].includes(assignment.status)
                    const dueToday = isDueToday(assignment.due_date)

                    return (
                      <Link
                        key={assignment.id}
                        to={`/assignments/${assignment.id}`}
                        className="block rounded-xl border border-border bg-[#0B1D33] p-4 hover:bg-white/[0.02] transition-colors"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1 min-w-0 mr-2">
                            <h3 className="font-medium text-white text-sm mb-1 truncate">
                              {assignment.assignment_name}
                            </h3>
                            <p className="text-xs text-slate-500">{assignment.assignment_code}</p>
                          </div>
                          <AssignmentPriorityBadge priority={assignment.priority} />
                        </div>

                        <div className="space-y-2 mb-3">
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <span className="truncate">{assignment.client_name}</span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center rounded border border-border px-2 py-0.5 text-xs text-slate-400">
                              {assignment.service_category}
                            </span>
                            <AssignmentStatusBadge status={assignment.status} />
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className={`text-xs ${overdue ? 'text-red-400 font-medium' : dueToday ? 'text-amber-400 font-medium' : 'text-slate-500'}`}>
                            <Calendar className="inline h-3 w-3 mr-1" />
                            {overdue ? 'Overdue' : dueToday ? 'Due today' : `Due ${new Date(assignment.due_date).toLocaleDateString()}`}
                          </div>
                          <div className="text-xs text-slate-500 font-mono">{assignment.completion_pct}%</div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-3 h-1.5 w-full rounded-full bg-slate-700 overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              assignment.completion_pct >= 80
                                ? 'bg-emerald-500'
                                : assignment.completion_pct >= 30
                                  ? 'bg-blue-500'
                                  : 'bg-slate-500'
                            }`}
                            style={{ width: `${assignment.completion_pct}%` }}
                          />
                        </div>
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
