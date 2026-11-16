import { useEffect, useState } from 'react'
import api from '../lib/api'

export function useFirm() {
  const [data, setData] = useState<{
    user: { full_name: string; email: string; role: string }
    firm: { name: string; slug: string; plan: string }
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await api.get('/api/auth/me')
        if (!cancelled) setData(res.data)
      } catch {
        if (!cancelled) setData(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return { data, loading }
}
