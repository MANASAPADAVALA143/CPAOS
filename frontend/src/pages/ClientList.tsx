import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'sonner'
import api from '../lib/api'
import { CountryFlag } from '../components/CountryFlag'

type ClientRow = {
  id: string
  client_name: string
  business_name?: string | null
  country: string
  entity_type: string
  status: string
  completion_pct: number
}

export default function ClientList() {
  const [rows, setRows] = useState<ClientRow[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())

  async function load() {
    try {
      const r = await api.get('/api/clients')
      setRows(r.data)
    } catch {
      setRows([])
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const allSelected = rows.length > 0 && rows.every((c) => selected.has(c.id))

  const selectedRows = useMemo(() => rows.filter((c) => selected.has(c.id)), [rows, selected])

  function toggle(id: string) {
    setSelected((prev) => {
      const n = new Set(prev)
      if (n.has(id)) n.delete(id)
      else n.add(id)
      return n
    })
  }

  function toggleAll() {
    if (allSelected) setSelected(new Set())
    else setSelected(new Set(rows.map((r) => r.id)))
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

  return (
    <div className="min-h-screen noise px-6 py-8 max-w-5xl mx-auto pb-24">
      <Link to="/dashboard" className="text-sm text-primary">
        ← Dashboard
      </Link>
      <div className="flex items-center justify-between gap-3 flex-wrap mt-4">
        <h1 className="font-display text-2xl font-semibold">Clients</h1>
        <label className="flex items-center gap-2 text-xs text-slate-400">
          <input type="checkbox" checked={allSelected} onChange={toggleAll} />
          Select all
        </label>
      </div>
      <div className="mt-6 space-y-2">
        {rows.map((c) => (
          <div
            key={c.id}
            className="flex gap-3 items-stretch rounded-xl border border-border bg-card p-4 hover:border-primary/40"
          >
            <div className="flex items-start pt-1">
              <input type="checkbox" checked={selected.has(c.id)} onChange={() => toggle(c.id)} />
            </div>
            <Link to={`/clients/${c.id}`} className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{c.client_name}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    <CountryFlag country={c.country} />
                    {c.country} · {c.entity_type}
                  </div>
                </div>
                <div className="text-sm text-slate-300">{c.completion_pct}%</div>
              </div>
              <div className="text-xs text-slate-500 mt-2">{c.status}</div>
            </Link>
          </div>
        ))}
      </div>

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
