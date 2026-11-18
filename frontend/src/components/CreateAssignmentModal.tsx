import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import api from '../lib/api'
import type { CreateAssignmentPayload, ServiceCategory, AssignmentPriority } from '../types/assignment'

interface Client {
  id: string
  company_name: string
}

interface FirmUser {
  id: string
  full_name: string
  role: string
}

interface CreateAssignmentModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (assignmentId: string) => void
}

export function CreateAssignmentModal({ isOpen, onClose, onSuccess }: CreateAssignmentModalProps) {
  const [clients, setClients] = useState<Client[]>([])
  const [staff, setStaff] = useState<FirmUser[]>([])
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const [formData, setFormData] = useState<CreateAssignmentPayload>({
    client_id: '',
    assignment_name: '',
    service_category: 'GST',
    assignment_type: '',
    financial_year: '',
    due_date: '',
    priority: 'medium',
  })

  useEffect(() => {
    if (isOpen) {
      void loadClients()
      void loadStaff()
    }
  }, [isOpen])

  async function loadClients() {
    try {
      const res = await api.get('/api/clients', { params: { limit: 1000 } })
      setClients(res.data.clients || [])
    } catch (error) {
      console.error('Failed to load clients:', error)
    }
  }

  async function loadStaff() {
    try {
      const res = await api.get('/api/firm-users')
      setStaff(res.data || [])
    } catch (error) {
      console.error('Failed to load staff:', error)
    }
  }

  function validateForm(): boolean {
    const newErrors: Record<string, string> = {}

    if (!formData.client_id) newErrors.client_id = 'Client is required'
    if (!formData.assignment_name.trim()) newErrors.assignment_name = 'Assignment name is required'
    if (!formData.service_category) newErrors.service_category = 'Service category is required'
    if (!formData.assignment_type.trim()) newErrors.assignment_type = 'Assignment type is required'
    if (!formData.financial_year.trim()) newErrors.financial_year = 'Financial year is required'
    if (!formData.due_date) newErrors.due_date = 'Due date is required'

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!validateForm()) return

    setLoading(true)
    try {
      const res = await api.post('/api/assignments', formData)
      onSuccess(res.data.id)
      handleClose()
    } catch (error: any) {
      console.error('Failed to create assignment:', error)
      setErrors({ submit: error.response?.data?.detail || 'Failed to create assignment' })
    } finally {
      setLoading(false)
    }
  }

  function handleClose() {
    setFormData({
      client_id: '',
      assignment_name: '',
      service_category: 'GST',
      assignment_type: '',
      financial_year: '',
      due_date: '',
      priority: 'medium',
    })
    setErrors({})
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-2xl rounded-xl border border-border bg-[#0B1D33] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="text-xl font-bold text-white">Create New Assignment</h2>
          <button
            onClick={handleClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-white/5 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid gap-4">
            {/* Client Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Client <span className="text-red-400">*</span>
              </label>
              <select
                value={formData.client_id}
                onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
              >
                <option value="">Select client...</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.company_name}
                  </option>
                ))}
              </select>
              {errors.client_id && <p className="mt-1 text-xs text-red-400">{errors.client_id}</p>}
            </div>

            {/* Assignment Name */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Assignment Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                value={formData.assignment_name}
                onChange={(e) => setFormData({ ...formData, assignment_name: e.target.value })}
                placeholder="e.g., GST Return Filing for October 2024"
                className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none"
              />
              {errors.assignment_name && <p className="mt-1 text-xs text-red-400">{errors.assignment_name}</p>}
            </div>

            {/* Row: Service Category + Assignment Type */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Service Category <span className="text-red-400">*</span>
                </label>
                <select
                  value={formData.service_category}
                  onChange={(e) => setFormData({ ...formData, service_category: e.target.value as ServiceCategory })}
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
                >
                  <option value="GST">GST</option>
                  <option value="Income Tax">Income Tax</option>
                  <option value="TDS">TDS</option>
                  <option value="TCS">TCS</option>
                  <option value="MCA">MCA</option>
                  <option value="ROC">ROC</option>
                  <option value="Audit">Audit</option>
                  <option value="Accounting">Accounting</option>
                  <option value="Payroll">Payroll</option>
                  <option value="Advisory">Advisory</option>
                  <option value="Other">Other</option>
                </select>
                {errors.service_category && <p className="mt-1 text-xs text-red-400">{errors.service_category}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Assignment Type <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={formData.assignment_type}
                  onChange={(e) => setFormData({ ...formData, assignment_type: e.target.value })}
                  placeholder="e.g., GSTR-3B Filing"
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none"
                />
                {errors.assignment_type && <p className="mt-1 text-xs text-red-400">{errors.assignment_type}</p>}
              </div>
            </div>

            {/* Row: Financial Year + Priority */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Financial Year <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={formData.financial_year}
                  onChange={(e) => setFormData({ ...formData, financial_year: e.target.value })}
                  placeholder="e.g., FY 2024-25"
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none"
                />
                {errors.financial_year && <p className="mt-1 text-xs text-red-400">{errors.financial_year}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Priority <span className="text-red-400">*</span>
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as AssignmentPriority })}
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            {/* Row: Start Date + Due Date */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Start Date
                </label>
                <input
                  type="date"
                  value={formData.start_date || ''}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">
                  Due Date <span className="text-red-400">*</span>
                </label>
                <input
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
                />
                {errors.due_date && <p className="mt-1 text-xs text-red-400">{errors.due_date}</p>}
              </div>
            </div>

            {/* Staff Assignment */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Assign to Staff
              </label>
              <select
                value={formData.assigned_staff || ''}
                onChange={(e) => setFormData({ ...formData, assigned_staff: e.target.value || undefined })}
                className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white focus:border-[#C9A227] focus:outline-none"
              >
                <option value="">Unassigned</option>
                {staff.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.full_name} - {user.role}
                  </option>
                ))}
              </select>
            </div>

            {/* Estimated Hours */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Estimated Hours
              </label>
              <input
                type="number"
                min="0"
                step="0.5"
                value={formData.estimated_hours || ''}
                onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value ? parseFloat(e.target.value) : undefined })}
                placeholder="e.g., 8"
                className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Description
              </label>
              <textarea
                value={formData.description || ''}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Add any additional details or instructions..."
                rows={3}
                className="w-full rounded-lg border border-border bg-[#07101F] px-4 py-2 text-sm text-white placeholder:text-slate-500 focus:border-[#C9A227] focus:outline-none resize-none"
              />
            </div>

            {/* Error Message */}
            {errors.submit && (
              <div className="rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
                {errors.submit}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-slate-300 hover:bg-white/5 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-[#C9A227] px-4 py-2 text-sm font-medium text-white hover:bg-[#D4B03A] disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Assignment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
