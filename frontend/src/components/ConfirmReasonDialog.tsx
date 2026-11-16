import { useEffect, useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'

export function ConfirmReasonDialog({
  open,
  title,
  description,
  placeholder,
  confirmLabel,
  tone = 'neutral',
  busy = false,
  onCancel,
  onConfirm,
}: {
  open: boolean
  title: string
  description?: string
  placeholder?: string
  confirmLabel: string
  tone?: 'danger' | 'neutral'
  busy?: boolean
  onCancel: () => void
  onConfirm: (reason: string) => void
}) {
  const [reason, setReason] = useState('')

  useEffect(() => {
    if (open) setReason('')
  }, [open])

  const trimmed = reason.trim()
  const confirmClass =
    tone === 'danger'
      ? 'bg-red-600 text-white hover:bg-red-500'
      : 'bg-primary text-white hover:bg-blue-500'

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        if (!next && !busy) onCancel()
      }}
    >
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[92vw] max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-card p-5 shadow-xl">
          <Dialog.Title className="font-medium">{title}</Dialog.Title>
          {description && (
            <Dialog.Description className="mt-1 text-sm text-slate-400">{description}</Dialog.Description>
          )}
          <form
            className="mt-4"
            onSubmit={(e) => {
              e.preventDefault()
              if (trimmed && !busy) onConfirm(trimmed)
            }}
          >
            <label className="block text-xs text-slate-400">
              Reason <span className="text-red-400">*</span>
              <textarea
                autoFocus
                required
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={placeholder}
                disabled={busy}
                className="mt-1 w-full rounded-lg border border-border bg-transparent px-3 py-2 text-sm text-slate-100 focus:border-primary focus:outline-none"
              />
            </label>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={onCancel}
                disabled={busy}
                className="rounded-lg border border-border px-3 py-1.5 text-sm text-slate-300 hover:bg-white/5 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!trimmed || busy}
                className={`rounded-lg px-3 py-1.5 text-sm disabled:cursor-not-allowed disabled:opacity-50 ${confirmClass}`}
              >
                {busy ? 'Saving…' : confirmLabel}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
