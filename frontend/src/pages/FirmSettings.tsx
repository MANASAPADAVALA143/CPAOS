import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import QRCode from 'qrcode'
import * as Tabs from '@radix-ui/react-tabs'
import { toast } from 'sonner'
import { useFirm } from '../hooks/useFirm'

export default function FirmSettings() {
  const { data } = useFirm()
  const [qr, setQr] = useState<string | null>(null)
  const slug = data?.firm.slug || ''
  const selfUrl = `${window.location.origin}/onboard/${slug}`

  useEffect(() => {
    if (!slug) return
    let cancelled = false
    QRCode.toDataURL(selfUrl, { margin: 1, width: 220, color: { dark: '#0f172a', light: '#ffffff' } })
      .then((url) => {
        if (!cancelled) setQr(url)
      })
      .catch(() => setQr(null))
    return () => {
      cancelled = true
    }
  }, [selfUrl, slug])

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(selfUrl)
      toast.success('Link copied')
    } catch {
      toast.error('Could not copy')
    }
  }

  return (
    <div className="min-h-screen noise px-6 py-8 max-w-4xl mx-auto">
      <Link to="/dashboard" className="text-sm text-primary">
        ← Dashboard
      </Link>
      <h1 className="font-display text-2xl font-semibold mt-4">Firm settings</h1>

      <Tabs.Root defaultValue="profile" className="mt-6">
        <Tabs.List className="flex gap-2 border-b border-border pb-2">
          {['profile', 'team', 'integrations', 'plan'].map((t) => (
            <Tabs.Trigger
              key={t}
              value={t}
              className="rounded-lg px-3 py-1.5 text-sm text-slate-300 data-[state=active]:bg-card data-[state=active]:border data-[state=active]:border-border"
            >
              {t[0].toUpperCase() + t.slice(1)}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        <Tabs.Content value="profile" className="mt-4 rounded-xl border border-border bg-card p-4 text-sm text-slate-300 space-y-3">
          <div>Firm: {data?.firm.name}</div>
          <div>Plan: {data?.firm.plan}</div>
          <div className="pt-4 border-t border-border">
            <div className="text-xs text-slate-400 mb-1">Your self-registration link</div>
            <div className="flex flex-wrap gap-2 items-center">
              <code className="text-xs break-all rounded bg-bg px-2 py-1 border border-border flex-1 min-w-[200px]">{selfUrl}</code>
              <button type="button" className="rounded-lg bg-primary px-3 py-1.5 text-xs text-white" onClick={copyLink}>
                Copy link
              </button>
            </div>
            <p className="text-xs text-slate-500 mt-2">Share this URL with new clients so they can start onboarding without staff creating the record first.</p>
            {qr ? (
              <div className="mt-4">
                <div className="text-xs text-slate-400 mb-2">QR code</div>
                <img src={qr} alt="Self-registration QR" className="rounded-lg border border-border bg-white p-2 max-w-[240px]" />
              </div>
            ) : null}
          </div>
        </Tabs.Content>
        <Tabs.Content value="team" className="mt-4 text-sm text-slate-400">
          Invite staff via <code className="font-mono">POST /api/firm/invite-user</code>
        </Tabs.Content>
        <Tabs.Content value="integrations" className="mt-4 text-sm text-slate-400">
          Configure n8n, Twilio, DocuSign, Resend, Slack, and VAPI secrets in your host environment variables.
        </Tabs.Content>
        <Tabs.Content value="plan" className="mt-4 text-sm text-slate-400">
          Upgrade path can be wired to Stripe later.
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
