import { useEffect, useState } from 'react'

export default function App() {
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

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        <h1 className="text-3xl font-bold text-white mb-2">
          Momentum Backtester
        </h1>
        <p className="text-slate-400 mb-6">Backend connection check</p>

        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500 text-red-400 px-4 py-3">
            Failed to reach the API: {error}
            <p className="mt-1 text-sm text-red-300">
              Is the backend running on port 8000?
            </p>
          </div>
        )}

        {!error && !health && (
          <div className="text-slate-400 animate-pulse">
            Checking API status…
          </div>
        )}

        {health && (
          <div className="rounded-lg bg-green-500/10 border border-green-500 text-green-400 px-4 py-3">
            <span className="font-semibold">API status:</span> {health.status}
          </div>
        )}
      </div>
    </div>
  )
}
