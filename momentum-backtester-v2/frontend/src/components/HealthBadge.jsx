import { useEffect, useState } from 'react'

export default function HealthBadge() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then(setHealth)
      .catch((err) => setError(err.message))
  }, [])

  if (error) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-red-500/10 border border-red-500 text-red-400 px-3 py-1 text-sm">
        <span className="h-2 w-2 rounded-full bg-red-400" />
        API unreachable: {error}
      </span>
    )
  }

  if (!health) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-slate-700/50 border border-slate-600 text-slate-400 px-3 py-1 text-sm animate-pulse">
        <span className="h-2 w-2 rounded-full bg-slate-400" />
        Checking API…
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-green-500/10 border border-green-500 text-green-400 px-3 py-1 text-sm">
      <span className="h-2 w-2 rounded-full bg-green-400" />
      API {health.status}
    </span>
  )
}
