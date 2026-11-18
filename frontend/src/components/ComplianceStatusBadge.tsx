import type { ComplianceStatus } from '../types/compliance'

interface Props {
  status: ComplianceStatus
}

const STATUS_STYLES: Record<ComplianceStatus, { label: string; className: string }> = {
  pending: {
    label: 'Pending',
    className: 'bg-slate-500/15 text-slate-300',
  },
  in_progress: {
    label: 'In Progress',
    className: 'bg-blue-500/15 text-blue-300',
  },
  completed: {
    label: 'Completed',
    className: 'bg-emerald-500/15 text-emerald-300',
  },
  overdue: {
    label: 'Overdue',
    className: 'bg-red-500/15 text-red-400',
  },
  not_applicable: {
    label: 'N/A',
    className: 'bg-gray-500/15 text-gray-400',
  },
}

export function ComplianceStatusBadge({ status }: Props) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.pending

  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${style.className}`}
    >
      {style.label}
    </span>
  )
}
