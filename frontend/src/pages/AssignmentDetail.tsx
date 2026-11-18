import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Calendar,
  User,
  Clock,
  FileText,
  CheckCircle2,
  AlertTriangle,
  MessageSquare,
  Send,
  ThumbsUp,
  ThumbsDown,
  AlertCircle,
} from 'lucide-react'
import api from '../lib/api'
import type { Assignment, AssignmentReview } from '../types/assignment'
import { AssignmentStatusBadge } from '../components/AssignmentStatusBadge'
import { AssignmentPriorityBadge } from '../components/AssignmentPriorityBadge'
import { useFirm } from '../hooks/useFirm'

type Tab = 'overview' | 'reviews' | 'activity'

export default function AssignmentDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: firmCtx } = useFirm()
  const [assignment, setAssignment] = useState<Assignment | null>(null)
  const [reviews, setReviews] = useState<AssignmentReview[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [reviewComment, setReviewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    void loadAssignment()
    void loadReviews()
  }, [id])

  async function loadAssignment() {
    try {
      setLoading(true)
      const res = await api.get(`/api/assignments/${id}`)
      setAssignment(res.data)
    } catch (error) {
      console.error('Failed to load assignment:', error)
    } finally {
      setLoading(false)
    }
  }

  async function loadReviews() {
    try {
      const res = await api.get(`/api/assignments/${id}/reviews`)
      setReviews(res.data)
    } catch (error) {
      console.error('Failed to load reviews:', error)
    }
  }

  async function handleSubmitForReview() {
    if (!confirm('Submit this assignment for manager review?')) return

    setSubmitting(true)
    try {
      await api.post(`/api/assignments/${id}/submit`)
      await loadAssignment()
      await loadReviews()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit for review')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleReview(action: 'approved' | 'rejected' | 'changes_requested') {
    if (!reviewComment.trim() && action !== 'approved') {
      alert('Please provide comments for rejection or change requests')
      return
    }

    const actionText = action === 'approved' ? 'approve' : action === 'rejected' ? 'reject' : 'request changes for'
    if (!confirm(`Are you sure you want to ${actionText} this assignment?`)) return

    setSubmitting(true)
    try {
      await api.post(`/api/assignments/${id}/review`, {
        status: action,
        comments: reviewComment.trim() || undefined,
      })
      setReviewComment('')
      await loadAssignment()
      await loadReviews()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit review')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#07101F]">
        <div className="text-slate-400">Loading assignment...</div>
      </div>
    )
  }

  if (!assignment) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-[#07101F]">
        <div className="text-slate-400 mb-4">Assignment not found</div>
        <Link to="/assignments" className="text-[#C9A227] hover:text-[#D4B03A]">
          Back to Assignments
        </Link>
      </div>
    )
  }

  const isOverdue = new Date(assignment.due_date) < new Date() && !['completed', 'approved'].includes(assignment.status)
  const canSubmit = assignment.assigned_staff === firmCtx?.user.id && ['assigned', 'in_progress'].includes(assignment.status)
  const canReview = ['manager_review', 'partner_review'].includes(assignment.status)

  return (
    <div className="min-h-screen bg-[#07101F]">
      {/* Header */}
      <div className="border-b border-border bg-[#0B1D33]/50 px-6 py-4">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <button
              onClick={() => navigate('/assignments')}
              className="mt-1 rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">{assignment.assignment_name}</h1>
              <p className="text-sm text-slate-400 mt-1">{assignment.assignment_code}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <AssignmentPriorityBadge priority={assignment.priority} />
            <AssignmentStatusBadge status={assignment.status} />
          </div>
        </div>
      </div>

      {/* Alert Banner */}
      {isOverdue && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-6 py-3">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="h-5 w-5" />
            <span className="text-sm font-medium">This assignment is overdue</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-border bg-[#0B1D33]/30 px-6">
        <div className="flex gap-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'overview'
                ? 'border-[#C9A227] text-[#C9A227]'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('reviews')}
            className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'reviews'
                ? 'border-[#C9A227] text-[#C9A227]'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            Reviews ({reviews.length})
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'activity'
                ? 'border-[#C9A227] text-[#C9A227]'
                : 'border-transparent text-slate-400 hover:text-slate-300'
            }`}
          >
            Activity
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Main Info */}
            <div className="lg:col-span-2 space-y-6">
              {/* Details Card */}
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Assignment Details</h2>
                
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Client</p>
                    <p className="text-sm text-slate-200">{assignment.client_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Service Category</p>
                    <p className="text-sm text-slate-200">{assignment.service_category}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Assignment Type</p>
                    <p className="text-sm text-slate-200">{assignment.assignment_type}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Financial Year</p>
                    <p className="text-sm text-slate-200">{assignment.financial_year}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Start Date</p>
                    <p className="text-sm text-slate-200">
                      {assignment.start_date ? new Date(assignment.start_date).toLocaleDateString() : '—'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Due Date</p>
                    <p className={`text-sm font-medium ${isOverdue ? 'text-red-400' : 'text-slate-200'}`}>
                      {new Date(assignment.due_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                {assignment.description && (
                  <div className="mt-6">
                    <p className="text-xs text-slate-500 mb-2">Description</p>
                    <p className="text-sm text-slate-300 whitespace-pre-wrap">{assignment.description}</p>
                  </div>
                )}

                {assignment.internal_notes && (
                  <div className="mt-4">
                    <p className="text-xs text-slate-500 mb-2">Internal Notes</p>
                    <p className="text-sm text-slate-300 whitespace-pre-wrap">{assignment.internal_notes}</p>
                  </div>
                )}
              </div>

              {/* Progress Card */}
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Progress</h2>
                
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="h-3 w-full rounded-full bg-slate-700 overflow-hidden">
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
                  </div>
                  <span className="text-lg font-bold text-white font-mono">{assignment.completion_pct}%</span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Estimated Hours</p>
                    <p className="text-sm text-slate-200">{assignment.estimated_hours || '—'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 mb-1">Actual Hours</p>
                    <p className="text-sm text-slate-200">{assignment.actual_hours || '—'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Team Card */}
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Team</h2>
                
                <div className="space-y-3">
                  {assignment.assigned_partner_name && (
                    <div className="flex items-start gap-3">
                      <User className="h-4 w-4 text-slate-500 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-500">Partner</p>
                        <p className="text-sm text-slate-200">{assignment.assigned_partner_name}</p>
                      </div>
                    </div>
                  )}
                  {assignment.assigned_manager_name && (
                    <div className="flex items-start gap-3">
                      <User className="h-4 w-4 text-slate-500 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-500">Manager</p>
                        <p className="text-sm text-slate-200">{assignment.assigned_manager_name}</p>
                      </div>
                    </div>
                  )}
                  {assignment.assigned_staff_name && (
                    <div className="flex items-start gap-3">
                      <User className="h-4 w-4 text-slate-500 mt-0.5" />
                      <div>
                        <p className="text-xs text-slate-500">Assigned Staff</p>
                        <p className="text-sm text-slate-200">{assignment.assigned_staff_name}</p>
                      </div>
                    </div>
                  )}
                  {!assignment.assigned_partner_name && !assignment.assigned_manager_name && !assignment.assigned_staff_name && (
                    <p className="text-sm text-slate-500">No team members assigned</p>
                  )}
                </div>
              </div>

              {/* Actions Card */}
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Actions</h2>
                
                {canSubmit && (
                  <button
                    onClick={handleSubmitForReview}
                    disabled={submitting}
                    className="w-full rounded-lg bg-[#C9A227] px-4 py-2 text-sm font-medium text-white hover:bg-[#D4B03A] disabled:opacity-50"
                  >
                    <Send className="inline h-4 w-4 mr-2" />
                    Submit for Review
                  </button>
                )}

                {!canSubmit && !canReview && (
                  <p className="text-sm text-slate-500">No actions available</p>
                )}
              </div>

              {/* Timestamps Card */}
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Timeline</h2>
                
                <div className="space-y-3 text-xs">
                  <div className="flex items-start gap-2">
                    <Calendar className="h-3 w-3 text-slate-500 mt-0.5" />
                    <div>
                      <p className="text-slate-500">Created</p>
                      <p className="text-slate-300">{new Date(assignment.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  {assignment.updated_at && (
                    <div className="flex items-start gap-2">
                      <Clock className="h-3 w-3 text-slate-500 mt-0.5" />
                      <div>
                        <p className="text-slate-500">Last Updated</p>
                        <p className="text-slate-300">{new Date(assignment.updated_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                  {assignment.completed_date && (
                    <div className="flex items-start gap-2">
                      <CheckCircle2 className="h-3 w-3 text-emerald-500 mt-0.5" />
                      <div>
                        <p className="text-slate-500">Completed</p>
                        <p className="text-slate-300">{new Date(assignment.completed_date).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'reviews' && (
          <div className="max-w-4xl">
            {/* Review Action Panel */}
            {canReview && (
              <div className="rounded-xl border border-border bg-[#0B1D33] p-6 mb-6">
                <h2 className="text-lg font-semibold text-white mb-4">Submit Review</h2>
                
                <textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  placeholder="Add your review comments..."
                  rows={4}
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none resize-none mb-4"
                />

                <div className="flex gap-3">
                  <button
                    onClick={() => handleReview('approved')}
                    disabled={submitting}
                    className="flex-1 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
                  >
                    <ThumbsUp className="inline h-4 w-4 mr-2" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleReview('changes_requested')}
                    disabled={submitting}
                    className="flex-1 rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50"
                  >
                    <AlertCircle className="inline h-4 w-4 mr-2" />
                    Request Changes
                  </button>
                  <button
                    onClick={() => handleReview('rejected')}
                    disabled={submitting}
                    className="flex-1 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                  >
                    <ThumbsDown className="inline h-4 w-4 mr-2" />
                    Reject
                  </button>
                </div>
              </div>
            )}

            {/* Reviews List */}
            <div className="rounded-xl border border-border bg-[#0B1D33] p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Review History</h2>
              
              {reviews.length === 0 ? (
                <p className="text-sm text-slate-500">No reviews yet</p>
              ) : (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div key={review.id} className="border-b border-border pb-4 last:border-0 last:pb-0">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="text-sm font-medium text-white">{review.reviewer_name}</p>
                          <p className="text-xs text-slate-500">
                            {review.review_level === 'manager' ? 'Manager Review' : 'Partner Review'}
                          </p>
                        </div>
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                            review.status === 'approved'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : review.status === 'rejected'
                                ? 'bg-red-500/10 text-red-400'
                                : review.status === 'changes_requested'
                                  ? 'bg-amber-500/10 text-amber-400'
                                  : 'bg-slate-500/10 text-slate-400'
                          }`}
                        >
                          {review.status === 'approved' ? 'Approved' : review.status === 'rejected' ? 'Rejected' : 'Changes Requested'}
                        </span>
                      </div>
                      
                      {review.comments && (
                        <p className="text-sm text-slate-300 mt-2 whitespace-pre-wrap">{review.comments}</p>
                      )}
                      
                      <div className="flex gap-4 mt-2 text-xs text-slate-500">
                        <span>Submitted: {new Date(review.submitted_at).toLocaleString()}</span>
                        {review.reviewed_at && (
                          <span>Reviewed: {new Date(review.reviewed_at).toLocaleString()}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'activity' && (
          <div className="max-w-4xl rounded-xl border border-border bg-[#0B1D33] p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Activity Log</h2>
            <p className="text-sm text-slate-500">Activity tracking coming soon...</p>
          </div>
        )}
      </div>
    </div>
  )
}
