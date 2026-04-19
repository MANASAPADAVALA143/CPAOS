import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import * as Tabs from '@radix-ui/react-tabs'
import api from '../lib/api'
import { ChecklistPanel, ChecklistRow } from '../components/ChecklistPanel'
import { DocumentViewer } from '../components/DocumentViewer'
import { WhatsAppLog, Msg } from '../components/WhatsAppLog'
import { SignatureStatus } from '../components/SignatureStatus'
import { CountryFlag } from '../components/CountryFlag'

type DocRow = {
  id: string
  filename: string
  original_filename: string
  uploaded_at: string
  ai_document_type?: string | null
  ai_confidence?: number | null
  review_status: string
  signed_url?: string | null
}

type ActivityRow = { id: string; action: string; description: string; created_at: string }

export default function ClientDetail() {
  const { id } = useParams()
  const [client, setClient] = useState<any>(null)
  const [checklist, setChecklist] = useState<ChecklistRow[]>([])
  const [docs, setDocs] = useState<DocRow[]>([])
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [activity, setActivity] = useState<ActivityRow[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [preview, setPreview] = useState<{ url: string; mime?: string } | null>(null)

  const selectedItem = useMemo(
    () => checklist.find((c) => c.id === selected) || null,
    [checklist, selected],
  )

  async function load() {
    const [c, ch, d, m, a] = await Promise.all([
      api.get(`/api/clients/${id}`),
      api.get(`/api/clients/${id}/checklist`),
      api.get(`/api/clients/${id}/documents`),
      api.get(`/api/clients/${id}/messages`),
      api.get(`/api/clients/${id}/activity`),
    ])
    setClient(c.data)
    setChecklist(ch.data)
    setDocs(d.data)
    setMsgs(m.data)
    setActivity(a.data)
    if (ch.data[0]) setSelected(ch.data[0].id)
  }

  useEffect(() => {
    if (!id) return
    load().catch(() => toast.error('Failed to load client'))
  }, [id])

  useEffect(() => {
    if (!selected) return
    const item = checklist.find((i) => i.id === selected)
    const doc = item?.document_id ? docs.find((d) => d.id === item.document_id) : undefined
    if (doc?.signed_url) setPreview({ url: doc.signed_url, mime: doc.filename.toLowerCase().endsWith('.pdf') ? 'application/pdf' : undefined })
    else setPreview(null)
  }, [selected, checklist, docs])

  if (!client) return <div className="p-8 text-slate-400">Loading…</div>

  return (
    <div className="min-h-screen noise px-6 py-8 max-w-6xl mx-auto">
      <Link to="/dashboard" className="text-sm text-primary">
        ← Dashboard
      </Link>
      <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold">{client.client_name}</h1>
          <div className="text-sm text-slate-400">{client.business_name}</div>
          <div className="mt-2 text-sm">
            <CountryFlag country={client.country} />
            {client.country} · <span className="rounded-full bg-border px-2 py-0.5 text-xs">{client.entity_type}</span>{' '}
            · <span className="rounded-full bg-border px-2 py-0.5 text-xs">{client.status}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="rounded-lg border border-border px-3 py-2 text-sm"
            onClick={() => navigator.clipboard.writeText(client.portal_link).then(() => toast.success('Copied'))}
          >
            Copy portal link
          </button>
          <a className="rounded-lg bg-primary px-3 py-2 text-sm text-white" href={client.portal_link} target="_blank" rel="noreferrer">
            View portal
          </a>
        </div>
      </div>

      <Tabs.Root defaultValue="checklist" className="mt-8">
        <Tabs.List className="flex flex-wrap gap-2 border-b border-border pb-2">
          {['checklist', 'documents', 'messages', 'activity', 'signature'].map((t) => (
            <Tabs.Trigger
              key={t}
              value={t}
              className="rounded-lg px-3 py-1.5 text-sm text-slate-300 data-[state=active]:bg-card data-[state=active]:border data-[state=active]:border-border"
            >
              {t[0].toUpperCase() + t.slice(1)}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="checklist" className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-2 rounded-xl border border-border bg-card p-4">
            <ChecklistPanel items={checklist} selectedId={selected} onSelect={setSelected} />
          </div>
          <div className="md:col-span-3 rounded-xl border border-border bg-card p-4">
            {!selectedItem && <div className="text-slate-400">Select an item</div>}
            {selectedItem && (
              <div>
                <div className="font-medium">{selectedItem.item_name}</div>
                <div className="text-sm text-slate-400 mt-1">{selectedItem.description}</div>
                <div className="mt-4">
                  {preview ? (
                    <DocumentViewer url={preview.url} mime={preview.mime} />
                  ) : (
                    <div className="text-slate-400 text-sm">No document uploaded yet</div>
                  )}
                </div>
              </div>
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content value="documents" className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          {docs.map((d) => (
            <div key={d.id} className="rounded-xl border border-border bg-card p-4">
              <div className="font-medium text-sm">{d.original_filename}</div>
              <div className="text-xs text-slate-500 mt-1">{new Date(d.uploaded_at).toLocaleString()}</div>
              <div className="text-xs mt-2">
                AI: {d.ai_document_type} ({Math.round((d.ai_confidence || 0) * 100)}%)
              </div>
              <div className="mt-3 flex gap-2">
                {d.signed_url && (
                  <a className="text-primary text-sm" href={d.signed_url} target="_blank" rel="noreferrer">
                    View
                  </a>
                )}
              </div>
            </div>
          ))}
        </Tabs.Content>

        <Tabs.Content value="messages" className="mt-4">
          <WhatsAppLog rows={msgs} />
        </Tabs.Content>

        <Tabs.Content value="activity" className="mt-4 space-y-3">
          {activity.map((a) => (
            <div key={a.id} className="rounded-lg border border-border bg-card p-3 text-sm">
              <div className="text-xs text-slate-500">{new Date(a.created_at).toLocaleString()}</div>
              <div className="mt-1">{a.description}</div>
            </div>
          ))}
        </Tabs.Content>

        <Tabs.Content value="signature" className="mt-4">
          <SignatureStatus sent={client.engagement_letter_sent} signed={client.engagement_letter_signed} envelopeId={client.signature_envelope_id} />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
