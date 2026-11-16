import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import { toast } from 'sonner'
import axios from 'axios'

const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export default function DocumentPortal() {
  const { firmSlug, token } = useParams()
  const [data, setData] = useState<any>(null)

  const load = useCallback(async () => {
    const res = await axios.get(`${apiBase}/api/portal/${firmSlug}/${token}`)
    setData(res.data)
  }, [firmSlug, token])

  useEffect(() => {
    load().catch(() => toast.error('Portal not found'))
  }, [load])

  const onDrop = useCallback(
    async (files: File[]) => {
      const file = files[0]
      if (!file) return
      const fd = new FormData()
      fd.append('file', file)
      try {
        toast.message('Verifying with AI…')
        const res = await axios.post(`${apiBase}/api/portal/${firmSlug}/${token}/upload`, fd, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        const { document_type, confidence, verified, issues, matched_item } = res.data
        if (verified) toast.success(`${document_type} verified`)
        else if (issues?.length) toast.error(`Issue: ${issues[0]}`)
        else toast.warning(`Uploaded (${document_type}, ${Math.round((confidence || 0) * 100)}%)`)
        if (matched_item) toast.message(`Matched checklist: ${matched_item}`)
        await load()
      } catch (e: any) {
        toast.error(e?.response?.data?.detail || 'Upload failed')
      }
    },
    [firmSlug, token, load],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, maxFiles: 1 })

  if (!data) return <div className="min-h-screen noise flex items-center justify-center text-slate-400">Loading…</div>

  const total = data.checklist_items?.length || 0
  const uploaded = data.checklist_items?.filter((i: any) => i.status !== 'pending').length || 0

  return (
    <div className="min-h-screen noise px-4 py-10 max-w-3xl mx-auto">
      <div className="rounded-2xl border border-border bg-card p-6">
        <div className="text-sm" style={{ color: data.firm_primary_color }}>
          {data.firm_name}
        </div>
        <h1 className="font-display text-2xl font-semibold mt-2">Welcome, {data.client_name}</h1>
        <div className="mt-4">
          <div className="text-sm text-slate-400">
            {uploaded} of {total} checklist rows updated
          </div>
          <div className="h-2 rounded bg-border overflow-hidden mt-2">
            <div className="h-full bg-primary" style={{ width: `${data.completion_pct}%` }} />
          </div>
        </div>

        <div className="mt-8 space-y-3">
          {data.checklist_items?.map((it: any) => (
            <div key={it.id} className="rounded-lg border border-border p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{it.item_name}</div>
                  <div className="text-xs text-slate-500 mt-1">{it.description}</div>
                </div>
                <div className="text-xs">{it.status}</div>
              </div>
            </div>
          ))}
        </div>

        <div
          {...getRootProps()}
          className={`mt-8 border border-dashed rounded-xl p-8 text-center cursor-pointer ${
            isDragActive ? 'border-primary bg-primary/5' : 'border-border'
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-sm text-slate-300">Drop a file here, or click to upload</div>
          <div className="text-xs text-slate-500 mt-1">PDF / images · max 20MB</div>
        </div>

        {data.firm_whatsapp_number && (
          <div className="text-xs text-slate-500 mt-6">Questions? WhatsApp us: {data.firm_whatsapp_number}</div>
        )}
      </div>
    </div>
  )
}
