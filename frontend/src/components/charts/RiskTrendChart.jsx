/**
 * RiskTrendChart — Area chart for risk score over time
 */

import { useMemo } from 'react'
import { Line } from 'react-chartjs-2'
import './chartSetup'

export default function RiskTrendChart({ data = [] }) {
  const chartData = useMemo(() => {
    const labels = data.slice(-20).map((d) => {
      const t = new Date(d.time)
      return t.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
    })
    const values = data.slice(-20).map((d) => Math.round((d.risk_score ?? 0) * 100))

    return {
      labels,
      datasets: [
        {
          label: 'Risk Score %',
          data: values,
          borderColor: '#ff3366',
          backgroundColor: 'rgba(255, 51, 102, 0.08)',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          pointBackgroundColor: '#ff3366',
          fill: true,
          tension: 0.4,
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
        grid: { color: '#1a2d4a55' },
        ticks: { color: '#4a6282', maxTicksLimit: 6 },
      },
      y: {
        min: 0,
        max: 100,
        grid: { color: '#1a2d4a55' },
        ticks: {
          color: '#4a6282',
          callback: (v) => `${v}%`,
          stepSize: 25,
        },
      },
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0a1628ee',
        borderColor: '#1a2d4a',
        borderWidth: 1,
        callbacks: {
          label: (ctx) => ` Risk: ${ctx.raw}%`,
        },
      },
    },
  }

  return (
    <div className="glass-card p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono font-semibold text-white uppercase tracking-wider">Risk Trend</h3>
        <span className="text-[10px] font-mono text-cyber-muted">last 20 snapshots</span>
      </div>
      <div style={{ height: 160 }}>
        {data.length < 2 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-xs font-mono text-cyber-muted">Accumulating data…</p>
          </div>
        ) : (
          <Line data={chartData} options={options} />
        )}
      </div>
    </div>
  )
}
