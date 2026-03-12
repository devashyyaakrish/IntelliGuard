/**
 * RiskGauge — Circular risk level indicator
 */

import { motion } from 'framer-motion'
import { getRiskLabel } from '../../utils/helpers'

const SIZE = 140
const STROKE = 10
const R = (SIZE - STROKE * 2) / 2
const CIRCUMFERENCE = 2 * Math.PI * R

export default function RiskGauge({ score = 0 }) {
  const pct = Math.min(Math.max(score, 0), 1)
  const filled = CIRCUMFERENCE * pct
  const { label, color } = getRiskLabel(pct)

  const riskColor =
    pct >= 0.8 ? '#ff3366' :
    pct >= 0.6 ? '#ff8c00' :
    pct >= 0.35 ? '#ffd700' : '#00ff88'

  return (
    <div className="glass-card p-4 flex flex-col items-center justify-center gap-2">
      <p className="text-[10px] font-mono text-cyber-muted uppercase tracking-widest">System Risk Level</p>

      <div className="relative flex items-center justify-center" style={{ width: SIZE, height: SIZE }}>
        {/* Background circle */}
        <svg width={SIZE} height={SIZE} className="absolute rotate-[-90deg]">
          <circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={R}
            fill="none"
            stroke="#1a2d4a"
            strokeWidth={STROKE}
          />
          <motion.circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={R}
            fill="none"
            stroke={riskColor}
            strokeWidth={STROKE}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            initial={{ strokeDashoffset: CIRCUMFERENCE }}
            animate={{ strokeDashoffset: CIRCUMFERENCE - filled }}
            transition={{ duration: 1.2, ease: 'easeInOut' }}
            style={{ filter: `drop-shadow(0 0 8px ${riskColor}88)` }}
          />
        </svg>

        {/* Center text */}
        <div className="flex flex-col items-center">
          <motion.span
            key={Math.round(pct * 100)}
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="text-4xl font-bold font-mono"
            style={{ color: riskColor, textShadow: `0 0 20px ${riskColor}66` }}
          >
            {Math.round(pct * 100)}
          </motion.span>
          <span className="text-[10px] font-mono text-cyber-muted -mt-1">%</span>
        </div>
      </div>

      <motion.div
        key={label}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="px-3 py-1 rounded-full text-xs font-mono font-bold tracking-widest"
        style={{
          background: `${riskColor}18`,
          border: `1px solid ${riskColor}44`,
          color: riskColor,
        }}
      >
        {label}
      </motion.div>

      {/* Nova branding */}
      <div className="flex flex-col items-center gap-0.5 mt-1">
        <span className="text-[9px] text-cyber-muted font-mono">Powered by</span>
        <span className="text-[9px] text-cyber-neon font-mono font-semibold tracking-wider">AMAZON NOVA LITE</span>
      </div>
    </div>
  )
}
