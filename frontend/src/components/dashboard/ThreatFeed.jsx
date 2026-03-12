/**
 * ThreatFeed — Real-time live threat event feed
 */

import { useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { getThreatIcon, getSeverityBg, formatRelativeTime, humanizeThreatType, formatConfidence } from '../../utils/helpers'

function ThreatRow({ threat, isNew }) {
  const sevcls = getSeverityBg(threat.severity)

  return (
    <motion.div
      layout
      initial={{ x: -20, opacity: 0, backgroundColor: 'rgba(0, 212, 255, 0.08)' }}
      animate={{ x: 0, opacity: 1, backgroundColor: 'rgba(10, 22, 40, 0)' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-start gap-3 py-2.5 px-3 border-b border-cyber-border/30 
                 hover:bg-cyber-border/10 transition-colors duration-200 group"
    >
      {/* Threat type icon */}
      <div className="text-lg leading-none mt-0.5 shrink-0 w-6 text-center">
        {getThreatIcon(threat.threat_type)}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-semibold text-white font-mono">
            {humanizeThreatType(threat.threat_type)}
          </span>
          <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-bold border ${sevcls}`}>
            {threat.severity?.toUpperCase()}
          </span>
          <span className="text-[10px] text-cyber-muted font-mono ml-auto">
            {formatRelativeTime(threat.timestamp)}
          </span>
        </div>

        <p className="text-[11px] text-slate-400 mt-0.5 truncate group-hover:text-slate-300 transition-colors">
          {threat.explanation || 'Threat detected via AI analysis'}
        </p>

        <div className="flex items-center gap-3 mt-1">
          {threat.source_ip && (
            <span className="text-[10px] font-mono text-cyber-muted">
              <span className="text-cyber-border">SRC</span> {threat.source_ip}
            </span>
          )}
          <span className="text-[10px] font-mono text-cyber-purple">
            CONF {formatConfidence(threat.confidence)}
          </span>
        </div>
      </div>
    </motion.div>
  )
}

export default function ThreatFeed({ threats }) {
  const listRef = useRef(null)

  return (
    <div className="glass-card flex flex-col h-full" style={{ minHeight: 320, maxHeight: 420 }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-cyber-border shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-cyber-red animate-pulse" />
          <h3 className="text-xs font-mono font-semibold text-white tracking-wider uppercase">Live Threat Feed</h3>
        </div>
        <span className="text-[10px] font-mono text-cyber-muted">
          {threats.length} events
        </span>
      </div>

      {/* Feed */}
      <div ref={listRef} className="overflow-y-auto flex-1 min-h-0">
        {threats.length === 0 ? (
          <div className="flex items-center justify-center h-24">
            <p className="text-xs font-mono text-cyber-muted">Monitoring… no threats detected</p>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {threats.slice(0, 30).map((t) => (
              <ThreatRow key={t.id} threat={t} />
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Nova attribution */}
      <div className="px-4 py-2 border-t border-cyber-border/50 flex items-center gap-1.5 shrink-0">
        <span className="text-[9px] font-mono text-cyber-muted">Detection by</span>
        <span className="text-[9px] font-mono text-cyber-neon font-semibold">AMAZON NOVA LITE</span>
        <span className="text-[9px] font-mono text-cyber-muted mx-1">·</span>
        <span className="text-[9px] font-mono text-cyber-muted">Response by</span>
        <span className="text-[9px] font-mono text-cyber-purple font-semibold">NOVA ACT</span>
      </div>
    </div>
  )
}
