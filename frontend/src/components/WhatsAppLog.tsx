export type Msg = {
  id: string
  channel: string
  message_type: string
  status: string
  sent_at: string
}

export function WhatsAppLog({ rows }: { rows: Msg[] }) {
  if (!rows.length) return <div className="text-slate-400">No messages yet.</div>
  return (
    <div className="space-y-3">
      {rows.map((m) => (
        <div key={m.id} className="rounded-lg border border-border bg-card p-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs text-slate-400">{new Date(m.sent_at).toLocaleString()}</span>
            <span className="rounded-full bg-border px-2 py-0.5 text-xs">
              {m.channel === 'whatsapp' ? 'WhatsApp 💬' : 'SMS 📱'}
            </span>
          </div>
          <div className="mt-1">{m.message_type}</div>
          <div className="text-xs text-slate-400 mt-1">Status: {m.status}</div>
        </div>
      ))}
    </div>
  )
}
