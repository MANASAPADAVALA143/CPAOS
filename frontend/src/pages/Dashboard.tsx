import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import { Globe2 } from 'lucide-react'
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

type CountryStat = { country: string; count: number; avg_completion_pct: number }

type Analytics = {
  kpis: Kpis
  by_country: CountryStat[]
  completion_trend: { month: string; completed: number }[]
}

const COUNTRY_META: Record<string, { code: string; color: string }> = {
  UAE: { code: 'AE', color: '#3B82F6' },
  UK: { code: 'GB', color: '#10B981' },
  India: { code: 'IN', color: '#F59E0B' },
  US: { code: 'US', color: '#818CF8' },
  Singapore: { code: 'SG', color: '#FB923C' },
  Australia: { code: 'AU', color: '#22D3EE' },
  Other: { code: '··', color: '#94A3B8' },
}

const metaFor = (country: string) => COUNTRY_META[country] ?? COUNTRY_META.Other

const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'under_review', label: 'Under review' },
  { value: 'signature_pending', label: 'Sig. pending' },
  { value: 'documents_pending', label: 'Docs pending' },
  { value: 'completed', label: 'Completed' },
  { value: 'invited', label: 'Invited' },
]

const STATUS_STYLE: Record<string, { label: string; className: string }> = {
  invited: { label: 'Invited', className: 'bg-slate-500/15 text-slate-400' },
  signature_pending: { label: 'Sig. pending', className: 'bg-indigo-500/15 text-indigo-300' },
  in_progress: { label: 'In progress', className: 'bg-blue-500/15 text-blue-300' },
  documents_pending: { label: 'Docs pending', className: 'bg-orange-500/15 text-orange-300' },
  under_review: { label: 'Under review', className: 'bg-amber-500/15 text-amber-300' },
  completed: { label: 'Completed', className: 'bg-emerald-500/15 text-emerald-300' },
  active: { label: 'Active', className: 'bg-emerald-500/15 text-emerald-300' },
}

const tooltipStyle = { background: '#0B1628', border: '1px solid #1E2A3B', borderRadius: 8, fontSize: 12 }

