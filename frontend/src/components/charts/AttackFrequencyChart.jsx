/**
 * AttackFrequencyChart — Bar chart showing attack frequency over time
 */

import { useMemo } from 'react'
import { Bar } from 'react-chartjs-2'
import './chartSetup'

export default function AttackFrequencyChart({ data = [], severityDist = {} }) {
  const chartData = useMemo(() => {
    const recent = data.slice(-15)
    const labels = recent.map((d) => {
      const t = new Date(d.time)
      return t.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    })

    return {
      labels,
      datasets: [
        {
          label: 'Attacks per interval',
          data: recent.map((d) => d.count ?? 0),
          backgroundColor: recent.map((d) => {
            const count = d.count ?? 0
            if (count > 10) return 'rgba(255, 51, 102, 0.7)'
            if (count > 5) return 'rgba(255, 140, 0, 0.7)'
            if (count > 2) return 'rgba(255, 215, 0, 0.7)'
            return 'rgba(0, 212, 255, 0.4)'
          }),
          borderColor: 'transparent',
          borderRadius: 4,
          barPercentage: 0.7,
        },
      ],
    }
  }, [data])

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: '#4a6282', maxTicksLimit: 6 },
      },
      y: {
        min: 0,
        grid: { color: '#1a2d4a55' },
        ticks: { color: '#4a6282', stepSize: 5 },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0a1628ee',
        borderColor: '#1a2d4a',
        borderWidth: 1,
        callbacks: {
          label: (ctx) => ` ${ctx.raw} attacks`,
        },
      },
    },
  }

  return (
    <div className="glass-card p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono font-semibold text-white uppercase tracking-wider">Attack Frequency</h3>
        <div className="flex gap-3">
          {Object.entries(severityDist).map(([sev, cnt]) => {
            const colors = { critical: '#ff3366', high: '#ff8c00', medium: '#ffd700', low: '#4a90e2' }
            return (
              <span key={sev} className="text-[10px] font-mono" style={{ color: colors[sev] || '#6b7280' }}>
                {sev.toUpperCase()[0]} {cnt}
              </span>
            )
          })}
        </div>
      </div>
      <div style={{ height: 160 }}>
        {data.length < 2 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-xs font-mono text-cyber-muted">Accumulating data…</p>
          </div>
        ) : (
          <Bar data={chartData} options={options} />
        )}
      </div>
    </div>
  )
}
