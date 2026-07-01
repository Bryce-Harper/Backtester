import HealthBadge from './components/HealthBadge.jsx'
import PriceExplorer from './components/PriceExplorer.jsx'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-900 p-4 sm:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-white">Momentum Backtester</h1>
          <HealthBadge />
        </header>
        <PriceExplorer />
      </div>
    </div>
  )
}
