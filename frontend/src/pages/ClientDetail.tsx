import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import * as Tabs from '@radix-ui/react-tabs'
import api from '../lib/api'
import { ChecklistPanel, ChecklistRow } from '../components/ChecklistPanel'
import { DocumentViewer } from '../components/DocumentViewer'
import { WhatsAppLog, Msg } from '../components/WhatsAppLog'
import { SignatureStatus } from '../components/SignatureStatus'
import { CountryFlag } from '../components/CountryFlag'
import { ConfirmReasonDialog } from '../components/ConfirmReasonDialog'

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

type ReasonDialogState =
  | { kind: 'reject'; docId: string; label: string }
  | { kind: 'waive'; itemId: string; label: string }
  | null

const STATUS_BADGE: Record<string, string> = {
  approved: 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300',
  verified: 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300',
  rejected: 'border-red-500/40 bg-red-500/15 text-red-300',
  waived: 'border-slate-500/40 bg-slate-500/15 text-slate-300',
  uploaded: 'border-blue-500/40 bg-blue-500/15 text-blue-300',
  pending: 'border-amber-500/40 bg-amber-500/15 text-amber-300',
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`rounded-full border px-2 py-0.5 text-xs capitalize ${STATUS_BADGE[status] ?? STATUS_BADGE.pending}`}>
      {status}
    </span>
  )
}

const ACTION_TONE = {
  approve: 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/25',
  reject: 'border-red-500/40 bg-red-500/15 text-red-300 hover:bg-red-500/25',
  waive: 'border-border text-slate-300 hover:bg-white/5',
}

