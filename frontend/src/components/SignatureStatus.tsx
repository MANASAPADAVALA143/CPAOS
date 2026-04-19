export function SignatureStatus({
  sent,
  signed,
  envelopeId,
}: {
  sent: boolean
  signed: boolean
  envelopeId?: string | null
}) {
  let label = 'Not sent'
  if (signed) label = 'Signed'
  else if (sent) label = 'Pending signature'
  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="text-sm text-slate-400">Engagement letter</div>
      <div className="text-lg font-display mt-1">{label}</div>
      {envelopeId && <div className="text-xs font-mono text-slate-500 mt-2">Envelope: {envelopeId}</div>}
    </div>
  )
}
