/**
 * MetricsRow — Overview KPI cards at the top of the dashboard
 */

import { motion } from 'framer-motion'
import { Shield, AlertTriangle, Activity, TrendingUp, Eye, Cpu } from 'lucide-react'
import { getRiskLabel } from '../../utils/helpers'

function MetricCard({ icon: Icon, label, value, unit, color, glow, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.4 }}
      className="glass-card p-4 flex items-center gap-4 relative overflow-hidden"
      style={{ boxShadow: glow ? `0 0 20px ${color}22` : undefined }}
    >
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
        style={{ background: `${color}18`, border: `1px solid ${color}33` }}
      >
        <Icon className="w-5 h-5" style={{ color }} />
      </div>
      <div className="min-w-0">
        <p className="text-[10px] font-mono text-cyber-muted uppercase tracking-wider truncate">{label}</p>
        <p className="text-2xl font-bold font-mono leading-none mt-0.5" style={{ color }}>
          {value ?? <span className="text-cyber-muted text-sm">—</span>}
          {unit && <span className="text-sm ml-1 text-cyber-muted">{unit}</span>}
        </p>
      </div>
      {/* Background accent */}
      <div
        className="absolute right-0 top-0 w-20 h-full opacity-5"
        style={{ background: `linear-gradient(90deg, transparent, ${color})` }}
      />
    </motion.div>
  )
}

export default function MetricsRow({ metrics }) {
  const risk = metrics?.risk_score ?? 0
  const riskInfo = getRiskLabel(risk)

  const cards = [
    {
      icon: Activity,
      label: 'Events Processed',
      value: metrics?.total_events_processed?.toLocaleString() ?? '0',
      color: '#00d4ff',
    },
    {
      icon: Shield,
      label: 'Threats Detected',
      value: metrics?.threats_detected?.toLocaleString() ?? '0',
      color: '#ff3366',
      glow: (metrics?.threats_detected ?? 0) > 0,
    },
    {
      icon: AlertTriangle,
      label: 'Active Incidents',
      value: metrics?.active_incidents ?? '0',
      color: '#ff8c00',
      glow: (metrics?.active_incidents ?? 0) > 0,
    },
    {
      icon: TrendingUp,
      label: 'Events / Min',
      value: metrics?.events_per_minute?.toFixed(1) ?? '0',
      color: '#00ff88',
    },
    {
      icon: Eye,
      label: 'Risk Score',
      value: `${Math.round(risk * 100)}`,
      unit: '%',
      color: getSeverityColorByRisk(risk),
      glow: risk > 0.5,
    },
    {
      icon: Cpu,
      label: 'AI Status',
      value: 'ONLINE',
      color: '#9b59ff',
    },
  ]

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((c, i) => (
        <MetricCard key={c.label} {...c} index={i} />
      ))}
    </div>
  )
}

function getSeverityColorByRisk(score) {
  if (score >= 0.8) return '#ff3366'
  if (score >= 0.6) return '#ff8c00'
  if (score >= 0.35) return '#ffd700'
  return '#00ff88'
}
