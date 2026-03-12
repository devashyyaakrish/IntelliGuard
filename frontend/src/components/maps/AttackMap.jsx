/**
 * AttackMap — Animated geographic attack source visualization
 */

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Globe } from 'lucide-react'
import { getSeverityColor } from '../../utils/helpers'

// Simplified world map SVG viewBox coordinates for key regions
// We use a simple dot-on-rectangle approximation for the hackathon
function geoToSvg(lat, lng) {
  // Equirectangular projection
  const x = ((lng + 180) / 360) * 100
  const y = ((90 - lat) / 180) * 100
  return { x, y }
}

const GRID_LINES = 5

export default function AttackMap({ geoThreats = [], targetCity = { lat: 37.09, lng: -95.71, name: 'USA' } }) {
  const [pulses, setPulses] = useState([])
  const idRef = useRef(0)

  useEffect(() => {
    if (!geoThreats.length) return

    const latest = geoThreats.slice(0, 8)
    const newPulses = latest.map((t) => ({
      ...t,
      id: ++idRef.current,
      src: geoToSvg(t.lat, t.lng),
      dst: geoToSvg(targetCity.lat, targetCity.lng),
    }))

    setPulses(newPulses)

    const timeout = setTimeout(() => setPulses([]), 4000)
    return () => clearTimeout(timeout)
  }, [geoThreats, targetCity])

  const target = geoToSvg(targetCity.lat, targetCity.lng)

  return (
    <div className="glass-card p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-cyber-neon" />
          <h3 className="text-xs font-mono font-semibold text-white uppercase tracking-wider">Attack Map</h3>
        </div>
        <span className="text-[10px] font-mono text-cyber-muted">{geoThreats.length} sources</span>
      </div>

      {/* Map SVG */}
      <div className="relative rounded-lg overflow-hidden bg-cyber-bg border border-cyber-border/40"
           style={{ paddingBottom: '50%' }}>
        <svg
          viewBox="0 0 100 50"
          className="absolute inset-0 w-full h-full"
          preserveAspectRatio="xMidYMid meet"
        >
          {/* Grid */}
          {Array.from({ length: GRID_LINES }).map((_, i) => (
            <g key={i}>
              <line
                x1="0" y1={((i + 1) * 50) / (GRID_LINES + 1)}
                x2="100" y2={((i + 1) * 50) / (GRID_LINES + 1)}
                stroke="#1a2d4a44" strokeWidth="0.2"
              />
              <line
                x1={((i + 1) * 100) / (GRID_LINES + 1)} y1="0"
                x2={((i + 1) * 100) / (GRID_LINES + 1)} y2="50"
                stroke="#1a2d4a44" strokeWidth="0.2"
              />
            </g>
          ))}

          {/* Attack lines and source dots */}
          <AnimatePresence>
            {pulses.map((p) => {
              const color = getSeverityColor(p.severity)
              return (
                <g key={p.id}>
                  {/* Attack line */}
                  <motion.line
                    x1={p.src.x} y1={p.src.y}
                    x2={p.dst.x} y2={p.dst.y}
                    stroke={color}
                    strokeWidth="0.3"
                    strokeDasharray="2 1"
                    initial={{ opacity: 0, pathLength: 0 }}
                    animate={{ opacity: 0.6, pathLength: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 1.5 }}
                  />

                  {/* Source dot */}
                  <motion.circle
                    cx={p.src.x} cy={p.src.y} r="0.8"
                    fill={color}
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ opacity: 0, scale: 0 }}
                  />

                  {/* Pulse ring at source */}
                  <motion.circle
                    cx={p.src.x} cy={p.src.y} r="0.8"
                    fill="none" stroke={color} strokeWidth="0.3"
                    initial={{ r: 0.8, opacity: 1 }}
                    animate={{ r: 3, opacity: 0 }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                  />
                </g>
              )
            })}
          </AnimatePresence>

          {/* Target (defended system) */}
          <circle cx={target.x} cy={target.y} r="1.2" fill="#00d4ff44" stroke="#00d4ff" strokeWidth="0.4" />
          <circle cx={target.x} cy={target.y} r="0.5" fill="#00d4ff" />
          <motion.circle
            cx={target.x} cy={target.y} r="1.2"
            fill="none" stroke="#00d4ff" strokeWidth="0.3"
            initial={{ r: 1.2, opacity: 0.8 }}
            animate={{ r: 4, opacity: 0 }}
            transition={{ repeat: Infinity, duration: 2 }}
          />

          {/* Labels for source IPs */}
          {pulses.slice(0, 5).map((p) => (
            <text key={`lbl-${p.id}`} x={p.src.x + 1.2} y={p.src.y - 0.5}
                  fontSize="1.5" fill="#94a3b8" fontFamily="monospace">
              {p.country}
            </text>
          ))}
        </svg>

        {/* Overlay: no data */}
        {geoThreats.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-xs font-mono text-cyber-muted">No geolocated threats</p>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="flex gap-4 flex-wrap">
        {['critical', 'high', 'medium', 'low'].map((sev) => (
          <div key={sev} className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ background: getSeverityColor(sev) }} />
            <span className="text-[9px] font-mono text-cyber-muted uppercase">{sev}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
