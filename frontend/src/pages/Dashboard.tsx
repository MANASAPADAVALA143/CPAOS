import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { supabase } from '../lib/supabase'
import api from '../lib/api'
import { useFirm } from '../hooks/useFirm'
import { CountryFlag } from '../components/CountryFlag'

type ClientRow = {
  id: string
  client_name: string
  business_name?: string | null
  country: string
  entity_type: string
  status: string
  completion_pct: number
  portal_link: string
  created_at?: string | null
}

type Kpis = {
  active_clients: number
  completed_this_month: number
  avg_completion_days: number
  docs_pending_review: number
  signature_pending: number
  completion_rate_pct: number
}

const PIE_COLORS = ['#2563EB', '#38BDF8', '#A78BFA', '#34D399', '#FBBF24', '#F472B6']

export default function Dashboard() {
  const { data: firmCtx, loading: firmLoading } = useFirm()
  const [clients, setClients] = useState<ClientRow[]>([])
  const [analytics, setAnalytics] = useState<{
    kpis: Kpis
    by_country: { country: string; count: number }[]
    completion_trend: { month: string; completed: number }[]
  } | null>(null)
  const [tab, setTab] = useState<string>('all')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const load = useCallback(async () => {
    try {
      const [cRes, aRes] = await Promise.all([
        api.get('/api/clients'),
        api.get('/api/analytics/dashboard').catch(() => null),
      ])
      setClients(cRes.data)
      if (aRes) setAnalytics(aRes.data)
    } catch {
      setClients([])
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const filtered = useMemo(() => {
    if (tab === 'all') return clients
    return clients.filter((c) => c.status === tab)
  }, [clients, tab])

  const allFilteredSelected =
    filtered.length > 0 && filtered.every((c) => selected.has(c.id))

  function toggleSelect(id: string) {
    setSelected((prev) => {
      const n = new Set(prev)
      if (n.has(id)) n.delete(id)
      else n.add(id)
      return n
    })
  }

  function toggleSelectAll() {
    if (allFilteredSelected) {
      setSelected((prev) => {
        const n = new Set(prev)
        filtered.forEach((c) => n.delete(c.id))
        return n
      })
    } else {
      setSelected((prev) => {
        const n = new Set(prev)
        filtered.forEach((c) => n.add(c.id))
        return n
      })
    }
  }

  async function logout() {
    await supabase.auth.signOut()
    window.location.reload()
  }

  async function bulkRemind() {
    const ids = Array.from(selected)
    if (!ids.length) return
    try {
      const res = await api.post('/api/clients/bulk-remind', { client_ids: ids })
      toast.success(`Reminders sent: ${res.data.sent}, failed: ${res.data.failed}`)
      void load()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Bulk remind failed')
    }
  }

  async function exportCsv() {
    const ids = Array.from(selected)
    try {
      const res = await api.get('/api/clients/export-csv', {
        params: ids.length ? { ids: ids.join(',') } : {},
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `clients-${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('CSV downloaded')
    } catch {
      toast.error('Export failed')
    }
  }

  async function generateReport() {
    const ids = Array.from(selected)
    if (!ids.length) {
      toast.error('Select at least one client')
      return
    }
    try {
      const res = await api.post(
        '/api/clients/generate-report',
        { client_ids: ids },
        { responseType: 'blob' },
      )
      const blob = res.data instanceof Blob ? res.data : new Blob([res.data], { type: 'application/pdf' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `cpaos-report-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      toast.success('PDF report downloaded')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Report download failed')
    }
  }

  if (firmLoading) return <div className="p-8 text-slate-400">Loading…</div>

  const authed = Boolean(firmCtx)
  const kpis = analytics?.kpis

  return (
    <div className="min-h-screen noise pb-24">
      <header className="border-b border-border bg-card/60 backdrop-blur px-6 py-4 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div className="font-display text-lg">{firmCtx?.firm.name ?? 'CPAOS'}</div>
          <div className="text-xs text-slate-400">
            {firmCtx ? firmCtx.user.full_name : 'Dashboard — sign in for live analytics'}
          </div>
        </div>
        <div className="flex gap-3 items-center flex-wrap">
          <Link to="/home" className="text-sm text-slate-400 hover:text-white">
            Marketing
          </Link>
          {authed ? (
            <>
              <Link to="/settings" className="text-sm text-slate-300">
                Settings
              </Link>
              <Link to="/clients/new" className="text-sm rounded-lg bg-primary px-3 py-1.5 text-white">
                New client
              </Link>
              <button type="button" className="text-sm text-slate-400" onClick={logout}>
                Log out
              </button>
            </>
          ) : null}
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-6 py-8">
        {!authed && (
          <p className="mb-6 text-sm text-slate-400 rounded-lg border border-border bg-card/50 px-4 py-3">
            Sign in to load firm analytics and client actions from the API.
          </p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { label: 'Active onboardings', value: kpis?.active_clients ?? '—' },
            { label: 'Completed this month', value: kpis?.completed_this_month ?? '—' },
            { label: 'Docs pending review', value: kpis?.docs_pending_review ?? '—' },
            { label: 'Pending signatures', value: kpis?.signature_pending ?? '—' },
            { label: 'Avg days to complete', value: kpis?.avg_completion_days ?? '—' },
            { label: 'Completion rate', value: kpis != null ? `${kpis.completion_rate_pct}%` : '—' },
          ].map((k) => (
            <div key={k.label} className="rounded-xl border border-border bg-card p-4">
              <div className="text-xs text-slate-400">{k.label}</div>
              <div className="text-2xl font-mono mt-2">{k.value}</div>
            </div>
          ))}
        </div>

        {analytics && (
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="text-sm font-medium text-slate-200 mb-2">Completion trend</div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.completion_trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="month" stroke="#94A3B8" />
                    <YAxis stroke="#94A3B8" allowDecimals={false} />
                    <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                    <Bar dataKey="completed" fill="#2563EB" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="rounded-xl border border-border bg-card p-4">
              <div className="text-sm font-medium text-slate-200 mb-2">Clients by country</div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analytics.by_country}
                      dataKey="count"
                      nameKey="country"
                      cx="50%"
                      cy="50%"
                      outerRadius={90}
                      label
                    >
                      {analytics.by_country.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        <div className="mt-8 flex flex-wrap gap-2">
          {['all', 'signature_pending', 'in_progress', 'under_review', 'completed'].map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`rounded-full px-3 py-1 text-xs border ${
                tab === t ? 'border-primary text-primary' : 'border-border text-slate-300'
              }`}
            >
              {t.replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        <div className="mt-4 rounded-xl border border-border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-card text-left text-xs text-slate-400">
              <tr>
                <th className="px-3 py-3 w-10">
                  <input type="checkbox" checked={allFilteredSelected} onChange={toggleSelectAll} />
                </th>
                <th className="px-4 py-3">Client</th>
                <th className="px-4 py-3">Entity</th>
                <th className="px-4 py-3">Country</th>
                <th className="px-4 py-3">Progress</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-500">
                    No clients to show yet.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => (
                  <tr key={c.id} className="border-t border-border">
                    <td className="px-3 py-3">
                      <input type="checkbox" checked={selected.has(c.id)} onChange={() => toggleSelect(c.id)} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium">{c.client_name}</div>
                      <div className="text-xs text-slate-500">{c.business_name}</div>
                    </td>
                    <td className="px-4 py-3">{c.entity_type}</td>
                    <td className="px-4 py-3">
                      <CountryFlag country={c.country} />
                      {c.country}
                    </td>
                    <td className="px-4 py-3 w-48">
                      <div className="h-2 rounded bg-border overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${c.completion_pct}%` }} />
                      </div>
                      <div className="text-xs text-slate-400 mt-1">{c.completion_pct}%</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-border px-2 py-0.5 text-xs">{c.status}</span>
                    </td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <Link className="text-primary" to={`/clients/${c.id}`}>
                        View
                      </Link>
                      <button
                        type="button"
                        className="text-slate-300"
                        onClick={() => navigator.clipboard.writeText(c.portal_link)}
                      >
                        Copy portal
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>

      {selected.size > 0 && (
        <div className="fixed bottom-0 inset-x-0 border-t border-border bg-card/95 backdrop-blur px-6 py-3 flex flex-wrap gap-3 items-center justify-between">
          <div className="text-sm text-slate-300">{selected.size} selected</div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="rounded-lg bg-primary px-3 py-1.5 text-sm text-white" onClick={bulkRemind}>
              Send reminder to all
            </button>
            <button type="button" className="rounded-lg border border-border px-3 py-1.5 text-sm" onClick={exportCsv}>
              Export to CSV
            </button>
            <button type="button" className="rounded-lg border border-border px-3 py-1.5 text-sm" onClick={generateReport}>
              Generate report
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
