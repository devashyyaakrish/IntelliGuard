/**
 * ThreatTypeChart — Doughnut chart of threat type distribution
 */

import { useMemo } from 'react'
import { Doughnut } from 'react-chartjs-2'
import { humanizeThreatType } from '../../utils/helpers'
import './chartSetup'

const COLORS = [
  '#ff3366', '#ff8c00', '#ffd700', '#00d4ff', '#9b59ff',
  '#00ff88', '#ff6b9d', '#4ecdc4', '#45b7d1', '#96ceb4',
]

export default function ThreatTypeChart({ data = {} }) {
  const chartData = useMemo(() => {
    const entries = Object.entries(data)
      .filter(([, v]) => v > 0)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 8)

    return {
      labels: entries.map(([k]) => humanizeThreatType(k)),
      datasets: [
        {
          data: entries.map(([, v]) => v),
          backgroundColor: COLORS.slice(0, entries.length).map((c) => `${c}bb`),
          borderColor: COLORS.slice(0, entries.length),
          borderWidth: 1,
          hoverOffset: 6,
        },
      ],
    }
  }, [data])

  const total = Object.values(data).reduce((a, b) => a + b, 0)

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    animation: { duration: 400 },
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: '#94a3b8',
          padding: 8,
          font: { size: 9.5, family: "'JetBrains Mono', monospace" },
          boxWidth: 10,
          boxHeight: 10,
        },
      },
      tooltip: {
        backgroundColor: '#0a1628ee',
        borderColor: '#1a2d4a',
        borderWidth: 1,
        callbacks: {
          label: (ctx) => ` ${ctx.label}: ${ctx.raw} (${Math.round((ctx.raw / total) * 100)}%)`,
        },
      },
    },
  }

  return (
    <div className="glass-card p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono font-semibold text-white uppercase tracking-wider">Threat Types</h3>
        <span className="text-[10px] font-mono text-cyber-neon">{total} total</span>
      </div>
      <div style={{ height: 160 }}>
        {total === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-xs font-mono text-cyber-muted">No threat data yet</p>
          </div>
        ) : (
          <Doughnut data={chartData} options={options} />
        )}
      </div>
    </div>
  )
}
