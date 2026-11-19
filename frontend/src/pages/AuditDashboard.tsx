/**
 * GNANOVA CA PRACTICE OS - Audit Dashboard
 * Phase 4: Audit engagement overview and statistics
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FileCheck,
  FileText,
  ClipboardList,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Plus,
} from 'lucide-react'
import { api } from '../lib/api'
import type { AuditDashboardStats, AuditEngagement } from '../types/audit'

export function AuditDashboard() {
  const [stats, setStats] = useState<AuditDashboardStats | null>(null)
  const [engagements, setEngagements] = useState<AuditEngagement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  async function fetchDashboardData() {
    try {
      const [statsRes, engagementsRes] = await Promise.all([
        api.get('/api/audit/engagements/dashboard/stats'),
        api.get('/api/audit/engagements'),
      ])
      setStats(statsRes.data)
      setEngagements(engagementsRes.data.engagements.slice(0, 10))
    } catch (error) {
      console.error('Failed to fetch audit dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#C9A227] border-r-transparent"></div>
          <p className="mt-2 text-sm text-slate-600">Loading audit dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Audit Management</h1>
          <p className="mt-1 text-sm text-slate-600">
            Manage audit engagements, working papers, and reviews
          </p>
        </div>
        <Link
          to="/audit/engagements/new"
          className="inline-flex items-center gap-2 rounded-lg bg-[#C9A227] px-4 py-2 text-sm font-medium text-white hover:bg-[#D4B03A] transition-colors"
        >
          <Plus className="h-4 w-4" />
          New Engagement
        </Link>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {/* Total Engagements */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Engagements</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.total_engagements}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.active_engagements} active
                </p>
              </div>
              <div className="rounded-lg bg-blue-50 p-3">
                <FileCheck className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Working Papers */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Working Papers</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.total_working_papers}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.approved_papers} approved
                </p>
              </div>
              <div className="rounded-lg bg-green-50 p-3">
                <FileText className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </div>

          {/* PBC Items */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">PBC Items</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.total_pbc_items}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.pending_pbc} pending
                </p>
              </div>
              <div className="rounded-lg bg-yellow-50 p-3">
                <ClipboardList className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </div>

          {/* Review Notes */}
          <div className="rounded-lg border border-slate-200 bg-white p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Open Reviews</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {stats.open_review_notes}
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  {stats.high_risk_areas} high risk
                </p>
              </div>
              <div className="rounded-lg bg-red-50 p-3">
                <AlertTriangle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Engagement Status Breakdown */}
      {stats && (
        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Engagement Status Breakdown
          </h2>
          <div className="grid gap-4 md:grid-cols-5">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-slate-600">Planning</p>
                <p className="text-xl font-semibold text-slate-900">
                  {stats.planning_phase}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-sm text-slate-600">Fieldwork</p>
                <p className="text-xl font-semibold text-slate-900">
                  {stats.fieldwork_phase}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-slate-600">Review</p>
                <p className="text-xl font-semibold text-slate-900">
                  {stats.review_phase}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <FileCheck className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-slate-600">Reporting</p>
                <p className="text-xl font-semibold text-slate-900">
                  {stats.reporting_phase}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-slate-600">Completed</p>
                <p className="text-xl font-semibold text-slate-900">
                  {stats.completed}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Engagements */}
      <div className="rounded-lg border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Recent Engagements</h2>
            <Link
              to="/audit/engagements"
              className="text-sm font-medium text-[#C9A227] hover:text-[#D4B03A]"
            >
              View all →
            </Link>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Engagement
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Client
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                  Progress
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {engagements.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <FileCheck className="mx-auto h-12 w-12 text-slate-300" />
                    <p className="mt-2 text-sm text-slate-600">No audit engagements yet</p>
                    <Link
                      to="/audit/engagements/new"
                      className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-[#C9A227] hover:text-[#D4B03A]"
                    >
                      <Plus className="h-4 w-4" />
                      Create your first engagement
                    </Link>
                  </td>
                </tr>
              ) : (
                engagements.map((engagement) => (
                  <tr key={engagement.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <Link
                        to={`/audit/engagements/${engagement.id}`}
                        className="font-medium text-slate-900 hover:text-[#C9A227]"
                      >
                        {engagement.engagement_name}
                      </Link>
                      <p className="text-xs text-slate-500">{engagement.engagement_code}</p>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">
                      {engagement.client_id}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                        {engagement.engagement_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(
                          engagement.status
                        )}`}
                      >
                        {engagement.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-32 rounded-full bg-slate-200">
                          <div
                            className="h-2 rounded-full bg-[#C9A227]"
                            style={{
                              width: `${getProgressPercent(engagement.status)}%`,
                            }}
                          />
                        </div>
                        <span className="text-xs text-slate-600">
                          {getProgressPercent(engagement.status)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    planning: 'bg-blue-100 text-blue-700',
    fieldwork: 'bg-yellow-100 text-yellow-700',
    review: 'bg-orange-100 text-orange-700',
    reporting: 'bg-purple-100 text-purple-700',
    completed: 'bg-green-100 text-green-700',
    archived: 'bg-slate-100 text-slate-700',
  }
  return colors[status] || 'bg-slate-100 text-slate-700'
}

function getProgressPercent(status: string): number {
  const progress: Record<string, number> = {
    planning: 20,
    fieldwork: 40,
    review: 60,
    reporting: 80,
    completed: 100,
    archived: 100,
  }
  return progress[status] || 0
}
