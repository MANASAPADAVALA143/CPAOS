export type ChecklistRow = {
  id: string
  category: string
  item_name: string
  status: string
  description?: string
  document_id?: string | null
}

export function ChecklistPanel({
  items,
  selectedId,
  onSelect,
}: {
  items: ChecklistRow[]
  selectedId: string | null
  onSelect: (id: string) => void
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
              <button
                key={it.id}
                type="button"
                onClick={() => onSelect(it.id)}
                className={`w-full text-left rounded-lg border px-3 py-2 text-sm ${
                  selectedId === it.id ? 'border-primary bg-primary/10' : 'border-border bg-card'
                }`}
              >
                <span className="mr-2">
                  {it.status === 'verified' && '✅'}
                  {it.status === 'uploaded' && '⏳'}
                  {it.status === 'pending' && '❌'}
                  {it.status === 'rejected' && '⚠️'}
                  {it.status === 'waived' && '◯'}
                </span>
                {it.item_name}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
