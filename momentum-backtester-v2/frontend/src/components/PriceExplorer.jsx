import { useState } from 'react'

const today = () => new Date().toISOString().slice(0, 10)
const oneYearAgo = () => {
  const d = new Date()
  d.setFullYear(d.getFullYear() - 1)
  return d.toISOString().slice(0, 10)
}

const inputClass =
  'w-full rounded-lg bg-slate-900 border border-slate-600 text-slate-200 px-3 py-2 text-sm focus:outline-none focus:border-sky-500'

export default function PriceExplorer() {
  const [symbol, setSymbol] = useState('AAPL')
  const [start, setStart] = useState(oneYearAgo())
  const [end, setEnd] = useState(today())
  const [interval, setInterval] = useState('1d')
  const [history, setHistory] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  async function loadPrices(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setHistory(null)
    try {
      const params = new URLSearchParams({ start, end, interval })
      const res = await fetch(
        `/api/prices/${encodeURIComponent(symbol.trim())}?${params}`,
      )
      const body = await res.json()
      if (!res.ok) throw new Error(body.detail || `HTTP ${res.status}`)
      setHistory(body)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const lastBars = history ? history.bars.slice(-10) : []

  return (
    <div className="bg-slate-800 rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Price data</h2>

      <form onSubmit={loadPrices} className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-4">
        <label className="block col-span-2 sm:col-span-1">
          <span className="block text-xs text-slate-400 mb-1">Symbol</span>
          <input
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className={inputClass}
            placeholder="AAPL"
            required
          />
        </label>
        <label className="block">
          <span className="block text-xs text-slate-400 mb-1">Start</span>
          <input type="date" value={start} onChange={(e) => setStart(e.target.value)} className={inputClass} />
        </label>
        <label className="block">
          <span className="block text-xs text-slate-400 mb-1">End</span>
          <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} className={inputClass} />
        </label>
        <label className="block">
          <span className="block text-xs text-slate-400 mb-1">Interval</span>
          <select value={interval} onChange={(e) => setInterval(e.target.value)} className={inputClass}>
            <option value="1d">Daily</option>
            <option value="1wk">Weekly</option>
            <option value="1mo">Monthly</option>
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white font-medium px-4 py-2 text-sm"
          >
            {loading ? 'Loading…' : 'Load'}
          </button>
        </div>
      </form>

      {error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500 text-red-400 px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {history && (
        <>
          <p className="text-sm text-slate-400 mb-3">
            {history.count} bars for{' '}
            <span className="text-slate-200 font-medium">{history.symbol}</span>{' '}
            ({history.start} → {history.end}, {history.interval}). Showing last{' '}
            {lastBars.length}.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="text-slate-400 border-b border-slate-700">
                  <th className="py-2 pr-4 font-medium">Date</th>
                  <th className="py-2 pr-4 font-medium text-right">Open</th>
                  <th className="py-2 pr-4 font-medium text-right">High</th>
                  <th className="py-2 pr-4 font-medium text-right">Low</th>
                  <th className="py-2 pr-4 font-medium text-right">Close</th>
                  <th className="py-2 font-medium text-right">Volume</th>
                </tr>
              </thead>
              <tbody>
                {lastBars.map((bar) => (
                  <tr key={bar.date} className="border-b border-slate-700/50 text-slate-300">
                    <td className="py-2 pr-4">{bar.date}</td>
                    <td className="py-2 pr-4 text-right">{bar.open.toFixed(2)}</td>
                    <td className="py-2 pr-4 text-right">{bar.high.toFixed(2)}</td>
                    <td className="py-2 pr-4 text-right">{bar.low.toFixed(2)}</td>
                    <td className="py-2 pr-4 text-right">{bar.close.toFixed(2)}</td>
                    <td className="py-2 text-right">{bar.volume.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
