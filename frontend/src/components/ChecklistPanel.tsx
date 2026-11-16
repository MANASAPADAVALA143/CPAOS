export type ChecklistRow = {
  id: string
  category: string
  item_name: string
  status: string
  description?: string
  document_id?: string | null
  expiry_date?: string | null
}

const EXPIRY_WINDOW_DAYS = 30

function daysUntil(isoDate: string): number {
  const [y, m, d] = isoDate.split('-').map(Number)
  const target = new Date(y, m - 1, d)
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  return Math.round((target.getTime() - today.getTime()) / 86_400_000)
}

function expiryInputClass(expiry?: string | null): string {
  if (!expiry) return 'border-border'
  const days = daysUntil(expiry)
  if (days < 0) return 'border-red-500 text-red-400'
  if (days <= EXPIRY_WINDOW_DAYS) return 'border-amber-500 text-amber-400'
  return 'border-border'
}

export function ChecklistPanel({
  items,
  selectedId,
  onSelect,
  onExpiryChange,
}: {
  items: ChecklistRow[]
  selectedId: string | null
  onSelect: (id: string) => void
  onExpiryChange?: (id: string, expiry: string | null) => void
}) {
  const grouped = items.reduce<Record<string, ChecklistRow[]>>((acc, it) => {
    acc[it.category] = acc[it.category] || []
    acc[it.category].push(it)
    return acc
  }, {})
  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([cat, list]) => (
        <div key={cat}>
          <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">{cat}</div>
          <div className="space-y-1">
            {list.map((it) => (
              <div
                key={it.id}
                className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
                  selectedId === it.id ? 'border-primary bg-primary/10' : 'border-border bg-card'
                }`}
              >
                <button type="button" onClick={() => onSelect(it.id)} className="flex-1 min-w-0 text-left">
                  <span className="mr-2">
                    {it.status === 'verified' && '✅'}
                    {it.status === 'uploaded' && '⏳'}
                    {it.status === 'pending' && '❌'}
                    {it.status === 'rejected' && '⚠️'}
                    {it.status === 'waived' && '◯'}
                  </span>
                  {it.item_name}
                </button>
                {it.document_id && onExpiryChange && (
                  <label className="flex items-center gap-1 text-xs text-slate-400 shrink-0">
                    Expiry Date
                    <input
                      type="date"
                      aria-label={`Expiry date for ${it.item_name}`}
                      value={it.expiry_date ?? ''}
                      onChange={(e) => onExpiryChange(it.id, e.target.value || null)}
                      className={`rounded border bg-transparent px-1 py-0.5 text-xs ${expiryInputClass(it.expiry_date)}`}
                    />
                  </label>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