function ActionButton({
  tone,
  busy,
  disabled,
  onClick,
  children,
}: {
  tone: keyof typeof ACTION_TONE
  busy: boolean
  disabled: boolean
  onClick: () => void
  children: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-busy={busy}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50 ${ACTION_TONE[tone]}`}
    >
      {busy && <span className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />}
      {busy ? `${children}…` : children}
    </button>
  )
}

export default function ClientDetail() {
  const { id } = useParams()
  const [client, setClient] = useState<any>(null)
  const [checklist, setChecklist] = useState<ChecklistRow[]>([])
  const [docs, setDocs] = useState<DocRow[]>([])
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [activity, setActivity] = useState<ActivityRow[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [preview, setPreview] = useState<{ url: string; mime?: string } | null>(null)
  const [busyAction, setBusyAction] = useState<string | null>(null)
  const [reasonDialog, setReasonDialog] = useState<ReasonDialogState>(null)
  const inFlight = useRef(false)

  const selectedItem = useMemo(
    () => checklist.find((c) => c.id === selected) || null,
    [checklist, selected],
  )

  function applyChecklist(rows: ChecklistRow[]) {
    setChecklist(rows)
    setSelected((cur) => (cur && rows.some((r) => r.id === cur) ? cur : rows[0]?.id ?? null))
  }

  async function load() {
    const [c, ch, d, m, a] = await Promise.all([
      api.get(`/api/clients/${id}`),
      api.get(`/api/clients/${id}/checklist`),
      api.get(`/api/clients/${id}/documents`),
      api.get(`/api/clients/${id}/messages`),
      api.get(`/api/clients/${id}/activity`),
    ])
    setClient(c.data)
    applyChecklist(ch.data)
    setDocs(d.data)
    setMsgs(m.data)
    setActivity(a.data)
  }

  async function refresh() {
    const [c, ch, d, a] = await Promise.all([
      api.get(`/api/clients/${id}`),
      api.get(`/api/clients/${id}/checklist`),
      api.get(`/api/clients/${id}/documents`),
      api.get(`/api/clients/${id}/activity`),
    ])
    setClient(c.data)
    applyChecklist(ch.data)
    setDocs(d.data)
    setActivity(a.data)
  }

  async function runAction(key: string, request: () => Promise<unknown>, successMessage: string): Promise<boolean> {
    if (inFlight.current) return false
    inFlight.current = true
    setBusyAction(key)
    try {
      await request()
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Action failed')
      inFlight.current = false
      setBusyAction(null)
      return false
    }
    try {
      await refresh()
      toast.success(successMessage)
    } catch {
      toast.error(`${successMessage}, but refreshing the page data failed`)
    } finally {
      inFlight.current = false
      setBusyAction(null)
    }
    return true
  }

  function approveDoc(docId: string) {
    void runAction(
      `approve:${docId}`,
      () => api.post(`/api/documents/${docId}/verify`, { action: 'approved' }),
      'Document approved',
    )
  }

  async function confirmReason(reason: string) {
    if (!reasonDialog) return
    const ok =
      reasonDialog.kind === 'reject'
        ? await runAction(
            `reject:${reasonDialog.docId}`,
            () =>
              api.post(`/api/documents/${reasonDialog.docId}/verify`, {
                action: 'rejected',
                rejection_reason: reason,
              }),
            'Document rejected',
          )
        : await runAction(
            `waive:${reasonDialog.itemId}`,
            () => api.patch(`/api/clients/${id}/checklist-items/${reasonDialog.itemId}`, { reason }),
            'Checklist item waived',
          )
    if (ok) setReasonDialog(null)
  }

  const dialogBusy =
    reasonDialog != null &&
    busyAction === (reasonDialog.kind === 'reject' ? `reject:${reasonDialog.docId}` : `waive:${reasonDialog.itemId}`)

  useEffect(() => {
    if (!id) return
    load().catch(() => toast.error('Failed to load client'))
  }, [id])

  async function updateExpiry(itemId: string, expiry: string | null) {
    const previous = checklist.find((i) => i.id === itemId)?.expiry_date ?? null
    setChecklist((rows) => rows.map((r) => (r.id === itemId ? { ...r, expiry_date: expiry } : r)))
    try {
      await api.patch(`/api/checklist/${itemId}/expiry`, { expiry_date: expiry })
      toast.success(expiry ? 'Expiry date saved' : 'Expiry date cleared')
    } catch (e: any) {
      setChecklist((rows) => rows.map((r) => (r.id === itemId ? { ...r, expiry_date: previous } : r)))
      toast.error(e?.response?.data?.detail || 'Failed to save expiry date')
    }
  }

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
            <ChecklistPanel
              items={checklist}
              selectedId={selected}
              onSelect={setSelected}
              onExpiryChange={updateExpiry}
            />
          </div>
          <div className="md:col-span-3 rounded-xl border border-border bg-card p-4">
            {!selectedItem && <div className="text-slate-400">Select an item</div>}
            {selectedItem && (
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="font-medium">{selectedItem.item_name}</div>
                  <StatusBadge status={selectedItem.status} />
                </div>
                <div className="text-sm text-slate-400 mt-1">{selectedItem.description}</div>
                {(() => {
                  const item = selectedItem
                  const canReview = item.status === 'uploaded' && Boolean(item.document_id)
                  const canWaive = canReview || item.status === 'pending' || item.status === 'rejected'
                  if (!canWaive) return null
                  const docId = item.document_id ?? ''
                  return (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {canReview && (
                        <>
                          <ActionButton
                            tone="approve"
                            busy={busyAction === `approve:${docId}`}
                            disabled={busyAction !== null}
                            onClick={() => approveDoc(docId)}
                          >
                            Approve
                          </ActionButton>
                          <ActionButton
                            tone="reject"
                            busy={busyAction === `reject:${docId}`}
                            disabled={busyAction !== null}
                            onClick={() => setReasonDialog({ kind: 'reject', docId, label: item.item_name })}
                          >
                            Reject
                          </ActionButton>
                        </>
                      )}
                      <ActionButton
                        tone="waive"
                        busy={busyAction === `waive:${item.id}`}
                        disabled={busyAction !== null}
                        onClick={() => setReasonDialog({ kind: 'waive', itemId: item.id, label: item.item_name })}
                      >
                        Waive
                      </ActionButton>
                    </div>
                  )
                })()}
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
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {d.signed_url && (
                  <a className="text-primary text-sm mr-1" href={d.signed_url} target="_blank" rel="noreferrer">
                    View
                  </a>
                )}
                {d.review_status === 'pending' ? (
                  <>
                    <ActionButton
                      tone="approve"
                      busy={busyAction === `approve:${d.id}`}
                      disabled={busyAction !== null}
                      onClick={() => approveDoc(d.id)}
                    >
                      Approve
                    </ActionButton>
                    <ActionButton
                      tone="reject"
                      busy={busyAction === `reject:${d.id}`}
                      disabled={busyAction !== null}
                      onClick={() => setReasonDialog({ kind: 'reject', docId: d.id, label: d.original_filename })}
                    >
                      Reject
                    </ActionButton>
                  </>
                ) : (
                  <StatusBadge status={d.review_status} />
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

      <ConfirmReasonDialog
        open={reasonDialog !== null}
        title={reasonDialog?.kind === 'waive' ? 'Waive checklist item' : 'Reject document'}
        description={
          reasonDialog?.kind === 'waive'
            ? `"${reasonDialog.label}" will no longer be required from the client.`
            : reasonDialog
              ? `"${reasonDialog.label}" will be marked as rejected.`
              : undefined
        }
        placeholder={
          reasonDialog?.kind === 'waive' ? 'e.g. Not applicable for this entity type' : 'e.g. Image is blurry, please re-upload'
        }
        confirmLabel={reasonDialog?.kind === 'waive' ? 'Waive item' : 'Reject document'}
        tone={reasonDialog?.kind === 'waive' ? 'neutral' : 'danger'}
        busy={dialogBusy}
        onCancel={() => setReasonDialog(null)}
        onConfirm={(reason) => void confirmReason(reason)}
      />
    </div>
  )
}