export default function Dashboard() {
  const { data: firmCtx, loading: firmLoading } = useFirm()
  const [clients, setClients] = useState<ClientRow[]>([])
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [country, setCountry] = useState<string>('all')
  const [status, setStatus] = useState<string>('all')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const loadClients = useCallback(async () => {
    try {
      const res = await api.get('/api/clients')
      setClients(res.data)
    } catch {
      setClients([])
    }
  }, [])

  const loadAnalytics = useCallback(async () => {
    try {
      const res = await api.get('/api/analytics/dashboard', {
        params: country === 'all' ? {} : { country },
      })
      setAnalytics(res.data)
    } catch {
      setAnalytics(null)
    }
  }, [country])

  useEffect(() => {
    void loadClients()
  }, [loadClients])

  useEffect(() => {
    void loadAnalytics()
  }, [loadAnalytics])

  const load = useCallback(async () => {
    await Promise.all([loadClients(), loadAnalytics()])
  }, [loadClients, loadAnalytics])

  const countryStats: CountryStat[] = useMemo(() => {
    if (analytics?.by_country?.length && analytics.by_country.every((s) => s.avg_completion_pct != null)) {
      return analytics.by_country
    }
    const acc = new Map<string, { count: number; sum: number }>()
    clients.forEach((c) => {
      const s = acc.get(c.country) ?? { count: 0, sum: 0 }
      s.count += 1
      s.sum += Number(c.completion_pct) || 0
      acc.set(c.country, s)
    })
    return Array.from(acc.entries())
      .map(([k, v]) => ({ country: k, count: v.count, avg_completion_pct: Math.round(v.sum / v.count) }))
      .sort((a, b) => b.count - a.count)
  }, [analytics, clients])

  const totalClients = countryStats.reduce((n, c) => n + c.count, 0)

  const filtered = useMemo(
    () =>
      clients.filter(
        (c) => (country === 'all' || c.country === country) && (status === 'all' || c.status === status),
      ),
    [clients, country, status],
  )

  const allFilteredSelected = filtered.length > 0 && filtered.every((c) => selected.has(c.id))

  function toggleSelect(id: string) {
    setSelected((prev) => {
      const n = new Set(prev)
      if (n.has(id)) n.delete(id)
      else n.add(id)
      return n
    })
  }

  function toggleSelectAll() {
    setSelected((prev) => {
      const n = new Set(prev)
      if (allFilteredSelected) filtered.forEach((c) => n.delete(c.id))
      else filtered.forEach((c) => n.add(c.id))
      return n
    })
  }

  function pickCountry(next: string) {
    setCountry((cur) => (cur === next ? 'all' : next))
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
      const res = await api.post('/api/clients/generate-report', { client_ids: ids }, { responseType: 'blob' })
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
  const kpiCards = [
    { label: 'Active', value: kpis?.active_clients, color: 'text-blue-400' },
    { label: 'Completed', value: kpis?.completed_this_month, color: 'text-emerald-400' },
    { label: 'Docs pending', value: kpis?.docs_pending_review, color: 'text-amber-400' },
    { label: 'Sig. pending', value: kpis?.signature_pending, color: 'text-slate-100' },
    { label: 'Avg days', value: kpis?.avg_completion_days, color: 'text-slate-100' },
    {
      label: 'Completion',
      value: kpis != null ? `${kpis.completion_rate_pct}%` : undefined,
      color: 'text-slate-100',
    },
  ]

  return (
    <div className="min-h-screen bg-[#07101F] pb-24">
      <header className="sticky top-0 z-10 border-b border-border bg-[#07101F]/90 backdrop-blur px-6 py-3 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <div className="text-lg font-semibold">{firmCtx?.firm.name ?? 'CPAOS'}</div>
          <div className="text-xs text-slate-500">
            {firmCtx ? `${firmCtx.user.full_name} · CPAOS` : 'Dashboard — sign in for live analytics'}
          </div>
        </div>
        <div className="flex gap-4 items-center flex-wrap text-sm">
          <Link to="/home" className="text-slate-400 hover:text-white">
            Marketing
          </Link>
          {authed && (
            <>
              <Link to="/settings" className="text-slate-400 hover:text-white">
                Settings
              </Link>
              <button type="button" className="text-slate-400 hover:text-white" onClick={logout}>
                Log out
              </button>
              <Link to="/clients/new" className="rounded-lg bg-primary px-3 py-1.5 font-medium text-white hover:bg-blue-500">
                + New client
              </Link>
            </>
          )}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-6">
        {!authed && (
          <p className="mb-6 text-sm text-slate-400 rounded-lg border border-border bg-card/50 px-4 py-3">
            Sign in to load firm analytics and client actions from the API.
          </p>
        )}

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {kpiCards.map((k) => (
            <div key={k.label} className="rounded-xl border border-border bg-[#0B1628] px-4 py-3">
              <div className="text-[11px] uppercase tracking-wider text-slate-500">{k.label}</div>
              <div className={`mt-2 font-mono text-2xl ${k.color}`}>{k.value ?? '—'}</div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-[11px] uppercase tracking-wider text-slate-500">Filter by country</div>
        <div className="mt-2 flex gap-3 overflow-x-auto pb-1">
          <CountryCard
            active={country === 'all'}
            onClick={() => setCountry('all')}
            icon={<Globe2 className="h-5 w-5 text-blue-400" />}
            name="All"
            count={totalClients}
            caption="clients total"
            pct={100}
            color="#3B82F6"
          />
          {countryStats.map((s) => {
            const m = metaFor(s.country)
            return (
              <CountryCard
                key={s.country}
                active={country === s.country}
                onClick={() => pickCountry(s.country)}
                icon={<span className="font-mono text-sm font-semibold text-slate-200">{m.code}</span>}
                name={s.country}
                count={s.count}
                caption={`${s.avg_completion_pct}% avg done`}
                pct={s.avg_completion_pct}
                color={m.color}
              />
            )
          })}
        </div>

        {analytics && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="rounded-xl border border-border bg-[#0B1628] p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium text-slate-200">
                  Completion trend{country !== 'all' && <span className="text-slate-500"> · {country}</span>}
                </div>
                <div className="text-xs text-slate-500">last 6 months</div>
              </div>
              <div className="mt-3 h-56">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics.completion_trend}>
                    <CartesianGrid stroke="#16233A" vertical={false} />
                    <XAxis dataKey="month" stroke="#64748B" tickLine={false} axisLine={false} fontSize={12} />
                    <YAxis stroke="#64748B" allowDecimals={false} tickLine={false} axisLine={false} fontSize={12} width={24} />
                    <Tooltip contentStyle={tooltipStyle} cursor={{ fill: '#16233A' }} />
                    <Bar
                      dataKey="completed"
                      fill={country === 'all' ? '#3B82F6' : metaFor(country).color}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-xl border border-border bg-[#0B1628] p-4">
              <div className="text-sm font-medium text-slate-200">Clients by country</div>
              <div className="mt-3 flex items-center gap-6">
                <div className="relative h-56 w-56 shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={countryStats}
                        dataKey="count"
                        nameKey="country"
                        innerRadius="62%"
                        outerRadius="95%"
                        stroke="#0B1628"
                        strokeWidth={2}
                        onClick={(d: any) => d?.country && pickCountry(d.country)}
                      >
                        {countryStats.map((s) => (
                          <Cell
                            key={s.country}
                            fill={metaFor(s.country).color}
                            opacity={country === 'all' || country === s.country ? 1 : 0.25}
                            className="cursor-pointer"
                          />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={tooltipStyle} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                    <div className="font-mono text-2xl">
                      {country === 'all' ? totalClients : countryStats.find((s) => s.country === country)?.count ?? 0}
                    </div>
                    <div className="text-xs text-slate-500">clients</div>
                  </div>
                </div>
                <ul className="flex-1 space-y-2 text-sm">
                  {countryStats.map((s) => (
                    <li key={s.country}>
                      <button
                        type="button"
                        onClick={() => pickCountry(s.country)}
                        className={`flex w-full items-center justify-between rounded px-2 py-1 hover:bg-white/5 ${
                          country === s.country ? 'bg-white/5' : ''
                        }`}
                      >
                        <span className="flex items-center gap-2 text-slate-300">
                          <span className="h-2 w-2 rounded-full" style={{ background: metaFor(s.country).color }} />
                          <span className="font-mono text-[10px] text-slate-500">{metaFor(s.country).code}</span>
                          {s.country}
                        </span>
                        <span className="font-mono text-slate-500">{s.count}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <div className="mt-6 flex flex-wrap items-center gap-2">
          <span className="text-xs text-slate-500 mr-1">{country === 'all' ? 'All countries' : country} ·</span>
          {STATUS_FILTERS.map((s) => (
            <button
              key={s.value}
              type="button"
              onClick={() => setStatus(s.value)}
              className={`rounded-full px-3 py-1 text-xs border ${
                status === s.value
                  ? 'border-primary bg-primary/15 text-blue-300'
                  : 'border-border text-slate-400 hover:text-slate-200'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        <div className="mt-3 rounded-xl border border-border bg-[#0B1628] overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-[11px] uppercase tracking-wider text-slate-500">
              <tr>
                <th className="px-4 py-3 w-10">
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
                    {clients.length === 0 ? 'No clients to show yet.' : 'No clients match these filters.'}
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const st = STATUS_STYLE[c.status] ?? { label: c.status, className: 'bg-slate-500/15 text-slate-400' }
                  const pct = Number(c.completion_pct) || 0
                  return (
                    <tr key={c.id} className="border-t border-border hover:bg-white/[0.02]">
                      <td className="px-4 py-3">
                        <input type="checkbox" checked={selected.has(c.id)} onChange={() => toggleSelect(c.id)} />
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium text-slate-100">{c.client_name}</div>
                        <div className="text-xs text-slate-500">{c.business_name}</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className="rounded border border-border px-2 py-0.5 text-xs text-slate-400">
                          {c.entity_type.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-slate-300">
                        <span className="mr-1 font-mono text-[10px] text-slate-500">{metaFor(c.country).code}</span>
                        {c.country}
                      </td>
                      <td className="px-4 py-3 w-48">
                        <div className="h-1.5 rounded bg-border overflow-hidden">
                          <div
                            className={`h-full ${pct >= 80 ? 'bg-emerald-500' : pct >= 30 ? 'bg-blue-500' : 'bg-amber-500'}`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <div className="text-xs text-slate-500 mt-1 font-mono">{pct}%</div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs ${st.className}`}>
                          <span className="h-1.5 w-1.5 rounded-full bg-current" />
                          {st.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right whitespace-nowrap space-x-3">
                        <Link className="text-blue-400 hover:text-blue-300" to={`/clients/${c.id}`}>
                          View
                        </Link>
                        <button
                          type="button"
                          className="text-slate-500 hover:text-slate-300"
                          onClick={() => {
                            void navigator.clipboard.writeText(c.portal_link)
                            toast.success('Portal link copied')
                          }}
                        >
                          Copy portal
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </main>

      {selected.size > 0 && (
        <div className="fixed bottom-0 inset-x-0 border-t border-border bg-[#0B1628]/95 backdrop-blur px-6 py-3 flex flex-wrap gap-3 items-center justify-between">
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

function CountryCard(props: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  name: string
  count: number
  caption: string
  pct: number
  color: string
}) {
  return (
    <button
      type="button"
      onClick={props.onClick}
      className={`w-36 shrink-0 rounded-xl border p-3 text-left transition-colors ${
        props.active ? 'border-blue-500 bg-blue-500/10' : 'border-border bg-[#0B1628] hover:border-slate-600'
      }`}
    >
      <div className="h-6 flex items-center">{props.icon}</div>
      <div className="mt-1 text-xs font-semibold text-slate-200">{props.name}</div>
      <div className="font-mono text-2xl text-slate-100">{props.count}</div>
      <div className="text-[11px] text-slate-500">{props.caption}</div>
      <div className="mt-2 h-1 rounded bg-border overflow-hidden">
        <div className="h-full rounded" style={{ width: `${Math.min(100, props.pct)}%`, background: props.color }} />
      </div>
    </button>
  )
}
